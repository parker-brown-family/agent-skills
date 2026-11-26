#!/usr/bin/env node
// Does an overlay hold still while someone types into it? Opens it, types each query, and records the top edge of the
// input and of the box after each. Exits 1 if either moved more than 1 px, 2 if it could not measure (no box, no input).
//   node hold-still.mjs URL [--open Control+k] [--input '#q'] [--box '#find'] [--type 'p,pe,peking'] [--width 1280 --height 900]
// Needs Playwright. Set PLAYWRIGHT to its index.mjs if `import('playwright')` does not resolve from here.
const args = process.argv.slice(2), url = args.find((a) => !a.startsWith("--") && !args[args.indexOf(a) - 1]?.startsWith("--"));
const opt = (k, d) => { const i = args.indexOf("--" + k); return i >= 0 ? args[i + 1] : d; };
if (!url) { console.error("usage: hold-still.mjs URL [--open KEY] [--input SEL] [--box SEL] [--type a,b,c] [--width N --height N]"); process.exit(2); }
const { chromium } = await import(process.env.PLAYWRIGHT || "playwright");
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: +opt("width", 1280), height: +opt("height", 900) } });
const errs = []; p.on("pageerror", (e) => errs.push(e.message));
const input = opt("input", "#q"), box = opt("box", "#find");
try { await p.goto(url, { waitUntil: "networkidle" }); } catch (e) { console.error("could not load " + url + ": " + e.message.split("\n")[0]); await b.close(); process.exit(2); }
await p.keyboard.press(opt("open", "Control+k")); await p.waitForTimeout(350);
const at = () => p.evaluate(([i, x]) => { const a = document.querySelector(i), c = document.querySelector(x); return a && c ? [Math.round(a.getBoundingClientRect().top), Math.round(c.getBoundingClientRect().top)] : null; }, [input, box]);
const rows = [["(empty)", await at()]];
for (const q of opt("type", "p,pe,peking").split(",")) { await p.fill(input, q); await p.waitForTimeout(250); rows.push([q, await at()]); }
await b.close();
if (rows.some((r) => !r[1])) { console.error(`could not find ${input} or ${box} after opening with ${opt("open", "Control+k")}`); process.exit(2); }
for (const [q, [i, x]] of rows) console.log(`${q.padEnd(12)} input top ${i}px  box top ${x}px`);
const moved = rows.some(([, r]) => Math.abs(r[0] - rows[0][1][0]) > 1 || Math.abs(r[1] - rows[0][1][1]) > 1);
if (errs.length) console.log("page errors:", errs.join(" | "));
console.log(moved ? "MOVED: the overlay shifts while typing (rule H1)" : "holds still");
process.exit(moved ? 1 : 0);
