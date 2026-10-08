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

