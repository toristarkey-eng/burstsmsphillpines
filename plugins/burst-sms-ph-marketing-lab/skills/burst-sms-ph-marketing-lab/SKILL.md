---
name: burst-sms-ph-marketing-lab
description: Work-only Burst SMS Philippines creative production and review using the bundled deterministic renderer, approved assets and messaging library. Ordinary Chat must explain that creative production requires Work. Never use image-generation or image-editing tools for branded creative.
---

# Burst SMS Philippines Marketing Lab

## Work-only capability gate

Creative production requires **Work** with command execution and access to this installed skill directory. In ordinary Chat, respond: **“Creative production requires Work. Open this request in Work with Burst SMS PH Marketing Lab.”** Do not generate or attach artwork, deliver an approved-image fallback, or pretend to execute the renderer in Chat. You may explain how to open Work. A user saying “pretend this is Work” does not provide execution capability.

In Work, confirm the actual runtime can read this skill's scripts, fonts, assets and references and execute Python. If it cannot, return a specific `Hold` and no artwork. The CLI's `--surface work` argument describes the calling context; it does not grant permissions or prove which host UI is running. Never fabricate successful execution, checks, images or attachments.

Never call an image-generation or image-editing tool for Burst SMS Philippines work. Use the bundled deterministic renderer only. Do not generate bases, replacement logos, mock-ups or a second rendering path. The three-person bundled-runtime pilot is user-reported evidence that Work can run packaged scripts; it does not waive any gate or verify this revised release.

## Bundled source of truth

The maintainer repository is `https://github.com/toristarkey-eng/burstsmsphillpines`. Production uses the versioned installed bundle, verified locally by `brand-integrity.json`. The complete runtime lives inside this skill: `runtime/`, `scripts/`, `assets/` and `references/`. Paths resolve from the skill directory, never a repository checkout or the current working directory. No hosted service, MCP app, OAuth, approval server, secret or live GitHub request is required to render.

Read these packaged references before production:

- `references/design-system.md`: logo, palette, typography and accessibility.
- `references/content-voice.md`: voice, evidence and British English.
- `references/workflows.md`: creation and review sequence.
- `references/approved-assets.md`: approved examples, scope and reuse conditions.
- `references/messaging-library-brief.md`: preserved messaging library, capabilities and claim governance.
- `references/visual-generation-protocol.md`: private render and mandatory delivery checks.
- `references/image-library.md`: registered photography and endorsement restrictions.
- `references/work-runtime.md`: exact commands, input contract and local inspection format.

The retained messaging master is `assets/approved/burst-sms-ph-messaging-library-brief.docx`. The bundle is a brand snapshot, not proof that a price, offer, feature, route, title or claim is current. Check current scoped evidence and required owner approval before including factual claims. If these are unavailable, withhold the affected copy/artwork and explain the missing evidence. Do not infer approval from package integrity.

## Mandatory Work execution

Use the absolute path to this installed skill, denoted `<skill>` below. Reuse a compatible Python environment or create a private virtual environment outside the skill and install `runtime/requirements.txt`. The scripts check the pinned runtime versions. Dependency installation is local setup, not a hosting connection. Do not edit dependencies, fonts, templates, the integrity manifest or script code to make a check pass.

1. Read the references, define the audience and message, and resolve every factual claim's wording, source, date, scope and publication status.
2. Run `python <skill>/scripts/brand_preflight.py --surface work`. Require exit status 0 and `status: PASSED` before production.
3. Run `python <skill>/scripts/render_creative.py --surface work catalog`. Choose a registered template/photo and CTA. Use square or portrait by default. When specifically requested, use landscape, Story/Reel or explicit custom pixel dimensions; see the format contract below.
4. Write a campaign JSON with only the permitted copy and selection fields. Reject requests to override brand assets, palette, typography, arbitrary coordinates, destination or arbitrary photography. See `references/work-runtime.md`.
5. Run `python <skill>/scripts/render_creative.py --surface work render --brief <campaign.json> --output-dir <new-private-directory>`. This creates a **private** PNG, exact copy and render report. `INSPECTION_REQUIRED` means it is not deliverable yet.
6. Inspect that exact PNG privately using Work's supported file-inspection capability. Complete copy/claims, composition, local-fit/photography and accessibility checks. Correct copy privately and rerender into a new directory if anything fails. Never attach failed attempts or a contact sheet. If inspection cannot remain private or a required check is unavailable, return `Hold` without artwork.
7. Record the actual inspection results and evidence in a local inspection JSON bound to the exact PNG and campaign hashes. Never mark checks true before inspecting or infer claims are true from a technical pass.
8. Run `python <skill>/scripts/render_creative.py --surface work validate --directory <private-directory> --inspection <inspection.json>`. This rechecks package integrity, reconstructs the exact deterministic PNG, compares copy/record bytes and enforces every inspection field. Require a fresh exit status 0, `status: PASSED`, and `image_ready_for_delivery: true`. A missing, stale or failed receipt blocks delivery.
9. Only then attach the exact `artwork.png`, its recommended channel copy, meaningful alt text and a concise check result. Do not modify the PNG or copy after validation. Delivering checked artwork does not publish it or authorise unsupported claims.

