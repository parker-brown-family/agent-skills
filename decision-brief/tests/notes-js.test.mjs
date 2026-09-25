// notes.js in a real Chromium, driven through the page's own buttons, held to the
// reference writer in ../fixtures/notes-format/writer.mjs.
//
//   node decision-brief/tests/notes-js.test.mjs                 test assets/notes.js
//   node decision-brief/tests/notes-js.test.mjs --notes-js <rev> test that commit's notes.js
//
// Each test names the release it was written against and what that release gets wrong,
// so `--notes-js 250188f` shows every test failing for its stated reason. Needs
// playwright-core and a Chromium; see ../fixtures/notes-format/README.md.
import { readFileSync, writeFileSync, mkdtempSync, mkdirSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { release, buildBrief } from '../fixtures/notes-format/brief.mjs';
import { planWrite, findIsland, attr, readIslands, buildMap } from '../fixtures/notes-format/writer.mjs';
import { launch, openPage, EXTRACT, STATE, applyEdits, saveIntoFile, copyMap, tsDate } from '../fixtures/notes-format/browser.mjs';
import { A, add, del, concur, unconcur, HOSTILE, CASES } from '../fixtures/notes-format/cases.mjs';
import { mirrors } from '../fixtures/notes-format/check.mjs';

const args = process.argv.slice(2);
const rev = args.includes('--notes-js') ? args[args.indexOf('--notes-js') + 1] : null;
const CURRENT = release('current');
const REL = rev ? { ...CURRENT, js: release(rev).js } : CURRENT;
const DIR = mkdtempSync(join(tmpdir(), 'notes-js-test-'));
const LABEL = 'brief.html';
const R = (hhmm) => `2026-09-24T${hhmm}:00.000Z`;
const anchorsOf = async (page) => (await page.evaluate(EXTRACT)).map(({ nid, title }) => ({ nid, title }));

let n = 0;
function file(html, name = 'brief.html') {
  const d = join(DIR, String(++n));
  mkdirSync(d);
  const p = join(d, name);
  writeFileSync(p, html);
  return { path: p, url: 'file://' + p };
}
// The notes.js under test, in place of whatever this release's notes.js a case inlines.
const swap = (html) => rev ? html.replace(CURRENT.js, () => REL.js) : html;
const el = (buf, id) => { const i = findIsland(buf, id); return i ? buf.subarray(i.tagStart, i.closeEnd).toString('utf8') : null; };
const trunc = (s) => JSON.stringify(s).slice(0, 300);

const TESTS = [];
const test = (name, wrong, fn) => TESTS.push({ name, wrong, fn });

// ---------------------------------------------------------------------------------------
test('the ordinary path: add and delete notes, concur and peel, reload, copy map, save into file, reopen',
  '250188f saves no revision, so its islands differ from the reference writer\'s',
  async (b, expect) => {
    expect(!/<\/script/i.test(REL.js) && !REL.js.includes('<!--'), 'notes.js holds no closing script tag and no "<!--", so it can be inlined');
    const { url, path } = file(buildBrief(REL));
    const original = readFileSync(path);
    const p = await openPage(b, url, { clock: tsDate('2026-09-24 20:00') });
    const anchors = await anchorsOf(p.page);
    const edits = [add(A.finding, 'First thought, deleted below.', '2026-09-24 20:00'),
      add(A.finding, 'A plain note, nothing odd in it.', '2026-09-24 20:01'),
      add(A.fig, 'And one on the figure.', '2026-09-24 20:02'),
      del(A.finding, 'First thought, deleted below.'),
      concur(A.ask1, '2026-09-24 20:03'), concur(A.ask2, '2026-09-24 20:04'), unconcur(A.ask2, '2026-09-24 20:05')];
    await applyEdits(p.page, edits);
    const st = await p.page.evaluate(STATE);
    expect(st.noteCount === '2' && st.concurCount === '1', 'two notes and one concur counted', trunc(st));
    expect(JSON.stringify(st.badges) === JSON.stringify({ [A.finding[0]]: '1', [A.fig[0]]: '1' }), 'badges on the finding and the figure', trunc(st.badges));
    expect(JSON.stringify(st.stamped) === JSON.stringify([A.ask1[0]]), 'a stamp on the first decision only', trunc(st.stamped));
    await p.page.reload({ waitUntil: 'load' });
    expect(JSON.stringify(await p.page.evaluate(STATE)) === JSON.stringify(st), 'a reload shows the same notes and stamps');
    const plan = planWrite(original, edits, { anchors, label: LABEL, concurSupport: 'supported', rev: R('20:10') });
    const map = await copyMap(p.page);
    expect(map === buildMap(LABEL, plan.notes, anchors, plan.concurs), 'copy map equals the reference buildMap', trunc(map));
    const { bytes } = await saveIntoFile(p.page, R('20:10'));
    await p.ctx.close();
    for (const id of ['report-notes', 'report-concurs']) {
      const tag = (findIsland(bytes, id) || {}).openTag || '';
      expect(attr(tag, 'data-format') === '1' && attr(tag, 'data-rev') === R('20:10'), `#${id} carries data-format="1" and data-rev="${R('20:10')}"`, tag);
      expect(el(bytes, id) === el(plan.out, id), `#${id} equals the reference writer's, byte for byte`, trunc(el(bytes, id)));
    }
    const bm = mirrors(bytes), wm = mirrors(plan.out);
    expect(bm.length === 1 && bm[0].equals(wm[0]), 'one READER NOTES comment, equal to the reference writer\'s', `${bm.length} comments`);
    const again = file(bytes);
    const r = await openPage(b, again.url);
    expect(JSON.stringify(await r.page.evaluate(STATE)) === JSON.stringify(st), 'the saved file reopens, in a fresh browser, to the same notes and stamps');
    expect((await copyMap(r.page)) === map, 'and its copy map is the same text');
    expect(!p.errors.length && !r.errors.length, 'no page errors', [...p.errors, ...r.errors].join(' | '));
    await r.ctx.close();
  });

// ---------------------------------------------------------------------------------------
test('hostile note text survives save into file and reopen, exactly (#25)',
  '250188f writes "</script>" raw into the island, so the rest spills into the page and the reopened file shows no notes',
  async (b, expect) => {
    const { url, path } = file(buildBrief(REL));
    const original = readFileSync(path);
    const p = await openPage(b, url, { clock: tsDate('2026-09-24 20:00') });
    const anchors = await anchorsOf(p.page);
    const edits = HOSTILE.map((t, i) => add(i < 3 ? A.finding : A.fig, t, `2026-09-24 20:0${i}`));
    await applyEdits(p.page, edits);
    const { bytes } = await saveIntoFile(p.page, R('20:10'));
    await p.ctx.close();
    const plan = planWrite(original, edits, { anchors, label: LABEL, concurSupport: 'supported', rev: R('20:10') });
    const isl = findIsland(bytes, 'report-notes');
    const inner = bytes.subarray(isl.start, isl.end).toString('utf8');
    expect(!inner.includes('</') && !inner.includes('<!'), 'the island holds no raw "</" or "<!"', trunc(inner));
    expect(el(bytes, 'report-notes') === el(plan.out, 'report-notes'), 'the island equals the reference writer\'s', trunc(el(bytes, 'report-notes')));
    const m = mirrors(bytes);
    expect(m.length === 1 && m[0].equals(mirrors(plan.out)[0]), 'one READER NOTES comment, equal to the reference writer\'s, not ended early', trunc(m.map(String)));
    let back = null;
    try { back = readIslands(bytes).notes; } catch (e) { back = e.message; }
    expect(JSON.stringify(back) === JSON.stringify(plan.notes), 'the island parses back to the identical notes', trunc(back));
    const again = file(bytes);
    const r = await openPage(b, again.url);
    const st = await r.page.evaluate(STATE);
    expect(st.noteCount === '5', 'the reopened file shows all five notes', trunc(st));
    const leaked = await r.page.evaluate(() => /LEAKED|"title"|ts"/.test(document.body.innerText));
    expect(!leaked, 'no note text leaks into the page');
    expect(!r.errors.length, 'no page errors', r.errors.join(' | '));
    if (st.noteCount !== '5') { await r.ctx.close(); return; }   // nothing left to save
    const { bytes: second } = await saveIntoFile(r.page, R('20:20'));
    await r.ctx.close();
    const i2 = findIsland(second, 'report-notes');
    expect(i2 && second.subarray(i2.start, i2.end).toString('utf8') === inner, 'saving the reopened file again writes the same island text');
  });

// ---------------------------------------------------------------------------------------
test('a save replaces the last READER NOTES comment instead of adding another (#25)',
  '250188f appends a comment on every save, so a grep finds a stale map first',
  async (b, expect) => {
    const first = file(buildBrief(REL));
    let p = await openPage(b, first.url, { clock: tsDate('2026-09-24 20:00') });
    await applyEdits(p.page, [add(A.finding, 'Saved once.', '2026-09-24 20:00')]);
    const { bytes: one } = await saveIntoFile(p.page, R('20:01'));
    await p.ctx.close();
    const second = file(one);
    p = await openPage(b, second.url, { clock: tsDate('2026-09-24 20:02') });
    const anchors = await anchorsOf(p.page);
    const edit = [add(A.card, 'Saved twice.', '2026-09-24 20:02')];
    await applyEdits(p.page, edit);
    const { bytes: two } = await saveIntoFile(p.page, R('20:03'));
    await p.ctx.close();
    const m = mirrors(two);
    expect(m.length === 1, 'one comment after two saves', `${m.length} comments`);
    expect(m.length && m[m.length - 1].toString().includes('Saved once.') && m[m.length - 1].toString().includes('Saved twice.'), 'and it lists both notes');
    const plan = planWrite(one, edit, { anchors, label: LABEL, concurSupport: 'supported', rev: R('20:03') });
    expect(m.length && m[m.length - 1].equals(mirrors(plan.out)[0]), 'equal to what the reference writer leaves');

    const staleSpec = CASES.find((c) => c.name === 'stale-mirrors');
    const stale = Buffer.from(swap(staleSpec.brief()));
    const s = file(stale);
    p = await openPage(b, s.url, { clock: tsDate('2026-09-24 20:00') });
    await applyEdits(p.page, staleSpec.edits);
    const { bytes: saved } = await saveIntoFile(p.page, staleSpec.rev);
    await p.ctx.close();
    const before = mirrors(stale), after = mirrors(saved);
    expect(after.length === 3, 'a brief that already holds three comments still holds three', `${after.length}`);
    expect(after.length === 3 && after[0].equals(before[0]) && after[1].equals(before[1]), 'the two stale ones are byte-identical');
    expect(after.length && after[after.length - 1].toString().includes('Added after the stale mirrors.'), 'the last one is the new map');
  });

// ---------------------------------------------------------------------------------------
const R2 = R('19:00');
const bakedA = { [A.finding[0]]: [{ text: 'Written into the file by another writer.', title: A.finding[1], ts: '2026-09-24 19:00' }] };
const bakedC = { [A.ask1[0]]: '2026-09-24 19:00' };
const browserB = { [A.fig[0]]: [{ text: 'Only this browser has this one.', title: A.fig[1], ts: '2026-09-23 08:00' }] };
function bakedBrief(withRev = true) {
  const pristine = Buffer.from(buildBrief(REL, withRev ? {} : { notesAttrs: '', concursAttrs: '' }));
  const anchors = Object.values(A).map(([nid, title]) => ({ nid, title }));
  return planWrite(pristine, [add(A.finding, bakedA[A.finding[0]][0].text, '2026-09-24 19:00'), concur(A.ask1, '2026-09-24 19:00')],
    { anchors, label: LABEL, concurSupport: 'supported', rev: R2 }).out;
}

test('notes written into the file after the browser stored its own map are shown (#24)',
  '250188f shows whatever localStorage holds for the filename, even {}, and never the file\'s islands',
  async (b, expect) => {
    // a. The browser's map carries an older revision: the file's note and concur come in,
    //    and the browser's own note stays.
    const f = file(bakedBrief());
    const sync = JSON.stringify({ notes: { rev: R('08:00'), seen: [] }, concurs: { rev: R('08:00'), seen: [] } });
    let p = await openPage(b, f.url, { storage: [['notes:' + LABEL, JSON.stringify(browserB)], ['concurs:' + LABEL, '{}'], ['notes-sync:' + LABEL, sync]] });
    let st = await p.page.evaluate(STATE);
    expect(st.badges[A.finding[0]] === '1', 'the note written into the file shows', trunc(st));
    expect(st.badges[A.fig[0]] === '1', 'the note only the browser had still shows', trunc(st));
    expect(st.concurCount === '1' && st.stamped[0] === A.ask1[0], 'the concur written into the file shows', trunc(st));
    await p.ctx.close();
    // b. What the clear button leaves in a browser from before format 1: {} and no record.
    p = await openPage(b, f.url, { storage: [['notes:' + LABEL, '{}'], ['concurs:' + LABEL, '{}']] });
    st = await p.page.evaluate(STATE);
    expect(st.noteCount === '1' && st.concurCount === '1', 'an empty stored map no longer hides the file\'s note and concur', trunc(st));
    await p.ctx.close();
    // c. A brief saved before format 1 has no revision at all. The rule: keep everything
    //    the browser holds, and bring in everything the file holds that it has not seen.
    const g = file(bakedBrief(false));
    p = await openPage(b, g.url, { storage: [['notes:' + LABEL, JSON.stringify(browserB)]] });
    st = await p.page.evaluate(STATE);
    expect(st.noteCount === '2', 'with no revision on the island: the browser\'s note and the file\'s note both show', trunc(st));
    await p.ctx.close();
  });

test('a newer file never costs the reader a note, and what the reader deleted stays deleted (#24)',
  '250188f keeps showing the browser\'s copy, so the newer file\'s note never appears',
  async (b, expect) => {
    const f = file(bakedBrief());
    const p = await openPage(b, f.url, { clock: tsDate('2026-09-24 20:00') });
    const anchors = await anchorsOf(p.page);
    await applyEdits(p.page, [del(A.finding, bakedA[A.finding[0]][0].text), unconcur(A.ask1, '2026-09-24 20:00'),
      add(A.card, 'Added in this browser, never saved into the file.', '2026-09-24 20:01')]);
    await p.page.reload({ waitUntil: 'load' });
    let st = await p.page.evaluate(STATE);
    expect(!st.badges[A.finding[0]] && st.concurCount === '0' && st.badges[A.card[0]] === '1', 'after a reload the deletions hold and the new note stays', trunc(st));
    // Another writer adds a note to the file, keeping the note and concur this browser removed.
    const newer = planWrite(readFileSync(f.path), [add(A.callout, 'Added to the file later, by another writer.', '2026-09-24 21:00')],
      { anchors, label: LABEL, concurSupport: 'supported', rev: R('21:00') }).out;
    writeFileSync(f.path, newer);
    await p.page.reload({ waitUntil: 'load' });
    st = await p.page.evaluate(STATE);
    expect(st.badges[A.callout[0]] === '1', 'the newer file\'s note shows', trunc(st));
    expect(st.badges[A.card[0]] === '1', 'the browser\'s unsaved note is still there', trunc(st));
    expect(!st.badges[A.finding[0]] && st.concurCount === '0', 'the note and concur the reader removed stay removed', trunc(st));
    // The clear button, answered: nothing the file holds comes back on reload.
    await p.page.click('#btn-clear');
    await p.page.reload({ waitUntil: 'load' });
    st = await p.page.evaluate(STATE);
    expect(st.noteCount === '0', 'after ✕ and a reload, no note comes back', trunc(st));
    expect(!p.errors.length, 'no page errors', p.errors.join(' | '));
    await p.ctx.close();
  });

// ---------------------------------------------------------------------------------------
test('a concurs island is made only when there are concurs, right after the notes island',
  '250188f adds an empty concurs island on every save, which the reference writer does not',
  async (b, expect) => {
    const { url, path } = file(buildBrief(REL, { concurs: null }));
    const original = readFileSync(path);
    const p = await openPage(b, url, { clock: tsDate('2026-09-24 20:00') });
    const anchors = await anchorsOf(p.page);
    await applyEdits(p.page, [add(A.finding, 'Notes only.', '2026-09-24 20:00')]);
    const { bytes: one } = await saveIntoFile(p.page, R('20:01'));
    expect(!findIsland(one, 'report-concurs'), 'no concurs island after a save with no concurs');
    const e2 = [add(A.finding, 'Notes only.', '2026-09-24 20:00'), concur(A.ask2, '2026-09-24 20:02')];
    await applyEdits(p.page, e2.slice(1));
    const { bytes: two } = await saveIntoFile(p.page, R('20:03'));
    await p.ctx.close();
    const plan = planWrite(original, e2, { anchors, label: LABEL, concurSupport: 'supported', rev: R('20:03') });
    const ni = findIsland(two, 'report-notes'), ci = findIsland(two, 'report-concurs');
    expect(ci && ci.tagStart === ni.closeEnd, 'with a concur, the island goes straight after the notes island\'s </script>');
    expect(el(two, 'report-concurs') === el(plan.out, 'report-concurs'), 'and equals the reference writer\'s', trunc(el(two, 'report-concurs')));
  });

// ---------------------------------------------------------------------------------------
const b = await launch();
console.log(`notes.js under test: ${rev ? rev : 'assets/notes.js (working tree)'}\n`);
let failed = 0;
for (const [i, t] of TESTS.entries()) {
  const misses = [];
  const expect = (cond, what, detail = '') => { if (!cond) misses.push(detail ? `${what}\n            got ${detail}` : what); };
  try { await t.fn(b, expect); } catch (e) { misses.push('threw: ' + String(e && e.stack || e).split('\n').slice(0, 3).join(' / ')); }
  if (misses.length) failed++;
  console.log(`${misses.length ? 'FAIL' : 'PASS'}  ${i + 1}. ${t.name}`);
  if (misses.length) {
    console.log(`        fails on 250188f because ${t.wrong}`);
    for (const m of misses) console.log(`        - ${m}`);
  }
}
await b.close();
rmSync(DIR, { recursive: true, force: true });
console.log(`\n${TESTS.length - failed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
