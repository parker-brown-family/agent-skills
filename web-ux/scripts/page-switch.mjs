#!/usr/bin/env node
// What does a page switch look like, frame by frame, and does the background hold still through it?
// Loads URL, clicks --click (a same-site link), scrolls, then reloads. Records the screen as JPEG frames with every
// stylesheet's animation-duration multiplied by --slow, so a 0.55 s view transition spans enough frames to see a snap.
// Prints the background layers (--layer) at each step. Exits 1 if the background changed on the switch or the scroll
// (rule M2), 2 if it could not measure.
//   node page-switch.mjs URL --click 'nav a[href="/b/"]' [--layer '.wall i'] [--out DIR] [--slow 10] [--width 1000 --height 750]
// Needs Playwright with full Chromium. The default headless shell draws nothing during a view transition (see Traps).
import fs from "fs";
const args = process.argv.slice(2), url = args.find((a) => !a.startsWith("--") && !args[args.indexOf(a) - 1]?.startsWith("--"));
const opt = (k, d) => { const i = args.indexOf("--" + k); return i >= 0 ? args[i + 1] : d; };
const click = opt("click"), layer = opt("layer", ".wall i"), out = opt("out", "page-switch-frames"), slow = +opt("slow", 10);
if (!url || !click) { console.error("usage: page-switch.mjs URL --click SEL [--layer SEL] [--out DIR] [--slow N] [--width N --height N]"); process.exit(2); }
const { chromium } = await import(process.env.PLAYWRIGHT || "playwright");
const b = await chromium.launch({ channel: "chromium", args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--enable-gpu"] });
const ctx = await b.newContext({ viewport: { width: +opt("width", 1000), height: +opt("height", 750) }, colorScheme: "dark" });
const p = await ctx.newPage(); const errs = []; p.on("pageerror", (e) => errs.push(e.message));
if (slow !== 1) await p.route(/\.css(\?|$)/, async (r) => {
  const res = await r.fetch(), t = (await res.text()).replace(/animation-duration:\s*([\d.]+)(m?s)/g, (_, n, u) => `animation-duration: ${+n * slow}${u}`);
  await r.fulfill({ response: res, body: t, headers: { ...res.headers(), "content-type": "text/css" } });
});
fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
const cdp = await ctx.newCDPSession(p); let n = 0, t0 = 0, step = "load";
cdp.on("Page.screencastFrame", async (f) => {
  t0 ||= f.metadata.timestamp;
  fs.writeFileSync(`${out}/${String(n++).padStart(3, "0")}-${Math.round((f.metadata.timestamp - t0) * 1000)}ms-${step}.jpg`, Buffer.from(f.data, "base64"));
  await cdp.send("Page.screencastFrameAck", { sessionId: f.sessionId }).catch(() => {});
});
const bg = () => p.evaluate((s) => [...document.querySelectorAll(s)].filter((l) => +getComputedStyle(l).opacity > 0.5).map((l) => getComputedStyle(l).backgroundImage.replace(/^.*\/|["')]+$/g, "")).join("+") || null, layer);
try { await p.goto(url, { waitUntil: "networkidle" }); } catch (e) { console.error("could not load " + url + ": " + e.message.split("\n")[0]); await b.close(); process.exit(2); }
await p.waitForTimeout(5000);
await cdp.send("Page.startScreencast", { format: "jpeg", quality: 60, everyNthFrame: 2 });
const seen = [["loaded", await bg()]];
step = "switch"; await p.click(click); await p.waitForTimeout(150); seen.push(["switch +0.15s", await bg()]); await p.waitForTimeout(1500 * slow / 2);
step = "scroll"; await p.mouse.wheel(0, 2500); await p.waitForTimeout(1500); seen.push(["scrolled", await bg()]);
step = "reload"; await p.reload({ waitUntil: "networkidle" }); await p.waitForTimeout(6000); seen.push(["reloaded +6s", await bg()]);
await cdp.send("Page.stopScreencast").catch(() => {}); await b.close();
for (const [k, v] of seen) console.log(`${k.padEnd(14)} ${v ?? "(no layer fully visible)"}`);
console.log(`${n} frames in ${out}/  (montage: ffmpeg -pattern_type glob -i '${out}/*.jpg' -vf "scale=400:-1,tile=4x6" -frames:v 1 sheet.jpg)`);
if (errs.length) console.log("page errors:", errs.join(" | "));
if (!seen[0][1]) { console.error(`no visible ${layer} after load: nothing to compare`); process.exit(2); }
const held = seen[1][1] === seen[0][1] && seen[2][1] === seen[0][1];
console.log(held ? "background held through the switch and the scroll" : "CHANGED: the background moved with navigation or scrolling (rule M2)");
process.exit(held ? 0 : 1);
