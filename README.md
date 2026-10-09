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

Release 0.4.7 removes automatic cropped phone details, adds full-device/SMS-card selection and deliberate hero/cover photo presentation with effective-crop reporting, and requires comparing relevant private compositions. Organic caption hashtag guidance is distinct from paid-ad copy.

Version 0.4.5 adds full-middle photographic composition with compact SMS overlays, lower-image CTA scrim, measured navy heading and protected bottom white identity bar. Explicit controlled positions and registered subject exclusion boxes reject clipping/obscuring of known faces/hands/action; actual full/feed inspection remains mandatory.

Version 0.4.7 adds explicitly selected high-energy-casual composition while preserving default artwork. Uses only registered professionally prepared native-alpha people and deliberate props. Current approved team source is opaque and no coffee prop is registered, so that acceptance example correctly Holds with no artwork. No near-white keying or invented substitutes.

## Optional person-plus-message composition (0.4.7)

Use `template_id: person-plus-message` and `composition: person-plus-message` when requested or clearly suited to a brief where a person adds human relevance and a message graphic explains updates, reminders, promotions or sender recognition. Never make it the default or force people, graphics or shapes into other campaigns. Keep the user's chosen style and existing layouts available.

Use square or portrait, `heading_style: navy`, `brand_strip: bottom`, `image_position: left` or `right`, registered `photo_id`, explicit meaningful fictional `sender_name` and `message`. Headline is short and oversized with white type and a concise cyan `accent`; supporting copy must fit one line. Measure wrapping and padding. Use `phone_view: card` (also the auto treatment) or `full` for a complete readable phone. Full phones that cannot fit without unreadable text Hold; do not substitute clipped devices. `graphic_decoration: none` is default; optional `cyan-band` stays behind the graphic. No arbitrary coordinates or overlays across the person.

Photography is proportionally contained within one adjacent person/UI group. Keep the original background unless a registered professionally prepared complete-subject alpha asset is available. No near-white removal. Preserve faces, hair, hands, clothing and physical equipment. User crop selection requires an actual inspection of the selected subject. Avoid disconnected tiles, excess gaps and competing focal points; try left/right or another suitable scene if the balance is poor. Illustrative people are not employees, customers or endorsers. Never use YOUR BRAND placeholders. CTA stays lower left and website lower right in one row inside the body, with approved terms nearby. The bottom white bar remains brand-only.

Acceptance brief: `references/examples/person-plus-message.json`, ACME SHOP / Your order is ready to collect. Inspect the exact PNG at full resolution and feed size for immediately understandable headline, readable message, preserved subjects, visual balance, edges, hierarchy and next action. Technical checks alone cannot establish creative quality; failed visual inspection Holds. Apply all existing claim, brand, accessibility and delivery checks. Reference photography or uploaded examples are not automatically registered assets.
