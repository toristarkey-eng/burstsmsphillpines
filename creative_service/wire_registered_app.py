"""Bind the existing plugin to an already registered, verified MCP app."""
import argparse
import json
import re
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--app-id", required=True, help="Verified app ID, not the plugin ID")
args = parser.parse_args()
if not re.fullmatch(r"(?:asdk_app_|connector_|templated_apps_)[A-Za-z0-9_]+", args.app_id):
    parser.error("Use the verified app ID returned by ChatGPT; do not supply a plugin_ ID")
root = Path(__file__).resolve().parents[1] / "plugins/burst-sms-ph-marketing-lab"
binding = {"apps": {"controlled-creative": {"id": args.app_id, "required": True}}}
path = root / ".app.json"
if path.exists():
    existing = json.loads(path.read_text())
    if "controlled-creative" in existing.get("apps", {}) and existing["apps"]["controlled-creative"]["id"] != args.app_id:
        parser.error("An existing controlled-creative app binding differs; reconcile it explicitly")
    existing.setdefault("apps", {}).update(binding["apps"])
    binding = existing
path.write_text(json.dumps(binding, indent=2) + "\n")
for relative in ["plugin.json", ".codex-plugin/plugin.json"]:
    manifest_path = root / relative
    manifest = json.loads(manifest_path.read_text())
    if relative == "plugin.json":
        manifest.setdefault("extensions", {}).setdefault("com.openai", {})["apps"] = "./.app.json"
    else:
        manifest["apps"] = "./.app.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
print("App binding written. Review and commit these changes, sync the existing marketplace, and enable the app for the intended roles.")
