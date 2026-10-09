# Work visual production protocol

New artwork is produced only in Work through the bundled deterministic renderer. Never call an image-generation or image-editing tool. Do not generate photographic bases or add an alternate compositor.

1. Confirm actual Work command execution, packaged-file access, private file inspection and attachment capabilities. Ordinary Chat must explain that creative production requires Work and deliver no artwork.
2. Read all references in `SKILL.md`, resolve wording and factual claims, and run the local package preflight. No source/font/asset integrity failure may be ignored.
3. Select only registered templates, formats, photos and CTA choices. Reject brand overrides. The renderer owns logo, palette, typography, geometry, crop, destination and export.
4. Render privately. Technical success produces `INSPECTION_REQUIRED`, not a deliverable. Inspect the exact PNG, copy, photo context and alt text without displaying drafts.
5. Record actual copy/claim, composition, local-fit/photography and accessibility inspection results bound to the current PNG/campaign hashes. Missing evidence, unavailable inspection or a failed check means `Hold`.
6. Run the local delivery validator. It verifies the installed bundle, reproduces the exact PNG and requires a fresh `PASSED` receipt for all technical and inspection checks.
7. Attach only the exact passed PNG with its exact channel-ready copy, meaningful alt text and concise check result. No post-validation edits or failed variants may be shown.

See `work-runtime.md` for commands and file formats. Technical checks do not establish publication authority, claims, consent or endorsement. Required publication-owner approval remains a content-governance rule; no hosted approval system, signing credential or MCP app exists in this release.

## Art direction acceptance

Visual composition requires a clear campaign idea, a strong focal point, deliberate hierarchy, balanced visual weight, purposeful whitespace, relevant photography, finished mask edges and readability at feed size. Technical fit is necessary but does not establish creative quality. Inspect the actual phone message and selected photo subject. Reject poor wraps, placeholder screens, unexplained empty halves and irrelevant filler; improve the body and rerender privately. Preserve brand and CTA bars through every variation.

For release 0.4.3, inspect full resolution and feed size explicitly for photo halos, backdrop slivers, subject damage and excessive whitespace. Require separate `photo_edges`, `body_balance` and `cta_and_terms` results. Bottom-brand CTA and terms belong in the coloured body; the white brand bar contains identity only. Failed visual checks always block delivery despite technical success. Preserve original backgrounds whenever trustworthy cutouts are unavailable.

Require `campaign_effectiveness` inspection: state the audience/need, objective, substantiated reason to choose Burst SMS and next action, and confirm they read immediately at feed size. Use compliance positioning only for a relevant campaign. A technical pass does not predict effectiveness and cannot waive any visual failure.

For photo-background, inspect the exact cover crop and every overlay against the final image. Confirm edge-to-edge coverage between heading and brand bar, no tile/gutters, preserved subjects, readable SMS and same-row CTA/website. Registered subject checks and automatic contrast are necessary but never establish artistic quality. Keep failed crop/overlay attempts private.

High-energy-casual is explicit opt-in only. Require registered native alpha and professionally prepared complete subjects/props; opaque sources Hold, never white-key. Actual full/feed inspection must verify subject preservation, typography hierarchy, cohesive shapes behind subjects and safe CTA. The current missing team-alpha/coffee-prop acceptance case must Hold without artwork; style code/unit tests are not a validated campaign example.

## Optional person-plus-message composition (0.4.7)

Use `template_id: person-plus-message` and `composition: person-plus-message` when requested or clearly suited to a brief where a person adds human relevance and a message graphic explains updates, reminders, promotions or sender recognition. Never make it the default or force people, graphics or shapes into other campaigns. Keep the user's chosen style and existing layouts available.

Use square or portrait, `heading_style: navy`, `brand_strip: bottom`, `image_position: left` or `right`, registered `photo_id`, explicit meaningful fictional `sender_name` and `message`. Headline is short and oversized with white type and a concise cyan `accent`; supporting copy must fit one line. Measure wrapping and padding. Use `phone_view: card` (also the auto treatment) or `full` for a complete readable phone. Full phones that cannot fit without unreadable text Hold; do not substitute clipped devices. `graphic_decoration: none` is default; optional `cyan-band` stays behind the graphic. `graphic_placement: adjacent` is default. Optional `layered` uses fixed inward positions with approved native-alpha cutouts only; an opacity check rejects any foreground pixel beneath the entire message/phone overlay, including soft hair. It may overlap transparent negative space, never faces, hands, clothing or equipment. No arbitrary coordinates.

Photography is proportionally contained within one adjacent person/UI group. Keep the original background unless a registered professionally prepared complete-subject alpha asset is available. No near-white removal. Preserve faces, hair, hands, clothing and physical equipment. User crop selection requires an actual inspection of the selected subject. Avoid disconnected tiles, excess gaps and competing focal points; try left/right or another suitable scene if the balance is poor. Illustrative people are not employees, customers or endorsers. Never use YOUR BRAND placeholders. CTA stays lower left and website lower right in one row inside the body, with approved terms nearby. The bottom white bar remains brand-only.

Acceptance brief: `references/examples/person-plus-message.json`, ACME SHOP / Your order is ready to collect. Inspect the exact PNG at full resolution and feed size for immediately understandable headline, readable message, preserved subjects, visual balance, edges, hierarchy and next action. Technical checks alone cannot establish creative quality; failed visual inspection Holds. Apply all existing claim, brand, accessibility and delivery checks. Reference photography or uploaded examples are not automatically registered assets.
