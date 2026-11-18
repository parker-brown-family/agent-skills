#!/usr/bin/env python3
"""Turn a product family's Omarchy themes into checked design tokens: tokens.css and tokens.json.

    python3 tokens.py --family FAMILY.py [--out DIR]            write both files, print the checks
    python3 tokens.py --family FAMILY.py [--out DIR] --check    check only: exit 1 on a failed rule or drift
    python3 tokens.py --family FAMILY.py --selftest             restore each OLD_VALUES entry; each must fail
    python3 tokens.py --family FAMILY.py --table                every check row, every derived accent

The family file is Python that sets FAMILY, PREFIX, SOURCES, FIXED, ORDER, OLD_VALUES and BRANDS
(examples/head-waters/family.py is a complete one). The rule and the checks are in
reference/omarchy-colour.md and reference/checks.md. Standard library only (Python 3.11+ for
tomllib, used only to read an installed theme the family file did not record).
Part of the design-language skill: github.com/parker-brown-family/agent-skills. MIT licence.
"""
import json, math, sys
from pathlib import Path

HERE = Path.cwd()
THEME_DIRS = [Path('/usr/share/omarchy/themes'), Path.home() / '.config/omarchy/themes']

# ── colour maths ──────────────────────────────────────────────────────────────
def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def _rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def lum(h):
    r, g, b = (_lin(c) for c in _rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

def _oklab_lin(r, g, b):
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)

def oklab(h):
    return _oklab_lin(*(_lin(c) for c in _rgb(h)))

def oklch(h):
    L, A, B = oklab(h)
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360

def _enc(c):
    c = max(0.0, min(1.0, c))
    v = 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    return round(max(0, min(1, v)) * 255)

def _lin_rgb(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)

def hexof(L, C, H):
    """OKLCH to hex. Out of sRGB, chroma is reduced (never hue or lightness), so the hue holds."""
    lo, hi = 0.0, C
    if not all(-1e-4 <= x <= 1 + 1e-4 for x in _lin_rgb(L, C, H)):
        for _ in range(30):
            mid = (lo + hi) / 2
            if all(-1e-4 <= x <= 1 + 1e-4 for x in _lin_rgb(L, mid, H)):
                lo = mid
            else:
                hi = mid
        C = lo
    r, g, bb = _lin_rgb(L, C, H)
    return '#%02x%02x%02x' % (_enc(r), _enc(g), _enc(bb))

_CVD = {'deutan': ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
        'protan': ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998))}

def cvd_distance(a, b, kind):
    def sim(h):
        v = [_lin(c) for c in _rgb(h)]
        return _oklab_lin(*(max(0.0, min(1.0, sum(row[i] * v[i] for i in range(3)))) for row in _CVD[kind]))
    return 100 * math.dist(sim(a), sim(b))

def lab_distance(a, b):
    return 100 * math.dist(oklab(a), oklab(b))

def mix_white(h, alpha):
    return '#%02x%02x%02x' % tuple(round(alpha * 255 + (1 - alpha) * c) for c in _rgb(h))

def hue_gap(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)

# ── the shared table ──────────────────────────────────────────────────────────
SHARED = {
    # Faces, version 3: Terminal Delight's Deco skin letters its chrome in JetBrains Mono (the
    # desktop's monospace, or TD's shipped default) with tracked capitals for labels. Titles and
    # labels take it; everything a person reads at length or types into takes Inter. Both are
    # SIL Open Font License 1.1. Fraunces is gone.
    'font': {
        'display': 'var(--font-jetbrains-mono, "JetBrains Mono"), ui-monospace, "SF Mono", Menlo, Consolas, monospace',
        'ui': 'var(--font-inter, "Inter"), system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
        'mono': 'var(--font-jetbrains-mono, "JetBrains Mono"), ui-monospace, "SF Mono", Menlo, Consolas, monospace',
    },
    'text': {'xs': [12, 16], 'sm': [14, 20], 'md': [16, 24], 'lg': [20, 28],
             'xl': [24, 32], '2xl': [30, 36], '3xl': [38, 44]},
    'weight': {'regular': 400, 'medium': 500, 'semibold': 600, 'bold': 700},
    'tracking': {'label': 0.12, 'display': 0.0},     # em; Deco's tracked caps for labels only
    'space': {'1': 4, '2': 8, '3': 12, '4': 16, '5': 24, '6': 32, '7': 48, '8': 64},
    'gap': {'tight': 4, 'related': 8, 'group': 16, 'section': 32, 'section-tight': 24},
    'pad': {'card': 24, 'card-phone': 16, 'page': 24, 'page-phone': 16, 'control-x': 16},
    'size': {'target': 44, 'target-android': 48, 'control-dense': 36, 'bar': 56, 'bar-phone': 52,
             'measure': '68ch', 'content-max': 1120, 'rail': 240, 'dock-max': 760},
    'radius': {'control': 8, 'card': 12, 'sheet': 16, 'pill': 999},
    # the folio tab (the selected menu item, joined to the page) and the line under the bar
    'folio': {'radius': 4, 'chip': 10, 'bar': 3},      # radius = card radius / 3, as Parker asked
    'line': {'width': 2},                              # recommended; 3 was drawn beside it
    'motion': {'dur-1': 120, 'dur-2': 200, 'dur-3': 300, 'dur-fade': 100,
               'ease': [0.2, 0, 0, 1], 'ease-exit': [0.3, 0, 1, 1], 'travel-max': 16},
    'focus': {'width': 2, 'offset': 2},
    'glow-live': {'blur': 12, 'alpha': 0.35},
}
# type roles: (step, weight, face, tracking-em, uppercase, tabular)
TYPE = {
    'eyebrow': ('xs', 600, 'display', 0.12, True, False), 'label': ('sm', 600, 'ui', 0, False, False),
    'tab': ('sm', 600, 'display', 0.08, True, False), 'meta': ('sm', 400, 'ui', 0, False, False),
    'body': ('md', 400, 'ui', 0, False, False), 'button': ('md', 600, 'ui', 0, False, False),
    'title-card': ('lg', 600, 'ui', 0, False, False), 'lead': ('lg', 400, 'ui', 0, False, False),
    'title-section': ('xl', 600, 'display', 0, False, False), 'title-page': ('2xl', 600, 'display', 0, False, False),
    'display': ('3xl', 600, 'display', 0, False, False), 'figure': ('3xl', 600, 'display', 0, False, True),
}
FONTS = [  # every face the family ships, with the licence as read from the file
    dict(face='Inter', role='everything a person reads or types: body, fields, buttons, meta',
         licence='SIL Open Font License 1.1', file='terminal-delight assets/fonts/OFL-Inter.txt',
         copyright='2016 The Inter Project Authors', url='https://github.com/rsms/inter'),
    dict(face='JetBrains Mono', role='titles, tracked-caps labels and tabs, big numbers, code',
         licence='SIL Open Font License 1.1', file='terminal-delight assets/fonts/OFL-JetBrainsMono.txt',
         copyright='2020 The JetBrains Mono Project Authors', url='https://github.com/JetBrains/JetBrainsMono'),
]

