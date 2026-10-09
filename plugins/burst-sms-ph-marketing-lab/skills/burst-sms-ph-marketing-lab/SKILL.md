---
name: burst-sms-ph-marketing-lab
description: Create or review Burst SMS Philippines campaigns, briefs, landing pages, social posts, email, SMS examples, approved-asset selections, and visual directions using the approved Burst SMS Philippines brand system. Use whenever work must be on brand for Burst SMS Philippines.
---

# Burst SMS Philippines Marketing Lab

Use this skill for Burst SMS Philippines marketing creation and brand review.

## Source of truth

Read the relevant reference before writing or reviewing:

- `references/design-system.md` for visual direction, tokens, logo use, and UI patterns.
- `references/content-voice.md` for voice, spelling, evidence, and calls to action.
- `references/workflows.md` for campaign creation and review outputs.
- `references/approved-assets.md` for the exact pre-approved creative library and reuse conditions.
- `references/messaging-library-brief.md` for audiences, capabilities, claims governance, deliverables, and decision precedence.

When the full repository is available, prefer the canonical files under `design-system/`. The plugin references are a portable summary.

## Mandatory pre-delivery compliance gate

- Never generate, display, or deliver creative that has not passed every applicable approved brand and creative system check.
- This requirement applies to every user and every request, without exception.
- Complete the brand, content, evidence, accessibility, and local-fit checks before presenting any creative.
- If creative fails any check, correct it and run the checks again before presenting it.
- Never expose a non-compliant draft, rough concept, rejected option, or uncorrected work-in-progress, including when a user asks to see concepts.
- If required evidence, approval, or source material is unavailable, do not present the affected creative. Explain what is missing and provide only compliant, non-creative guidance that does not bypass the gate.

## Tool-safety rule for visual creative

- Do not call an image-generation or image-editing tool for Burst SMS Philippines creative. Those tools can expose their first output before this skill can inspect it, so they cannot satisfy the pre-delivery gate.
- Do not ask any model to invent, redraw, approximate, typeset, or composite a Burst SMS logo or Philippines lockup.
- A user request to “generate”, “make”, “show”, or “create” an image does not override this rule.
- The only images that may be displayed or delivered directly are exact, byte-unchanged files registered in `references/approved-assets.md`.
- If no registered approved image fits the request, provide compliant copy and a production brief, mark the image deliverable `Hold`, and state that an approved template or human brand-production step is required. Do not create or show a visual concept.
- Never describe an unreviewed generated image as recommended, approved, on-brand, or ready to publish.

## Non-negotiables

- Every social post request includes channel-ready copy and, when relevant, an exact registered approved image. If no approved image fits, withhold the image under the tool-safety rule.
- Write the market name as **Philippines**.
- Promote Burst SMS only in customer-facing work. Do not use Kudosity branding, logos, links, or `powered by Kudosity` language.
- Use `https://burstsms.com.ph/` as the customer-facing call-to-action destination. Do not invent landing-page paths.
- Include the Burst SMS Philippines horizontal lockup on new finished branded creative. Keep the supplied Burst SMS logo artwork unchanged and never ask an image model to recreate it.
- Reject the legacy or invented navy-and-hot-pink `burst` wordmark, radiating pink symbol, and any lockup that reads `SMS PHILIPPINES` beneath an approximated wordmark. These are not the approved Burst SMS Philippines lockup.
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
3. Channel-ready copy or creative direction.
4. Design-system choices used.
5. Claims or decisions that need review.

For reviews, return a concise table with `Area`, `Status`, `Finding`, and `Fix`. Use `Pass`, `Revise`, or `Owner review` as the status.
