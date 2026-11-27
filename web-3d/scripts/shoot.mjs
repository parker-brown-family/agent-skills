// Photograph a web-3d page from every view, on the graphics card, for a hill-climb round (SKILL.md, "Hill-climb it"):
//   node shoot.mjs PAGE_URL OUT_DIR [part-id-to-select]
// Writes OUT_DIR/<view>.png for each view the hook lists, plus selected.png when a part is named, and prints each path.
// Headless, so nothing opens on the desktop. Look at every picture before changing anything.
const pw = process.env.PLAYWRIGHT || `${process.env.HOME}/.local/share/mise/installs/playwright/latest/node_modules/playwright/index.mjs`;
const { chromium } = await import(pw);
import { mkdirSync } from 'node:fs';
const [url, out, sel] = process.argv.slice(2); if (!url || !out) { console.error('usage: node shoot.mjs PAGE_URL OUT_DIR [part-id]'); process.exit(2); }
const HOOK = process.env.HOOK || '__model3d', W = +(process.env.W || 1600), Hh = +(process.env.H || 1000);
mkdirSync(out, { recursive: true });
const b = await chromium.launch({ channel: 'chromium', args: ['--enable-gpu', '--ignore-gpu-blocklist', '--use-gl=angle', '--use-angle=gl-egl'] });
const p = await (await b.newContext({ viewport: { width: W, height: Hh }, deviceScaleFactor: +(process.env.DPR || 1) })).newPage();
p.on('pageerror', e => console.error('page error:', String(e))); p.on('console', m => m.type() === 'error' && console.error('console:', m.text()));
await p.goto(url, { waitUntil: 'networkidle' });
await p.waitForFunction(h => window[h]?.settled, HOOK, { timeout: 20000 });
console.log('renderer:', await p.evaluate(h => window[h].gpu, HOOK));
const stage = p.locator('[data-model3d]');
for (const v of await p.evaluate(h => window[h].views, HOOK)) {
  await p.evaluate(([h, v]) => window[h].fly(v), [HOOK, v]); await p.waitForFunction(h => window[h].settled, HOOK); await p.waitForTimeout(350);
  await stage.screenshot({ path: `${out}/${v}.png` }); console.log(`${out}/${v}.png`);
}
if (sel) {
  await p.evaluate(([h]) => window[h].fly('perspective'), [HOOK]); await p.waitForFunction(h => window[h].settled, HOOK);
  await p.evaluate(([h, id]) => window[h].select(id), [HOOK, sel]); await p.waitForFunction(h => window[h].settled, HOOK); await p.waitForTimeout(350);
  await stage.screenshot({ path: `${out}/selected.png` }); console.log(`${out}/selected.png`);
}
console.log('fps:', (await p.evaluate(h => window[h].fps, HOOK))?.toFixed?.(1) ?? 'not measured yet');
await b.close();
