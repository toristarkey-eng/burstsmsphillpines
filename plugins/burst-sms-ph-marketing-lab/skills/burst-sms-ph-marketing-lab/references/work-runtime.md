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

Permitted inputs are `template_id`, `format`, `dimensions`, `headline`, `accent`, `supporting`, `primary_text`, `post_type`, `hashtags`, `cta`, `photo_id`, `message`, `brand_strip`, `composition`, `image_position`, `image_treatment`, `photo_crop` and `photo_description`, `sender_name`, `phone_view`, `photo_backdrop`, `photo_fit`, `heading_style`, `message_placement`, `sms_position`, `creative_style`, `energy_treatment`, `prop_id`, `graphic_id`, `graphic_colour`, `graphic_placement`, `graphic_decoration` and `offer_terms`. Unknown fields, hidden/control characters, markup, URLs/bare domains, competing-brand copy and unsupported superiority claims are rejected. Templates are `recognition`, `customer-updates`, `people-first`, `team-coffee`, `bold-statement`, `offer-focus`, `person-plus-message`, `graphic-focus`. Default social sizes remain square 1080 × 1080 and portrait 1080 × 1350. Explicit alternatives are landscape 1200 × 628, story 1080 × 1920 or custom dimensions. For custom only, provide `"format": "custom", "dimensions": [1200, 800]`; each side must be 600–4096px and height/width 0.5–2. Dimensions on named formats are rejected. Headings wrap and adapt within readable limits; compact landscapes use smaller proportional bars and type. Copy that cannot fit is rejected. The layout is recomposed at the requested aspect ratio before uniform rasterisation, not stretched from another finished ad. Use registered photo sources/CTA choices, not paths or free-form styles.

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

The output is private `artwork.png`, `recommended-copy.md` and `render-report.json`. `recommended-copy.md` includes contextual hashtags for organic social posts and omits them for paid ads. `INSPECTION_REQUIRED` is not permission to attach it. Do not reuse or overwrite an existing output directory. Keep outputs outside the skill so the package stays intact.

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

Optional fields: `brand_strip` is `top` (default) or `bottom`; `composition` is `auto` (default), `side-by-side`, `text-first`, `image-first`, `hero` `photo-background` or `person-plus-message`; `image_position` is `left`, `centre` or `right` (`centre` is the default). The renderer measures copy and allocates remaining space to imagery. The recognition template supports its phone illustration by default or registered illustrative photography. Team photography remains restricted to `team-coffee`. Photo frames follow the complete registered panel's aspect ratio and fill exactly; never stretch subjects. Select coherent source crops deliberately and inspect faces, hair, hands, equipment and framing. Avoid excessive source/body whitespace. These fields select controlled compositions, not arbitrary coordinates, styles or fonts. Inspect the actual final image before delivery.

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

## Full-width photographic composition (0.4.5)

Choose `composition: photo-background` for edge-to-edge registered photography behind SMS and CTA. This layout requires `heading_style: navy`, `brand_strip: bottom`, a messaging template (`recognition` or `customer-updates`), an explicit fictional `message` and registered `photo_id`. Use `image_treatment: panel`, `photo_backdrop: none` and default `message_placement: below`; the SMS is overlaid, not a separate tile. The renderer forces proportional cover cropping of the entire middle section, without cloud-coloured gutters, rounded photo masks or stretching. It paints photography, lower-image navy scrim, compact SMS card and CTA, then protects the full navy heading panel and white bottom identity bar.

Select `sms_position` from upper-left, upper-right, middle-left, middle-right, lower-left or lower-right. Never submit arbitrary overlay coordinates. The CTA stays lower left and website lower right on one row, inside safe margins over the photo; approved terms remain nearby. Select the overlay only after inspecting where the faces, hands, phone and focal action sit. Registered subject exclusion boxes add technical checks where available; they do not replace visual inspection. Reject any cover crop or overlay that harms the scene. Choose another registered scene/format if the requested one cannot fit. Full resolution and feed-size review must reject floating tiles, unintended blank bands, damaged subjects, weak hierarchy and unreadable overlays, even if technical checks pass.

