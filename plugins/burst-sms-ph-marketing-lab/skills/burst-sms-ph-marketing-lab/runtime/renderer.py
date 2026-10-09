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
SERVICE = ROOT / "runtime"
PLUGIN = ROOT
APPROVED_LOGO_SHA256 = "3b6bb8131d6ce1bf81d7f2481d8b3159058c8e71e87e0d6b5f1582efde3341f2"
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
    brand_strip: Literal["top", "bottom"] = "top"
    composition: Literal["auto", "side-by-side", "text-first", "image-first"] = "auto"
    image_position: Literal["left", "centre", "right"] = "centre"

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
            if name == "message" and re.search(r"your (?:brand|message) here|placeholder|lorem ipsum|sample message", text, re.I):
                raise ValueError("Use a meaningful fictional SMS example, not placeholder message copy")
            if re.search(r"kudosity|[a-z][a-z0-9+.-]*://|mailto:|tel:|www\.|\b(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,63}\b|\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b|\b(?:best|number one|guaranteed)\b", text, re.I):
                raise ValueError(f"{name}: prohibited brand, link or unsupported superiority claim")
        if "\n" in self.headline or "\n" in self.accent or "\n" in self.supporting or "\n" in self.message:
            raise ValueError("Artwork fields must be single paragraphs; wrapping belongs to the renderer")
        return self


