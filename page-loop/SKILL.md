---
name: page-loop
description: "Record a live, interactive piece of a web page (a WebGL or three.js scene, a 3D model, a chart, a board, an animated SVG) as a short seamless looping video for another page: frame-exact rather than screen-recorded, headless on the real GPU, driven through the piece's own buttons and sliders, encoded to an MP4 and a WebM under a size budget with a poster, and embedded so it pauses off screen, respects less motion, and still plays under a CRT or lens effect that draws a picture of the page. Ships a renderer that refuses a software GPU and fails a loop that jumps or stutters at its seam, a worked example, and a self-test. Use when someone wants 'a video of the board', 'a GIF of this', 'an animated preview', 'a hero loop', 'spin the model', 'click through the layers as it turns', 'make it a 5–10 second loop', 'embed the real thing, lightweight', 'show the roadmap on the home page', or '/page-loop'. Not for screen recordings of a person using an app (that is a screencast), and not for a film with a story (that is cinema-delight)."
license: MIT
---

# Page loop: the real piece, as a seconds-long video

Some pieces of a site are too heavy to embed in another page: a 3D board, a WebGL scene, a dashboard with live
controls. A picture of one is flat, and a GIF is huge, banded and blurry. What works is a loop of five to ten seconds,
recorded from the real piece in its own page, under a megabyte, playing silently in a `<video>`.

The pipeline is three parts. A **scene file** says what happens at each moment t from 0 to 1. **`scripts/loop-render.mjs`**
draws each frame headless on the GPU, checks the seam, and encodes the result. Then **the embed** decides when the
video plays. Every rule below comes from a loop that actually shipped (a three.js roadmap board turning once while its
four layers were shown in turn and its date ran forward, seven seconds, 919 KB) and from what went wrong on the way.

## Rules

**L1. Record the real piece, from its own build.** Serve the site's built output locally and point the scene at it. Do
not make a mock, a stylized redraw or a separate demo page. The owner of the board said it plainly: *"no need to be
secretive about the image / video — just use the actual piece."* A redraw drifts from the real thing on the first
change and has to be maintained twice.

**L2. Step time; never record it.** Every state is a function of t alone, and the renderer calls `frame(page, t)` for
t = i / N, waits two animation frames, and takes a screenshot. A screen recording drops frames, records the jitter of
the machine, and cannot be reproduced. A stepped render comes out the same every time, at any frame rate, however
slow each frame is (the board took 440 ms a frame and plays at 30 fps).

**L3. On the real graphics card, checked.** Headless Chromium falls back to SwiftShader, a software renderer, which
washed out the board's glow and blending to a dull grey and ran ten times slower. The renderer launches with
`--enable-gpu --use-gl=angle --use-angle=gl-egl --ignore-gpu-blocklist`. It reads back the WebGL renderer string and
exits 2 if that string names software. `--allow-software` is only for a scene with no WebGL (a 2D canvas, an SVG).

**L4. Drive it with its own controls; reach inside only for what has none.** Click the real layer buttons. Set the real
slider and fire the `input` event a person's drag fires. The video then shows what a visitor will find, labels and
pressed states included. Only something with no control (the camera, say) is set directly. To expose it, rewrite the
served module in the scene's `routes`, for example `R = {` becomes `R = window.__R = {`. Never edit the site's source
to make it recordable.

**L5. The loop has no seam.** A loop that does not close jumps once a lap, and every visitor sees it.
- Use t = i / N, never i / (N − 1), because t = 1 is frame 0 of the next lap.
- Angles go round a whole number of turns.
- A discrete state (which layer is shown, which label) indexes with `t % 1`, or at t = 1 it falls off the end of
  its list.
- A value that runs forward (a date) resets at the seam on purpose, like a clock.

The renderer checks this. It draws one extra frame at t = 1 and requires it to match frame 0 (38 dB PSNR by default).
It also fails a last frame that is frame 0 again, the i / (N − 1) stutter. In the self-test the check caught a
label list indexed with `floor(t × 3)`, in a scene written to pass.

**L6. Fit the chrome to the shot, not the shot to the chrome.** The first board loop clipped to the canvas, and the
toolbar above it, which spans the page, lost its last button mid-word ("Plug everything ba…"). Widening the clip to
the toolbar pulled the neighbouring panel into the frame. The fix is in the page: for the render, set the toolbar to
the canvas's width and let it wrap. Then clip to exactly what is meant to be seen.

**L7. Render at 2×, scale down with Lanczos.** Labels on a 3D board are small. Drawing at `deviceScaleFactor: 2` and
scaling down to the delivery width keeps them legible, where drawing at 1× blurs them.

