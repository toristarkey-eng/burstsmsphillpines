import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = process.cwd();
const plugin = path.join(root, 'plugins/burst-sms-ph-marketing-lab');
const skill = path.join(plugin, 'skills/burst-sms-ph-marketing-lab');
const errors = [];
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const json = file => JSON.parse(fs.readFileSync(file, 'utf8'));
try {
  const lock = json(path.join(skill, 'brand-integrity.json'));
  if (lock.plugin_name !== 'burst-sms-ph-marketing-lab' || lock.plugin_version !== '0.4.7' || lock.runtime !== 'Work') errors.push('Wrong Work package identity/version');
  for (const [relative, expected] of Object.entries(lock.files)) {
    const target = path.resolve(skill, relative);
    if (!target.startsWith(skill + path.sep) || !fs.realpathSync(target).startsWith(skill + path.sep)) errors.push(`Unsafe package path: ${relative}`);
    else if (sha(fs.readFileSync(target)) !== expected) errors.push(`Bundled integrity mismatch: ${relative}`);
  }
  const logoHash = '3b6bb8131d6ce1bf81d7f2481d8b3159058c8e71e87e0d6b5f1582efde3341f2';
  if (sha(fs.readFileSync(path.join(skill, 'assets/burst-sms-logo.png'))) !== logoHash) errors.push('Approved logo changed');
  for (const relative of ['plugin.json', '.codex-plugin/plugin.json']) {
    const manifest = json(path.join(plugin, relative));
    if (manifest.name !== lock.plugin_name || manifest.version !== lock.plugin_version) errors.push(`Manifest identity/version mismatch: ${relative}`);
    if (manifest.apps || manifest.mcpServers || manifest.extensions?.['com.openai']?.apps) errors.push(`Hosted binding remains: ${relative}`);
  }
  const marketplace = json(path.join(root, '.agents/plugins/marketplace.json'));
  if (marketplace.name !== 'personal' || marketplace.plugins[0].pluginId !== 'Plugin_f128b9ca740081918b32107ab5b22124') errors.push('Existing marketplace/plugin identity changed');
  for (const file of ['.app.json', '.mcp.json', 'mcp.json']) if (fs.existsSync(path.join(plugin, file))) errors.push(`Hosted configuration remains: ${file}`);
  const tokens = json(path.join(skill, 'assets/tokens.json'));
  if (JSON.stringify(tokens) !== JSON.stringify(json(path.join(root, 'design-system/tokens/tokens.json')))) errors.push('Bundled tokens differ from approved source');
  const css = fs.readFileSync(path.join(root, 'design-system/tokens/tokens.css'), 'utf8').toLowerCase();
  for (const [name, token] of Object.entries(tokens.color.brand)) if (!css.includes(token.$value.toLowerCase())) errors.push(`Missing CSS token: ${name}`);
  const skillText = fs.readFileSync(path.join(skill, 'SKILL.md'), 'utf8');
  for (const policy of ['Creative production requires Work.', 'ordinary Chat', 'No successful compliance checks, no delivery', 'Never call an image-generation or image-editing tool', 'brand_preflight.py', 'image_ready_for_delivery: true', 'Promote Burst SMS only']) if (!skillText.includes(policy)) errors.push(`Missing policy: ${policy}`);
  const approved = path.join(skill, 'assets/approved');
  for (const name of fs.readdirSync(approved).filter(name => name.endsWith('.png'))) {
    if (!fs.readFileSync(path.join(approved, name)).equals(fs.readFileSync(path.join(root, 'design-system/assets/approved', name)))) errors.push(`Approved example changed: ${name}`);
  }
  if (!fs.readFileSync(path.join(approved, 'burst-sms-ph-messaging-library-brief.docx')).equals(fs.readFileSync(path.join(root, 'design-system/briefs/burst-sms-ph-messaging-library-brief.docx')))) errors.push('Messaging master changed');
  const html = fs.readFileSync(path.join(root, 'design-system/index.html'), 'utf8');
  for (const id of ['foundations', 'logo', 'components', 'voice', 'templates', 'governance']) if (!html.includes(`id="${id}"`)) errors.push(`Missing design-system section: ${id}`);
} catch (error) { errors.push(error.message); }
if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
console.log('Burst SMS Philippines design system and Work bundle validation passed.');
