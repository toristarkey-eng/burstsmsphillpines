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
    creative_style: Literal["default", "high-energy-casual"] = "default"
    energy_treatment: Literal["diagonal", "bands", "none"] = "diagonal"
    prop_id: str | None = Field(default=None, max_length=64)
    template_id: Literal["recognition", "customer-updates", "people-first", "team-coffee", "bold-statement", "offer-focus", "person-plus-message", "graphic-focus"]
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
    composition: Literal["auto", "side-by-side", "text-first", "image-first", "hero", "photo-background", "person-plus-message", "graphic-hero"] = "auto"
    imagery_channel: Literal["sms", "rcs", "whatsapp", "viber"] = "sms"
    channel_request: str = Field(default="", max_length=240)
    graphic_id: str | None = Field(default=None, max_length=64)
    graphic_colour: Literal["brand", "navy", "violet", "cyan"] = "brand"
    graphic_placement: Literal["adjacent", "layered"] = "adjacent"
    graphic_decoration: Literal["none", "cyan-band"] = "none"
    image_position: Literal["left", "centre", "right"] = "centre"
    sender_name: str = Field(default="BURST SMS", min_length=1, max_length=11)
    phone_view: Literal["auto", "full", "detail", "card"] = "auto"
    sms_position: Literal["upper-left", "upper-right", "middle-left", "middle-right", "lower-left", "lower-right"] = "lower-left"
    heading_style: Literal["light", "navy"] = "light"
    photo_fit: Literal["contain", "cover"] = "contain"
    message_placement: Literal["below", "beside"] = "below"
    photo_backdrop: Literal["none", "cyan-ellipse"] = "none"
    offer_terms: str = Field(default="", max_length=160)
    image_treatment: Literal["panel", "rounded", "circle", "cutout"] = "panel"
    photo_crop: list[int] | None = Field(default=None, min_length=4, max_length=4)
    photo_description: str = Field(default="", max_length=180)

    @model_validator(mode="after")
    def plain_copy(self):
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9 ]{0,10}", self.sender_name) or self.sender_name != self.sender_name.strip():
            raise ValueError("Illustrative sender names require 1–11 plain alphanumeric characters/spaces")
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

    def copy_block(self, campaign, x, y, width, budget, dark=False, paint=True, column=False, heading_sizes=None):
        # Choose from bounded approved sizes using actual wrapping, never free-form styles.
        for heading_size in (heading_sizes or ((48, 44, 40, 36) if self.compact else (64, 60, 56, 52, 48) if column else (80, 76, 72, 68, 64, 60, 56, 52))):
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

    def energy_copy(self, campaign, x, y, width, budget, paint=True):
        for size in ((60,56,52) if self.compact else (96,88,80)):
            probe=Canvas(self.image.size); cursor=y
            try:
                cursor+=probe.text(campaign.headline,(x,cursor,width,budget),size,"navy",True,2)
                if campaign.accent:
                    cursor+=12
                    cursor+=probe.text(campaign.accent,(x,cursor,width,budget-(cursor-y)),36 if self.compact else 52,"violet",True,2)
                if campaign.supporting:
                    cursor+=16
                    cursor+=probe.text(campaign.supporting,(x,cursor,width,budget-(cursor-y)),24 if self.compact else 28,"navy",False,2)
            except Hold:
                continue
            if paint:
                self.pending_text.extend(probe.pending_text);self.text_checks.extend(probe.text_checks)
            return cursor-y
        raise Hold("High-energy copy exceeds readable limits; shorten the headline/supporting copy or change format")

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

    def photo(self, photo, box, position="centre", treatment="panel", backdrop="none", fit="contain"):
        source = Image.open(PLUGIN / photo["file"]).convert("RGBA")
        crop = tuple(photo["crop"])
        if not (0 <= crop[0] < crop[2] <= source.width and 0 <= crop[1] < crop[3] <= source.height):
            raise Hold("Photo crop outside its approved source")
        x, y, w, h = box
        if min(x, y) < 0 or min(w, h) <= 0 or x+w > self.image.width or y+h > self.image.height:
            raise Hold("Photo region is outside the canvas")
        panel = source.crop(crop)
        effective_crop = list(crop)
        if fit == "cover":
            # A deliberate photographic crop fills the region; never warp subjects.
            ratio = w/h
            if panel.width/panel.height > ratio:
                crop_width = max(1,round(panel.height*ratio))
                offset = 0 if position == "left" else panel.width-crop_width if position == "right" else (panel.width-crop_width)//2
                panel=panel.crop((offset,0,offset+crop_width,panel.height))
                effective_crop[0]+=offset; effective_crop[2]=effective_crop[0]+crop_width
            else:
                crop_height=max(1,round(panel.width/ratio))
                # Top anchoring preserves faces; actual hands/equipment/framing still require inspection.
                panel=panel.crop((0,0,panel.width,crop_height))
                effective_crop[3]=effective_crop[1]+crop_height
        requested_treatment = treatment
        fallback = None
        native_alpha = panel.getchannel("A")
        # Never infer subject/background from brightness: white clothing/equipment and fine hair are foreground.
        # Use only a registered, professionally prepared straight-alpha source; otherwise retain original RGB.
        if treatment == "cutout" and not (photo.get("approved_subject_alpha") is True and native_alpha.getextrema() == (0,255)):
            treatment = "panel"
            fallback = "No approved subject alpha; retained original photograph background"
        alpha = native_alpha if treatment == "cutout" else Image.new("L", panel.size, 255)
        scale = (max if fit == "cover" else min)(w/panel.width, h/panel.height)
        size = (max(1, round(panel.width*scale)), max(1, round(panel.height*scale)))
        # Pillow RGBA resampling handles premultiplied colour, preserving soft source alpha without white-key fringes.
        scaled_rgba = panel.resize(size, Image.Resampling.LANCZOS)
        if fit == "cover":
            ox,oy=(size[0]-w)//2,(size[1]-h)//2
            scaled_rgba=scaled_rgba.crop((ox,oy,ox+w,oy+h))
            size=(w,h)
            alpha=Image.new("L",size,255)
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
            "effective_crop": effective_crop, "photo_fit": fit, "additional_crop_inspection_required": fit == "cover",
            "region": list(box), "frame": [px,py,*size], "frame_filled": True,
            "complete_panel_preserved": treatment == "panel", "requested_treatment": requested_treatment,
            "image_treatment": treatment, "cutout_fallback": fallback, "photo_backdrop": backdrop,
            "mask_has_transparency": mask.getextrema()[0] < 255,
            "mask_bounds_match": True, "subject_and_edges_inspection_required": True,
            "proportional_scale": True})
        return self.photo_checks[-1]["frame"]

    def graphic(self, asset, box, colour="brand"):
        source=Image.open(PLUGIN/asset["file"])
        if (not asset.get("recolour_allowed") and not asset.get("preserve_channel_identity")) or (asset.get("native_alpha") and ("A" not in source.getbands() or source.getchannel("A").getextrema()[0] != 0)):
            raise Hold("Campaign graphic registration or alpha is invalid")
        x,y,w,h=box
        if min(x,y)<0 or min(w,h)<=0 or x+w>self.image.width or y+h>self.image.height:
            raise Hold("Graphic region leaves the canvas")
        crop=asset["crop"]
        if not (0<=crop[0]<crop[2]<=source.width and 0<=crop[1]<crop[3]<=source.height):
            raise Hold("Graphic crop leaves its registered source")
        panel=source.convert("RGBA").crop(tuple(crop))
        label=asset.get("sender_label_overlay")
        if label:
            bx,by,bw,bh=label["source_box"];bx-=crop[0];by-=crop[1]
            if min(bx,by)<0 or bx+bw>panel.width or by+bh>panel.height:raise Hold("Registered sender-label repair leaves the graphic")
            draw=ImageDraw.Draw(panel);draw.rectangle((bx,by,bx+bw,by+bh),fill=PALETTE["white"])
            label_font=font(label["font_size"],True)
            if draw.textlength(label["text"],font=label_font)>bw:raise Hold("Registered sender label does not fit")
            draw.text((bx,by+4),label["text"],font=label_font,fill=PALETTE["navy"])
        scale=min(w/panel.width,h/panel.height)
        if asset.get("max_upscale") is not None and scale>asset["max_upscale"]:
            raise Hold("Graphic source is too small for this export; use a larger original or deterministic recreation")
        size=(round(panel.width*scale),round(panel.height*scale))
        if size[0]<asset["min_rendered_width"]:
            raise Hold("Graphic text/details would be too small; use graphic-hero or a simpler registered graphic")
        # Bounded palette mapping is deterministic; no arbitrary colour/URL/logo/photo mutations.
        names=list(PALETTE) if colour=="brand" else list(dict.fromkeys(["navy",colour,"cloud","white"]))
        colours=[tuple(int(PALETTE[name][i:i+2],16) for i in (1,3,5)) for name in names]
        # Prepared illustrations retain dimensional depth through controlled tints of
        # exact locked brand colours, never arbitrary generated palette values.
        prepared=colour=="brand" and asset.get("prepared_brand_palette")
        if prepared:
            bases=[tuple(int(PALETTE[name][i:i+2],16) for i in (1,3,5)) for name in ("navy","violet","cyan","blue")]
            colours=[tuple(round(value+(255-value)*step/63) for value in base) for base in bases for step in range(64)]
            colours[-1]=tuple(int(PALETTE["cloud"][i:i+2],16) for i in (1,3,5))
        palette=Image.new("P",(1,1));palette.putpalette([v for i in range(256) for v in colours[i%len(colours)]])
        rgb=panel.convert("RGB")
        if prepared:
            # Approved recolouring: replace warm pink/red illustration accents
            # with cyan before shade mapping, rather than washing them to grey.
            hue,saturation,value=rgb.convert("HSV").split()
            warm=ImageChops.multiply(hue.point(lambda v:255 if v<=20 or v>=235 else 0),saturation.point(lambda v:255 if v>=16 else 0))
            hue.paste(132,mask=warm)
            rgb=Image.merge("HSV",(hue,saturation,value)).convert("RGB")
        rgb=rgb.quantize(palette=palette,dither=Image.Dither.NONE).convert("RGB")
        mark=asset.get("protected_channel_mark_box")
        if mark:
            mx,my,mw,mh=mark;mx-=crop[0];my-=crop[1]
            if min(mx,my)<0 or mx+mw>panel.width or my+mh>panel.height:raise Hold("Registered channel mark leaves the graphic")
            rgb.paste(panel.convert("RGB").crop((mx,my,mx+mw,my+mh)),(mx,my))
        alpha=panel.getchannel("A").point(lambda value:0 if value<=2 else value)
        rgba=rgb.convert("RGBA");rgba.putalpha(alpha);rgba=rgba.resize(size,Image.Resampling.LANCZOS)
        px=x+(w-size[0])//2;py=y+(h-size[1])//2
        self.image.paste(rgba,(px,py),rgba.getchannel("A"))
        self.graphic_check={"id":asset["id"],"source":asset["file"],"frame":[px,py,*size],"region":list(box),
            "proportional_scale":True,"minimum_readable_width":asset["min_rendered_width"],"palette":{} if asset.get("preserve_channel_identity") else {name:PALETTE[name] for name in names},
            "channel_identity_preserved":bool(asset.get("preserve_channel_identity")), "sender_label_repair":label,
            "palette_mapping":"approved channel artwork identity preserved; surrounding illustration mapped to locked brand tints" if asset.get("preserve_channel_identity") else "controlled tints of exact locked brand hues; no dither; native alpha retained" if colour=="brand" and asset.get("prepared_brand_palette") else "nearest approved palette; no dither; native alpha retained except alpha <=2 noise",
            "embedded_text":asset["embedded_text"],"embedded_text_fit_and_contrast":"actual full/feed visual inspection required", "approved_source":asset["approval_source"]}
        return self.graphic_check["frame"]

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

    def sms_overlay(self, campaign, box, paint=True):
        x,y,w,h=box
        probe=Canvas(self.image.size)
        probe.text(campaign.sender_name,(x+20,y+16,w-40,28),20,bold=True,max_lines=1)
        used=probe.text(campaign.message,(x+20,y+50,w-40,h-64),22,max_lines=4)
        card_height=50+used+14
        if paint:
            self.draw.rounded_rectangle((x,y,x+w-1,y+card_height-1),18,fill=PALETTE["white"])
            self.draw.rounded_rectangle((x+10,y+44,x+w-11,y+50+used+7),12,fill=PALETTE["cloud"])
            self.pending_text.extend(probe.pending_text); self.text_checks.extend(probe.text_checks)
            self.message_card=[x,y,w,card_height]
        return card_height

    def phone(self, campaign, box):
        """Proportional device or intentionally cropped close-up, with readable SMS UI."""
        x, y, region_width, region_height = box
        view = "full" if campaign.phone_view == "auto" else campaign.phone_view
        if view == "card" or view == "full" and campaign.phone_view == "auto" and region_height < 520:
            used = self.bubble(campaign.message,(x,y,region_width,min(region_height,300)),campaign.sender_name,paint=False)
            py=y+(region_height-used)//2
            self.bubble(campaign.message,(x,py,region_width,used),campaign.sender_name)
            self.phone_check={"view":"card","device_dimensions":None,"visible_frame":[x,py,region_width,used],
                "sender_header":campaign.sender_name,"message_bubble":True,"proportional_device":True,
                "message_fully_visible":True,"unintended_device_crop":False}
            return
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
        ui_size = (24 if self.compact else 28) if view == "detail" else 24
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
                          "proportional_device":True,"message_fully_visible":True,"unintended_device_crop":False}



