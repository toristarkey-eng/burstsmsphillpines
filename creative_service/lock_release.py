"""Maintainer-only lock refresh; never exposed to the agent as a tool."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
files = [str(p.relative_to(root)) for p in (root / "creative_service").rglob("*")
         if p.is_file() and (p.suffix in {".py", ".ttf"} or p.name in {"templates.json", "requirements.txt"}) and "__pycache__" not in p.parts]
files += ["plugins/burst-sms-ph-marketing-lab/scripts/brand-preflight.mjs", "plugins/burst-sms-ph-marketing-lab/brand-integrity.json"]
templates = json.loads((root / "creative_service/templates.json").read_text())
files += ["plugins/burst-sms-ph-marketing-lab/" + photo["file"] for photo in templates["photos"].values()]
files += ["design-system/tokens/tokens.json"]
files = sorted(set(files))
lock = {"schema_version": 1, "files": {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in files}}
(root / "creative_service/release-lock.json").write_text(json.dumps(lock, indent=2) + "\n")
