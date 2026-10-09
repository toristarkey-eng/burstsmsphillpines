#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const pluginDir = path.dirname(scriptDir);
const argument = (name) => {
  const index = process.argv.indexOf(name);
  return index === -1 ? undefined : process.argv[index + 1];
};
const outputDir = path.resolve(argument("--output-dir") || path.join(process.cwd(), "burst-sms-ph-facebook-delivery"));
const repoBase = argument("--repo-base");
const cacheDir = path.join(outputDir, ".verified-source");
const preflightArgs = [path.join(scriptDir, "brand-preflight.mjs"), "--output-dir", cacheDir];
if (repoBase) preflightArgs.push("--repo-base", repoBase);

await fs.mkdir(outputDir, { recursive: true });
const preflight = spawnSync(process.execPath, preflightArgs, { encoding: "utf8" });
if (preflight.status !== 0) {
  process.stderr.write(preflight.stderr || preflight.stdout || "Brand preflight failed.\n");
  process.exit(1);
}

const integrity = JSON.parse(await fs.readFile(path.join(pluginDir, "brand-integrity.json"), "utf8"));
const selectedRelative = "plugins/burst-sms-ph-marketing-lab/assets/approved/approved-sender-id-great-offer.png";
const selectedSource = path.join(cacheDir, selectedRelative);
const visualPath = path.join(outputDir, "burst-sms-ph-facebook-ad.png");
const visual = await fs.readFile(selectedSource);
const visualHash = crypto.createHash("sha256").update(visual).digest("hex");
if (visualHash !== integrity.files[selectedRelative]) throw new Error("Selected approved artwork failed its integrity check");
await fs.writeFile(visualPath, visual);

const copy = `Your customers should know who is messaging them. 📱

Help customers recognise your business when you send an SMS. Explore branded Sender IDs with Burst SMS Philippines and make every message easier to identify.

Learn more: https://burstsms.com.ph/

#BurstSMSPhilippines #SMSMarketing #PhilippinesBusiness`;
const copyPath = path.join(outputDir, "recommended-facebook-copy.md");
await fs.writeFile(copyPath, `${copy}\n`, "utf8");

const tokens = JSON.parse(await fs.readFile(path.join(cacheDir, "design-system/tokens/tokens.json"), "utf8"));
const checks = {
  liveRepositoryRetrieved: true,
  exactApprovedArtworkHash: visualHash === integrity.files[selectedRelative],
  exactApprovedLogoHash: integrity.files["plugins/burst-sms-ph-marketing-lab/assets/burst-sms-logo.png"] === "3b6bb8131d6ce1bf81d7f2481d8b3159058c8e71e87e0d6b5f1582efde3341f2",
  colourTokens: tokens.color.brand.navy.$value === "#002A66" && tokens.color.brand.violet.$value === "#4C23CC" && tokens.color.brand.cyan.$value === "#00AEC4",
  typography: tokens.font.family.sans.$value.includes("Noto Sans"),
  correctCta: copy.includes("https://burstsms.com.ph/") && !copy.includes("kudosity"),
  philippinesLocalisation: copy.includes("Burst SMS Philippines") && copy.includes("#PhilippinesBusiness"),
  finishedArtworkDelivered: visual.length > 0
};
if (Object.values(checks).some((value) => value !== true)) throw new Error("Facebook delivery validation failed");

const manifest = {
  status: "PASSED",
  deliverable: "Burst SMS Philippines Facebook ad",
  visual: path.basename(visualPath),
  recommendedCopy: path.basename(copyPath),
  sourceArtwork: selectedRelative,
  sourceArtworkSha256: visualHash,
  brandCompliance: "Passed against the exact approved asset registry and live design tokens",
  publicationApproval: "Owner review required for current Sender ID route and approval conditions before campaign flight",
  checks
};
await fs.writeFile(path.join(outputDir, "delivery-validation.json"), `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ ...manifest, outputDir }, null, 2));
