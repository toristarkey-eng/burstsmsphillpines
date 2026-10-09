"""No arbitrary HTML, CSS, paths, colours, fonts or image URLs are accepted."""
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
    format: Literal["square", "portrait", "landscape", "story", "custom"] = "portrait"
    dimensions: list[int] | None = Field(default=None, min_length=2, max_length=2)
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
    sender_name: str = Field(default="BURST SMS", min_length=1, max_length=11)
    phone_view: Literal["auto", "full", "detail"] = "auto"
    photo_backdrop: Literal["none", "cyan-ellipse"] = "none"
    offer_terms: str = Field(default="", max_length=160)
    image_treatment: Literal["panel", "rounded", "circle", "cutout"] = "panel"
    photo_crop: list[int] | None = Field(default=None, min_length=4, max_length=4)
    photo_description: str = Field(default="", max_length=180)

    @model_validator(mode="after")
    def plain_copy(self):
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9 ]{0,10}", self.sender_name) or self.sender_name != self.sender_name.strip():
            raise ValueError("Illustrative sender names require 1–11 plain alphanumeric characters/spaces")
        if self.sender_name.upper() in ("YOUR BRAND", "YOUR SHOP"):
            raise ValueError("Use a deliberate illustrative sender name, not a placeholder")
        if self.format == "custom":
            if self.dimensions is None:
                raise ValueError("Custom artwork requires explicit width and height in pixels")
            width, height = self.dimensions
            if not (600 <= width <= 4096 and 600 <= height <= 4096 and 0.5 <= height/width <= 2):
                raise ValueError("Custom artwork supports 600–4096px per side and aspect ratios from 2:1 to 1:2")
        elif self.dimensions is not None:
            raise ValueError("Dimensions are only permitted with explicitly requested custom artwork")
        for name in ["headline", "accent", "supporting", "primary_text", "message", "photo_description", "sender_name", "offer_terms"]:
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
        if "\n" in self.headline or "\n" in self.accent or "\n" in self.supporting or "\n" in self.message or "\n" in self.offer_terms:
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
        self.compact = size[1] < 900

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
        for heading_size in ((48, 44, 40, 36) if self.compact else (64, 60, 56, 52, 48) if column else (80, 76, 72, 68, 64, 60, 56, 52)):
            probe = Canvas(self.image.size)
            cursor = y
            try:
                cursor += probe.text(campaign.headline, (x, cursor, width, budget), heading_size,
                                     "white" if dark else "navy", True, 4 if column else 2)
                if campaign.accent:
                    cursor += 12
                    cursor += probe.text(campaign.accent, (x, cursor, width, budget - (cursor-y)),
                                         max(30 if self.compact else 42, heading_size-10), "cyan" if dark else "violet", True, 3 if column else 2)
                if campaign.supporting:
                    cursor += 16 if self.compact else 28
                    cursor += probe.text(campaign.supporting, (x, cursor, width, budget - (cursor-y)),
                                         24 if self.compact else 30, "white" if dark else "navy", False, 5 if column else 3)
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

    def photo(self, photo, box, position="centre", treatment="panel", backdrop="none"):
        source = Image.open(PLUGIN / photo["file"]).convert("RGBA")
        crop = tuple(photo["crop"])
        if not (0 <= crop[0] < crop[2] <= source.width and 0 <= crop[1] < crop[3] <= source.height):
            raise Hold("Photo crop outside its approved source")
        x, y, w, h = box
        if min(x, y) < 0 or min(w, h) <= 0 or x+w > self.image.width or y+h > self.image.height:
            raise Hold("Photo region is outside the canvas")
        panel = source.crop(crop)
        requested_treatment = treatment
        fallback = None
        native_alpha = panel.getchannel("A")
        # Never infer subject/background from brightness: white clothing/equipment and fine hair are foreground.
        # Use only a registered, professionally prepared straight-alpha source; otherwise retain original RGB.
        if treatment == "cutout" and not (photo.get("approved_subject_alpha") is True and native_alpha.getextrema() == (0,255)):
            treatment = "panel"
            fallback = "No approved subject alpha; retained original photograph background"
        alpha = native_alpha if treatment == "cutout" else Image.new("L", panel.size, 255)
        scale = min(w/panel.width, h/panel.height)
        size = (max(1, round(panel.width*scale)), max(1, round(panel.height*scale)))
        # Pillow RGBA resampling handles premultiplied colour, preserving soft source alpha without white-key fringes.
        scaled_rgba = panel.resize(size, Image.Resampling.LANCZOS)
        scaled = scaled_rgba.convert("RGB")
        mask = scaled_rgba.getchannel("A") if treatment == "cutout" else alpha.resize(size, Image.Resampling.LANCZOS)
        px = x if position == "left" else x+w-size[0] if position == "right" else x+(w-size[0])//2
        py = y+h-size[1]  # Anchor the subject to the visual group, not an arbitrary floating centre.
        if treatment in ("rounded", "circle"):
            shape = Image.new("L", size)
            sd = ImageDraw.Draw(shape)
            if treatment == "circle":
                sd.ellipse((0,0,size[0]-1,size[1]-1), fill=255)
            else:
                sd.rounded_rectangle((0,0,size[0]-1,size[1]-1), min(size)//8, fill=255)
            mask = ImageChops.multiply(mask, shape)
        # Composite optional backing and image through ONE mask, with exactly the same exclusive bounds.
        # No separate canvas ellipse can leak beyond the photo frame or around its corners.
        if backdrop == "cyan-ellipse":
            backing = Image.new("RGB", size, PALETTE["cyan"])
            ellipse = Image.new("L", size)
            ImageDraw.Draw(ellipse).ellipse((0,0,size[0]-1,size[1]-1), fill=255)
            backing_mask = ImageChops.multiply(ellipse, mask)
            self.image.paste(backing, (px,py), backing_mask)
        self.image.paste(scaled, (px,py), mask)
        self.photo_checks.append({"source": photo["file"], "registered_crop": list(crop),
            "region": list(box), "frame": [px,py,*size], "frame_filled": True,
            "complete_panel_preserved": treatment == "panel", "requested_treatment": requested_treatment,
            "image_treatment": treatment, "cutout_fallback": fallback, "photo_backdrop": backdrop,
            "mask_has_transparency": mask.getextrema()[0] < 255,
            "mask_bounds_match": True, "subject_and_edges_inspection_required": True,
            "proportional_scale": True})
        return self.photo_checks[-1]["frame"]

    def bubble(self, text, box, sender="BURST SMS", paint=True):
        """Measure before painting: both the sender card and message bubble hug actual content."""
        x, y, w, h = box
        inset, label_y, message_y = (20,16,55) if self.compact else (28,25,80)
        probe = Canvas(self.image.size)
        probe.text(sender,(x+inset,y+label_y,w-2*inset,40),20 if self.compact else 25,bold=True,max_lines=1)
        used = probe.text(text or "Your order is ready for collection. Thank you!",(x+inset,y+message_y,w-2*inset,h-message_y-18),22 if self.compact else 29,max_lines=4)
        card_height = message_y+used+18
        if paint:
            self.draw.rounded_rectangle((x,y,x+w-1,y+card_height-1),24,fill=PALETTE["white"])
            self.draw.rounded_rectangle((x+12,y+message_y-12,x+w-13,y+message_y+used+12),16,fill=PALETTE["cloud"])
            self.pending_text.extend(probe.pending_text)
            self.text_checks.extend(probe.text_checks)
            self.message_card = [x,y,w,card_height]
        return card_height

    def phone(self, campaign, box):
        """Proportional device or intentionally cropped close-up, with readable SMS UI."""
        x, y, region_width, region_height = box
        view = "full" if campaign.phone_view == "full" else "detail"
        device_height = min(680, region_height) if view == "full" else min(region_width, 370 if self.compact else 520)*2
        device_width = round(device_height*0.50)
        if device_width > region_width:
            device_width = region_width
            device_height = device_width*2
        if view == "full" and device_width < 260:
            raise Hold("Full phone view is too small to read; use detail view or a taller layout")
        # Compose outside the canvas so a close-up crops the device rather than changing its proportions.
        component = Canvas((device_width, device_height))
        d = component.draw
        rim = 10
        d.rounded_rectangle((0,0,device_width-1,device_height-1), 42, fill=PALETTE["navy"])
        d.rounded_rectangle((rim,rim,device_width-rim-1,device_height-rim-1), 32, fill=PALETTE["white"])
        d.rounded_rectangle((device_width//2-42,20,device_width//2+42,34),7,fill=PALETTE["navy"])
        # Sender navigation is separate from the conversation, not placeholder copy in its body.
        ui_size = (24 if self.compact else 28) if view == "detail" else 22
        d.line((24,65,18,72,24,79),fill=PALETTE["navy"],width=2)
        component.text(campaign.sender_name,(40,59,device_width-64,40),ui_size,bold=True,max_lines=1)
        d.line((rim+1,104,device_width-rim-2,104),fill=PALETTE["cloud"],width=2)
        message = campaign.message or "Your order is ready for collection. Thank you!"
        text_x, text_y, text_width = 35, 135, device_width-70
        used = component.text(message,(text_x,text_y,text_width,device_height-text_y-65),ui_size,max_lines=6)
        bubble_box=(24,120,device_width-24,text_y+used+16)
        d.rounded_rectangle(bubble_box,18,fill=PALETTE["cloud"])
        d.polygon([(24,text_y+used-6),(18,text_y+used+15),(42,text_y+used+15)],fill=PALETTE["cloud"])
        component.finish_text()
        visible_height=min(device_height,region_height,text_y+used+55) if view == "detail" else min(device_height,region_height)
        if text_y+used+16 > visible_height-8:
            raise Hold("Phone message is outside the visible device view; shorten the SMS or choose a taller composition")
        px=x+(region_width-device_width)//2
        py=y+(region_height-visible_height)//2
        self.image.paste(component.image.crop((0,0,device_width,visible_height)),(px,py))
        for check in component.text_checks:
            check["box"] = list(check["box"])
            check["box"][0] += px
            check["box"][1] += py
            self.text_checks.append(check)
        self.phone_check={"view":view,"device_dimensions":[device_width,device_height],
                          "visible_frame":[px,py,device_width,visible_height],
                          "sender_header":campaign.sender_name,"message_bubble":True,
                          "proportional_device":True,"message_fully_visible":True}



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
    if campaign.photo_crop is not None:
        if not photo:
            raise Hold("Photo crop requires a registered source")
        photo = {**photo, "crop": campaign.photo_crop}
    if photo and photo.get("requires_crop") and (campaign.photo_crop is None or not campaign.photo_description):
        raise Hold("Choose one coherent scene from the source sheet and describe the selected photograph")
    if campaign.photo_description:
        if not photo:
            raise Hold("Photo description requires photography")
        photo = {**photo, "alt": campaign.photo_description}
    if (campaign.image_treatment != "panel" or campaign.photo_backdrop != "none") and not photo:
        raise Hold("Photo treatment requires photography")
    if (campaign.phone_view != "auto" or campaign.sender_name != "BURST SMS") and template["layout"] not in ["phone", "conversation"]:
        raise Hold("Sender/device options require a messaging template")
    if campaign.message and template["layout"] not in ["phone", "conversation"]:
        raise Hold("Message copy is only supported in messaging templates")
    output_width, output_height = campaign.dimensions if campaign.format == "custom" else config["formats"][campaign.format]
    # Recompose at a common design width using the requested aspect ratio.
    # Only the completed, recomposed canvas is uniformly rasterised to export size.
    width, height = 1080, round(output_height*1080/output_width)
    export_scale = output_width/width
    c = Canvas((width, height))
    d = c.draw
    compact = c.compact
    header_height = 100 if compact else 150
    cta_height = 110 if compact else 180
    brand_y = 0 if campaign.brand_strip == "top" else height-header_height
    footer = height-cta_height if campaign.brand_strip == "top" else brand_y-cta_height
    # Fixed white header, original logo, separate divider and market descriptor.
    brand_canvas = Image.new("RGB", (width,header_height), PALETTE["white"])
    brand_draw = ImageDraw.Draw(brand_canvas)
    logo = Image.open(PLUGIN / "assets/burst-sms-logo.png").convert("RGB")
    logo_factor = 1.3 if compact else 2
    scaled_logo = logo.resize((round(logo.width*logo_factor), round(logo.height*logo_factor)), Image.Resampling.LANCZOS)
    logo_x, logo_y = 56, 10 if compact else 15
    brand_canvas.paste(scaled_logo, (logo_x,logo_y))
    brand_draw.line((280 if compact else 382, 28 if compact else 48, 280 if compact else 382, 72 if compact else 107), fill=PALETTE["cyan"], width=2)
    descriptor_font = ImageFont.truetype(str(SERVICE / "fonts/NotoSans-SemiBold.ttf"), 20 if compact else 24)
    tx = 310 if compact else 415
    for letter in "PHILIPPINES":
        brand_draw.text((tx, 40 if compact else 65), letter, fill=PALETTE["navy"], font=descriptor_font, anchor="lt")
        tx += brand_draw.textlength(letter, font=descriptor_font) + 3
    layout = ("conversation" if campaign.message or campaign.sender_name != "BURST SMS" else "split") if template["layout"] == "phone" and photo else template["layout"]
    if campaign.phone_view != "auto" and layout != "phone":
        raise Hold("Device view requires phone imagery; use auto for a photographic SMS card")
    body_top = (125 if compact else 195) if campaign.brand_strip == "top" else (25 if compact else 45)
    body_bottom = footer-(20 if compact else 28)
    body_height = body_bottom - body_top
    has_visual = layout in ("phone", "split", "team", "conversation")
    side = layout in ("phone", "split", "team", "conversation") and (campaign.composition == "side-by-side" or campaign.composition == "auto" and height <= 1500)
    copy_width = 455 if side else 880 if layout == "feature" else 940
    copy_x = 561 if side and campaign.image_position == "left" else 100 if layout == "feature" else 64
    gap = 20 if compact else 30
    budget = body_height if side or not has_visual else body_height-(350 if layout == "phone" else 260 if layout == "conversation" else 230)-gap
    try:
        copy_height = c.copy_block(campaign, copy_x, body_top, copy_width, budget,
                                  dark=layout == "statement", paint=False, column=side)
    except Hold:
        if not side or campaign.composition != "auto" or compact:
            raise
        side = False
        copy_width, copy_x = 940, 64
        budget = body_height-(350 if layout == "phone" else 260)-gap
        copy_height = c.copy_block(campaign, copy_x, body_top, copy_width, budget, paint=False)
    image_first = has_visual and campaign.composition == "image-first" and not side
    visual_height = body_height if side else body_height-copy_height-gap if has_visual else 0
    copy_y = body_top+(budget-copy_height)//2 if side else body_top+(body_height-copy_height)//2 if not has_visual else body_top+visual_height+gap if image_first else body_top
    visual_y = body_top if side or image_first else body_top+copy_height+gap
    if layout == "conversation" and not side:
        # Centre the actual copy/photo/card group, not a large empty visual allocation.
        group_width = 952
        measured_card = c.bubble(campaign.message,(64,visual_y,group_width,min(300,visual_height)),campaign.sender_name,paint=False)
        crop = photo["crop"]
        measured_photo = min(visual_height-measured_card-16, round(group_width*(crop[3]-crop[1])/(crop[2]-crop[0])))
        group_height = measured_photo+measured_card+16
        spare = max(0,visual_height-group_height)
        if image_first:
            visual_y += spare//2
            copy_y = visual_y+group_height+gap
        else:
            copy_y += spare//2
            visual_y += spare//2
        visual_height = group_height
    if layout == "statement":
        d.rectangle((0,header_height if campaign.brand_strip == "top" else 0,width,height if campaign.brand_strip == "top" else brand_y),fill=PALETTE["navy"])
    elif layout == "feature":
        d.rectangle((0,header_height if campaign.brand_strip == "top" else 0,width,footer),fill=PALETTE["cloud"] if campaign.brand_strip == "bottom" else PALETTE["white"])
        d.rounded_rectangle((62,body_top-20,1018,footer-20), 42, fill=PALETTE["cloud"])
        d.rectangle((62,body_top+20,72,footer-60), fill=PALETTE["cyan"])
    c.copy_block(campaign, copy_x, copy_y, copy_width, copy_height, dark=layout == "statement", column=side)
    if layout == "phone":
        c.phone(campaign, (64 if side and campaign.image_position == "left" else 548 if side else 64,
                           visual_y, 468 if side else 952, visual_height))
    elif layout == "conversation":
        # Photo and SMS share one aligned group in the visual column.
        group_width = 468 if side else 952
        group_x = (64 if campaign.image_position == "left" else 548) if side else (width-group_width)//2
        card_height = c.bubble(campaign.message,(group_x,visual_y,group_width,min(300,visual_height)),campaign.sender_name,paint=False)
        photo_budget = visual_height-card_height-16
        if photo_budget < 100:
            raise Hold("Photograph and SMS need more body space; shorten copy or change composition")
        frame = c.photo(photo,(group_x,visual_y,group_width,photo_budget),"centre",campaign.image_treatment,campaign.photo_backdrop)
        c.bubble(campaign.message,(group_x,frame[1]+frame[3]+16,group_width,card_height),campaign.sender_name)
    elif layout in ("split", "team"):
        photo_x = 64 if campaign.image_position == "left" else 548
        c.photo(photo, (photo_x if side else 64, visual_y, 468 if side else 952, visual_height), "centre" if side else campaign.image_position, campaign.image_treatment,campaign.photo_backdrop)
    if campaign.brand_strip == "top":
        d.rectangle((0,footer,width,height),fill=PALETTE["white"])
    cta_font = font(24 if compact else 29,True)
    button_width = round(d.textlength(campaign.cta,font=cta_font))+66
    button_y = footer+(18 if compact else 28)
    button_height = 52 if compact else 72
    button_box = [64,button_y,button_width,button_height]
    d.rounded_rectangle((64,button_y,64+button_width-1,button_y+button_height-1),button_height//2,fill=PALETTE["violet"])
    c.text(campaign.cta,(96,button_y+(14 if compact else 20),button_width-64,40),24 if compact else 29,"white",True,1)
    website_size = 20 if compact else 28
    website_width = round(d.textlength("burstsms.com.ph",font=font(website_size,True)))+2
    website_x = width-64-website_width
    same_line = website_x >= 64+button_width+40
    website_y = button_y+(16 if compact else 22) if same_line else footer+(80 if compact else 121)
    website_box = [website_x if same_line else 68,website_y,website_width,40]
    c.text("burstsms.com.ph",tuple(website_box),website_size,
           "white" if layout == "statement" and campaign.brand_strip == "bottom" else "navy",True,1)
    terms_box = None
    if campaign.offer_terms:
        terms_y = button_y+button_height+12 if same_line else website_y+36
        terms_box = [64,terms_y,width-128,footer+cta_height-terms_y-12]
        c.text(campaign.offer_terms,tuple(terms_box),22,
               "white" if layout == "statement" and campaign.brand_strip == "bottom" else "navy",False,4)
    # Paint the isolated brand bar last. Its pixels cannot contain CTA/campaign content.
    c.image.paste(brand_canvas,(0,brand_y))
    logo_y += brand_y
    protected_brand = [0,brand_y,width,header_height]
    cta_region = [0,footer,width,cta_height]
    for check in c.text_checks:
        tx,ty,tw,th = check["box"]
        if ty < brand_y+header_height and ty+check["used_height"] > brand_y:
            raise Hold("Campaign text intrudes into the brand-only bar")
    for check in c.photo_checks:
        px,py,pw,ph = check["frame"]
        if py+ph > footer or py < body_top:
            raise Hold("Photography intrudes into protected CTA/brand space")
    if not (footer <= button_y and website_y < footer+cta_height and (campaign.brand_strip != "bottom" or footer+cta_height == brand_y)):
        raise Hold("CTA placement does not follow the brand bar")
    if terms_box is not None:
        terms_check = next(check for check in reversed(c.text_checks) if check["text"] == campaign.offer_terms)
        if not (terms_box[0] >= 64 and terms_box[1] >= button_y+button_height+12 and footer <= terms_box[1] and terms_box[1]+terms_check["used_height"] <= footer+cta_height):
            raise Hold("Terms must fit alongside CTA inside its reserved region")
    c.finish_text()
    logo_pixels = c.image.crop((logo_x, logo_y, logo_x + scaled_logo.width, logo_y + scaled_logo.height))
    if ImageChops.difference(logo_pixels, scaled_logo).getbbox():
        raise Hold("Logo pixels changed after composition")
    if c.image.size != (output_width, output_height):
        c.image = c.image.resize((output_width, output_height), Image.Resampling.LANCZOS)
        for check in c.text_checks:
            check["box"] = [round(v*export_scale) for v in check["box"]]
            check["used_height"] = round(check["used_height"]*export_scale)
            check["size"] = round(check["size"]*export_scale)
        for check in c.photo_checks:
            for name in ("region", "frame"):
                check[name] = [round(v*export_scale) for v in check[name]]
        if hasattr(c, "phone_check"):
            for name in ("device_dimensions", "visible_frame"):
                c.phone_check[name] = [round(v*export_scale) for v in c.phone_check[name]]
        for box in (button_box,website_box,protected_brand,cta_region,terms_box,getattr(c,"message_card",None)):
            if box is not None:
                box[:] = [round(v*export_scale) for v in box]
        logo_x, logo_y = round(logo_x*export_scale), round(logo_y*export_scale)
        scaled_logo = logo.resize((round(logo.width*logo_factor*export_scale), round(logo.height*logo_factor*export_scale)), Image.Resampling.LANCZOS)
        c.image.paste(scaled_logo, (logo_x, logo_y))
        # The exported logo must remain the exact proportional master rasterisation.
        if ImageChops.difference(c.image.crop((logo_x, logo_y, logo_x+scaled_logo.width, logo_y+scaled_logo.height)), scaled_logo).getbbox():
            raise Hold("Exported logo pixels changed")
    buf = io.BytesIO()
    c.image.save(buf, format="PNG", optimize=False)
    png = buf.getvalue()
    if Image.open(io.BytesIO(png)).size != (output_width, output_height):
        raise Hold("PNG export dimensions changed")
    pairs = [("navy", "white"), ("navy", "cloud"), ("violet", "cloud"), ("white", "violet"), ("white", "navy"), ("cyan", "navy")]
    contrasts = {f"{a}_on_{b}": round(contrast(PALETTE[a], PALETTE[b]), 2) for a, b in pairs}
    if any(value < 4.5 for value in contrasts.values()):
        raise Hold("Locked text colour contrast failed")
    report = {
        "technical_status": "PASSED", "delivery_status": "INSPECTION_REQUIRED",
        "campaign": campaign.model_dump(), "campaign_sha256": digest(canonical(campaign.model_dump())),
        "png_sha256": digest(png), "release_sha256": digest(canonical(lock)),
        "dimensions": [output_width, output_height], "layout_dimensions": [width, height], "destination": DESTINATION,
        "template_reference": template["reference"], "photography": photo,
        "logo_source": "assets/burst-sms-logo.png", "logo_sha256": digest((PLUGIN / "assets/burst-sms-logo.png").read_bytes()),
        "palette": PALETTE, "typography": "Bundled Noto Sans Regular, SemiBold and Bold", "text_checks": c.text_checks,
        "body_layout": "side-by-side" if side else "image-first" if image_first else "stacked" if has_visual else "statement",
        "brand_region": protected_brand, "cta_region": cta_region, "cta_button": button_box,
        "terms_box": terms_box, "website_box": website_box, "cta_alignment": "same-line" if same_line else "stacked", "message_card": getattr(c,"message_card",None),
        "phone_check": getattr(c, "phone_check", None),
        "sender_name": campaign.sender_name if layout in ("phone", "conversation") else None,
        "phone_message": (campaign.message or "Your order is ready for collection. Thank you!") if layout in ("phone", "conversation") else None,
        "photo_checks": c.photo_checks, "brand_strip": campaign.brand_strip, "logo_box": [logo_x, logo_y, scaled_logo.width, scaled_logo.height],
        "alt_text": "Burst SMS Philippines: " + ". ".join(part.rstrip(". ") for part in [campaign.headline, campaign.accent, photo["alt"] if photo else "", ("Illustrative SMS from "+campaign.sender_name+": "+(campaign.message or "Your order is ready for collection. Thank you!")) if layout in ("phone","conversation") else ""] if part),
        "channel_copy": campaign.primary_text + "\n\n" + campaign.cta + ": " + DESTINATION + ("\n\nTerms: "+campaign.offer_terms if campaign.offer_terms else ""),
        "contrast_ratios": contrasts,
        "checks": {"asset_integrity": True, "logo_pixels": True, "locked_styles": True, "text_fit": True, "fixed_dimensions": True, "fixed_destination": True, "text_contrast": True, "message_visible": layout not in ("phone", "conversation") or any(t["text"] == (campaign.message or "Your order is ready for collection. Thank you!") for t in c.text_checks), "cta_placement": True, "brand_bar_separation": True, "terms_placement": True, "text_collisions": True, "mask_bounds": all(p["mask_bounds_match"] for p in c.photo_checks), "photo_frame_fit": all(p["frame_filled"] and p["proportional_scale"] for p in c.photo_checks)},
        "inspection_required": ["copy_and_claims", "visual_composition", "local_fit_and_photography", "accessibility", "photo_edges", "body_balance", "cta_and_terms", "campaign_effectiveness"]
    }
    return png, report
