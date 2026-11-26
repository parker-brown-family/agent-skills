/* web-3d starter: a data model drawn as a stack of layers on the graphics card (WebGL2, three.js vendored beside it).
   Copy this file into the project, point the import at the project's bundle (scripts/vendor-three.sh), and call
   mountModel(stage, model, opts). It returns a controller, or null when this machine should get the flat view instead.

   model = {
     layers: [{ key, name }],                          bottom to top
     parts:  [{ id, layer, x, z, w, d, h?, label, known, color? }],
               x, z: the centre, w, d: the footprint, in model units, placed by the project's own rules, never by hand.
               known: true (it has run: solid), false (planned, not run: a hologram), null (nobody knows: grey, dashed).
     links:  [{ from, to, kind: 'needs' | 'helps' }],  "to needs from": pulling `from` darkens `to` and what needs it;
                                                       a 'helps' link only weakens.
   }
   opts = { force, hook, toolbar, onPick(id), gap, exposure, bloom, views, words, label, room }

   The rules this file keeps are written up in SKILL.md: picking ignores glows, outlines and captions; nothing animates for
   a reader who asks for reduced motion, and nothing is drawn when nothing changed; the loop stops when the canvas leaves
   the page; software WebGL gets the flat view unless the reader asks for 3D. */
import * as THREE from './three-bundle.js';
const { OrbitControls, EffectComposer, RenderPass, UnrealBloomPass, OutputPass, Line2, LineMaterial, LineGeometry, RoomEnvironment } = THREE;

const reduce = matchMedia('(prefers-reduced-motion: reduce)');

/* 'gpu', 'software' (SwiftShader, llvmpipe: measured at 5 frames a second on a scene this size) or 'none' */
export function gpuKind() {
  try {
    const g = document.createElement('canvas').getContext('webgl2'); if (!g) return 'none';
    const x = g.getExtension('WEBGL_debug_renderer_info'), name = x ? String(g.getParameter(x.UNMASKED_RENDERER_WEBGL)) : '';
    g.getExtension('WEBGL_lose_context')?.loseContext();   // a page gets about sixteen contexts; never hold a probe's
    return /swiftshader|llvmpipe|softpipe|software/i.test(name) ? 'software' : 'gpu';
  } catch (e) { return 'none'; }
}

/* colours come from the page's CSS variables, through a 2D canvas so oklch() and color-mix() resolve */
const probe = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
function toColor(css, fallback = '#888') {
  probe.clearRect(0, 0, 1, 1); probe.fillStyle = fallback; if (css) probe.fillStyle = css; probe.fillRect(0, 0, 1, 1);
  const d = probe.getImageData(0, 0, 1, 1).data; return new THREE.Color().setRGB(d[0] / 255, d[1] / 255, d[2] / 255, THREE.SRGBColorSpace);
}
function palette(el) {
  const v = (n, f) => toColor(getComputedStyle(el).getPropertyValue(n).trim(), f);
  return { bg: v('--bg', '#14161a'), fg: v('--fg', '#d8dde4'), acc: v('--acc', '#5fb3ff'), good: v('--good', '#5fd38a'), warn: v('--warn', '#e8b04a'), none: v('--none', '#7a808a') };
}

/* text painted on a canvas: part names on top faces, layer captions */
function textTex(lines, w, h, scale = 4) {
  const c = document.createElement('canvas'); c.width = Math.round(w * scale); c.height = Math.round(h * scale);
  const g = c.getContext('2d'); g.scale(scale, scale);
  lines.forEach(L => { g.font = `${L.weight || 600} ${L.size || 12}px ${L.mono ? 'ui-monospace, monospace' : 'system-ui, sans-serif'}`; g.fillStyle = L.color; g.textAlign = 'center'; g.textBaseline = 'middle';
    let t = String(L.text); while (g.measureText(t).width > w - 6 && t.length > 2) t = t.slice(0, -2) + '…';
    g.fillText(t, w / 2, L.y); });
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; return tex;
}
const css = c => '#' + c.getHexString(THREE.SRGBColorSpace);
const noPick = o => { o.raycast = () => {}; o.userData.noPick = true; return o; };   // light, outlines and words are not targets
function glowTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d'), r = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  r.addColorStop(0, 'rgba(255,255,255,.85)'); r.addColorStop(.35, 'rgba(255,255,255,.22)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
}
const ease = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;

