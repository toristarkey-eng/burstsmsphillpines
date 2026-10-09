# Work bundled renderer

Run these commands using this installed skill's absolute path. The entire skill folder can be copied out of the repository and executed from an unrelated working directory. Python 3.11+ and the pinned packages in `runtime/requirements.txt` are required; no Node.js, repository checkout, external host, MCP registration or credential is needed.

```sh
python -m venv <private-venv>
<private-venv>/bin/python -m pip install -r <skill>/runtime/requirements.txt
<private-venv>/bin/python <skill>/scripts/brand_preflight.py --surface work
<private-venv>/bin/python <skill>/scripts/render_creative.py --surface work catalog
```

On Windows use the virtual environment's `Scripts/python.exe` path. Never overwrite an existing environment or modify the installed skill. If package installation/execution is unavailable, return `Hold`; do not fabricate a runtime.

## Campaign contract

The only inputs are `template_id`, `format`, `headline`, `accent`, `supporting`, `primary_text`, `cta`, `photo_id` and `message`. Unknown fields, hidden/control characters, markup, URLs/bare domains, competing-brand copy and unsupported superiority claims are rejected. Templates are `recognition`, `customer-updates`, `people-first`, `team-coffee`, `bold-statement`, `offer-focus`. Sizes are square 1080 × 1080 and portrait 1080 × 1350. Text never shrinks automatically to fit. Use the catalog's photo/CTA registrations; do not submit paths or style instructions.

Example structure, using an invitation without a product, price or performance claim:

```json
{
  "template_id": "recognition",
  "format": "portrait",
  "headline": "Start a conversation.",
  "accent": "Talk to our team.",
  "supporting": "Discuss messaging for your business.",
  "primary_text": "Talk to Burst SMS Philippines about messaging for your business.",
  "cta": "Talk to our team",
  "photo_id": null,
  "message": ""
}
```

```sh
<python> <skill>/scripts/render_creative.py --surface work render --brief <campaign.json> --output-dir <new-private-directory>
```

The output is private `artwork.png`, `recommended-copy.md` and `render-report.json`. `INSPECTION_REQUIRED` is not permission to attach it. Do not reuse or overwrite an existing output directory. Keep outputs outside the skill so the package stays intact.

## Final inspection and delivery

Privately inspect the actual PNG, exact copy and alt text. Check the source file/crop, brand lockup, composition, readable text and spacing, accessibility and Philippine suitability. List each factual claim with current source/date/scope and approval status; reject unresolved claims. Record what was actually inspected, not a generic checklist assertion. Copy the current hashes from the render report into this inspection structure:

```json
{
  "png_sha256": "<current PNG hash>",
  "campaign_sha256": "<current campaign hash>",
  "checks": {
    "copy_and_claims": true,
    "visual_composition": true,
    "local_fit_and_photography": true,
    "accessibility": true
  },
  "notes": {
    "copy_and_claims": "<exact wording checked; claim sources, dates, scope and owner approval, or explain why there is no factual claim>",
    "visual_composition": "<actual lockup, safe zones, hierarchy and text spacing inspected>",
    "local_fit_and_photography": "<registered photo/crop, illustrative status and local suitability checked>",
    "accessibility": "<readability, contrast and exact alt text inspected>"
  }
}
```

```sh
<python> <skill>/scripts/render_creative.py --surface work validate --directory <private-directory> --inspection <inspection.json>
```

Require a **fresh successful command** plus `delivery-validation.json` with `status: PASSED` and `image_ready_for_delivery: true`. Validation rerenders from the locked inputs, compares PNG/record/copy and requires every inspection result to be true and explained. Hashes bind inspection to this exact wording/image; they are not reviewer signatures. Copy/PNG/package changes invalidate delivery. Failure withholds artwork even if an older receipt exists. Attach only the exact validated PNG and copy using Work's supported artifact/file-delivery capability. If attachment or private inspection is unavailable, return `Hold`.

Local checks enforce technical constraints, not claim truth or host-wide access control. `--surface work` is a caller declaration, not authenticated proof of Work. The skill's capability gate and workspace's surface availability must be verified in fresh conversations. Brand-check completion is distinct from publication permission; this tool does not publish.

## Maintenance

Maintainers update files in code review, run `python scripts/lock-work-package.py` from the repository and inspect the manifest diff. This helper is deliberately outside the shipped skill. Run all tests after intentional changes. Do not expose a hash-refresh or bypass command to creative users. Keep this existing plugin identity; update its package through the established marketplace release process only when authorised.

The Noto Sans fonts use the bundled `runtime/fonts/OFL.txt`. SemiBold provenance: `https://raw.githubusercontent.com/notofonts/noto-fonts/ffebf8c1ee449e544955a7e813c54f9b73848eac/hinted/ttf/NotoSans/NotoSans-SemiBold.ttf`, SHA-256 `87a8b90ece1e89746b544e4e086f85a3710e41485a8078f9be874837dfad45d5`.
