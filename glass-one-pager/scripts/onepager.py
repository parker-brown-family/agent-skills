#!/usr/bin/env python3
"""A one-page PDF drawn as a terminal window: a sidebar of projects beside a curved-glass screen, over a wallpaper.

    onepager.py new DIR                         start a page: writes DIR/content.json to fill in
    onepager.py build CONTENT [--theme T]       write the .html and .pdf (and a .png if pdftoppm is installed) beside it
    onepager.py check CONTENT                   compare each GitHub pull request's mark with its real state (needs gh)
    onepager.py themes                          list the themes that ship with the skill
    onepager.py theme NAME --wallpaper IMG      start a theme of your own from an image (needs ImageMagick)

Python's standard library only. Building the PDF needs Chrome or Chromium ($CHROME picks one).
Exit status: 0 done, 1 the page or the content is wrong and says where, 2 a tool it needs is missing.
"""
import argparse
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

SKILL = pathlib.Path(__file__).resolve().parent.parent
THEMES = SKILL / "themes"
FONTS = SKILL / "assets" / "fonts"
W, H = 1920, 1200
E = lambda s: html.escape(str(s), quote=True)
ADVANCE = 0.6  # JetBrains Mono: every character is 0.6 of the type size wide


class Problem(Exception):
    """Something the author has to change. Printed, exit 1."""


# ---------------------------------------------------------------- content and theme

URL = re.compile(r"^(https?://[^\s\"'<>]+|mailto:[^\s\"'<>]+)$")
LOCAL = re.compile(r"^https?://(localhost(?=[:/]|$)|(127|10)(\.\d+){3}|192\.168(\.\d+){2}|172\.(1[6-9]|2\d|3[01])(\.\d+){2}|\[::1\]|[^/:]*\.(local|localhost|test)(?=[:/]|$))", re.I)
PERSONAL = [("an email address", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")), ("a phone number", re.compile(r"(?<!\w)\+?1?[ .-]?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\w)")),
            ("a home directory path", re.compile(r"(/home/|/Users/|C:\\Users\\)\w+"))]


HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, node


def load_content(path):
    try:
        c = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise Problem(f"{path} does not exist")
    except json.JSONDecodeError as e:
        raise Problem(f"{path} is not JSON: {e}")
    wrong = [f"missing: {k}" for k in ("name", "title", "states", "projects") if not c.get(k)]
    if wrong:
        raise Problem("\n".join(wrong))
    for i, p in enumerate(c["projects"]):
        wrong += [f"projects[{i}] missing: {k}" for k in ("name", "why") if not p.get(k)]
        if p.get("colour") and not HEX.match(p["colour"]):
            wrong.append(f"projects[{i}].colour: {p['colour']!r} is not a hex colour")
        for j, it in enumerate(p.get("items", [])):
            if it.get("state") not in c["states"]:
                wrong.append(f"projects[{i}].items[{j}]: state {it.get('state')!r} is not one of {sorted(c['states'])}")
            if not it.get("text"):
                wrong.append(f"projects[{i}].items[{j}] missing: text")
    for where, v in walk(c):
        if not isinstance(v, str):
            continue
        if where.endswith(".url") or where == "url":
            if v and (not URL.match(v) or LOCAL.match(v)):
                wrong.append(f"{where}: {v!r} is not a public http(s) or mailto link")
        if re.search(r"<[a-z][^>]*>|\bTODO\b", v):
            wrong.append(f"{where}: placeholder left in: {v[:50]!r}")
        if not c.get("contact_is_public"):
            for what, rx in PERSONAL:
                if rx.search(v) and not v.startswith("mailto:"):
                    wrong.append(f"{where}: holds {what}. Take it out, or set contact_is_public to true")
    if not c.get("contact_is_public") and any(isinstance(v, str) and v.startswith("mailto:") for _, v in walk(c)):
        wrong.append("a mailto: link publishes an address. Take it out, or set contact_is_public to true")
    if wrong:
        raise Problem("\n".join(wrong))
    return c


