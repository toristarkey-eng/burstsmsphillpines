"""Build a separate review listing while preserving the installed skill bytes."""
import argparse
import json
import shutil
import zipfile
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if output.exists() or output.is_relative_to(source) or source.is_relative_to(output):
        parser.error("Use a new, separate output directory")
    manifest = json.loads((source / "plugin.json").read_text())
    name = manifest["name"] + "-review"
    target = output / name
    shutil.copytree(source, target)
    for relative in ("plugin.json", ".codex-plugin/plugin.json"):
        path = target / relative
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        data["name"] = name
        interface = data["extensions"]["com.openai"]["interface"] if "extensions" in data else data["interface"]
        interface["displayName"] += " Review"
        interface["shortDescription"] = "Private Work creative review"
        path.write_text(json.dumps(data, indent=2) + "\n")
    # The skill and its integrity manifest must remain byte-identical.
    for path in (source / "skills").rglob("*"):
        if path.is_file() and path.read_bytes() != (target / path.relative_to(source)).read_bytes():
            raise ValueError("A skill file changed during review packaging")
    archive = output / (name + ".zip")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zipped:
        for path in target.rglob("*"):
            if path.is_file():
                zipped.write(path, str(path.relative_to(output)))
    print(archive)

if __name__ == "__main__":
    main()
