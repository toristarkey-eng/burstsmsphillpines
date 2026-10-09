# Burst SMS PH Marketing Lab plugin

The existing plugin identity and messaging library are preserved. Creative
production runs in Work using the installed skill alone; ordinary Chat explains
that creative production requires Work. Campaign strategy and copy remain
available without producing artwork.

Everything needed by the renderer is under `skills/burst-sms-ph-marketing-lab/`:

- `assets/`: unchanged approved logo, lockup references, photography, seven approved examples, messaging-library DOCX and tokens.
- `runtime/`: deterministic renderer, six templates, pinned dependencies and licensed Noto Sans fonts.
- `scripts/`: local preflight, private rendering and final validation.
- `references/`: approved messaging, brand rules and runtime workflow.
- `brand-integrity.json`: hashes of the complete skill package.

Use Python 3.11+ in a private environment with `runtime/requirements.txt` installed.
No external host, MCP app, OAuth or server-side approval infrastructure is needed.
Initial dependency installation may require an approved package source; rendering
uses local files without a network connection or repository checkout.

Read [runtime instructions](skills/burst-sms-ph-marketing-lab/references/work-runtime.md)
and [fresh-conversation tests](../../tests/FRESH_CONVERSATION_TESTS.md).
Never deliver a candidate until the exact image has been inspected and a fresh
validation returns `PASSED` and `image_ready_for_delivery: true`. Hashes detect
accidental modification; they are not a signature against someone who controls
the entire package. The Work surface gate is an instruction backed by capability
checks, not authentication inferred from a command-line flag.

The plugin does not publish content, make claims current or replace compliance
approval. This PR does not authorize merging, releasing or syncing a team update.