def load_theme(name):
    p = pathlib.Path(name)
    p = p if p.suffix == ".json" else THEMES / f"{name}.json"
    if not p.exists():
        raise Problem(f"no theme {name!r}. Run: onepager.py themes")
    t = json.loads(p.read_text(encoding="utf-8"))
    for k in ("wallpaper", "wallpaper_blurred"):
        f = (p.parent / t[k]).resolve()
        if not f.exists():
            raise Problem(f"{p.name}: {k} {t[k]!r} does not exist")
        t[k] = f
    bad = [k for k, v in t["colours"].items() for x in (v if isinstance(v, list) else [v]) if not HEX.match(x)]
    if bad:
        raise Problem(f"{p.name}: not hex colours: {sorted(set(bad))}")
    return t


# ---------------------------------------------------------------- drawing

class Page:
    def __init__(self, theme):
        self.t, self.c, self.g = theme, theme["colours"], theme["glass"]
        self.defs, self.links, self.n = [], [], 0

    def id(self, k):
        self.n += 1
        return f"{k}{self.n}"

    def link(self, x, y, w, h, url):
        if url:
            self.links.append(f'<a href="{E(url)}" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px"></a>')

    def ui(self, x, y, s, size, fill, weight=400, extra=""):
        return f'<text class="ui" x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" {extra}>{E(s)}</text>'

    def arc(self, x, y, w, k, spans, fs):
        """One line of text set along its own curve. It stays vector, so it stays sharp and selectable."""
        i = self.id("p")
        self.defs.append(f'<path id="{i}" d="M{x:.1f},{y-k:.1f} Q{x+w/2:.1f},{y+k:.1f} {x+w:.1f},{y-k:.1f}"/>')
        t = "".join(f'<tspan fill="{c}" stroke="{c}">{E(s)}</tspan>' for s, c in spans)
        return f'<text class="mono" font-size="{fs}"><textPath href="#{i}">{t}</textPath></text>'

    def tube(self, x, y, w, h, colour):
        g, b, r = self.g, min(w, h) * self.g["bulge"], min(w, h) * self.g["corner"]
        d = (f"M{x+r},{y} Q{x+w/2},{y-b} {x+w-r},{y} Q{x+w},{y} {x+w},{y+r} Q{x+w+b},{y+h/2} {x+w},{y+h-r} "
             f"Q{x+w},{y+h} {x+w-r},{y+h} Q{x+w/2},{y+h+b} {x+r},{y+h} Q{x},{y+h} {x},{y+h-r} Q{x-b},{y+h/2} {x},{y+r} Q{x},{y} {x+r},{y} Z")
        c, dark = self.id("c"), self.c["shade"]
        self.defs += [f'<clipPath id="{c}"><path d="{d}"/></clipPath>',
                      f'<radialGradient id="{c}v" cx=".5" cy=".5" r=".72"><stop offset="0" stop-color="{colour}" stop-opacity="{g["phosphor"]}"/>'
                      f'<stop offset=".6" stop-color="{dark}" stop-opacity="{g["smoke"]}"/><stop offset="1" stop-color="{self.c["edge"]}" stop-opacity="{g["vignette"]}"/></radialGradient>']
        box = f'x="{x-b}" y="{y-b}" width="{w+2*b}" height="{h+2*b}"'
        glow = "".join(f'<path d="{d}" fill="none" stroke="{colour}" stroke-opacity="{o}" stroke-width="{s}"/>' for s, o in ((26, .05), (16, .08), (8, .16)))
        return (f'{glow}<g clip-path="url(#{c})"><image href="{self.t["wallpaper_blurred"].as_uri()}" width="{W}" height="{H}" preserveAspectRatio="none"/>'
                f'<rect {box} fill="{dark}" fill-opacity="{g["tint"]}"/><rect {box} fill="url(#{c}v)"/><rect {box} fill="url(#scan)"/>'
                f'<ellipse cx="{x+w*.26}" cy="{y-h*.04}" rx="{w*.5}" ry="{h*.26}" fill="url(#glare)"/></g>'
                f'<path d="{d}" fill="none" stroke="{self.c["edge"]}" stroke-width="7"/><path d="{d}" fill="none" stroke="{colour}" stroke-opacity=".85" stroke-width="1.8"/>')

    def panel(self, x, y, w, h):
        c = self.id("c")
        self.defs.append(f'<clipPath id="{c}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/></clipPath>')
        return (f'<g clip-path="url(#{c})"><image href="{self.t["wallpaper_blurred"].as_uri()}" width="{W}" height="{H}" preserveAspectRatio="none"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{self.c["panel"]}" fill-opacity="{self.g["panel_tint"]}"/></g>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="{self.c["line"]}" stroke-width="1.5"/>')