Use `references/examples/photo-background-ping.json` as the acceptance brief for “Good news deserves a little ping” with registered two-shopper scene, a fictional collection SMS and lower-image CTA. Compare private placements; do not assert this scene suits every aspect ratio. A crop that cannot preserve its protected subjects must Hold. This is a supported layout for all Work users after syncing this version, not an image-generation workaround.

Catalogue includes `compositions` and the photo-background contract. `sms_position` defaults to lower-left and only non-default values apply to photo-background. Registered `two-shoppers` uses the coherent bottom-row shopping scene from the existing source; source pixels remain unchanged.

## Optional high-energy-casual treatment (0.4.6)

Default `creative_style` is `default`, preserving the existing composition choices. Choose `creative_style: high-energy-casual` only when the user explicitly asks for high-energy, playful, casual, promotional or bold visual treatment, or an approved reference with that feel. Record the explicit tone/reference in inspection notes. A campaign objective such as “promote Sender ID”, “generate leads” or “high-performing” alone does not select this treatment. Do not apply it to every brief or override an explicitly professional, calm or formal tone.

This deterministic treatment uses a short oversized navy headline, violet emphasis and conversational supporting line, with prominent authentic people and no isolated photo tile. Use `composition: auto`, `heading_style: light`, no messaging/device overlay, and a registered professionally prepared complete-subject alpha asset. The renderer never keys near-white pixels, infers an alpha mask, invents people, or modifies identity, proportions, hair, clothing or hands. Approved diagonal shapes or layered bands stay below text, behind people, within navy/violet/cyan colours. Choose `energy_treatment: diagonal` (style default), `bands` or `none` deliberately. Keep existing protected bars, fonts, margins and responsive CTA placement. Bottom brand bar means CTA left and website right on the same row immediately above the brand-only white bar.

Use `prop_id` only to choose a registered professionally prepared transparent campaign prop. Coffee props are reserved for deliberate `team-coffee` invitations. That campaign requires actual Philippines-team identity metadata and a registered coffee prop; never use illustrative people as team members. Other high-energy campaigns may omit props. No arbitrary asset paths, coordinates or decorative colours are accepted. Asset registration requires original file, owner approval, native alpha, complete-subject crop, identity/category and template scope; optional alpha alone is not professional approval.

Write warmer copy with one clear offer and next step. Avoid forced slang, unsupported urgency, exaggerated outcomes and invented offer terms. Owner-requested coffee acceptance copy: headline Coffee’s on us.; emphasis Let’s make every message count.; supporting Meet your Philippines team for a messaging audit.; CTA Book a coffee chat. See `references/examples/high-energy-coffee.json`. This request confirms that invitation wording only, not quantified benefits, deadlines or invented conditions.

Current package has an opaque approved team JPEG and no separately registered coffee prop. The high-energy coffee acceptance example must return a precise Hold until a professionally prepared transparent version of the actual team and registered coffee prop are supplied and reviewed. Do not turn the JPEG into a guessed cutout, crop props from an existing finished ad, substitute coffee-montage people for the team, or display an unchecked approximation. These missing assets do not block ordinary styles.

Inspect the exact full-resolution PNG and Facebook feed view for short readable headline/emphasis/supporting copy, preserved identities/edges/subjects, strong coherent focal point, balanced people/prop scale, quiet purposeful spacing, decorations behind subjects and unobstructed CTA. Complete existing eight inspection/evidence/accessibility checks and exact delivery validation; a technical pass never establishes creative quality or performance. After new assets are registered, this real coffee acceptance example must pass those checks before any delivery.

## Optional person-plus-message composition (0.4.7)

Use `template_id: person-plus-message` and `composition: person-plus-message` when requested or clearly suited to a brief where a person adds human relevance and a message graphic explains updates, reminders, promotions or sender recognition. Never make it the default or force people, graphics or shapes into other campaigns. Keep the user's chosen style and existing layouts available.

