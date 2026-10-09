"""Maintainer-only integrity refresh; not shipped as a skill tool or runtime bypass."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
skill = root / "plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab"
manifest = {
    "schema_version": 1,
    "plugin_name": "burst-sms-ph-marketing-lab",
    "plugin_id": "Plugin_f128b9ca740081918b32107ab5b22124",
    "plugin_version": "0.4.6",
    "repository": "https://github.com/toristarkey-eng/burstsmsphillpines",
    "runtime": "Work",
    "files": {str(p.relative_to(skill)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(skill.rglob("*")) if p.is_file() and p.name != "brand-integrity.json" and "__pycache__" not in p.parts and p.suffix != ".pyc"},
}
(skill / "brand-integrity.json").write_text(json.dumps(manifest, indent=2) + "\n")
