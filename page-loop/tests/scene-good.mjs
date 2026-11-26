// A full turn and a label that cycles: periodic in t, so the loop closes.
export const url = new URL('./demo.html', import.meta.url).href;
export const viewport = { width: 400, height: 260 };
export const clip = '#stage';
export async function frame(page, t) { await page.evaluate((t) => draw(2 * Math.PI * t, ['one', 'two', 'three'][Math.floor((t % 1) * 3)]), t); }