ELEV = {
    'inset': [dict(x=0, y=1, blur=2, spread=0, alpha=0.08, inset=True)],
    '1': [dict(lit=True), dict(x=0, y=1, blur=2, spread=0, alpha=0.06), dict(x=0, y=8, blur=20, spread=-12, alpha=0.20)],
    '2': [dict(lit=True), dict(x=0, y=2, blur=6, spread=0, alpha=0.08), dict(x=0, y=16, blur=32, spread=-16, alpha=0.28)],
    '3': [dict(lit=True), dict(x=0, y=4, blur=12, spread=0, alpha=0.10), dict(x=0, y=28, blur=56, spread=-24, alpha=0.40)],
}
PRESS = {'light': dict(x=0, y=2, blur=4, spread=0, alpha=0.25, inset=True, color='#000000'),
         'dark': dict(x=0, y=2, blur=4, spread=0, alpha=0.45, inset=True, color='#000000')}
ANDROID_ELEVATION = {'inset': 0, '1': 2, '2': 6, '3': 12}
SHEEN_MAX = 0.12

# The default neutrals (an app without data-product) and the status colours, unchanged from v2.
LIGHT = {
    'ground': '#faf8f4', 'surface': '#ffffff', 'raised': '#ffffff', 'float': '#ffffff',
    'inset': '#f3efe7', 'field': '#ffffff',
    'surface-top': '#ffffff', 'surface-bottom': '#fbfaf7', 'raised-bottom': '#f8f6f1',
    'ink': '#1c2530', 'ink-2': '#475563', 'ink-3': '#5f6b78',
    'edge': '#e4ddd1', 'edge-control': '#828991',
    'lit': 'rgba(255, 255, 255, 0.9)', 'shadow': '28, 37, 48',
    'danger': '#b42318', 'danger-ink': '#a3200f', 'danger-tint': '#fdeceb', 'danger-edge': '#efb4ad', 'on-danger': '#ffffff',
    'success': '#1f7a3f', 'success-ink': '#1b6d38', 'success-tint': '#e6f3e9', 'success-edge': '#a9d6b5',
    'warning': '#b7791f', 'warning-ink': '#7f4f00', 'warning-tint': '#fbf0d6', 'warning-edge': '#e8c983',
    'neutral': '#6b7785', 'neutral-tint': '#eef0f3', 'neutral-edge': '#cfd5dc',
    'done': '#3f7a55',
    'scrim': 'rgba(17, 22, 28, 0.45)',
}
DARK = {
    'ground': '#11161c', 'surface': '#19202a', 'raised': '#212935', 'float': '#29323f',
    'inset': '#0d1117', 'field': '#0f141a',
    'surface-top': '#1d2531', 'surface-bottom': '#19202a', 'raised-bottom': '#1f2732',
    'ink': '#edf1f5', 'ink-2': '#b7c1cb', 'ink-3': '#97a2ae',
    'edge': '#2b3440', 'edge-control': '#727d8a',
    'lit': 'rgba(255, 255, 255, 0.06)', 'shadow': '0, 0, 0',
    'danger': '#ff9b91', 'danger-ink': '#ffa59c', 'danger-tint': '#3a1714', 'danger-edge': '#7a2e27', 'on-danger': '#2a0b08',
    'success': '#7ad49a', 'success-ink': '#86dba5', 'success-tint': '#12301d', 'success-edge': '#2f6a43',
    'warning': '#f2c46b', 'warning-ink': '#f5cd7f', 'warning-tint': '#33270e', 'warning-edge': '#6e5520',
    'neutral': '#8f9aa6', 'neutral-tint': '#262f3b', 'neutral-edge': '#3d4856',
    'done': '#6fbf8c',
    'scrim': 'rgba(0, 0, 0, 0.6)',
}
NEUTRAL_ROLES = ('ground', 'surface', 'surface-top', 'surface-bottom', 'raised', 'raised-bottom', 'float',
                 'inset', 'field', 'ink', 'ink-2', 'ink-3', 'edge', 'edge-control', 'neutral', 'neutral-tint', 'neutral-edge')
# The most chroma each neutral may take from a theme's background (rule step 4)
CHROMA_CAP = {
    'light': {'ground': 0.008, 'surface': 0.0, 'surface-top': 0.0, 'surface-bottom': 0.004, 'raised': 0.0,
              'raised-bottom': 0.006, 'float': 0.0, 'inset': 0.012, 'field': 0.0, 'ink': 0.024, 'ink-2': 0.03,
              'ink-3': 0.03, 'edge': 0.015, 'edge-control': 0.015, 'neutral': 0.03, 'neutral-tint': 0.012,
              'neutral-edge': 0.015},
    'dark': {'ground': 0.012, 'surface': 0.016, 'surface-top': 0.018, 'surface-bottom': 0.016, 'raised': 0.018,
             'raised-bottom': 0.018, 'float': 0.02, 'inset': 0.01, 'field': 0.01, 'ink': 0.008, 'ink-2': 0.016,
             'ink-3': 0.02, 'edge': 0.02, 'edge-control': 0.02, 'neutral': 0.02, 'neutral-tint': 0.02,
             'neutral-edge': 0.02},
}
ALIASES = {
    'neutral-ink': 'ink-2', 'done-ink': 'ink-2', 'done-tint': 'neutral-tint',
    'avatar-bg': 'neutral-tint', 'avatar-ink': 'ink-2',
    'assist-surface': 'raised', 'assist-ink': 'ink', 'assist-live': 'accent',
    'word': 'ink', 'line': 'edge',
}

# ── the family: loaded from --family FILE (see examples/head-waters/family.py) ──
FAMILY = 'Family'
PREFIX = '--fam-'
INTENT_C = {'ink': 0.0, 'grey': 0.035, 'gentle': 0.05, 'bright': 0.13}
SOURCES = {}        # product -> theme source (theme name, intent, slot or hue, colours read, why, licence)
FIXED = {}          # product -> a palette given whole (a product whose brand predates the rule)
ORDER = []          # placement order for rule step 6: fixed products first
OFFSETS = [0, -0.02, 0.02, -0.04, 0.04, -0.06, 0.06, -0.08, 0.08, -0.10, 0.10]
OLD_VALUES = []     # values that were wrong once; --selftest proves each still fails
BRANDS = {}         # brands a client page may wear (optional), checked by R10
BRAND_SUBTITLE_ALPHA = 1.0
BRAND_BAND_SHEEN = 0.0
OVERRIDES = {}   # (product, mode, role) -> value; used by --selftest only