Use square or portrait, `heading_style: navy`, `brand_strip: bottom`, `image_position: left` or `right`, registered `photo_id`, explicit meaningful fictional `sender_name` and `message`. Headline is short and oversized with white type and a concise cyan `accent`; supporting copy must fit one line. Measure wrapping and padding. Use `phone_view: card` (also the auto treatment) or `full` for a complete readable phone. Full phones that cannot fit without unreadable text Hold; do not substitute clipped devices. `graphic_decoration: none` is default; optional `cyan-band` stays behind the graphic. `graphic_placement: adjacent` is default. Optional `layered` uses fixed inward positions with approved native-alpha cutouts only; an opacity check rejects any foreground pixel beneath the entire message/phone overlay, including soft hair. It may overlap transparent negative space, never faces, hands, clothing or equipment. No arbitrary coordinates.

Photography is proportionally contained within one adjacent person/UI group. Keep the original background unless a registered professionally prepared complete-subject alpha asset is available. No near-white removal. Preserve faces, hair, hands, clothing and physical equipment. User crop selection requires an actual inspection of the selected subject. Avoid disconnected tiles, excess gaps and competing focal points; try left/right or another suitable scene if the balance is poor. Illustrative people are not employees, customers or endorsers. Use deliberate fictional examples by default; owner-approved YOUR BRAND labels may explain customer branding. CTA stays lower left and website lower right in one row inside the body, with approved terms nearby. The bottom white bar remains brand-only.

Acceptance brief: `references/examples/person-plus-message.json`, ACME SHOP / Your order is ready to collect. Inspect the exact PNG at full resolution and feed size for immediately understandable headline, readable message, preserved subjects, visual balance, edges, hierarchy and next action. Technical checks alone cannot establish creative quality; failed visual inspection Holds. Apply all existing claim, brand, accessibility and delivery checks. Reference photography or uploaded examples are not automatically registered assets.

## Approved campaign graphics and Vhey (0.4.8)

Tori supplied and approved the attached graphics on 10 October 2026, including permission to recolour graphic artwork using only the Burst SMS approved palette. They are optional campaign assets, not a new default style. Choose assets by campaign relevance: order-confirmed, delivery-update, appointment-reminder, early-access, reactivation, booking-conversation, sender-recognition, black-friday-bags, black-friday-trolley, double-digit-sale, order-details or growth-sculpture. Seasonal artwork does not establish a Burst offer, discount, deadline or campaign-performance result. Do not use a sender ID graphic to imply regulatory approval.

Use `template_id: graphic-focus`, `composition: graphic-hero` and `graphic_id` for a prominent standalone graphic, square or portrait. Both brand positions are supported; top has separate bottom CTA strip, bottom keeps CTA/website in the body above the brand-only bar. Use a short headline and concise supporting copy so the graphic remains large. `graphic_colour: brand` preserves a registered prepared graphic’s approved Burst hues and tonal shading. Unprepared source graphics use bounded palette mapping. Optional navy, violet or cyan gives a bounded theme using that colour, navy, cloud and white. Original source files remain unchanged. Recolouring applies only to registered graphic artwork, never photographs, the approved Burst logo or third-party marks. No arbitrary hex values, fonts, URLs or coordinates. Native alpha is preserved apart from alpha 0–2 noise; reviewed prepared variants remove edge defects before registration. Opaque reference graphics retain their original background.

A `graphic_id` may replace the deterministic SMS/phone in person-plus-message. Omit `message`, `sender_name` overrides and `phone_view` overrides when the graphic supplies its own content. The graphical object is proportionally contained, content and minimum readable size are checked, and the same safe subject/overlay gates apply. Wide text-heavy graphics will Hold in the narrow person layout: use graphic-hero, or a simpler shopping prop alongside the person. Do not deliver unreadable raster copy merely because an asset was approved.

Tori explicitly approved YOUR BRAND as an explanatory sender/white-label label on 10 October 2026. It may remain on the approved sender-recognition graphic. Prefer meaningful fictional sender/message examples by default; use YOUR BRAND deliberately when the brief explains where the customer's brand appears. ACME SHOP, Acme Beauty or Burst SMS may be used where appropriate. The deterministic UI uses the locked font and palette. Recreating an approved low-resolution reference with deterministic text is allowed; do not paint over baked text with an invented font, misrepresent a live conversation or fabricate unsupported brand/product claims. Approved raster graphic typography is retained as owner-approved illustrative content, not used for new campaign headlines, body copy, CTA or branding.

