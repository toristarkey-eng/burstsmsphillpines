# Visual generation protocol

New Burst SMS Philippines visual creative uses a controlled, fail-closed workflow.

Before production, retrieve the current brand files from `https://github.com/toristarkey-eng/burstsmsphillpines`. Run `plugins/burst-sms-ph-marketing-lab/scripts/brand-preflight.mjs` wherever execution is supported and use only its verified output. If live retrieval, an expected hash, the required plugin version, or a token check fails, stop without generating or displaying artwork.

1. Approve copy and claims before production.
2. Generate only a private, unbranded photographic or illustrative base. The generation prompt must prohibit logos, words, letters, numbers, readable signage, UI, message bubbles, phone content, badges, CTAs, URLs, icons, watermarks, and brand graphic treatments.
3. Use deterministic composition to add the actual supplied Burst SMS logo, the approved horizontal Philippines lockup, Noto Sans typography, approved copy, and approved palette values.
4. Do not use generative editing after brand elements are applied.
5. Inspect the exact final file for logo integrity, colour, type, copy, claims, accessibility, local fit, dimensions, destination, and generated artefacts.
6. Deliver only the passed final. Never show base layers, drafts, failed variants, approximate logos, contact sheets, or rejected concepts.

Generation is allowed only when intermediate output can remain private, actual assets can be composited unchanged, and the final can be inspected before display. If any capability is unavailable or uncertain, return `Hold` instead of generating.

## Deterministic production service

The repository now includes `creative_service/`. This is a non-generative production path: the model supplies copy and registered selections only. The service owns fonts, geometry, palette, logo, crops, CTA and export. Candidates remain private until independent human review; only signed reviewed files are released. See `creative_service/README.md` and the plugin reference `controlled-creative-service.md`. Code being present does not mean the hosted app is connected.
