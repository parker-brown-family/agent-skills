// The classic off-by-one: t runs 0..1 inclusive, so the last frame is the first again and the loop stutters.
export const url = new URL('./demo.html', import.meta.url).href;
export const viewport = { width: 400, height: 260 };
export const clip = '#stage';
const N = +(process.env.FRAMES || 24);
export async function frame(page, t, i) { const u = i / (N - 1); await page.evaluate((u) => draw(2 * Math.PI * u, 'one'), u); }