The 145x85px message thumbnail is reference-only due to resolution. The Kudosity contact sheet is reference-only because it contains Kudosity branding, historical UI and other channel assets: do not export the contact sheet as a Burst creative. The subsequently supplied ZIP provides individual source masters in assets/kudosity-source-library with historical UI/channel notes. Approval is recorded for all supplied files; registration for delivery still needs suitable resolution, contrast, framing and source suitability.

`photo_id: vhey` is the authentic cleaned transparent portrait. User confirmed her name and approved mask-only cleanup; no role, quotation or endorsement is inferred. RGB channels match the original supplied portrait exactly. Hair, hands, phone and clothing are retained, with background alpha residue removed. Use `image_treatment: cutout`, `photo_fit: contain` and the complete registered crop. Never recolour Vhey or re-run generative portrait edits. The existing team-coffee template remains for approved Philippines team imagery, not an inferred substitution.

Inspect every exact output at full resolution and feed size, including graphic edges, all embedded illustrative text, typography exceptions scoped to approved raster content, contrast, palette, readability, subject preservation, campaign relevance, CTA, claims and next action. Technical graphic checks measure bounds, scale and palette; they cannot establish embedded-text contrast or creative effectiveness. A failed visual check still Holds. Examples: references/examples/graphic-order-update.json, references/examples/vhey-message.json and references/examples/vhey-black-friday.json.

### Additional source masters supplied 10 October 2026
The named transparent sender-recognition PNG replaces the earlier JPEG as the preferred source. `order-details` and `growth-sculpture` add distinct approved graphics. Eight renamed attachments duplicate earlier originals; do not create duplicate catalogue entries. The complete Kudosity source library is preserved in `assets/kudosity-source-library`, including original SVG masters, source manifest and README. Follow its historical UI and channel notes; this does not automatically register every source as a supported renderer input.

### Channel imagery is explicitly requested only
Use RCS, WhatsApp or Viber imagery only when the actual user request specifically names that channel. Generic messaging, customer-update, automation and SMS requests default to SMS imagery. Never infer a channel from the audience, an uploaded contact sheet or the availability of an asset. For a registered channel asset, record `imagery_channel` and a verbatim `channel_request` excerpt naming the channel; do not invent that excerpt. `viber-order-update` is the supplied approved, mask-cleaned Viber card. Use `graphic_colour: brand` to preserve the channel illustration and mark, never recolour a third-party logo. The campaign heading/CTA/bars still use locked Burst styles. RCS/WhatsApp masters retain their source notes in assets/kudosity-source-library; library presence is not a product availability claim or permission to bypass supported renderer registration. Illustrative sender labels and delivery ticks do not establish a live customer or guarantee delivery.

## Person-plus-message composition (0.4.10)

Apply only to person-plus-message creatives, not as the default campaign style. Preserve the approved headline, colours, CTA, website and brand bar when those elements already work.

Compose the person and SMS example as one connected visual group. Scale the person to occupy most of the available body height, preserving proportions and the complete supplied subject. For portraits that end at the torso, anchor the lower edge to the bottom of the visual area immediately above the reserved CTA space. Do not leave the cropped torso floating in open space or extend the body artificially.

Position the SMS card closer to the person, beside their phone or upper torso, with deliberate alignment. Keep it clear of faces, hands, clothing and equipment. Increase its size where needed so the sender name and message remain readable at feed size. Reduce the gap between person and message before adding decoration. Use scale, proximity and alignment to create cohesion.

If the supplied portrait cannot sit naturally in the available layout, choose another registered image or supported composition. Do not change working copy or brand elements merely to accommodate an unsuitable portrait.

Mandatory visual check: reject floating cutouts, visibly abrupt torso endings, excessive gaps and disconnected person/message elements. Compare suitable arrangements privately and deliver only after full-resolution and feed-size inspection passes. Record observed portrait anchoring, subject preservation, card readability, separation and cohesion in the existing visual_composition, photo_edges, body_balance and campaign_effectiveness inspection notes. Technical checks alone do not pass this standard.

