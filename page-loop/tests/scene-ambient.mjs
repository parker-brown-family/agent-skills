// The page's own ambient motion left running on the virtual clock: a drifting dot that never repeats within the loop.
// The seam must still pass (the state closes; the ambient is crossfaded), which it can only do if the dot reads the
// virtual clock, since the closing check resets the clock to frame 0's time.
export const url = new URL('./demo.html', import.meta.url).href;
export const viewport = { width: 400, height: 300 };
export const clock = 'virtual';
export const crossfade = 6;
export async function clip(page) { return page.evaluate(() => { const a = document.getElementById('stage').getBoundingClientRect(), b = document.getElementById('amb').getBoundingClientRect(); return { x: a.left, y: a.top, width: a.width, height: b.bottom - a.top }; }); }
export async function frame(page, t) { await page.evaluate((t) => draw(2 * Math.PI * t, ['one', 'two', 'three'][Math.floor((t % 1) * 3)]), t); }