def wrap(s, n):
    out, cur = [], ""
    for w in s.split():
        if cur and len(cur) + len(w) + 1 > n:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return out + [cur]


def colour_of(theme, i, p):
    cs = theme["colours"]["projects"]
    return p.get("colour") or cs[i % len(cs)]


def sidebar(pg, c, x, y, w, h):
    """Every project and what was done in it, shrunk together until all of it fits."""
    col, projects, closed = pg.c, c["projects"], c.get("closed", [])
    rows, heads = sum(len(p.get("items", [])) for p in projects), len(projects)
    for fs in [15.5 - .25 * i for i in range(22)]:
        lead = fs * 1.71
        if 76 + heads * (lead + 8) + rows * (lead - 2.5) + len(closed) * (lead + 5) <= h - 10:
            break
    else:
        raise Problem(f"the sidebar holds {heads} projects and {rows} items, more than fit at a readable size. Cut some, or move projects to closed")
    out = pg.panel(x, y, w, h)
    label = c.get("sidebar", "PROJECTS")
    out += f'<rect x="{x+18}" y="{y+16}" width="{24+len(label)*9.4:.0f}" height="26" rx="3" fill="{col["accent"]}" fill-opacity=".16" stroke="{col["accent"]}"/>' + pg.ui(x + 30, y + 34, label, 13, col["accent"], extra='letter-spacing=".6"')
    yy, room = y + 76, w - 100
    for i, p in enumerate(projects):
        out += pg.ui(x + 18, yy, "▼", 12, col["dim"]) + f'<circle cx="{x+44}" cy="{yy-5}" r="5" fill="{colour_of(pg.t, i, p)}"/>' + pg.ui(x + 58, yy, p["name"].upper(), fs + 1, col["bright"], 600, 'letter-spacing=".4"')
        pg.link(x + 14, yy - 18, w - 30, 24, p.get("url"))
        yy += lead
        for it in p.get("items", []):
            st = c["states"][it["state"]]
            if len(it["text"]) * (fs - 1.5) * .53 > room:
                raise Problem(f'sidebar line too long, shorten it: {it["text"]!r}')
            out += f'<rect x="{x+48}" y="{yy-13:.1f}" width="2" height="16" fill="{col["line"]}"/>' + pg.ui(x + 60, yy, it["text"], fs - 1.5, col["text"], extra='fill-opacity=".9"')
            out += f'<text class="mono" x="{x+w-32}" y="{yy:.1f}" font-size="14" fill="{col[st["colour"]]}">{E(st["mark"])}</text>'
            pg.link(x + 48, yy - 16, w - 62, 22, it.get("url"))
            yy += lead - 2.5
        yy += 8
    for i, p in enumerate(closed):
        out += pg.ui(x + 18, yy, "▶", 12, col["dim"]) + f'<circle cx="{x+44}" cy="{yy-5}" r="5" fill="{colour_of(pg.t, i + heads, p)}"/>' + pg.ui(x + 58, yy, p["name"].upper(), fs + 1, col["bright"], 600, 'letter-spacing=".4"')
        pg.link(x + 14, yy - 20, w - 30, 28, p.get("url"))
        yy += lead + 5
    return out


def screen_lines(pg, c, n):
    col, L = pg.c, []
    for i, p in enumerate(c["projects"]):
        L.append(([("❯ ", colour_of(pg.t, i, p)), (p["name"].lower(), col["bright"]), (f'   {p.get("by", "")}', col["dim"])], p.get("url")))
        L += [([("  " + s, col["text"])], None) for s in wrap(p["why"], n - 2)]
        if p.get("love"):
            L += [([("  ♥  " if j == 0 else "     ", col["heart"]), (s, col["heart_text"])], None) for j, s in enumerate(wrap(p["love"], n - 5))]
        L.append(([], None))
    if c.get("prompt"):
        L.append(([("❯ ", col["accent"]), (c["prompt"] + " ", col["bright"]), ("█", col["accent"])], None))
    return L


