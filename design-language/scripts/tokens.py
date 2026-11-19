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
import json, math, re, sys
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
    # Faces are the family's: FACES, below, set by the family file (reference/type.md).
    'text': {'xs': [12, 16], 'sm': [14, 20], 'md': [16, 24], 'lg': [20, 28],
             'xl': [24, 32], '2xl': [30, 36], '3xl': [38, 44]},
    'weight': {'regular': 400, 'medium': 500, 'semibold': 600, 'bold': 700},
    'tracking': {'label': 0.10, 'display': 0.0},     # em; the frame's tracked capitals
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
    # The glass header, after Terminal Delight's docs site (github.com/parker-brown-family/
    # terminal-delight, docsite/redesign/redesign.css): a faint lit sheet over the ground, a
    # hairline edge, and a soft shadow below in place of a hard line; a glow in the top right corner.
    # The toggle, in place of every checkbox.
    'toggle': {'width': 44, 'height': 26, 'thumb': 20, 'inset': 3},
    'header': {'height': 96, 'control': 34,
               'glass': {'sheet': 'linear-gradient(#ffffff12, #ffffff04)', 'tint': 26, 'blur': 20,
                         'edge': '#ffffff20', 'shadow': '0 14px 34px #00000055, inset 0 1px 0 #ffffff22'},
               'glow': {'origin': '100% 0%', 'reach-x': '38%', 'reach-y': '112%', 'core-stop': '14%', 'mid-stop': '46%'},
               'gel': {'alpha': 62, 'blur': 14, 'saturate': 1.5, 'sheet': 'linear-gradient(#ffffff48, #ffffff0d)',
                       'edge-white': 45, 'shadow': '0 8px 20px #00000055, inset 0 1px 0 #ffffff66'},
               'frost': {'blur': 14, 'saturate': 1.4}},
}
# ── type: set by the family file (see reference/type.md and examples/head-waters/family.py) ──
# FACES: CSS stacks for 'display' (the frame), 'ui' (content, numbers included), 'mono' (code only).
# TYPE: role -> (size, weight, face, tracking-em, uppercase, tabular); size is a step of
#   SHARED['text'] or (px, line) for a display face fitted by its x-height.
# FRAME_ROLES: the roles the display face may set. They never hold a digit.
# FONTS: one entry per face, read from its files: licence_file (relative to the family file),
#   licence, copyright (as the file says it), reserved_name (or None), weights, figures_line_up.
# NATIVE_FACES: (face, weight) -> the static cut a native app bundles.
FACES, TYPE, FRAME_ROLES, FONTS, NATIVE_FACES, TYPE_NOTES = {}, {}, (), [], {}, {}
# Every character that can stand inside a number; the display face's unicode-range leaves them out.
NUMBER_CHARS = '0123456789#$%+,./:=¢£¤¥°±²³¹¼½¾×÷‰′″⁄−' + ''.join(chr(c) for c in range(0x20a0, 0x20d0))
FONT_DIR = Path('.')

def unicode_range_without(chars):
    out, start, gone = [], 0, sorted({ord(c) for c in chars})
    for g in gone + [0x10000]:
        if g > start:
            out.append(f'U+{start:04X}' if g - 1 == start else f'U+{start:04X}-{g - 1:04X}')
        start = g + 1
    return ', '.join(out)

def type_size(step):
    return SHARED['text'][step] if isinstance(step, str) else step

def font_for(css):
    return next(f for f in FONTS if f['css'] == css)

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
    'on-warning': '#1f1300', 'on-success': '#ffffff',
    'scrim': 'rgba(17, 22, 28, 0.45)',
    'frost-sheet': 'linear-gradient(#ffffffa8, #ffffff55)', 'frost-tint': 'transparent',
    'frost-edge': '#ffffffc0', 'frost-shadow': '0 6px 18px #00000026, inset 0 1px 0 #ffffffd0',
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
    'on-warning': '#2a1d02', 'on-success': '#0b2414',
    'scrim': 'rgba(0, 0, 0, 0.6)',
    'frost-sheet': 'linear-gradient(#ffffff22, #ffffff08)', 'frost-tint': 'color-mix(in srgb, var(--hw-header-tint) 45%, transparent)',
    'frost-edge': '#ffffff38', 'frost-shadow': '0 6px 18px #00000040, inset 0 1px 0 #ffffff30',
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
    'word': 'ink', 'line': 'edge', 'page': 'ground',
    'toggle-on': 'accent', 'toggle-thumb-on': 'on-accent', 'toggle-off': 'inset', 'toggle-thumb-off': 'edge-control',
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
SETTLED = {}        # product -> a palette its owner settled by eye: {'light': {...}, 'dark': {...},
                    #   'derived': {mode: {role: (lightness, chroma or None or 'ink')}}}; placed last,
                    #   only its accent and gel move, and only as far as a check needs
REVIEW = {}         # (product, mode, role) -> value: a second provider's accepted changes, given whole;
                    #   neutral roles move their aliases with them; the checks hold them like any other
REVIEW_WHY = {}     # product -> one line: what the review changed and why
GLOW_REACH = {}     # product -> {'reach-x': '32%', 'reach-y': '92%'} where not the base 38% by 112%
GLOW_FROM = {}      # product -> (name, colour): the theme colour its header's corner tone takes
                    #   its hue and chroma (at most 0.07) from
# The header's lightness structure when no product is settled: the corner core and mid (with the
# mid's alpha), the frosted tint and the gel, per mode. A settled product's own values replace it.
HEADER_LIGHTNESS = {'light': {'core': 0.252, 'mid': 0.363, 'mid_alpha': 0.69, 'tint': 0.309, 'gel': 0.63},
                    'dark': {'core': 0.469, 'mid': 0.309, 'mid_alpha': 0.63, 'tint': 0.252, 'gel': 0.63}}

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

def glow_reach(name):
    base = SHARED['header']['glow']
    return {'reach-x': base['reach-x'], 'reach-y': base['reach-y'], **GLOW_REACH.get(name, {})}

def apply_review(name, mode, c, roles):
    """Put the review's values for these roles into a palette, and move the aliases that point at them."""
    for (p_, m, role), v in REVIEW.items():
        if p_ == name and m == mode and role in roles and (name, mode, role) not in OVERRIDES:
            old = c.get(role)
            c[role] = v
            for k, t in ALIASES.items():
                if t == role and c.get(k) == old:
                    c[k] = v

def alpha_hex(h, a):
    return h + '%02x' % round(a * 255)

