/* fancy-pants-brief — the rail of gel buttons that jumps between a page's parts.
   An empty <nav class="sections"> is filled from the page's h2s; a page with three or more
   h2s and no rail gets one, placed after its masthead. A rail someone wrote by hand is left
   alone. Each h2 without an id is given one from its words. */
(function () {
  var heads = [].slice.call(document.querySelectorAll('h2')).filter(function (h) {
    return !h.closest('dialog, nav, figure, .glass');
  });
  var nav = document.querySelector('nav.sections');
  if (nav && nav.children.length) return;
  if (!nav) {
    if (heads.length < 3) return;
    nav = document.createElement('nav');
    nav.className = 'sections';
    var top = document.querySelector('header.top, body > header, .wrap > header, h1');
    var after = top && (top.tagName === 'H1' ? top.parentNode : top);
    if (after && after.parentNode) after.parentNode.insertBefore(nav, after.nextSibling);
    else document.body.insertBefore(nav, document.body.firstChild);
  }
  nav.setAttribute('aria-label', 'Sections');
  var used = {};
  heads.forEach(function (h) {
    var n = h.querySelector('.n');
    if (!h.id) {
      /* "part-07-decide", never "07decide": the number and the words are kept
         apart, and an id that starts with a digit cannot be named as #07decide. */
      var text = (n ? n.textContent + ' ' : '') + (h.textContent || '').replace(n ? n.textContent : '', '');
      var base = 'part-' + (text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 44) || 'x');
      var id = base, i = 2;
      while (used[id] || document.getElementById(id)) id = base + '-' + i++;
      h.id = id;
    }
    used[h.id] = true;
    var a = document.createElement('a');
    a.href = '#' + h.id;
    if (n) { var s = document.createElement('span'); s.className = 'n'; s.textContent = n.textContent.trim(); a.appendChild(s); }
    var words = (h.textContent || '').replace(n ? n.textContent : '', '').trim();
    a.appendChild(document.createTextNode(words.length > 40 ? words.slice(0, 38) + '…' : words));
    nav.appendChild(a);
  });
})();

/* The rail floats. Parker, 2026-11-11: "the nav is annoyingly on TOP of the useful content of
   the page... nav should be on RIGHT side ... add a grip icon ... click dragged anywhere on the
   page and resizable ... default 35% height ... a VERY NICE looking vertical scrollbar (no
   horizontal scrollbar) where mousewheel hover over the nav scrolls the nav and NOT the
   underlying page".
   So the rail is a glass panel docked on the right: a grip bar to move it, corner handles to
   size it, one list that scrolls vertically and keeps the wheel to itself. Where the reader
   leaves it is remembered for every brief in this browser; a double-click on the grip (or Home
   on the focused grip) docks it again. It is built after every DOMContentLoaded handler has run,
   so a rail that briefing's reading.js rebuilds is wrapped once it is final. */
