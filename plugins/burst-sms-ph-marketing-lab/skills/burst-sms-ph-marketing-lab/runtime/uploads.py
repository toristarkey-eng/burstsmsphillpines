"""Campaign-local user images, reviewed and bound to their exact source bytes."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageOps, ImageCms
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

CHECKS = ("rights_and_consent", "brand_and_third_party_marks", "embedded_copy_and_claims",
          "privacy_and_sensitive_data", "image_quality", "subject_and_edges", "channel_accuracy")


def sha(data):
    return hashlib.sha256(data).hexdigest()


class ProtectedRegion(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    label: str = Field(min_length=3, max_length=100)
    box: list[int] = Field(min_length=4, max_length=4)


class UploadReview(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_origin: Literal["user-supplied", "imagegen-generated"] = "user-supplied"
    description: str = Field(min_length=15, max_length=500)
    kind: Literal["photo", "phone", "screenshot", "illustration"]
    channel: Literal["none", "sms", "rcs", "whatsapp", "viber"] = "none"
    framing: Literal["complete-subject", "continuous-scene"]
    protected_regions: list[ProtectedRegion] = Field(default_factory=list, max_length=32)
    checks: dict[str, bool]
    notes: dict[str, str]

    def checked(self):
        if set(self.checks) != set(CHECKS) or any(v is not True for v in self.checks.values()):
            raise ValueError("Every user-image source review must pass before use")
        if set(self.notes) != set(CHECKS) or any(not 15 <= len(v.strip()) <= 2000 for v in self.notes.values()):
            raise ValueError("Record actual source-image inspection findings for every check")
        if any(ord(c) < 32 for c in self.description) or any(c in self.description for c in "<>"):
            raise ValueError("Use a plain-text image description")
        return self

    def check_regions(self, dimensions):
        width, height = dimensions
        for region in self.protected_regions:
            x, y, w, h = region.box
            if min(x, y) < 0 or min(w, h) <= 0 or x+w > width or y+h > height:
                raise ValueError("Protected subject region leaves the orientation-correct source")


def normalise(raw):
    if not 0 < len(raw) <= 20*1024*1024:
        raise ValueError("User images must be PNG, JPEG or WebP up to 20 MiB")
    with Image.open(io.BytesIO(raw)) as source:
        if source.format not in ("PNG", "JPEG", "WEBP") or getattr(source, "n_frames", 1) != 1:
            raise ValueError("Only static PNG, JPEG and WebP uploads are supported")
        w,h=source.size
        if min(w,h)<300 or max(w,h)<600 or max(w,h)>8192 or w*h>24_000_000:
            raise ValueError("Upload needs at least 300px per side, 600px on its long side and at most 24 megapixels / 8192px per side")
        # Honour source colour profiles and orientation, retain genuine alpha and strip metadata.
        image=ImageOps.exif_transpose(source).convert("RGBA")
        if source.info.get("icc_profile"):
            try:
                profile=ImageCms.ImageCmsProfile(io.BytesIO(source.info["icc_profile"]))
                rgb=ImageCms.profileToProfile(image.convert("RGB"),profile,ImageCms.createProfile("sRGB"),outputMode="RGB")
                rgb.putalpha(image.getchannel("A"));image=rgb
            except (OSError, ValueError, ImageCms.PyCMSError) as exc:
                raise ValueError("Uploaded colour profile cannot be read; export as sRGB PNG or JPEG") from exc
        alpha=image.getchannel("A").getextrema()
        if alpha[1]==0:
            raise ValueError("Uploaded image contains no visible pixels")
        if alpha[0]<255 and alpha != (0,255):
            raise ValueError("Transparent uploads need both fully clear and fully opaque pixels; use a properly prepared PNG")
        clean=Image.new("RGBA",image.size);clean.paste(image)
        out=io.BytesIO();clean.save(out,format="PNG",optimize=False)
        return out.getvalue(),list(clean.size),alpha==(0,255)


def prepare(image_path, review_data, directory):
    with Path(image_path).open("rb") as stream:
        raw=stream.read(20*1024*1024+1)
    review=UploadReview.model_validate(review_data).checked()
    if sha(raw)!=review.source_sha256:
        raise ValueError("Source review does not match this exact uploaded image")
    png,dimensions,alpha=normalise(raw)
    review.check_regions(dimensions)
    if alpha and review.framing != "complete-subject":
        raise ValueError("Transparent uploads must preserve a complete subject or device")
    directory=Path(directory)
    directory.mkdir(parents=True,mode=0o700,exist_ok=False)
    (directory/"original.bin").write_bytes(raw)
    (directory/"source.png").write_bytes(png)
    record={"schema_version":1,"review":review.model_dump(),"source_sha256":sha(png),
            "dimensions":dimensions,"native_alpha":alpha}
    (directory/"source-review.json").write_text(json.dumps(record,indent=2)+"\n")
    return {"status":"SOURCE_REVIEW_PASSED","image_ready_for_delivery":False,
            "source_sha256":sha(png),"dimensions":dimensions,"native_alpha":alpha}


def load(directory):
    directory=Path(directory).resolve()
    for name in ("original.bin","source.png","source-review.json"):
        p=directory/name
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(directory):
            raise ValueError("Upload bundle must contain local immutable source/review files")
    if (directory/"source-review.json").stat().st_size>20000:
        raise ValueError("Upload review is too large")
    r=json.loads((directory/"source-review.json").read_text())
    if set(r)!={"schema_version","review","source_sha256","dimensions","native_alpha"} or r['schema_version']!=1:
        raise ValueError("Upload source record is invalid")
    review=UploadReview.model_validate(r['review']).checked()
    if (directory/"original.bin").stat().st_size>20*1024*1024 or (directory/"source.png").stat().st_size>100*1024*1024:
        raise ValueError("Uploaded source exceeds the bounded file limits")
    raw=(directory/"original.bin").read_bytes()
    if sha(raw)!=review.source_sha256:
        raise ValueError("Original upload changed after source review")
    png,dims,alpha=normalise(raw)
    review.check_regions(dims)
    if png!=(directory/"source.png").read_bytes() or sha(png)!=r['source_sha256'] or dims!=r['dimensions'] or alpha is not r['native_alpha']:
        raise ValueError("Uploaded image or preparation record changed after review")
    if alpha and review.framing!='complete-subject':
        raise ValueError("Transparent uploaded subjects must remain complete")
    asset={"file":"user-upload/source.png","crop":[0,0,*dims],"alt":review.description,
           "templates":["uploaded-image"],"user_supplied":True,"kind":review.kind,
           "source_origin":review.source_origin,"channel":review.channel,
           "approved_subject_alpha":alpha,"upload_review":r}
    return asset
