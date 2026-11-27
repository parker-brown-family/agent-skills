---
name: web-3d
description: "Turn structured data (a roadmap, an architecture, a dependency graph, a plan with layers) into a 3D model on a web page that the reader turns, lays flat, lifts apart into layers, and clicks into, drawn on the graphics card with WebGL2 and three.js bundled into the site. Every part is placed by a rule from the data, never by hand; work not yet run looks different from work that has, and unknown looks different from both; a click lands on the part drawn under the pointer; a flat view stands in where there is no graphics card. Ships a starter scene, a bundling script, a contract test that runs headless on the real GPU and catches the picking, chain and motion bugs it was written against, and a screenshot script for hill-climbing the look. Use when someone wants a page that is '3D', 'something I can move around', 'lay it flat', 'see the layers', 'explode it', 'orbit', 'a motherboard / circuit board / exploded diagram of X', 'make it mind-blowing', 'use the graphics card', 'WebGL', 'three.js', 'WebGPU', or asks whether 'WebAssembly' / 'web C' would make a visual faster, or '/web-3d'. For how the page around it behaves (keys, focus, nothing moving under the reader), use web-ux; for its colours and type, design-language; to record it as a looping video for another page, page-loop."
license: MIT
---

# Web 3D: a data model the reader can turn

This skill builds a page where data becomes an object: layers stacked like the boards of a machine, parts standing on
them, links arching between them. The reader drags to turn it, flies between a top, side and exploded view, lifts the
layers apart with a slider, and clicks a part to see what it needs and what needs it. It came out of a roadmap drawn as
a motherboard that plugs into a competition. That board went from a flat SVG to a 3D model in one session and five rounds of
screenshots, and every rule below is something that went wrong in those rounds.

Start from `template/scene.js`; do not start from a blank file. It already keeps every rule here, and the contract test
proves it.

## 1. Pick the engine by what the work is

| The work | Engine | Why |
|---|---|---|
| Fewer than about 100 marks, read flat, printed or searched | SVG | Text stays text; but nothing may animate inside a filtered group, or the blur is redrawn every frame (measured 25 frames a second, 58 once the moving parts left the filtered sheets) |
| Depth, turning, layers lifted apart, glow, hundreds of lit parts | **WebGL2 through three.js** | Drawing is the graphics card's job; this ran at 60 frames a second on an RTX 3080 |
| Heavy arithmetic per frame: physics, layout of 100,000 nodes, parsing | WebAssembly, feeding WebGL | WebAssembly ("web C") makes *processor* work fast. It does not draw anything faster |
| Compute shaders, or millions of instances | WebGPU | Worth its newer API only past what WebGL2 does; a scene this size gains nothing |

Answer the WebAssembly question in one line when it is asked, because it is asked: it speeds up the processor, and drawing belongs on the graphics card.

## 2. Map, never place

**M1. Every part comes from a rule over the data.** An ordered table maps each record to a kind of part (the first rule
that matches wins), and zones plus an ordering (date, rank) give it a place. Nothing is positioned by hand, so the
picture changes when the data does, and a reviewer can argue with a rule instead of a pixel. Keep two lists the test
reads, `unmapped` and `unplaced`, and fail when either is non-empty. *Specimen:* dropped items had a rule but no zone
and silently vanished from the board, until the unplaced check named them.

**M2. Known, not run and unknown are three different looks.** `known: true` (it ran) is a solid slab with a lit LED.
`false` (planned, not run) is a hologram: additive, see-through, outlined, with NOT RUN on its face. `null` (nobody
knows) is grey and dashed, with UNKNOWN on its face. A missing value is never drawn as a value: an empty axis is
hatched, not zero. The contract test fails any part whose `known` is not one of the three.

**M2a. On a map, an unknown number is a little map pin with a "?" in it.** When a place's value was never gathered
or never published, stand a small pin on the place (a teardrop extruded and bevelled, point on the place, a light eye
carrying a dark "?", about one hex tall, turned to face the camera), in slate grey, with a "not published" banner on the
largest ones. Keep the eye out of the bloom (bloom runs on linear light before tone mapping), or the "?" blurs away.
Never a hollow or wireframe bar: a height reads as a number that does not exist. Never flat on the ground: it sinks into
the terrain. Never a big floating "?": it shouts over the real numbers. This holds on every map of ours, 2D included (the
2D banner shows "?"). *Specimen:* Canada in relief tried all three failed looks in a day; Parker: *"hollow bars are bad
and misleading"*, then the flat ring *"cannot sit flat on the surface"*, then the big "?" was *"too big and should be
captured in a little pin kind of thing"*, for *"all of our maps."* The working version is `pinGeometry()` in
`canada-homeless-map/web/3d/scene.js`.

