# Work bundled renderer

Run these commands using this installed skill's absolute path. The entire skill folder can be copied out of the repository and executed from an unrelated working directory. Python 3.11+ and the pinned packages in `runtime/requirements.txt` are required; no Node.js, repository checkout, external host, MCP registration or credential is needed.

```sh
python -m venv <private-venv>
<private-venv>/bin/python -m pip install -r <skill>/runtime/requirements.txt
<private-venv>/bin/python <skill>/scripts/brand_preflight.py --surface work
<private-venv>/bin/python <skill>/scripts/render_creative.py --surface work catalog
```

On Windows use the virtual environment's `Scripts/python.exe` path. Never overwrite an existing environment or modify the installed skill. If package installation/execution is unavailable, return `Hold`; do not fabricate a runtime.

## Campaign contract

Permitted inputs are `template_id`, `format`, `dimensions`, `headline`, `accent`, `supporting`, `primary_text`, `cta`, `photo_id`, `message`, `brand_strip`, `composition`, `image_position`, `image_treatment`, `photo_crop` and `photo_description`, `sender_name`, `phone_view`, `photo_backdrop`, `photo_fit`, `heading_style` and `offer_terms`. Unknown fields, hidden/control characters, markup, URLs/bare domains, competing-brand copy and unsupported superiority claims are rejected. Templates are `recognition`, `customer-updates`, `people-first`, `team-coffee`, `bold-statement`, `offer-focus`. Default social sizes remain square 1080 × 1080 and portrait 1080 × 1350. Explicit alternatives are landscape 1200 × 628, story 1080 × 1920 or custom dimensions. For custom only, provide `"format": "custom", "dimensions": [1200, 800]`; each side must be 600–4096px and height/width 0.5–2. Dimensions on named formats are rejected. Headings wrap and adapt within readable limits; compact landscapes use smaller proportional bars and type. Copy that cannot fit is rejected. The layout is recomposed at the requested aspect ratio before uniform rasterisation, not stretched from another finished ad. Use registered photo sources/CTA choices, not paths or free-form styles.

Example structure, using an invitation without a product, price or performance claim:

```json
{
  "template_id": "recognition",
  "format": "portrait",
  "headline": "Start a conversation.",
  "accent": "Talk to our team.",
  "supporting": "Discuss messaging for your business.",
  "primary_text": "Talk to Burst SMS Philippines about messaging for your business.",
  "cta": "Talk to our team",
  "photo_id": null,
  "message": ""
}
```

```sh
<python> <skill>/scripts/render_creative.py --surface work render --brief <campaign.json> --output-dir <new-private-directory>
```

The output is private `artwork.png`, `recommended-copy.md` and `render-report.json`. `INSPECTION_REQUIRED` is not permission to attach it. Do not reuse or overwrite an existing output directory. Keep outputs outside the skill so the package stays intact.

## Final inspection and delivery

Privately inspect the actual PNG, exact copy and alt text. Check the source file/crop, brand lockup, composition, readable text and spacing, accessibility and Philippine suitability. List each factual claim with current source/date/scope and approval status; reject unresolved claims. Record what was actually inspected, not a generic checklist assertion. Copy the current hashes from the render report into this inspection structure:

```json
{
  "png_sha256": "<current PNG hash>",
  "campaign_sha256": "<current campaign hash>",
  "checks": {
    "copy_and_claims": true,
    "visual_composition": true,
    "local_fit_and_photography": true,
    "accessibility": true,
    "photo_edges": true,
    "body_balance": true,
    "cta_and_terms": true,
    "campaign_effectiveness": true
  },
  "notes": {
    "copy_and_claims": "<exact wording checked; claim sources, dates, scope and owner approval, or explain why there is no factual claim>",
    "visual_composition": "<actual lockup, safe zones, hierarchy and text spacing inspected>",
    "local_fit_and_photography": "<registered photo/crop, illustrative status and local suitability checked>",
    "accessibility": "<readability, contrast and exact alt text inspected>",
    "photo_edges": "<actual full-resolution and feed-size edges, subjects, halos and backdrop pixels inspected>",
    "body_balance": "<actual photo/message grouping, focal point, card sizing and whitespace inspected>",
    "cta_and_terms": "<CTA left/website right, approved terms nearby, contrast and brand-only bar separation inspected>",
    "campaign_effectiveness": "<audience, need, objective, substantiated reason to choose Burst SMS and immediate next action inspected>"
  }
}
```

```sh
<python> <skill>/scripts/render_creative.py --surface work validate --directory <private-directory> --inspection <inspection.json>
```

Require a **fresh successful command** plus `delivery-validation.json` with `status: PASSED` and `image_ready_for_delivery: true`. Validation rerenders from the locked inputs, compares PNG/record/copy and requires every inspection result to be true and explained. Hashes bind inspection to this exact wording/image; they are not reviewer signatures. Copy/PNG/package changes invalidate delivery. Failure withholds artwork even if an older receipt exists. Attach only the exact validated PNG and copy using Work's supported artifact/file-delivery capability. If attachment or private inspection is unavailable, return `Hold`.

Local checks enforce technical constraints, not claim truth or host-wide access control. `--surface work` is a caller declaration, not authenticated proof of Work. The skill's capability gate and workspace's surface availability must be verified in fresh conversations. Brand-check completion is distinct from publication permission; this tool does not publish.

## Maintenance

