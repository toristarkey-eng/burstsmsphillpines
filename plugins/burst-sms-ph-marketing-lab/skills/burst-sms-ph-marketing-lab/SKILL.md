---
name: burst-sms-ph-marketing-lab
description: Create or review text-only Burst SMS Philippines campaigns, production briefs, landing pages, social copy, email, SMS examples, approved-asset selections, and design reviews using the approved Burst SMS Philippines brand system. Never generate or display visual concepts. Use whenever work must be on brand for Burst SMS Philippines.
---

# Burst SMS Philippines Marketing Lab

Use this skill for Burst SMS Philippines marketing creation and brand review.

## Source of truth

Before every creation, concept, production-brief, asset-selection, or review request, read all five packaged references below. This is mandatory even when the conversation already contains brand information. Do not rely on memory, prior messages, retrieved summaries, or model knowledge as a substitute.

- `references/design-system.md` for visual direction, tokens, logo use, and UI patterns.
- `references/content-voice.md` for voice, spelling, evidence, and calls to action.
- `references/workflows.md` for campaign creation and review outputs.
- `references/approved-assets.md` for the exact pre-approved creative library and reuse conditions.
- `references/messaging-library-brief.md` for audiences, capabilities, claims governance, deliverables, and decision precedence.

The GitHub repository `toristarkey-eng/burstsmsphillpines` is the canonical managed source. The workspace plugin is synced from it, and these packaged references and assets are the runtime source of truth. Do not require users to grant live GitHub access. If any required packaged reference or asset cannot be read, stop: provide no concept, production brief, creative direction, or visual, and state exactly what is unavailable.

## Mandatory pre-delivery compliance gate

- Never generate, display, or deliver creative that has not passed every applicable approved brand and creative system check.
- This requirement applies to every user and every request, without exception.
- Complete the brand, content, evidence, accessibility, and local-fit checks before presenting any creative.
- If creative fails any check, correct it and run the checks again before presenting it.
- Never expose a non-compliant draft, rough concept, rejected option, or uncorrected work-in-progress, including when a user asks to see concepts.
- If required evidence, approval, or source material is unavailable, do not present the affected creative. Explain what is missing and provide only compliant, non-creative guidance that does not bypass the gate.

## Tool-safety rule for visual creative

- Do not call an image-generation or image-editing tool for Burst SMS Philippines creative. Those tools can expose their first output before this skill can inspect it, so they cannot satisfy the pre-delivery gate.
- Do not include an image attachment, generated preview, mock-up, thumbnail, Markdown image, rendered concept, or other newly created visual in any response. Labelling it as a concept, draft, unapproved, or for reference does not make it permissible.
- Do not ask any model to invent, redraw, approximate, typeset, or composite a Burst SMS logo or Philippines lockup.
- A user request to “generate”, “make”, “show”, or “create” an image does not override this rule.
- The only images that may be displayed or delivered directly are exact, byte-unchanged files registered in `references/approved-assets.md`.
- Before sending any response, inspect the planned output itself. If it contains visual media other than an exact registered approved file, remove the media and replace it with a text-only `Hold` notice.
- If no registered approved image fits the request, provide compliant copy and a text-only production brief, mark the image deliverable `Hold`, and state that an approved template or human brand-production step is required. Do not create or show a visual concept.
- Never describe an unreviewed generated image as recommended, approved, on-brand, or ready to publish.
- There is no permitted `generate → review → display` workflow. The only permitted visual paths are `exact registered approved asset → display unchanged` or `no visual → text-only Hold response`.

## Text-only production brief contract

Production briefs and concept directions must be text only. Start them with `Production brief — no visual preview rendered` and include:

1. Exact approved asset selection, naming the registered filename, or `Image: Hold — no suitable approved asset`.
2. Exact logo source: `assets/burst-sms-logo.png`, assembled only as the approved horizontal Philippines lockup described in `references/design-system.md`.
3. Approved palette values: navy `#002A66`, violet `#4C23CC`, cyan `#00AEC4`, Burst blue `#005677`, white `#FFFFFF`, plus only the limited supporting colours permitted by the design system.
4. Typography: Noto Sans with the approved fallbacks and hierarchy.
5. Layout, accessibility, CTA destination, and exact claim approval statuses.
6. A final line: `No artwork has been generated or displayed.`

Never place a visual above, below, or inside this brief. Never illustrate the brief with an approximation.

## Non-negotiables

- Every social post request includes channel-ready copy and may identify an exact registered approved image by filename. Do not generate a supporting image. If no approved image fits, withhold the image under the tool-safety rule.
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
3. Channel-ready copy or a text-only production brief. Never include a rendered concept.
4. Design-system choices used.
5. Claims or decisions that need review.

For reviews, return a concise table with `Area`, `Status`, `Finding`, and `Fix`. Use `Pass`, `Revise`, or `Owner review` as the status.