def header_reference(mode):
    """Lightness of the corner core, mid (and its alpha), frosted tint and gel: from the first
    settled product if there is one, else HEADER_LIGHTNESS."""
    for fx in SETTLED.values():
        hs = fx[mode]
        return {'core': oklch(hs['glow-core'])[0], 'mid': oklch(hs['glow-mid'][:7])[0],
                'mid_alpha': int(hs['glow-mid'][7:] or 'ff', 16) / 255, 'tint': oklch(hs['header-tint'])[0],
                'gel': oklch(hs['gel'])[0], 'gel_C': oklch(hs['gel'])[1]}
    return {**HEADER_LIGHTNESS[mode], 'gel_C': 0.094}

HEADER_ROLES = ('header-ink', 'header-tint', 'glow-core', 'glow-mid', 'gel', 'on-gel', 'frost-ink')

def header_roles(name, mode, c, products):
    """The glass header's colours for one product and mode."""
    if name in SETTLED:
        return {k: SETTLED[name][mode][k] for k in HEADER_ROLES if k in SETTLED[name][mode]}
    ref = header_reference(mode)
    _label, col = GLOW_FROM.get(name, ('its accent', c['accent']))
    _L, Ct, H = oklch(col)
    C = min(Ct, 0.07)
    dark_acc = products[name]['dark']['accent']
    _aL, aC, aH = oklch(dark_acc)
    ink_kind = SOURCES.get(name, {}).get('intent') == 'ink'
    gel = dark_acc if ink_kind else hexof(ref['gel'], min(aC, ref['gel_C']), aH)
    return {'header-ink': c['ink'], 'header-tint': hexof(ref['tint'], C * 0.6, H), 'glow-core': hexof(ref['core'], C, H),
            'glow-mid': alpha_hex(hexof(ref['mid'], C, H), ref['mid_alpha']), 'gel': gel,
            'on-gel': hexof(0.18, min(aC, 0.02), aH), 'frost-ink': c['ink']}

MODE_L = {'light': 0.30, 'dark': 0.80}     # the band: dark under a light page, light under a dark one
MODE_C_MAX = 0.05

def mode_roles(c, mode):
    """The mode strip (you are acting for someone else, or on a test instance): a band in the product's
    deep tone (the corner glow's hue and chroma, at most 0.05), inverse to the page so it is seen at a
    glance without a status colour. Lightness moves only as far as R21 needs."""
    _L, C, H = oklch(c['glow-core'][:7])
    C = min(C, MODE_C_MAX)
    L = MODE_L[mode]
    step = 0.01 if mode == 'light' else -0.01
    ink_L = 0.97 if mode == 'light' else 0.17
    for _ in range(40):
        band, ink = hexof(L, C, H), hexof(ink_L, min(C, 0.012), H)
        if (contrast(ink, band) >= 7.0 and contrast(band, c['ground']) >= 3.0
                and contrast(band, header_bare(c)) >= 3.0):
            break
        L -= step
    return {'mode': band, 'on-mode': ink}

def settled_palette(name, mode):
    """A settled product's given values, with the roles its mock did not show derived from them."""
    base = LIGHT if mode == 'light' else DARK
    fx = SETTLED[name]
    hs = fx[mode]
    _gL, gC, gH = oklch(hs['ground'])
    _iL, iC, iH = oklch(hs['ink'])
    c = {**base, **{k: v for k, v in hs.items() if k in ('ground', 'surface', 'ink')}}
    for role, (L, C) in fx.get('derived', {}).get(mode, {}).items():
        c[role] = hexof(L, iC, iH) if C == 'ink' else hexof(L, gC if C is None else C, gH)
    return c

def derive_settled(name, placed):
    """A settled palette: the given values, with only the accent moved, by rule step 6, if a check fails."""
    out, moves = {}, []
    for mode in ('light', 'dark'):
        hs = SETTLED[name][mode]
        c0 = settled_palette(name, mode)
        L0, C, H = oklch(hs['accent'])
        chosen, first_fail = None, (99, None)
        for off in OFFSETS:
            if off == 0:
                acc = {'accent': hs['accent'], 'on-accent': hs['on-accent'],
                       **{k: v for k, v in accent_set(L0, C, H, mode).items() if k not in ('accent', 'on-accent')}}
            else:
                acc = accent_set(L0 + off, C, H, mode)
            cand = resolve({**c0, **acc})
            iL, iC, iH = oklch(cand['accent-ink'])      # the link keeps the hue, finds its own lightness
            step = -0.01 if mode == 'light' else 0.01
            for _ in range(30):
                if all(contrast(cand['accent-ink'], cand[bg]) >= 4.5 for bg in SURFACES + ('accent-tint',)):
                    break
                iL += step
                cand['accent-ink'] = hexof(iL, iC, iH)
            for (p_, m, role), v in OVERRIDES.items():
                if p_ == name and m == mode:
                    cand[role] = v
            near = min(((min(cvd_distance(cand['accent'], o, 'deutan'), cvd_distance(cand['accent'], o, 'protan')), n)
                        for n, o in placed[mode].items()), default=(99, None))
            if (name, mode, 'accent') in OVERRIDES or (own_ok(cand, mode) and near[0] >= 5.0):
                chosen = (off, cand, near)
                break
            if off == 0:
                first_fail = near
        if chosen is None:
            chosen = (0, resolve({**c0, **accent_set(L0, C, H, mode), 'accent': hs['accent'], 'on-accent': hs['on-accent']}), first_fail)
            moves.append(f'{mode}: no lightness in reach passes every check; left as settled for the checks to report')
        off, cand, near = chosen
        if off:
            moves.append(f"{mode} accent {hs['accent']} -> {cand['accent']} (lightness {L0:.2f} -> {L0 + off:.2f}, rule step 6): "
                         f"as settled it was {first_fail[0]:.2f} from {str(first_fail[1]).capitalize()} for colour-blind readers, under 5.0")
        cand['signature'] = OVERRIDES.get((name, mode, 'signature'), hs.get('signature', cand['accent']))
        cand['word'] = hs.get('header-ink', cand['ink'])
        cand['page'] = cand['surface']
        out[mode] = cand
        placed[mode][name] = cand['accent']
    return out, moves

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
        if name in SETTLED:
            products[name], moves = derive_settled(name, placed)
            record[name] = {'source': src, 'moves': moves}
            continue
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
    for name in ORDER:
        for mode in ('light', 'dark'):
            c = products[name][mode]
            apply_review(name, mode, c, NEUTRAL_ROLES)
            c.update(header_roles(name, mode, c, products))
            apply_review(name, mode, c, ('glow-core', 'glow-mid', 'gel'))
            c.update(mode_roles(c, mode))
            for (p_, m, role), v in OVERRIDES.items():
                if p_ == name and m == mode and role in ('mode', 'on-mode'):
                    c[role] = v
            if (name, mode, 'gel') in OVERRIDES:
                c['gel'] = OVERRIDES[(name, mode, 'gel')]
                continue
            if (name, mode, 'gel') in REVIEW:
                continue
            g0 = c['gel']
            L, C, H = oklch(g0)
            step = 0.01 if mode == 'dark' else -0.01
            for _ in range(30):
                if min(gel_label_contrasts(c).values()) >= 4.5:
                    break
                L += step
                c['gel'] = hexof(L, C, H)
            if c['gel'] != g0:
                worst = min(gel_label_contrasts({**c, 'gel': g0}).items(), key=lambda kv: kv[1])
                record[name]['moves'].append(f"{mode} gel {g0} -> {c['gel']} (lightness {oklch(g0)[0]:.2f} -> {L:.2f}): "
                                             f"its label read {worst[1]:.2f} at the {worst[0]}")
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
    rows.extend(type_checks())
    for prod, mode, c in palettes():
        rows.extend(header_checks(prod, mode, c))
        rows.extend(toggle_checks(prod, mode, c))
        rows.extend(alert_checks(prod, mode, c))
        advisories.append(f"{prod} {mode}: corner glow core {c['glow-core']} is {contrast(c['glow-core'], c['ground']):.2f}:1 against the ground (how much the glow shows)")
    for name, rec in record.items():
        for m in rec['moves']:
            advisories.append(f'{name}: {m}')
    advisories.extend(theme_file_advisories())
    return rows, advisories