**L8. A budget, met by the encoder settings rather than by luck.** Five to ten seconds, 960 px wide, under about
1.2 MB (`--budget-kb`).
- H.264: `-crf 28 -tune animation -preset veryslow -movflags +faststart -pix_fmt yuv420p`, no audio track.
- VP9: two passes at a target bitrate (1100 kb/s by default). A CRF VP9 came out larger than the H.264 at the
  same look.
- Poster: WebP, from frame 0.

If the encodes are over budget, shorten the loop, narrow it, or calm the scene: fewer moving pixels, less noise, a
slower turn. A GIF of the same loop is many times the size, in 256 colours.

**L9. Embed it so it costs nothing when nobody is watching.** Use `autoplay muted loop playsinline
preload="metadata"`, a poster, and `width` and `height`, so the space is reserved before the video arrives and nothing
moves (web-ux H2). Put the smaller source first. Give it an `aria-label` that says what moves and a `figcaption` that
says what it is. Under `prefers-reduced-motion`, remove autoplay and show the controls. Pause it whenever it is off
screen.

**L10. Through a picture-of-the-page effect, draw the video live.** A CRT bend or a lens that draws a snapshot of the
page (an SVG `foreignObject`, html2canvas, `drawImage` of the DOM) captures a `<video>` as blank or frozen. Mark the
video (`data-glass`) and have the effect upload it as its own texture every frame (`texImage2D(…, video)`) at its page
rectangle, bent by the same mapping as everything else. Test it with two screenshots one second apart. The video's box
must differ between them and the rest of the page must not (see web-ux, "a picture of the page lands where the page
is").

**L11. Nothing opens on the desktop.** The renderer is headless and needs no display. The self-test is too. Never
check a loop by opening it in a browser or player on someone's live desktop; hand them the file or the page.

## The scene file

```js
export const url = 'http://127.0.0.1:8000/roadmap/';      // the real page, served from its build (L1)
export const viewport = { width: 1400, height: 1100 };     // optional
export const storage = { 'site-look': { theme: 'dark', crt: 'off' } };  // optional: localStorage before the page runs
export const routes = [['**/board.js', (src) => src.replace('R = {', 'R = window.__R = {')]];  // optional (L4)
export async function setup(page) { /* wait for ready, fix the parts of the shot that do not move, fit the chrome (L6) */ }
export async function clip(page) { return { x, y, width, height }; }  // or: export const clip = '#stage'
export async function frame(page, t, i) { /* put the page in its state for t, 0 <= t < 1 (L2, L5) */ }
```

Write the storyboard as functions of t before writing any frame code. For example: *a full turn over the whole loop;
each of four layers shown alone for 0.19 of it from t = 0.06; the date runs from twelve days ago to the close over the
first 0.8, then holds.* `examples/orbit-board.scene.mjs` is that storyboard, complete.

## Run it

```bash
node page-loop/scripts/loop-render.mjs scene.mjs --out public/media --name board --frames 210 --fps 30 --width 960
```

`PLAYWRIGHT=/path/to/playwright/index.mjs` if `playwright` does not resolve from where you run it. It prints the GPU,
the time per frame, the clip, the seam verdict, the three file sizes, and an embed snippet with the right width,
height and source order. It also writes `NAME.json` beside the files: frames, seconds, sizes, seam. Exit 0 means
done, 1 means a check failed (seam or budget), and 2 means it could not run. `--keep-frames` keeps the PNGs for
inspection.

Keep the scene file in the site's own repository, beside its other scripts, so the loop can be remade when the piece
changes.

## Embed it

```html
<figure class="loop">
  <video data-glass autoplay muted loop playsinline preload="metadata" poster="/media/board.webp" width="960" height="652"
         aria-label="The roadmap board turning once while each layer is shown in turn and the date runs forward">
    <source src="/media/board.mp4" type="video/mp4">
    <source src="/media/board.webm" type="video/webm">
  </video>
  <figcaption>One sentence saying what it is.</figcaption>
</figure>
```

```css
.loop video { display: block; width: 100%; height: auto; aspect-ratio: 960 / 652; }
```

```js
document.querySelectorAll('video[data-glass]').forEach((v) => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) { v.removeAttribute('autoplay'); v.pause(); v.controls = true; return; }
  new IntersectionObserver((es) => es.forEach((e) => (e.isIntersecting ? v.play().catch(() => {}) : v.pause()))).observe(v);
});
```

## Before handing it over

1. The renderer exits 0: real GPU, seam closed, under budget.
2. Look at three frames from `--keep-frames`: the first, one mid-loop, and the last. Check that every label and
   button meant to be seen is whole (L6) and nothing from beside the piece is in the shot.
3. Served from where the page will serve it, both files and the poster return 200 with the right content type.
4. On the page, the video holds its space before it loads, and stays paused under reduced motion. If the page has a
   CRT or lens, its frames change through the effect (L10).

`tests/selftest.sh` proves the renderer itself, headless and with no network: a closed loop passes, and both seam
bugs are caught.
