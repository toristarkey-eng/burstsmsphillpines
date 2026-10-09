---
name: check-burst-work-runtime
description: Check whether a fresh ChatGPT Work conversation can execute bundled Python and load the unchanged Burst logo and Noto font. Use for the Burst Work runtime pilot, not campaign production.
---

Run a diagnostic, not campaign production. Do not generate or display artwork.

1. Locate this installed skill's actual execution directory using the skill provider. Do not guess a filesystem path or treat a `skill://` URI as a filesystem path. Obtain the packaged `scripts/check_runtime.py`, `assets/integrity.json`, `assets/burst-sms-logo.png`, `assets/NotoSans-Regular.ttf` and `assets/OFL.txt` through the provider's supported resource mechanism if they are not already materialised. Preserve directory structure and original bytes. Do not retrieve replacements from GitHub or use files from a previous conversation, local repository, user upload or shared scratch location: this test must exercise the installed plugin's own bundle.
2. If code execution or original bundled files are unavailable, return `BLOCKED` with the missing capability. Do not invent results, rewrite the diagnostic, encode substitute assets or install software to turn a missing prerequisite into a pass.
3. Execute the unchanged bundled script with Python. It produces a JSON receipt and keeps diagnostic image bytes in memory. If Pillow is absent, report that blocker without installing it during this pilot.
4. Return the exact JSON receipt as text and state whether the script and assets were loaded from the installed plugin bundle. Also state whether this is a fresh Work conversation and any permissions prompts observed. Do not include an image.
5. Explain that `PASSED` establishes prerequisites for this conversation only. It does not prove the full renderer runs, validate campaign quality, establish tamper resistance against the model, or prove access for other users. Runtime hash checks protect normal file integrity; an agent with shell write access can edit code and checks, so this approach is not an enforceable security boundary.

Run once in each of three team members' fresh Work conversations. Treat an ordinary Chat test or a repository-backed Codex environment as a separate result. Never claim these are equivalent surfaces.