def over(top, a, bottom):
    t, b = _rgb(top), _rgb(bottom)
    return '#%02x%02x%02x' % tuple(round(a * x + (1 - a) * y) for x, y in zip(t, b))

def header_surfaces(c):
    """What the header's text and controls sit on, as drawn: the lit sheet over the ground tint over
    the glow (or the ground, away from it). Returns the glass at the left and at the glow's core."""
    g = SHARED['header']['glass']
    tint = g['tint'] / 100
    sheet_a = int('12', 16) / 255
    left = over('#ffffff', sheet_a, over(c['ground'], tint, c['ground']))
    corner = over('#ffffff', sheet_a, over(c['ground'], tint, over(c['glow-core'][:7], 1, c['ground'])))
    return left, corner

def header_bare(c):
    """The header's weakest ground: no glow, and its lit sheet at its faint end (2%). Any control can
    end up here at some width, so a control's text is measured here too (R18, version 4.2)."""
    tint = SHARED['header']['glass']['tint'] / 100
    return over('#ffffff', 0x04 / 255, over(c['ground'], tint, c['ground']))

GEL_LABEL_BAND = (7 / 34, 27 / 34)   # the label's line box inside the 34 px button: where text can sit

def gel_label_contrasts(c):
    """on-gel against the gel at the top and bottom of its label band, over the glow's core and over
    clear glass (where a narrow header puts the gel, past the glow's reach)."""
    gl = SHARED['header']['gel']
    left, corner = header_surfaces(c)
    top_a, bottom_a = 0x48 / 255, 0x0d / 255
    out = {}
    for where, back in (('over the glow', corner), ('over clear glass', left)):
        gel = over(c['gel'], gl['alpha'] / 100, back)
        for edge, y in zip(('top', 'bottom'), GEL_LABEL_BAND):
            a = top_a + (bottom_a - top_a) * y
            out[f'{edge} of the label {where}'] = contrast(c['on-gel'], over('#ffffff', a, gel))
    # version 4.2: the gel over the header's bare ground, at its very top and its foot
    gel = over(c['gel'], gl['alpha'] / 100, header_bare(c))
    out['top of the gel over bare ground'] = contrast(c['on-gel'], over('#ffffff', top_a, gel))
    out['foot of the gel over bare ground'] = contrast(c['on-gel'], over('#ffffff', bottom_a, gel))
    return out

def header_button_text(c):
    """R18: text on the header's buttons against the header's bare ground: the gel's label at its top
    and foot, and words in a frosted button (an account name, say) at the frost's faint end."""
    out = {k: v for k, v in gel_label_contrasts(c).items() if 'bare ground' in k}
    bare = header_bare(c)
    if c.get('frost-tint', 'transparent') == 'transparent' or 'color-mix' not in str(c.get('frost-tint', '')):
        frost = over('#ffffff', 0x55 / 255, bare)                          # light: white fading to 33%
    else:
        frost = over('#ffffff', 0x08 / 255, over(c['header-tint'], 0.45, bare))   # dark: the tint, white fading to 3%
    out['words in a frosted button over bare ground'] = contrast(c['frost-ink'], frost)
    return out

def header_checks(prod, mode, c):
    """R16: the glass header. Its text on the glass, the folio bar on it, the gel button's label at both
    ends of its sheen over the glow, and the frosted switch's icon."""
    rows = []
    def need(what, fg, bg, floor):
        r = contrast(fg, bg)
        rows.append(('R16', prod, mode, what, round(r, 2), floor, r >= floor))
    left, corner = header_surfaces(c)
    need('header ink on the glass', c['header-ink'], left, 4.5)
    need('header ink at 82% (a tab not selected) on the glass', over(c['header-ink'], 0.82, left), left, 4.5)
    need('folio bar (signature) on the glass', c['signature'], left, 3.0)
    for what, r in gel_label_contrasts(c).items():
        if 'bare ground' not in what:
            rows.append(('R16', prod, mode, f'on-gel at the {what}', round(r, 2), 4.5, r >= 4.5))
    for what, r in header_button_text(c).items():
        rows.append(('R18', prod, mode, f'text at the {what}', round(r, 2), 4.5, r >= 4.5))
    if mode == 'dark':
        frost = over('#ffffff', 0x22 / 255, over(c['header-tint'], 0.45, corner))
    else:
        frost = over('#ffffff', 0xa8 / 255, corner)
    need('switch icon (frost-ink) on the frosted button by the glow', c['frost-ink'], frost, 3.0)
    return rows

def toggle_checks(prod, mode, c):
    """R17: a toggle's state reads without colour vision and against every surface: the on track at
    3:1 on the surfaces it sits on, its thumb 3:1 on it, the off thumb and outline 3:1 on theirs."""
    rows = []
    on, thumb_on = c[ALIASES['toggle-on']], c[ALIASES['toggle-thumb-on']]
    off, thumb_off = c[ALIASES['toggle-off']], c[ALIASES['toggle-thumb-off']]
    for bg in ('surface', 'ground', 'raised', 'float'):
        r = contrast(on, c[bg])
        rows.append(('R17', prod, mode, f'toggle on (track) on {bg}', round(r, 2), 3.0, r >= 3.0))
        r = contrast(c['edge-control'], c[bg])
        rows.append(('R17', prod, mode, f'toggle off (outline) on {bg}', round(r, 2), 3.0, r >= 3.0))
    r = contrast(thumb_on, on)
    rows.append(('R17', prod, mode, 'thumb on the on track', round(r, 2), 3.0, r >= 3.0))
    r = contrast(thumb_off, off)
    rows.append(('R17', prod, mode, 'thumb on the off track', round(r, 2), 3.0, r >= 3.0))
    return rows

