// The web-3d contract, checked in a real browser against any page that follows it (SKILL.md, "The contract"):
//   node model-e2e.mjs http://localhost:8000/fixture.html            software WebGL: flat by default, 3D on request
//   GPU=1 node model-e2e.mjs http://localhost:8000/fixture.html      this machine's graphics card; holds 45 frames a second
// Headless always: no window opens on anyone's desktop. Every expected answer is worked out here from the model's own
// data, never read back from the scene's answer to the same question.
// HOOK names the window global (default __model3d); PLAYWRIGHT points at playwright's index.mjs if it is not on mise's path.
const pw = process.env.PLAYWRIGHT || `${process.env.HOME}/.local/share/mise/installs/playwright/latest/node_modules/playwright/index.mjs`;
const { chromium } = await import(pw);
const URL0 = process.argv[2] || process.env.URL; if (!URL0) { console.error('usage: node model-e2e.mjs PAGE_URL'); process.exit(2); }
const HOOK = process.env.HOOK || '__model3d', GPU = process.env.GPU === '1', FLOOR = +(process.env.FPS_FLOOR || 45);
const b = await chromium.launch(GPU ? { channel: 'chromium', args: ['--enable-gpu', '--ignore-gpu-blocklist', '--use-gl=angle', '--use-angle=gl-egl'] } : {});
let fails = 0; const fail = m => { console.error('FAIL', m); fails++; }, ok = m => console.log('ok  ', m), info = m => console.log('info', m);
const at = q => URL0 + (URL0.includes('?') ? '&' : '?') + q;
const H = (p, f, a) => p.evaluate(([h, src, a]) => (0, eval)(src)(window[h], a), [HOOK, f.toString(), a]);
const settle = p => p.waitForFunction(h => window[h]?.settled, HOOK, { timeout: 15000 });
async function open(url, o = {}) {
  const ctx = await b.newContext({ viewport: o.viewport || { width: 1600, height: 1000 }, reducedMotion: o.reduced ? 'reduce' : 'no-preference' });
  if (o.noWebGL2) await ctx.addInitScript(() => { const g = HTMLCanvasElement.prototype.getContext; HTMLCanvasElement.prototype.getContext = function (k, ...a) { return k === 'webgl2' ? null : g.call(this, k, ...a); }; });
  const p = await ctx.newPage(), errs = [];
  p.on('pageerror', e => errs.push(String(e))); p.on('console', m => m.type() === 'error' && errs.push(m.text()));
  await p.goto(url, { waitUntil: 'networkidle' });
  await p.waitForFunction(() => document.querySelector('[data-model3d]')?.dataset.ready === '1', null, { timeout: 15000 });
  return { ctx, p, errs, mode: () => p.evaluate(() => document.querySelector('[data-model3d]').dataset.mode) };
}