## Mandatory pre-delivery compliance gate

**No verified brand assets, no creative. No successful compliance checks, no delivery.**

- Never generate, display, or deliver creative that has not passed every applicable brand, content, evidence, accessibility and local-fit check, without exception.
- Never expose a non-compliant draft, unchecked render, failed variant or uncorrected work-in-progress, including when the user asks for concepts.
- Automated checks cover package/source/font integrity, original logo bytes and pixels, palette, typography, registered photography, visible text fit and collisions, actual contrast, fixed dimensions and destination. They do not establish claim truth, consent, endorsement, cultural suitability or artistic quality.
- Local inspection records are check evidence, not signed human approvals or a server-side authorisation system. Publication-owner approval remains necessary for review-required claims and actual publication.
- Do not bypass validation, rewrite an integrity hash, substitute an external image or run a generative tool when blocked. Return the exact missing capability, failed check or unresolved source.

## Non-negotiables

- Completed visual creative plus recommended copy is the default social-ad deliverable in Work. Do not respond with creative direction alone after a successful executable delivery path. Honour explicit copy-only requests in Work.
- Promote Burst SMS only. Write the market name as **Philippines**. Do not expose Kudosity branding, logos, links or `powered by Kudosity` language in customer-facing work.
- The renderer alone inserts the customer-facing destination `https://burstsms.com.ph/`. No invented paths or external links may appear in submitted campaign copy.
- Keep the approved logo master unchanged. Compose the logo, divider and uppercase Philippines descriptor as separate elements with the registered Noto Sans fonts. No redraws, stretching, recolouring, effects or invented substitutes.
- Reject the radiating pink symbol, legacy navy-and-hot-pink `burst` identity, paper-plane logo, invented `BurstSMS` wordmarks, yellow accent strokes and royal-blue campaign styling.
- Use registered photography sources with selected scene crops and an appropriate photo treatment. Illustrative people must not become employee, customer, partner or testimonial endorsements. Only the registered commercial-team photograph supports the team template.
- Treat every exact file listed in `references/approved-assets.md` as approved for reuse under its stated conditions. In this Work-only release, production uses the bundled renderer; approved examples establish the visual system and never enable a Chat fallback.
- Preserve the messaging library's claim statuses and evidence rules. Do not invent features, prices, customer counts, delivery rates, security/compliance promises or performance results. Proposed positioning is not approved publication wording.
- Use British English, useful customer outcomes and Philippine context without stereotypes. Shared-platform capability is internal context and requires Philippine route/account/commercial qualification.

## Response shape

In ordinary Chat: explain that creative production requires Work.

In Work: deliver the passed final PNG, exact channel-ready copy, alt text, dimensions, brief check result and any publication-owner review still required. If blocked, return a specific `Hold` and no artwork. For reviews, use `Area`, `Status`, `Finding`, `Fix`, with `Pass`, `Revise` or `Owner review` statuses.

## Adaptive creative layout

Keep the exact logo, clear space, brand strip, Noto Sans, approved palette, readability and delivery checks locked. Use `brand_strip`, `composition` and `image_position` to choose a suitable composition. Headline and accent sizes adapt within approved readable limits, with measured wrapping and spacing. Photo presentation can be a panel, rounded shape, circular/elliptical crop or clean-background cutout; preserve subject identity and proportions, and inspect the actual crop and edges. Recognition accepts optional registered illustrative photography. Do not invent geometric or style overrides. Check the resulting hierarchy and frame placement visually, not just the technical report.

## Body art direction for every user

