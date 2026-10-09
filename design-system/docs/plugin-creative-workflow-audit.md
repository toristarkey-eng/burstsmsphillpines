# Work-only creative workflow review

Version 0.4.0 preserves the plugin identity and approved messaging while moving
all creative runtime inputs into the installed skill. The renderer accepts only
registered templates, two export sizes, approved photography and fixed CTAs.
Logo pixels, palette, fonts, layout bounds, text fit and contrast are checked.

Package preflight checks every shipped file. Candidates remain private and carry
`INSPECTION_REQUIRED`; final delivery requires an inspection bound to the exact
image and campaign hashes and a fresh deterministic revalidation. Invalid or
changed candidates invalidate the prior delivery receipt. Ordinary Chat returns
the Work requirement without importing the renderer or writing artwork.

There is no hosted MCP service, OAuth, app registration, approval database or
server credential in this implementation. Local inspection is a delivery check,
not independent human authorization or publication approval. Package hashes are
integrity checks, not cryptographic publisher signatures. Work gating also needs
fresh-conversation acceptance because a skill cannot authenticate its host UI.

Automated checks cover all templates, formats, registered photo combinations,
CTAs, brand overrides, tampering and execution of a copied skill from an unrelated
directory. See `tests/FRESH_CONVERSATION_TESTS.md` for the remaining surface tests.
The reported three-person pilot is user-provided evidence for bundled execution;
the revised package must still be verified in fresh conversations before release.
No merge, release or team plugin update is authorized by this PR.