def alert_checks(prod, mode, c):
    """R19: the alert reads as an alert and its words read: its heading and sentence at 4.5:1 on the
    alert tint, the icon's mark at 4.5:1 on its disc, and the alert edge at 3:1 on the tint and on
    the card or page it sits on."""
    rows = []
    def need(what, fg, bg, floor):
        r = contrast(fg, bg)
        rows.append(('R19', prod, mode, what, round(r, 2), floor, r >= floor))
    for level, role in (('failed', 'danger'), ('attention', 'warning'), ('worked', 'success')):
        need(f'{level} notice heading ({role}-ink) on its tint', c[f'{role}-ink'], c[f'{role}-tint'], 4.5)
        need(f'{level} notice sentence (ink) on its tint', c['ink'], c[f'{role}-tint'], 4.5)
        need(f'{level} notice icon mark (on-{role}) on its mark', c[f'on-{role}'], c[role], 4.5)
        need(f'{level} notice edge ({role}-ink) on its tint', c[f'{role}-ink'], c[f'{role}-tint'], 3.0)
        for bg in ('surface', 'ground', 'raised', 'float'):
            need(f'{level} notice edge ({role}-ink) on {bg}', c[f'{role}-ink'], c[bg], 3.0)
    # R21: the mode strip, seen at a glance and read, on the weakest ground it meets
    for what, fg, bg, floor in (('mode strip words (on-mode) on the band', c['on-mode'], c['mode'], 7.0),
                                ('mode strip band against the page ground', c['mode'], c['ground'], 3.0),
                                ('mode strip band against the header\'s bare ground', c['mode'], header_bare(c), 3.0)):
        r = contrast(fg, bg)
        rows.append(('R21', prod, mode, what, round(r, 2), floor, r >= floor))
    # R22: status in a row: the word on its tint, the icon on its tint
    for st, tint, ink, mark in (('waiting', 'neutral-tint', 'neutral-ink', 'neutral'), ('done', 'done-tint', 'done-ink', 'done'),
                                ('held', 'warning-tint', 'warning-ink', 'warning'), ('refused', 'danger-tint', 'danger-ink', 'danger'),
                                ('unknown', 'neutral-tint', 'neutral-ink', 'neutral')):
        r = contrast(c[ink], c[tint])
        rows.append(('R22', prod, mode, f'{st} status word on its tint', round(r, 2), 4.5, r >= 4.5))
        r = contrast(c[mark], c[tint])
        rows.append(('R22', prod, mode, f'{st} status icon on its tint', round(r, 2), 3.0, r >= 3.0))
    return rows

def type_checks():
    """R12-R15: which face sets what, what each face can do, and each licence as read from its file."""
    rows = []
    for name, (step, weight, face, track, upper, tab) in TYPE.items():
        f = font_for(face)
        frame = name in FRAME_ROLES
        rows.append(('R12', 'type', name, f'{f["face"]} on a {"frame" if frame else "content"} role',
                     face, 'display only on frame roles, and every frame role display', (face == 'display') == frame))
        if face == 'display':
            rows.append(('R12', 'type', name, 'frame role asks for no figures', tab, 'no tabular', not tab))
        rows.append(('R13', 'type', name, f'{f["face"]} at weight {weight}', weight, f['weights'], weight in f['weights']))
        rows.append(('R13', 'type', name, f'native cut for {face} {weight}', NATIVE_FACES.get((face, weight)), 'bundled', (face, weight) in NATIVE_FACES))
        if tab:
            rows.append(('R14', 'type', name, f'figures line up in {f["face"]}', f['figures'], 'tabular or monospaced', f['figures_line_up']))
    rng = unicode_range_without(NUMBER_CHARS)
    spans = [(int(r[2:].split('-')[0], 16), int(r[2:].split('-')[-1], 16)) for r in rng.split(', ')]
    lost = [c for c in NUMBER_CHARS if any(lo <= ord(c) <= hi for lo, hi in spans)]
    rows.append(('R12', 'type', 'web', "the display face's unicode-range leaves out every character of a number", ''.join(lost) or 'none left in', 'none', not lost))
    for f in FONTS:
        path = FONT_DIR / f['licence_file']
        if not path.exists():
            rows.append(('R15', 'font', f['face'], f'licence file {f["licence_file"]}', 'missing', 'read', False))
            continue
        text = path.read_text(errors='replace')
        head = text.split('This Font Software is licensed')[0]
        rows.append(('R15', 'font', f['face'], 'OFL 1.1 in its own licence file', 'SIL OPEN FONT LICENSE Version 1.1' in text, True, 'SIL OPEN FONT LICENSE Version 1.1' in text))
        rows.append(('R15', 'font', f['face'], 'copyright as recorded', f['copyright'], 'in the file', f['copyright'] in head))
        m = re.search(r'Reserved Font Names?\s+"?([^"\n.]+)"?', head)
        found = m.group(1).strip() if m else None
        rows.append(('R15', 'font', f['face'], 'reserved name as recorded', f'{found!r} in the file, {f["reserved_name"]!r} recorded', 'equal', found == f['reserved_name']))
    return rows

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
    for k, f in FACES.items():
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
    for name, (step, weight, face, track, _u, _tab) in TYPE.items():
        size, lh = type_size(step)
        v[f'type-{name}'] = f'{weight} {size:g}px/{lh}px var(--hw-font-{face})'
        if track:
            v[f'tracking-{name}'] = f'{track}em'
    v['focus-width'] = f"{s['focus']['width']}px"
    v['focus-offset'] = f"{s['focus']['offset']}px"
    h = s['header']
    v['header-height'] = f"{h['height']}px"
    v['header-control'] = f"{h['control']}px"
    v['glass-sheet'] = h['glass']['sheet']
    v['glass-tint'] = f"{h['glass']['tint']}%"
    v['glass-blur'] = f"{h['glass']['blur']}px"
    v['glass-edge'] = h['glass']['edge']
    v['glass-shadow'] = h['glass']['shadow']
    for k, val in h['glow'].items():
        v[f'glow-{k}'] = val
    v['gel-alpha'] = f"{h['gel']['alpha']}%"
    v['gel-sheet'] = h['gel']['sheet']
    v['gel-shadow'] = h['gel']['shadow']
    v['gel-filter'] = f"blur({h['gel']['blur']}px) saturate({h['gel']['saturate']})"
    v['frost-filter'] = f"blur({h['frost']['blur']}px) saturate({h['frost']['saturate']})"
    for k, n in s['toggle'].items():
        v[f'toggle-{k}'] = f'{n}px'
    return v

