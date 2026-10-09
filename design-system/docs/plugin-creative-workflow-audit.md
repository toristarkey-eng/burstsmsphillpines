# Burst SMS Philippines plugin creative-workflow audit

## Root cause

The earlier plugin depended on written instructions and conversation context to influence a general-purpose image generator. It did not have an executable live-source preflight, cryptographic asset verification, a private intermediate stage, deterministic logo composition, or an automated delivery test. As a result, a model could skip repository retrieval, approximate the logo and palette, expose an unchecked first render, or avoid the risk by returning copy and a brief without artwork.

GitHub storage was not the underlying problem. The missing enforcement between the repository and creative production was the problem: marketplace synchronisation installed the plugin package, but did not itself guarantee that every creative request retrieved and verified the current repository contents.

## Corrective controls in version 0.1.7

- `brand-integrity.json` locks the canonical repository, plugin version, approved logo, approved examples, messaging brief, colours, typeface and CTA.
- `scripts/brand-preflight.mjs` retrieves the current GitHub files and fails closed on access, version, hash, token or instruction failure.
- `scripts/prepare-facebook-ad.mjs` implements the generic Facebook-ad acceptance path. It delivers an exact registered visual, Philippines copy and a machine-readable validation receipt.
- `references/visual-generation-protocol.md` permits a generated base image only when it remains private and unbranded. The actual logo, type and brand layer must be added deterministically and the exact final must be inspected before display.
- `tests/brand-workflow.test.mjs` verifies successful retrieval, exact logo integrity, palette tokens, Noto Sans, correct CTA, Philippines localisation, Burst-only copy, finished artwork delivery and fail-closed behaviour for a corrupted logo.
- The shared skill makes finished artwork plus recommended copy the default for social-ad requests. It prohibits treating a brief-only response as completion unless a named gate failed.
- A fresh-session v0.1.6 test showed that ChatGPT could retrieve the repository but could not execute the packaged script or attach the packaged binary, so it returned a brief without artwork. Version 0.1.7 adds a commit-pinned raw GitHub delivery URL for the exact hash-locked approved visual. This preserves the approved bytes and makes the default acceptance path work on no-execution ChatGPT surfaces.

## Enforcement boundary

Where code execution is available, the preflight and delivery receipt are technical gates. Where a ChatGPT surface cannot execute packaged scripts, the skill requires equivalent live retrieval and hash checks using an available repository or web tool; if that capability is absent, it must return `Hold` and no artwork. A skill package cannot grant itself network or filesystem permissions, so publication testing must confirm the target workspace surface exposes the required access.

## Release acceptance

The release is eligible for deployment only after:

1. repository validation and automated workflow tests pass;
2. version 0.1.7 is pushed to the canonical repository;
3. live GitHub preflight passes against the pushed revision;
4. the workspace marketplace is resynchronised and reports version 0.1.7 installed for everyone; and
5. a fresh-session request confirms the plugin returns finished artwork plus copy or a specific fail-closed error.
