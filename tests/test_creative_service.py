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
        for text in ["Use Kudosity", "Try https://evil.example", "Hello\u202eevil", "Hello \u2014 world", "Guaranteed best results"]:
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
        app = make_app(self.store, make_mcp(self.store), password, "https://creative.example")
        with TestClient(app) as client:
            url = f"/review/{self.id}"
            self.assertEqual(client.get(url).status_code, 401)
            client.auth = ("brand-reviewer", password)
            self.assertEqual(client.get(url).status_code, 200)
            self.assertEqual(client.get(url + "/image").headers["cache-control"], "no-store")
            self.assertEqual(client.post(url, data={"csrf": "forged"}, headers={"origin": "https://creative.example"}).status_code, 403)
            _, record = self.store.candidate(self.id)
            csrf = self.store.sign({"review": self.id, "png_sha256": record["png_sha256"]})
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
        app = make_app(self.store, mcp, "separate-human-review-password", "https://testserver")
        headers = {"accept": "application/json, text/event-stream", "content-type": "application/json", "mcp-protocol-version": "2025-06-18"}
        body = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "release-test", "version": "1"}}}
        with TestClient(app) as client:
            self.assertEqual(client.post("/mcp", json=body, headers=headers).status_code, 401)
            headers["authorization"] = "Bearer wrong-scope-token"
            self.assertEqual(client.post("/mcp", json=body, headers=headers).status_code, 403)
            headers["authorization"] = "Bearer test-use-token"
            self.assertIn("result", client.post("/mcp", json=body, headers=headers).json())
            call = {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_reviewed_creative", "arguments": {"artifact_id": self.id}}}
            result = client.post("/mcp", json=call, headers=headers).json()["result"]
            self.assertTrue(result["isError"])
            self.assertFalse(any(c["type"] == "image" for c in result["content"]))
            self.approve()
            result = client.post("/mcp", json=call, headers=headers).json()["result"]
            image = next(c for c in result["content"] if c["type"] == "image")
            self.assertEqual(base64.b64decode(image["data"]), self.store.release(self.id)[0])


if __name__ == "__main__":
    unittest.main()
