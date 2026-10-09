"""Diagnostic only: no campaign creative, network calls or external writes."""
import hashlib
import io
import json
import platform
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    root = Path(__file__).resolve().parents[1]
    result = {"pilot": "burst-work-runtime-v1", "status": "BLOCKED",
              "python": platform.python_version(), "checks": {},
              "scope": "This conversation only; not a production renderer or brand approval."}
    try:
        import PIL
        from PIL import Image, ImageChops, ImageDraw, ImageFont
        result["pillow"] = PIL.__version__
        expected = json.loads((root / "assets/integrity.json").read_text())
        for name, sha in expected.items():
            if digest((root / "assets" / name).read_bytes()) != sha:
                raise ValueError("Bundled asset integrity failed: " + name)
        result["checks"]["bundled_assets_intact"] = True
        logo = Image.open(root / "assets/burst-sms-logo.png").convert("RGBA")
        if logo.size != (145, 60):
            raise ValueError("Unexpected master logo dimensions")
        font = ImageFont.truetype(str(root / "assets/NotoSans-Regular.ttf"), 28)
        result["checks"]["bundled_font_loads"] = True
        result["checks"]["original_logo_loads"] = True
        def render_probe():
            image = Image.new("RGBA", (1080, 1350), "white")
            image.paste(logo, (50, 50))
            ImageDraw.Draw(image).text((50, 160), "Runtime diagnostic only", font=font, fill="black")
            if ImageChops.difference(image.crop((50, 50, 195, 110)), logo).getbbox():
                raise ValueError("Master logo pixels changed")
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            data = buffer.getvalue()
            with Image.open(io.BytesIO(data)) as decoded:
                if decoded.size != (1080, 1350) or decoded.format != "PNG":
                    raise ValueError("PNG export failed")
            return data
        first = render_probe()
        if first != render_probe():
            raise ValueError("PNG bytes differed between identical runs")
        result["checks"].update({"original_logo_pixels_preserved": True,
                                 "png_export_dimensions": True,
                                 "repeatable_png_bytes": True})
        result["probe_sha256"] = digest(first)
        result["status"] = "PASSED"
    except Exception as exc:
        result["reason"] = type(exc).__name__ + ": " + str(exc)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