{ // the main run: the 3D model, turned, flattened, lifted apart, picked and pulled
  const { ctx, p, errs, mode } = await open(URL0);
  const m0 = await mode();
  if (GPU) m0 === '3d' ? ok('with a graphics card the page opens on the 3D model') : fail('GPU run opened ' + m0);
  else {
    m0 === 'flat' && await p.isVisible('[data-to3d]') ? ok('software WebGL opens flat, with 3D one click away') : fail('software WebGL opened ' + m0);
    await p.click('[data-to3d]');
  }
  (await mode()) === '3d' ? ok('the 3D model is up') : fail('mode ' + await mode());
  await settle(p);
  const gpu = await H(p, h => h.gpu); info('renderer: ' + gpu);

  // the data holds: links resolve, nothing required loops, no two parts on one layer overlap
  const D = await H(p, h => h.data);
  const ids = new Set(D.parts.map(x => x.id)), layers = new Set(D.layers.map(l => l.key));
  const bad = [...D.parts.filter(x => !layers.has(x.layer)).map(x => x.id + '@' + x.layer), ...D.links.filter(l => !ids.has(l.from) || !ids.has(l.to)).map(l => l.from + '→' + l.to)];
  bad.length ? fail('dangling: ' + bad) : ok(`${D.parts.length} parts on ${D.layers.length} layers, ${D.links.length} links, all resolve`);
  const unk = D.parts.filter(x => x.known !== true && x.known !== false && x.known !== null).map(x => x.id);
  unk.length ? fail('known must be true, false or null (undeclared is not none): ' + unk) : ok('every part declares known: true, false or null');
  const needsOf = {}; D.parts.forEach(x => needsOf[x.id] = []); D.links.forEach(l => l.kind === 'needs' && needsOf[l.to]?.push(l.from));
  const state = {}, cyc = []; const visit = (k, path) => { if (state[k] === 2) return; if (state[k] === 1) { cyc.push([...path, k].join('→')); return; } state[k] = 1; needsOf[k].forEach(n => visit(n, [...path, k])); state[k] = 2; };
  Object.keys(needsOf).forEach(k => visit(k, []));
  cyc.length ? fail('a needs loop: ' + cyc[0]) : ok('nothing required loops');
  const clash = []; D.parts.forEach((a, i) => D.parts.slice(i + 1).forEach(c => { if (a.layer === c.layer && Math.abs(a.x - c.x) * 2 < a.w + c.w && Math.abs(a.z - c.z) * 2 < a.d + c.d) clash.push(a.id + '/' + c.id); }));
  clash.length ? fail('parts overlap on one layer: ' + clash) : ok('no two parts on a layer overlap');

  // views: top lays the layers together, exploded stacks them in order, the pressed button says so
  const names = await H(p, h => h.views);
  await p.click('[data-view="top"]'); await settle(p);
  const ys0 = await H(p, (h, ks) => ks.map(k => h.layerY(k)), D.layers.map(l => l.key));
  await p.click('[data-view="exploded"]'); await settle(p);
  const ys1 = await H(p, (h, ks) => ks.map(k => h.layerY(k)), D.layers.map(l => l.key));
  const together = Math.max(...ys0) - Math.min(...ys0) < .1, stacked = ys1.every((y, i) => !i || y - ys1[i - 1] > .5);
  together && stacked ? ok('Top lays every layer together; Exploded stacks them bottom to top') : fail(JSON.stringify({ ys0, ys1 }));
  (await p.getAttribute('[data-view="exploded"]', 'aria-pressed')) === 'true' && (await p.getAttribute('[data-view="top"]', 'aria-pressed')) === 'false' ? ok('the pressed view button says so') : fail('aria-pressed wrong');
  await p.evaluate(() => { const x = document.querySelector('[data-explode]'); x.value = .5; x.dispatchEvent(new Event('input')); });
  Math.abs(await H(p, h => h.explode) - .5) < 1e-6 ? ok('the slider sets how far apart the layers are') : fail('slider ignored');

  // turning it: a drag moves the camera; a key flies to a view
  const box = await p.locator('[data-model3d] canvas').boundingBox(), c0 = await H(p, h => h.camera);
  await p.mouse.move(box.x + box.width * .5, box.y + box.height * .5); await p.mouse.down(); await p.mouse.move(box.x + box.width * .7, box.y + box.height * .4, { steps: 8 }); await p.mouse.up(); await p.waitForTimeout(300);
  const c1 = await H(p, h => h.camera);
  Math.hypot(c1[0] - c0[0], c1[2] - c0[2]) > .3 ? ok('a drag turns the model') : fail('drag did not move the camera');
  await p.focus('[data-model3d] canvas'); await p.keyboard.press('2'); await settle(p);
  (await H(p, h => h.view)) === names[1] ? ok(`key 2 flies to the ${names[1]} view`) : fail('key 2 gave view ' + await H(p, h => h.view));

  // picking: every part, layer by layer, is found by a ray from where it is drawn. This is the check that caught glow
  // planes and outlines taking their neighbours' clicks.
  await p.click('[data-view="top"]'); await settle(p);
  const miss = [], gaps = [];
  for (const l of D.layers) {
    await H(p, (h, k) => h.solo(k), l.key); await p.waitForTimeout(50);
    const on = D.parts.filter(x => x.layer === l.key);
    for (const x of on) {
      const pt = await H(p, (h, id) => h.project(id), x.id), got = await H(p, (h, a) => h.hitAt(a.x, a.y), pt); if (got !== x.id) miss.push(`${x.id}→${got}`);
      // just outside each edge, where a glow, an outline or a caption would steal a click: the answer is whatever part the
      // data puts at that spot, and usually nothing
      for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const X = x.x + dx * (x.w / 2 + .12), Z = x.z + dz * (x.d / 2 + .12);
        const owner = on.find(o => Math.abs(X - o.x) * 2 < o.w && Math.abs(Z - o.z) * 2 < o.d)?.id ?? null;
        const q = await H(p, (h, a) => h.projectPoint(a.X, a.Z, a.k), { X, Z, k: l.key }), hit = await H(p, (h, a) => h.hitAt(a.x, a.y), q);
        if (hit !== owner) gaps.push(`beside ${x.id}: ${hit} (want ${owner})`);
      }
    }
  }
  await H(p, h => h.solo(null));
  miss.length ? fail('rays land on the wrong part: ' + miss.join(' ')) : ok(`a ray at each of the ${D.parts.length} parts finds that part`);
  gaps.length ? fail('the space beside a part takes clicks: ' + gaps.slice(0, 6).join('; ')) : ok(`the ${D.parts.length * 4} spots just beside the parts take no stolen clicks`);

  // a real click opens a part on the top layer; its chain matches the one worked out here; Esc puts it back
  const topKey = D.layers.at(-1).key, neededBy = {}; D.parts.forEach(x => neededBy[x.id] = []); D.links.forEach(l => l.kind === 'needs' && neededBy[l.from]?.push(l.to));
  const walk = (s, nx) => { const o = new Set(), go = k => nx[k].forEach(n => { if (!o.has(n)) { o.add(n); go(n); } }); go(s); return o; };
  const want = id => [...new Set([...walk(id, needsOf), ...walk(id, neededBy)])].sort();
  const target = D.parts.filter(x => x.layer === topKey).sort((a, c) => want(c.id).length - want(a.id).length)[0].id;
  const pt = await H(p, (h, id) => h.project(id), target); await p.mouse.click(pt.x, pt.y); await p.waitForTimeout(200);
  const sel = await p.evaluate(() => document.querySelector('[data-model3d]').dataset.sel);
  sel === target ? ok(`a click on ${target} selects it`) : fail(`clicked ${target}, selected ${sel}`);
  const ch = await H(p, (h, id) => h.chain(id), target), lit = await H(p, h => h.lit());
  JSON.stringify(ch) === JSON.stringify(want(target)) ? ok(`its chain is the ${ch.length} parts the data says`) : fail(`chain ${ch} want ${want(target)}`);
  JSON.stringify(lit) === JSON.stringify([...want(target), target].sort()) ? ok('exactly the chain stays lit') : fail(`lit ${lit}`);
  // and for every other part: what it needs all the way up, what needs it all the way down, lit and nothing else
  const wrong = [];
  for (const x of D.parts) { await H(p, (h, id) => h.select(id), x.id);
    const c = await H(p, (h, id) => h.chain(id), x.id), l = await H(p, h => h.lit());
    if (JSON.stringify(c) !== JSON.stringify(want(x.id)) || JSON.stringify(l) !== JSON.stringify([...want(x.id), x.id].sort())) wrong.push(x.id); }
  await H(p, (h, id) => h.select(id), target);
  wrong.length ? fail('chain or lit set wrong for ' + wrong) : ok(`selecting each of the ${D.parts.length} parts lights exactly its chain`);
  await settle(p); await p.mouse.move(2, 2); await p.focus('[data-model3d] canvas'); await p.keyboard.press('Escape');   // off the part first: a hover lights its chain on purpose await p.waitForTimeout(150);
  (await p.evaluate(() => document.querySelector('[data-model3d]').dataset.sel)) === '' && (await H(p, h => h.lit())).length === D.parts.length ? ok('Esc clears the selection and lights everything') : fail('Esc did not clear');

  // flat and back
  await p.click('[data-toflat]'); const f = await mode(); await p.click('[data-to3d]'); const g = await mode();
  f === 'flat' && g === '3d' ? ok('flat and 3D switch both ways') : fail(`flat ${f}, back ${g}`);
  await settle(p);

  // speed: renders a second, best of three two-second windows (a shared machine drops a window now and then)
  const win = () => H(p, h => new Promise(r => { const n0 = h.frames, t0 = performance.now(); setTimeout(() => r((h.frames - n0) * 1000 / (performance.now() - t0)), 2000); }));
  const fps = Math.max(await win(), await win(), await win());
  if (GPU) fps >= FLOOR ? ok(`${fps.toFixed(1)} frames a second on the graphics card`) : fail(`${fps.toFixed(1)} frames a second on the graphics card, under ${FLOOR}`);
  else info(`${fps.toFixed(1)} frames a second in software (GPU=1 holds it to ${FLOOR})`);
  errs.length ? fail('page errors: ' + errs.join(' | ')) : ok('no page errors');
  await ctx.close();
}
{ // no WebGL2 at all: the flat view stands in, with no way to ask for 3D
  const { ctx, errs, mode, p } = await open(URL0, { noWebGL2: true });
  (await mode()) === 'flat' && !(await p.isVisible('[data-to3d]')) && !errs.length ? ok('without WebGL2 the flat view stands in') : fail(`mode ${await mode()} errors ${errs}`);
  await ctx.close();
}
{ // reduced motion: no arrival flight, views jump, and nothing is drawn while nothing changes
  const { ctx, p, errs, mode } = await open(at('gl'), { reduced: true });
  const settled = await H(p, h => h.settled);
  await p.click('[data-view="side"]'); await p.waitForTimeout(60);
  const e = await H(p, h => h.explode); await p.waitForTimeout(400);
  const n0 = await H(p, h => h.frames); await p.waitForTimeout(700); const n1 = await H(p, h => h.frames);
  (await mode()) === '3d' && settled && e === 1 && n1 === n0 ? ok('reduced motion: arrives still, views jump, idle frames draw nothing') : fail(JSON.stringify({ settled, e, idleFrames: n1 - n0 }));
  errs.length && fail('page errors, reduced: ' + errs.join(' | ')); await ctx.close();
}
await b.close();
console.log(fails ? `${fails} failed` : 'all passed'); process.exit(fails ? 1 : 0);