(function () {
  var KEY = 'brief-rail-geometry', MIN_W = 180, MIN_H = 120, EDGE = 8;
  var DOTS = '<svg viewBox="0 0 10 16" width="10" height="16" aria-hidden="true">' + [2, 8].map(function (x) {
    return [2, 8, 14].map(function (y) { return '<circle cx="' + x + '" cy="' + y + '" r="1.6"/>'; }).join('');
  }).join('') + '</svg>';
  function load() { try { return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) { return null; } }
  function save(g) { try { if (g) localStorage.setItem(KEY, JSON.stringify(g)); else localStorage.removeItem(KEY); } catch (e) {} }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  function float(nav) {
    if (!nav || nav.dataset.railFloat || !nav.querySelector('a')) return;
    nav.dataset.railFloat = '1';
    if (nav.parentNode !== document.body) document.body.appendChild(nav);
    var list = document.createElement('div');
    list.className = 'rail-list';
    while (nav.firstChild) list.appendChild(nav.firstChild);
    var grip = document.createElement('div');
    grip.className = 'rail-grip';
    grip.tabIndex = 0;
    grip.setAttribute('role', 'button');
    grip.setAttribute('aria-label', 'Move the sections panel with the mouse or the arrow keys; double-click or press Home to dock it on the right');
    grip.title = 'Drag to move · double-click to dock on the right';
    grip.innerHTML = DOTS + '<span>Sections</span>';
    /* Fold the panel to its grip bar; on a narrow screen it starts folded, so it never sits on the page. */
    var fold = document.createElement('button');
    fold.type = 'button';
    fold.className = 'rail-fold';
    grip.appendChild(fold);
    function folded(on) {
      nav.classList.toggle('rail-folded', on);
      fold.textContent = on ? '+' : '−';
      fold.setAttribute('aria-expanded', String(!on));
      fold.setAttribute('aria-label', on ? 'Show the sections' : 'Fold the sections panel to its title bar');
    }
    var held = null;
    try { held = localStorage.getItem(KEY + ':folded'); } catch (e) {}
    folded(held === null ? innerWidth < 700 : held === '1');
    fold.addEventListener('pointerdown', function (e) { e.stopPropagation(); });
    fold.addEventListener('click', function () {
      var on = !nav.classList.contains('rail-folded');
      folded(on);
      try { localStorage.setItem(KEY + ':folded', on ? '1' : '0'); } catch (e) {}
    });
    var sizers = ['sw', 'se'].map(function (corner) {
      var h = document.createElement('div');
      h.className = 'rail-size rail-size-' + corner;
      h.title = 'Drag to resize';
      h.setAttribute('aria-hidden', 'true');
      return h;
    });
    nav.append(grip, list, sizers[0], sizers[1]);
    nav.classList.add('rail-float');
    /* Stamped elements (notes.js) whose rail links were rebuilt after the stamp went on. */
    [].forEach.call(list.querySelectorAll('a[href^="#"]'), function (a) {
      var id = decodeURIComponent(a.getAttribute('href').slice(1));
      var el = document.getElementById(id) || document.querySelector('[data-nid="' + id.replace(/"/g, '') + '"]');
      if (el && el.classList.contains('has-concur')) a.classList.add('has-concur');
    });
    document.documentElement.classList.add('has-floating-rail');

    /* Anything later appended straight to the rail joins the list, not the frame. */
    new MutationObserver(function (changes) {
      changes.forEach(function (c) {
        [].forEach.call(c.addedNodes, function (n) {
          if (n !== grip && n !== list && sizers.indexOf(n) < 0 && n.parentNode === nav) list.appendChild(n);
        });
      });
    }).observe(nav, { childList: true });

    function apply(g) {
      document.documentElement.classList.toggle('rail-docked', !g);
      if (!g) { nav.style.left = nav.style.top = nav.style.width = nav.style.height = ''; nav.style.right = ''; return; }
      var w = clamp(g.w, MIN_W, innerWidth - 2 * EDGE), h = clamp(g.h, MIN_H, innerHeight - 2 * EDGE);
      nav.style.width = w + 'px';
      nav.style.height = h + 'px';
      nav.style.left = clamp(g.x, EDGE - w + 64, innerWidth - 64) + 'px';
      nav.style.top = clamp(g.y, EDGE, innerHeight - 40) + 'px';
      nav.style.right = 'auto';
    }
    function current() { var r = nav.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; }
    apply(load());
    addEventListener('resize', function () { var g = load(); if (g) apply(g); });

    /* The wheel over the panel scrolls the panel, never the page beneath it, even when the list
       is too short to scroll (where overscroll-behavior alone would hand the wheel on). */
    nav.addEventListener('wheel', function (e) {
      if (e.ctrlKey) return;  // pinch zoom stays the browser's
      e.preventDefault();
      var unit = e.deltaMode === 1 ? 18 : e.deltaMode === 2 ? list.clientHeight : 1;
      list.scrollTop += (Math.abs(e.deltaY) >= Math.abs(e.deltaX) ? e.deltaY : e.deltaX) * unit;
    }, { passive: false });

    function drag(handle, move) {
      handle.addEventListener('pointerdown', function (e) {
        if (e.button !== 0) return;
        e.preventDefault();
        handle.setPointerCapture(e.pointerId);
        var start = current(), x0 = e.clientX, y0 = e.clientY;
        nav.classList.add('rail-moving');
        function on(ev) { apply(move(start, ev.clientX - x0, ev.clientY - y0)); }
        function off() {
          handle.removeEventListener('pointermove', on);
          handle.removeEventListener('pointerup', off);
          handle.removeEventListener('pointercancel', off);
          nav.classList.remove('rail-moving');
          save(current());
        }
        handle.addEventListener('pointermove', on);
        handle.addEventListener('pointerup', off);
        handle.addEventListener('pointercancel', off);
      });
    }
    drag(grip, function (s, dx, dy) { return { x: s.x + dx, y: s.y + dy, w: s.w, h: s.h }; });
    drag(sizers[0], function (s, dx, dy) { var w = Math.max(MIN_W, s.w - dx); return { x: s.x + s.w - w, y: s.y, w: w, h: s.h + dy }; });
    drag(sizers[1], function (s, dx, dy) { return { x: s.x, y: s.y, w: s.w + dx, h: s.h + dy }; });
    function dock() { save(null); apply(null); }
    grip.addEventListener('dblclick', function (e) { if (e.target !== fold) dock(); });
    grip.addEventListener('keydown', function (e) {
      var step = e.shiftKey ? 64 : 16, d = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] }[e.key];
      if (e.key === 'Home') { e.preventDefault(); dock(); return; }
      if (!d) return;
      e.preventDefault();
      var g = current();
      apply({ x: g.x + d[0], y: g.y + d[1], w: g.w, h: g.h });
      save(current());
    });
  }

  function run() { setTimeout(function () { float(document.querySelector('nav.sections')); }, 0); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run();
  window.BriefRail = { float: float };
})();
