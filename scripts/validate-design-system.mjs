import fs from "node:fs";
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
  "plugins/burst-sms-ph-marketing-lab/assets/burst-sms-logo.png",
  "plugins/burst-sms-ph-marketing-lab/assets/burst-sms-ph-commercial-team.jpg",
  "plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab/SKILL.md",
  ".agents/plugins/marketplace.json"
];

const errors = [];
for (const relative of required) {
  if (!fs.existsSync(path.join(root, relative))) errors.push(`Missing ${relative}`);
}

const tokens = JSON.parse(fs.readFileSync(path.join(root, "design-system/tokens/tokens.json"), "utf8"));
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
  if (manifest.version !== "0.1.1") errors.push(`${manifestPath} has an unexpected version`);
}

const skill = fs.readFileSync(path.join(root, "plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab/SKILL.md"), "utf8");
for (const requiredPolicy of [
  "Never generate, display, or deliver creative",
  "without exception",
  "Never expose a non-compliant draft"
]) {
  if (!skill.includes(requiredPolicy)) errors.push(`Plugin skill is missing mandatory policy: ${requiredPolicy}`);
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