def read_theme(name):
    """A theme's colours from its colors.toml, when the family file did not record them."""
    import tomllib
    for d in THEME_DIRS:
        p = d / name / 'colors.toml'
        if p.exists():
            with open(p, 'rb') as f:
                data = tomllib.load(f)
            return {k: v for k, v in data.items() if isinstance(v, str) and v.startswith('#')}
    raise SystemExit(f"theme '{name}' is not installed and its colours are not recorded in the family file")

# ── derivation (the rule, steps 2 to 6) ───────────────────────────────────────
def ramp(mode, hue, scale):
    base = LIGHT if mode == 'light' else DARK
    out = {}
    for role in NEUTRAL_ROLES:
        L, _C, _H = oklch(base[role])
        C = CHROMA_CAP[mode][role] * scale
        out[role] = hexof(L, C, hue) if C > 0 else hexof(L, 0, 0)
    return out

def resolve(c):
    out = dict(c)
    for k, target in ALIASES.items():
        if k not in out and target in out:
            out[k] = out[target]
    return out

def sheen_alpha(fill, ink):
    a = SHEEN_MAX
    while a > 0 and contrast(ink, mix_white(fill, a)) < 4.6:
        a = round(a - 0.01, 2)
    return max(a, 0.0)

def accent_set(L, C, H, mode, ink_kind=False, fg=None):
    if mode == 'light':
        if ink_kind:
            return {'accent': hexof(L, 0, 0), 'accent-hover': hexof(L + 0.08, 0, 0), 'accent-ink': hexof(L, 0, 0),
                    'accent-tint': hexof(0.95, 0, 0), 'on-accent': '#ffffff'}
        return {'accent': hexof(L, C, H), 'accent-hover': hexof(L - 0.06, C, H), 'accent-ink': hexof(L - 0.02, C, H),
                'accent-tint': hexof(0.955, min(C * 0.4, 0.025), H), 'on-accent': '#ffffff'}
    if ink_kind:
        fL, fC, fH = fg
        return {'accent': hexof(L, fC, fH), 'accent-hover': hexof(min(L + 0.05, 0.97), fC, fH),
                'accent-ink': hexof(min(L + 0.03, 0.97), fC, fH), 'accent-tint': hexof(0.27, 0.01, fH),
                'on-accent': hexof(0.15, 0, 0)}
    return {'accent': hexof(L, C, H), 'accent-hover': hexof(min(L + 0.05, 0.95), C, H),
            'accent-ink': hexof(min(L + 0.04, 0.95), C, H), 'accent-tint': hexof(0.29, min(C * 0.5, 0.04), H),
            'on-accent': hexof(0.20, min(C, 0.05), H)}

def own_ok(c, mode):
    """Rule step 6, for one candidate: does this palette pass its own contrast?"""
    if contrast(c['on-accent'], c['accent']) < 4.6 or contrast(c['on-accent'], c['accent-hover']) < 4.6:
        return False
    for bg in SURFACES + ('accent-tint',):
        if contrast(c['accent-ink'], c[bg]) < 4.5:
            return False
    L, C, _H = oklch(c['accent'])
    if mode == 'light' and C >= 0.05 and not 0.38 <= L <= 0.55:
        return False
    return status_ok(c)

def status_ok(c):
    L, C, H = oklch(c['accent'])
    if C < 0.02:
        return True
    for s in ('danger', 'warning', 'success'):
        if hue_gap(H, oklch(c[s])[2]) >= 40:
            continue
        if C <= 0.06 and lab_distance(c['accent'], c[s]) >= 8.0:
            continue
        return False
    return True

def signature_for(src, c, mode):
    slot = src.get('signature_slot')
    if isinstance(slot, dict):
        slot = slot.get(mode)
    if not slot:
        return c['accent'], None
    L, C, H = oklch(src['colours'][slot])
    start = L
    step = -0.01 if mode == 'light' else 0.01
    for _ in range(60):
        h = hexof(L, C, H)
        if all(contrast(h, c[bg]) >= 3.0 for bg in ('ground', 'raised', 'raised-bottom')):
            return h, (round(start, 3), round(L, 3))
        L += step
    return hexof(L, C, H), (round(start, 3), round(L, 3))

def derive_all():
    """Every product's light and dark palette, with the record of what the rule did."""
    products, record, placed = {}, {}, {'light': {}, 'dark': {}}
    for name, fx in FIXED.items():      # products whose palette is given whole come first
        pl = resolve({**LIGHT, **fx['light']})
        pd = resolve({**DARK, **{k: hexof(*v) for k, v in fx['dark_lch'].items()}})
        pl.setdefault('signature', pl['accent']); pd.setdefault('signature', pd['accent'])
        products[name] = {'light': pl, 'dark': pd}
        placed['light'][name], placed['dark'][name] = pl['accent'], pd['accent']
        record[name] = {'source': fx['source'], 'moves': []}
    for name in [n for n in ORDER if n not in FIXED]:
        src = SOURCES[name]
        if 'colours' not in src:
            src['colours'] = read_theme(src['theme'])
        ident = src['colours'][src['slot']] if src.get('slot') else None
        H = src.get('hue') if src.get('hue') is not None else oklch(ident)[2]
        C = INTENT_C[src['intent']]
        bL, bC, bH = oklch(src['colours']['background'])
        scale = max(0.0, min(1.0, bC / 0.025))
        fg = oklch(src['colours']['foreground'])
        ink_kind = src['intent'] == 'ink'
        products[name], moves = {}, []
        for mode in ('light', 'dark'):
            base = LIGHT if mode == 'light' else DARK
            neutrals = ramp(mode, bH, scale)
            if ink_kind:
                L0 = 0.24 if mode == 'light' else fg[0]
            else:
                L0 = 0.46 if mode == 'light' else 0.78
            chosen = None
            for off in OFFSETS:
                cand = resolve({**base, **neutrals, **accent_set(L0 + off, C, H, mode, ink_kind, fg)})
                if not own_ok(cand, mode):
                    continue
                if any(min(cvd_distance(cand['accent'], other, 'deutan'), cvd_distance(cand['accent'], other, 'protan')) < 5.0
                       for other in placed[mode].values()):
                    continue
                chosen = (off, cand)
                break
            if chosen is None:
                chosen = (0, resolve({**base, **neutrals, **accent_set(L0, C, H, mode, ink_kind, fg)}))
                moves.append(f'{mode}: no lightness in reach passes every check; left at {L0:.2f} for the checks to report')
            off, cand = chosen
            if off:
                moves.append(f'{mode} accent lightness {L0:.2f} -> {L0 + off:.2f} (rule step 6)')
            for (p, m, role), v in OVERRIDES.items():
                if p == name and m == mode and role != 'signature':
                    cand[role] = v
            sig, sigmove = signature_for(src, cand, mode)
            if (name, mode, 'signature') in OVERRIDES:
                sig = OVERRIDES[(name, mode, 'signature')]
            elif sigmove and abs(sigmove[0] - sigmove[1]) > 0.001:
                moves.append(f'{mode} signature lightness {sigmove[0]:.2f} -> {sigmove[1]:.2f} to read 3:1')
            cand['signature'] = sig
            if (name, mode, 'accent') in OVERRIDES:
                cand['assist-live'] = cand['accent']
            products[name][mode] = cand
            placed[mode][name] = cand['accent']
        record[name] = {'source': src, 'moves': moves, 'hue': round(H, 1), 'chroma': C,
                        'neutral_hue': round(bH, 1), 'neutral_scale': round(scale, 2)}
    return products, record

