"""No arbitrary HTML, CSS, paths, colours, fonts, sizes or image URLs are accepted."""
from __future__ import annotations

import hashlib
import io
import json
import re
import unicodedata
from pathlib import Path
from typing import Literal

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "creative_service"
PLUGIN = ROOT / "plugins/burst-sms-ph-marketing-lab"
DESTINATION = "https://burstsms.com.ph/"
PALETTE = {"navy": "#002A66", "violet": "#4C23CC", "cyan": "#00AEC4", "blue": "#005677", "white": "#FFFFFF", "cloud": "#F4F5FF"}


class Hold(ValueError):
    """A failed gate; no image may be returned by a delivery tool."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def contrast(a: str, b: str) -> float:
    def luminance(colour):
        values = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        values = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in values]
        return sum(v * w for v, w in zip(values, (0.2126, 0.7152, 0.0722)))
    lighter, darker = sorted((luminance(a), luminance(b)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class Campaign(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    template_id: Literal["recognition", "customer-updates", "people-first", "team-coffee", "bold-statement", "offer-focus"]
    format: Literal["square", "portrait"] = "portrait"
    headline: str = Field(min_length=1, max_length=65)
    accent: str = Field(default="", max_length=45)
    supporting: str = Field(default="", max_length=130)
    primary_text: str = Field(min_length=1, max_length=1200)
    cta: Literal["Talk to our team", "Explore SMS solutions", "Explore branded Sender IDs", "Book a coffee chat"] = "Talk to our team"
    photo_id: str | None = Field(default=None, max_length=64)
    message: str = Field(default="", max_length=85)

    @model_validator(mode="after")
    def plain_copy(self):
        for name in ["headline", "accent", "supporting", "primary_text", "message"]:
            text = getattr(self, name)
            if text != text.strip():
                raise ValueError(f"{name}: remove outer whitespace")
            if any(unicodedata.category(c).startswith("C") and c != "\n" for c in text):
                raise ValueError(f"{name}: hidden/control characters are not allowed")
            if any(c in text for c in ["<", ">", "\u2014"]):
                raise ValueError(f"{name}: markup and em dashes are not allowed")
            # Narrow character repertoire is deliberate: no silent missing glyphs.
            if any(ord(c) > 0x024F and c not in "\u2018\u2019\u201c\u201d\u2013" for c in text):
                raise ValueError(f"{name}: unsupported character; use plain English text")
            if re.search(r"kudosity|[a-z][a-z0-9+.-]*://|mailto:|tel:|www\.|\b(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,63}\b|\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b|\b(?:best|number one|guaranteed)\b", text, re.I):
                raise ValueError(f"{name}: prohibited brand, link or unsupported superiority claim")
        if "\n" in self.headline or "\n" in self.accent or "\n" in self.supporting or "\n" in self.message:
            raise ValueError("Artwork fields must be single paragraphs; wrapping belongs to the renderer")
        return self


def load_locks() -> dict:
    """Validate all renderer inputs and code against the committed release lock."""
    lock = json.loads((SERVICE / "release-lock.json").read_text())
    if lock.get("schema_version") != 1 or not isinstance(lock.get("files"), dict):
        raise Hold("Release lock is invalid")
    required = {str(p.relative_to(ROOT)) for p in SERVICE.rglob("*")
                if p.is_file() and (p.suffix in {".py", ".ttf"} or p.name in {"templates.json", "requirements.txt"}) and "__pycache__" not in p.parts}
    required.update({"design-system/tokens/tokens.json", "plugins/burst-sms-ph-marketing-lab/scripts/brand-preflight.mjs", "plugins/burst-sms-ph-marketing-lab/brand-integrity.json"})
    templates = json.loads((SERVICE / "templates.json").read_text())
    required.update("plugins/burst-sms-ph-marketing-lab/" + photo["file"] for photo in templates["photos"].values())
    if not required.issubset(lock["files"]):
        raise Hold("Release lock omits a production input")
    for relative, expected in lock["files"].items():
        if Path(relative).is_absolute() or ".." in Path(relative).parts or not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise Hold("Release lock entry is invalid")
        if digest((ROOT / relative).read_bytes()) != expected:
            raise Hold(f"Release integrity mismatch: {relative}")
    integrity = json.loads((PLUGIN / "brand-integrity.json").read_text())
    for relative, expected in integrity["files"].items():
        if digest((ROOT / relative).read_bytes()) != expected:
            raise Hold(f"Approved brand asset integrity mismatch: {relative}")
    tokens = json.loads((ROOT / "design-system/tokens/tokens.json").read_text())
    for name in ["navy", "violet", "cyan", "blue"]:
        if tokens["color"]["brand"][name]["$value"] != PALETTE[name]:
            raise Hold(f"Brand token changed: {name}")
    if "Noto Sans" not in tokens["font"]["family"]["sans"]["$value"]:
        raise Hold("Required Noto Sans font family is missing")
    return lock


def catalog() -> dict:
    load_locks()
    return json.loads((SERVICE / "templates.json").read_text())


def font(size: int, bold: bool = False):
    return ImageFont.truetype(str(SERVICE / "fonts" / ("NotoSans-Bold.ttf" if bold else "NotoSans-Regular.ttf")), size)


class Canvas:
    def __init__(self, size):
        self.image = Image.new("RGB", size, PALETTE["cloud"])
        self.draw = ImageDraw.Draw(self.image)
        self.text_checks = []
        self.pending_text = []

    def text(self, text, box, size, colour="navy", bold=False, max_lines=3):
        if not text:
            return
        x, y, w, h = box
        if min(x, y) < 0 or min(w, h) <= 0 or x + w > self.image.width or y + h > self.image.height:
            raise Hold("Text box is outside the canvas")
        f = font(size, bold)
        lines, line = [], ""
        for word in text.split():
            if self.draw.textlength(word, font=f) > w:
                raise Hold("A word exceeds the locked text box")
            candidate = f"{line} {word}".strip()
            if self.draw.textlength(candidate, font=f) > w and line:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        line_h = round(size * 1.32)
        if len(lines) > max_lines or len(lines) * line_h > h:
            raise Hold("Copy overflows the template. Shorten it; font size will not be reduced")
        for i, line in enumerate(lines):
            bounds = self.draw.textbbox((x, y + i * line_h), line, font=f, anchor="lt")
            if bounds[0] < x or bounds[1] < y or bounds[2] > x + w or bounds[3] > y + h:
                raise Hold("Visible glyphs overflow the locked text box")
            self.pending_text.append(((x, y + i * line_h), line, f, colour))
        self.text_checks.append({"text": text, "box": box, "size": size, "lines": len(lines), "fits": True})

    def finish_text(self):
        """Check actual backgrounds after all shapes/photos, then paint text last."""
        occupied = Image.new("L", self.image.size)
        for position, text, face, colour in self.pending_text:
            mask = Image.new("L", self.image.size)
            ImageDraw.Draw(mask).text(position, text, font=face, fill=255, anchor="lt")
            visible = mask.point(lambda value: 255 if value else 0)
            if ImageChops.multiply(occupied, visible).getbbox():
                raise Hold("Text overlaps other text")
            bounds = visible.getbbox()
            if bounds:
                pixels = zip(self.image.crop(bounds).get_flattened_data(), visible.crop(bounds).get_flattened_data())
                for rgb in {rgb for rgb, alpha in pixels if alpha}:
                    if contrast(PALETTE[colour], "#%02x%02x%02x" % rgb) < 4.5:
                        raise Hold("Text contrast fails against the actual rendered background")
            occupied = ImageChops.lighter(occupied, visible)
            self.draw.text(position, text, font=face, fill=PALETTE[colour], anchor="lt")

    def photo(self, photo, box):
        source = Image.open(PLUGIN / photo["file"]).convert("RGB")
        crop = tuple(photo["crop"])
        if not (0 <= crop[0] < crop[2] <= source.width and 0 <= crop[1] < crop[3] <= source.height):
            raise Hold("Photo crop outside its approved source")
        # Contain, never cover: no additional automatic crop of faces or equipment.
        scaled = ImageOps.contain(source.crop(crop), (box[2], box[3]), Image.Resampling.LANCZOS)
        self.image.paste(scaled, (box[0] + (box[2] - scaled.width) // 2, box[1] + (box[3] - scaled.height) // 2))

    def bubble(self, text, box):
        x, y, w, h = box
        self.draw.rounded_rectangle((x, y, x + w, y + h), 30, fill=PALETTE["white"])
        self.text("YOUR BRAND", (x + 28, y + 25, w - 56, 40), 25, bold=True, max_lines=1)
        self.text(text or "Your update is here. Thank you!", (x + 28, y + 80, w - 56, h - 100), 29, max_lines=3)


def render(campaign: Campaign) -> tuple[bytes, dict]:
    try:
        campaign = Campaign.model_validate(campaign.model_dump())
    except ValidationError as exc:
        raise Hold("Campaign input is invalid") from exc
    lock = load_locks()
    config = catalog()
    template = config["templates"][campaign.template_id]
    photo = config["photos"].get(campaign.photo_id) if campaign.photo_id else None
    if campaign.photo_id and not photo:
        raise Hold("Photo is not registered")
    if template["photography"] != bool(photo):
        raise Hold("Choose a registered photo for this template, or omit it for a text template")
    if photo and campaign.template_id not in photo["templates"]:
        raise Hold("Photo is not registered for this template")
    if campaign.message and template["layout"] not in ["phone", "conversation"]:
        raise Hold("Message copy is only supported in messaging templates")
    width, height = config["formats"][campaign.format]
    c = Canvas((width, height))
    d = c.draw
    footer = height - 180
    # Fixed white header, original logo, separate divider and market descriptor.
    d.rectangle((0, 0, width, 150), fill=PALETTE["white"])
    logo = Image.open(PLUGIN / "assets/burst-sms-logo.png").convert("RGB")
    scaled_logo = logo.resize((logo.width * 2, logo.height * 2), Image.Resampling.LANCZOS)
    c.image.paste(scaled_logo, (56, 15))
    d.line((382, 48, 382, 107), fill=PALETTE["cyan"], width=2)
    descriptor_font = ImageFont.truetype(str(SERVICE / "fonts/NotoSans-SemiBold.ttf"), 24)
    tx = 415
    for letter in "PHILIPPINES":
        d.text((tx, 65), letter, fill=PALETTE["navy"], font=descriptor_font, anchor="lt")
        tx += d.textlength(letter, font=descriptor_font) + 3
    layout = template["layout"]
    if layout == "statement":
        d.rectangle((0, 151, width, footer), fill=PALETTE["navy"])
        d.ellipse((940, footer - 240, 1360, footer + 180), fill=PALETTE["cyan"])
        c.text(campaign.headline, (64, 215, 938, 285), 80, "white", True, 2)
        c.text(campaign.accent, (64, 490, 930, 140), 68, "cyan", True, 1)
        c.text(campaign.supporting, (68, 655 if height > 1080 else 650, 820, footer - 665), 32, "white", max_lines=3)
    elif layout == "feature":
        d.rectangle((0, 151, width, footer), fill=PALETTE["white"])
        d.rounded_rectangle((62, 203, 1018, footer - 48), 42, fill=PALETTE["cloud"])
        d.rectangle((62, 243, 72, footer - 88), fill=PALETTE["cyan"])
        c.text(campaign.headline, (105, 260, 810, 265), 76, bold=True, max_lines=2)
        c.text(campaign.accent, (105, 540, 810, 190), 64, "violet", True, 2)
        c.text(campaign.supporting, (108, 755 if height > 1080 else 745, 790, footer - 785), 31, max_lines=3)
    elif layout == "phone":
        c.text(campaign.headline, (64, 200, 940, 235), 70, bold=True, max_lines=2)
        c.text(campaign.accent, (64, 430, 940, 130), 62, "violet", True, 1)
        c.text(campaign.supporting, (64, 553, 470, footer - 585), 32, max_lines=3)
        d.ellipse((510, 570, 1020, footer - 25), outline=PALETTE["cyan"], width=20)
        d.rounded_rectangle((570, 545, 969, footer - 38), 47, fill=PALETTE["navy"])
        d.rounded_rectangle((588, 570, 951, footer - 63), 30, fill=PALETTE["white"])
        d.rounded_rectangle((698, 582, 842, 603), 10, fill=PALETTE["navy"])
        c.bubble(campaign.message, (605, 640, 330, min(280, footer - 718)))
    else:
        # These distinct layouts share a fixed, readable headline zone above photography.
        headline_y = 195
        c.text(campaign.headline, (64, headline_y, 940, 230), 68, bold=True, max_lines=2)
        c.text(campaign.accent, (64, 425, 940, 125), 58, "violet", True, 1)
        c.text(campaign.supporting, (64, 547, 940, 95), 30, max_lines=2)
        photo_y = 665 if height > 1080 else 650
        if layout == "team":
            d.polygon([(0, photo_y), (180, photo_y + 160), (0, footer)], fill=PALETTE["cyan"])
            d.polygon([(width, photo_y), (width - 180, photo_y + 160), (width, footer)], fill=PALETTE["violet"])
            c.photo(photo, (86, photo_y, 908, footer - photo_y - 20))
        elif layout == "split":
            d.rounded_rectangle((58, photo_y, 1022, footer - 25), 38, fill=PALETTE["white"])
            c.photo(photo, (80, photo_y + 6, 920, footer - photo_y - 36))
        else:
            c.photo(photo, (548, photo_y, 485, footer - photo_y - 20))
            c.bubble(campaign.message, (62, photo_y + 18, 459, min(300, footer - photo_y - 44)))
    d.rectangle((0, footer, width, height), fill=PALETTE["white"])
    cta_font = font(29, True)
    button_width = int(d.textlength(campaign.cta, font=cta_font)) + 64
    d.rounded_rectangle((64, footer + 28, 64 + button_width, footer + 100), 36, fill=PALETTE["violet"])
    d.text((96, footer + 48), campaign.cta, font=cta_font, fill=PALETTE["white"], anchor="lt")
    c.text("burstsms.com.ph", (68, footer + 121, 650, 45), 28, bold=True, max_lines=1)
    c.finish_text()
    logo_pixels = c.image.crop((56, 15, 56 + scaled_logo.width, 15 + scaled_logo.height))
    if ImageChops.difference(logo_pixels, scaled_logo).getbbox():
        raise Hold("Logo pixels changed after composition")
    buf = io.BytesIO()
    c.image.save(buf, format="PNG", optimize=False)
    png = buf.getvalue()
    if Image.open(io.BytesIO(png)).size != (width, height):
        raise Hold("PNG export dimensions changed")
    pairs = [("navy", "white"), ("navy", "cloud"), ("violet", "cloud"), ("white", "violet"), ("white", "navy"), ("cyan", "navy")]
    contrasts = {f"{a}_on_{b}": round(contrast(PALETTE[a], PALETTE[b]), 2) for a, b in pairs}
    if any(value < 4.5 for value in contrasts.values()):
        raise Hold("Locked text colour contrast failed")
    report = {
        "technical_status": "PASSED", "publication_status": "AWAITING_OWNER_REVIEW",
        "campaign": campaign.model_dump(), "campaign_sha256": digest(canonical(campaign.model_dump())),
        "png_sha256": digest(png), "release_sha256": digest(canonical(lock)),
        "dimensions": [width, height], "destination": DESTINATION,
        "template_reference": template["reference"], "photography": photo,
        "logo_source": "assets/burst-sms-logo.png", "logo_sha256": digest((PLUGIN / "assets/burst-sms-logo.png").read_bytes()),
        "palette": PALETTE, "typography": "Bundled Noto Sans Regular, SemiBold and Bold", "text_checks": c.text_checks,
        "alt_text": "Burst SMS Philippines: " + campaign.headline + (". " + campaign.accent if campaign.accent else "") + (". " + photo["alt"] if photo else ""),
        "channel_copy": campaign.primary_text + "\n\n" + campaign.cta + ": " + DESTINATION,
        "contrast_ratios": contrasts,
        "checks": {"asset_integrity": True, "logo_pixels": True, "locked_styles": True, "text_fit": True, "fixed_dimensions": True, "fixed_destination": True, "text_contrast": True},
        "requires_human_review": ["wording_and_claims", "visual_composition", "local_fit_and_photography", "accessibility", "publication_authority"]
    }
    return png, report
