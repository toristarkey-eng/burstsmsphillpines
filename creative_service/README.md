# Controlled creative production

This service upgrades the existing Burst SMS PH Marketing Lab. It separates
campaign thinking from production. The model writes copy and chooses a registered
template/photo. It cannot submit logo files, CSS, HTML, colours, typefaces,
positions, sizes, links or arbitrary photography.

## Implemented

- Six templates derived from the approved references: recognition, customer
  updates, people first, team coffee, bold statement and offer focus.
- Fixed 1080 × 1080 and 1080 × 1350 PNG exports.
- Original byte-verified logo, separate horizontal Philippines descriptor,
  bundled licensed Noto Sans fonts, locked palette and CTA destination.
- Registered photo crops only; containment preserves the full selected panel.
  Illustrative photography never becomes an employee/customer endorsement.
- Live GitHub preflight, deployed-source hashes, exact logo pixel comparison,
  text overflow rejection, text contrast checks and export verification.
- Private candidates with signed records. Human review covers claims, copy,
  composition, local context, accessibility and publication authority.
- Only signed, unchanged approved PNGs can leave the MCP retrieval tool.
- Authenticated Streamable HTTP MCP and a separately protected review page.

## Tools

| Tool | Result |
| --- | --- |
| `list_creative_templates` | Allowed templates, photos, CTA choices and export sizes |
| `prepare_creative` | Private candidate ID or Hold; never image pixels |
| `get_reviewed_creative` | Exact approved PNG + copy + receipt, or Hold without image |

There is deliberately no MCP approval, source-editing or validation-bypass tool.
The human review credential must not be provided to the AI, its OAuth client or
its tool configuration. The separate review site is for the publication owner.

## Run tests

```sh
python -m pip install -r creative_service/requirements.txt
npm test
python -m unittest discover -s tests -p 'test_creative_service.py' -v
```

The three-user test is a simulation at the service layer. It does not replace
three separate people testing fresh ChatGPT conversations after deployment.

## Deploy the service

The repository alone does not host this service or register it as a ChatGPT app.
Use your existing approved container host and an HTTPS domain. Build from the
repository root:

```sh
docker build -f creative_service/Dockerfile -t burst-creative .
```

Configure these environment variables in the host's secret/configuration store:

| Variable | Meaning |
| --- | --- |
| `BURST_PUBLIC_ORIGIN` | Actual HTTPS origin, without trailing slash |
| `BURST_OAUTH_ISSUER` | Your OAuth issuer, with an exact issuer match |
| `BURST_OAUTH_AUDIENCE` | Audience issued specifically for this service |
| `BURST_OAUTH_JWKS_URL` | Issuer's HTTPS public key endpoint |
| `BURST_REVIEW_PASSWORD` | At least 24 characters, separate from MCP OAuth credentials |
| `BURST_REVIEW_SIGNING_KEY` | At least 32 random characters, stable across restarts |
| `BURST_PRIVATE_DATA` | Durable private volume, `/data` in the container |
| `PORT` | Optional listening port, default 8000 |

The OAuth application must issue RS256 JWT access tokens with `sub`, `exp`,
`iss`, `aud` and the `creative:use` scope to authorised workspace users only.
Configure the issuer for the ChatGPT OAuth client, including its supported
registration and consent flow. This service verifies tokens and publishes MCP
protected-resource metadata; it is not a replacement OAuth authorization server.
Put TLS and request/body/rate limits at the ingress. Run one service worker with
its durable volume; horizontal scaling needs shared transactional storage first.
Scope this deployment to one workspace. Do not reuse it as a multi-tenant service.
Review password access is an administrative role: record the reviewer's name on
each decision and keep this credential outside the model's tool permissions.

Health: `/health`. MCP: `/mcp`. Human review: `/review/<candidate-id>`.
The review page uses browser Basic authentication with username `brand-reviewer`
and the separately held review password. Approval binds the exact wording,
PNG bytes and renderer release. Changes or missing checks invalidate delivery.

## Connect to the existing web plugin

Do **not** add a placeholder `mcp.json` to the imported workspace plugin.
Bundled raw MCP configuration makes a GitHub-imported plugin desktop-only.
For the existing ChatGPT web plugin:

1. Deploy and smoke-test the real HTTPS `/mcp` endpoint.
2. In ChatGPT Plugins, add the custom MCP server using that endpoint and the
   configured OAuth details. Record the real registered **app ID**.
3. Bind that existing app to this plugin:

   ```sh
   python -m creative_service.wire_registered_app --app-id <verified-app-id>
   ```

   Use the actual `asdk_app_…`, `connector_…` or `templated_apps_…` ID. Do not use
   `Plugin_f128b9ca740081918b32107ab5b22124` here. The helper preserves the plugin's
   identity, marketplace entry, default prompts and existing app dependencies.
4. Review and commit the binding, sync the same marketplace, make the registered
   app available to the intended roles and have users authenticate.
5. Test three fresh conversations with three real users. Each request must use
   the renderer tools, withhold pending candidates and return the same reviewed
   PNG bytes for the same candidate ID. Brand/style overrides must be rejected.

The release is not operational in ChatGPT until hosting, app registration,
binding, permissions and these host tests have completed. Until then the plugin
keeps its existing exact-approved-asset fallback.

Official references:
- https://developers.openai.com/plugins/build/mcp-server
- https://developers.openai.com/plugins/build/plugins
- https://learn.chatgpt.com/docs/enterprise/plugin-management

## Release governance and limits

Maintain the templates and approval rules in code review. After intentional
source/font/template changes, run `python -m creative_service.lock_release`,
review the lock diff and run both test suites before deployment. This command is
for maintainers and is never exposed as a tool. Deploy from a reviewed commit.
Old candidate approvals are invalidated by a new locked renderer release.

Automated checks prove technical constraints, not truth or creative quality.
They cannot establish pricing, route availability, consent, local cultural fit,
image authenticity, endorsement or artistic judgement. An independent human
must approve those aspects. The logo master supplied in the repository is only
145 × 60 pixels; this implementation retains it and scales proportionally. A
higher-resolution approved master would improve large-format output, but must
be registered through the same integrity process before use.
