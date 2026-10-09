# Approved Philippines image library

These registered files are approved as supporting photography sources for Burst SMS Philippines creative. They are not finished advertisements and must never be presented as approved final artwork without deterministic composition and the complete compliance gate.

## Registered sources

- `assets/photography/diverse-filipino-workforce-portrait-collage.png` — clean-background portraits spanning small business, delivery, construction, healthcare, office and service roles.
- `assets/photography/everyday-connections-manila.png` — candid mobile and workplace scenes for messaging, operations and customer-connection stories.
- `assets/photography/good-coffee-good-people-montage.png` — warmer retail, hospitality, delivery and support scenes for human, approachable campaigns.
- `assets/photography/diverse-collaborative-work-portrait-grid.png` — clean-background portraits and collaborative groups for business, team and service-led communications.

## Required use

- Select a coherent single panel or scene that supports the audience and message. Do not place the full contact sheet into an advertisement unless a montage is explicitly required.
- Record the source filename and crop coordinates in the production record so the selected photography is traceable.
- Preserve faces, bodies, uniforms, safety equipment and visible third-party marks. Never use generative editing to change identity, ethnicity, clothing, expression, equipment or signage.
- Do not imply that depicted people are Burst SMS customers, employees, partners or testimonial participants. Treat all scenes as illustrative unless separately documented.
- Do not infer or state a person's name, employer, result, endorsement, protected trait or personal story from the image.
- Use authentic Philippine business contexts without stereotypes, tokenism or forced slang.
- Reserve clean space for copy and apply the approved white brand bar, unchanged horizontal Burst SMS Philippines lockup, Noto Sans hierarchy, navy/violet/cyan palette and approved CTA treatment through deterministic composition only.

## Approval boundary

Cropping a panel, colour treatment, retouching, adding copy, adding the logo or otherwise composing a new layout creates new creative. The result must pass the full logo, palette, typography, copy, claims, accessibility, local-fit, dimensions and destination checks before it can be displayed or delivered. The library approval does not approve every possible crop, caption or derivative.

## Dynamic campaign presentation

The approved source does not mandate a rectangular panel in the final ad. The renderer supports proportionate panels, rounded/elliptical masks and clean-background cutouts. Choose coherent scenes anywhere in the four approved sheets with recorded source crop and descriptive alt text. Check masked faces, hair, hands, clothing, equipment and edges privately before delivery. Background removal that damages a subject fails review; select another crop/treatment. Team-supplied photography requires usage approval and library registration, not approval of an exact finished ad.

Cutout quality: current opaque source sheets have no approved subject-alpha masks. A requested cutout therefore preserves the original photograph background and records a fallback. Future professionally prepared transparent sources must be registered, approved for subject/edge preservation and integrity-locked before use. Never remove bright pixels from hair/clothing/equipment. `photo_backdrop` is optional and defaults to none; any backing must be composited through the exact photo mask.

`two-shoppers`: registered coherent scene of two illustrative shoppers checking a phone together, from the preserved everyday-connections source. They are not employees, customers or endorsers. Face and hands/phone exclusion boxes guide full-background crop/overlay rejection, supplemented by actual full/feed inspection.

High-energy team production requires an authentic owner-approved Philippines team RGBA asset with `approved_subject_alpha: true`, `identity: philippines-team`, complete-subject crop and team-coffee template scope. Props require approved native alpha, category and template scope in catalogue props. Current team JPEG is opaque and no coffee prop is registered. Hold the high-energy coffee request; ordinary background-preserving photography remains supported.

## Optional person-plus-message composition (0.4.7)

Use `template_id: person-plus-message` and `composition: person-plus-message` when requested or clearly suited to a brief where a person adds human relevance and a message graphic explains updates, reminders, promotions or sender recognition. Never make it the default or force people, graphics or shapes into other campaigns. Keep the user's chosen style and existing layouts available.

Use square or portrait, `heading_style: navy`, `brand_strip: bottom`, `image_position: left` or `right`, registered `photo_id`, explicit meaningful fictional `sender_name` and `message`. Headline is short and oversized with white type and a concise cyan `accent`; supporting copy must fit one line. Measure wrapping and padding. Use `phone_view: card` (also the auto treatment) or `full` for a complete readable phone. Full phones that cannot fit without unreadable text Hold; do not substitute clipped devices. `graphic_decoration: none` is default; optional `cyan-band` stays behind the graphic. `graphic_placement: adjacent` is default. Optional `layered` uses fixed inward positions with approved native-alpha cutouts only; an opacity check rejects any foreground pixel beneath the entire message/phone overlay, including soft hair. It may overlap transparent negative space, never faces, hands, clothing or equipment. No arbitrary coordinates.

Photography is proportionally contained within one adjacent person/UI group. Keep the original background unless a registered professionally prepared complete-subject alpha asset is available. No near-white removal. Preserve faces, hair, hands, clothing and physical equipment. User crop selection requires an actual inspection of the selected subject. Avoid disconnected tiles, excess gaps and competing focal points; try left/right or another suitable scene if the balance is poor. Illustrative people are not employees, customers or endorsers. Never use YOUR BRAND placeholders. CTA stays lower left and website lower right in one row inside the body, with approved terms nearby. The bottom white bar remains brand-only.

Acceptance brief: `references/examples/person-plus-message.json`, ACME SHOP / Your order is ready to collect. Inspect the exact PNG at full resolution and feed size for immediately understandable headline, readable message, preserved subjects, visual balance, edges, hierarchy and next action. Technical checks alone cannot establish creative quality; failed visual inspection Holds. Apply all existing claim, brand, accessibility and delivery checks. Reference photography or uploaded examples are not automatically registered assets.