def alias_block():
    d = {k: f'var(--hw-{t})' for k, t in ALIASES.items()}
    d['signature'] = 'var(--hw-accent)'
    d['accent-fill'] = 'linear-gradient(180deg, var(--hw-accent-top) 0%, var(--hw-accent) 100%)'
    d['accent-fill-hover'] = 'linear-gradient(180deg, var(--hw-accent-hover-top) 0%, var(--hw-accent-hover) 100%)'
    d['danger-fill'] = 'linear-gradient(180deg, var(--hw-danger-top) 0%, var(--hw-danger) 100%)'
    d['glow'] = ('radial-gradient(ellipse var(--hw-glow-reach-x) var(--hw-glow-reach-y) at var(--hw-glow-origin), '
                 'var(--hw-glow-core) 0%, var(--hw-glow-core) var(--hw-glow-core-stop), var(--hw-glow-mid) var(--hw-glow-mid-stop), transparent 100%)')
    d['gel-fill'] = 'var(--hw-gel-sheet), color-mix(in srgb, var(--hw-gel) var(--hw-gel-alpha), transparent)'
    d['glass-tint-colour'] = 'color-mix(in srgb, var(--hw-ground) var(--hw-glass-tint), transparent)'
    d['gel-edge'] = 'color-mix(in srgb, var(--hw-gel) 55%, #ffffff 45%)'
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
     Toggles, never checkboxes: <button type="button" role="switch" aria-checked class="hw-toggle">.
     A figure inside a display-face label (a price on a button): <span class="hw-fig">.
     Notices: .hw-notice (failed, .attention, .worked; .hw-alert is failed), .hw-mode above the header.
     Status in a row: .hw-status[data-status=waiting|done|held|refused|unknown]. Sign-in: .hw-signin*.
     Type: one class per role, .hw-text-<role> (or font: var(--hw-type-<role>) plus its tracking).
           The display face sets the frame roles only and never a digit (tokens.json behaviour.type);
           the ui face sets content, numbers and data included, in figures that line up.
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
        out.append(f"/* {src['label']}. From {src['theme']}{' (inferred)' if src.get('inferred') else ''}."
                   + (' Settled by its owner.' if name in SETTLED else '')
                   + (f" PENDING: {src['pending']}" if src.get('pending') else '') + ' */')
        blocks = []
        for mode in ('light', 'dark'):
            c = products[name][mode]
            v = colour_vars(c, mode, full=False)
            for k in ('signature', 'word', 'edge-accent', 'page'):
                if k in c and not (k == 'signature' and c[k] == c['accent']) and not (k == 'word' and c[k] == c['ink']) \
                        and not (k == 'page' and c[k] == c['ground']):
                    v[k] = c[k]
            blocks.append(v)
        reach = {f'glow-{k}': v for k, v in glow_reach(name).items() if v != SHARED['header']['glow'][k]}
        out.append(css_block(f'[data-product="{name}"]', {**blocks[0], **reach}))
        out.append(css_block(f'.dark[data-product="{name}"], .dark [data-product="{name}"], [data-product="{name}"] .dark', blocks[1]))
    out.append(SIG_CSS)
    out.append(HEADER_CSS)
    out.append(TOGGLE_CSS)
    out.append(PATTERN_CSS)
    out.append(type_css())
    return '\n\n'.join(out) + '\n'

HEADER_CSS = r'''
/* ════════════════════════════════════════════════════════════════════════════
   5 · The glass header
   On the recipe of Terminal Delight's docs site (docsite/redesign/redesign.css): a faint lit
   sheet over the ground, a hairline edge and a soft shadow below in place of a hard line.
   The old-tree glow starts in the top right corner, behind the gel button, and fades left and
   down, leaving the wordmark on clear glass. Two rows: the wordmark, the switch and the gel;
   then the tabs, with the selected one as the folio tab, open into the page below.
   ════════════════════════════════════════════════════════════════════════════ */
.hw-header {
  position: relative; z-index: 2; isolation: isolate; min-height: var(--hw-header-height);
  display: flex; flex-direction: column; justify-content: space-between;
  color: var(--hw-header-ink); background: var(--hw-ground);
  border-bottom: 1px solid var(--hw-glass-edge);
  box-shadow: var(--hw-glass-shadow);
}
/* Under the content: the corner glow, softened by the glass's blur and kept inside the header,
   then the glass itself (the ground at 26% and the faint lit sheet) over it. */
.hw-header::before, .hw-header::after { content: ""; position: absolute; inset: 0; z-index: -1; pointer-events: none; }
.hw-header::before { background: var(--hw-glow); filter: blur(var(--hw-glass-blur)); clip-path: inset(0); }
.hw-header::after { background: var(--hw-glass-sheet), var(--hw-glass-tint-colour); }
.hw-header-row { display: flex; align-items: center; gap: 12px; padding: 12px 16px 8px; }
.hw-header-row > .hw-end { margin-left: auto; display: flex; align-items: center; gap: 12px; }
.hw-header .hw-word { font: var(--hw-type-wordmark); letter-spacing: var(--hw-tracking-wordmark); text-transform: uppercase;
  color: var(--hw-word); white-space: nowrap; }
.hw-header-tabs { display: flex; align-items: flex-end; gap: 16px; padding: 0 16px; white-space: nowrap; }
.hw-header .hw-tab { font: var(--hw-type-tab); color: inherit; opacity: .82; padding: 6px 2px 9px; text-decoration: none; }
/* The folio tab in the header: the page's colour, the bar over its words, the chip; it covers the
   hairline and opens the shadow below it, so it still joins the page. */
.hw-header .hw-folio { opacity: 1; padding: 6px 15px 9px; margin-bottom: -1px; position: relative; z-index: 1;
  background: var(--hw-page); color: var(--hw-ink); border-left: 0;
  clip-path: polygon(0 0, calc(100% - var(--hw-folio-chip)) 0, 100% var(--hw-folio-chip), 100% calc(100% + var(--hw-pad-page)), 0 calc(100% + var(--hw-pad-page))); }
.hw-header .hw-folio::after { display: none; }
/* It stops at the page's padding, so it can never lie over content. */
.hw-header .hw-folio::before { content: ""; position: absolute; left: 0; right: 0; top: 100%; height: var(--hw-pad-page);
  background: linear-gradient(var(--hw-page) 35%, color-mix(in srgb, var(--hw-page) 0%, transparent)); pointer-events: none; }
/* Frosted round button (the theme switch lives here) and the gel button: 34 px to the eye, 44 px to the hand. */
.hw-frost, .hw-gel { position: relative; height: var(--hw-header-control); border-radius: var(--hw-radius-pill);
  display: inline-grid; place-items: center; flex: none; cursor: pointer; }
.hw-frost::before, .hw-gel::before { content: ""; position: absolute; inset: calc((var(--hw-header-control) - var(--hw-size-target)) / 2); }
.hw-frost { width: var(--hw-header-control); color: var(--hw-frost-ink);
  -webkit-backdrop-filter: var(--hw-frost-filter); backdrop-filter: var(--hw-frost-filter);
  background: var(--hw-frost-sheet), var(--hw-frost-tint); border: 1px solid var(--hw-frost-edge); box-shadow: var(--hw-frost-shadow); }
.hw-frost svg { width: 16px; height: 16px; }
.hw-gel { padding: 0 17px; font: var(--hw-type-gel); color: var(--hw-on-gel); white-space: nowrap;
  -webkit-backdrop-filter: var(--hw-gel-filter); backdrop-filter: var(--hw-gel-filter);
  background: var(--hw-gel-fill); border: 1px solid var(--hw-gel-edge); box-shadow: var(--hw-gel-shadow); }
'''