def screen(pg, c, x, y, w, h):
    """The curved glass. The type is as large as the words allow."""
    pad, top, foot = w * .081, h * .097, h * .02
    for fs in [24 - .5 * i for i in range(27)]:
        n, lead = int((w - 2 * pad) / (fs * ADVANCE)), fs * 1.705
        L = screen_lines(pg, c, n)
        if sum(lead if s else lead * .55 for s, _ in L) <= h - top - foot:
            break
    else:
        raise Problem("the screen holds more words than fit at a readable size. Shorten why and love, or show fewer projects")
    out, yy, edges = pg.tube(x, y, w, h, pg.c["accent"]), y + top, []
    for spans, url in L:
        if spans:
            v = (yy - (y + h / 2)) / (h / 2)
            out += pg.arc(x + pad, yy, w - 2 * pad, v * h * pg.g["bend"], spans, fs)
            wide = sum(len(s) for s, _ in spans) * fs * ADVANCE
            edges.append((yy, x + pad + wide))
            pg.link(x + pad, yy - fs * 1.05, wide, fs * 1.4, url)
        yy += lead if spans else lead * .55
    return out, edges, fs


def note(pg, n, x, y, w, h):
    rows = [n["title"]] + n.get("lines", [])
    t = "".join(f'<text class="hand" x="{x+24}" y="{y+50+i*34}" font-size="{33 if i == 0 else 28}" fill="{pg.c["note_ink"]}">{E(s)}</text>' for i, s in enumerate(rows))
    return (f'<g transform="rotate(4 {x+w/2} {y+h/2})"><rect x="{x+7}" y="{y+9}" width="{w}" height="{h}" fill="#000" fill-opacity=".35"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{pg.c["note"]}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#paper)"/>{t}</g>')


def place_note(n, edges, x, y, w, h):
    """Where the sticky note covers no words: the first height, from the middle out, whose lines all end left of it."""
    rows = [n["title"]] + n.get("lines", [])
    nw, nh = max(len(rows[0]) * 18, max((len(s) for s in rows[1:]), default=0) * 12.2) + 54, 70 + 34 * len(rows)
    nx, mid = x + w - nw - 44, y + h * .42
    for d in range(0, int(h * .40), 12):
        for ny in (mid - d, mid + d):
            if y + 40 <= ny <= y + h - nh - 60 and not any(ny - 24 < ey < ny + nh + 24 and ex > nx - 18 for ey, ex in edges):
                return nx, ny, nw, nh
    raise Problem("no room for the note without covering words. Shorten a line on the screen, or take the note out")


