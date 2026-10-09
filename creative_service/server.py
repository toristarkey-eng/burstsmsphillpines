"""MCP drafting/retrieval tools; separate authenticated human review routes."""
from __future__ import annotations

import asyncio
import base64
import html
import json
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import parse_qs

import jwt
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import CallToolResult, ImageContent, TextContent, ToolAnnotations
from pydantic import AnyHttpUrl, ValidationError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Mount, Route

from .renderer import Campaign, Hold, catalog
from .store import REVIEW_CHECKS, Store


class JWTVerifier(TokenVerifier):
    def __init__(self, issuer: str, audience: str, jwks_url: str):
        if not all(s.startswith("https://") for s in [issuer, audience, jwks_url]):
            raise ValueError("Production OAuth settings must use HTTPS")
        self.issuer, self.audience = issuer, audience
        self.jwks = jwt.PyJWKClient(jwks_url, cache_keys=True)

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            key = await asyncio.to_thread(self.jwks.get_signing_key_from_jwt, token)
            data = jwt.decode(token, key.key, algorithms=["RS256"], issuer=self.issuer, audience=self.audience,
                              options={"require": ["exp", "iss", "aud", "sub"]})
            return AccessToken(token=token, client_id=data["sub"], scopes=data.get("scope", "").split(), expires_at=data["exp"], resource=self.audience)
        except (jwt.PyJWTError, ValueError, TypeError):
            return None


def make_mcp(store: Store, verifier=None, auth=None, public_host="localhost") -> FastMCP:
    mcp = FastMCP("Burst SMS PH controlled creative", instructions=
        "Use list_creative_templates, then prepare_creative with campaign copy. Brand styles are locked. Preparation returns no image. Human approval is outside MCP. Only get_reviewed_creative releases a validated, reviewed PNG. Never substitute an image-generation tool.",
        token_verifier=verifier, auth=auth, stateless_http=True, json_response=True,
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=True,
            allowed_hosts=[public_host, "localhost:*", "127.0.0.1:*"], allowed_origins=[f"https://{public_host}", "http://localhost:*", "http://127.0.0.1:*"]))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False))
    def list_creative_templates() -> dict:
        """Get six locked Burst SMS Philippines templates, sizes, registered photos and CTA choices."""
        return catalog()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True))
    async def prepare_creative(campaign: Campaign) -> dict:
        """Create a private technically checked candidate from copy; no image is released before independent human review. Never supply colours, font settings, file paths or image URLs."""
        try:
            return await asyncio.to_thread(store.prepare, campaign, "mcp-drafter")
        except (Hold, ValidationError, OSError, TimeoutError, ValueError) as exc:
            return {"status": "HOLD", "reason": str(exc), "image_released": False}

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False))
    def get_reviewed_creative(artifact_id: str) -> CallToolResult:
        """Return the exact PNG and publication record only after technical checks and independently signed owner review pass. Pending/rejected/tampered candidates return Hold without an image."""
        try:
            png, receipt = store.release(artifact_id)
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(receipt)),
                ImageContent(type="image", mimeType="image/png", data=base64.b64encode(png).decode())], structuredContent=receipt)
        except (Hold, OSError, ValueError) as exc:
            return CallToolResult(isError=True, content=[TextContent(type="text", text=f"Hold: {exc}")])
    return mcp


