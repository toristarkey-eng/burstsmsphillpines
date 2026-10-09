import assert from "node:assert/strict";
import fs from "node:fs/promises";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";
import { after, before, test } from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
let server;
let baseUrl;
let corruptLogo = false;
let corruptRenderer = false;

function run(args) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, args, { cwd: root });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });
    child.on("close", (code) => resolve({ code, stdout, stderr }));
  });
}

before(async () => {
  server = http.createServer(async (request, response) => {
    try {
      const relative = decodeURIComponent(new URL(request.url, "http://localhost").pathname).replace(/^\/+/, "");
      const target = path.resolve(root, relative);
      if (!target.startsWith(`${root}${path.sep}`)) throw new Error("Invalid path");
      let content = await fs.readFile(target);
      if (corruptLogo && relative === "plugins/burst-sms-ph-marketing-lab/assets/burst-sms-logo.png") {
        content = Buffer.from("not-the-approved-logo");
      }
      if (corruptRenderer && relative === "creative_service/renderer.py") content = Buffer.from("modified-renderer");
      response.writeHead(200);
      response.end(content);
    } catch {
      response.writeHead(404);
      response.end("Not found");
    }
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(async () => {
  await new Promise((resolve) => server.close(resolve));
});

test("live-source preflight verifies logo, tokens, instructions and approved examples", async () => {
  const result = await run(["plugins/burst-sms-ph-marketing-lab/scripts/brand-preflight.mjs", "--repo-base", baseUrl]);
  assert.equal(result.code, 0, result.stderr);
  const receipt = JSON.parse(result.stdout);
  assert.equal(receipt.allowed, true);
  assert.equal(receipt.gate, "PASSED");
  assert.equal(receipt.verifiedLogoSha256, "3b6bb8131d6ce1bf81d7f2481d8b3159058c8e71e87e0d6b5f1582efde3341f2");
  assert.deepEqual(receipt.tokenValues, {
    navy: "#002A66",
    violet: "#4C23CC",
    cyan: "#00AEC4",
    burstBlue: "#005677",
    white: "#FFFFFF"
  });
});

test("acceptance request produces finished artwork, copy and a passed validation receipt", async () => {
  const outputDir = await fs.mkdtemp(path.join(os.tmpdir(), "burst-sms-ph-acceptance-"));
  const result = await run(["plugins/burst-sms-ph-marketing-lab/scripts/prepare-facebook-ad.mjs", "--repo-base", baseUrl, "--output-dir", outputDir]);
  assert.equal(result.code, 0, result.stderr);
  const manifest = JSON.parse(await fs.readFile(path.join(outputDir, "delivery-validation.json"), "utf8"));
  const copy = await fs.readFile(path.join(outputDir, manifest.recommendedCopy), "utf8");
  const artwork = await fs.readFile(path.join(outputDir, manifest.visual));
  assert.equal(manifest.status, "PASSED");
  assert.ok(Object.values(manifest.checks).every(Boolean));
  assert.match(copy, /Burst SMS Philippines/);
  assert.match(copy, /https:\/\/burstsms\.com\.ph\//);
  assert.doesNotMatch(copy, /Kudosity/i);
  assert.ok(artwork.length > 100000);
  const skill = await fs.readFile(path.join(root, "plugins/burst-sms-ph-marketing-lab/skills/burst-sms-ph-marketing-lab/SKILL.md"), "utf8");
  assert.match(skill, /raw\.githubusercontent\.com\/toristarkey-eng\/burstsmsphillpines\/c188b54\/plugins\/burst-sms-ph-marketing-lab\/assets\/approved\/approved-sender-id-great-offer\.png/);
  assert.match(skill, /Do not respond with creative direction/);
});

test("preflight fails closed when the exact approved logo cannot be verified", async () => {
  corruptLogo = true;
  const result = await run(["plugins/burst-sms-ph-marketing-lab/scripts/brand-preflight.mjs", "--repo-base", baseUrl]);
  corruptLogo = false;
  assert.notEqual(result.code, 0);
  const receipt = JSON.parse(result.stderr.slice(result.stderr.indexOf("{"), result.stderr.lastIndexOf("}") + 1));
  assert.equal(receipt.allowed, false);
  assert.equal(receipt.gate, "BLOCKED");
  assert.ok(receipt.failures.some((failure) => failure.includes("SHA-256 mismatch")));
});

test("release preflight verifies renderer sources and rejects remote source tampering", async () => {
  const args = ["plugins/burst-sms-ph-marketing-lab/scripts/brand-preflight.mjs", "--repo-base", baseUrl, "--release-lock", "creative_service/release-lock.json"];
  const good = await run(args);
  assert.equal(good.code, 0, good.stderr);
  assert.ok(JSON.parse(good.stdout).verifiedFiles > 15);
  corruptRenderer = true;
  try {
    const changed = await run(args);
    assert.notEqual(changed.code, 0);
    assert.match(changed.stderr, /creative_service\/renderer.py: SHA-256 mismatch/);
  } finally {
    corruptRenderer = false;
  }
});
