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
3. Run `python <skill>/scripts/render_creative.py --surface work catalog`. Choose a registered template/photo, CTA and `square` or `portrait` format.
4. Write a campaign JSON with only the permitted copy and selection fields. Reject requests to override brand assets, palette, typography, dimensions, arbitrary coordinates, destination or arbitrary photography. See `references/work-runtime.md`.
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
- Use only registered photo IDs and crops. Illustrative people must not become employee, customer, partner or testimonial endorsements. Only the registered commercial-team photograph supports the team template.
- Treat every exact file listed in `references/approved-assets.md` as approved for reuse under its stated conditions. In this Work-only release, production uses the bundled renderer; approved examples establish the visual system and never enable a Chat fallback.
- Preserve the messaging library's claim statuses and evidence rules. Do not invent features, prices, customer counts, delivery rates, security/compliance promises or performance results. Proposed positioning is not approved publication wording.
- Use British English, useful customer outcomes and Philippine context without stereotypes. Shared-platform capability is internal context and requires Philippine route/account/commercial qualification.

## Response shape

In ordinary Chat: explain that creative production requires Work.

In Work: deliver the passed final PNG, exact channel-ready copy, alt text, dimensions, brief check result and any publication-owner review still required. If blocked, return a specific `Hold` and no artwork. For reviews, use `Area`, `Status`, `Finding`, `Fix`, with `Pass`, `Revise` or `Owner review` statuses.

## Adaptive creative layout

Keep the exact logo, clear space, brand strip, Noto Sans, approved palette, readability and delivery checks locked. Use `brand_strip`, `composition` and `image_position` to choose a suitable composition. Headline and accent sizes adapt within approved readable limits, with measured wrapping and spacing. Photo frames adapt to the registered image proportions without cutting people or stretching. Recognition accepts optional registered illustrative photography. Do not invent geometric or style overrides. Check the resulting hierarchy and frame placement visually, not just the technical report.
