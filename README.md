# Burst SMS Philippines Marketing Lab

This repository is the source of truth for the Burst SMS Philippines design system and the team Codex plugin that applies it.

## What is included

- `design-system/` contains the visual system, design tokens, content guidance, templates, and a browsable reference page.
- `plugins/burst-sms-ph-marketing-lab/` contains the reusable Codex plugin.
- `.agents/plugins/marketplace.json` exposes the plugin through a repository-local team marketplace.
- `scripts/validate-design-system.mjs` checks the key files and token consistency without external dependencies.

## Preview the design system

Open `design-system/index.html` directly, or run a small local server from the repository root:

```powershell
python -m http.server 4173
```

Then visit `http://localhost:4173/design-system/`.

## Install the team plugin

Register this repository as a marketplace once:

```powershell
codex plugin marketplace add .
```

Then install the plugin:

```powershell
codex plugin install burst-sms-ph-marketing-lab@personal
```

If your Codex CLI displays a different marketplace name after registration, use that name after `@`.

## Validate

```powershell
node scripts/validate-design-system.mjs
```

The plugin package also has its own validator in the bundled Codex plugin-creator tooling.

## Brand governance

Use the supplied logo artwork without redrawing, recolouring, stretching, or adding effects. Marketing claims must have a current source. Product, pricing, compliance, and performance statements require review by the relevant owner before publication.


## Work-only creative production

The existing plugin now bundles six deterministic templates, square (1080 × 1080)
and portrait (1080 × 1350) exports, approved assets, Noto Sans fonts and mandatory
brand checks inside its skill. It runs in Work with Python 3.11+ and the pinned
local runtime dependencies. No external hosting, MCP connection or authentication
credentials are required. Ordinary Chat explains that creative production requires Work.

Candidates stay private until technical checks and inspection of the exact image,
copy, claims, accessibility and local fit pass. This does not publish content or
replace business approval. See [runtime instructions](plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab/references/work-runtime.md)
and [fresh-conversation acceptance tests](tests/FRESH_CONVERSATION_TESTS.md).

Run the checks:

```sh
python -m pip install -r plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab/runtime/requirements.txt
npm test
npm run test:creative
```

Version 0.4.1 adds measured headline/copy layout, bounded readable heading sizes,
proportionate photo frames, top/bottom brand strips and image-first/text-first
composition choices. Recognition accepts optional registered illustrative photos.
The original logo, approved fonts/palette, safe margins, export sizes and mandatory
private inspection plus delivery validation remain required.

Owner authorisation for team release was given on 9 October 2026. Release follows
passing automated, visual and CI checks. The existing Git-synced plugin identity
remains unchanged; no external hosting or service credentials are needed.

Version 0.4.2 makes balanced side-by-side body composition the automatic default for copy/phone/photo layouts. Brand/CTA bars stay unchanged; meaningful visible message cards and visual composition review are mandatory for every user.

Explicitly requested landscape (1200 × 628), static Story/Reel cover (1080 × 1920) and custom PNG dimensions are supported. Square/portrait remain default. Custom sizes are 600–4096px per side, aspect ratio 1:2 through 2:1, with body recomposition and unchanged delivery checks. Narrow banners and print/video/vector exports need dedicated capabilities.

Release 0.4.3 makes CTA/terms follow brand placement, groups photography with content-sized SMS cards, removes automatic cyan backdrops and destructive white-key cutouts, and requires explicit edge/balance/CTA visual checks. Current opaque photos retain their original backgrounds for cutout requests; approved native subject-alpha sources can be registered later.

Release 0.4.8 removes automatic cropped phone details, adds full-device/SMS-card selection and deliberate hero/cover photo presentation with effective-crop reporting, and requires comparing relevant private compositions. Organic caption hashtag guidance is distinct from paid-ad copy.

Version 0.4.5 adds full-middle photographic composition with compact SMS overlays, lower-image CTA scrim, measured navy heading and protected bottom white identity bar. Explicit controlled positions and registered subject exclusion boxes reject clipping/obscuring of known faces/hands/action; actual full/feed inspection remains mandatory.

Version 0.4.8 adds explicitly selected high-energy-casual composition while preserving default artwork. Uses only registered professionally prepared native-alpha people and deliberate props. Current approved team source is opaque and no coffee prop is registered, so that acceptance example correctly Holds with no artwork. No near-white keying or invented substitutes.

## Optional person-plus-message composition (0.4.8)

Use `template_id: person-plus-message` and `composition: person-plus-message` when requested or clearly suited to a brief where a person adds human relevance and a message graphic explains updates, reminders, promotions or sender recognition. Never make it the default or force people, graphics or shapes into other campaigns. Keep the user's chosen style and existing layouts available.

Use square or portrait, `heading_style: navy`, `brand_strip: bottom`, `image_position: left` or `right`, registered `photo_id`, explicit meaningful fictional `sender_name` and `message`. Headline is short and oversized with white type and a concise cyan `accent`; supporting copy must fit one line. Measure wrapping and padding. Use `phone_view: card` (also the auto treatment) or `full` for a complete readable phone. Full phones that cannot fit without unreadable text Hold; do not substitute clipped devices. `graphic_decoration: none` is default; optional `cyan-band` stays behind the graphic. No arbitrary coordinates or overlays across the person.