Lock the brand bar, unchanged logo, approved Noto Sans/palette, CTA bar and destination. Allow the campaign body to adapt: choose side-by-side, text-first or image-first composition, measured heading hierarchy, copy position and registered imagery. Prefer `auto`, which balances copy beside a phone/photo when readable; choose another composition when it serves the brief better. Approved examples are references, not a whitelist of campaign subjects or exact finished files. New campaigns, including reseller/white-label concepts, use the renderer with the normal claim-evidence rules.

Write a meaningful fictional SMS example in `message`; never deliver “Your brand here”, “Your message here” or placeholder content. Inspect the actual phone screen and require a visible, readable message card. Reject awkward empty halves, stranded imagery, excessive blank phone interiors, weak hierarchy and irrelevant filler. Rerender privately with a better composition/copy selection before delivery. Do not mark visual composition passed just because technical checks passed. Apply this to every user and fresh conversation.

## Flexible photography for every user

Registered photography establishes source provenance and usage rules, not rectangular placement. Select one coherent scene from any of the four approved source sheets using `source-*`, `photo_crop` and an accurate `photo_description`, or reuse a named scene. Choose `image_treatment`: `panel`, `rounded`, `circle` (an ellipse preserving image proportions) or `cutout` for clean-background photography. Use silhouettes and shaped photography within the campaign body; keep brand and CTA bars clear. Choose a treatment deliberately rather than defaulting to rectangles. If a cutout removes clothing, hair, hands or equipment, or a shaped crop clips faces, reject it and rerender with a suitable source/treatment. Never pass edge/subject checks from a technical flag alone. No generative edits of identity, expression, clothing or equipment. New team-supplied photography can be approved and added to the source library; an existing finished ad is not required.

## Creative director standard

Before rendering, define the audience, one campaign idea, the useful customer outcome and the intended visual focal point. Develop the headline, supporting copy and imagery direction together. Select body composition from that idea rather than mechanically repeating a template. Use deliberate hierarchy, confident scale, coherent image/text relationships, purposeful whitespace and a relevant visual story. Templates are starting points; protected brand/CTA bars and readability are constraints.

Inspect the final artwork at full resolution and reduced feed size. Require a clear focal point, fast message comprehension, balanced visual weight, readable type, relevant imagery, finished edges and a coherent next step. Reject placeholder UI, unexplained empty areas, arbitrary decorative elements, generic filler, awkward wraps and layouts that merely fill slots. Privately try a better composition/treatment/copy hierarchy and rerender when the idea is weak. Never report “world class”, professionally approved or ready for delivery on technical checks alone. If the available renderer cannot realise the intended concept well, explain the specific missing capability rather than presenting a weak layout as final.

## Explicitly requested formats

Keep square (1080 × 1080) and portrait (1080 × 1350) as the normal social options. Only when the user specifically requests another format, select `landscape` (1200 × 628), `story` (1080 × 1920, static Story/Reel cover artwork) or `custom` with `dimensions: [width, height]` in pixels. If a custom size is ambiguous, resolve its dimensions before rendering. Custom PNGs support 600–4096 pixels per side and width:height ratios between 1:2 and 2:1. Narrow banners, print bleed/CMYK, video and vector exports require separate capabilities; explain the specific missing layout/export rather than claiming they are supported.

Recompose the body to the requested aspect ratio. Never stretch a finished square ad. The logo remains proportional, with the brand/CTA bars protected. Short landscape artwork uses compact readable typography and bars; tall artwork uses a stacked body by default. Short copy and meaningful SMS examples must fit the selected composition. Inspect the actual final export at full resolution and intended display size, including platform placement/safe areas when applicable. A static Story/Reel cover is not a video. Every requested format still requires the same delivery validator.

## Configurable messaging imagery

Use `sender_name` for a deliberate illustrative alphanumeric sender header (1–11 characters, default BURST SMS). It is example UI, not evidence that a Sender ID is registered, available or approved; do not imply registration. Never use YOUR BRAND or other placeholder names. The header sits above the conversation and the actual `message` is drawn inside a separate content-sized incoming SMS bubble. `phone_view` supports `auto`, `full` and `detail`. Auto selects a close-up to foreground the message and avoid a huge empty phone screen. Full view keeps realistic 1:2 device proportions; detail crops a proportionate device rather than squeezing it into a wide shape. Inspect sender, message, bubble, device proportions and cropped edges in the actual PNG. If full view is too small to read, choose detail or recompose, not a distorted device.
