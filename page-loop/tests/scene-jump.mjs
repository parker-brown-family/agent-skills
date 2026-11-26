// Half a turn of an asymmetric shape: the loop does not close, so it jumps at the seam.
export const url = new URL('./demo.html', import.meta.url).href;
export const viewport = { width: 400, height: 260 };
export const clip = '#stage';
export async function frame(page, t) { await page.evaluate((t) => draw(Math.PI * t, 'one'), t); }