export function mountModel(stage, model, opts = {}) {
  const kind = gpuKind();
  if (kind === 'none' || (kind === 'software' && !opts.force)) return null;
  const hookName = opts.hook || '__model3d', gap = opts.gap ?? 1.4, words = Object.assign({ true: 'DONE', false: 'NOT RUN', null: 'UNKNOWN' }, opts.words);
  const P = palette(opts.room || stage);
  const keys = model.layers.map(l => l.key), byId = Object.fromEntries(model.parts.map(p => [p.id, p]));
  const minX = Math.min(...model.parts.map(p => p.x - p.w / 2)), maxX = Math.max(...model.parts.map(p => p.x + p.w / 2));
  const minZ = Math.min(...model.parts.map(p => p.z - p.d / 2)), maxZ = Math.max(...model.parts.map(p => p.z + p.d / 2));
  const cx = (minX + maxX) / 2, cz = (minZ + maxZ) / 2, W = maxX - minX + 1, D = maxZ - minZ + 1, r = Math.max(W, D), top = gap * (keys.length - 1);

  /* what pulling a part darkens: everything that needs it, all the way down, and everything it needs, all the way up */
  const needsOf = {}, neededBy = {}, helps = {};
  model.parts.forEach(p => { needsOf[p.id] = []; neededBy[p.id] = []; helps[p.id] = []; });
  model.links.forEach(l => { if (!byId[l.from] || !byId[l.to]) return; if (l.kind === 'needs') { needsOf[l.to].push(l.from); neededBy[l.from].push(l.to); } else { helps[l.to].push(l.from); helps[l.from].push(l.to); } });
  const walk = (start, next) => { const s = new Set(), go = k => next[k].forEach(n => { if (!s.has(n)) { s.add(n); go(n); } }); go(start); return s; };
  const chain = id => new Set([...walk(id, needsOf), ...walk(id, neededBy)]);

  /* the renderer: ACES tone mapping, the room's reflections, bloom on whatever glows */
  const canvas = document.createElement('canvas'); canvas.tabIndex = 0; canvas.className = 'm3d-gl';
  canvas.setAttribute('aria-label', opts.label || 'A 3D model. Drag to turn it, scroll to zoom, right-drag to move it, keys 1 to 4 change the view, Esc clears a selection.');
  canvas.style.cssText = 'display:block;width:100%;height:100%;outline:none;cursor:grab;touch-action:none';
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = opts.exposure ?? .85; renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene(); scene.background = P.bg.clone().multiplyScalar(.6); scene.fog = new THREE.Fog(scene.background, r * 2.2, r * 4.5);
  const pmrem = new THREE.PMREMGenerator(renderer); scene.environment = pmrem.fromScene(new RoomEnvironment(), .04).texture; pmrem.dispose();
  scene.environmentIntensity = opts.reflections ?? .35;   // the room at full strength bleached every surface to a pale haze
  const camera = new THREE.PerspectiveCamera(38, 1, .1, r * 12);
  const controls = new OrbitControls(camera, canvas);
  Object.assign(controls, { enableDamping: true, dampingFactor: .08, minDistance: r * .18, maxDistance: r * 3, maxPolarAngle: Math.PI * .92, keyPanSpeed: 14 });
  controls.listenToKeyEvents(canvas);
  scene.add(new THREE.HemisphereLight(P.fg, P.bg, .25));
  const key = new THREE.DirectionalLight(0xffffff, 1.2); key.position.set(-r * .5, r + top, -r * .4); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -.0004;
  Object.assign(key.shadow.camera, { left: -r * .7, right: r * .7, top: r * .7, bottom: -r * .7, near: .5, far: r * 4 }); scene.add(key);
  const comp = new EffectComposer(renderer); comp.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(256, 256), opts.bloom ?? .55, .42, .84); comp.addPass(bloom); comp.addPass(new OutputPass());

  /* layers: one group each, raised by the explode amount; a plate, an outline and a caption on every one */
  const groups = {}, plates = {}, captions = {};
  keys.forEach((k, i) => {
    const g = new THREE.Group(); g.name = k; scene.add(g); groups[k] = g; g.userData.parts = new THREE.Group(); g.add(g.userData.parts);
    const plate = new THREE.Mesh(new THREE.BoxGeometry(W, .05, D), new THREE.MeshPhysicalMaterial({ color: P.bg.clone().lerp(P.acc, .05 + i * .03), roughness: .7, metalness: .1, transparent: true, opacity: i ? .55 : .95, clearcoat: .25, depthWrite: !i }));
    plate.position.y = -.026; plate.receiveShadow = true; g.add(plate); plates[k] = plate;
    plate.add(noPick(new THREE.LineSegments(new THREE.EdgesGeometry(plate.geometry), new THREE.LineBasicMaterial({ color: P.acc, transparent: true, opacity: .45 }))));
    const cap = noPick(new THREE.Sprite(new THREE.SpriteMaterial({ map: textTex([{ text: model.layers[i].name || k, size: 15, y: 16, color: css(P.fg) }], 220, 32), transparent: true, depthWrite: false })));
    cap.scale.set(2.2, .32, 1); cap.position.set(-W / 2 + 1.2, .18, D / 2 + .32); g.add(cap); captions[k] = cap;   // on the front edge, which every view sees and no part stands on
  });

  /* parts: solid when known to have run, a hologram when planned, grey and dashed when nobody knows */
  const glow = glowTexture(), parts = {}, PX = 80;   // canvas pixels per model unit on a part's top face
  model.parts.forEach(p => {
    const g = new THREE.Group(); g.position.set(p.x - cx, 0, p.z - cz); g.userData.id = p.id;
    const h = p.h ?? .35, geo = new THREE.BoxGeometry(p.w, h, p.d), c = p.color ? toColor(p.color) : p.known === null ? P.none : P.acc;
    const mats = [], add = (o, base) => { (Array.isArray(o.material) ? o.material : [o.material]).forEach(m => { m.transparent = true; m.userData.base = base ?? m.opacity; mats.push(m); }); g.add(o); return o; };
    let body;
    if (p.known === true) {
      body = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: P.bg.clone().lerp(c, .2), roughness: .55, metalness: .35 })); body.castShadow = body.receiveShadow = true;   // dark slab, light words: pale slabs made the names unreadable
      add(noPick(new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: c, transparent: true, opacity: .55 })))).position.y = h / 2;
      const led = new THREE.Mesh(new THREE.SphereGeometry(.05, 16, 12), new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: 1.6 }));
      led.position.set(p.w / 2 - .12, h + .05, p.d / 2 - .12); g.userData.led = led; add(noPick(led));
      const pool = noPick(new THREE.Mesh(new THREE.PlaneGeometry(p.w * 2, p.d * 2), new THREE.MeshBasicMaterial({ map: glow, color: c, transparent: true, opacity: .22, depthWrite: false, blending: THREE.AdditiveBlending })));
      pool.rotation.x = -Math.PI / 2; pool.position.y = .004; add(pool);
    } else if (p.known === false) {
      body = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: .08, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide }));
      add(noPick(new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: c, transparent: true, opacity: .9 })))).position.y = h / 2;
    } else {
      body = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: P.none, transparent: true, opacity: .06, depthWrite: false }));
      const e = noPick(new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineDashedMaterial({ color: P.none, dashSize: .06, gapSize: .05, transparent: true }))); e.computeLineDistances(); add(e).position.y = h / 2;
    }
    body.position.y = h / 2; body.userData.pid = p.id; add(body);
    const label = noPick(new THREE.Mesh(new THREE.PlaneGeometry(p.w * .94, p.d * .94), new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false,
      map: textTex([{ text: p.label || p.id, size: 13, y: p.d * PX * .38, color: p.known === true ? '#f4f6f8' : css(c.clone().lerp(new THREE.Color(1, 1, 1), .45)) }, { text: words[String(p.known)], size: 9, mono: true, y: p.d * PX * .68, color: p.known === true ? css(P.good) : css(c.clone().lerp(new THREE.Color(1, 1, 1), .3)) }], p.w * PX, p.d * PX) })));
    label.rotation.x = -Math.PI / 2; label.position.y = h + .003; add(label);
    groups[p.layer].userData.parts.add(g); parts[p.id] = { g, body, h, mats };
  });

  /* links: an arch from the top of one part to the top of the other, recomputed whenever the layers move */
  const res = new THREE.Vector2(1, 1);
  const links = model.links.filter(l => byId[l.from] && byId[l.to]).map(l => {
    const need = l.kind === 'needs';
    const mat = new LineMaterial({ color: need ? P.acc : P.fg, linewidth: need ? 3 : 1.6, transparent: true, opacity: need ? .85 : .4, dashed: !need, dashSize: .1, gapSize: .09, worldUnits: false, resolution: res });
    const line = noPick(new Line2(new LineGeometry(), mat)); scene.add(line); mat.userData.base = mat.opacity;
    return { ...l, need, mat, line };
  });
  const tip = id => { const o = parts[id]; return o.g.getWorldPosition(new THREE.Vector3()).setY(groups[byId[id].layer].position.y + o.h); };
  function route(L) {
    const a = tip(L.from), b = tip(L.to), lift = .45 + a.distanceTo(b) * .12, c = a.clone().lerp(b, .5); c.y = Math.max(a.y, b.y) + lift;
    const pts = new THREE.QuadraticBezierCurve3(a, c, b).getPoints(20), flat = []; pts.forEach(v => flat.push(v.x, v.y, v.z));
    L.line.geometry.dispose(); L.line.geometry = new LineGeometry(); L.line.geometry.setPositions(flat); L.line.computeLineDistances();
  }

  const S = { explode: .25, flight: null, view: 'perspective', sel: null, hover: null, dirty: true, frames: 0, fps: null, fpsAt: 0, fpsN: 0, t0: performance.now(), solo: null };
  function layout() {
    keys.forEach((k, i) => { groups[k].position.y = i * .012 + i * gap * S.explode; });   // the small step keeps flat layers from fighting for depth
    keys.forEach((k, i) => { if (i) plates[k].material.opacity = .55 - S.explode * .3; captions[k].visible = S.explode > .25; captions[k].material.opacity = Math.min(1, (S.explode - .25) / .5); });
    scene.updateMatrixWorld(true); links.forEach(route); S.dirty = true;
    opts.toolbar?.querySelectorAll('[data-explode]').forEach(x => { if (+x.value !== S.explode) x.value = S.explode; });
  }

  /* lit, weak, dim: the selection (or the hover) and its chain stay lit, what only helps it is half lit */
  function apply() {
    const f = S.sel || S.hover, lit = f ? chain(f).add(f) : null, weak = f ? new Set(helps[f]) : null;
    Object.entries(parts).forEach(([id, o]) => { const k = !lit || lit.has(id) ? 1 : weak.has(id) ? .5 : .16; o.lit = k === 1;
      o.mats.forEach(m => { m.opacity = m.userData.base * k; }); });
    links.forEach(L => { const on = !lit || (lit.has(L.from) && lit.has(L.to)); L.mat.opacity = L.mat.userData.base * (on ? 1 : .12); });
    S.dirty = true;
  }

  /* views are data: where the camera sits, where it looks, how far apart the layers are */
  const VIEWS = Object.assign({
    perspective: { pos: [-r * .78, r * .78 + top * .3, r * 1.02], tgt: [0, top * .15, 0], e: .25 },
    top: { pos: [0, r * 1.3, .001], tgt: [0, 0, 0], e: 0 },
    side: { pos: [0, top * .5 + r * .08, r * 1.3], tgt: [0, top * .5, 0], e: 1 },
    exploded: { pos: [-r * 1.05, r * .62 + top * .5, r * 1.0], tgt: [0, top * .45, 0], e: 1 },
  }, opts.views);
  const names = Object.keys(VIEWS);
  function press(view) { opts.toolbar?.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed', b.dataset.view === view ? 'true' : 'false')); }
  function fly(v, ms = 1100) {
    const to = typeof v === 'string' ? VIEWS[v] : v; if (!to) return;
    S.flight = { from: { p: camera.position.clone(), t: controls.target.clone(), e: S.explode }, to: { p: new THREE.Vector3(...to.pos), t: new THREE.Vector3(...to.tgt), e: to.e ?? S.explode }, t0: performance.now(), ms: reduce.matches ? 0 : ms };
    S.view = typeof v === 'string' ? v : null; press(S.view); S.dirty = true;
  }
  function flyTo(id) {   // close enough to read it, from the side the camera already looks from
    const p = parts[id].g.getWorldPosition(new THREE.Vector3()), dir = camera.position.clone().sub(controls.target).normalize();
    if (dir.y < .55) { dir.y = .55; dir.normalize(); }
    const buried = keys.indexOf(byId[id].layer) < keys.length - 1, e = buried ? Math.max(S.explode, 1) : S.explode;   // a part under other layers is lifted clear of them
    p.y += (e - S.explode) * gap * keys.indexOf(byId[id].layer);
    fly({ pos: p.clone().add(dir.multiplyScalar(r * .6)).toArray(), tgt: p.toArray(), e }, 900);
  }

  /* picking: only part bodies on visible layers; a drag that moved more than 5 px is a turn, not a click */
  const ray = new THREE.Raycaster(), ptr = new THREE.Vector2(); ray.params.Line.threshold = .005; ray.params.Points.threshold = .005;
  const shown = o => { for (; o; o = o.parent) if (!o.visible) return false; return true; };
  const owner = o => { for (; o; o = o.parent) if (o.userData.id) return o.userData.id; return null; };   // any mesh of a part answers for the part, so whatever is not a target must say noPick
  function hitsAt(x, y) {
    const b = canvas.getBoundingClientRect(); ptr.set((x - b.left) / b.width * 2 - 1, -(y - b.top) / b.height * 2 + 1); ray.setFromCamera(ptr, camera);
    return ray.intersectObjects(keys.map(k => groups[k].userData.parts), true).filter(h => shown(h.object) && !h.object.userData.noPick)
      .map(h => ({ id: owner(h.object), kind: h.object.type, d: +h.distance.toFixed(3) }));
  }
  const hitAt = (x, y) => hitsAt(x, y)[0]?.id ?? null;
  function select(id) {   // Esc flies back to the view the reader left
    const next = id && parts[id] ? id : null; if (next && !S.sel) S.back = S.view || 'perspective';
    S.sel = next; stage.dataset.sel = S.sel || ''; apply(); opts.onPick?.(S.sel); if (S.sel) flyTo(S.sel);
  }
  let down = null;
  canvas.addEventListener('pointerdown', ev => { down = [ev.clientX, ev.clientY]; });
  canvas.addEventListener('pointerup', ev => { if (down && Math.hypot(ev.clientX - down[0], ev.clientY - down[1]) <= 5) select(hitAt(ev.clientX, ev.clientY)); down = null; });
  canvas.addEventListener('pointermove', ev => { if (ev.buttons) return; const id = hitAt(ev.clientX, ev.clientY); canvas.style.cursor = id ? 'pointer' : 'grab'; if (id !== S.hover) { S.hover = id; if (!S.sel) apply(); } });
  canvas.addEventListener('pointerleave', () => { S.hover = null; if (!S.sel) apply(); });
  canvas.addEventListener('keydown', ev => {
    if (ev.key === 'Escape' && S.sel) { select(null); fly(S.back || 'perspective'); ev.preventDefault(); return; }
    const v = names[+ev.key - 1]; if (v && /^[1-9]$/.test(ev.key)) { fly(v); ev.preventDefault(); }
  });
  controls.addEventListener('change', () => { S.dirty = true; });
  controls.addEventListener('start', () => { S.flight = null; if (S.view) { S.view = null; press(null); } });
  opts.toolbar?.querySelectorAll('[data-view]').forEach(b => { b.onclick = () => fly(b.dataset.view); });
  opts.toolbar?.querySelectorAll('[data-explode]').forEach(x => { x.oninput = () => { S.flight = null; S.explode = +x.value; layout(); }; });

  /* size: the canvas fills the stage; fat lines need the new resolution or they draw at the wrong width */
  function size() { const w = stage.clientWidth, h = stage.clientHeight; if (!w || !h) return; renderer.setSize(w, h, false); comp.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix(); res.set(w, h); S.dirty = true; }
  stage.replaceChildren(canvas);
  const ro = new ResizeObserver(size); ro.observe(stage); size();

  /* arrival: the model settles out of the sky with its layers closing, once per page load, never under reduced motion */
  const v0 = VIEWS.perspective;
  if (reduce.matches || window.__model3dArrived) { camera.position.set(...v0.pos); controls.target.set(...v0.tgt); S.explode = v0.e; }
  else { camera.position.set(.01, r * 2, r * .12); controls.target.set(0, 0, 0); S.explode = 1.6; fly('perspective', 2600); }
  window.__model3dArrived = true; layout(); apply(); press(S.view);

  let alive = true;
  function loop() {
    if (!alive || !canvas.isConnected) return dispose();
    requestAnimationFrame(loop);
    const now = performance.now(), t = (now - S.t0) / 1000;
    if (S.flight) { const f = S.flight, k = f.ms ? Math.min(1, (now - f.t0) / f.ms) : 1, q = ease(k);
      camera.position.lerpVectors(f.from.p, f.to.p, q); controls.target.lerpVectors(f.from.t, f.to.t, q);
      if (f.to.e !== f.from.e) { S.explode = f.from.e + (f.to.e - f.from.e) * q; layout(); }
      if (k >= 1) S.flight = null; S.dirty = true; }
    controls.update();
    if (!reduce.matches) {   // the only things that move on their own: LEDs breathe, helping links crawl
      Object.values(parts).forEach(o => { const L = o.g.userData.led; if (L) L.material.emissiveIntensity = 1.1 + .7 * Math.sin(t * 3 + o.g.position.x); });
      links.forEach(L => { if (!L.need) L.mat.dashOffset = -t * .4; });
      S.dirty = true;
    }
    if (!S.dirty) return; S.dirty = false;
    comp.render(); S.frames++; S.fpsN++;
    if (now - S.fpsAt >= 1000) { S.fps = S.fpsAt ? S.fpsN * 1000 / (now - S.fpsAt) : null; S.fpsN = 0; S.fpsAt = now; }
  }
  function dispose() {
    if (!alive) return; alive = false; ro.disconnect(); controls.dispose();
    scene.traverse(o => { o.geometry?.dispose?.(); (Array.isArray(o.material) ? o.material : o.material ? [o.material] : []).forEach(m => { m.map?.dispose?.(); m.dispose(); }); });
    comp.dispose?.(); renderer.dispose(); renderer.forceContextLoss(); canvas.remove();
    if (window[hookName] === hook) delete window[hookName];
  }

  /* the hook a test drives: every number here is read off the scene, never off a copy of the answer */
  const hook = {
    mode: '3d', gpu: kind, data: model, views: names,
    get view() { return S.view; }, get settled() { return !S.flight; }, get explode() { return S.explode; }, set explode(e) { S.flight = null; S.explode = e; layout(); },
    get selected() { return S.sel; }, get camera() { return camera.position.toArray(); }, get fps() { return S.fps; }, get frames() { return S.frames; },
    layerY: k => groups[k]?.position.y ?? null,
    fly, select, hitAt, hitsAt,
    chain: id => [...chain(id)].sort(),
    lit: () => Object.keys(parts).filter(id => parts[id].lit).sort(),
    solo(k) { keys.forEach(j => { groups[j].visible = !k || j === k; }); S.dirty = true; },
    projectPoint(x, z, layer) {   // a point on a layer, in model units, in page pixels: tests probe the gaps between parts with it
      const g = groups[layer]; if (!g) return null; g.updateMatrixWorld(true);
      const p = new THREE.Vector3(x - cx, .06, z - cz).applyMatrix4(g.matrixWorld).project(camera), b = canvas.getBoundingClientRect();
      return { x: b.left + (p.x + 1) / 2 * b.width, y: b.top + (1 - p.y) / 2 * b.height };
    },
    project(id) {   // the middle of a part's top face, in page pixels
      const o = parts[id]; if (!o) return null; o.g.updateMatrixWorld(true);
      const p = new THREE.Box3().setFromObject(o.body).getCenter(new THREE.Vector3()); p.y = new THREE.Box3().setFromObject(o.body).max.y; p.project(camera);
      const b = canvas.getBoundingClientRect(); return { x: b.left + (p.x + 1) / 2 * b.width, y: b.top + (1 - p.y) / 2 * b.height };
    },
  };
  window[hookName] = hook;
  stage.dataset.mode = '3d'; stage.dataset.sel = ''; stage.dataset.ready = '1';
  loop();
  return { hook, fly, select, dispose, get explode() { return S.explode; } };
}
