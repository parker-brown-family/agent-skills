// The worked example: a three.js "circuit board" roadmap, recorded as a seven-second loop for a home page.
//
// The storyboard, every part a function of t:
//   0.00–0.05  wide, every layer on, layers close together, the board alive (LEDs, pulses on the traces)
//   0.06–0.82  each of the four layers alone in turn, by its real button: the camera pans to that layer's parts and
//              pushes in, the layers lift apart; each switch lands while the camera is moving (a cut on action)
//   0.82–1.00  every layer back, the camera pulls out to the wide shot it started from
//   throughout the camera swings ±43° side to side (a full turn showed the board from behind, labels mirrored), and
//              the date slider runs from its first day to the close, then holds
//
//   node ../scripts/loop-render.mjs orbit-board.scene.mjs --out public/now --name roadmap --frames 210
//
// The page's own controls do what they can (the layer buttons, the date and spread sliders, fired with the events a
// person's input fires). Only the camera has no control to drive, so the served module is rewritten to hand its
// renderer object to window, and the camera is placed by hand. Selectors and globals are this board's own; a scene
// for another page keeps the shape and changes those.
export const url = process.env.BOARD_URL || 'http://127.0.0.1:8814/roadmap/';
export const viewport = { width: 1400, height: 1100 };
export const storage = { 'halo-look': { theme: 'deep-quiet', mode: 'dark', crt: 'off', wall: 'off' } };  // no wallpaper, no glass
export const routes = [['**/board3d.js', (src) => src.replace('R = { stage, host,', 'R = window.__R = { stage, host,')]];
export const clock = 'virtual';  // the board's blinking LEDs and travelling pulses run, one frame of time per frame
export const crossfade = 15;     // they do not repeat in seven seconds, so half a second of seam is crossfaded

const W = 960, H = 540, LAYERS = ['research', 'engineering', 'pipeline', 'support'];
let S;  // what setup measured: the date range, the wide shot, and where each layer's parts sit

export async function setup(page) {
  await page.waitForFunction(() => !!window.__R && !!window.__R.W, null, { timeout: 30000 });
  S = await page.evaluate(([W, H, LAYERS]) => {
    const R = window.__R; R.flight = null;
    R.stage.style.width = W + 'px'; R.stage.style.height = H + 'px';
    // Fit the chrome to the shot: keep the row the video drives (layers, date), hide the controls it never touches.
    document.querySelectorAll('.rb-reset, .rb-to3d, .rb-3dctl').forEach((e) => { e.style.display = 'none'; });
    const bar = document.querySelector('.rb-bar'); bar.style.maxWidth = W + 'px'; bar.style.flexWrap = 'wrap';
    bar.scrollIntoView({ block: 'start' }); window.scrollBy(0, -12);
    // Where each layer's parts are: show it alone, average the world positions of what is visible.
    const solo = (l) => document.querySelectorAll('.rb-layer').forEach((b) => { if ((b.getAttribute('aria-pressed') === 'true') !== (l == null || b.dataset.l === l)) b.click(); });
    const where = () => {
      const ps = Object.entries(R.W.parts).filter(([id, g]) => !id.startsWith('sock:') && g.visible).map(([, g]) => { g.updateMatrixWorld(true); const m = g.matrixWorld.elements; return [m[12], m[13], m[14]]; });
      const c = [0, 1, 2].map((k) => ps.reduce((s, p) => s + p[k], 0) / ps.length);
      const spread = Math.max(...ps.map((p) => Math.hypot(p[0] - c[0], p[2] - c[2])));
      return { c, spread };
    };
    const layers = {}; for (const l of LAYERS) { solo(l); layers[l] = where(); }
    solo(null);
    const d = document.querySelector('.rb-day');
    return { layers, day: { min: +d.min, close: window.__haloBoard.CLOSE, step: +d.step || 0.5 } };
  }, [W, H, LAYERS]);
}