def draw(c, theme):
    pg, col = Page(theme), theme["colours"]
    lost = sorted({st["colour"] for st in c["states"].values()} - set(col))
    if lost:
        raise Problem(f"states use colours the theme does not have: {lost}")
    q = "".join(f'<rect x="{34+dx}" y="{28+dy}" width="11" height="11" rx="2" fill="{k}"/>' for dx, dy, k in zip((0, 13, 0, 13), (0, 0, 13, 13), col["projects"]))
    b = (f'<rect x="8" y="8" width="{W-16}" height="{H-16}" rx="12" fill="none" stroke="{col["accent"]}" stroke-opacity=".75" stroke-width="3"/>'
         f'<rect x="8" y="8" width="{W-16}" height="60" rx="12" fill="{col["panel"]}" fill-opacity=".55"/>{q}' + pg.ui(76, 47, c["name"], 21, col["bright"], 600)
         + pg.ui(76 + len(c["name"]) * 11.6 + 18, 47, c["title"], 17, col["dim"]))
    xx = W - 44
    for l in reversed(c.get("links", [])):
        wd = len(l["label"]) * 8.5
        xx -= wd
        b += pg.ui(xx, 46, l["label"], 16, col["link"])
        pg.link(xx - 8, 22, wd + 16, 34, l.get("url"))
        xx -= 46
    b += sidebar(pg, c, 24, 88, 428, 1050)
    b += (f'<rect x="470" y="88" width="1426" height="1050" fill="{col["edge"]}" fill-opacity="{theme["glass"]["frame_tint"]}" stroke="{col["accent"]}" stroke-width="4"/>'
          + pg.ui(494, 124, "▸ " + c.get("heading", "").upper(), 18, col["good"]) + pg.ui(1820, 124, "live", 17, col["good"]))
    s, edges, fs = screen(pg, c, 500, 160, 1366, 946)
    b += s
    if c.get("note"):
        b += note(pg, c["note"], *place_note(c["note"], edges, 500, 160, 1366, 946))
    x = 500
    for st in c["states"].values():
        b += f'<text x="{x:.0f}" y="1172" font-size="15" class="mono" fill="{col[st["colour"]]}">{E(st["mark"])} <tspan fill="{col["dim"]}">{E(st["means"])}</tspan></text>'
        x += 36 + len(st["means"]) * 9.4
    g = theme["glass"]
    d = (f'<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.6" fill="#000" fill-opacity="{g["scanlines"]}"/></pattern>'
         f'<radialGradient id="glare"><stop offset="0" stop-color="{col["glare"]}" stop-opacity="{g["glare"]}"/><stop offset="1" stop-color="{col["glare"]}" stop-opacity="0"/></radialGradient>'
         '<linearGradient id="paper" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset="1" stop-color="#000" stop-opacity=".22"/></linearGradient>')
    face = lambda n, f, w: f'@font-face{{font-family:{n};src:url({(FONTS/f).as_uri()});font-weight:{w}}}'
    css = (f'@page{{size:{W}px {H}px;margin:0}}*{{box-sizing:border-box}}html,body{{margin:0;background:{col["edge"]};-webkit-print-color-adjust:exact;print-color-adjust:exact}}'
           + face("OnePagerUI", "inter-latin.woff2", "100 900") + face("OnePagerMono", "jetbrains-mono-latin.woff2", "100 800") + face("OnePagerHand", "Caveat-Variable.ttf", "400 700")
           + f'.page{{position:relative;width:{W}px;height:{H}px;overflow:hidden}}svg{{position:absolute;inset:0}}.page a{{position:absolute;display:block}}'
             '.mono{font-family:OnePagerMono,"JetBrainsMono Nerd Font","DejaVu Sans Mono",monospace;font-weight:400;white-space:pre}.mono tspan{stroke-opacity:.22;stroke-width:2.4;paint-order:stroke}'
             '.ui{font-family:OnePagerUI,sans-serif}.hand{font-family:OnePagerHand,cursive;font-weight:600}')
    page = (f'<!DOCTYPE html><html lang="{E(c.get("lang", "en"))}"><head><meta charset="utf-8"><title>{E(c["name"])} — {E(c["title"])}</title><style>{css}</style></head><body><div class="page">'
            f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg"><defs>{d}{"".join(pg.defs)}</defs><image href="{theme["wallpaper"].as_uri()}" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>'
            f'<rect width="{W}" height="{H}" fill="{col["shade"]}" fill-opacity="{g["wallpaper_dim"]}"/>{b}</svg>{"".join(pg.links)}</div></body></html>')
    return page, {"type": fs, "links": len(pg.links)}


# ---------------------------------------------------------------- commands

def chrome():
    for n in filter(None, [os.environ.get("CHROME"), "google-chrome-stable", "google-chrome", "chromium", "chromium-browser"]):
        if shutil.which(n):
            return n
    print("onepager: needs Chrome or Chromium (set CHROME to its name)", file=sys.stderr)
    sys.exit(2)


def build(a):
    src = pathlib.Path(a.content).resolve()
    c = load_content(src)
    page, info = draw(c, load_theme(a.theme or c.get("theme", "deep-quiet")))
    out = pathlib.Path(a.out).resolve() if a.out else src.with_name(c.get("file", src.stem))
    h, p = out.with_suffix(".html"), out.with_suffix(".pdf")
    h.write_text(page, encoding="utf-8")
    p.unlink(missing_ok=True)
    subprocess.run([chrome(), "--headless=new", "--no-pdf-header-footer", "--allow-file-access-from-files", f"--print-to-pdf={p}", h.as_uri()], capture_output=True)
    if not p.exists():
        raise Problem("the browser wrote no PDF")
    if shutil.which("pdfinfo"):
        m = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True).stdout)
        if not m or m[1] != "1":
            raise Problem(f"the PDF is {m[1] if m else 'an unknown number of'} pages, and has to be one")
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-r", "96", "-png", "-singlefile", str(p), str(out)], capture_output=True)
    print(f"{p}\n  one page, {info['links']} links, screen type {info['type']}px. Open it and look before you send it.")


