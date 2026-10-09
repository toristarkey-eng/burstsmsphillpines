#!/usr/bin/env python3
"""Work-local rendering and a fail-closed delivery check; no hosting or credentials."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
INSPECTION_CHECKS = ("copy_and_claims", "visual_composition", "local_fit_and_photography", "accessibility", "photo_edges", "body_balance", "cta_and_terms", "campaign_effectiveness")


def read_json(path: Path, limit=131072):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON fields are not allowed")
            result[key] = value
        return result
    with path.open("rb") as stream:
        body = stream.read(limit + 1)
    if len(body) > limit:
        raise ValueError("Input is too large")
    return json.loads(body, object_pairs_hook=unique)


def json_file(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check_dependencies():
    if sys.version_info < (3, 11):
        raise ValueError("Python 3.11 or newer is required")
    versions = {}
    for line in (SKILL / "runtime/requirements.txt").read_text().splitlines():
        name, expected = line.split("==")
        version = importlib.metadata.version(name)
        if version != expected:
            raise ValueError("Install the bundled runtime/requirements.txt in a private virtual environment")
        versions[name] = version
    return versions


def candidate_file(directory, name):
    path = directory / name
    if not path.resolve().is_relative_to(directory.resolve()):
        raise ValueError("Candidate files must stay inside the private working directory")
    return path


def render_candidate(brief, directory, engine):
    # All rendering/checks happen in memory before a new private directory is created.
    campaign = engine.Campaign.model_validate(read_json(brief, 16384))
    png, report = engine.render(campaign)
    if directory.resolve().is_relative_to(SKILL.resolve()):
        raise ValueError("Use a new private directory outside the installed skill")
    directory.mkdir(parents=True, mode=0o700, exist_ok=False)
    (directory / "artwork.png").write_bytes(png)
    json_file(directory / "render-report.json", report)
    (directory / "recommended-copy.md").write_text(report["channel_copy"] + "\n", encoding="utf-8")
    return {"status": "INSPECTION_REQUIRED", "technical_status": "PASSED", "image_ready_for_delivery": False,
            "directory": str(directory.resolve()), "png_sha256": report["png_sha256"], "campaign_sha256": report["campaign_sha256"],
            "inspection_required": list(INSPECTION_CHECKS)}


def validate_delivery(directory, inspection_path, engine):
    receipt_path = candidate_file(directory, "delivery-validation.json")
    # Remove only this tool's stale receipt; a failed rerun must not leave PASSED.
    if receipt_path.exists():
        receipt_path.unlink()
    report = read_json(candidate_file(directory, "render-report.json"))
    campaign = engine.Campaign.model_validate(report["campaign"])
    expected_png, expected_report = engine.render(campaign)
    expected_report = json.loads(json.dumps(expected_report))
    with candidate_file(directory, "artwork.png").open("rb") as stream:
        png = stream.read(8 * 1024 * 1024 + 1)
    if png != expected_png or report != expected_report:
        raise ValueError("Candidate image or record differs from the locked deterministic render")
    if candidate_file(directory, "recommended-copy.md").read_text() != report["channel_copy"] + "\n":
        raise ValueError("Recommended copy changed after rendering")
    inspection = read_json(inspection_path, 16384)
    if not isinstance(inspection, dict) or set(inspection) != {"png_sha256", "campaign_sha256", "checks", "notes"}:
        raise ValueError("Final inspection fields are invalid")
    if any(inspection.get(key) != report[key] for key in ("png_sha256", "campaign_sha256")):
        raise ValueError("Inspect the exact current artwork and wording")
    checks, notes = inspection["checks"], inspection["notes"]
    if not isinstance(checks, dict) or set(checks) != set(INSPECTION_CHECKS) or any(value is not True for value in checks.values()):
        raise ValueError("Every final brand/content inspection must pass")
    if not isinstance(notes, dict) or set(notes) != set(INSPECTION_CHECKS) or any(not isinstance(value, str) or not 15 <= len(value.strip()) <= 2000 for value in notes.values()):
        raise ValueError("Record actual inspection results and claim sources/holds for every check")
    receipt = {"status": "PASSED", "image_ready_for_delivery": True, "runtime": "Work",
               "publication_status": "NOT_PUBLISHED", "png_sha256": report["png_sha256"], "campaign_sha256": report["campaign_sha256"],
               "package_sha256": report["release_sha256"], "dimensions": report["dimensions"], "destination": report["destination"],
               "technical_checks": report["checks"], "inspection": inspection, "alt_text": report["alt_text"],
               "visual": "artwork.png", "recommended_copy": "recommended-copy.md"}
    json_file(receipt_path, receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface", choices=("work", "chat"), required=True,
                        help="Calling surface; skill instructions require actual Work execution. This is not host authentication.")
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("preflight")
    actions.add_parser("catalog")
    render = actions.add_parser("render")
    render.add_argument("--brief", type=Path, required=True)
    render.add_argument("--output-dir", type=Path, required=True)
    validate = actions.add_parser("validate")
    validate.add_argument("--directory", type=Path, required=True)
    validate.add_argument("--inspection", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.surface != "work":
        print(json.dumps({"status": "HOLD", "reason": "Creative production requires Work. Open this request in Work with Burst SMS PH Marketing Lab.", "image_ready_for_delivery": False}), file=sys.stderr)
        return 1
    try:
        if args.action == "validate":
            stale = candidate_file(args.directory, "delivery-validation.json")
            if stale.exists():
                stale.unlink()
        sys.path.insert(0, str(SKILL))
        from runtime import renderer as engine
        engine.load_locks()
        versions = check_dependencies()
        if args.action == "preflight":
            result = {"status": "PASSED", "plugin": "burst-sms-ph-marketing-lab", "version": "0.4.3", "runtime_versions": versions, "logo_sha256": engine.APPROVED_LOGO_SHA256}
        elif args.action == "catalog":
            result = engine.catalog()
        elif args.action == "render":
            result = render_candidate(args.brief, args.output_dir, engine)
        else:
            result = validate_delivery(args.directory, args.inspection, engine)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError) as exc:
        print(json.dumps({"status": "HOLD", "reason": str(exc), "image_ready_for_delivery": False}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
