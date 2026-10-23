"""Installed-bundle smoke test for the Burst SMS PH renderer.

Diagnostic only. Keeps the probe PNG in memory and prints a JSON receipt.
Run this file from the installed skill bundle in a fresh Work conversation.
"""
import hashlib
import io
import json
import platform
from pathlib import Path


REQUIRED_FILES = (
    "assets/burst-sms-logo.png",
    "runtime/fonts/NotoSans-Regular.ttf",
    "runtime/fonts/OFL.txt",
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    root = Path(__file__).resolve().parents[1]
    result = {
        "pilot": "burst-sms-plugin-runtime-v1",
        "status": "BLOCKED",
        "python": platform.python_version(),
        "script_path": str(Path(__file__).resolve()),
        "skill_root": str(root),
        "checks": {},
        "scope": "This script path only; run from the installed Work plugin bundle, not a repository checkout.",
    }
    try:
        import PIL
        from PIL import Image, ImageChops, ImageDraw, ImageFont
        result["pillow"] = PIL.__version__

        manifest_path = root / "brand-integrity.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_files = manifest.get("files", {})
        for relative_path in REQUIRED_FILES:
            expected = expected_files.get(relative_path)
            if not expected:
                raise ValueError("Bundle manifest is missing " + relative_path)
            data = (root / relative_path).read_bytes()
            if sha256(data) != expected:
                raise ValueError("Installed bundle integrity failed: " + relative_path)
        result["checks"]["logo_font_and_license_match_manifest"] = True

        logo = Image.open(root / REQUIRED_FILES[0]).convert("RGBA")
        if logo.width < 1 or logo.height < 1:
            raise ValueError("Bundled Burst logo is empty")
        font = ImageFont.truetype(str(root / REQUIRED_FILES[1]), 28)
        result["checks"]["original_logo_loads"] = True
        result["checks"]["bundled_font_loads"] = True

        def render_probe():
            width = max(360, logo.width + 40)
            height = max(160, logo.height + 70)
            image = Image.new("RGBA", (width, height), "white")
            image.alpha_composite(logo, (20, 20))
            draw = ImageDraw.Draw(image)
            draw.text((20, 25 + logo.height), "Runtime diagnostic only", font=font, fill="black")
            placed = image.crop((20, 20, 20 + logo.width, 20 + logo.height))
            if ImageChops.difference(placed, logo).getbbox():
                raise ValueError("Master logo pixels changed")
            buffer = io.BytesIO()
            image.save(buffer, format="PNG", optimize=False)
            encoded = buffer.getvalue()
            with Image.open(io.BytesIO(encoded)) as decoded:
                if decoded.size != (width, height) or decoded.format != "PNG":
                    raise ValueError("In-memory PNG export failed")
            return encoded

        first = render_probe()
        if first != render_probe():
            raise ValueError("Identical probe renders produced different PNG bytes")
        result["checks"].update({
            "original_logo_pixels_preserved": True,
            "in_memory_png_export": True,
            "repeatable_png_bytes": True,
        })
        result["probe_sha256"] = sha256(first)
        result["status"] = "PASSED"
    except Exception as exc:
        result["reason"] = type(exc).__name__ + ": " + str(exc)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