def make_app(store: Store, mcp: FastMCP, reviewer_password: str, public_origin: str) -> Starlette:
    if len(reviewer_password) < 24:
        raise ValueError("Reviewer password must be at least 24 characters and separate from OAuth credentials")

    def authorised(request):
        try:
            kind, value = request.headers.get("authorization", "").split(" ", 1)
            name, password = base64.b64decode(value).decode().split(":", 1)
            return kind.lower() == "basic" and name == "brand-reviewer" and secrets.compare_digest(password, reviewer_password)
        except (ValueError, UnicodeError):
            return False

    headers = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer",
               "Content-Security-Policy": "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'"}

    async def review_page(request: Request):
        if not authorised(request):
            return Response(status_code=401, headers={**headers, "WWW-Authenticate": 'Basic realm="Burst SMS brand review"'})
        artifact_id = request.path_params["artifact_id"]
        try:
            _, record = store.candidate(artifact_id)
            csrf = store.sign({"review": artifact_id, "png_sha256": record["png_sha256"]})
            checks = "".join(f'<label><input type="checkbox" name="{key}" required> {key.replace("_", " ")}</label><br>' for key in REVIEW_CHECKS)
            text = html.escape(json.dumps(record["campaign"], indent=2))
            return HTMLResponse(f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Private Burst SMS brand review</title>
            <style>body{{font:18px sans-serif;max-width:1080px;margin:40px auto;padding:20px;color:#002A66}}img{{max-width:500px;width:100%}}label{{line-height:2}}textarea{{width:100%;height:100px}}button{{padding:12px 24px}}</style>
            <h1>Private publication review</h1><p>Technical checks passed. This candidate is withheld from the marketing tool until you approve it. Check the exact image, all copy, claim sources, local context and accessibility.</p>
            <img src="/review/{artifact_id}/image" alt="Private candidate awaiting owner review"><pre>{text}</pre>
            <form method="post"><input type="hidden" name="csrf" value="{csrf}"><p><label>Your name <input name="reviewer" required maxlength="100"></label></p>{checks}
            <p><label>Approval basis and sources <textarea name="evidence" required minlength="15" maxlength="4000"></textarea></label></p>
            <button name="decision" value="approve">Approve for publication</button><button name="decision" value="reject" formnovalidate>Reject</button></form></html>''', headers=headers)
        except (Hold, OSError, ValueError):
            return Response("Candidate unavailable or integrity check failed", status_code=404, headers=headers)

    async def review_image(request: Request):
        if not authorised(request):
            return Response(status_code=401, headers={**headers, "WWW-Authenticate": 'Basic realm="Burst SMS brand review"'})
        try:
            png, _ = store.candidate(request.path_params["artifact_id"])
            return Response(png, media_type="image/png", headers=headers)
        except (Hold, OSError, ValueError):
            return Response(status_code=404, headers=headers)

    async def review_post(request: Request):
        if not authorised(request):
            return Response(status_code=401, headers=headers)
        if request.headers.get("origin") != public_origin:
            return Response("Invalid review origin", status_code=403, headers=headers)
        if int(request.headers.get("content-length", "0")) > 10000:
            return Response(status_code=413, headers=headers)
        try:
            body = await request.body()
            if len(body) > 10000:
                return Response(status_code=413, headers=headers)
            data = {k: v[0] for k, v in parse_qs(body.decode()).items()}
            artifact_id = request.path_params["artifact_id"]
            _, record = store.candidate(artifact_id)
            if not secrets.compare_digest(data.get("csrf", ""), store.sign({"review": artifact_id, "png_sha256": record["png_sha256"]})):
                return Response("Invalid review token", status_code=403, headers=headers)
            if data.get("decision") not in {"approve", "reject"}:
                raise Hold("Choose approve or reject")
            approval = store.review(artifact_id, data.get("reviewer", ""), {k: data.get(k) == "on" for k in REVIEW_CHECKS},
                                    data.get("evidence", ""), data["decision"] == "approve")
            return JSONResponse({"status": approval["status"], "id": artifact_id}, headers=headers)
        except (Hold, ValueError, OSError) as exc:
            return JSONResponse({"status": "HOLD", "reason": str(exc)}, status_code=400, headers=headers)

    @asynccontextmanager
    async def lifespan(app):
        async with mcp.session_manager.run():
            yield

    return Starlette(lifespan=lifespan, routes=[
        Route("/health", lambda _: JSONResponse({"service": "Burst SMS PH controlled creative", "status": "running"})),
        Route("/review/{artifact_id}", review_page, methods=["GET"]),
        Route("/review/{artifact_id}", review_post, methods=["POST"]),
        Route("/review/{artifact_id}/image", review_image, methods=["GET"]),
        Mount("/", app=mcp.streamable_http_app())])


def main():
    import uvicorn
    from urllib.parse import urlsplit
    origin = os.environ["BURST_PUBLIC_ORIGIN"].rstrip("/")
    if not origin.startswith("https://"):
        raise ValueError("Remote service requires a public HTTPS origin")
    issuer, audience, jwks = (os.environ[k] for k in ["BURST_OAUTH_ISSUER", "BURST_OAUTH_AUDIENCE", "BURST_OAUTH_JWKS_URL"])
    verifier = JWTVerifier(issuer, audience, jwks)
    store = Store(Path(os.environ["BURST_PRIVATE_DATA"]), os.environ["BURST_REVIEW_SIGNING_KEY"])
    auth = AuthSettings(issuer_url=AnyHttpUrl(issuer), resource_server_url=AnyHttpUrl(origin + "/mcp"), required_scopes=["creative:use"])
    mcp = make_mcp(store, verifier, auth, urlsplit(origin).netloc)
    app = make_app(store, mcp, os.environ["BURST_REVIEW_PASSWORD"], origin)
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), workers=1)


if __name__ == "__main__":
    main()
