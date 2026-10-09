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
