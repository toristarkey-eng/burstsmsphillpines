---
name: burst-sms-ph-marketing-lab
description: Create or review Burst SMS Philippines campaigns, production briefs, landing pages, social copy, email, SMS examples, approved-asset selections, design reviews, and capability-gated visual creative using the approved Burst SMS Philippines brand system. Use whenever work must be on brand for Burst SMS Philippines.
---

# Burst SMS Philippines Marketing Lab

Use this skill for Burst SMS Philippines marketing creation and brand review.

## Mandatory GitHub source of truth

The official repository is `https://github.com/toristarkey-eng/burstsmsphillpines`. Before every creative request, retrieve the current brand system, plugin instructions, messaging guidance, and relevant approved examples from that repository. Do not ask the user for the repository URL; it is fixed here. Do not rely on memory, prior messages, retrieved summaries, generic knowledge, or an AI-generated interpretation as a substitute.

Where command execution is available, run `node scripts/brand-preflight.mjs --output-dir <private-working-directory>` from the plugin root before any creative production. Use only the verified files written to that private directory. In a full repository checkout, also run `node scripts/validate-design-system.mjs` from the repository root. Where command execution is unavailable, use an available web or repository tool to retrieve the same current files and verify the locked logo and token values in `brand-integrity.json`. If live repository access or verification is unavailable, stop. Do not generate or display creative.

For the generic request `Create a high-performing Facebook ad for Burst SMS Philippines` or an equivalent request without a narrower product brief, run `node scripts/prepare-facebook-ad.mjs --output-dir <private-delivery-directory>` where execution is supported. Deliver its finished PNG and recommended copy only when `delivery-validation.json` reports `status: PASSED`. This executable acceptance workflow uses an exact registered approved visual and live-verified tokens; it must not be replaced by a copy-only response or a generic generated image. If execution is unavailable, retrieve the same exact approved visual and perform the equivalent checks before delivery.

### No-execution exact-asset delivery path

On ChatGPT surfaces that cannot execute packaged scripts, the generic Facebook-ad acceptance request still requires artwork. After retrieving the live textual guidance and confirming the current `brand-integrity.json` lists the expected SHA-256 for `approved-sender-id-great-offer.png`, display the byte-locked approved artwork from this commit-pinned raw URL:

`https://raw.githubusercontent.com/toristarkey-eng/burstsmsphillpines/c188b54/plugins/burst-sms-ph-marketing-lab/assets/approved/approved-sender-id-great-offer.png`

Use Markdown image syntax with that exact URL and the approved alt text from `references/approved-assets.md`. This commit-pinned file is the same registered asset with SHA-256 `4c04464a7900ab7b63a8e625ca50fb197fdc7b18b2ff9cd736830dc4c88d1859`. Do not replace it with a generated preview. Do not respond with creative direction or say that the exact asset is unverified after the live integrity record and commit-pinned URL have been retrieved successfully. Deliver the image, recommended Facebook copy, the CTA `https://burstsms.com.ph/`, and the publication-owner review note together.

Retrieve and read all six current references below. Packaged copies support discovery and offline review, but they do not replace the mandatory live-repository check for creative generation.

- `references/design-system.md` for visual direction, tokens, logo use, and UI patterns.
- `references/content-voice.md` for voice, spelling, evidence, and calls to action.
- `references/workflows.md` for campaign creation and review outputs.
- `references/approved-assets.md` for the exact pre-approved creative library and reuse conditions.
- `references/messaging-library-brief.md` for audiences, capabilities, claims governance, deliverables, and decision precedence.
- `references/visual-generation-protocol.md` for the only permitted method of creating new visual artwork.

Retrieve the current approved logo from `plugins/burst-sms-ph-marketing-lab/assets/burst-sms-logo.png`, the current tokens from `design-system/tokens/tokens.json`, approved examples from `plugins/burst-sms-ph-marketing-lab/assets/approved/`, and the approved messaging brief. Verify them with `brand-integrity.json`. If any required live or packaged reference cannot be read and verified, stop: provide no concept, production brief, creative direction, or visual, and state exactly what is unavailable.

## Mandatory pre-delivery compliance gate

**No verified brand assets, no creative. No successful compliance checks, no delivery.**

- Never generate, display, or deliver creative that has not passed every applicable approved brand and creative system check.
- This requirement applies to every user and every request, without exception.
- Complete the brand, content, evidence, accessibility, and local-fit checks before presenting any creative.
- If creative fails any check, correct it and run the checks again before presenting it.
- Never expose a non-compliant draft, rough concept, rejected option, or uncorrected work-in-progress, including when a user asks to see concepts.
- If required evidence, approval, or source material is unavailable, do not present the affected creative. Explain what is missing and provide only compliant, non-creative guidance that does not bypass the gate.

## Capability gate for visual creative

New visual generation is permitted only through `references/visual-generation-protocol.md` and only when every gate below is true before any generation begins:

1. All six packaged references and the exact approved logo assets are readable.
2. Generated intermediate output can remain non-user-visible until review is complete.
3. A deterministic compositor can place the actual supplied logo, Philippines descriptor, approved type, copy, and shapes without asking an image model to reproduce them.
4. The final composited file can be visually inspected before it is attached or displayed.
5. Failed files can be discarded or corrected without exposing them to the user.

If any gate is false or uncertain, do not call a visual-generation tool. Return a text-only production brief with `Image: Hold — controlled production capability unavailable`.

- An image model may generate only an unbranded photographic or illustrative base layer. It must not generate logos, lockups, text, letters, numbers, message bubbles, phone UI, offer badges, buttons, URLs, icons, or brand-coloured graphic treatments.
- Never ask any model to invent, redraw, approximate, typeset, or composite a Burst SMS logo or Philippines lockup.
- After the base layer is generated privately, use deterministic composition to add the actual approved brand assets and typography. Do not use generative editing after brand elements are applied.
- Inspect the exact final file against every check before showing it. A disclaimer such as concept, draft, unapproved, or for reference never permits a failed file to be displayed.
- Exact, byte-unchanged files registered in `references/approved-assets.md` may be displayed directly under their documented reuse conditions.

## Brand-bound production brief contract

Create this specification before producing new artwork. If the capability gate fails, return it as text only. Start it with `Burst SMS Philippines production brief` and include:

1. Exact approved asset selection, naming the registered filename, or `Image: Hold — no suitable approved asset`.
2. Exact logo source: `assets/burst-sms-logo.png`, assembled only as the approved horizontal Philippines lockup described in `references/design-system.md`.
3. Approved palette values: navy `#002A66`, violet `#4C23CC`, cyan `#00AEC4`, Burst blue `#005677`, white `#FFFFFF`, plus only the limited supporting colours permitted by the design system.
4. Typography: Noto Sans with the approved fallbacks and hierarchy.
5. Layout, accessibility, CTA destination, and exact claim approval statuses.
6. Generation-layer instructions that prohibit all logos, text, UI, signage, badges, brand graphics, and legible phone content.
7. Composition-layer instructions that name the exact real asset files and approved tokens.
8. Pre-delivery inspection results for logo integrity, palette, typography, copy, claims, accessibility, local fit, dimensions, and destination.

Never illustrate a brief with an approximation. A visual may accompany it only after the controlled protocol passes in full.

## Non-negotiables

- Every social post request includes channel-ready copy and a supporting image when either an exact registered asset fits or the controlled visual-generation protocol passes. Otherwise withhold the image and return `Hold`.
- Completed visual creative plus recommended copy is the default deliverable for every social-ad request. A creative brief alone is not completion unless the workflow is blocked and clearly reports the specific failed gate.
- Write the market name as **Philippines**.
- Promote Burst SMS only in customer-facing work. Do not use Kudosity branding, logos, links, or `powered by Kudosity` language.
- Use `https://burstsms.com.ph/` as the customer-facing call-to-action destination. Do not invent landing-page paths.
- Include the Burst SMS Philippines horizontal lockup on new finished branded creative. Keep the supplied Burst SMS logo artwork unchanged and never ask an image model to recreate it.
- Reject the legacy or invented navy-and-hot-pink `burst` wordmark, radiating pink symbol, and any lockup that reads `SMS PHILIPPINES` beneath an approximated wordmark. These are not the approved Burst SMS Philippines lockup.
- Reject any paper-plane logo, a one-word blue `BurstSMS` approximation, a small widely spaced `PHILIPPINES` line placed directly beneath it, yellow accent strokes, or royal-blue campaign styling. None is an approved substitute for the supplied logo and horizontal market lockup.
- Treat every exact file listed in `references/approved-assets.md` as approved for reuse as supplied. Do not reject or redesign those exact assets because they predate a newer layout rule. Any modification or derivative becomes new creative and must pass the complete compliance gate.
- Use British English unless a channel or product field requires another convention.
- Lead with a useful customer outcome and explain it in plain language.
- Do not invent product features, customer counts, delivery rates, prices, compliance claims, or performance results.
- Treat product, pricing, security, compliance, and performance statements as review-required.
- Localise examples for Philippine organisations and audiences without stereotypes or forced slang.
- Treat the shared Kudosity platform as internal product context only. Qualify every capability for Philippine route, carrier, account, commercial, and release availability before publication.

## Default response shape

For new work, return:

1. Audience and job to be done.
2. Core message and evidence needed.
3. Channel-ready copy and either a passed final visual, an exact approved asset, or a production brief with `Hold`.
4. Design-system choices used.
5. Claims or decisions that need review.

For reviews, return a concise table with `Area`, `Status`, `Finding`, and `Fix`. Use `Pass`, `Revise`, or `Owner review` as the status.
