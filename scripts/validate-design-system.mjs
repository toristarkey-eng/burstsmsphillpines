import fs from "node:fs";
import crypto from "node:crypto";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const required = [
  "design-system/index.html",
  "design-system/styles.css",
  "design-system/app.js",
  "design-system/tokens/tokens.json",
  "design-system/tokens/tokens.css",
  "design-system/assets/brand/burst-sms-logo-primary.png",
  "design-system/assets/photography/burst-sms-ph-commercial-team.jpg",
  "plugins/burst-sms-ph-marketing-lab/plugin.json",
  "plugins/burst-sms-ph-marketing-lab/.codex-plugin/plugin.json",
  "plugins/burst-sms-ph-marketing-lab/brand-integrity.json",
  "plugins/burst-sms-ph-marketing-lab/scripts/brand-preflight.mjs",
  "plugins/burst-sms-ph-marketing-lab/scripts/prepare-facebook-ad.mjs",
  "tests/brand-workflow.test.mjs",
  "plugins/burst-sms-ph-marketing-lab/assets/burst-sms-logo.png",
  "plugins/burst-sms-ph-marketing-lab/assets/burst-sms-ph-commercial-team.jpg",
  "plugins/burst-sms-ph-marketing-lab/assets/burst-sms-ph-lockup-light-reference.png",
  "plugins/burst-sms-ph-marketing-lab/assets/burst-sms-ph-lockup-dark-reference.png",
  "plugins/burst-sms-ph-marketing-lab/assets/approved/approved-coffee-chat-team-with-lockup.png",
  "plugins/burst-sms-ph-marketing-lab/assets/approved/approved-coffee-chat-team.png",
  "plugins/burst-sms-ph-marketing-lab/assets/approved/approved-grace-briones-country-manager.png",
  "plugins/burst-sms-ph-marketing-lab/assets/approved/approved-sender-id-free-offer.png",
  "plugins/burst-sms-ph-marketing-lab/assets/approved/approved-sender-id-great-offer.png",
  "plugins/burst-sms-ph-marketing-lab/assets/approved/approved-be-recognised-facebook.png",
  "plugins/burst-sms-ph-marketing-lab/assets/approved/approved-keep-customers-in-loop.png",
  "plugins/burst-sms-ph-marketing-lab/assets/approved/burst-sms-ph-messaging-library-brief.docx",
  "plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab/SKILL.md",
  "plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab/references/approved-assets.md",
  "plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab/references/messaging-library-brief.md",
  "plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab/references/visual-generation-protocol.md",
  "design-system/docs/approved-assets.md",
  "design-system/docs/visual-generation-protocol.md",
  "design-system/docs/plugin-creative-workflow-audit.md",
  "design-system/briefs/burst-sms-ph-messaging-library-brief.docx",
  ".agents/plugins/marketplace.json"
];

const errors = [];
for (const relative of required) {
  if (!fs.existsSync(path.join(root, relative))) errors.push(`Missing ${relative}`);
}

const tokens = JSON.parse(fs.readFileSync(path.join(root, "design-system/tokens/tokens.json"), "utf8"));
const integrity = JSON.parse(fs.readFileSync(path.join(root, "plugins/burst-sms-ph-marketing-lab/brand-integrity.json"), "utf8"));
const sha256 = (buffer) => crypto.createHash("sha256").update(buffer).digest("hex");
for (const [relative, expectedHash] of Object.entries(integrity.files)) {
  const absolute = path.join(root, relative);
  if (fs.existsSync(absolute) && sha256(fs.readFileSync(absolute)) !== expectedHash) {
    errors.push(`Integrity hash mismatch: ${relative}`);
  }
}
if (integrity.repository !== "https://github.com/toristarkey-eng/burstsmsphillpines") errors.push("Integrity manifest has the wrong repository");
if (integrity.pluginVersion !== "0.1.9") errors.push("Integrity manifest has the wrong plugin version");
const css = fs.readFileSync(path.join(root, "design-system/tokens/tokens.css"), "utf8").toLowerCase();
for (const [name, token] of Object.entries(tokens.color.brand)) {
  if (!css.includes(token.$value.toLowerCase())) errors.push(`Brand colour ${name} is missing from tokens.css`);
}

for (const manifestPath of [
  "plugins/burst-sms-ph-marketing-lab/plugin.json",
  "plugins/burst-sms-ph-marketing-lab/.codex-plugin/plugin.json"
]) {
  const manifest = JSON.parse(fs.readFileSync(path.join(root, manifestPath), "utf8"));
  if (manifest.name !== "burst-sms-ph-marketing-lab") errors.push(`${manifestPath} has the wrong plugin name`);
  if (manifest.version !== "0.1.9") errors.push(`${manifestPath} has an unexpected version`);
}

const skill = fs.readFileSync(path.join(root, "plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab/SKILL.md"), "utf8");
for (const requiredPolicy of [
  "Never generate, display, or deliver creative",
  "Never call an image-generation or image-editing tool on ChatGPT",
  "without exception",
  "Never expose a non-compliant draft",
  "Exact, byte-unchanged files",
  "radiating pink symbol",
  "paper-plane logo",
  "Mandatory GitHub source of truth",
  "https://github.com/toristarkey-eng/burstsmsphillpines",
  "scripts/brand-preflight.mjs",
  "scripts/prepare-facebook-ad.mjs",
  "Completed visual creative plus recommended copy",
  "No verified brand assets, no creative",
  "No successful compliance checks, no delivery",
  "Generated intermediate output can remain non-user-visible",
  "deterministic compositor",
  "references/visual-generation-protocol.md"
]) {
  if (!skill.includes(requiredPolicy)) errors.push(`Plugin skill is missing mandatory policy: ${requiredPolicy}`);
}

for (const requiredPolicy of [
  "Promote Burst SMS only",
  "https://burstsms.com.ph/",
  "Treat every exact file listed in `references/approved-assets.md` as approved"
]) {
  if (!skill.includes(requiredPolicy)) errors.push(`Plugin skill is missing library policy: ${requiredPolicy}`);
}

for (const name of [
  "approved-coffee-chat-team-with-lockup.png",
  "approved-coffee-chat-team.png",
  "approved-grace-briones-country-manager.png",
  "approved-sender-id-free-offer.png",
  "approved-sender-id-great-offer.png"
  ,"approved-be-recognised-facebook.png"
  ,"approved-keep-customers-in-loop.png"
]) {
  const pluginAsset = fs.readFileSync(path.join(root, "plugins/burst-sms-ph-marketing-lab/assets/approved", name));
  const designAsset = fs.readFileSync(path.join(root, "design-system/assets/approved", name));
  if (!pluginAsset.equals(designAsset)) errors.push(`Approved asset copies differ: ${name}`);
}

const html = fs.readFileSync(path.join(root, "design-system/index.html"), "utf8");
for (const id of ["foundations", "logo", "components", "voice", "templates", "governance"]) {
  if (!html.includes(`id="${id}"`)) errors.push(`Preview is missing #${id}`);
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}

console.log("Burst SMS Philippines design system validation passed.");