def palettes():
    products, _ = derive_all()
    for name in ORDER:
        for mode in ('light', 'dark'):
            yield name, mode, products[name][mode]

def fills(c):
    out = {}
    for k, ink in (('accent', 'on-accent'), ('accent-hover', 'on-accent'), ('danger', 'on-danger')):
        a = sheen_alpha(c[k], c[ink])
        out[f'{k}-top'] = mix_white(c[k], a)
        out[f'{k}-sheen'] = a
    return out

def brands():
    return BRANDS, 'the family file'

def theme_file_advisories():
    """The recorded theme colours against the theme files on this machine, when present."""
    out = []
    for name, src in SOURCES.items():
        path = next((d / src['theme'] / 'colors.toml' for d in THEME_DIRS if (d / src['theme'] / 'colors.toml').exists()), None)
        if not path:
            out.append(f"{name}: theme '{src['theme']}' not installed here; using the recorded colours")
            continue
        text = path.read_text().lower()
        for k, v in src['colours'].items():
            if f'"{v.lower()}"' not in text:
                out.append(f"{name}: recorded {k} {v} not found in {path}")
    return out

# ── checks ────────────────────────────────────────────────────────────────────
SURFACES = ('ground', 'surface', 'surface-top', 'surface-bottom', 'raised', 'raised-bottom', 'float', 'inset', 'field')

def checks():
    rows, advisories = [], []
    def need(rule, prod, mode, what, fg, bg, floor):
        r = contrast(fg, bg)
        rows.append((rule, prod, mode, what, round(r, 2), floor, r >= floor))
    products, record = derive_all()
    for prod, mode, c in palettes():
        f = fills(c)
        for ink in ('ink', 'ink-2', 'ink-3'):
            for bg in SURFACES:
                need('R1', prod, mode, f'{ink} on {bg}', c[ink], c[bg], 4.5)
        for fill, ink in (('accent', 'on-accent'), ('accent-hover', 'on-accent'), ('danger', 'on-danger')):
            need('R2', prod, mode, f'{ink} on {fill}', c[ink], c[fill], 4.5)
            need('R2', prod, mode, f'{ink} on {fill} top (sheen {f[fill + "-sheen"]})', c[ink], f[fill + '-top'], 4.5)
        for bg in SURFACES + ('accent-tint',):
            need('R3', prod, mode, f'accent-ink on {bg}', c['accent-ink'], c[bg], 4.5)
        if 'edge-accent' in c:
            need('R3', prod, mode, 'edge-accent on ground', c['edge-accent'], c['ground'], 4.5)
        for bg in SURFACES:
            need('R4', prod, mode, f'edge-control on {bg}', c['edge-control'], c[bg], 3.0)
            need('R5', prod, mode, f'focus on {bg}', c['accent-ink'], c[bg], 3.0)
        for s in ('danger', 'success', 'warning'):
            need('R6', prod, mode, f'{s}-ink on {s}-tint', c[f'{s}-ink'], c[f'{s}-tint'], 4.5)
            for bg in ('surface', 'ground', 'inset', 'raised-bottom', 'float'):
                need('R6', prod, mode, f'{s}-ink on {bg}', c[f'{s}-ink'], c[bg], 4.5)
        need('R6', prod, mode, 'neutral-ink on neutral-tint', c['neutral-ink'], c['neutral-tint'], 4.5)
        for mark in ('neutral', 'done'):
            for bg in ('surface', 'ground', 'inset', 'raised-bottom', 'float', 'neutral-tint'):
                need('R6', prod, mode, f'{mark} mark on {bg}', c[mark], c[bg], 3.0)
        L, C, H = oklch(c['accent'])
        if mode == 'light':
            rows.append(('R7', prod, mode, f'accent OKLCH L={L:.2f} C={C:.3f}', round(L, 2), '0.38-0.55', C < 0.05 or 0.38 <= L <= 0.55))
        if C >= 0.02:
            for s in ('danger', 'warning', 'success'):
                gap, dist = hue_gap(H, oklch(c[s])[2]), lab_distance(c['accent'], c[s])
                ok = gap >= 40 or (C <= 0.06 and dist >= 8.0)
                rows.append(('R8', prod, mode, f'accent hue {H:.0f} vs {s}: {gap:.0f} deg, {dist:.1f} apart', round(gap, 1), '40 deg, or C<=0.06 and 8 apart', ok))
        for bg in ('ground', 'raised', 'raised-bottom'):
            need('R11', prod, mode, f'folio bar (signature) on {bg}', c['signature'], c[bg], 3.0)
        if 'word' in c:
            need('R11', prod, mode, 'wordmark on raised', c['word'], c['raised'], 3.0)
    for mode in ('light', 'dark'):
        acc = {n: products[n][mode]['accent'] for n in ORDER}
        for i, a in enumerate(ORDER):
            for b in ORDER[i + 1:]:
                for kind in ('deutan', 'protan'):
                    d = cvd_distance(acc[a], acc[b], kind)
                    rows.append(('R9', f'{a}/{b}', mode, f'{kind} distance', round(d, 2), 5.0, d >= 5.0))
    data, _src = brands()
    for name, b in data.items():
        band = mix_white(b['headerBg'], BRAND_BAND_SHEEN)
        need('R10', f'brand:{name}', 'light', 'headerText on the band top', b['headerText'], band, 4.5)
        sub = '#%02x%02x%02x' % tuple(round(BRAND_SUBTITLE_ALPHA * x + (1 - BRAND_SUBTITLE_ALPHA) * y)
                                      for x, y in zip(_rgb(b['headerText']), _rgb(band)))
        need('R10', f'brand:{name}', 'light', f'subtitle (headerText at {BRAND_SUBTITLE_ALPHA:.0%}) on the band top', sub, band, 4.5)
        r = contrast(b['accentBar'], b['headerBg'])
        if r < 4.5:
            advisories.append(f"brand:{name}: accentBar {b['accentBar']} as subtitle text is {r:.2f}:1 on {b['headerBg']}; draw the subtitle in headerText")
        w = b.get('web')
        if w:
            need('R10', f'brand:{name}', 'light', 'white on web accent', '#ffffff', w['accent'], 4.5)
            need('R10', f'brand:{name}', 'light', 'web accent on accentSoft', w['accent'], w['accentSoft'], 4.5)
            need('R10', f'brand:{name}', 'light', 'white on web accent top', '#ffffff', mix_white(w['accent'], sheen_alpha(w['accent'], '#ffffff')), 4.5)
            need('R10', f'brand:{name}', 'dark', 'accentDark on dark surface', w['accentDark'], DARK['surface'], 4.5)
            need('R10', f'brand:{name}', 'dark', 'dark ink on accentDark', '#0d1117', w['accentDark'], 4.5)
    for name, rec in record.items():
        for m in rec['moves']:
            advisories.append(f'{name}: {m}')
    advisories.extend(theme_file_advisories())
    return rows, advisories