Maintainers update files in code review, run `python scripts/lock-work-package.py` from the repository and inspect the manifest diff. This helper is deliberately outside the shipped skill. Run all tests after intentional changes. Do not expose a hash-refresh or bypass command to creative users. Keep this existing plugin identity; update its package through the established marketplace release process only when authorised.

The Noto Sans fonts use the bundled `runtime/fonts/OFL.txt`. SemiBold provenance: `https://raw.githubusercontent.com/notofonts/noto-fonts/ffebf8c1ee449e544955a7e813c54f9b73848eac/hinted/ttf/NotoSans/NotoSans-SemiBold.ttf`, SHA-256 `87a8b90ece1e89746b544e4e086f85a3710e41485a8078f9be874837dfad45d5`.

## Adaptive composition (0.4.2)

Optional fields: `brand_strip` is `top` (default) or `bottom`; `composition` is `auto` (default), `side-by-side`, `text-first`, `image-first` or `hero`; `image_position` is `left`, `centre` or `right` (`centre` is the default). The renderer measures copy and allocates remaining space to imagery. The recognition template supports its phone illustration by default or registered illustrative photography. Team photography remains restricted to `team-coffee`. Photo frames follow the complete registered panel's aspect ratio and fill exactly; never stretch subjects. Select coherent source crops deliberately and inspect faces, hair, hands, equipment and framing. Avoid excessive source/body whitespace. These fields select controlled compositions, not arbitrary coordinates, styles or fonts. Inspect the actual final image before delivery.

## Body composition quality

The template is an art-direction starting point, not a rigid copy/photo grid. Keep protected brand/CTA styles and follow the responsive CTA placement rules below. Use auto for a balanced side-by-side headline/copy and phone/photo when it fits; explicit side-by-side does not silently change layout. Auto may choose stacked for longer copy. Stacked phones are centred. Select composition from the campaign message, not habit. Provide a concise, meaningful fictional `message` for messaging layouts. Placeholder text such as “Your brand here” is rejected. If empty, the renderer uses the clearly fictional order-collection example recorded as `phone_message`. Do not imply a real customer endorsement or measured result. A visible message card, coherent hierarchy, proportionate imagery and balanced use of both sides of the body are mandatory visual inspection criteria. Technical text fit alone does not approve the design.

## Photography treatments and scene selection

Optional `image_treatment`: `panel`, `rounded`, `circle` (proportional elliptical mask), `cutout`. Cutout uses only registered approved native subject alpha. Opaque sources fall back to the unchanged original photo background, with the fallback recorded. Never infer a subject mask from brightness; privately inspect hair, hands, clothing and equipment, and reject damaged or visibly poor edges. Masks may change framing, so the report explicitly requires subject/edge inspection.

To choose beyond the named scenes, use `source-workforce`, `source-connections`, `source-coffee` or `source-collaborative`, plus `photo_crop: [left, top, right, bottom]` in source pixels and an accurate `photo_description`. Crop bounds must remain within the approved image. Select one coherent scene rather than a contact sheet. All selected-source bytes are integrity checked. Creative positioning/shape is flexible within the body, while protected bars, readability and final inspection remain mandatory.

## CTA and quality examples (0.4.3)

Use bundled `references/examples/customer-updates-top.json` or `customer-updates-bottom.json` as neutral input examples. The same illustrative photograph and SMS are shown as one group; `photo_backdrop` is `none`. Bottom placement reserves the coloured body CTA area before sizing the photo and text. Explicitly requested alternative formats still use the same gates. Add `offer_terms` only after resolving actual approved wording/evidence.

A final inspection requires eight boolean checks and eight corresponding notes: `copy_and_claims`, `visual_composition`, `local_fit_and_photography`, `accessibility`, `photo_edges`, `body_balance`, `cta_and_terms`, `campaign_effectiveness`. Every value must be true based on actual inspection and each note 15–2000 characters. State full/feed-size edge findings, subject preservation/fallback, whitespace/hierarchy, CTA/bar separation and terms readability. False, omitted or stale checks block delivery and remove old receipts.

CTA row: left button and right website share the same row where readable; approved terms occupy the nearby row within the reserved CTA area. Use the dated owner confirmation in the messaging reference for compliance/onboarding positioning and approved team imagery, without extending it to regulatory approval.

## Full device and hero photography (0.4.4)

Auto device views use complete full phones where readable, or complete sender/SMS cards in short allocations. Only an explicit `detail` view crops a device. `photo_fit` is `contain` by default or deliberate `cover`. `hero` is a text-first photographic composition with cover fit, giving the image the full available body width. Additional photographic crops are reported as effective_crop and require actual subject/context inspection. Crop selection does not authorise clipping faces, damaging equipment or presenting irrelevant stock imagery. Compare suitable private layouts; deliver only after all eight visual/content checks pass.

`heading_style` is `light` (default) or `navy` for photographic templates. Navy creates a distinct measured heading area with white/cyan type and a stacked photo body. It can be combined with `hero` cover photography; subject/crop and panel transition inspection remains mandatory.

For photographic SMS campaigns, select `message_placement: beside` with a stacked heading (`text-first`, `image-first`, `hero` or navy heading) to put a substantial photo and content-sized SMS card beside each other. Default `below` keeps the card underneath. Prefer beside when a wide shallow cover crop would damage a person or hide the messaging context. Inspect both arrangements; unsupported small side columns return Hold.
