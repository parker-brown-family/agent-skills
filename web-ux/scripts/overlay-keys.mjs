#!/usr/bin/env node
// Do the keys reach an overlay the moment it opens, and does focus come back when it closes? Clicks the opener, checks that
// focus is inside the box, presses a scroll key and checks the scroller moved, optionally presses a "next" key and checks
// the scroller came to rest at the target's top, then presses Escape and checks focus is back on the opener.
// Exits 1 if any check fails, 2 if it could not measure (no opener, no box, no scroller).
//   node overlay-keys.mjs URL --click SEL --box SEL --scroller SEL [--key ArrowDown] [--next ArrowRight --target SEL --offset 18]
//     [--wait 2500] [--width 1280 --height 900]
// --target is the element the "next" key should land on (e.g. '.rd-wrap:nth-of-type(2)'); --offset is the gap the page
// leaves above it. Needs Playwright. Set PLAYWRIGHT to its index.mjs if `import('playwright')` does not resolve from here.
const args = process.argv.slice(2), url = args.find((a) => !a.startsWith("--") && !args[args.indexOf(a) - 1]?.startsWith("--"));
const opt = (k, d) => { const i = args.indexOf("--" + k); return i >= 0 ? args[i + 1] : d; };
if (!url || !opt("click") || !opt("box") || !opt("scroller")) { console.error("usage: overlay-keys.mjs URL --click SEL --box SEL --scroller SEL [--key K] [--next K --target SEL --offset N] [--wait MS]"); process.exit(2); }
const { chromium } = await import(process.env.PLAYWRIGHT || "playwright");
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: +opt("width", 1280), height: +opt("height", 900) } });
const errs = [], fails = []; p.on("pageerror", (e) => errs.push(e.message));
const box = opt("box"), sc = opt("scroller"), wait = +opt("wait", 2500);
const done = async (code) => { await b.close(); if (errs.length) console.log("page errors:", errs.join(" | ")); process.exit(code); };
try { await p.goto(url, { waitUntil: "networkidle" }); } catch (e) { console.error("could not load " + url + ": " + e.message.split("\n")[0]); await done(2); }
const opener = await p.$(opt("click")); if (!opener) { console.error("no opener matches " + opt("click")); await done(2); }
await opener.evaluate((x) => { x.dataset.uxOpener = "1"; }); await opener.click(); await p.waitForTimeout(wait);
const state = () => p.evaluate(([bx, s]) => { const B = document.querySelector(bx), S = document.querySelector(s), a = document.activeElement;
  return B && S ? { inside: B.contains(a), focus: a ? (a.id ? "#" + a.id : a.tagName.toLowerCase()) : "none", top: Math.round(S.scrollTop) } : null; }, [box, sc]);
const s0 = await state(); if (!s0) { console.error(`no ${box} or ${sc} after clicking the opener`); await done(2); }
console.log(`opened      focus ${s0.focus} ${s0.inside ? "(inside the box)" : "(OUTSIDE the box)"}  scroll ${s0.top}px`);
if (!s0.inside) fails.push("focus stayed outside the overlay when it opened (rule K6)");
await p.keyboard.press(opt("key", "ArrowDown")); await p.waitForTimeout(400);
const s1 = await state(); console.log(`${opt("key", "ArrowDown").padEnd(11)} scroll ${s1.top}px`);
if (s1.top === s0.top) fails.push(`${opt("key", "ArrowDown")} did not scroll ${sc} (rule K6)`);
if (opt("next")) {
  await p.keyboard.press(opt("next")); await p.waitForTimeout(wait);
  const r = await p.evaluate(([s, t, off]) => { const S = document.querySelector(s), T = document.querySelector(t); return T ? { top: Math.round(S.scrollTop), want: T.offsetTop - off } : null; }, [sc, opt("target"), +opt("offset", 0)]);
  if (!r) { console.error("no target matches " + opt("target")); await done(2); }
  console.log(`${opt("next").padEnd(11)} scroll ${r.top}px, target ${r.want}px`);
  if (Math.abs(r.top - r.want) > 4) fails.push(`${opt("next")} came to rest ${r.top - r.want}px from its target (rule K7)`);
}
await p.keyboard.press("Escape"); await p.waitForTimeout(300);
const back = await p.evaluate(() => document.activeElement?.dataset?.uxOpener === "1");
console.log(`Escape      focus ${back ? "back on the opener" : "NOT back on the opener"}`);
if (!back) fails.push("Escape did not return focus to what opened the overlay (rule K6)");
fails.forEach((f) => console.log("FAIL " + f));
console.log(fails.length ? "the keys do not reach this overlay properly" : "keys reach the overlay, and focus comes home");
await done(fails.length ? 1 : 0);
