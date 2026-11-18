// No number is ever set in the frame face (the example: Federo). Part of the design-language skill.
// Run it in any rendered screen, for example from Playwright:
//   const offenders = await page.evaluate(`(${frameDigits})()`)   // [] means the screen passes
// It returns each piece of visible text whose element is set in Federo and which holds a
// character a number is made of: a digit, a currency or number sign. (The separators , . : / are
// left out here because titles use them; the unicode-range on Federo's @font-face hands them to
// DM Sans anyway.) A number that reaches a frame string is an authoring mistake even where the
// unicode-range draws it in DM Sans, so this fails on it.
function frameDigits(frameFamily = /federo/i) {
  const NUM = /[0-9#$%+=¢-¥°-³¹¼-¾×÷‰′″⁄−₠-⃏]/;
  const where = (el) => {
    const parts = [];
    for (let e = el; e && e.nodeType === 1 && parts.length < 4; e = e.parentElement) {
      parts.unshift(e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.classList.length ? '.' + [...e.classList].slice(0, 2).join('.') : ''));
    }
    return parts.join(' > ');
  };
  const bad = [];
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walk.nextNode(); n; n = walk.nextNode()) {
    if (!NUM.test(n.nodeValue)) continue;
    const el = n.parentElement;
    if (!el || el.closest('script, style, template')) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || !el.getClientRects().length) continue;
    const first = cs.fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, '');
    if (frameFamily.test(first)) bad.push({ text: n.nodeValue.trim().slice(0, 60), family: first, where: where(el) });
  }
  return bad;
}
if (typeof module !== 'undefined') module.exports = { frameDigits };