def render(campaign: Campaign) -> tuple[bytes, dict]:
    try:
        campaign = Campaign.model_validate(campaign.model_dump())
    except ValidationError as exc:
        raise Hold("Campaign input is invalid") from exc
    lock = load_locks()
    config = catalog()
    template = config["templates"][campaign.template_id]
    photo = config["photos"].get(campaign.photo_id) if campaign.photo_id else None
    graphic=config.get("graphics",{}).get(campaign.graphic_id) if campaign.graphic_id else None
    graphic_hero=campaign.template_id=="graphic-focus" or campaign.composition=="graphic-hero"
    if campaign.graphic_id and (not graphic or campaign.template_id not in graphic["templates"]):
        raise Hold("Graphic is not registered for this template; references cannot be rendered")
    if graphic:graphic={**graphic,"id":campaign.graphic_id}
    if campaign.imagery_channel!="sms":
        if not re.search(r"\b"+re.escape(campaign.imagery_channel)+r"\b",campaign.channel_request,re.I):
            raise Hold("Channel imagery requires an explicit user request excerpt naming that channel")
        if not graphic or graphic.get("channel")!=campaign.imagery_channel:
            raise Hold("Choose registered imagery matching the explicitly requested channel")
    if graphic and graphic.get("requires_explicit_channel"):
        if campaign.imagery_channel!=graphic["channel"] or campaign.graphic_colour!="brand":
            raise Hold("Channel-specific imagery requires its explicit channel request and unchanged channel identity")
    if not graphic and campaign.graphic_colour!="brand":
        raise Hold("Graphic colour selection requires a registered graphic")
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
    if (campaign.image_treatment != "panel" or campaign.photo_backdrop != "none" or campaign.photo_fit != "contain" or campaign.composition == "hero" or campaign.heading_style == "navy") and not photo and not (graphic_hero and campaign.heading_style=="navy" and campaign.image_treatment=="panel" and campaign.photo_backdrop=="none" and campaign.photo_fit=="contain"):
        raise Hold("Photo treatment requires photography")
    person_message = campaign.template_id == "person-plus-message" or campaign.composition == "person-plus-message"
    if graphic and not (person_message or graphic_hero):
        raise Hold("Registered graphics require person-plus-message or graphic-hero composition")
    if graphic and (campaign.message or campaign.sender_name!="BURST SMS" or campaign.phone_view!="auto"):
        raise Hold("Approved graphic supplies its own illustrative content; remove conflicting SMS/device inputs")
    if graphic_hero and (not graphic or photo or campaign.format not in ("square","portrait") or campaign.creative_style!="default" or campaign.graphic_placement!="adjacent" or campaign.graphic_decoration!="none" or campaign.photo_crop is not None or campaign.photo_description or campaign.image_treatment!="panel" or campaign.photo_backdrop!="none" or campaign.photo_fit!="contain" or campaign.composition not in ("auto","graphic-hero")):
        raise Hold("Graphic-hero requires one registered graphic, square/portrait and no photography/device/crop/energy options")
    if (campaign.graphic_decoration != "none" or campaign.graphic_placement != "adjacent") and not person_message:
        raise Hold("Graphic decoration requires person-plus-message composition")
    if person_message and (not photo or campaign.format not in ("square", "portrait") or campaign.brand_strip != "bottom" or campaign.heading_style != "navy" or (not graphic and (not campaign.message )) or campaign.image_position not in ("left", "right") or campaign.photo_fit != "contain" or campaign.photo_backdrop != "none" or campaign.image_treatment not in ("panel", "cutout") or campaign.phone_view not in ("auto", "card", "full") or campaign.creative_style != "default" or campaign.composition not in ("auto", "person-plus-message") or campaign.message_placement != "below" or campaign.sms_position != "lower-left"):
        raise Hold("Person-plus-message requires square/portrait, registered photography, navy heading, bottom brand bar, left/right subject, an explicit fictional sender/message and contained panel or approved cutout; use card or complete phone")
    if person_message and photo.get("approved_subject_alpha") is True:
        prepared=Image.open(PLUGIN/photo["file"])
        if "A" not in prepared.getbands() or prepared.getchannel("A").getextrema() != (0,255) or campaign.image_treatment != "cutout":
            raise Hold("Prepared transparent subjects require native alpha and cutout treatment")
        bbox=prepared.getchannel("A").getbbox();crop=photo["crop"]
        if not bbox or bbox[0]<crop[0] or bbox[1]<crop[1] or bbox[2]>crop[2] or bbox[3]>crop[3]:
            raise Hold("Person-plus-message crop clips its prepared alpha subject")
    if person_message and (len(campaign.headline.split()) > 8 or len(campaign.accent.split()) > 5):
        raise Hold("Person-plus-message requires a short headline and one concise emphasis phrase")
    if (campaign.phone_view != "auto" or campaign.sender_name != "BURST SMS") and template["layout"] not in ["phone", "conversation"]:
        raise Hold("Sender/device options require a messaging template")
    if campaign.message and template["layout"] not in ["phone", "conversation"]:
        raise Hold("Message copy is only supported in messaging templates")
    energy=campaign.creative_style == "high-energy-casual"
    prop=None
    if not energy and (campaign.prop_id is not None or campaign.energy_treatment != "diagonal"):
        raise Hold("Props and energy treatments require explicit high-energy-casual selection")
    if energy:
        if not photo:
            raise Hold("High-energy-casual requires a registered professionally prepared transparent people asset")
        if campaign.composition != "auto" or campaign.heading_style != "light" or campaign.message or campaign.phone_view != "auto" or campaign.photo_crop is not None or campaign.photo_backdrop != "none" or campaign.photo_fit != "contain" or campaign.image_treatment not in ("panel","cutout") or campaign.message_placement != "below" or campaign.sms_position != "lower-left":
            raise Hold("High-energy-casual uses its controlled people/copy composition; remove conflicting layout/device/crop options")
        if len(campaign.headline.split()) > 8:
            raise Hold("High-energy-casual requires a short headline of up to eight words")
        def require_prepared_alpha(asset,label):
            image=Image.open(PLUGIN/asset["file"])
            if asset.get("approved_subject_alpha") is not True or "A" not in image.getbands() or image.getchannel("A").getextrema() != (0,255):
                raise Hold(label+" requires a registered professionally prepared transparent asset; no white-background removal or invented substitute is allowed")
            if not asset.get("crop"):
                raise Hold(label+" requires a registered complete-subject crop")
            bbox=image.getchannel("A").getbbox();crop=asset["crop"]
            if not bbox or bbox[0]<crop[0] or bbox[1]<crop[1] or bbox[2]>crop[2] or bbox[3]>crop[3]:
                raise Hold(label+" registered crop clips its approved alpha subject")
        require_prepared_alpha(photo,"Team/people imagery")
        if campaign.prop_id:
            prop=config.get("props",{}).get(campaign.prop_id)
            if not prop or campaign.template_id not in prop.get("templates",[]):
                raise Hold("Prop is not registered for this campaign template")
            require_prepared_alpha(prop,"Campaign prop")
        if campaign.template_id == "team-coffee":
            if photo.get("identity") != "philippines-team":
                raise Hold("Use a registered authentic Philippines team asset, never illustrative or invented team imagery")
            if not prop or prop.get("category") != "coffee":
                raise Hold("High-energy coffee invitation requires a registered professionally prepared coffee prop")
        elif prop and prop.get("category") == "coffee":
            raise Hold("Coffee props are reserved for deliberate team coffee invitations")
    output_width, output_height = campaign.dimensions if campaign.format == "custom" else config["formats"][campaign.format]
    # Recompose at a common design width using the requested aspect ratio.
    # Only the completed, recomposed canvas is uniformly rasterised to export size.
    width, height = 1080, round(output_height*1080/output_width)
    export_scale = output_width/width
    c = Canvas((width, height))
    d = c.draw
    compact = c.compact
    header_height = 100 if compact else 150
    background = campaign.composition == "photo-background"
    if background and (not photo or campaign.brand_strip != "bottom" or campaign.heading_style != "navy" or template["layout"] not in ("phone","conversation") or not campaign.message):
        raise Hold("Photo-background requires registered messaging photography, navy heading, bottom brand bar and an explicit SMS")
    if background and (campaign.image_treatment != "panel" or campaign.photo_backdrop != "none" or campaign.message_placement != "below"):
        raise Hold("Photo-background uses an edge-to-edge panel and controlled overlay, without decorative photo treatments")
    if not background and campaign.sms_position != "lower-left":
        raise Hold("SMS overlay positions require photo-background composition")
    cta_height = ((150 if campaign.offer_terms else 110) if compact else (180 if campaign.offer_terms else 120)) if background or person_message or graphic_hero else (150 if campaign.offer_terms else 110) if compact else 180
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
    if campaign.message_placement == "beside" and layout != "conversation":
        raise Hold("Beside message placement requires registered photography and an SMS message")
    if campaign.phone_view != "auto" and layout != "phone" and not person_message:
        raise Hold("Device view requires phone imagery; use auto for a photographic SMS card")
    subject_regions=[]
    if energy:
        side=False;image_first=False;copy_x=64;copy_width=952;copy_y=(125 if compact else 190) if campaign.brand_strip=="top" else 32
        body_top=copy_y;body_bottom=footer-24;body_height=body_bottom-body_top
        copy_height=c.energy_copy(campaign,copy_x,copy_y,copy_width,body_height-(150 if compact else 260)-24,paint=False)
        visual_y=copy_y+copy_height+24;visual_height=body_bottom-visual_y
        # Decorations live only in the visual region, behind protected native-alpha subjects.
        if campaign.energy_treatment=="diagonal":
            d.polygon([(0,visual_y+round(visual_height*.18)),(width,visual_y+round(visual_height*.48)),(width,body_bottom),(0,visual_y+round(visual_height*.73))],fill=PALETTE["cyan"])
            d.polygon([(0,visual_y+round(visual_height*.55)),(width,visual_y+round(visual_height*.75)),(width,body_bottom),(0,body_bottom)],fill=PALETTE["violet"])
        elif campaign.energy_treatment=="bands":
            d.rectangle((0,visual_y+visual_height//3,width,body_bottom),fill=PALETTE["cyan"])
            d.rectangle((0,visual_y+2*visual_height//3,width,body_bottom),fill=PALETTE["violet"])
        subject_width=752 if prop else 952
        c.photo(photo,(64,visual_y,subject_width,visual_height),campaign.image_position,"cutout","none","contain")
        if prop:
            frame=c.photo(prop,(840,body_bottom-min(180,visual_height),176,min(180,visual_height)),"right","cutout","none","contain")
            c.photo_checks[-1]["role"]="prop"
        c.energy_copy(campaign,copy_x,copy_y,copy_width,copy_height)
    elif graphic_hero:
        side=False;image_first=False;has_visual=True;copy_x=64;copy_width=952
        copy_y=190 if campaign.brand_strip=="top" else 32
        dark=campaign.heading_style=="navy"
        copy_height=c.copy_block(campaign,copy_x,copy_y,copy_width,260,dark=dark,paint=False)
        heading_bottom=copy_y+copy_height+32
        body_top=heading_bottom;body_bottom=footer-24;body_height=body_bottom-body_top
        if body_height<200:raise Hold("Graphic-hero needs more visual space; shorten copy or use portrait")
        c.graphic(graphic,(64,body_top+16,952,body_height-32),campaign.graphic_colour)
        if dark:d.rectangle((0,0,width,heading_bottom-1),fill=PALETTE["navy"])
        c.copy_block(campaign,copy_x,copy_y,copy_width,copy_height,dark=dark)
    elif person_message:
        side=False; image_first=False; has_visual=True; copy_x=64;copy_width=952;copy_y=32
        person_heading_sizes=(112,104,96) if campaign.format=="portrait" else (96,88,80)
        copy_height=c.copy_block(campaign,copy_x,copy_y,copy_width,460 if campaign.format=="portrait" else 340,dark=True,paint=False,heading_sizes=person_heading_sizes)
        supporting_check=Canvas(c.image.size)
        if campaign.supporting:
            supporting_check.text(campaign.supporting,(64,32,952,45),30,"white",False,1)
        heading_bottom=copy_y+copy_height+32
        body_top=heading_bottom;body_bottom=footer-24;body_height=body_bottom-body_top
        if body_height<300:
            raise Hold("Person-plus-message needs more visual space; shorten heading/emphasis or choose portrait")
        # One adjacent group, with complete-source photography and content-sized deterministic UI.
        # Non-overlapping safe regions avoid covering faces, hands, physical phones or essential text.
        visual_y=body_top+24;visual_height=body_height-48
        photo_x=64 if campaign.image_position=="left" else 444
        graphic_x=668 if campaign.image_position=="left" else 64
        graphic_width=348
        if campaign.graphic_placement=="layered":
            alpha_source=Image.open(PLUGIN/photo["file"])
            if photo.get("approved_subject_alpha") is not True or "A" not in alpha_source.getbands() or alpha_source.getchannel("A").getextrema() != (0,255) or campaign.image_treatment!="cutout":
                raise Hold("Layered message placement requires a registered professionally prepared alpha subject")
            graphic_x=584 if campaign.image_position=="left" else 148
        if campaign.graphic_decoration=="cyan-band":
            d.rounded_rectangle((graphic_x-12,visual_y+visual_height//3,graphic_x+graphic_width+11,body_bottom-12),32,fill=PALETTE["cyan"])
        c.photo(photo,(photo_x,visual_y,572,visual_height),"centre",campaign.image_treatment,"none","contain")
        if graphic:
            c.graphic(graphic,(graphic_x,visual_y,graphic_width,visual_height),campaign.graphic_colour)
        elif campaign.phone_view=="full":
            c.phone(campaign,(graphic_x,visual_y,graphic_width,visual_height))
        else:
            card_height=c.bubble(campaign.message,(graphic_x,visual_y,graphic_width,min(300,visual_height)),campaign.sender_name,paint=False)
            c.bubble(campaign.message,(graphic_x,visual_y+(visual_height-card_height)//2,graphic_width,card_height),campaign.sender_name)
        d.rectangle((0,0,width,heading_bottom-1),fill=PALETTE["navy"])
        c.copy_block(campaign,copy_x,copy_y,copy_width,copy_height,dark=True,heading_sizes=person_heading_sizes)
    elif background:
        side=False; image_first=False; copy_x=64; copy_width=952; copy_y=24 if compact else 32
        budget=(110 if compact else 90)+(60 if campaign.accent else 0)+(70 if campaign.supporting else 0)
        copy_height=c.copy_block(campaign,copy_x,copy_y,copy_width,budget,dark=True,paint=False,heading_sizes=(60,56,52))
        heading_bottom=copy_y+copy_height+(24 if compact else 32)
        body_top=heading_bottom; body_bottom=brand_y; body_height=body_bottom-body_top
        if body_height < cta_height+140:
            raise Hold("Photo-background needs more photograph and overlay space; shorten copy or change format")
        photo_region=[0,body_top,width,body_height]
        c.photo(photo,photo_region,campaign.image_position,"panel","none","cover")
        effective=c.photo_checks[-1]["effective_crop"]
        for region in photo.get("protected_subject_regions",[]):
            sx,sy,ex,ey=region["box"]
            if sx<effective[0] or sy<effective[1] or ex>effective[2] or ey>effective[3]:
                raise Hold("Photo-background crop clips a registered face, hand or focal action; choose another scene/format")
            subject_regions.append({"label":region["label"],"box":[(sx-effective[0])*width/(effective[2]-effective[0]),body_top+(sy-effective[1])*body_height/(effective[3]-effective[1]),(ex-sx)*width/(effective[2]-effective[0]),(ey-sy)*body_height/(effective[3]-effective[1])]})
        # Opaque enough for white text against the lightest source pixels, but keeps the photo visible.
        scrim=Image.new("RGBA",(width,cta_height),(*tuple(int(PALETTE["navy"].lstrip('#')[i:i+2],16) for i in (0,2,4)),224))
        c.image.paste(scrim,(0,footer),scrim)
        card_width=480 if not compact else 440
        card_height=c.sms_overlay(campaign,(64,body_top+24,card_width,min(250,body_height-cta_height-48)),paint=False)
        card_x=64 if campaign.sms_position.endswith("left") else width-64-card_width
        available=footer-body_top
        card_y=body_top+24 if campaign.sms_position.startswith("upper") else body_top+(available-card_height)//2 if campaign.sms_position.startswith("middle") else footer-8-card_height
        c.sms_overlay(campaign,(card_x,card_y,card_width,card_height))
        # Protected heading painted after photographic stage, never a floating band with blank margins.
        d.rectangle((0,0,width,heading_bottom-1),fill=PALETTE["navy"])
        c.copy_block(campaign,copy_x,copy_y,copy_width,copy_height,dark=True,heading_sizes=(60,56,52))
    else:
        body_top = (125 if compact else 195) if campaign.brand_strip == "top" else (25 if compact else 45)
        body_bottom = footer-(20 if compact else 28)
        body_height = body_bottom - body_top
        has_visual = layout in ("phone", "split", "team", "conversation")
        side = layout in ("phone", "split", "team", "conversation") and campaign.heading_style != "navy" and (campaign.composition == "side-by-side" or campaign.composition == "auto" and height <= 1500)
        copy_width = 455 if side else 880 if layout == "feature" else 940
        copy_x = 561 if side and campaign.image_position == "left" else 100 if layout == "feature" else 64
        gap = 20 if compact else 30
        budget = body_height if side or not has_visual else body_height-(350 if layout == "phone" else 260 if layout == "conversation" else (130 if compact else 230))-gap
        try:
            copy_height = c.copy_block(campaign, copy_x, body_top, copy_width, budget,
                                      dark=layout == "statement" or campaign.heading_style == "navy", paint=False, column=side)
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
        if layout == "conversation" and not side and campaign.message_placement == "below":
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
        if campaign.heading_style == "navy":
            d.rectangle((0,max(0,copy_y-20),width,copy_y+copy_height+20),fill=PALETTE["navy"])
        if layout == "statement":
            d.rectangle((0,header_height if campaign.brand_strip == "top" else 0,width,height if campaign.brand_strip == "top" else brand_y),fill=PALETTE["navy"])
        elif layout == "feature":
            d.rectangle((0,header_height if campaign.brand_strip == "top" else 0,width,footer),fill=PALETTE["cloud"] if campaign.brand_strip == "bottom" else PALETTE["white"])
            d.rounded_rectangle((62,body_top-20,1018,footer-20), 42, fill=PALETTE["cloud"])
            d.rectangle((62,body_top+20,72,footer-60), fill=PALETTE["cyan"])
        c.copy_block(campaign, copy_x, copy_y, copy_width, copy_height, dark=layout == "statement" or campaign.heading_style == "navy", column=side)
        if layout == "phone":
            c.phone(campaign, (64 if side and campaign.image_position == "left" else 548 if side else 64,
                               visual_y, 468 if side else 952, visual_height))
        elif layout == "conversation":
            # Photo and SMS share one aligned group in the visual column.
            group_width = 468 if side else 952
            group_x = (64 if campaign.image_position == "left" else 548) if side else (width-group_width)//2
            if campaign.message_placement == "beside":
                if group_width < 700:
                    raise Hold("Photo and SMS beside one another require a stacked heading composition")
                half = (group_width-24)//2
                card_height = c.bubble(campaign.message,(group_x+half+24,visual_y,half,min(300,visual_height)),campaign.sender_name,paint=False)
                frame = c.photo(photo,(group_x,visual_y,half,visual_height),"centre",campaign.image_treatment,campaign.photo_backdrop,"cover" if campaign.composition == "hero" else campaign.photo_fit)
                c.bubble(campaign.message,(group_x+half+24,visual_y+(visual_height-card_height)//2,half,card_height),campaign.sender_name)
            else:
                card_height = c.bubble(campaign.message,(group_x,visual_y,group_width,min(300,visual_height)),campaign.sender_name,paint=False)
                photo_budget = visual_height-card_height-16
                if photo_budget < 100:
                    raise Hold("Photograph and SMS need more body space; shorten copy or change composition")
                frame = c.photo(photo,(group_x,visual_y,group_width,photo_budget),"centre",campaign.image_treatment,campaign.photo_backdrop,"cover" if campaign.composition == "hero" else campaign.photo_fit)
                c.bubble(campaign.message,(group_x,frame[1]+frame[3]+16,group_width,card_height),campaign.sender_name)
        elif layout in ("split", "team"):
            photo_x = 64 if campaign.image_position == "left" else 548
            c.photo(photo, (photo_x if side else 64, visual_y, 468 if side else 952, visual_height), "centre" if side else campaign.image_position, campaign.image_treatment,campaign.photo_backdrop,"cover" if campaign.composition == "hero" else campaign.photo_fit)
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
           "white" if background or layout == "statement" and campaign.brand_strip == "bottom" else "navy",True,1)
    terms_box = None
    if campaign.offer_terms:
        terms_y = button_y+button_height+12 if same_line else website_y+36
        terms_box = [64,terms_y,width-128,footer+cta_height-terms_y-12]
        c.text(campaign.offer_terms,tuple(terms_box),22,
               "white" if background or layout == "statement" and campaign.brand_strip == "bottom" else "navy",False,4)
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
        if (py+ph > (brand_y if background else footer) or py < body_top):
            raise Hold("Photography intrudes into protected CTA/brand space")
    if not (footer <= button_y and website_y < footer+cta_height and (campaign.brand_strip != "bottom" or footer+cta_height == brand_y)):
        raise Hold("CTA placement does not follow the brand bar")
    if terms_box is not None:
        terms_check = next(check for check in reversed(c.text_checks) if check["text"] == campaign.offer_terms)
        if not (terms_box[0] >= 64 and terms_box[1] >= button_y+button_height+12 and footer <= terms_box[1] and terms_box[1]+terms_check["used_height"] <= footer+cta_height):
            raise Hold("Terms must fit alongside CTA inside its reserved region")
    if person_message:
        graphic_box = c.graphic_check["frame"] if graphic else getattr(c,"message_card",None) or c.phone_check["visible_frame"]
        px,py,pw,ph=c.photo_checks[0]["frame"]
        gx,gy,gw,gh=graphic_box
        collision=gx<px+pw and gx+gw>px and gy<py+ph and gy+gh>py
        if collision and campaign.graphic_placement=="layered":
            # Check the entire overlay against actual registered subject opacity, including soft hair.
            # Only overlap within transparent negative space is permitted, never foreground pixels.
            alpha=Image.open(PLUGIN/photo["file"]).getchannel("A").crop(tuple(photo["crop"])).resize((pw,ph),Image.Resampling.LANCZOS)
            ix0,iy0=max(gx,px),max(gy,py);ix1,iy1=min(gx+gw,px+pw),min(gy+gh,py+ph)
            collision=alpha.crop((ix0-px,iy0-py,ix1-px,iy1-py)).getbbox() is not None
        if gx<64 or gx+gw>width-64 or gy<body_top+24 or gy+gh>footer-24 or collision:
            raise Hold("Person and message graphic collide or leave their safe visual group")
        if not same_line:
            raise Hold("Person-plus-message requires CTA and website on the same row")
    if background:
        def overlaps(a,b):
            return a[0]<b[0]+b[2] and a[0]+a[2]>b[0] and a[1]<b[1]+b[3] and a[1]+a[3]>b[1]
        overlays=[c.message_card,button_box,website_box]+([terms_box] if terms_box else [])
        for box in overlays:
            if box[0]<64 or box[0]+box[2]>width-64 or box[1]<body_top+20 or box[1]+box[3]>brand_y-12:
                raise Hold("Photo overlay leaves safe middle-section bounds")
        for i,box in enumerate(overlays):
            if any(overlaps(box,other) for other in overlays[i+1:]):
                raise Hold("Photo overlays collide")
        for region in subject_regions:
            if any(overlaps(region["box"],box) for box in overlays+[cta_region]):
                raise Hold("Photo overlay/readability treatment obscures a registered face, hand or focal action")
        if c.photo_checks[0]["frame"] != photo_region or c.photo_checks[0]["mask_has_transparency"]:
            raise Hold("Photo does not cover the entire middle section")
    if graphic:
        gx,gy,gw,gh=c.graphic_check["frame"]
        if gx<64 or gx+gw>width-64 or gy<body_top or gy+gh>footer-24:
            raise Hold("Registered graphic leaves the protected body space")
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
        if hasattr(c,"graphic_check"):
            for name in ("frame","region"):
                c.graphic_check[name]=[round(v*export_scale) for v in c.graphic_check[name]]
        if hasattr(c, "phone_check"):
            for name in ("device_dimensions", "visible_frame"):
                if c.phone_check[name] is not None:
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
        "body_region": [round(v*export_scale) for v in ((0,body_top,width,body_height) if background else (64,body_top,952,body_height))],
        "photo_background": {"coverage":True,"sms_position":campaign.sms_position,"readability_treatment":"navy scrim alpha 224/255","subject_regions":[{"label":r["label"],"box":[round(v*export_scale) for v in r["box"]]} for r in subject_regions],"visual_subject_inspection_required":True} if background else None,
        "message_placement": campaign.message_placement,
        "heading_style": campaign.heading_style,
        "heading_region": ([0,0,output_width,round(heading_bottom*export_scale)] if background or person_message or graphic_hero else [0,round(max(0,copy_y-20)*export_scale),output_width,round((copy_height+40)*export_scale)]) if campaign.heading_style == "navy" else None,
        "creative_style": campaign.creative_style,
        "energy_treatment": campaign.energy_treatment if energy else None,
        "prop_id": campaign.prop_id,
        "graphic_id": campaign.graphic_id, "imagery_channel":campaign.imagery_channel, "channel_request":campaign.channel_request,
        "graphic_check": getattr(c,"graphic_check",None),
        "graphic_colour": campaign.graphic_colour if graphic else None,
        "graphic_placement": campaign.graphic_placement if person_message else None,
        "graphic_decoration": campaign.graphic_decoration if person_message else None,
        "body_layout": "graphic-hero" if graphic_hero else "person-plus-message" if person_message else "high-energy-casual" if energy else "photo-background" if background else "side-by-side" if side else "image-first" if image_first else "stacked" if has_visual else "statement",
        "brand_region": protected_brand, "cta_region": cta_region, "cta_button": button_box,
        "terms_box": terms_box, "website_box": website_box, "cta_alignment": "same-line" if same_line else "stacked", "message_card": getattr(c,"message_card",None),
        "phone_check": getattr(c, "phone_check", None),
        "sender_name": campaign.sender_name if layout in ("phone", "conversation") and not graphic else None,
        "phone_message": (campaign.message or "Your order is ready for collection. Thank you!") if layout in ("phone", "conversation") and not graphic else None,
        "photo_checks": c.photo_checks, "brand_strip": campaign.brand_strip, "logo_box": [logo_x, logo_y, scaled_logo.width, scaled_logo.height],
        "alt_text": "Burst SMS Philippines: " + ". ".join(part.rstrip(". ") for part in [campaign.headline, campaign.accent, photo["alt"] if photo else "", ("Illustrative SMS from "+campaign.sender_name+": "+(campaign.message or "Your order is ready for collection. Thank you!")) if layout in ("phone","conversation") and not graphic else "", graphic["alt"] if graphic else ""] if part),
        "channel_copy": campaign.primary_text + "\n\n" + campaign.cta + ": " + DESTINATION + ("\n\nTerms: "+campaign.offer_terms if campaign.offer_terms else ""),
        "contrast_ratios": contrasts,
        "checks": {**({"registered_graphic":True,"graphic_readable_size":True,"graphic_palette_only":True,"graphic_bounds":True} if graphic else {}),**({"person_graphic_separation":True,"complete_photo_preserved":True,"readable_graphic":True} if person_message else {}),**({"prepared_subject_alpha":True,"registered_prop":not prop or prop.get("approved_subject_alpha") is True,"decorations_behind_subjects":True} if energy else {}),**({"photo_coverage":True,"overlay_bounds":True,"overlay_collisions":True,"registered_subject_preservation":True} if background else {}),"asset_integrity": True, "logo_pixels": True, "locked_styles": True, "text_fit": True, "fixed_dimensions": True, "fixed_destination": True, "text_contrast": True, "message_visible": bool(graphic) or layout not in ("phone", "conversation") or any(t["text"] == (campaign.message or "Your order is ready for collection. Thank you!") for t in c.text_checks), "cta_placement": True, "brand_bar_separation": True, "terms_placement": True, "text_collisions": True, "mask_bounds": all(p["mask_bounds_match"] for p in c.photo_checks), "photo_frame_fit": all(p["frame_filled"] and p["proportional_scale"] for p in c.photo_checks)},
        "inspection_required": ["copy_and_claims", "visual_composition", "local_fit_and_photography", "accessibility", "photo_edges", "body_balance", "cta_and_terms", "campaign_effectiveness"]
    }
    return png, report
