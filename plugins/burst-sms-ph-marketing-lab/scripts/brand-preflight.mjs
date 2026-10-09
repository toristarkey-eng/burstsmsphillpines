#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const pluginDir = path.dirname(scriptDir);
const integrity = JSON.parse(await fs.readFile(path.join(pluginDir, "brand-integrity.json"), "utf8"));

const argument = (name) => {
  const index = process.argv.indexOf(name);
  return index === -1 ? undefined : process.argv[index + 1];
};

const rawBase = (argument("--repo-base") || process.env.BURST_SMS_PH_REPO_BASE_URL || integrity.rawBase).replace(/\/$/, "");
const outputDir = argument("--output-dir");
const timeoutMs = Number(argument("--timeout-ms") || 20000);
const requiredPaths = [...new Set([...Object.keys(integrity.files), ...integrity.requiredLiveFiles])];

const sha256 = (buffer) => crypto.createHash("sha256").update(buffer).digest("hex");
const fetched = new Map();
const failures = [];

async function retrieve(relativePath) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${rawBase}/${relativePath}`, {
      cache: "no-store",
      headers: { "user-agent": "burst-sms-ph-brand-preflight/0.2.0" },
      signal: controller.signal
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const buffer = Buffer.from(await response.arrayBuffer());
    fetched.set(relativePath, buffer);
  } catch (error) {
    failures.push(`${relativePath}: ${error.message}`);
  } finally {
    clearTimeout(timer);
  }
}

await Promise.all(requiredPaths.map(retrieve));

for (const [relativePath, expectedHash] of Object.entries(integrity.files)) {
  const buffer = fetched.get(relativePath);
  if (buffer && sha256(buffer) !== expectedHash) failures.push(`${relativePath}: SHA-256 mismatch`);
}

function readJson(relativePath) {
  try {
    return JSON.parse(fetched.get(relativePath).toString("utf8"));
  } catch (error) {
    failures.push(`${relativePath}: invalid JSON (${error.message})`);
    return undefined;
  }
}

const manifestPath = "plugins/burst-sms-ph-marketing-lab/plugin.json";
const nestedManifestPath = "plugins/burst-sms-ph-marketing-lab/.codex-plugin/plugin.json";
const tokensPath = "design-system/tokens/tokens.json";
const skillPath = "plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab/SKILL.md";
const manifest = fetched.has(manifestPath) ? readJson(manifestPath) : undefined;
const nestedManifest = fetched.has(nestedManifestPath) ? readJson(nestedManifestPath) : undefined;
const tokens = fetched.has(tokensPath) ? readJson(tokensPath) : undefined;
const skill = fetched.get(skillPath)?.toString("utf8") || "";

for (const [label, value] of [[manifestPath, manifest], [nestedManifestPath, nestedManifest]]) {
  if (value && value.version !== integrity.pluginVersion) failures.push(`${label}: expected version ${integrity.pluginVersion}`);
}

const tokenValues = {
  navy: tokens?.color?.brand?.navy?.$value,
  violet: tokens?.color?.brand?.violet?.$value,
  cyan: tokens?.color?.brand?.cyan?.$value,
  burstBlue: tokens?.color?.brand?.blue?.$value,
  white: tokens?.color?.neutral?.white?.$value
};
for (const [name, expected] of Object.entries(integrity.requiredColours)) {
  if (tokenValues[name]?.toUpperCase() !== expected.toUpperCase()) failures.push(`${tokensPath}: ${name} must be ${expected}`);
}
if (!tokens?.font?.family?.sans?.$value?.includes(integrity.requiredFont)) failures.push(`${tokensPath}: ${integrity.requiredFont} is missing`);

for (const phrase of [
  integrity.repository,
  integrity.requiredDestination,
  "No verified brand assets, no creative",
  "No successful compliance checks, no delivery",
  "scripts/brand-preflight.mjs"
]) {
  if (!skill.includes(phrase)) failures.push(`${skillPath}: missing mandatory instruction '${phrase}'`);
}

if (failures.length) {
  console.error(JSON.stringify({
    allowed: false,
    gate: "BLOCKED",
    repository: integrity.repository,
    message: "No verified brand assets, no creative. No successful compliance checks, no delivery.",
    failures
  }, null, 2));
  process.exit(1);
}

if (outputDir) {
  for (const [relativePath, buffer] of fetched) {
    const target = path.join(outputDir, relativePath);
    await fs.mkdir(path.dirname(target), { recursive: true });
    await fs.writeFile(target, buffer);
  }
}

console.log(JSON.stringify({
  allowed: true,
  gate: "PASSED",
  repository: integrity.repository,
  rawBase,
  pluginVersion: integrity.pluginVersion,
  verifiedLogoSha256: integrity.files["plugins/burst-sms-ph-marketing-lab/assets/burst-sms-logo.png"],
  tokenValues,
  retrievedFiles: fetched.size,
  verifiedFiles: Object.keys(integrity.files).length,
  outputDir: outputDir ? path.resolve(outputDir) : null
}, null, 2));