// The shot is the toolbar row and the canvas, no wider than the canvas.
export async function clip(page) {
  return page.evaluate(() => {
    const bar = document.querySelector('.rb-bar').getBoundingClientRect(), c = window.__R.canvas.getBoundingClientRect();
    return { x: c.left, y: bar.top - 8, width: c.width, height: c.bottom - bar.top + 8 };
  });
}

// Camera keys: target, distance, height, how far apart the layers are. Between keys, smootherstep; the last key is
// the first, so the loop closes.
const WIDE = { tgt: [0, -0.3, 0.4], r: 15, h: 8.8, e: 0.45 };
const close = (l, k = 1) => {
  // Aim at the layer's own centre, at the height its parts are lifted to when the layers are apart (about 2 units at
  // e = 1; aiming at the board instead left the parts cropped off the top of the frame).
  const L = S.layers[l], r = Math.min(11.5, Math.max(8, L.spread * 1.5 + 5.5)) * k;
  return { tgt: [L.c[0], 1.2, L.c[2]], r, h: r * 0.66, e: 1 };
};
let KEYS;
const keys = () => KEYS || (KEYS = [
  { t: 0, ...WIDE }, { t: 0.05, ...WIDE },
  ...LAYERS.flatMap((l, i) => { const s = 0.06 + 0.19 * i; return [{ t: s + 0.07, ...close(l) }, { t: s + 0.17, ...close(l, 0.9) }]; }),
  { t: 0.93, ...WIDE }, { t: 1, ...WIDE },
]);
const smoother = (x) => x * x * x * (x * (6 * x - 15) + 10);
const mix = (a, b, q) => (Array.isArray(a) ? a.map((v, k) => v + (b[k] - v) * q) : a + (b - a) * q);
function cam(t) {
  const K = keys(); let i = 0; while (i < K.length - 2 && t >= K[i + 1].t) i++;
  const a = K[i], b = K[i + 1], q = smoother(Math.min(1, Math.max(0, (t - a.t) / (b.t - a.t))));
  return { tgt: mix(a.tgt, b.tgt, q), r: mix(a.r, b.r, q), h: mix(a.h, b.h, q), e: mix(a.e, b.e, q) };
}
const soloAt = (t) => (t < 0.06 || t >= 0.82 ? null : LAYERS[Math.min(3, Math.floor((t - 0.06) / 0.19))]);
const dayAt = (t) => {
  const q = smoother(Math.min(1, Math.max(0, (t - 0.03) / 0.83))), { min, close: c, step } = S.day;
  return Math.round((min + (c - min) * q) / step) * step;
};

export async function frame(page, t) {
  const u = t % 1, C = cam(u), az = Math.atan2(10.2, -7.2) + 0.75 * Math.sin(2 * Math.PI * u);
  await page.evaluate(([solo, day, C, az]) => {
    document.querySelectorAll('.rb-layer').forEach((b) => {
      const want = solo == null || b.dataset.l === solo;
      if ((b.getAttribute('aria-pressed') === 'true') !== want) b.click();
    });
    const d = document.querySelector('.rb-day'); if (+d.value !== day) { d.value = day; d.dispatchEvent(new Event('input')); }
    const x = document.querySelector('.rb-explode'); if (Math.abs(+x.value - C.e) > 1e-4) { x.value = C.e; x.dispatchEvent(new Event('input')); }
    const R = window.__R; R.flight = null; R.explode = C.e;
    const [tx, ty, tz] = C.tgt, rh = Math.sqrt(Math.max(0.01, C.r * C.r - C.h * C.h));
    R.camera.position.set(tx + rh * Math.cos(az), ty + C.h, tz + rh * Math.sin(az));
    R.controls.target.set(tx, ty, tz); R.camera.lookAt(tx, ty, tz); R.dirty = true;
  }, [soloAt(u), dayAt(u), C, az]);
}