def load_locks() -> dict:
    """Verify the installed skill package locally, without a checkout or network."""
    try:
        lock = json.loads((ROOT / "brand-integrity.json").read_text())
        if lock.get("schema_version") != 1 or lock.get("plugin_name") != "burst-sms-ph-marketing-lab" or not isinstance(lock.get("files"), dict):
            raise Hold("Bundled integrity manifest is invalid")
        required = {"SKILL.md", "runtime/__init__.py", "runtime/renderer.py", "runtime/requirements.txt", "runtime/templates.json", "assets/tokens.json", "assets/burst-sms-logo.png", "scripts/render_creative.py", "scripts/brand_preflight.py", "assets/approved/burst-sms-ph-messaging-library-brief.docx"}
        required.update(str(p.relative_to(ROOT)) for folder in [ROOT / "runtime", ROOT / "scripts", ROOT / "references"] for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
        templates = json.loads((SERVICE / "templates.json").read_text())
        required.update(photo["file"] for photo in templates["photos"].values())
        if not required.issubset(lock["files"]):
            raise Hold("Bundled integrity manifest omits a required input")
        for relative, expected in lock["files"].items():
            file = ROOT / relative
            if Path(relative).is_absolute() or ".." in Path(relative).parts or not file.resolve().is_relative_to(ROOT.resolve()) or not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                raise Hold("Bundled integrity entry is invalid")
            if digest(file.read_bytes()) != expected:
                raise Hold(f"Bundled integrity mismatch: {relative}")
        if digest((ROOT / "assets/burst-sms-logo.png").read_bytes()) != APPROVED_LOGO_SHA256:
            raise Hold("Approved logo master changed")
        tokens = json.loads((ROOT / "assets/tokens.json").read_text())
        for name in ["navy", "violet", "cyan", "blue"]:
            if tokens["color"]["brand"][name]["$value"] != PALETTE[name]:
                raise Hold(f"Brand token changed: {name}")
        if tokens["color"]["neutral"]["white"]["$value"] != PALETTE["white"] or "Noto Sans" not in tokens["font"]["family"]["sans"]["$value"]:
            raise Hold("Required white or Noto Sans token changed")
        return lock
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        if isinstance(exc, Hold):
            raise
        raise Hold("Required bundled input is missing or invalid") from exc


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
        self.photo_checks = []

    def text(self, text, box, size, colour="navy", bold=False, max_lines=3):
        if not text:
            return 0
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
        used_height = (len(lines)-1)*line_h + self.draw.textbbox((0, 0), lines[-1], font=f, anchor="lt")[3]
        if len(lines) > max_lines or used_height > h:
            raise Hold("Copy overflows the template. Shorten it; font size will not be reduced")
        for i, line in enumerate(lines):
            bounds = self.draw.textbbox((x, y + i * line_h), line, font=f, anchor="lt")
            if bounds[0] < x or bounds[1] < y or bounds[2] > x + w or bounds[3] > y + h:
                raise Hold("Visible glyphs overflow the locked text box")
            self.pending_text.append(((x, y + i * line_h), line, f, colour))
        self.text_checks.append({"text": text, "box": box, "size": size, "lines": len(lines), "used_height": used_height, "fits": True})
        return used_height

    def copy_block(self, campaign, x, y, width, budget, dark=False, paint=True, column=False):
        # Choose from bounded approved sizes using actual wrapping, never free-form styles.
        for heading_size in ((64, 60, 56, 52, 48) if column else (80, 76, 72, 68, 64, 60, 56, 52)):
            probe = Canvas(self.image.size)
            cursor = y
            try:
                cursor += probe.text(campaign.headline, (x, cursor, width, budget), heading_size,
                                     "white" if dark else "navy", True, 4 if column else 2)
                if campaign.accent:
                    cursor += 12
                    cursor += probe.text(campaign.accent, (x, cursor, width, budget - (cursor-y)),
                                         max(42, heading_size-10), "cyan" if dark else "violet", True, 3 if column else 2)
                if campaign.supporting:
                    cursor += 28
                    cursor += probe.text(campaign.supporting, (x, cursor, width, budget - (cursor-y)),
                                         30, "white" if dark else "navy", False, 5 if column else 3)
                if cursor-y > budget:
                    continue
            except Hold:
                continue
            if paint:
                self.pending_text.extend(probe.pending_text)
                self.text_checks.extend(probe.text_checks)
            return cursor-y
        raise Hold("Copy exceeds the adaptive layout's readable size limits; shorten it")

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

    def photo(self, photo, box, position="centre"):
        source = Image.open(PLUGIN / photo["file"]).convert("RGB")
        crop = tuple(photo["crop"])
        if not (0 <= crop[0] < crop[2] <= source.width and 0 <= crop[1] < crop[3] <= source.height):
            raise Hold("Photo crop outside its approved source")
        x, y, w, h = box
        if min(x, y) < 0 or min(w, h) <= 0 or x+w > self.image.width or y+h > self.image.height:
            raise Hold("Photo region is outside the canvas")
        # The frame adapts to the registered panel rather than distorting or cropping people.
        panel = source.crop(crop)
        scale = min(w / panel.width, h / panel.height)
        size = (max(1, round(panel.width * scale)), max(1, round(panel.height * scale)))
        scaled = panel.resize(size, Image.Resampling.LANCZOS)
        px = x if position == "left" else x+w-scaled.width if position == "right" else x+(w-scaled.width)//2
        py = y+(h-scaled.height)//2
        self.image.paste(scaled, (px, py))
        self.photo_checks.append({"source": photo["file"], "registered_crop": list(crop),
                                  "region": list(box), "frame": [px, py, *size],
                                  "frame_filled": True, "complete_panel_preserved": True,
                                  "proportional_scale": True})

    def bubble(self, text, box):
        x, y, w, h = box
        self.draw.rounded_rectangle((x, y, x + w, y + h), 30, fill=PALETTE["white"])
        self.text("YOUR BRAND", (x + 28, y + 25, w - 56, 40), 25, bold=True, max_lines=1)
        message_height = self.text(text or "Your order is ready for collection. Thank you!", (x + 28, y + 80, w - 56, h - 100), 29, max_lines=4)
        self.draw.rounded_rectangle((x+15, y+65, x+w-15, y+80+message_height+15), 20, fill=PALETTE["cloud"])


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
    if template["photography"] != "optional" and template["photography"] != bool(photo):
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
    layout = "split" if template["layout"] == "phone" and photo else template["layout"]
    body_top, body_bottom = 195, footer - 28
    body_height = body_bottom - body_top
    has_visual = layout in ("phone", "split", "team", "conversation")
    side = layout in ("phone", "split", "team", "conversation") and campaign.composition in ("auto", "side-by-side")
    copy_width = 455 if side else 880 if layout == "feature" else 940
    copy_x = 561 if side and campaign.image_position == "left" else 100 if layout == "feature" else 64
    gap = 30
    budget = body_height-250 if side and layout == "conversation" else body_height if side or not has_visual else body_height-(350 if layout == "phone" else 260 if layout == "conversation" else 230)-gap
    try:
        copy_height = c.copy_block(campaign, copy_x, body_top, copy_width, budget,
                                  dark=layout == "statement", paint=False, column=side)
    except Hold:
        if not side or campaign.composition != "auto":
            raise
        side = False
        copy_width, copy_x = 940, 64
        budget = body_height-(350 if layout == "phone" else 260)-gap
        copy_height = c.copy_block(campaign, copy_x, body_top, copy_width, budget, paint=False)
    image_first = has_visual and campaign.composition == "image-first" and not side
    visual_height = body_height if side else body_height-copy_height-gap if has_visual else 0
    copy_y = body_top+(budget-copy_height)//2 if side else body_top+(body_height-copy_height)//2 if not has_visual else body_top+visual_height+gap if image_first else body_top
    visual_y = body_top if side or image_first else body_top+copy_height+gap
    if layout == "statement":
        d.rectangle((0, 151, width, footer), fill=PALETTE["navy"])
    elif layout == "feature":
        d.rectangle((0, 151, width, footer), fill=PALETTE["white"])
        d.rounded_rectangle((62, 175, 1018, footer-20), 42, fill=PALETTE["cloud"])
        d.rectangle((62, 215, 72, footer-60), fill=PALETTE["cyan"])
    c.copy_block(campaign, copy_x, copy_y, copy_width, copy_height, dark=layout == "statement", column=side)
    if layout == "phone":
        # Keep a realistic phone shape; a stacked phone is centred, never stranded at one side.
        phone_height = min(560, visual_height)
        phone_width = min(399, max(325, round(phone_height*0.70)))
        phone_x = (64 if campaign.image_position == "left" else 580) if side else (width-phone_width)//2
        phone_y = visual_y+(visual_height-phone_height)//2
        d.rounded_rectangle((phone_x, phone_y, phone_x+phone_width, phone_y+phone_height), 38, fill=PALETTE["navy"])
        d.rounded_rectangle((phone_x+18, phone_y+18, phone_x+phone_width-18, phone_y+phone_height-18), 26, fill=PALETTE["white"])
        d.rounded_rectangle((phone_x+phone_width//2-60, phone_y+28, phone_x+phone_width//2+60, phone_y+45), 8, fill=PALETTE["navy"])
        c.bubble(campaign.message, (phone_x+28, phone_y+65, phone_width-56, phone_height-90))
    elif layout == "conversation":
        photo_x = 64 if campaign.image_position == "left" else 548
        bubble_x = 575 if campaign.image_position == "left" else 64
        c.photo(photo, (photo_x, visual_y, 468, visual_height), campaign.image_position)
        c.bubble(campaign.message, (copy_x if side else bubble_x, body_bottom-220 if side else visual_y, 455 if side else 440, 220 if side else min(300, visual_height)))
    elif layout in ("split", "team"):
        photo_x = 64 if campaign.image_position == "left" else 548
        c.photo(photo, (photo_x if side else 64, visual_y, 468 if side else 952, visual_height), "centre" if side else campaign.image_position)
    d.rectangle((0, footer, width, height), fill=PALETTE["white"])
    cta_font = font(29, True)
    button_width = int(d.textlength(campaign.cta, font=cta_font)) + 64
    d.rounded_rectangle((64, footer + 28, 64 + button_width, footer + 100), 36, fill=PALETTE["violet"])
    d.text((96, footer + 48), campaign.cta, font=cta_font, fill=PALETTE["white"], anchor="lt")
    c.text("burstsms.com.ph", (68, footer + 121, 650, 45), 28, bold=True, max_lines=1)
    c.finish_text()
    logo_y = 15
    if campaign.brand_strip == "bottom":
        original = c.image.copy()
        c.image.paste(original.crop((0, 150, width, height)), (0, 0))
        c.image.paste(original.crop((0, 0, width, 150)), (0, height-150))
        logo_y = height-150+15
        for check in c.text_checks:
            check["box"] = list(check["box"])
            check["box"][1] -= 150
        for check in c.photo_checks:
            check["region"][1] -= 150
            check["frame"][1] -= 150
    logo_pixels = c.image.crop((56, logo_y, 56 + scaled_logo.width, logo_y + scaled_logo.height))
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
        "technical_status": "PASSED", "delivery_status": "INSPECTION_REQUIRED",
        "campaign": campaign.model_dump(), "campaign_sha256": digest(canonical(campaign.model_dump())),
        "png_sha256": digest(png), "release_sha256": digest(canonical(lock)),
        "dimensions": [width, height], "destination": DESTINATION,
        "template_reference": template["reference"], "photography": photo,
        "logo_source": "assets/burst-sms-logo.png", "logo_sha256": digest((PLUGIN / "assets/burst-sms-logo.png").read_bytes()),
        "palette": PALETTE, "typography": "Bundled Noto Sans Regular, SemiBold and Bold", "text_checks": c.text_checks,
        "body_layout": "side-by-side" if side else "image-first" if image_first else "stacked" if has_visual else "statement",
        "phone_message": (campaign.message or "Your order is ready for collection. Thank you!") if layout in ("phone", "conversation") else None,
        "photo_checks": c.photo_checks, "brand_strip": campaign.brand_strip, "logo_box": [56, logo_y, scaled_logo.width, scaled_logo.height],
        "alt_text": "Burst SMS Philippines: " + ". ".join(part.rstrip(". ") for part in [campaign.headline, campaign.accent, photo["alt"] if photo else ""] if part),
        "channel_copy": campaign.primary_text + "\n\n" + campaign.cta + ": " + DESTINATION,
        "contrast_ratios": contrasts,
        "checks": {"asset_integrity": True, "logo_pixels": True, "locked_styles": True, "text_fit": True, "fixed_dimensions": True, "fixed_destination": True, "text_contrast": True, "message_visible": layout not in ("phone", "conversation") or any(t["text"] == (campaign.message or "Your order is ready for collection. Thank you!") for t in c.text_checks), "photo_frame_fit": all(p["frame_filled"] and p["complete_panel_preserved"] for p in c.photo_checks)},
        "inspection_required": ["copy_and_claims", "visual_composition", "local_fit_and_photography", "accessibility"]
    }
    return png, report