The renderer fits adjacent person/message groups to their actual proportions, uses a 24px group gap and a wider 380px card region at the 1080px layout scale, and anchors the portrait at the CTA boundary. Approved-alpha portraits may lose wholly transparent outer padding only; every nonzero alpha pixel remains. Layered arrangements preserve horizontal negative space and retain the actual subject-opacity collision check. If the available width limits portrait scale, inspect the result and choose a better registered image or supported composition rather than stretching, cropping the subject or forcing a pass.


## Visible portrait grounding and connected composition (0.4.12)

This corrects the floating Vhey portrait failure reported by Tori on 12 October 2026. An invisible layout coordinate is not visual grounding. Apply this acceptance rule to every user and every photographic layout. A cropped torso must finish naturally at a visible scene surface or structural boundary; reject an exposed torso cut edge suspended in uninterrupted background, even when its frame reaches the reserved CTA coordinate. Never invent or extend anatomy, add a decorative connector, or infer a background from a finished reference ad. Preserve approved subject pixels, proportions and protected brand elements.

The registered Vhey cutout now requires visible grounding. Supported person-plus-message places her at the contrasting navy CTA boundary, with white destination/terms text and the unchanged violet CTA and white identity bar. The supplied right-hand crop is anchored to the right canvas edge, with a larger proportional portrait and its SMS card beside the torso/phone region. Vhey therefore requires right placement; left, centre, layered and other ungrounded layouts Hold rather than exposing her supplied side cut edge in open space. A technical grounding gate rejects a portrait ending above the boundary or a boundary with less than 3:1 contrast. Other layouts using this cutout must meet the same gate or Hold; choose a supported grounded arrangement or a registered continuous photographic scene. Do not claim the check establishes artistic cohesion.

Before delivery, inspect the exact full-resolution image and a representative Facebook feed view. In visual_composition, photo_edges, body_balance and campaign_effectiveness, record the visible surface/boundary that grounds the person, actual torso termination, portrait scale, relation of message to phone/upper torso, and unified reading order. Reject stranded message cards, small pasted-on people, equally competing elements or a nominally touching portrait that still looks abruptly cut off. Favour the continuous-scene relationship in the user's Keep Customers in the Loop reference; a colour strip is an available grounding mechanism, not permission to pass a weak composition. If the available source cannot achieve that quality, Hold and identify the missing registered scene asset or layout capability.


## Silhouette contact, not bounding-box contact (0.4.13)

Supersedes 0.4.10–0.4.12 complete-subject preservation only for the explicitly registered shallow lower-jacket/forearm grounding crop. Tori requested correction of the remaining wedge below Vhey on 12 October 2026. The unchanged source is preserved. A reviewed crop may remove a bounded lower jacket/forearm band to achieve a continuous opaque contact edge; never alter anatomy or clip face, hair, palms, fingers or phone. Every protected source region must remain inside the crop. No arbitrary user crop or guessed mask is enabled. If a safe crop cannot establish contact, Hold and use another registered subject or continuous scene.

Vhey's renderer now chooses the shallowest safe source crop whose full registered lower-torso contact span is opaque, bounded by a 10% maximum of visible subject height and protected-region clearance. It checks the actual resampled alpha across the entire exported contact span at the CTA edge. One touching point or an image rectangle aligned to the bar cannot pass. Missing, transparent or partially disconnected columns block delivery. Keep the right-edge anchor, readable adjacent message, original logo/font/palette and brand-only bar.

Inspect full resolution and feed size specifically beneath the forearm and jacket, including the right-side notch that failed in 0.4.12. Require no background wedge between the visible lower torso and CTA, a natural deliberate crop and preserved fingers, palms and phone. Record the actual crop and contact findings in photo_edges, visual_composition and body_balance. Technical span checks do not prove overall visual cohesion. Do not show weak or failed attempts or describe bounding-box contact as sufficient grounding.


## Eight approved campaign imagery options (0.4.14)