TOGGLE_CSS = r'''
/* ════════════════════════════════════════════════════════════════════════════
   6 · Toggles, in place of every checkbox. One control per decision, its label on the left, the toggle on
   the right; 44 px to the hand. Markup: <button type="button" role="switch" aria-checked="false"
   class="hw-toggle" aria-labelledby="..."></button>; a form keeps the value in a hidden input.
   Several choices from a list are selectable rows (the selected tint and a check icon), never boxes.
   ════════════════════════════════════════════════════════════════════════════ */
.hw-toggle { position: relative; flex: none; box-sizing: border-box; width: var(--hw-toggle-width); height: var(--hw-toggle-height);
  padding: 0; border-radius: var(--hw-radius-pill); cursor: pointer;
  background: var(--hw-toggle-off); border: 1px solid var(--hw-edge-control);
  transition: background-color var(--hw-dur-2) var(--hw-ease), border-color var(--hw-dur-2) var(--hw-ease); }
.hw-toggle::before { content: ""; position: absolute; left: 0; right: 0;
  top: calc((var(--hw-toggle-height) - var(--hw-size-target)) / 2 - 1px); bottom: calc((var(--hw-toggle-height) - var(--hw-size-target)) / 2 - 1px); }
.hw-toggle::after { content: ""; position: absolute; top: calc(var(--hw-toggle-inset) - 1px); left: calc(var(--hw-toggle-inset) - 1px);
  width: var(--hw-toggle-thumb); height: var(--hw-toggle-thumb); border-radius: 50%;
  background: var(--hw-toggle-thumb-off); box-shadow: 0 1px 2px rgb(0 0 0 / .28);
  transition: transform var(--hw-dur-2) var(--hw-ease), background-color var(--hw-dur-2) var(--hw-ease); }
.hw-toggle[aria-checked="true"] { background: var(--hw-toggle-on); border-color: var(--hw-toggle-on); }
.hw-toggle[aria-checked="true"]::after { background: var(--hw-toggle-thumb-on);
  transform: translateX(calc(var(--hw-toggle-width) - var(--hw-toggle-thumb) - 2 * var(--hw-toggle-inset))); }
.hw-toggle:disabled, .hw-toggle[aria-disabled="true"] { cursor: not-allowed; background: var(--hw-inset); border-color: var(--hw-edge); }
.hw-toggle:disabled::after, .hw-toggle[aria-disabled="true"]::after { background: var(--hw-edge); box-shadow: none; }
.hw-toggle:disabled[aria-checked="true"], .hw-toggle[aria-disabled="true"][aria-checked="true"] { background: var(--hw-accent-tint); border-color: var(--hw-edge); }
.hw-toggle-row { display: flex; align-items: center; justify-content: space-between; gap: var(--hw-space-4);
  min-height: var(--hw-size-target); font: var(--hw-type-body); color: var(--hw-ink); }
.hw-toggle-row [data-hint] { display: block; font: var(--hw-type-meta); color: var(--hw-ink-3); }
'''

