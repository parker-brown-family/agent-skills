// The worked example: a three.js "circuit board" roadmap, recorded as a seven-second loop for a home page. One full
// orbit of the camera; each layer shown alone in turn by clicking its real toggle button; the date slider replayed
// from twelve days ago to the close; the layers spread apart. Labels stay on.
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

const W = 960, H = 540, LAYERS = ['research', 'engineering', 'pipeline', 'support'];
let days;

export async function setup(page) {
  await page.waitForFunction(() => !!window.__R, null, { timeout: 30000 });
  await page.evaluate(([W, H]) => {
    window.__R.stage.style.width = W + 'px'; window.__R.stage.style.height = H + 'px';
    const bar = document.querySelector('.rb-bar'); bar.style.maxWidth = W + 'px'; bar.style.flexWrap = 'wrap';  // fit the chrome to the shot
    document.querySelector('.rb-bar').scrollIntoView({ block: 'start' }); window.scrollBy(0, -12);
    const e = document.querySelector('.rb-explode'); e.value = 1; e.dispatchEvent(new Event('input')); window.__R.explode = 1;
  }, [W, H]);
  await page.waitForTimeout(1500);  // the spread eases in; let it land before frame 0
  days = await page.evaluate(() => ({ today: window.__haloBoard.today, close: window.__haloBoard.CLOSE }));
}

// The shot is the toolbar and the canvas, no wider than the canvas. The toolbar spans the page, so a clip taken from
// the canvas cut its last button off mid-word ("Plug everything ba…"), and a clip widened to the toolbar pulled in the
// panel beside the board. Setup wraps the toolbar to the canvas width instead: fit the chrome to the shot.
export async function clip(page) {
  return page.evaluate(() => {
    const bar = document.querySelector('.rb-bar').getBoundingClientRect(), c = window.__R.canvas.getBoundingClientRect();
    return { x: c.left, y: bar.top - 8, width: c.width, height: c.bottom - bar.top + 8 };
  });
}

// The storyboard, every part a function of t. Discrete states index with (t % 1) so that t = 1 is t = 0 again.
const soloAt = (t) => (t < 0.06 || t >= 0.82 ? null : LAYERS[Math.min(3, Math.floor((t - 0.06) / 0.19))]);
const dayAt = (t) => Math.round(2 * (days.today - 12 + Math.min(1, (t % 1) / 0.8) * (days.close - days.today + 12))) / 2;

export async function frame(page, t) {
  await page.evaluate(([t, solo, day]) => {
    document.querySelectorAll('.rb-layer').forEach((b) => {
      const want = solo == null || b.dataset.l === solo;
      if ((b.getAttribute('aria-pressed') === 'true') !== want) b.click();
    });
    const d = document.querySelector('.rb-day'); if (+d.value !== day) { d.value = day; d.dispatchEvent(new Event('input')); }
    const R = window.__R, a = 2 * Math.PI * t, r = 12.5, tx = 0, ty = -0.3, tz = 0.4, a0 = Math.atan2(10.2, -7.2);
    R.flight = null;
    R.camera.position.set(tx + r * Math.cos(a0 + a), 8.4, tz + r * Math.sin(a0 + a));
    R.controls.target.set(tx, ty, tz); R.camera.lookAt(tx, ty, tz); R.dirty = true;
  }, [t, soloAt(t % 1), dayAt(t)]);
}