# ── emit CSS ──────────────────────────────────────────────────────────────────
def css_block(sel, d, prefix='--hw-'):
    return '\n'.join([f'{sel} {{'] + [f'  {prefix}{k}: {v};' for k, v in d.items()] + ['}'])

def shadow_css(layers, shadow_rgb, dark):
    parts = []
    for l in layers:
        if l.get('lit'):
            parts.append('inset 0 1px 0 var(--hw-lit)')
            continue
        a = min(l['alpha'] * (2.2 if dark else 1), 0.85)
        col = l.get('color')
        rgb = ', '.join(str(x) for x in _rgb(col)) if col else shadow_rgb
        spread = f" {l['spread']}px" if l['spread'] else ''
        parts.append(f"{'inset ' if l.get('inset') else ''}{l['x']}px {l['y']}px {l['blur']}px{spread} rgba({rgb}, {a:.2f})")
    return ', '.join(parts)

def colour_vars(c, mode, full=True):
    dark = mode == 'dark'
    out = {k: v for k, v in c.items() if k != 'shadow' and k not in ALIASES}
    out['surface-fill'] = f"linear-gradient(180deg, {c['surface-top']} 0%, {c['surface-bottom']} 100%)"
    out['raised-fill'] = f"linear-gradient(180deg, {c['raised']} 0%, {c['raised-bottom']} 100%)"
    if full:
        for k, layers in ELEV.items():
            out[f'elev-{k}'] = shadow_css(layers, c['shadow'], dark)
        out['press'] = shadow_css([PRESS[mode]], c['shadow'], False)
    if 'accent' in c:
        f = fills(c)
        out['accent-top'], out['accent-hover-top'] = f['accent-top'], f['accent-hover-top']
    out['danger-top'] = mix_white(c['danger'], sheen_alpha(c['danger'], c['on-danger']))
    return out

def shared_vars():
    s = SHARED
    v = {}
    for k, f in s['font'].items():
        v[f'font-{k}'] = f
    for k, (size, lh) in s['text'].items():
        v[f'text-{k}'] = f'{size}px'
        v[f'leading-{k}'] = f'{lh}px'
    for k, w in s['weight'].items():
        v[f'weight-{k}'] = str(w)
    for k, t in s['tracking'].items():
        v[f'tracking-{k}'] = f'{t}em'
    for group in ('space', 'gap', 'pad', 'size', 'radius'):
        for k, n in s[group].items():
            v[f'{group}-{k}'] = n if isinstance(n, str) else f'{n}px'
    for k, n in s['folio'].items():
        v[f'folio-{k}'] = f'{n}px'
    v['line-width'] = f"{s['line']['width']}px"
    m = s['motion']
    for k in ('dur-1', 'dur-2', 'dur-3', 'dur-fade'):
        v[k] = f'{m[k]}ms'
    v['ease'] = 'cubic-bezier({}, {}, {}, {})'.format(*m['ease'])
    v['ease-exit'] = 'cubic-bezier({}, {}, {}, {})'.format(*m['ease-exit'])
    v['motion-travel-max'] = f"{m['travel-max']}px"
    fam = {'ui': 'var(--hw-font-ui)', 'display': 'var(--hw-font-display)'}
    for name, (step, weight, face, _t, _u, _tab) in TYPE.items():
        size, lh = s['text'][step]
        v[f'type-{name}'] = f'{weight} {size}px/{lh}px {fam[face]}'
    v['focus-width'] = f"{s['focus']['width']}px"
    v['focus-offset'] = f"{s['focus']['offset']}px"
    return v

def alias_block():
    d = {k: f'var(--hw-{t})' for k, t in ALIASES.items()}
    d['signature'] = 'var(--hw-accent)'
    d['accent-fill'] = 'linear-gradient(180deg, var(--hw-accent-top) 0%, var(--hw-accent) 100%)'
    d['accent-fill-hover'] = 'linear-gradient(180deg, var(--hw-accent-hover-top) 0%, var(--hw-accent-hover) 100%)'
    d['danger-fill'] = 'linear-gradient(180deg, var(--hw-danger-top) 0%, var(--hw-danger) 100%)'
    g = SHARED['glow-live']
    d['glow-live'] = f"0 0 {g['blur']}px color-mix(in srgb, var(--hw-accent) {int(g['alpha'] * 100)}%, transparent)"
    return d