Tori approved all eight newly generated supporting images for plugin users on 12 October 2026. They are AI-generated illustrative scenes, not documentary photographs, actual employees, customers or testimonials. Approval allows using these registered sources in new campaigns, subject to normal claim, brand, crop, subject, accessibility, composition and delivery checks; it does not approve every derivative or a product claim.

Registered photo IDs: retail-connection, order-fulfilment, appointment-welcome, team-collaboration, hospitality-owner-full-body, business-professional-full-body, multicultural-manila-collaboration and philippines-travel-tourism. Select by audience and use case. Reuse the original continuous counters/desks for naturally grounded compositions; preserve faces, hands and equipment and inspect any cover crop. The two full-body sources retain complete shoes and hands. Their original generated alpha is softly translucent and ranges 0–254; the renderer composites them deterministically onto locked cloud and uses background-preserving panel photography. They are NOT registered clean-alpha cutouts or high-energy-casual sources. Do not remove their backgrounds, infer an alpha mask or extend anatomy. Native sources remain unchanged.

For new cutouts, register safe framing/grounding and protected regions per source before enabling them; do not copy Vhey's crop onto another person. Photograph selection remains optional and concept-led. See assets/photography/approved-expansion-2026-10-12.json and references/image-library.md for provenance and campaign scope.


## Campaign asset toolkit and registered prop composition (0.4.15)

Tori requested creation, registration and plugin access for the campaign asset toolkit on 12 October 2026. Supporting photographs are illustrative AI-generated sources, never real customer, staff, patient or student proof. Use the existing commercial-team photo for actual Philippines team campaigns. New individual staff portraits and verified current product screenshots require actual supplied sources; do not invent them.

New photo IDs: phone-in-hand-close-up, laptop-workspace-detail, parcel-shopping-props, travel-booking-props, coffee-invitation-props, healthcare-reception-scene, education-services-scene and logistics-dispatch-scene. Select by audience and message, preserve complete relevant objects, faces, hands and equipment, and inspect any crop. Screens and paperwork are illustrative/blank, not product or customer evidence. No generative final campaign assembly or source-photo recolouring is enabled.

Reusable native graphic IDs phone-frame and laptop-frame have editable SVG masters and deterministic PNGs in assets/device-frames. Use graphic-focus/graphic-hero to render them; they contain no UI or copy and do not establish feature availability. The existing recognition phone remains the preferred deterministic frame for a readable fictional SMS. Do not paste fabricated dashboards into device screens. Current approved screenshots must be separately provided, verified and registered before insertion.

Choose template_id prop-focus, composition prop-hero, a registered prop_id and square/portrait for one prominent photographic still life: parcel-shopping-props, travel-booking-props or coffee-invitation-props. Keep photo_id, graphic_id and message empty, use original-background panel photography, and keep the protected bars, Noto Sans, CTA and destination. Photographic props keep their original colours/backgrounds and are never passed through illustration recolouring or inferred cutout masks. Use short relevant copy so the prop has confident scale. Inspect full and feed size for complete objects, hierarchy and a coherent next step. Coffee is for a deliberate invitation, not filler; image availability does not invent a free-coffee offer or terms.

This supersedes older statements that no prop is registered: three original-background photographic props now exist. High-energy team-coffee still requires authentic prepared team alpha and a separately prepared native-alpha coffee prop; these still lifes and the opaque team photo do not satisfy that composition. Ordinary team-coffee and prop-focus remain available. See assets/photography/campaign-toolkit-2026-10-12.json. Every final campaign still needs fresh delivery validation; source availability is not automatic approval of an arbitrary derivative.


## Controlled campaign sizing (0.4.16)

Use `heading_scale` (0.85–1.6, default 1) to scale headline and accent together; `message_scale` (1–1.6, default 1) to enlarge deterministic SMS sender and message text. The renderer remeasures wrapping, card height and header space. No new font, colour, coordinate, logo size or brand-bar control is permitted. Select sizes from actual composition and feed readability, not a claim that larger always performs better.

