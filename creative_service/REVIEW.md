# PR #1 implementation and security review

The review identified and corrected the following gaps on the existing branch.

| Finding | Change and evidence |
| --- | --- |
| MCP 1.26.0 had known dependency advisories | Upgraded to 1.28.1; pinned all Python dependencies. The installed dependency set was audited against PyPI vulnerability metadata with no known advisories remaining. This is a point-in-time result, not a guarantee against future findings. |
| Every candidate used the same `mcp-drafter` identity and a typed reviewer name could bypass self-review separation | Preparation now records the authenticated JWT subject. Review uses the server-configured designated reviewer's subject and ignores typed identity fields. HTTP regressions cover subject propagation and self-review rejection. The review password must be issued exclusively to that reviewer; shared passwords/identity aliases are unsupported. |
| An old signed form could approve again after rejection | Review tokens bind the current approval-record revision. Review updates and delivery reads are serialised within the single process. Stale forms fail without changing the current decision. |
| Streaming bodies were read in full and concurrent/cancelled requests could accumulate compositions | Added declared/streamed POST size limits and a single preparation slot that stays occupied until the worker finishes, even if the caller disconnects. Host rate/time limits and storage quotas remain required. |
| Mutable `main` and brand-only remote checks did not verify the deployed renderer release | Production requires a full reviewed `BURST_RELEASE_REF`. Live preflight verifies locked source, fonts, registered photos and approved assets against that exact GitHub commit. Missing lock coverage is rejected. CI/local tests verify source tampering fails. |
| Palette-pair checks could miss text over a cyan decoration or later shapes | Text is painted after shapes/photos. The renderer checks actual background pixels, text collisions, visible glyph bounds and canvas boundaries. The statement decoration was moved outside supporting copy. Tests cover low-contrast and overlapping text. |
| The logo was stretched slightly and the Philippines descriptor used Bold rather than the documented SemiBold | The master logo uses an exact uniform 2× scale, with pixel comparison after composition. Added the unchanged licensed official Noto Sans SemiBold font, its pinned upstream provenance, and its release hash. Original logo bytes are unchanged. |
| Bare domain/IP destinations could bypass the explicit HTTPS-link filter | Copy now rejects bare domains, IP destinations and other URL schemes as well as HTTP links; the renderer alone inserts the registered CTA destination. Regression cases exercise each route. |
| Unknown photo IDs could be silently ignored on text templates | All nonempty photo IDs must resolve to a registered entry; campaign validation is repeated at the renderer boundary. |
| Corrupt approval records could cause generic errors rather than a controlled Hold | Signed-record shape/signature checks and review/technical-check revalidation withhold pixels. Malformed record tests exercise MCP retrieval. |
| Restrictive checkout permissions made copied application files unreadable to the runtime user | Docker normalises read/traverse permissions on application sources while retaining root ownership, and sets private data permissions to 0700. Non-root image smoke tests cover source validation, Node workflow tests and rendering. |
| Tests did not exercise real JWT signatures or the container | Added RSA signature, issuer, audience, expiry, required-claim, scope-shape and algorithm rejection tests, protected-resource metadata and authenticated preparation checks, plus Docker build/runtime verification in CI. |

## Validation

The documented commands execute 4 Node brand/release workflow tests and 24 Python renderer/release/security tests. All templates are exercised in both export formats; the three-user test remains a simulation. Dependency consistency and whitespace checks also pass.

In the cloud machine, Docker's build networking could not resolve destinations, including the configured proxy. An otherwise equivalent image was built using a temporary Dockerfile whose pip-install step consumed the same pinned wheels downloaded through verified HTTPS. It passed the non-root runtime smoke. The committed CI workflow runs the unmodified production Dockerfile with ordinary registry access; check its latest result before merging.

## Merge and release boundaries

These changes are suitable for code merge once the latest CI run passes and normal maintainer review is complete. They do not authorise publication of any creative or establish deployment readiness. The revised lockup and templates still need publication-owner visual/brand review before live use. Automated tests do not prove claims, pricing, consent, cultural fit, image authenticity or endorsement.

Deployment requires an approved HTTPS container host; one workspace, worker and designated reviewer; a durable private `/data` volume owned by UID 10001 with quotas/backups; a read-only application filesystem; ingress rate/body/time limits; outbound GitHub/JWKS access; and host-managed OAuth and review configuration described in `README.md`. No hosting, authentication provider, app registration or workspace permissions have been provisioned by this PR. Hosted OAuth/HTTPS smoke tests, restart persistence, registered-app binding and three fresh conversations with three real users remain release gates.
