"""Private candidates, independent signed review, and verified release only."""
from __future__ import annotations

import hmac
import json
import os
import re
import secrets
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .renderer import Campaign, Hold, PLUGIN, ROOT, canonical, digest, load_locks, render

REVIEW_CHECKS = ["wording_and_claims", "visual_composition", "local_fit_and_photography", "accessibility", "publication_authority"]


class Store:
    def __init__(self, directory: Path, signing_key: str):
        if len(signing_key) < 32:
            raise ValueError("Review signing key must be at least 32 characters")
        self.directory = directory.resolve()
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.key = signing_key.encode()

    def path(self, artifact_id: str) -> Path:
        if not re.fullmatch(r"[0-9a-f]{32}", artifact_id):
            raise Hold("Unknown creative ID")
        return self.directory / artifact_id

    def sign(self, record) -> str:
        return hmac.new(self.key, canonical(record), "sha256").hexdigest()

    def prepare(self, campaign: Campaign, creator: str) -> dict:
        live_source_gate()
        return self._prepare_verified(campaign, creator)

    def _prepare_verified(self, campaign: Campaign, creator: str) -> dict:
        """Private test/internal seam, never registered as a tool or HTTP route."""
        png, report = render(campaign)
        artifact_id = secrets.token_hex(16)
        target = self.path(artifact_id)
        target.mkdir(mode=0o700)
        report.update({"id": artifact_id, "creator": creator, "created_at": now()})
        (target / "candidate.png").write_bytes(png)
        atomic_json(target / "record.json", {"report": report, "signature": self.sign(report)})
        return {"id": artifact_id, "status": "AWAITING_OWNER_REVIEW", "technical_status": "PASSED", "dimensions": report["dimensions"], "message": "Private candidate created. An authorised reviewer must inspect the separate review page. No image has been released."}

    def candidate(self, artifact_id: str) -> tuple[bytes, dict]:
        load_locks()
        try:
            target = self.path(artifact_id)
            record = json.loads((target / "record.json").read_text())
            report = record["report"]
            if not hmac.compare_digest(record["signature"], self.sign(report)):
                raise Hold("Candidate record integrity mismatch")
            png = (target / "candidate.png").read_bytes()
            if digest(png) != report["png_sha256"]:
                raise Hold("Candidate image integrity mismatch")
            if report["release_sha256"] != digest(canonical(load_locks())):
                raise Hold("Renderer changed since review. Prepare a new candidate")
            return png, report
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as exc:
            raise Hold("Creative not found or its record is invalid") from exc

    def review(self, artifact_id: str, reviewer: str, checks: dict, evidence: str, approved: bool = True) -> dict:
        _, report = self.candidate(artifact_id)
        if not reviewer.strip() or reviewer == report["creator"]:
            raise Hold("Review must be by an identified person independent of the drafting identity")
        if approved and (set(checks) != set(REVIEW_CHECKS) or any(v is not True for v in checks.values())):
            raise Hold("Every human review check must pass before approval")
        if len(evidence.strip()) < 15:
            raise Hold("Record the approval basis and sources, or the reason for rejection")
        approval = {"id": artifact_id, "status": "APPROVED" if approved else "REJECTED", "reviewer": reviewer,
                    "reviewed_at": now(), "checks": checks, "evidence": evidence.strip(),
                    "png_sha256": report["png_sha256"], "campaign_sha256": report["campaign_sha256"], "release_sha256": report["release_sha256"]}
        atomic_json(self.path(artifact_id) / "approval.json", {"approval": approval, "signature": self.sign(approval)})
        return approval

    def release(self, artifact_id: str) -> tuple[bytes, dict]:
        png, report = self.candidate(artifact_id)
        try:
            record = json.loads((self.path(artifact_id) / "approval.json").read_text())
            approval = record["approval"]
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as exc:
            raise Hold("Owner review is pending; image withheld") from exc
        if not hmac.compare_digest(record["signature"], self.sign(approval)):
            raise Hold("Approval signature is invalid")
        if approval["status"] != "APPROVED" or any(approval.get(k) != report[k] for k in ["png_sha256", "campaign_sha256", "release_sha256"]):
            raise Hold("Creative was rejected or changed after review")
        return png, {**report, "publication_status": "APPROVED", "approval": approval}


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value):
    fd, temp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(value, handle, indent=2)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def live_source_gate():
    """Use deployed known code, a fixed source, and no model-controlled override."""
    load_locks()
    clean_env = {k: v for k, v in os.environ.items() if k not in {"BURST_SMS_PH_REPO_BASE_URL", "NODE_OPTIONS", "NODE_PATH"}}
    try:
        result = subprocess.run(["node", str(PLUGIN / "scripts/brand-preflight.mjs")], cwd=ROOT,
                                env=clean_env, capture_output=True, text=True, timeout=45)
    except (subprocess.SubprocessError, OSError) as exc:
        raise Hold("Live brand preflight unavailable; no image created") from exc
    if result.returncode != 0:
        raise Hold("Live brand preflight failed; source unavailable or release differs. No image created")
    receipt = json.loads(result.stdout)
    if receipt.get("gate") != "PASSED" or receipt.get("allowed") is not True:
        raise Hold("Live source gate did not pass")
