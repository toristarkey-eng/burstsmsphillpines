import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const plugin = path.join(root, 'plugins/burst-sms-ph-marketing-lab');
const skill = path.join(plugin, 'skills/burst-sms-ph-marketing-lab');

test('both manifests retain existing plugin identity and declare Work production', async () => {
  for (const relative of ['plugin.json', '.codex-plugin/plugin.json']) {
    const manifest = JSON.parse(await fs.readFile(path.join(plugin, relative), 'utf8'));
    assert.equal(manifest.name, 'burst-sms-ph-marketing-lab');
    assert.equal(manifest.version, '0.4.0');
    assert.match(manifest.description, /Work/);
    assert.equal(manifest.apps, undefined);
    assert.equal(manifest.mcpServers, undefined);
  }
  const marketplace = JSON.parse(await fs.readFile(path.join(root, '.agents/plugins/marketplace.json'), 'utf8'));
  assert.equal(marketplace.plugins[0].pluginId, 'Plugin_f128b9ca740081918b32107ab5b22124');
});

test('ordinary Chat requires Work and has no approved-image or image-generation fallback', async () => {
  const instructions = await fs.readFile(path.join(skill, 'SKILL.md'), 'utf8');
  assert.match(instructions, /Creative production requires Work\. Open this request in Work with Burst SMS PH Marketing Lab\./);
  assert.match(instructions, /Do not generate or attach artwork, deliver an approved-image fallback/);
  assert.match(instructions, /Never call an image-generation or image-editing tool/);
  assert.match(instructions, /fresh exit status 0/);
  assert.doesNotMatch(instructions, /c188b54|list_creative_templates|get_reviewed_creative/);
});

test('all packaged references and runtime inputs resolve inside the installed skill', async () => {
  const lock = JSON.parse(await fs.readFile(path.join(skill, 'brand-integrity.json'), 'utf8'));
  for (const reference of ['design-system', 'content-voice', 'workflows', 'approved-assets', 'messaging-library-brief', 'visual-generation-protocol', 'image-library', 'work-runtime']) {
    const text = await fs.readFile(path.join(skill, 'references', reference + '.md'), 'utf8');
    assert.ok(lock.files['references/' + reference + '.md']);
    assert.doesNotMatch(text, /\.\.\/\.\.\/\.\.\/assets|creative_service\/|controlled-creative-service\.md/);
  }
  for (const file of ['runtime/renderer.py', 'runtime/templates.json', 'runtime/fonts/NotoSans-Regular.ttf', 'runtime/fonts/NotoSans-SemiBold.ttf', 'runtime/fonts/NotoSans-Bold.ttf', 'assets/tokens.json', 'assets/burst-sms-logo.png', 'scripts/render_creative.py']) assert.ok(lock.files[file]);
  await assert.rejects(fs.access(path.join(root, 'creative_service')));
});