**M3. A link says whether it is required.** `needs` is a solid line, and pulling its source darkens the target and
everything that needs that, all the way down. `helps` is a dashed line, and pulling its source only weakens the
target. The test works the darkened set out from the data itself and compares it with the set the scene actually lit, for every part.

**M4. No two parts on one layer overlap**, and nothing required loops. Both are data checks in the test.

## 3. One model, several views, and a stand-in for every machine

The 3D scene is a *view* of a model the page already owns. The page's flat drawing (SVG, or a list) reads the same
model and stays the fallback, the print view and what search indexes.

| Machine or reader | Gets |
|---|---|
| WebGL2 on a real graphics card | the 3D model |
| Software WebGL (SwiftShader, llvmpipe): 3 to 5 frames a second | the flat view, with **Open in 3D** one click away (`?gl` forces it) |
| No WebGL2 | the flat view, and no 3D button |
| A phone | whatever reads on a narrow screen (the roadmap used a transit-style line map) |
| Reduced motion | the 3D model, arriving still; views jump instead of flying; nothing breathes or crawls |
| Light theme | the stage keeps a dark room, because glow on a pale page reads as mud |

`gpuKind()` in the template reads the renderer string and says which. It releases its probe context, because a page gets about sixteen.

## 4. Build the scene from the template

```bash
scripts/vendor-three.sh static/three/three-bundle.js         # three.js 0.187 + addons, minified ESM, MIT licence beside it
cp template/scene.js src/                                    # point its import at the bundle
```

`mountModel(stage, model, opts)` takes `{ layers, parts, links }` (documented at the top of the file) and returns a
controller, or `null` for the flat view. The settings it ships, each the end of a hill-climb round:

| Setting | Value | What went wrong without it |
|---|---|---|
| Tone mapping | ACES, exposure .82 to .85 | linear output clipped every glow to white |
| `scene.environmentIntensity` | about .35 | full-strength room reflections bleached every surface to a pale haze |
| Bloom (UnrealBloomPass) | strength .55, radius .42, threshold .84 | lower thresholds bloomed the plates and the labels; only LEDs and emissives should |
| Solid parts | dark slab (`bg` 80%, owner's hue 20%), light text, a hue outline | pale slabs made white names unreadable |
| Holograms | additive, opacity about .08, edges at .9, name in the hue lightened 45% | names on holograms vanished at .07 with the raw hue |
| Labels | canvas textures, 80 px per model unit, `anisotropy` 8 | lower densities smeared when tilted |
| Layer captions | sprites on the front edge, shown once layers are apart | captions on the back edge or the left fell off-frame or under parts |
| Fat lines | `Line2` with `resolution` updated on every resize | lines drew at the wrong width after the first resize |
| Colours | read from the page's CSS variables through a 2D canvas | `oklch()` and `color-mix()` are not parsed by `THREE.Color` |
| Pixel ratio | `min(devicePixelRatio, 2)` | 3× screens tripled fill cost for no visible gain |

**Views are data:** `{ pos, tgt, e }`, the camera, where it looks, and how far apart the layers are. Default four:
perspective, top (everything flat together), side (the stack edge-on, captions showing), exploded. Keys 1 to 4 on the
focused canvas, buttons with `aria-pressed`, and a range input for the gap. A selected part on a buried layer lifts the
layers clear before the camera arrives; Esc flies back to the view the reader left.

**Arrival:** the model settles out of the sky with its layers closing, once per page load, 2.6 seconds, never under
reduced motion. After that, nothing moves the camera but the reader.

## 5. A click lands on the part drawn under the pointer

**P1. Only part bodies are targets.** Every glow plane, light sprite, outline, caption, label and beacon gets
`raycast = () => {}` and `userData.noPick`. The hit is resolved by walking up from the struck mesh to the group that
carries the id, which is what any part built from several meshes needs. That walk is also why a forgotten glow steals a
neighbour's click. *Specimen:* clicks on the roadmap opened the part next door. Glow pools twice a part's size sat in front of their neighbours.

**P2. Set the line pick reach.** `raycaster.params.Line.threshold` defaults to one whole world unit, so any outline
within a unit of the pointer wins. Set it to .005 and mark outlines noPick as well.

**P3. A drag is not a click.** Pick on `pointerup` only when the pointer moved 5 px or less since `pointerdown`.

**P4. The test aims where the part is drawn, and just beside it.** `project(id)` gives the middle of a part's top face in
page pixels, and `projectPoint(x, z, layer)` any spot on a layer. The test solos one layer at a time, from the top view.
At each part's middle the ray must find that part. Just outside each of its four edges, the ray must find whatever the
data puts there, which is usually nothing.

## 6. Motion and speed

- One `requestAnimationFrame` loop, which stops and disposes everything when the canvas leaves the page.
- **Queue the next frame before any work, and catch a frame's error** (report it once). A throw before
  `requestAnimationFrame` stops drawing for good: Canada in relief froze until a refresh (*"it tends to lock the
  screen requiring page refresh"*).
- Draw only when something changed (`dirty`), except the few things that move on their own: LEDs breathe, `helps` lines
  crawl. Under reduced motion those stop, so an idle scene draws no frames at all. The test counts them.
- Measure frames *drawn* a second, best of three two-second windows. A machine shared with a desktop and a score of
  agents drops a window now and then. The floor on a real graphics card is 45.
- Headless Chromium reaches the graphics card with `--enable-gpu --ignore-gpu-blocklist --use-gl=angle
  --use-angle=gl-egl` and `channel: 'chromium'`. Without them it falls to SwiftShader, which reports 3 to 5 frames a second.

## 7. The contract a page keeps

The test and the screenshot script drive any page that keeps this, not just the template:

- The stage element carries `data-model3d`, and `data-mode` (`3d` or `flat`), `data-ready="1"` and `data-sel` (the
  selected id, or empty).
- Toolbar: `[data-view="<name>"]` buttons, a `[data-explode]` range, `[data-toflat]`, `[data-to3d]`.
- `window.__model3d` (or `HOOK=`): `data`, `views`, `view`, `settled`, `explode` (get and set), `selected`, `camera`,
  `fps`, `frames`, `gpu`, `layerY(k)`, `fly(v)`, `select(id)`, `hitAt(x, y)`, `hitsAt(x, y)`, `chain(id)`, `lit()`,
  `solo(k)`, `project(id)`, `projectPoint(x, z, k)`. Every number is read off the scene, never off a copy of the answer.

## 8. Test it

```bash
python3 -m http.server 8837 --bind 127.0.0.1        # or the project's own preview
node scripts/model-e2e.mjs http://127.0.0.1:8837/page.html          # software: flat first, then 3D on request
GPU=1 node scripts/model-e2e.mjs http://127.0.0.1:8837/page.html    # the graphics card, held to 45 frames a second
```

The test checks 23 things:
- **The data:** links resolve, `known` is declared on every part, nothing required loops, and no parts overlap.
- **The views:** top lays the layers together, exploded stacks them in order, the pressed button says so, and the slider sets the gap.
- **Turning:** a drag moves the camera, and key 2 flies to the second view.
- **Picking:** a ray at every part, and beside it.
- **Selection:** a real click selects a part, and every part's chain matches the data, both computed and lit. Esc clears it.
- **Fallbacks:** flat and 3D switch both ways, and the flat view stands in when WebGL2 is missing.
- **Motion and speed:** reduced motion arrives still and draws nothing while idle, and the graphics card holds its frame rate.

It runs headless every time, so no window opens on anyone's desktop.

**It was mutation-checked, and the first version failed.** Four bugs were put back on purpose:
- a pickable glow
- outlines with the default line reach
- a chain that only walked upstream
- reduced motion that still animated

At first the test caught one of the four. The glow hid under its own part when seen from above, and the single part it checked had nothing above it. Probing just beside every part, and checking every part's chain, catches all four. When you change the test, plant a bug again and watch the test fail.

## 9. Hill-climb the look

A 3D scene that passes every test can still be ugly, and only a picture shows it. Each round:

1. `node scripts/shoot.mjs URL OUT_DIR <part-id>` photographs every view and a selection, on the graphics card, and prints page errors.
2. Look at every picture. Write down the worst thing in a sentence ("names unreadable on pale slabs").
3. Change one thing, rerun the contract test, and shoot again. Keep a table of round, problem and fix: it goes in the
   brief, and it is how the next person learns the settings in section 4.

These have come up, in roughly this order, on both scenes this skill has built:
1. A yellow or white haze over everything, from exposure, bloom and reflections.
2. Unreadable names, from pale slabs.
3. Clicks landing next door, from glows and line reach.
4. The model starting below the fold, which needs the stage capped at the window's height (`max-height: calc(100vh - 150px)`, `aspect-ratio: 16/10`).
5. Outlines sunk half into their layer, because edges are drawn around the origin, not the box.
6. Captions falling off the frame.
7. Selecting a buried part, which then stays hidden.

## 10. three.js traps

- `Object.assign(mesh, { position: … })` throws: `position`, `rotation` and `scale` are read-only. Use `.set()`, or a
  helper `at(o, x, y, z)` that sets it and returns the object.
- `group.add(child)` returns the *group*, so `g.add(m).position.y = 1` moves the group. The template's `add()` returns the child on purpose.
- `Raycaster` does not skip invisible objects. Filter hits by walking up the ancestors for `visible`.
- A canvas needs `tabIndex = 0` and an `aria-label` that says how to drive it, or keys never reach it.
- `OrbitControls.listenToKeyEvents(canvas)` gives arrow-key panning. Put the view keys on the same canvas.
- A trailing `// comment` added to a long one-line statement swallows the code after it on that line. It happened twice
  while writing this skill, so run `node --check` after any scripted edit.
- An effect that draws a *picture* of the page (a CRT bend, a lens) cannot hold a live WebGL canvas. It stands down on
  that page (web-ux H4 and section 7).

## 10a. Maps: what Canada in relief settled

A map is the same method with the land as the bottom layer. What worked, from `canada-homeless-map` (`web/3d/scene.js`):

- **Wear the 2D map's own painting.** Coloured hexes looked flat beside a painted 2D map. Bake the 2D renderer's
  terrain once to an image covering the world rectangle (`dev-tools/bake-terrain.mjs`, 4096 and 8192 px, the larger
  only where `MAX_TEXTURE_SIZE` allows), and sample it in the land's shader by world position, so every hex prism
  wears its own patch and its sides a darkened copy. One draw call for the whole country.
- **A bar is a stack of countable pieces, on a linear scale.** One hex piece per band (1,000 people, 500 beds, $50M),
  the top one partial, a groove between pieces, drawn in the shader from a per-instance count. A small value is a
  thin coin, which keeps it visible without the square-root scale that distorted every comparison. Parker, on plain
  columns: *"the bars all look really yuk"*.
- **Unknown is a little pin** (rule M2a).
- **Lead with the overview.** A card with the national number for what is on screen, its run over the years and the
  five largest places; a year slider on one fixed scale (so growth is real), with a play button. Parker: the map is
  *"a tool for visual pass"*, for *"summary and overview and impact"*, the particulars secondary.
- **Year over year, a stack grows from last year and each year is its own piece.** Never replay from zero when the
  year changes: tween from the height on screen. Shade each point by the first year the stack reached it (light at
  the bottom, one clear step darker per year, a bright seam where each year's piece begins), and mark last year's
  height with a pale collar. Parker: *"every year that passes, the animation starts from zero ... This does not give
  us a sense of going year over year."* A year a source does not cover is unknown, not zero (the agreements record
  begins in 2019), and playback starts at a measure's first known year.
- **Pressure is a division a visitor can see.** Beside the raw measures, give people per bed, dollars per person and
  dollars per bed their own buttons and stacks, each labelled as the plain division of two published numbers.
- **Labels are HTML banners in the 2D map's style, and they hold still.** Measure each plate once at its real size (a
  plate hidden with `display: none` measures zero, seems not to collide, is shown, collides, is hidden: it flickers
  every frame); let plates already on screen claim their room first; require a few frames clear before one appears and
  a few blocked before it goes; fade rather than snap. Parker: *"flickering plates problem"*.
- **A view must exist for every measure it can be asked to show, or not at all.** A layers-apart view with sheets for
  three of seven measures looked up a missing sheet and threw every frame; it was removed.

## 11. Hand it over

Deliver the reading, not the source: a brief with the screenshots from each view, a short clip (see `page-loop`), the
hill-climb table, the test output, and the calls you made (for example, "software WebGL opens flat"). Name what no
headless run can tell you, and say so plainly: how the drag and zoom feel under the reader's own mouse or trackpad, at
their own browser zoom.