Use `image_scale` and `graphic_scale` (0.65–1, default 1) to adjust registered photography/props and raster graphics proportionally inside their allocated body regions. 1 is the largest safe allocation; to enlarge beyond it, choose a supported composition with more visual space or reduce copy. Do not crop, stretch or overflow to force more scale. Grounded portraits retain their source-edge and lower-boundary anchor. Continuous photo-background requires image_scale 1 to preserve edge-to-edge coverage. Raster graphic embedded text is not editable through message_scale. Missing or incompatible source/layout options Hold rather than silently ignoring a control.

Inspect final full/feed size after resizing for preserved subjects, grounding, safe SMS placement, legible raster text and visual cohesion. Resizing must still pass original logo pixels, fonts, palette, contrast, bounds, collisions, graphic minimum readability, CTA-left/website-right, terms, brand-bar separation, integrity and exact delivery reconstruction checks. Never weaken a gate or infer artistic quality from sizing success. All users receive these controls with the updated plugin release.

For photo-background SMS overlays, `message_width_scale` (0.75–1.4, default 1) adjusts card width; sender/message text size remains controlled separately. The complete content-sized card must fit safe bounds and avoid every subject. Other compositions Hold non-default width sizing rather than ignoring it.


## Playful social input contract (0.4.18)

Use the native `social-playground` illustration when the user asks for an illustrated social concept, visual gag, or message-led graphic. A request for a fun or exciting post does not by itself mean the audience wants illustration: when the brief is people-focused, prefer a registered people-first photograph and carry the fun through the headline, scene, and caption. Keep normal and photographic layouts available.

For `social-playground`, retain `creative_style: playful-social`, `composition: social-hero`, the bottom brand bar, and square/portrait format. Choose `social_motif`: `phone-chat` for a message shown on a complete phone over a lively colour field, `mystery-sender` for an explicitly requested disguise joke, `message-pop` for a prominent message, or `spotlight` for a focused reveal. Choose `social_backdrop`: `violet` or `navy`. Supply a short headline/accent, concise support, a fictional business `sender_name`, and a natural, meaningful fictional `message`. Inspect phone proportions, bubble outline and readability at feed size. See `references/examples/social-mystery-sender.json`.

The message graphic must read as a plausible generic SMS conversation, not an invented product screenshot. Show one sender header once and one distinct message bubble. Keep a white card on a visibly contrasting coloured field; never stack white-on-white cards or use same-fill overlapping panels with indistinguishable edges. Give the message bubble a clear tonal fill or visible outline. Do not use decorative ellipses in place of a message, repeat the sender name, or add folded package-style labels. Keep playful effects around the conversation card, not over its text. Use a fictional business sender such as `ACME SHOP` and a short customer-relevant line such as `Hi Mia, your order is ready for collection.` Do not imply the example is a real customer or live product interface.

Native illustration may personify a message with sunglasses/moustache, exaggerated scale and folded reveal labels. These are illustrative metaphors, not actual UI, security/anonymity features, verification, registration or performance evidence. Avoid decorative strokes that add clutter without strengthening the idea. Never modify brand assets or put costumes/effects on the Burst logo, real people or third-party marks. No arbitrary coordinates, colours, external images, fonts or asset paths. All illustration is generated by registered deterministic code using the locked palette. Cyan emphasis on navy; white emphasis on violet. The brand and CTA bars remain isolated and unchanged.

Tori authorised this renderer extension on 22 October 2026 to allow more adventurous on-brand social creative. This authorises the visual treatment, not product/route claims or publication. Inspect the exact full/feed export for a clear visual joke, intact illustration, readable name/message, deliberate hierarchy and coherent next action. Reject clutter, incidental decorations and a motif that does not serve the campaign. Require normal evidence, actual-background contrast, text fit/collision, integrity, exact reconstruction and all eight delivery inspection checks. Do not substitute native illustration approval for photographic provenance, or relax any existing gate.


## User-supplied campaign imagery (0.4.20)

Use the `prepare-upload` and `render --upload-dir` path in [user-uploads.md](user-uploads.md) for photos, illustrations, phones and screenshots. The `uploaded-image` template accepts a hash-bound, reviewed campaign-local source supplied by the user or generated privately for the campaign; this extends the catalogue-only source rule without changing brand or delivery checks. The candidate snapshots the private source and final validation rechecks it. Do not put campaign images in the shared plugin package.