SIG_CSS = r'''
/* ════════════════════════════════════════════════════════════════════════════
   3 · The family's shapes: the line under the bar, the folio tab, the theme switch
   (version 3: the per-product corner shapes are gone; every app draws these)
   ════════════════════════════════════════════════════════════════════════════ */
.hw-bar {
  min-height: var(--hw-size-bar);
  background: var(--hw-raised-fill);
  color: var(--hw-ink);
  border-bottom: var(--hw-line-width) solid var(--hw-line);
}
@media (max-width: 599px) { .hw-bar { min-height: var(--hw-size-bar-phone); } }

/* The folio tab: the selected menu item, joined to the page below it. A bar over the words
   in the product's colour, a chip cut from the right corner, a slight rounding on the left
   (a third of a card's), and no line under it, so it opens into the page. */
.hw-folio {
  position: relative; align-self: flex-end;
  background: var(--hw-ground); color: var(--hw-ink);
  border-top: var(--hw-folio-bar) solid var(--hw-signature);
  border-left: 1px solid var(--hw-edge);
  border-radius: var(--hw-folio-radius) 0 0 0;
  margin-bottom: calc(-1 * var(--hw-line-width));
  padding-bottom: var(--hw-line-width);
  clip-path: polygon(0 0, calc(100% - var(--hw-folio-chip)) 0, 100% var(--hw-folio-chip), 100% 100%, 0 100%);
}
.hw-folio::after {   /* the right side, and the chip's edge */
  content: ""; position: absolute; right: 0; top: 0; bottom: 0; width: var(--hw-folio-chip);
  background:
    linear-gradient(to bottom left, transparent calc(50% - 1px), var(--hw-edge) calc(50% - 1px) 50%, transparent 50%) top right / var(--hw-folio-chip) var(--hw-folio-chip) no-repeat,
    linear-gradient(var(--hw-edge), var(--hw-edge)) right var(--hw-folio-chip) / 1px 100% no-repeat;
  pointer-events: none;
}

/* The theme switch: one button, three states. html[data-theme-pref] holds the person's choice
   (system, light or dark); html.dark is what is drawn. See tokens.json "behaviour.theme". */
.hw-theme-switch { display: inline-grid; place-items: center; width: var(--hw-size-target); height: var(--hw-size-target);
  border-radius: var(--hw-radius-control); color: var(--hw-ink-2); background: transparent; border: 0; cursor: pointer; }
.hw-theme-switch:hover { background: var(--hw-inset); color: var(--hw-ink); }
.hw-theme-switch svg { width: 20px; height: 20px; }
.hw-theme-switch [data-for] { display: none; }
[data-theme-pref="system"] .hw-theme-switch [data-for="system"],
[data-theme-pref="light"] .hw-theme-switch [data-for="light"],
[data-theme-pref="dark"] .hw-theme-switch [data-for="dark"] { display: block; }

/* A reed: a physical border down the left of a block, in --hw-edge-accent when a product has one.
   A selected block swaps it for the accent; one left edge at a time. */
.hw-reed { border-left: 3px solid var(--hw-edge-accent, var(--hw-edge)); }
.hw-reed[aria-selected="true"] { border-left-color: var(--hw-accent); }

:where([data-product]) :focus-visible {
  outline: var(--hw-focus-width) solid var(--hw-accent-ink);
  outline-offset: var(--hw-focus-offset);
}
.hw-dense { position: relative; min-height: var(--hw-size-control-dense); }
.hw-dense::before { content: ""; position: absolute; left: 0; right: 0;
  top: calc((var(--hw-size-control-dense) - var(--hw-size-target)) / 2);
  bottom: calc((var(--hw-size-control-dense) - var(--hw-size-target)) / 2); }
'''

HEADER = '''/* __FAMILY__ family tokens. Generated by tokens.py from the family file; edit that, not this.

   HOW TO USE
   1. Put data-product="<product>" on <html>.
   2. Put data-theme-pref="system" | "light" | "dark" on <html> from the person's saved choice, and
      the class "dark" when dark is what gets drawn (tokens.json "behaviour.theme" says how).
   3. Tailwind v4 stays: map roles once in globals.css (@theme inline { --color-surface:
      var(--hw-surface); ... }) and never write a hex in a component.
   4. Gradients (*-fill) are web only and go in the background shorthand; native uses the solid
      colour of the same name. Numbers for a native theme are in tokens.json under "native".

   WHERE THE COLOURS COME FROM (version 3)
     Each product follows an Omarchy theme, by the rule in tokens.py; tokens.json records the
     theme, its licence, the colours read and every lightness the rule moved, under
     products.<name>.source.

   WHICH ROLE FOR WHAT
     --hw-ground  the page            --hw-surface  cards, lists (elev-1)
     --hw-raised  top bar, dock (elev-2)    --hw-float  menus, popovers, dialogs (elev-3)
     --hw-inset   wells, tracks, disabled    --hw-field  inside an input
     --hw-ink / -ink-2 / -ink-3   titles and body / secondary / meta, hints, placeholders
     --hw-edge          card borders, dividers     --hw-line  the line under the bar (= edge)
     --hw-edge-control  the outline of a field, button or checkbox (3:1 on every surface)
     --hw-accent        FILLS in the product colour     --hw-accent-fill  the primary's background
     --hw-accent-ink    TEXT and icons in the product colour, the focus ring
     --hw-accent-tint   the BACKGROUND of a selected item     --hw-on-accent  text on a fill
     --hw-signature     the bar over the selected menu item's words (the accent, or a named slot)
     --hw-danger | success | warning | neutral | done (+ -ink, -tint, -edge)   status only
     --hw-avatar-*, --hw-assist-*, --hw-word, --hw-press, --hw-glow-live
     Shapes: --hw-line-width (2), --hw-folio-radius (4), --hw-folio-chip (10), --hw-folio-bar (3)
     Type: font: var(--hw-type-body) ... -tab and -eyebrow are JetBrains Mono in tracked capitals
           (uppercase, --hw-tracking-label); titles and -figure are JetBrains Mono; the rest Inter.
*/'''

def build_css():
    products, record = derive_all()
    out = [HEADER.replace('__FAMILY__', FAMILY), '''
/* ════════════════════════════════════════════════════════════════════════════
   1 · Shared
   ════════════════════════════════════════════════════════════════════════════ */''']
    out.append(css_block(':root', shared_vars()))
    out.append(css_block(':root', colour_vars(dict(LIGHT), 'light')))
    out.append(css_block('.dark', colour_vars(dict(DARK), 'dark')))
    out.append('/* Roles that point at other roles, declared wherever the target can change. */')
    out.append(css_block(':root, [data-product], .dark', alias_block()))
    out.append('@media (prefers-reduced-motion: reduce) {\n  :root { --hw-dur-1: 0ms; --hw-dur-2: 0ms; --hw-dur-3: 0ms; }\n}')
    out.append('''
/* ════════════════════════════════════════════════════════════════════════════
   2 · Products: each from its Omarchy theme by the rule in build_tokens.py
   ════════════════════════════════════════════════════════════════════════════ */''')
    for name in ORDER:
        src = record[name]['source']
        out.append(f"/* {src['label']}. From {src['theme']}{' (inferred)' if src.get('inferred') else ''}. */")
        blocks = []
        for mode in ('light', 'dark'):
            c = products[name][mode]
            v = colour_vars(c, mode, full=False)
            for k in ('signature', 'word', 'edge-accent'):
                if k in c and not (k == 'signature' and c[k] == c['accent']) and not (k == 'word' and c[k] == c['ink']):
                    v[k] = c[k]
            blocks.append(v)
        out.append(css_block(f'[data-product="{name}"]', blocks[0]))
        out.append(css_block(f'.dark[data-product="{name}"], .dark [data-product="{name}"], [data-product="{name}"] .dark', blocks[1]))
    out.append(SIG_CSS)
    return '\n\n'.join(out) + '\n'

