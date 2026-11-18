"""The Head Waters family: the worked example for the design-language skill.

Six products from one small company: Stone (booking), Silo (client records and charting),
Scythe (payments), Surge (email), Home (the suite's front page) and Piper (dictation to
chart). Five take their colour from Omarchy themes by the rule in tokens.py; Piper's palette
is given whole, because its brand came first. Run from the skill's directory:

    python3 scripts/tokens.py --family examples/head-waters/family.py --check
    python3 scripts/tokens.py --family examples/head-waters/family.py --selftest

Quotes are the product owner's, from his notes of 2026-11-18. The marks drawn in this
example's pages are placeholders, not a source of truth.
"""
FAMILY = 'Head Waters'
PREFIX = '--hw-'

# A brand a client page may wear instead of the product's accent (checked by R10). The names
# are made up; the colours are a real practice's public brand colours.
BRANDS = {
    'example-practice': {'headerBg': '#405cd0', 'headerText': '#ffffff', 'accentBar': '#b5e1fe',
                         'web': {'accent': '#405cd0', 'accentSoft': '#eef1fd', 'accentDark': '#8ea2ff', 'accentSoftDark': '#1d2552'}},
    'example-shop': {'headerBg': '#2a1810', 'headerText': '#f3ebdd', 'accentBar': '#c99a3f', 'web': None},
}

SOURCES = {
    'stone': dict(theme='nord', label='Stone · Booking', intent='grey', slot='accent',
                  colours={'accent': '#81a1c1', 'background': '#2e3440', 'foreground': '#d8dee9'},
                  licence='MIT (Omarchy stock theme; the Nord palette is MIT, Arctic Ice Studio)',
                  url='https://github.com/omacom/omarchy/tree/HEAD/themes/nord',
                  why='Parker, 2026-11-18: "Stone follow NORD theme", "Stone will be gray".', inferred=False),
    'silo': dict(theme='jade-horse', label='Silo · Clients, charts, billing', intent='gentle', slot='accent',
                 colours={'accent': '#8bcbb1', 'background': '#142620', 'foreground': '#dfede5'},
                 licence='MIT (David Heinemeier Hansson)', url='https://github.com/dhh/omarchy-jade-horse-theme',
                 why='Parker: "similar to the Jade Horse, not so saturated in green ... a little bit more seriously".', inferred=False),
    'scythe': dict(theme='praus', label='Scythe · Payments', intent='ink', slot='background',
                   signature_slot={'light': 'yellow', 'dark': 'bright_yellow'},
                   colours={'accent': '#86917B', 'background': '#000000', 'foreground': '#D4D0BF', 'yellow': '#A18C60',
                            'bright_yellow': '#CDA369'},
                   licence='MIT (Parker Brown)', url='https://github.com/parker-brown-family/omarchy-praus-theme',
                   why='Parker: "a more black and white feel. With gold", "very, very similar" to Praus. Its bronze is the gold; it signs the folio bar and never fills, because gold sits on the warning hue.', inferred=False),
    'surge': dict(theme='retro-82', label='Surge · Email', intent='bright', slot=None, hue=236,
                  colours={'accent': '#faa968', 'background': '#05182e', 'foreground': '#f6dcac', 'green': '#028391'},
                  licence='MIT (Omarchy stock theme)', url='https://github.com/omacom/omarchy/tree/HEAD/themes/retro-82',
                  why='Parker: "Surge will follow the Retro 82 Omarchy theme", "brighter, more azure kind of blue". Retro 82\'s own accent is orange, on the warning hue; the azure is taken between its navy ground (253°) and its teal (208°). The exact point is feel, not measurement.', inferred=False),
    'home': dict(theme='miasma', label='Head Waters · the suite', intent='gentle', slot='accent',
                 colours={'accent': '#78824b', 'background': '#222222', 'foreground': '#c2c2b0'},
                 licence='MIT (Omarchy stock theme)', url='https://github.com/omacom/omarchy/tree/HEAD/themes/miasma',
                 why='Inferred: Parker named no theme. Home already wore olive drab, Miasma is the stock olive theme, and olive is the one free hue in the set.', inferred=True),
}
ORDER = ['piper', 'scythe', 'stone', 'silo', 'surge', 'home']   # fixed products first, then the rule in this order

# Piper keeps its own brand as its theme (assets/brand/tokens.css): parchment, deep green,
# gold, lavender for voice, burgundy trim ("burgundy (Not red!)", Parker 2026-11-17).
_PIPER_SOURCE = dict(theme='Piper brand (piper assets/brand)', label='Piper · Dictation to chart', intent='brand',
                    colours={'parchment': '#F9E5CE', 'deep-green': '#294B2B', 'gold': '#E6A93B', 'lavender': '#9B7AD6',
                             'pale-lavender': '#C8B5F0', 'red-trim': '#B94A3D'},
                    licence='the product\'s own brand; only its colour values appear here', url='',
                    why='Light: the 2026-11-17 restyle from the logo. Dark (new): the brand sheet\'s "logo on green field": deep green ground, parchment ink, lavender for what is active, burgundy for borders, gold for the wordmark.', inferred=True)