Photography is proportionally contained within one adjacent person/UI group. Keep the original background unless a registered professionally prepared complete-subject alpha asset is available. No near-white removal. Preserve faces, hair, hands, clothing and physical equipment. User crop selection requires an actual inspection of the selected subject. Avoid disconnected tiles, excess gaps and competing focal points; try left/right or another suitable scene if the balance is poor. Illustrative people are not employees, customers or endorsers. Never use YOUR BRAND placeholders. CTA stays lower left and website lower right in one row inside the body, with approved terms nearby. The bottom white bar remains brand-only.

Acceptance brief: `references/examples/person-plus-message.json`, ACME SHOP / Your order is ready to collect. Inspect the exact PNG at full resolution and feed size for immediately understandable headline, readable message, preserved subjects, visual balance, edges, hierarchy and next action. Technical checks alone cannot establish creative quality; failed visual inspection Holds. Apply all existing claim, brand, accessibility and delivery checks. Reference photography or uploaded examples are not automatically registered assets.

## Approved campaign graphics and Vhey (0.4.8)

Tori supplied and approved the attached graphics on 10 October 2026, including permission to recolour graphic artwork using only the Burst SMS approved palette. They are optional campaign assets, not a new default style. Choose assets by campaign relevance: order-confirmed, delivery-update, appointment-reminder, early-access, reactivation, booking-conversation, sender-recognition, black-friday-bags, black-friday-trolley, double-digit-sale, order-details or growth-sculpture. Seasonal artwork does not establish a Burst offer, discount, deadline or campaign-performance result. Do not use a sender ID graphic to imply regulatory approval.

Use `template_id: graphic-focus`, `composition: graphic-hero` and `graphic_id` for a prominent standalone graphic, square or portrait. Both brand positions are supported; top has separate bottom CTA strip, bottom keeps CTA/website in the body above the brand-only bar. Use a short headline and concise supporting copy so the graphic remains large. `graphic_colour: brand` preserves a registered prepared graphic’s approved Burst hues and tonal shading. Unprepared source graphics use bounded palette mapping. Optional navy, violet or cyan gives a bounded theme using that colour, navy, cloud and white. Original source files remain unchanged. Recolouring applies only to registered graphic artwork, never photographs, the approved Burst logo or third-party marks. No arbitrary hex values, fonts, URLs or coordinates. Native alpha is preserved apart from alpha 0–2 noise; reviewed prepared variants remove edge defects before registration. Opaque reference graphics retain their original background.

A `graphic_id` may replace the deterministic SMS/phone in person-plus-message. Omit `message`, `sender_name` overrides and `phone_view` overrides when the graphic supplies its own content. The graphical object is proportionally contained, content and minimum readable size are checked, and the same safe subject/overlay gates apply. Wide text-heavy graphics will Hold in the narrow person layout: use graphic-hero, or a simpler shopping prop alongside the person. Do not deliver unreadable raster copy merely because an asset was approved.

Tori explicitly approved YOUR BRAND as an explanatory sender/white-label label on 10 October 2026. It may remain on the approved sender-recognition graphic. Prefer meaningful fictional sender/message examples by default; use YOUR BRAND deliberately when the brief explains where the customer's brand appears. ACME SHOP, Acme Beauty or Burst SMS may be used where appropriate. The deterministic UI uses the locked font and palette. Recreating an approved low-resolution reference with deterministic text is allowed; do not paint over baked text with an invented font, misrepresent a live conversation or fabricate unsupported brand/product claims. Approved raster graphic typography is retained as owner-approved illustrative content, not used for new campaign headlines, body copy, CTA or branding.

The 145x85px message thumbnail is reference-only due to resolution. The Kudosity contact sheet is reference-only because it contains Kudosity branding, historical UI and other channel assets: do not export the contact sheet as a Burst creative. The subsequently supplied ZIP provides individual source masters in assets/kudosity-source-library with historical UI/channel notes. Approval is recorded for all supplied files; registration for delivery still needs suitable resolution, contrast, framing and source suitability.

`photo_id: vhey` is the authentic cleaned transparent portrait. User confirmed her name and approved mask-only cleanup; no role, quotation or endorsement is inferred. RGB channels match the original supplied portrait exactly. Hair, hands, phone and clothing are retained, with background alpha residue removed. Use `image_treatment: cutout`, `photo_fit: contain` and the complete registered crop. Never recolour Vhey or re-run generative portrait edits. The existing team-coffee template remains for approved Philippines team imagery, not an inferred substitution.

Inspect every exact output at full resolution and feed size, including graphic edges, all embedded illustrative text, typography exceptions scoped to approved raster content, contrast, palette, readability, subject preservation, campaign relevance, CTA, claims and next action. Technical graphic checks measure bounds, scale and palette; they cannot establish embedded-text contrast or creative effectiveness. A failed visual check still Holds. Examples: references/examples/graphic-order-update.json, references/examples/vhey-message.json and references/examples/vhey-black-friday.json.

Version 0.4.8 includes 13 prepared illustrative graphics and authentic mask-cleaned Vhey. Viber is explicitly requested only; RCS and WhatsApp source masters are retained with the same explicit-only selection rule and source suitability notes. No generic SMS creative may automatically use another channel. Fresh Work preflight reports 0.4.8.