Choose composition from the image and campaign idea; do not funnel every upload into the same tile. Continuous-scene photos can connect with the headline through a full-body `photo-background`, a deliberate `hero` crop, or connected `side-by-side`, `image-first` and `text-first` arrangements. Use `panel`, `rounded` or `circle` only where the frame supports the concept and the subject remains intact. Compare safe options privately, inspect real crop boundaries and keep the subject, headline and CTA in one clear reading path. Avoid detached floating imagery, empty bands, redundant decoration and gaps that make the image feel pasted on.

Keep phones, screenshots and channel imagery at their supplied proportions in a contained panel; never crop, mask, recolour or cover embedded content. True supplied-alpha complete subjects may use the registered cutout treatment and controlled Burst shapes behind them. Never infer alpha or remove a background. Brand logo, identity bar, typography, palette and CTA remain locked. Organic social caption copy supports up to three contextual hashtags, chosen explicitly or supplied by the renderer; paid copy omits hashtags. The tags appear in `recommended-copy.md`, outside the artwork.

## Social caption and hashtags (0.4.20)

`post_type` defaults to `organic`; set `hashtags` to up to three relevant tags when the campaign has a deliberate tag strategy. Otherwise the renderer recommends a short contextual set in `recommended-copy.md`. For paid social, set `post_type: paid`; hashtag input is rejected and no tags are appended. Review the caption and tags for campaign relevance and local fit before publication. Hashtags are caption copy and never rendered into the artwork.


## Explicitly requested image hero with overlaid copy (0.4.25)

Only when the user specifically requests a full-bleed image with headline and CTA overlaid, choose `composition: image-overlay` and retain their verbatim request in `layout_request`. A request for a fun, bold or engaging ad alone does not select it. Keep all existing layouts and defaults unchanged. This mode supersedes the separate heading/CTA-panel requirements only for that explicit layout: retain the unchanged white top brand bar and original Burst SMS Philippines lockup, then fill the entire remaining canvas with one reviewed image. Overlay headline, accent, supporting line, CTA button, destination and approved terms on the image. No opaque heading or CTA panel is added. This does not enable transparent brand bars or reversed production logos.

Use `template_id: uploaded-image`, `photo_id: user-upload`, `brand_strip: top`, `photo_fit: contain`, `image_treatment: panel`, `image_scale: 1`, `photo_backdrop: none` and `creative_style: default`. Square and portrait are supported. The source must exactly match the full region below the 150px bar: 1080 x 930 for square or 1080 x 1200 for portrait, or a proportional source that rasterises to exactly that region. Do not stretch, crop, mask or repaint a supplied device. Request or privately generate a suitably framed source with clear upper headline and lower CTA areas if necessary. Keep `message` empty: never add simulated UI over supplied phones/screens. The ordinary image and channel reviews still apply.

During source inspection, record `protected_regions` in the source-review JSON. Each entry has `label` and `box: [x, y, width, height]` in orientation-correct source pixels. Include every face, hand, complete phone/screen and essential visual content. These are reviewer evidence describing content, not arbitrary campaign positioning controls. At least one region is required; missing, invalid or out-of-bounds regions Hold. Inspect their completeness and accuracy; a nonempty array alone does not prove subject protection. The renderer maps regions to the output and rejects headline, CTA, website or terms covering them.

`heading_style: light` uses navy/violet text directly over a suitably light image; `navy` uses white/cyan directly over a suitably dark image. It does not paint a navy heading panel. Actual underlying-pixel contrast must pass for every text glyph; do not add unregistered decorative shapes or weaken contrast to force a pass. If the source is busy, obscures subjects or cannot provide readable overlay areas, reframe/regenerate the source privately or Hold. Keep the complete phone and its embedded text legible at feed size.

Inspect exact full/feed exports for continuous image coverage to all edges below the bar, one dominant image, readable overlays, intact faces/hands/devices, coherent hierarchy and clear next action. All eight final inspection fields and fresh deterministic delivery validation remain mandatory. Keep private campaign sources and reviews outside the shared/public plugin.
