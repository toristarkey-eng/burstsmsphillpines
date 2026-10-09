import asyncio
import base64
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from pydantic import ValidationError
from starlette.testclient import TestClient
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl

from creative_service.renderer import Campaign, Hold, PLUGIN, ROOT, catalog, render
from creative_service.server import make_app, make_mcp
from creative_service.store import REVIEW_CHECKS, Store


def campaign(template="recognition", fmt="portrait"):
    photo = "commercial-team" if template == "team-coffee" else "workplace-portrait" if template in ["customer-updates", "people-first"] else None
    return Campaign(template_id=template, format=fmt, headline="Make every message count.", accent="Stay connected.",
                    supporting="Explore messaging for your business.", primary_text="Talk to Burst SMS Philippines about messaging for your business.", photo_id=photo)


class RendererTests(unittest.TestCase):
    def test_all_templates_and_both_formats_are_deterministic(self):
        for template in catalog()["templates"]:
            for fmt in ["square", "portrait"]:
                with self.subTest(template=template, format=fmt):
                    png, report = render(campaign(template, fmt))
                    again, _ = render(campaign(template, fmt))
                    self.assertEqual(png, again)
                    self.assertEqual(Image.open(io.BytesIO(png)).size, (1080, 1080 if fmt == "square" else 1350))
                    self.assertTrue(all(report["checks"].values()))
                    self.assertEqual(report["publication_status"], "AWAITING_OWNER_REVIEW")
                    self.assertIn("https://burstsms.com.ph/", report["channel_copy"])

    def test_styles_paths_links_and_unregistered_photos_cannot_be_injected(self):
        for field, value in [("colour", "#ff00ff"), ("logo_path", "/tmp/logo.png"), ("font", "Arial"), ("dimensions", [400, 400]), ("approval", True), ("html", "<script>")]:
            with self.subTest(field=field), self.assertRaises(ValidationError):
                Campaign.model_validate({**campaign().model_dump(), field: value})
        for text in ["Use Kudosity", "Try evil.example", "Try 192.0.2.1", "Try ftp://evil.example", "Try https://evil.example", "Hello\u202eevil", "Hello \u2014 world", "Guaranteed best results"]:
            with self.subTest(text=text), self.assertRaises(ValidationError):
                Campaign.model_validate({**campaign().model_dump(), "headline": text})
        with self.assertRaises(Hold):
            render(campaign("people-first").model_copy(update={"photo_id": "../../etc/passwd"}))

    def test_overflow_fails_without_shrinking_type(self):
        with self.assertRaises(Hold):
            render(campaign().model_copy(update={"headline": "W" * 65}))

    def test_modified_logo_blocks_even_if_its_dimensions_are_unchanged(self):
        logo = PLUGIN / "assets/burst-sms-logo.png"
        original = logo.read_bytes()
        try:
            im = Image.open(io.BytesIO(original)).convert("RGB")
            im.putpixel((0, 0), (255, 0, 255))
            im.save(logo)
            with self.assertRaises(Hold):
                render(campaign())
        finally:
            logo.write_bytes(original)

    def test_changed_team_photograph_is_blocked(self):
        photo = PLUGIN / "assets/burst-sms-ph-commercial-team.jpg"
        original = photo.read_bytes()
        try:
            photo.write_bytes(original + b"changed")
            with self.assertRaises(Hold):
                render(campaign("team-coffee"))
        finally:
            photo.write_bytes(original)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name), "s" * 48)
        self.id = self.store._prepare_verified(campaign(), "mcp-drafter")["id"]
        self.checks = {k: True for k in REVIEW_CHECKS}

    def tearDown(self):
        self.temp.cleanup()

    def approve(self):
        return self.store.review(self.id, "authorised-reviewer", self.checks, "Owner verified copy, brand, illustrative scene and publication suitability.")

    def test_pending_rejected_and_incomplete_reviews_withhold_images(self):
        with self.assertRaises(Hold):
            self.store.release(self.id)
        with self.assertRaises(Hold):
            self.store.review(self.id, "mcp-drafter", self.checks, "Owner review has been completed.")
        with self.assertRaises(Hold):
            self.store.review(self.id, "reviewer", {**self.checks, "wording_and_claims": False}, "A claim is still unsupported.")
        self.store.review(self.id, "reviewer", self.checks, "Please revise the headline before publication.", approved=False)
        with self.assertRaises(Hold):
            self.store.release(self.id)

    def test_three_simulated_users_receive_identical_reviewed_bytes(self):
        self.approve()
        outputs = [self.store.release(self.id)[0] for _ in range(3)]
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[1], outputs[2])

    def test_edited_image_and_forged_approval_cannot_be_released(self):
        self.approve()
        target = self.store.path(self.id)
        png = (target / "candidate.png").read_bytes()
        (target / "candidate.png").write_bytes(png + b"tampered")
        with self.assertRaises(Hold):
            self.store.release(self.id)
        (target / "candidate.png").write_bytes(png)
        record = json.loads((target / "approval.json").read_text())
        record["approval"]["reviewer"] = "forged"
        (target / "approval.json").write_text(json.dumps(record))
        with self.assertRaises(Hold):
            self.store.release(self.id)

    def test_live_gate_is_mandatory_before_tool_preparation(self):
        with patch("creative_service.store.live_source_gate", side_effect=Hold("Live source unavailable")), self.assertRaises(Hold):
            self.store.prepare(campaign(), "drafter")

    def test_mcp_has_no_approval_or_brand_mutation_tool(self):
        mcp = make_mcp(self.store)
        names = {tool.name for tool in asyncio.run(mcp.list_tools())}
        self.assertEqual(names, {"list_creative_templates", "prepare_creative", "get_reviewed_creative"})
        result = asyncio.run(mcp.call_tool("get_reviewed_creative", {"artifact_id": self.id}))
        self.assertFalse(any(block.type == "image" for block in result.content))
        self.approve()
        result = asyncio.run(mcp.call_tool("get_reviewed_creative", {"artifact_id": self.id}))
        images = [block for block in result.content if block.type == "image"]
        self.assertEqual(len(images), 1)
        self.assertEqual(base64.b64decode(images[0].data), self.store.release(self.id)[0])

    def test_review_http_is_private_and_requires_signed_form_and_origin(self):
        password = "a-review-password-separate-from-mcp"
        app = make_app(self.store, make_mcp(self.store), password, "https://creative.example", "authorised-reviewer")
        with TestClient(app) as client:
            url = f"/review/{self.id}"
            self.assertEqual(client.get(url).status_code, 401)
            client.auth = ("brand-reviewer", password)
            self.assertEqual(client.get(url).status_code, 200)
            self.assertEqual(client.get(url + "/image").headers["cache-control"], "no-store")
            self.assertEqual(client.post(url, data={"csrf": "☃"}, headers={"origin": "https://creative.example"}).status_code, 403)
            self.assertEqual(client.post(url, data={"csrf": "forged"}, headers={"origin": "https://creative.example"}).status_code, 403)
            _, record = self.store.candidate(self.id)
            csrf = self.store.review_token(self.id)
            form = {"csrf": csrf, "reviewer": "Tori", "evidence": "Owner verified wording, brand and local context.", "decision": "approve", **{k: "on" for k in REVIEW_CHECKS}}
            self.assertEqual(client.post(url, data=form, headers={"origin": "https://evil.example"}).status_code, 403)
            self.assertEqual(client.post(url, data=form, headers={"origin": "https://creative.example"}).status_code, 200)
            self.assertEqual(self.store.release(self.id)[1]["publication_status"], "APPROVED")

    def test_authenticated_streamable_http_protocol_and_release_gate(self):
        class TestVerifier(TokenVerifier):
            async def verify_token(self, token):
                return AccessToken(token=token, client_id="test-user", scopes=["creative:use"] if token == "test-use-token" else [])
        auth = AuthSettings(issuer_url=AnyHttpUrl("https://issuer.example"),
                            resource_server_url=AnyHttpUrl("https://testserver/mcp"), required_scopes=["creative:use"])
        mcp = make_mcp(self.store, TestVerifier(), auth, public_host="testserver")
        app = make_app(self.store, mcp, "separate-human-review-password", "https://testserver", "authorised-reviewer")
        headers = {"accept": "application/json, text/event-stream", "content-type": "application/json", "mcp-protocol-version": "2025-06-18"}
        body = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "release-test", "version": "1"}}}
        with TestClient(app) as client:
            self.assertEqual(client.post("/mcp", json=body, headers=headers).status_code, 401)
            headers["authorization"] = "Bearer wrong-scope-token"
            self.assertEqual(client.post("/mcp", json=body, headers=headers).status_code, 403)
            headers["authorization"] = "Bearer test-use-token"
            self.assertIn("result", client.post("/mcp", json=body, headers=headers).json())
            self.assertEqual(client.get("/.well-known/oauth-protected-resource/mcp").status_code, 200)
            prepare_call = {"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "prepare_creative", "arguments": {"campaign": campaign().model_dump()}}}
            with patch("creative_service.store.live_source_gate"):
                prepared = client.post("/mcp", json=prepare_call, headers=headers).json()["result"]
            self.assertFalse(prepared.get("isError"))
            candidate_id = json.loads(prepared["content"][0]["text"])["id"]
            self.assertEqual(self.store.candidate(candidate_id)[1]["creator"], "test-user")
            self.assertFalse(any(c["type"] == "image" for c in prepared["content"]))
            call = {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_reviewed_creative", "arguments": {"artifact_id": self.id}}}
            result = client.post("/mcp", json=call, headers=headers).json()["result"]
            self.assertTrue(result["isError"])
            self.assertFalse(any(c["type"] == "image" for c in result["content"]))
            self.approve()
            result = client.post("/mcp", json=call, headers=headers).json()["result"]
            image = next(c for c in result["content"] if c["type"] == "image")
            self.assertEqual(base64.b64decode(image["data"]), self.store.release(self.id)[0])

class SecurityRegressionTests(unittest.TestCase):
    def test_jwt_verifies_real_signatures_claims_and_scope_shape(self):
        import time
        import jwt
        from types import SimpleNamespace
        from cryptography.hazmat.primitives.asymmetric import rsa
        from creative_service.server import JWTVerifier
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        verifier = JWTVerifier("https://issuer.example", "urn:burst:creative", "https://issuer.example/jwks")
        claims = {"sub": "drafter-123", "exp": int(time.time()) + 300, "iss": "https://issuer.example", "aud": "urn:burst:creative", "scope": "creative:use"}
        with patch.object(verifier.jwks, "get_signing_key_from_jwt", return_value=SimpleNamespace(key=key.public_key())):
            token = jwt.encode(claims, key, algorithm="RS256")
            result = asyncio.run(verifier.verify_token(token))
            self.assertEqual(result.client_id, "drafter-123")
            self.assertEqual(result.scopes, ["creative:use"])
            for update in [{"exp": 1}, {"exp": float("inf")}, {"iss": "https://evil.example"}, {"aud": "other-service"}, {"sub": ""}, {"scope": ["creative:use"]}]:
                with self.subTest(update=update):
                    self.assertIsNone(asyncio.run(verifier.verify_token(jwt.encode({**claims, **update}, key, algorithm="RS256"))))
            for field in ("sub", "exp", "iss", "aud"):
                invalid = {name: value for name, value in claims.items() if name != field}
                self.assertIsNone(asyncio.run(verifier.verify_token(jwt.encode(invalid, key, algorithm="RS256"))))
            wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            self.assertIsNone(asyncio.run(verifier.verify_token(jwt.encode(claims, wrong_key, algorithm="RS256"))))
            self.assertIsNone(asyncio.run(verifier.verify_token(jwt.encode(claims, "different-key" * 4, algorithm="HS256"))))

    def test_invalid_production_urls_are_rejected(self):
        from creative_service.server import https_url
        for value in ("http://creative.example", "https://user:pass@creative.example", "https://creative.example/path", "https://creative.example?x=1", "https://creative.example#x"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                https_url(value, origin=True)

    def test_streamed_and_declared_bodies_are_bounded_before_parsing(self):
        from creative_service.server import BodyLimitMiddleware
        async def run(path, headers, chunks):
            messages = []
            async def app(scope, receive, send):
                self.fail("Oversized or malformed request reached the application")
            events = iter({"type": "http.request", "body": chunk, "more_body": i < len(chunks)-1} for i, chunk in enumerate(chunks))
            async def receive():
                return next(events)
            async def send(message):
                messages.append(message)
            await BodyLimitMiddleware(app)({"type": "http", "method": "POST", "path": path, "headers": headers}, receive, send)
            return messages[0]["status"]
        self.assertEqual(asyncio.run(run("/mcp", [], [b"x"*70000, b"x"*70000])), 413)
        self.assertEqual(asyncio.run(run("/review/123", [], [b"x"*6000, b"x"*6000])), 413)
        self.assertEqual(asyncio.run(run("/mcp", [(b"content-length", b"200000")], [])), 413)
        self.assertEqual(asyncio.run(run("/mcp", [(b"content-length", b"bad")], [])), 400)

    def test_live_gate_pins_release_and_verifies_all_locked_sources(self):
        from types import SimpleNamespace
        from creative_service.store import live_source_gate
        sha = "a" * 40
        receipt = SimpleNamespace(returncode=0, stdout='{"gate":"PASSED","allowed":true}')
        with patch("creative_service.store.subprocess.run", return_value=receipt) as run:
            live_source_gate(sha)
            args = run.call_args.args[0]
            self.assertIn(f"https://raw.githubusercontent.com/toristarkey-eng/burstsmsphillpines/{sha}", args)
            self.assertIn("--release-lock", args)
        with self.assertRaises(Hold):
            live_source_gate("main")
        with patch("creative_service.store.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout="[]")), self.assertRaises(Hold):
            live_source_gate(sha)

    def test_actual_background_contrast_and_text_collision_are_checked(self):
        from creative_service.renderer import Canvas, PALETTE
        canvas = Canvas((300, 120))
        canvas.text("Example", (5, 5, 280, 80), 32, "white")
        canvas.draw.rectangle((0, 0, 300, 120), fill=PALETTE["cyan"])
        with self.assertRaises(Hold):
            canvas.finish_text()
        canvas = Canvas((300, 120))
        canvas.text("Example", (5, 5, 280, 80), 32)
        canvas.text("Example", (5, 5, 280, 80), 32)
        with self.assertRaises(Hold):
            canvas.finish_text()

    def test_missing_release_lock_coverage_blocks_rendering(self):
        from creative_service.renderer import load_locks
        lock = ROOT / "creative_service/release-lock.json"
        original = lock.read_text()
        data = json.loads(original)
        del data["files"]["creative_service/server.py"]
        try:
            lock.write_text(json.dumps(data))
            with self.assertRaises(Hold):
                load_locks()
        finally:
            lock.write_text(original)

    def test_canvas_rejects_invalid_boxes_and_signed_approval_requires_all_checks(self):
        from creative_service.renderer import Canvas
        for box in [(-1, 0, 100, 80), (0, 0, 301, 80), (0, 0, 100, 0)]:
            with self.subTest(box=box), self.assertRaises(Hold):
                Canvas((300, 120)).text("Example", box, 32)
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory), "s"*48)
            artifact = store._prepare_verified(campaign(), "drafter-sub")["id"]
            approval = store.review(artifact, "reviewer-sub", {k: True for k in REVIEW_CHECKS}, "Owner verified the campaign and artwork.")
            approval["checks"] = {}
            (store.path(artifact) / "approval.json").write_text(json.dumps({"approval": approval, "signature": store.sign(approval)}))
            with self.assertRaises(Hold):
                store.release(artifact)

    def test_logo_is_scaled_proportionally_and_unregistered_photos_are_rejected(self):
        from PIL import ImageChops
        png, _ = render(campaign())
        image = Image.open(io.BytesIO(png)).convert("RGB")
        logo = Image.open(PLUGIN / "assets/burst-sms-logo.png").convert("RGB")
        expected = logo.resize((logo.width*2, logo.height*2), Image.Resampling.LANCZOS)
        self.assertIsNone(ImageChops.difference(image.crop((56, 15, 56+expected.width, 15+expected.height)), expected).getbbox())
        with self.assertRaises(Hold):
            render(campaign().model_copy(update={"photo_id": "unregistered"}))

    def test_stale_review_cannot_reverse_rejection_or_forge_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory), "s"*48)
            artifact = store._prepare_verified(campaign(), "reviewer-sub")["id"]
            app = make_app(store, make_mcp(store), "separate-human-review-password", "https://creative.example", "reviewer-sub")
            form = {"csrf": store.review_token(artifact), "reviewer": "someone-else", "evidence": "The campaign has been checked independently.", "decision": "approve", **{k: "on" for k in REVIEW_CHECKS}}
            with TestClient(app) as client:
                client.auth = ("brand-reviewer", "separate-human-review-password")
                response = client.post(f"/review/{artifact}", data=form, headers={"origin": "https://creative.example"})
                self.assertEqual(response.status_code, 400)
            other = store._prepare_verified(campaign(), "drafter-sub")["id"]
            old_token = store.review_token(other)
            store.review(other, "reviewer-sub", {}, "Reject pending the claim source.", approved=False, review_token=old_token)
            with self.assertRaises(Hold):
                store.review(other, "reviewer-sub", {k: True for k in REVIEW_CHECKS}, "Old form must not overwrite rejection.", review_token=old_token)
            with self.assertRaises(Hold):
                store.release(other)

    def test_corrupt_approval_returns_hold_without_pixels(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory), "s"*48)
            artifact = store._prepare_verified(campaign(), "drafter-sub")["id"]
            mcp = make_mcp(store)
            for record in ({}, {"approval": None, "signature": 1}, {"approval": {}, "signature": "bad"}):
                (store.path(artifact) / "approval.json").write_text(json.dumps(record))
                result = asyncio.run(mcp.call_tool("get_reviewed_creative", {"artifact_id": artifact}))
                self.assertTrue(result.isError)
                self.assertFalse(any(block.type == "image" for block in result.content))

    def test_prepare_uses_authenticated_subject_and_busy_requests_hold(self):
        from mcp.server.auth.middleware.auth_context import auth_context_var
        from mcp.server.auth.middleware.bearer_auth import AuthenticatedUser
        import threading
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory), "s"*48)
            mcp = make_mcp(store)
            entered, complete = threading.Event(), threading.Event()
            def prepare(campaign, creator):
                entered.set()
                complete.wait(5)
                return {"creator": creator}
            async def exercise():
                context = auth_context_var.set(AuthenticatedUser(AccessToken(token="test", client_id="drafter-sub", scopes=["creative:use"])))
                try:
                    first = asyncio.create_task(mcp.call_tool("prepare_creative", {"campaign": campaign().model_dump()}))
                    await asyncio.to_thread(entered.wait, 5)
                    second = await mcp.call_tool("prepare_creative", {"campaign": campaign().model_dump()})
                    self.assertIn("Renderer busy", str(second))
                    complete.set()
                    self.assertIn("drafter-sub", str(await first))
                finally:
                    complete.set()
                    auth_context_var.reset(context)
            with patch.object(store, "prepare", side_effect=prepare) as mocked:
                asyncio.run(exercise())
                self.assertEqual(mocked.call_count, 1)
                self.assertEqual(mocked.call_args.args[1], "drafter-sub")

    def test_cancelled_preparation_keeps_capacity_until_worker_finishes(self):
        from mcp.server.auth.middleware.auth_context import auth_context_var
        from mcp.server.auth.middleware.bearer_auth import AuthenticatedUser
        import threading
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory), "s"*48)
            mcp = make_mcp(store)
            entered, complete, finished = threading.Event(), threading.Event(), threading.Event()
            def prepare(campaign, creator):
                entered.set()
                complete.wait(5)
                finished.set()
                return {"status": "AWAITING_OWNER_REVIEW"}
            async def exercise():
                context = auth_context_var.set(AuthenticatedUser(AccessToken(token="test", client_id="drafter-sub", scopes=["creative:use"])))
                try:
                    first = asyncio.create_task(mcp.call_tool("prepare_creative", {"campaign": campaign().model_dump()}))
                    self.assertTrue(await asyncio.to_thread(entered.wait, 5))
                    first.cancel()
                    with self.assertRaises(asyncio.CancelledError):
                        await first
                    second = await mcp.call_tool("prepare_creative", {"campaign": campaign().model_dump()})
                    self.assertIn("Renderer busy", str(second))
                    complete.set()
                    self.assertTrue(await asyncio.to_thread(finished.wait, 5))
                finally:
                    complete.set()
                    auth_context_var.reset(context)
            with patch.object(store, "prepare", side_effect=prepare) as mocked:
                asyncio.run(exercise())
                self.assertEqual(mocked.call_count, 1)


if __name__ == "__main__":
    unittest.main()
