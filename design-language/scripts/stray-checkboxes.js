// Toggles, never checkboxes. Part of the design-language skill (MIT).
// Run it in any rendered screen, for example from Playwright:
//   const strays = await page.evaluate(`(${strayCheckboxes})()`)   // [] means the screen passes
// It returns every visible checkbox: an <input type="checkbox">, anything with role="checkbox" or
// "menuitemcheckbox", and any role="switch" not drawn as the family's toggle (.hw-toggle).
function strayCheckboxes() {
  const where = (el) => {
    const parts = [];
    for (let e = el; e && e.nodeType === 1 && parts.length < 4; e = e.parentElement) {
      parts.unshift(e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.classList.length ? '.' + [...e.classList].slice(0, 2).join('.') : ''));
    }
    return parts.join(' > ');
  };
  const label = (el) => (el.getAttribute('aria-label') || (el.labels && el.labels[0] && el.labels[0].textContent) ||
    (el.closest('label') && el.closest('label').textContent) || '').trim().slice(0, 60);
  const shown = (el) => {
    const cs = getComputedStyle(el);
    return !(cs.display === 'none' || cs.visibility === 'hidden') && (el.getClientRects().length || el.type === 'checkbox');
  };
  const out = [];
  document.querySelectorAll('input[type="checkbox"], [role="checkbox"], [role="menuitemcheckbox"], [role="switch"]').forEach((el) => {
    if (el.matches('[role="switch"].hw-toggle')) return;
    if (el.matches('input[type="checkbox"][hidden], input[type="checkbox"][aria-hidden="true"]') && !el.getClientRects().length) return;
    if (!shown(el)) return;
    out.push({ what: el.matches('[role="switch"]') ? 'a switch not drawn as .hw-toggle' : 'a checkbox', label: label(el), where: where(el) });
  });
  return out;
}
if (typeof module !== 'undefined') module.exports = { strayCheckboxes };