PATTERN_CSS = r'''
/* ════════════════════════════════════════════════════════════════════════════
   7 · Notices: one pattern, four levels (4.3). The alert of 4.2 is its loudest level.
   failed     something went wrong      danger roles    role="alert"   under the button pressed, or top of its panel
   attention  something needs you       warning roles   role="status"  top of the section it concerns, until resolved
   mode       you are in an unusual mode the mode band  a region       a strip above the header, on every page
   worked     it worked, and nothing    success roles   role="status"  where the action was; only when the result
              else on screen shows it                                  is not otherwise visible
   A block: an icon, a Federo heading naming what happened (no figures), one Plex sentence saying what
   to do or what it means. Never a notice: a field's own error (its hint), a routine save (the state
   shows itself), a row's state (.hw-status), a question before a destructive act (a dialog), tips,
   news or promotion, loading, an empty page.
   <div class="hw-notice attention" role="status"><span class="hw-notice-icon" aria-hidden="true"></span>
     <div><p class="hw-notice-title">The card on file expires this month</p>
     <p class="hw-notice-text">Ask the client for a new card at their next visit.</p></div></div>
   ════════════════════════════════════════════════════════════════════════════ */
.hw-notice, .hw-alert { --n-tint: var(--hw-danger-tint); --n-edge: var(--hw-danger-edge); --n-mark: var(--hw-danger);
  --n-on-mark: var(--hw-on-danger); --n-ink: var(--hw-danger-ink);
  display: flex; gap: var(--hw-space-3); align-items: flex-start; padding: var(--hw-space-4);
  background: var(--n-tint); color: var(--hw-ink); border: 1px solid var(--n-edge);
  border-left: 4px solid var(--n-ink); border-radius: var(--hw-radius-control); }   /* the edge in the level's ink: 3:1 on any ground */
.hw-notice.attention { --n-tint: var(--hw-warning-tint); --n-edge: var(--hw-warning-edge); --n-mark: var(--hw-warning);
  --n-on-mark: var(--hw-on-warning); --n-ink: var(--hw-warning-ink); }
.hw-notice.worked { --n-tint: var(--hw-success-tint); --n-edge: var(--hw-success-edge); --n-mark: var(--hw-success);
  --n-on-mark: var(--hw-on-success); --n-ink: var(--hw-success-ink); }
.hw-notice-icon, .hw-alert-icon { flex: none; width: 24px; height: 24px; margin-top: 1px; display: grid; place-items: center;
  border-radius: 50%; background: var(--n-mark); color: var(--n-on-mark); font: 600 14px/1 var(--hw-font-ui); }
.hw-notice-icon::before { content: "!"; }                    /* failed: a disc with ! */
.hw-alert-icon::before { content: none; }
.hw-notice.attention .hw-notice-icon { border-radius: 0; clip-path: polygon(50% 4%, 100% 96%, 0 96%); padding-top: 6px; }  /* a triangle */
.hw-notice.worked .hw-notice-icon::before { content: "\2713"; }   /* a check */
.hw-notice-title, .hw-alert-title { margin: 0; font: var(--hw-type-alert-title); color: var(--n-ink); }
.hw-notice-text, .hw-alert-text { margin: var(--hw-space-1) 0 0; font: var(--hw-type-body); color: var(--hw-ink); }

/* The mode strip: you are acting for someone else (or on a test instance). It belongs with the
   header: directly above it, full width, sticky with it, on every page while the mode lasts, never
   dismissable; its one action leaves the mode. Above, not below, so the folio tab still opens into
   the page. Inverse to the page, in the product's deep tone, so it
   is seen at a glance without a status colour. Names are content, so its words are Plex; its button
   is Federo. Also prefix the page title: "Acting for Riverside Physio · Stone".
   <div class="hw-mode" role="region" aria-label="Acting for Riverside Physio"><span class="hw-mode-icon" aria-hidden="true"></span>
     <p class="hw-mode-text"><b>You are Maria Ruiz, Head Waters staff, in Riverside Physio's Stone.</b> Everything you do here is recorded.</p>
     <button class="hw-mode-action">Stop acting</button></div> */
.hw-mode { display: flex; align-items: center; gap: var(--hw-space-3); min-height: 40px; padding: 6px 16px;
  background: var(--hw-mode); color: var(--hw-on-mode); }
.hw-mode-icon { flex: none; width: 18px; height: 18px; border: 2px solid currentColor; border-radius: 50% 50% 4px 4px; opacity: .9; }
.hw-mode-text { flex: 1; margin: 0; font: var(--hw-type-meta); color: var(--hw-on-mode); }
.hw-mode-text b { font-weight: 600; }
.hw-mode-action { position: relative; flex: none; padding: 4px 12px; border-radius: var(--hw-radius-pill); cursor: pointer;
  font: var(--hw-type-button-small); color: var(--hw-on-mode); background: transparent; border: 1px solid currentColor; }
.hw-mode-action::before { content: ""; position: absolute; inset: -8px 0; }

/* Status in a row: one vocabulary for Sent, payments, Today. A word and an icon, never colour alone.
   waiting  (neutral)  queued, going out, booked, scheduled, not yet due       a clock
   done     (done)     delivered, paid, signed, attended                        a check
   held     (warning)  not sent or not taken, on purpose, with its reason beside it: held by a test
                       instance, no consent, on hold                            a pause
   refused  (danger)   the other side said no or it failed: bounced, declined, refused   a cross
   unknown  (neutral, dashed)  no answer yet, and we will not guess                 a question mark
   <span class="hw-status" data-status="held">Held</span> <span class="hw-status-why">a test server sends only to people who sign in</span> */
.hw-status { --s-tint: var(--hw-neutral-tint); --s-ink: var(--hw-neutral-ink); --s-mark: var(--hw-neutral); --s-edge: var(--hw-neutral-edge);
  display: inline-flex; align-items: center; gap: 6px; padding: 2px 10px 2px 8px; border-radius: var(--hw-radius-pill);
  font: 600 13px/20px var(--hw-font-ui); color: var(--s-ink); background: var(--s-tint); border: 1px solid var(--s-edge); white-space: nowrap; }
.hw-status::before { flex: none; font: 700 12px/1 var(--hw-font-ui); color: var(--s-mark); content: "\25F7"; }
.hw-status[data-status="done"] { --s-tint: var(--hw-done-tint); --s-ink: var(--hw-done-ink); --s-mark: var(--hw-done); }
.hw-status[data-status="done"]::before { content: "\2713"; }
.hw-status[data-status="held"] { --s-tint: var(--hw-warning-tint); --s-ink: var(--hw-warning-ink); --s-mark: var(--hw-warning); --s-edge: var(--hw-warning-edge); }
.hw-status[data-status="held"]::before { content: "\2016"; }
.hw-status[data-status="refused"] { --s-tint: var(--hw-danger-tint); --s-ink: var(--hw-danger-ink); --s-mark: var(--hw-danger); --s-edge: var(--hw-danger-edge); }
.hw-status[data-status="refused"]::before { content: "\2715"; }
.hw-status[data-status="unknown"] { border-style: dashed; }
.hw-status[data-status="unknown"]::before { content: "?"; }
.hw-status-why { font: var(--hw-type-meta); color: var(--hw-ink-3); }

/* ════════════════════════════════════════════════════════════════════════════
   8 · The sign-in page: the same in every app. A one-row glass header naming the product, one
   card: the title "Sign in to <Product>" in Federo, one line saying which account, the Google
   button with Google's own "G" on a white square inside it (Google asks for the mark; it is never
   recoloured), and the alert under it after a refusal. Only what works on this instance: with
   password sign-in off there is no field, no "or", no "Forgot password?".
   ════════════════════════════════════════════════════════════════════════════ */
.hw-header.single { min-height: var(--hw-size-bar); justify-content: center; }
@media (max-width: 599px) { .hw-header.single { min-height: var(--hw-size-bar-phone); } }
.hw-signin { background: var(--hw-ground); color: var(--hw-ink);
  padding: clamp(24px, 14vh, 128px) var(--hw-pad-page-phone) var(--hw-space-7); }
.hw-signin-card { box-sizing: border-box; max-width: 400px; margin: 0 auto; display: flex; flex-direction: column; gap: var(--hw-gap-group);
  padding: var(--hw-pad-card); background: var(--hw-surface-fill); border: 1px solid var(--hw-edge);
  border-top: var(--hw-folio-bar) solid var(--hw-signature); border-radius: var(--hw-radius-card); box-shadow: var(--hw-elev-1); }
@media (max-width: 599px) { .hw-signin-card { padding: var(--hw-pad-card-phone); } }
.hw-signin-title { margin: 0; font: var(--hw-type-title-section); color: var(--hw-ink); }
.hw-signin-lead { margin: calc(-1 * var(--hw-space-2)) 0 0; font: var(--hw-type-body); color: var(--hw-ink-2); }
.hw-signin-or { display: flex; align-items: center; gap: var(--hw-space-3); font: var(--hw-type-meta); color: var(--hw-ink-3); }
.hw-signin-or::before, .hw-signin-or::after { content: ""; flex: 1; border-top: 1px solid var(--hw-edge); }
.hw-signin-g { flex: none; display: inline-grid; place-items: center; width: 26px; height: 26px; margin-right: var(--hw-space-3);
  border-radius: 4px; background: #ffffff; }
.hw-signin-g svg { width: 18px; height: 18px; }
'''

