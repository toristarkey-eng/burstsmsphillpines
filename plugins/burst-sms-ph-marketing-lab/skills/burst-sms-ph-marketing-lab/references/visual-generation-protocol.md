# Controlled visual-generation protocol

This is the only permitted workflow for producing new Burst SMS Philippines visual creative. It is fail-closed: if an intermediate can become user-visible before approval, do not begin generation.

This protocol is not permission to call a ChatGPT image-generation or image-editing tool. On ChatGPT, use exact registered approved artwork unchanged or return `Hold`. The steps below apply only to a private execution environment with a deterministic compositor and private final-file inspection.

## 0. Pass the live-source gate

Retrieve the current source files from `https://github.com/toristarkey-eng/burstsmsphillpines`. Where execution is supported, run `scripts/brand-preflight.mjs` and use its verified private output directory. The result must be `allowed: true` and `gate: PASSED`. Where execution is unavailable, retrieve and verify the equivalent live files and locked hashes with an available repository or web tool. Packaged copies alone are not sufficient for new creative. Any failure means `Hold`; do not call an image tool or display artwork.

## 1. Load and lock the sources

Read every reference named in `SKILL.md`. Confirm the approved asset inventory is accessible. Record the exact files selected for production.

For a new market lockup, use the actual supplied logo file `../../../assets/burst-sms-logo.png` unchanged. Assemble the divider and `PHILIPPINES` descriptor deterministically according to `design-system.md`. Never use a reference screenshot as a production master and never recreate the logo with a model.

## 2. Approve the message before visual production

Set every claim to one of: `Proposed copy`, `Verified capability`, `Approved for publication`, or `Hold`. Only approved wording may be placed in final artwork. Do not place inferred features, performance language, prices, offers, trust statements, local-support statements, or customer claims in artwork.

Use `https://burstsms.com.ph/` as the destination unless an approved campaign brief supplies another verified destination.

## 3. Generate only an unbranded base layer

The generation prompt must request photography or illustration only and must explicitly require:

- no logos, wordmarks, brand names, letters, numbers, readable signage, watermarks, badges, buttons, icons, message bubbles, phone UI, URLs, captions, or promotional text;
- no imitation of the Burst SMS palette or identity;
- a clean, uncluttered negative-space region reserved for deterministic brand composition;
- natural Philippine context without stereotypes or forced cultural cues;
- realistic anatomy, devices, environments, lighting, and perspective;
- the requested aspect ratio and safe crop area.

Do not generate an SMS screenshot or legible phone display. Build any approved message representation deterministically during composition.

Keep the generated base layer private. If the tool or host automatically displays its output, the capability gate fails and the tool must not be called.

## 4. Compose the brand layer deterministically

Use a non-generative renderer or locked template to add:

- the actual approved Burst SMS logo and horizontal Philippines lockup;
- Noto Sans typography with approved fallbacks;
- navy `#002A66`, violet `#4C23CC`, cyan `#00AEC4`, Burst blue `#005677`, white `#FFFFFF`, and only the limited supporting colours allowed by `design-system.md`;
- approved headline and CTA copy;
- approved shapes, spacing, clear space, hierarchy, and accessibility treatment;
- any phone UI, message bubble, icon, button, or URL as deterministic vector or text elements rather than generated pixels.

Do not apply generative editing after the brand layer has been added. Do not recolour, distort, crop, redraw, outline, shadow, or blend the logo.

## 5. Inspect the exact final file

Review the final composited file, not the prompt or production intent. All checks must pass:

- Logo: actual supplied artwork, correct variant, proportions, clear space, divider, descriptor, contrast, and legibility.
- Palette: only approved colours in the branded layer; no hot pink, yellow accent strokes, royal-blue campaign styling, or unapproved gradients.
- Type: Noto Sans hierarchy, readable mobile-feed size, no generated or malformed lettering.
- Copy: exact approved wording, British English, one clear CTA, correct destination, and no unsupported claims.
- Composition: correct aspect ratio, safe zones, visual hierarchy, uncluttered layout, and no accidental crops.
- Accessibility: adequate contrast, meaningful alt text, and no information conveyed by colour alone.
- Local fit: relevant Philippine context without stereotypes.
- Integrity: no paper-plane mark, invented `BurstSMS` wordmark, approximate logo, watermark, malformed device UI, or residual generated text.

Any failure blocks delivery. Correct it privately and repeat the full inspection. If correction cannot be completed without exposing the failed file, discard it and return `Hold`.

## 6. Deliver only the passed final

Attach or display only the final file that passed every check. Do not show base layers, drafts, rejected variations, contact sheets, before-and-after comparisons, or failed attempts. Report the asset files used, dimensions, alt text, claim status, and completed checks.
