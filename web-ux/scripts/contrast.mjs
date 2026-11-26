#!/usr/bin/env node
// Is every piece of text readable, in every look the site offers? Loads each page in each look, headless, and runs
// axe-core's colour-contrast rule over it: each text node's colour against the background actually behind it,
// see-through layers included, held to WCAG AA (4.5:1, or 3:1 for large text). Tabs and other hidden panels are not
// checked until shown, so pass --open for anything that toggles. Exits 1 on any failure, 2 if it could not run.
//
//   node contrast.mjs URL [URL…] [--looks looks.json] [--root '#main'] [--open 'label.tab'] [--width 1280]
//
// looks.json is an array of looks, each a name and the localStorage that selects it:
//   [{ "name": "dark", "storage": { "theme": "{\"mode\":\"dark\"}" } }, …]
// Without it the page is checked once, as a first visit sees it.
// Needs Playwright (PLAYWRIGHT=…/index.mjs if it does not resolve) and axe-core (AXE=…/axe.min.js, or
// `npm i -D axe-core` in the project). axe-core is MPL-2.0; it is loaded into the page under test, never copied here.
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const urls = args.filter((a, i) => !a.startsWith('--') && !args[i - 1]?.startsWith('--'));
if (!urls.length) { console.error('usage: contrast.mjs URL [URL…] [--looks looks.json] [--root SEL] [--open SEL] [--width N]'); process.exit(2); }
const axePath = process.env.AXE || [join(process.cwd(), 'node_modules/axe-core/axe.min.js')].find(existsSync);
if (!axePath) { console.error('axe-core not found: npm i -D axe-core, or set AXE=/path/to/axe.min.js'); process.exit(2); }
const AXE = readFileSync(axePath, 'utf8');
const looks = opt('looks') ? JSON.parse(readFileSync(opt('looks'), 'utf8')) : [{ name: 'first visit', storage: {} }];
const { chromium } = await import(process.env.PLAYWRIGHT || 'playwright');
const b = await chromium.launch();  // headless: never a window on anyone's desktop
const ctx = await b.newContext({ viewport: { width: +opt('width', 1280), height: 900 }, reducedMotion: 'reduce' });
await ctx.addInitScript(() => { const s = sessionStorage.getItem('__look'); if (s) for (const [k, v] of Object.entries(JSON.parse(s))) localStorage.setItem(k, v); });
const p = await ctx.newPage();
const found = new Map(); let views = 0;
async function audit(look, url) {
  const res = await p.evaluate(async (root) => {
    const r = await window.axe.run(document.querySelector(root) || document, { runOnly: { type: 'rule', values: ['color-contrast'] }, resultTypes: ['violations'] });
    return r.violations.flatMap((v) => v.nodes.map((n) => ({ target: n.target.join(' '), html: n.html.slice(0, 90), d: n.any[0]?.data || {} })));
  }, opt('root', 'body'));
  views++;
  for (const v of res) {
    const key = `${look.name}|${v.target.replace(/:nth-child\(\d+\)/g, '')}|${v.d.fgColor}|${v.d.bgColor}`;
    if (!found.has(key)) found.set(key, { look: look.name, url, ...v });
  }
}
try {
  for (const look of looks) {
    for (const url of urls) {
      await p.goto(url, { waitUntil: 'domcontentloaded' });
      await p.evaluate((s) => sessionStorage.setItem('__look', JSON.stringify(s)), look.storage || {});
      await p.goto(url, { waitUntil: 'networkidle' });
      await p.addScriptTag({ content: AXE });
      const toggles = opt('open') ? await p.$$(opt('open')) : [];
      if (!toggles.length) await audit(look, url);
      for (const t of toggles) { await t.click(); await audit(look, url); }
    }
  }
} catch (e) { console.error('could not run: ' + e.message.split('\n')[0]); await b.close(); process.exit(2); }
await b.close();
const rows = [...found.values()].sort((a, c) => a.d.contrastRatio - c.d.contrastRatio);
for (const r of rows) console.log(`FAIL  ${r.look}  ${r.d.contrastRatio}:1 (needs ${r.d.expectedContrastRatio})  ${r.d.fgColor} on ${r.d.bgColor}  ${r.target}  ${r.url}  ${r.html}`);
console.log(`contrast: ${views} page views in ${looks.length} look${looks.length > 1 ? 's' : ''}, ${rows.length} distinct failure${rows.length === 1 ? '' : 's'}`);
process.exitCode = rows.length ? 1 : 0;