# ── emit JSON ─────────────────────────────────────────────────────────────────
def tok(value, typ, css=None, desc=None):
    t = {'$value': value, '$type': typ}
    if desc:
        t['$description'] = desc
    if css:
        t['$extensions'] = {'css': css}
    return t

def color_group(c):
    g = {}
    for k, v in resolve(c).items():
        if k in ('shadow', 'lit', 'scrim') or not isinstance(v, str) or not v.startswith('#'):
            continue
        g[k] = tok(v, 'color', '--hw-' + k)
    if 'accent' in c:
        f = fills(c)
        g['accent-top'] = tok(f['accent-top'], 'color', '--hw-accent-top', 'top end of the primary fill (web gradient)')
        g['accent-hover-top'] = tok(f['accent-hover-top'], 'color', '--hw-accent-hover-top')
    return g

def native_layers(layers, c, mode):
    out = []
    for l in layers:
        if l.get('lit'):
            out.append({'x': 0, 'y': 1, 'blur': 0, 'spread': 0, 'color': '#ffffff',
                        'alpha': 0.9 if mode == 'light' else 0.06, 'inset': True, 'optional': True})
            continue
        a = min(l['alpha'] * (2.2 if mode == 'dark' else 1), 0.85)
        col = l.get('color') or '#%02x%02x%02x' % tuple(int(x) for x in c['shadow'].split(','))
        out.append({'x': l['x'], 'y': l['y'], 'blur': l['blur'], 'spread': l['spread'], 'color': col,
                    'alpha': round(a, 2), 'inset': bool(l.get('inset'))})
    return out

def native_group():
    s = SHARED
    num = lambda d: {k: v for k, v in d.items() if not isinstance(v, str)}
    typ = {}
    for name, (step, weight, face, track, upper, tab) in TYPE.items():
        size, lh = s['text'][step]
        t = {'face': face, 'size': size, 'lineHeight': lh, 'weight': str(weight), 'letterSpacing': round(track * size, 2)}
        if upper:
            t['textTransform'] = 'uppercase'
        if tab:
            t['fontVariant'] = ['tabular-nums']
        typ[name] = t
    return {
        '$description': 'Plain numbers for a native theme (React Native, iPad, Android, Mac). Sizes are dp/pt, equal to CSS px. Fills are solid on native.',
        'font': {
            'ui': {'bundle': ['Inter_400Regular', 'Inter_600SemiBold'], 'package': '@expo-google-fonts/inter', 'licence': 'OFL 1.1'},
            'display': {'bundle': ['JetBrainsMono_500Medium', 'JetBrainsMono_600SemiBold'], 'package': '@expo-google-fonts/jetbrains-mono', 'licence': 'OFL 1.1'},
            'note': 'Both bundled, so every platform draws the same faces; allowFontScaling keeps Dynamic Type working.',
        },
        'type': typ,
        'space': num(s['space']), 'gap': num(s['gap']), 'pad': num(s['pad']), 'size': num(s['size']),
        'radius': num(s['radius']), 'focus': dict(s['focus']), 'folio': dict(s['folio']), 'line': dict(s['line']),
        'motion': {'dur1': s['motion']['dur-1'], 'dur2': s['motion']['dur-2'], 'dur3': s['motion']['dur-3'],
                   'durFade': s['motion']['dur-fade'], 'ease': s['motion']['ease'], 'easeExit': s['motion']['ease-exit'],
                   'travelMax': s['motion']['travel-max'], 'reducedMotion': 'durations 0; keep the press shadow and a 100 ms fade'},
        'elevation': {
            'light': {k: native_layers(v, LIGHT, 'light') for k, v in ELEV.items()},
            'dark': {k: native_layers(v, DARK, 'dark') for k, v in ELEV.items()},
            'android': ANDROID_ELEVATION,
            'press': {m: native_layers([PRESS[m]], LIGHT if m == 'light' else DARK, 'light') for m in ('light', 'dark')},
        },
        'glowLive': {'blur': s['glow-live']['blur'], 'alpha': s['glow-live']['alpha'], 'color': 'accent'},
        'example-dictation-app': {
            'colorScheme': 'follows behaviour.theme (light, dark or system)',
            'reed': {'side': 'left', 'width': 3, 'color': 'edge-accent', 'selected': 'accent'},
            'dock': {'maxWidth': s['size']['dock-max'], 'sideMargin': s['pad']['page'],
                     'rule': 'width = min(760, window width - 2 x 24), so it shrinks in split view'},
            'disabled': {'background': 'inset', 'text': 'ink-3', 'border': 'edge', 'opacity': 1},
            'pressed': {'background': 'accent-hover', 'shadow': 'press'},
            'focus': {'width': 2, 'offset': 2, 'color': 'accent-ink'},
            'hit': {'ios': s['size']['target'], 'android': s['size']['target-android']},
        },
    }

BEHAVIOUR = {
    'theme': {
        '$description': 'The theme switch, in every app. After the Terminal Delight documentation site (github.com/parker-brown-family/terminal-delight, docsite/layout.html and assets/td-shell.js), extended from two states to three.',
        'values': ['system', 'light', 'dark'],
        'default': 'system',
        'control': 'one icon button at the right of the bar; each press moves system -> light -> dark -> system; the icon shows the current state (half-filled circle, sun, moon) and its label says the next',
        'stored': 'with the person\'s account (one field, theme_preference), so it follows them across devices and across every app in the suite',
        'mirror': 'a cookie hw-theme=<value> on the suite\'s shared parent domain (Path=/, SameSite=Lax, one year), written on every change and on sign-in from the account value; every app reads it on the server',
        'before_first_paint': 'the server renders data-theme-pref from the cookie and the class dark when the value is dark; for system, a five-line inline script in <head> adds dark from matchMedia(prefers-color-scheme: dark) before the body paints, and follows the device while it changes',
        'signed_out': 'a visitor without an account (a client on a booking page) gets this device\'s cookie if one exists, else system; the switch sits in the page footer and its choice stays on this device',
        'native': 'a native app reads the same account field after sign-in; before sign-in, system (Appearance API)',
    },
}