def check(a):
    """Open on GitHub must be marked open; merged must not be. A pull request that cannot be read is reported, never passed."""
    c = load_content(a.content)
    if not shutil.which("gh"):
        print("onepager: check needs the GitHub CLI (gh)", file=sys.stderr)
        sys.exit(2)
    stale = unread = seen = 0
    for p in c["projects"]:
        for it in p.get("items", []):
            m = re.fullmatch(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)/?", it.get("url") or "")
            if not m:
                continue
            seen += 1
            r = subprocess.run(["gh", "pr", "view", m[2], "-R", m[1], "--json", "state", "-q", ".state"], capture_output=True, text=True)
            real, want = r.stdout.strip(), c["states"][it["state"]].get("pull_request")
            word = "UNREAD" if not real else "UNMAPPED" if want is None else "ok" if real == want else "STALE"
            unread += word in ("UNREAD", "UNMAPPED")
            stale += word == "STALE"
            print(f"{word:9}{it['state']:10}{real or '?':8}{p['name']}: {it['text']}")
    print(f"{seen} pull requests: {stale} stale, {unread} could not be judged")
    sys.exit(1 if stale or unread else 0)


def new(a):
    d = pathlib.Path(a.dir)
    d.mkdir(parents=True, exist_ok=True)
    f = d / "content.json"
    if f.exists():
        raise Problem(f"{f} is already there")
    shutil.copy(SKILL / "templates" / "content.json", f)
    print(f"{f}\n  fill it in, then: onepager.py build {f}")


def themes(_):
    for f in sorted(THEMES.glob("*.json")):
        print(f"{f.stem:16}{json.loads(f.read_text(encoding='utf-8')).get('about', '')}")


def theme(a):
    im = shutil.which("magick") or shutil.which("convert")
    if not im:
        print("onepager: theme needs ImageMagick", file=sys.stderr)
        sys.exit(2)
    d = pathlib.Path(a.dir)
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{a.name}.json"
    if f.exists():
        raise Problem(f"{f} is already there")
    t = json.loads((THEMES / f"{a.base}.json").read_text(encoding="utf-8"))
    wall, blur = d / f"{a.name}.jpg", d / f"{a.name}-blur.jpg"
    subprocess.run([im, a.wallpaper, "-resize", f"{W}x{H}^", "-gravity", "center", "-extent", f"{W}x{H}", "-quality", "88", str(wall)], check=True)
    subprocess.run([im, str(wall), "-blur", "0x7", "+level", "0,62%", "-quality", "82", str(blur)], check=True)
    t.update(name=a.name, about=f"Made from {a.base}. Say who made the wallpaper and under what licence.", wallpaper=wall.name, wallpaper_blurred=blur.name)
    f.write_text(json.dumps(t, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{f}\n  change its colours to suit the picture, then: onepager.py build CONTENT --theme {f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = ap.add_subparsers(dest="cmd", required=True)
    p = s.add_parser("new"); p.add_argument("dir"); p.set_defaults(f=new)
    p = s.add_parser("build"); p.add_argument("content"); p.add_argument("--theme"); p.add_argument("--out"); p.set_defaults(f=build)
    p = s.add_parser("check"); p.add_argument("content"); p.set_defaults(f=check)
    p = s.add_parser("themes"); p.set_defaults(f=themes)
    p = s.add_parser("theme"); p.add_argument("name"); p.add_argument("--wallpaper", required=True); p.add_argument("--base", default="deep-quiet"); p.add_argument("--dir", default="."); p.set_defaults(f=theme)
    a = ap.parse_args()
    try:
        a.f(a)
    except Problem as e:
        print(f"onepager: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