_PIPER_LIGHT = {'accent': '#5f4bae', 'accent-hover': '#4f3d99', 'accent-ink': '#4b3a8f', 'accent-tint': '#efe9fa', 'on-accent': '#ffffff',
               'ground': '#f7e7d1', 'surface': '#fffaf2', 'raised': '#fbf0e1', 'float': '#fffaf2', 'inset': '#f1e1ca', 'field': '#fffaf2',
               'surface-top': '#fffcf7', 'surface-bottom': '#fffaf2', 'raised-bottom': '#f8ead6',
               'ink': '#2b1a12', 'ink-2': '#5b4535', 'ink-3': '#6b5546', 'edge': '#dcc3b6', 'edge-control': '#977b6b',
               'edge-accent': '#7a3341',
               'danger': '#7a3341', 'danger-ink': '#7a3341', 'danger-tint': '#f3dde0', 'danger-edge': '#c79f97', 'on-danger': '#ffffff',
               'neutral': '#7d6656', 'neutral-tint': '#f0e6d8', 'neutral-edge': '#d8c4b3', 'word': '#5c571e'}
# Piper dark, as OKLCH recipes: green field at hue 145, parchment ink at 75, lavender at 299, burgundy at 10
G, P_, LV, BG_ = 145, 75, 299, 10
_PIPER_DARK_LCH = {
    'ground': (0.17, 0.030, G), 'surface': (0.21, 0.032, G), 'surface-top': (0.225, 0.033, G), 'surface-bottom': (0.21, 0.032, G),
    'raised': (0.245, 0.034, G), 'raised-bottom': (0.235, 0.034, G), 'float': (0.27, 0.036, G), 'inset': (0.14, 0.025, G),
    'field': (0.15, 0.026, G), 'ink': (0.94, 0.030, P_), 'ink-2': (0.83, 0.032, P_), 'ink-3': (0.74, 0.032, P_),
    'edge': (0.33, 0.032, G), 'edge-control': (0.56, 0.030, P_),
    'accent': (0.81, 0.084, LV), 'accent-hover': (0.86, 0.070, LV), 'accent-ink': (0.84, 0.076, LV),
    'accent-tint': (0.31, 0.060, LV), 'on-accent': (0.20, 0.050, LV),
    'edge-accent': (0.70, 0.105, BG_), 'danger': (0.70, 0.110, BG_), 'danger-ink': (0.75, 0.100, BG_),
    'danger-tint': (0.27, 0.055, BG_), 'danger-edge': (0.43, 0.080, BG_), 'on-danger': (0.18, 0.040, BG_),
    'neutral': (0.68, 0.030, P_), 'neutral-tint': (0.27, 0.030, G), 'neutral-edge': (0.37, 0.030, G),
    'word': (0.78, 0.140, 78),
}

FIXED = {'piper': {'source': _PIPER_SOURCE, 'light': _PIPER_LIGHT, 'dark_lch': _PIPER_DARK_LCH}}

# ── values that were wrong once; --selftest proves each still fails ─────────────
OLD_VALUES = [
    ('LIGHT', None, 'edge-control', '#8a9199', 'v1: outline 2.78:1 on light inset'),
    ('DARK', None, 'edge-control', '#6f7a87', 'v1: outline 2.96:1 on dark float'),
    ('FIXED:piper', None, 'edge-control', '#9c7f6f', 'v1: outline 2.88:1 on Piper inset'),
    ('SHEEN', None, None, 0.30, 'a heavy sheen: white text at the light end of a fill'),
    ('BRAND_SUBTITLE', None, None, (0.85, 0.06), 'v1 mockup band: 6% sheen, subtitle 85% white'),
    ('RAW', 'surge', ('light', 'accent'), '#faa968', 'Retro 82\'s own accent used raw: orange on the warning hue'),
    ('RAW', 'stone', ('light', 'accent'), '#81a1c1', 'Nord\'s accent used raw in light mode: white text fails'),
    ('RAW', 'silo', ('light', 'accent'), '#8bcbb1', 'Jade Horse\'s accent used raw in light mode'),
    ('RAW', 'scythe', ('light', 'signature'), '#CDA369', 'Praus\'s lamp gold used raw as the folio bar in light mode'),
    ('RAW', 'silo', ('dark', 'accent'), '#99c2b1', 'Silo dark at the rule\'s starting lightness 0.78, before step 6 moved it'),
    ('RAW', 'surge', ('dark', 'accent'), '#58c4ff', 'Surge dark at the starting lightness 0.78, before step 6 moved it'),
]