def build_json():
    s = SHARED
    products, record = derive_all()
    j = {
        '$description': f'{FAMILY} family tokens. Each product colour derives from an Omarchy theme by the rule in tokens.py; products.<name>.source records the theme, its licence, the colours read, and every lightness the rule moved.',
        'shared': {
            'font': {k: tok(v, 'fontFamily', f'--hw-font-{k}') for k, v in s['font'].items()},
            'fonts': FONTS,
            'text': {k: {'size': tok(f'{a}px', 'dimension', f'--hw-text-{k}'),
                         'lineHeight': tok(f'{b}px', 'dimension', f'--hw-leading-{k}')} for k, (a, b) in s['text'].items()},
            'weight': {k: tok(v, 'fontWeight', f'--hw-weight-{k}') for k, v in s['weight'].items()},
            'tracking': {k: tok(f'{v}em', 'dimension', f'--hw-tracking-{k}') for k, v in s['tracking'].items()},
            'space': {k: tok(f'{v}px', 'dimension', f'--hw-space-{k}') for k, v in s['space'].items()},
            'gap': {k: tok(f'{v}px', 'dimension', f'--hw-gap-{k}') for k, v in s['gap'].items()},
            'pad': {k: tok(f'{v}px', 'dimension', f'--hw-pad-{k}') for k, v in s['pad'].items()},
            'size': {k: tok(v if isinstance(v, str) else f'{v}px', 'dimension', f'--hw-size-{k}') for k, v in s['size'].items()},
            'radius': {k: tok(f'{v}px', 'dimension', f'--hw-radius-{k}') for k, v in s['radius'].items()},
            'folio': {k: tok(f'{v}px', 'dimension', f'--hw-folio-{k}') for k, v in s['folio'].items()},
            'line': {'width': tok(f"{s['line']['width']}px", 'dimension', '--hw-line-width'),
                     'color': tok('{shared.color.light.edge}', 'color', '--hw-line', 'the edge colour, not an accent')},
            'motion': {
                'dur-1': tok('120ms', 'duration', '--hw-dur-1'), 'dur-2': tok('200ms', 'duration', '--hw-dur-2'),
                'dur-3': tok('300ms', 'duration', '--hw-dur-3'), 'dur-fade': tok('100ms', 'duration', '--hw-dur-fade'),
                'ease': tok(s['motion']['ease'], 'cubicBezier', '--hw-ease'),
                'ease-exit': tok(s['motion']['ease-exit'], 'cubicBezier', '--hw-ease-exit'),
                'travel-max': tok('16px', 'dimension', '--hw-motion-travel-max'),
            },
            'focus': {'width': tok('2px', 'dimension', '--hw-focus-width'), 'offset': tok('2px', 'dimension', '--hw-focus-offset')},
            'color': {'light': color_group(resolve(dict(LIGHT))), 'dark': color_group(resolve(dict(DARK)))},
        },
        'products': {},
        'behaviour': BEHAVIOUR,
        'native': native_group(),
    }
    for name in ORDER:
        rec = record[name]
        src = rec['source']
        j['products'][name] = {
            '$description': f"{src['label']}. From {src['theme']}.",
            'source': {'theme': src['theme'], 'url': src['url'], 'licence': src['licence'], 'colours_read': src['colours'],
                       'slot': src.get('slot'), 'hue': rec.get('hue'), 'intent': src['intent'],
                       'neutral_hue': rec.get('neutral_hue'), 'neutral_scale': rec.get('neutral_scale'),
                       'why': src['why'], 'inferred': src['inferred'], 'moves': rec['moves']},
            'light': color_group(products[name]['light']),
            'dark': color_group(products[name]['dark']),
        }
    return json.dumps(j, indent=2) + '\n'

# ── self-test ─────────────────────────────────────────────────────────────────
def selftest():
    global BRAND_SUBTITLE_ALPHA, BRAND_BAND_SHEEN
    slipped = []
    for where, prod, key, old, why in OLD_VALUES:
        if where == 'SHEEN':
            saved = globals()['sheen_alpha']
            globals()['sheen_alpha'] = lambda fill, ink, _a=old: _a
            fails = [r for r in checks()[0] if not r[-1]]
            globals()['sheen_alpha'] = saved
        elif where == 'BRAND_SUBTITLE':
            keep = (BRAND_SUBTITLE_ALPHA, BRAND_BAND_SHEEN)
            BRAND_SUBTITLE_ALPHA, BRAND_BAND_SHEEN = old
            fails = [r for r in checks()[0] if not r[-1]]
            BRAND_SUBTITLE_ALPHA, BRAND_BAND_SHEEN = keep
        elif where == 'RAW':
            OVERRIDES[(prod, key[0], key[1])] = old
            fails = [r for r in checks()[0] if not r[-1]]
            OVERRIDES.clear()
        else:
            table = {'LIGHT': LIGHT, 'DARK': DARK}.get(where) or FIXED[where.split(':', 1)[1]]['light']
            keep = table[key]
            table[key] = old
            fails = [r for r in checks()[0] if not r[-1]]
            table[key] = keep
        first = f'{fails[0][0]} {fails[0][1]} {fails[0][2]} {fails[0][3]} = {fails[0][4]}' if fails else 'NOTHING FAILED'
        label = f"{where}{'.' + prod if prod else ''}{'.' + '.'.join(key) if isinstance(key, tuple) else ('.' + key if key else '')}"
        print(f"{'ok  ' if fails else 'SLIP'} restore {label} = {old}: {len(fails)} check(s) fail, first {first}  [{why}]")
        if not fails:
            slipped.append(label)
    return not slipped

def load_family():
    global HERE
    args = sys.argv
    if '--family' not in args:
        raise SystemExit('usage: tokens.py --family FAMILY.py [--out DIR] [--check | --selftest | --table]')
    path = Path(args[args.index('--family') + 1]).resolve()
    exec(compile(path.read_text(), str(path), 'exec'), globals())
    HERE = Path(args[args.index('--out') + 1]).resolve() if '--out' in args else path.parent

def main():
    load_family()
    if '--selftest' in sys.argv:
        sys.exit(0 if selftest() else 1)
    rows, advisories = checks()
    fails = [r for r in rows if not r[-1]]
    css, js = build_css().replace('--hw-', PREFIX), build_json().replace('--hw-', PREFIX)
    drift = []
    if '--check' in sys.argv:
        for name, text in (('tokens.css', css), ('tokens.json', js)):
            path = HERE / name
            if not path.exists() or path.read_text() != text:
                drift.append(name)
    else:
        (HERE / 'tokens.css').write_text(css)
        (HERE / 'tokens.json').write_text(js)
        print('wrote tokens.css and tokens.json')
    print(f'{len(rows)} checks, {len(fails)} failed; drift: {", ".join(drift) if drift else "none"}; brands from {brands()[1]}')
    for r in fails:
        print('FAIL', *r)
    for d in drift:
        print(f'DRIFT {d} differs from what the table writes; run without --check')
    for a in advisories:
        print('NOTE', a)
    if '--table' in sys.argv:
        for r in rows:
            print(*r)
        products, record = derive_all()
        for n in ORDER:
            for m in ('light', 'dark'):
                c = products[n][m]
                L, C, H = oklch(c['accent'])
                print('ACCENT', n, m, c['accent'], f'L={L:.3f} C={C:.3f} H={H:.0f}', 'signature', c['signature'], 'ground', c['ground'])
    sys.exit(1 if fails or drift else 0)

if __name__ == '__main__':
    main()
