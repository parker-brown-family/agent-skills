#!/usr/bin/env node
// Records a live piece of a web page (a WebGL scene, a chart, a board, an SVG) as a short, seamless, lightweight loop:
// frame-exact rather than screen-recorded, headless on the real GPU, then encoded to MP4 and WebM with a WebP poster.
// Nothing opens on anyone's desktop.
//
//   node loop-render.mjs SCENE.mjs --out DIR [--frames 210] [--fps 30] [--width 960] [--scale 2] [--name loop]
//                        [--webm-kbps 1100] [--crf 28] [--budget-kb 1200] [--seam-db 38] [--allow-software] [--allow-hold]
//                        [--keep-frames]
//
// SCENE.mjs is a small module (see ../examples/):
//   export const url = 'http://127.0.0.1:8000/page/';     the real page, served from its own build
//   export const viewport = { width: 1400, height: 1000 }; optional
//   export const storage = { key: 'value' };               optional localStorage, set before the page's own scripts
//   export const routes = [['**/scene.js', (src) => src.replace(…)]];  optional: expose internals by rewriting what is
//                                                           served, never by editing the source
//   export async function setup(page) {}                   optional: wait for ready, set the fixed parts of the shot
//   export async function clip(page) { return {x, y, width, height}; }  or: export const clip = '#selector'
//   export async function frame(page, t, i) {}             required: put the page in its state for t, 0 <= t < 1
//
// Every state must be a function of t alone, and at t = 1 the scene must be back where it was at t = 0. The seam
// check enforces it: one extra frame is drawn at t = 1 and must match frame 0 (or the loop jumps on every lap), and the
// last frame must not already be frame 0 (or t ran to 1 inclusive and the first picture is shown twice).
//
// Exit 0 done, 1 a check failed (seam, size budget), 2 could not run (software GPU, missing tool, bad scene).
import { mkdirSync, mkdtempSync, rmSync, statSync, writeFileSync, readdirSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const flag = (k) => args.includes('--' + k);
const sceneArg = args.find((a, i) => !a.startsWith('--') && !(args[i - 1] || '').startsWith('--'));
const die = (code, msg) => { console.error(msg); process.exit(code); };
if (!sceneArg || !opt('out')) die(2, 'usage: loop-render.mjs SCENE.mjs --out DIR [--frames N] [--fps N] [--width N] [--name NAME]');

const N = +opt('frames', 210), FPS = +opt('fps', 30), W = +opt('width', 960), SCALE = +opt('scale', 2);
const NAME = opt('name', 'loop'), OUT = resolve(opt('out')), KBPS = +opt('webm-kbps', 1100), CRF = +opt('crf', 28);
const BUDGET = +opt('budget-kb', 1200) * 1024;
for (const tool of ['ffmpeg']) if (spawnSync(tool, ['-version']).status !== 0) die(2, `${tool} not found`);

const scene = await import(pathToFileURL(resolve(sceneArg)).href);
if (typeof scene.frame !== 'function') die(2, 'the scene must export frame(page, t, i)');
const { chromium } = await import(process.env.PLAYWRIGHT || 'playwright').catch(() => die(2, 'Playwright not found: set PLAYWRIGHT=/path/to/playwright/index.mjs'));

mkdirSync(OUT, { recursive: true });
const FR = mkdtempSync(join(tmpdir(), 'page-loop-'));
// Headless, on the real graphics card. Without these flags headless Chromium renders WebGL in SwiftShader, which
// washes out glow and blending and runs ten times slower.
const b = await chromium.launch({ headless: true, args: ['--enable-gpu', '--use-gl=angle', '--use-angle=gl-egl', '--ignore-gpu-blocklist'] });
let exit = 0;
try {
  const p = await b.newPage({ viewport: scene.viewport || { width: 1400, height: 1000 }, deviceScaleFactor: SCALE, reducedMotion: 'reduce' });
  if (scene.storage) await p.addInitScript((s) => { for (const [k, v] of Object.entries(s)) localStorage.setItem(k, typeof v === 'string' ? v : JSON.stringify(v)); }, scene.storage);
  for (const [pattern, rewrite] of scene.routes || []) {
    await p.route(pattern, async (r) => { const res = await r.fetch(); r.fulfill({ response: res, body: rewrite(await res.text()) }); });
  }
  await p.goto(scene.url, { waitUntil: 'networkidle' });

  const renderer = await p.evaluate(() => {
    const gl = document.createElement('canvas').getContext('webgl2') || document.createElement('canvas').getContext('webgl');
    if (!gl) return 'no WebGL';
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
  });
  console.log('renderer:', renderer);
  if (/swiftshader|llvmpipe|software|no webgl/i.test(renderer) && !flag('allow-software')) {
    die(2, 'software renderer: the frames would come out washed out and slow. Run on a machine with a GPU, or pass --allow-software for a scene with no WebGL.');
  }

  if (scene.setup) await scene.setup(p);
  const box = typeof scene.clip === 'function' ? await scene.clip(p)
    : await p.evaluate((sel) => { const r = document.querySelector(sel)?.getBoundingClientRect(); return r && { x: r.left, y: r.top, width: r.width, height: r.height }; }, scene.clip || 'body');
  if (!box || box.width < 2 || box.height < 2) die(2, 'clip is empty: ' + JSON.stringify(box));
  const clip = { x: Math.floor(box.x), y: Math.floor(box.y), width: Math.ceil(box.width), height: Math.ceil(box.height) };

  const t0 = Date.now();
  for (let i = 0; i < N; i++) {
    await scene.frame(p, i / N, i);  // i / N, never i / (N - 1): t = 1 is frame 0 of the next lap
    await p.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
    await p.screenshot({ path: join(FR, `f${String(i).padStart(4, '0')}.png`), clip });
    if (i === 4) console.log(`per frame ${Math.round((Date.now() - t0) / 5)} ms, ${N} frames`);
  }
  // One frame more, at t = 1: a closed loop is back at frame 0 there. Not encoded; only compared.
  await scene.frame(p, 1, N);
  await p.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  await p.screenshot({ path: join(FR, 'lap.png'), clip });
  console.log('clip', JSON.stringify(clip), `${(N / FPS).toFixed(2)} s at ${FPS} fps`);
} finally { await b.close(); }

const ff = (a) => { const r = spawnSync('ffmpeg', ['-hide_banner', '-y', ...a], { encoding: 'utf8' }); if (r.status !== 0) die(2, 'ffmpeg failed: ' + r.stderr.split('\n').slice(-4).join('\n')); return r.stderr; };
const IN = ['-framerate', String(FPS), '-i', join(FR, 'f%04d.png')];
const SCALE_VF = `scale=${W}:-2:flags=lanczos,format=yuv420p`;
const mp4 = join(OUT, NAME + '.mp4'), webm = join(OUT, NAME + '.webm'), poster = join(OUT, NAME + '.webp');
ff([...IN, '-vf', SCALE_VF, '-c:v', 'libx264', '-preset', 'veryslow', '-crf', String(CRF), '-tune', 'animation', '-movflags', '+faststart', '-an', mp4]);
// VP9 by bitrate in two passes: by CRF it came out larger than the H.264 at the same look.
const log = join(FR, 'vp9');
ff([...IN, '-vf', SCALE_VF, '-c:v', 'libvpx-vp9', '-b:v', KBPS + 'k', '-pass', '1', '-passlogfile', log, '-an', '-f', 'null', '/dev/null']);
ff([...IN, '-vf', SCALE_VF, '-c:v', 'libvpx-vp9', '-b:v', KBPS + 'k', '-pass', '2', '-passlogfile', log, '-row-mt', '1', '-an', webm]);
ff(['-i', join(FR, 'f0000.png'), '-vf', `scale=${W}:-2:flags=lanczos`, '-quality', '82', poster]);

// The seam. At t = 1 the scene must be back at frame 0 (otherwise it jumps on every lap), and the last frame must not
// be frame 0 already (otherwise t ran to 1 inclusive and the first picture is shown twice).
const psnr = (a, b2) => { const m = /average:(inf|[\d.]+)/.exec(ff(['-i', a, '-i', b2, '-lavfi', 'psnr', '-f', 'null', '-'])); return m ? (m[1] === 'inf' ? Infinity : +m[1]) : NaN; };
const f = (i) => join(FR, `f${String(i).padStart(4, '0')}.png`);
const SEAM_DB = +opt('seam-db', 38);
const closes = psnr(join(FR, 'lap.png'), f(0)), last = psnr(f(N - 1), f(0)), step = psnr(f(Math.floor(N / 2)), f(Math.floor(N / 2) + 1));
let seamVerdict = 'ok';
if (closes < SEAM_DB) seamVerdict = 'jump';
else if (!Number.isFinite(last) && Number.isFinite(step) && !flag('allow-hold')) seamVerdict = 'repeat';
const fmt = (x) => (Number.isFinite(x) ? x.toFixed(1) + ' dB' : 'identical');
console.log(`seam: t=1 against frame 0 ${fmt(closes)} (needs ${SEAM_DB}), last frame against frame 0 ${fmt(last)}, a mid-loop step ${fmt(step)} -> ${seamVerdict}`);
if (seamVerdict === 'jump') { console.error('FAIL seam: at t = 1 the scene is not back where it started, so it jumps on every lap. Make every state periodic in t. (--seam-db lower for a scene with deliberate noise.)'); exit = 1; }
if (seamVerdict === 'repeat') { console.error('FAIL seam: the last frame is the first frame again, so the loop stutters. Use t = i / N, not i / (N - 1). (--allow-hold if the scene deliberately holds still.)'); exit = 1; }

const size = (p2) => statSync(p2).size;
const sizes = { mp4: size(mp4), webm: size(webm), poster: size(poster) };
for (const [k, v] of Object.entries(sizes)) console.log(`${k.padEnd(6)} ${(v / 1024).toFixed(0).padStart(6)} KB  ${{ mp4, webm, poster }[k]}`);
if (Math.min(sizes.mp4, sizes.webm) > BUDGET) { console.error(`FAIL size: both encodes are over ${BUDGET / 1024} KB. Shorten the loop, narrow --width, raise --crf, lower --webm-kbps, or calm the scene (less noise, fewer moving pixels).`); exit = 1; }

const probe = spawnSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', mp4], { encoding: 'utf8' }).stdout.trim().split(',').map(Number);
const [vw, vh] = probe.length === 2 && probe.every(Boolean) ? probe : [W, null];
const order = sizes.webm < sizes.mp4 ? ['webm', 'mp4'] : ['mp4', 'webm'];
const web = (x) => '/' + NAME + '.' + x;
const snippet = `<figure class="loop">
  <video autoplay muted loop playsinline preload="metadata" poster="${web('webp')}" width="${vw}" height="${vh}"
         aria-label="WHAT MOVES, in one sentence">
${order.map((x) => `    <source src="${web(x)}" type="video/${x}">`).join('\n')}
  </video>
  <figcaption>WHAT IT IS, in one sentence.</figcaption>
</figure>`;
writeFileSync(join(OUT, NAME + '.json'), JSON.stringify({ frames: N, fps: FPS, seconds: N / FPS, width: vw, height: vh, sizes, seam: { closesDb: Number.isFinite(closes) ? closes : 'identical', verdict: seamVerdict }, made: new Date().toISOString() }, null, 2) + '\n');
console.log('\nembed (smaller source first; the paths are where the files will be served):\n' + snippet);

if (flag('keep-frames')) { const kept = join(OUT, NAME + '-frames'); mkdirSync(kept, { recursive: true }); for (const n of readdirSync(FR)) if (n.endsWith('.png')) spawnSync('cp', [join(FR, n), kept]); console.log('frames kept in', kept); }
rmSync(FR, { recursive: true, force: true });
process.exitCode = exit;
