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
                 why='Inferred: Parker named no theme. Home already wore olive drab, Miasma is the stock olive theme, and olive is the one free hue in the set.', inferred=True,
                 pending='a holding value: the owner has since asked for Home to be Deep Quiet pulled toward the company brand, and is choosing among mixes; that pick replaces this entry.'),
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
    # type: each must fail R12 to R15
    ('TYPE', None, 'figure', ('3xl', 600, 'display', 0, False, True), 'the big number in the display face, as the version before set it'),
    ('TYPE', None, 'data', ('md', 400, 'ui', 0, False, True), 'figures asked to line up in DM Sans, which has no tabular figures'),
    ('TYPE', None, 'title-page', ((34, 40), 600, 'display', 0, False, False), 'a semibold Federo title: one weight, so the browser fakes it'),
    ('TYPE', None, 'meta', ('sm', 400, 'display', 0, False, False), 'meta (dates, times) in Federo'),
    ('FONT', None, 'Federo', None, 'Federo recorded with no reserved name: a subset would ship under a name its licence reserves'),
    ('CHARS', None, None, '0123456789', 'a unicode-range that only leaves out the digits: a price\'s $ and . would draw in Federo'),
]

# ── type (reference/type.md) ──────────────────────────────────────────────────
# The owner, on a sample of Federo: "can't use it for numbers or data... but the title and headers
# look really nice", and Federo for "the surrounding elements, the meta elements, the headers, the
# titles, the folders, maybe even buttons", with DM Sans "for all of the body content". Measuring the
# files then found that DM Sans 4.004 has no tabular figures, so digits that line up take DM Mono.
FACES = {
    'display': 'var(--font-federo, "Federo"), var(--font-dm-sans, "DM Sans"), system-ui, sans-serif',
    'ui': 'var(--font-dm-sans, "DM Sans"), system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
    'figures': 'var(--font-dm-mono, "DM Mono"), ui-monospace, "SF Mono", Menlo, Consolas, monospace',
    'mono': 'var(--font-dm-mono, "DM Mono"), ui-monospace, "SF Mono", Menlo, Consolas, monospace',
}
FRAME_ROLES = ('wordmark', 'eyebrow', 'tab', 'title-section', 'title-page', 'display')
# Federo's x-height is 0.46 em against DM Sans's 0.526: a Federo title is the step it replaces x 1.14.
TYPE = {
    'wordmark': ((19, 28), 400, 'display', 0.10, True, False),
    'eyebrow': ((13, 16), 400, 'display', 0.10, True, False),
    'tab': ((16, 20), 400, 'display', 0.08, True, False),
    'title-section': ((28, 32), 400, 'display', 0, False, False),
    'title-page': ((34, 40), 400, 'display', 0, False, False),
    'display': ((44, 52), 400, 'display', 0, False, False),
    'label': ('sm', 600, 'ui', 0, False, False), 'meta': ('sm', 400, 'ui', 0, False, False),
    'body': ('md', 400, 'ui', 0, False, False),
    'button': ('md', 600, 'ui', 0, False, False),        # the owner has not yet chosen Federo or DM Sans
    'title-card': ('lg', 600, 'ui', 0, False, False), 'lead': ('lg', 400, 'ui', 0, False, False),
    'title-record': ('2xl', 600, 'ui', 0, False, False),
    'figure': ('3xl', 600, 'ui', 0, False, False),
    'data': ('md', 400, 'figures', 0, False, True),
}
FONTS = [  # read from the files with scripts/font_facts.py and from each OFL.txt
    dict(face='Federo', css='display', role='the frame: wordmark, eyebrows, tabs, section and page titles',
         licence_file='OFL-Federo.txt', licence='SIL Open Font License 1.1',
         copyright='Copyright (c) 2011, Cyreal (www.cyreal.org)', reserved_name='Federo',
         weights=[400], italic=False, figures_line_up=False,
         figures='proportional: a 1 is 0.31 em, a 0 is 0.61 em; no tabular figures',
         measured='x-height 0.46 em, cap height 0.73 em; 220 glyphs; lacks the ellipsis and arrows',
         url='https://github.com/google/fonts/tree/main/ofl/federo'),
    dict(face='DM Sans', css='ui', role='everything a person reads or types, and one number standing alone',
         licence_file='OFL-DMSans.txt', licence='SIL Open Font License 1.1',
         copyright='Copyright 2014 The DM Sans Project Authors', reserved_name=None,
         weights=[400, 500, 600], italic=True, figures_line_up=False,
         figures='proportional only: version 4.004 has no tnum feature (a 1 is 0.34 em, a 0 is 0.66 em)',
         measured='x-height 0.526 em, cap height 0.70 em; variable, opsz 9-40 and wght 100-1000',
         url='https://github.com/googlefonts/dm-fonts'),
    dict(face='DM Mono', css='figures', role='figures that line up (amounts, times and counts in a column, totals, counters); code',
         licence_file='OFL-DMMono.txt', licence='SIL Open Font License 1.1',
         copyright='Copyright 2020 The DM Mono Project Authors', reserved_name=None,
         weights=[300, 400, 500], italic=True, figures_line_up=True,
         figures='every digit 0.60 em', measured='x-height 0.496 em, cap height 0.70 em (the same as DM Sans)',
         url='https://github.com/googlefonts/dm-mono'),
]
NATIVE_FACES = {  # @expo-google-fonts export names, read from each package
    ('display', 400): 'Federo_400Regular',
    ('ui', 400): 'DMSans_400Regular', ('ui', 500): 'DMSans_500Medium', ('ui', 600): 'DMSans_600SemiBold',
    ('figures', 400): 'DMMono_400Regular', ('figures', 500): 'DMMono_500Medium',
}
TYPE_NOTES = {
    'figures': 'DM Sans 4.004 has no tabular figures, so a column of amounts in DM Sans will not line up whatever font-variant-numeric says (at 16 px, 111.11 is 28 px wide and 888.88 is 53). Figures in a column, a total, a running count or a clock take DM Mono (type-data: every digit 0.60 em, the same cap height as DM Sans). A number inside a sentence, or one standing alone (type-figure), stays DM Sans.',
    'emphasis': 'Federo has one weight and no italic. A frame string takes no emphasis inside it; one frame string ranks above another by size and ink level. A word that needs emphasis inside a title is content, so it is DM Sans 600. font-synthesis: none on :root stops a browser faking bold or italic.',
    'optical_size': 'DM Sans is variable with an optical-size axis (9 to 40); browsers set it from the font size, so a 38 px figure draws the display cut and 14 px meta the text cut. Native bundles static cuts.',
    'buttons': 'Not yet chosen: Federo or DM Sans. Until then type-button is DM Sans 600. If Federo wins, a button that carries a figure still draws the figure in DM Sans: the unicode-range does it on the web, and native splits the label.',
    'licences': 'Each licence is read from its own OFL.txt (check R15). Federo reserves its name: ship the file as published, or a WOFF2 that only compresses it; a subset or other conversion is a modified version and may not be called Federo (OFL-FAQ 2.1, 2.6). DM Sans and DM Mono reserve no name, so they may be subset.',
    'web': 'localFont({ src: "./fonts/Federo-Regular.ttf", variable: "--font-federo", weight: "400", display: "swap", declarations: [{ prop: "unicode-range", value: behaviour.type.unicode_range }] }); DM_Sans({ subsets: ["latin"], axes: ["opsz"], variable: "--font-dm-sans" }); DM_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-dm-mono" })',
    'native': 'Bundle @expo-google-fonts/federo, /dm-sans and /dm-mono; native.type.<role>.fontFamily names the cut. Native has no unicode-range, so the frame text component throws in development on a digit.',
}