def type_css():
    lines = ['''/* ════════════════════════════════════════════════════════════════════════════
   4 · Type: one class per role, carrying its face, size, case, tracking and figures
   ════════════════════════════════════════════════════════════════════════════ */
/* Nothing is faked: a display face with one weight and no italic draws as it is when bold or
   italic is asked of it, instead of being smeared. It inherits from the root. */
:root { font-synthesis: none; }''']
    for name, (step, weight, face, track, upper, tab) in TYPE.items():
        d = [f'font: var(--hw-type-{name})']
        if track:
            d.append(f'letter-spacing: var(--hw-tracking-{name})')
        if upper:
            d.append('text-transform: uppercase')
        if tab:
            d.append('font-variant-numeric: tabular-nums lining-nums')
        lines.append(f'.hw-text-{name} {{ {"; ".join(d)}; }}')
    lines.append('/* A figure inside a display-face string (a price on a pay button): the text face, same size. */')
    lines.append('.hw-fig { font-family: var(--hw-font-ui); font-weight: 400; font-variant-numeric: tabular-nums lining-nums; letter-spacing: 0; text-transform: none; }')
    return '\n'.join(lines)

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
        size, lh = type_size(step)
        t = {'face': face, 'fontFamily': NATIVE_FACES.get((face, weight)), 'size': size, 'lineHeight': lh,
             'weight': str(weight), 'letterSpacing': round(track * size, 2)}
        if upper:
            t['textTransform'] = 'uppercase'
        if tab:
            t['fontVariant'] = ['tabular-nums']
        typ[name] = t
    return {
        '$description': 'Plain numbers for a native theme (React Native, iPad, Android, Mac). Sizes are dp/pt, equal to CSS px. Fills are solid on native.',
        'font': {css: {'face': font_for(css)['face'], 'bundle': sorted(n for (f, _w), n in NATIVE_FACES.items() if f == css),
                       'licence': font_for(css)['licence'] + (f', Reserved Font Name "{font_for(css)["reserved_name"]}": bundle the file as published, never a subset' if font_for(css)['reserved_name'] else '')}
                 for css in [f['css'] for f in FONTS]},
        'type': typ,
        'space': num(s['space']), 'gap': num(s['gap']), 'pad': num(s['pad']), 'size': num(s['size']),
        'radius': num(s['radius']), 'focus': dict(s['focus']), 'folio': dict(s['folio']), 'line': dict(s['line']),
        'toggle': {**s['toggle'], 'hit': {'ios': s['size']['target'], 'android': s['size']['target-android']},
                   'track_on': 'accent', 'thumb_on': 'on-accent', 'track_off': 'inset', 'outline_off': 'edge-control', 'thumb_off': 'edge-control',
                   'role': 'switch (accessibilityRole="switch", accessibilityState={ checked })', 'never': 'a checkbox (expo-checkbox or any other)'},
        'button_label': 'the display face for the words; a run of figures inside the label in the text face at the same size; a label that is only a number is data (type-data)',
        'header': {'height': s['header']['height'], 'control': s['header']['control'], 'hit': s['size']['target'],
                   'glow': 'draw with react-native-svg: a RadialGradient centred on the top right corner, rx products.<name>.header_glow.reach-x of the width (base 38%), ry reach-y of the height (base 112%); stops glow-core at 0 and 0.14, glow-mid at 0.46, transparent at 1',
                   'glass': 'opaque on native: the ground, the glow, then white at 7% fading to 2%; expo-blur only for the frosted controls',
                   'edge': {'width': 1, 'color': '#ffffff', 'alpha': 0.125}, 'shadow': {'y': 14, 'blur': 34, 'alpha': 0.33}},
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

def type_behaviour():
    disp = font_for('display')
    return {
        '$description': 'Which face sets what. The display face sets only the frame roles, words the product ships; content, including a person\'s or record\'s name where a title goes, is the ui face; digits that line up are the figures face.',
        'frame_roles': list(FRAME_ROLES),
        'digits': f'No digit, price, time, date, count, table cell or form value is ever set in {disp["face"]}. On the web the net below draws any that slip through in the next face of the stack; scripts/frame-digits.js finds them on a rendered screen.',
        'unicode_range': unicode_range_without(NUMBER_CHARS),
        'unicode_range_use': f'put it on {disp["face"]}\'s @font-face (next/font/local: declarations: [{{ prop: "unicode-range", value: <this> }}])',
        **TYPE_NOTES,
    }

def build_json():
    s = SHARED
    products, record = derive_all()
    j = {
        '$description': f'{FAMILY} family tokens. Each product colour derives from an Omarchy theme by the rule in tokens.py; products.<name>.source records the theme, its licence, the colours read, and every lightness the rule moved.',
        'shared': {
            'font': {k: tok(v, 'fontFamily', f'--hw-font-{k}') for k, v in FACES.items()},
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
            'header': {'$description': 'The glass header, after Terminal Delight\'s docs site (github.com/parker-brown-family/terminal-delight, docsite/redesign/redesign.css). It paints its own ground, glow and glass, so it looks the same wherever it sits; its frosted controls blur the glow behind them.',
                       **SHARED['header']},
            'color': {'light': color_group(resolve(dict(LIGHT))), 'dark': color_group(resolve(dict(DARK)))},
        },
        'products': {},
        'behaviour': {**BEHAVIOUR, 'type': type_behaviour()},
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
                       'why': src['why'], 'inferred': src['inferred'], 'moves': rec['moves'], 'settled': name in SETTLED,
                       **({'review': REVIEW_WHY[name]} if name in REVIEW_WHY else {}),
                       **({'also_from': src['also']} if src.get('also') else {}),
                       **({'pending': src['pending']} if src.get('pending') else {})},
            'header_glow': {**glow_reach(name), 'origin': SHARED['header']['glow']['origin']},
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
        elif where == 'ALIAS':
            keep = ALIASES[key]
            ALIASES[key] = old
            fails = [r for r in checks()[0] if not r[-1]]
            ALIASES[key] = keep
        elif where == 'FACE':
            i = next(n for n, x in enumerate(FONTS) if x['css'] == key)
            keep = FONTS[i]
            FONTS[i] = old
            fails = [r for r in checks()[0] if not r[-1]]
            FONTS[i] = keep
        elif where == 'TYPE':
            keep = TYPE[key]
            TYPE[key] = old
            fails = [r for r in checks()[0] if not r[-1]]
            TYPE[key] = keep
        elif where == 'FONT':
            f = next(x for x in FONTS if x['face'] == key)
            keep = f['reserved_name']
            f['reserved_name'] = old
            fails = [r for r in checks()[0] if not r[-1]]
            f['reserved_name'] = keep
        elif where == 'CHARS':      # the range a too-short list would give, checked against the full list
            rng = unicode_range_without(old)
            saved = globals()['unicode_range_without']
            globals()['unicode_range_without'] = lambda chars, _r=rng: _r
            fails = [r for r in checks()[0] if not r[-1]]
            globals()['unicode_range_without'] = saved
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
    globals()['FONT_DIR'] = path.parent
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
