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
    'home': dict(theme='deep-quiet', label='Head Waters · the suite', intent='gentle', slot=None,
                 colours={'blue': '#8FBEB7', 'foreground': '#DDD7C1', 'dark_background': '#1D241F', 'brown': '#BE9A76'},
                 also={'the company brand teal': '#007480',
                       'old-tree browns (the settled mock)': {'bark': '#2C1F15', 'umber': '#3D2C1E', 'heartwood': '#4E3927',
                                                              'weathered': '#6A5340', 'lit corner': '#6E553C'}},
                 licence='MIT (Parker Brown and David Heinemeier Hansson)',
                 url='https://github.com/parker-brown-family/omarchy-deep-quiet-theme',
                 why='Settled by the owner by eye ("Settle on C ! <3"): Deep Quiet\'s sea-glass moved toward the company\'s brand teal, "with a little bit of brown", then "OLD TREE" browns in a corner glow. The dark ink is Deep Quiet\'s foreground and the tab bar close to its brown. Given whole in SETTLED; only what fails a check moves.',
                 inferred=False),
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
    ('FACE', None, 'ui', dict(face='DM Sans', css='ui', role='content', licence_file='OFL-Federo.txt', licence='SIL Open Font License 1.1',
                             copyright='Copyright (c) 2011, Cyreal (www.cyreal.org)', reserved_name='Federo', weights=[400, 500, 600],
                             italic=True, figures_line_up=False, figures='proportional only (no tnum)'),
     'DM Sans, the first candidate, as the content face: its figures cannot line up, so the data role fails'),
    ('FONT', None, 'IBM Plex Sans', None, 'Plex recorded from its name table, which states no reserved name; its OFL.txt reserves "Plex"'),
    ('RAW', 'home', ('light', 'accent'), '#0C6E75', 'Home light accent as settled: 3.04 from Stone for colour-blind readers'),
    ('RAW', 'home', ('dark', 'accent'), '#6BAAAE', 'Home dark accent as settled: 3.50 from Silo for colour-blind readers'),
    ('RAW', 'home', ('dark', 'gel'), '#2F9AA0', 'Home dark gel as settled: its label under 4.5 at the bottom of its line over clear glass'),
    ('TYPE', None, 'button', ('md', 600, 'ui', 0, False, False), 'buttons in IBM Plex Sans, as the example first had them: a frame role in the content face'),
    ('ALIAS', None, 'toggle-on', 'accent-tint', 'a pale tinted on-state for the toggle: on and off differ only by a faint colour'),
    ('TYPE', None, 'title-page', ((34, 40), 600, 'display', 0, False, False), 'a semibold Federo title: one weight, so the browser fakes it'),
    ('TYPE', None, 'meta', ('sm', 400, 'display', 0, False, False), 'meta (dates, times) in Federo'),
    ('FONT', None, 'Federo', None, 'Federo recorded with no reserved name: a subset would ship under a name its licence reserves'),
    ('CHARS', None, None, '0123456789', 'a unicode-range that only leaves out the digits: a price\'s $ and . would draw in Federo'),
]

# ── type (reference/type.md) ──────────────────────────────────────────────────
# The owner, on a sample of Federo: "can't use it for numbers or data... but the title and headers
# look really nice"; then, on IBM Plex Sans: "let's keep it simple ... Still fedora for all the STYLE
# stuff... and then IBM for all the CONTENT". Two faces. The first candidate for content, DM Sans
# 4.004, had no tabular figures; Plex's line up by default, so numbers need no third face.
FACES = {
    'display': 'var(--font-federo, "Federo"), var(--font-ibm-plex-sans, "IBM Plex Sans"), system-ui, sans-serif',
    'ui': 'var(--font-ibm-plex-sans, "IBM Plex Sans"), system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
    'mono': 'ui-monospace, "SF Mono", Menlo, Consolas, monospace',
}
# Buttons are frame too (the owner: "remember how I said buttons get fedora? still stands").
FRAME_ROLES = ('wordmark', 'eyebrow', 'tab', 'title-section', 'title-page', 'display', 'button', 'button-small', 'gel')
# Federo's x-height is 0.46 em against Plex's 0.516: a Federo title is the step it replaces x 1.12.
# The wordmark and tabs are the values of the header the owner settled.
TYPE = {
    'wordmark': ((19, 28), 400, 'display', 0.11, True, False),
    'eyebrow': ((13, 16), 400, 'display', 0.10, True, False),
    'tab': ((16.5, 20), 400, 'display', 0, False, False),
    'title-section': ((27, 32), 400, 'display', 0, False, False),
    'title-page': ((34, 40), 400, 'display', 0, False, False),
    'display': ((43, 52), 400, 'display', 0, False, False),
    'label': ('sm', 600, 'ui', 0, False, False), 'meta': ('sm', 400, 'ui', 0, False, False),
    'body': ('md', 400, 'ui', 0, False, False),
    'button': ((18, 24), 400, 'display', 0, False, False),        # Plex 16 semibold -> Federo 18
    'button-small': ((16, 20), 400, 'display', 0, False, False),
    'gel': ((16, 20), 400, 'display', 0, False, False),
    'title-card': ('lg', 600, 'ui', 0, False, False), 'lead': ('lg', 400, 'ui', 0, False, False),
    'title-record': ('2xl', 600, 'ui', 0, False, False),
    'figure': ('3xl', 600, 'ui', 0, False, False),
    'data': ('md', 400, 'ui', 0, False, True),
}
FONTS = [  # read from the files with scripts/font_facts.py and from each OFL.txt
    dict(face='Federo', css='display', role='the frame: wordmark, eyebrows, tabs, section and page titles',
         licence_file='OFL-Federo.txt', licence='SIL Open Font License 1.1',
         copyright='Copyright (c) 2011, Cyreal (www.cyreal.org)', reserved_name='Federo',
         weights=[400], italic=False, figures_line_up=False,
         figures='proportional: a 1 is 0.31 em, a 0 is 0.61 em; no tabular figures',
         measured='x-height 0.46 em, cap height 0.73 em; 220 glyphs; lacks the ellipsis and arrows',
         url='https://github.com/google/fonts/tree/main/ofl/federo'),
    dict(face='IBM Plex Sans', css='ui', role='everything a person reads or types, numbers, data and every button included',
         licence_file='OFL-IBMPlexSans.txt', licence='SIL Open Font License 1.1',
         copyright='Copyright © 2017 IBM Corp.', reserved_name='Plex',
         weights=[400, 500, 600], italic=True, figures_line_up=True,
         figures='tabular by default: every digit 0.60 em',
         measured='x-height 0.516 em, cap height 0.698 em; variable, wght 100-700 and wdth 75-100; the name table states no reserved name, the OFL.txt reserves "Plex"',
         url='https://github.com/google/fonts/tree/main/ofl/ibmplexsans'),
]
NATIVE_FACES = {  # @expo-google-fonts export names, read from each package
    ('display', 400): 'Federo_400Regular',
    ('ui', 400): 'IBMPlexSans_400Regular', ('ui', 500): 'IBMPlexSans_500Medium', ('ui', 600): 'IBMPlexSans_600SemiBold',
}
TYPE_NOTES = {
    'figures': 'IBM Plex Sans\'s figures line up by default (every digit 0.60 em), so amounts, totals and clocks are Plex as it stands (type-data). Never switch on old-style figures (onum) for data. The first candidate, DM Sans 4.004, had no tabular figures: at 16 px, 111.11 measured 28 px and 888.88 53 px with tabular-nums set.',
    'emphasis': 'Federo has one weight and no italic. A frame string takes no emphasis inside it; one ranks above another by size and ink level. A word that needs emphasis inside a title is content, so it is Plex 600. font-synthesis: none on :root stops a browser faking bold or italic.',
    'buttons': 'Federo, every button, the header\'s gel included; one weight, so a button ranks by its fill and size.',
    'button_figures': 'A figure inside a button label is IBM Plex Sans at the same size: <button class="hw-btn primary">Pay <span class="hw-fig">$95.00</span></button>. A control whose label is only a number (a stepper, a page number, a count) is data, its plus and minus included. Keep the amount on a pay button.',
    'licences': 'Each licence is read from its own OFL.txt (check R15). Both faces reserve their names, "Federo" and "Plex" (Plex\'s only in its OFL.txt). Ship each file as published, or a WOFF2 that only compresses it; a subset or other conversion is a modified version and may not use the name (OFL-FAQ 2.1, 2.6), so neither goes through next/font/google.',
    'web': 'localFont({ src: "./fonts/Federo-Regular.woff2", variable: "--font-federo", weight: "400", display: "swap", declarations: [{ prop: "unicode-range", value: behaviour.type.unicode_range }] }); localFont({ src: "./fonts/IBMPlexSans-var.woff2", variable: "--font-ibm-plex-sans", weight: "100 700", display: "swap" })',
    'native': 'Bundle @expo-google-fonts/federo and /ibm-plex-sans; native.type.<role>.fontFamily names the cut. Native has no unicode-range, so the frame text component throws in development on a digit.',
}

# ── the settled product and the header (reference/glass-header.md) ────────────
# Home was settled by eye on a mock; these are the mock's values. The roles the mock did not show
# are derived: (lightness, chroma) at the ground's hue, or 'ink' for the ink's hue and chroma.
SETTLED = {'home': {
    'light': {'ground': '#EDE6D5', 'surface': '#F7F1E2', 'ink': '#1B2420', 'accent': '#0C6E75', 'on-accent': '#ffffff',
              'signature': '#7A5B3C', 'header-ink': '#241A10', 'header-tint': '#3D2C1E',
              'glow-core': '#2C1F15', 'glow-mid': '#4E3927b0', 'gel': '#2F9AA0', 'on-gel': '#061416', 'frost-ink': '#2a2118'},
    'dark': {'ground': '#1E221D', 'surface': '#272C25', 'ink': '#DDD7C1', 'accent': '#6BAAAE', 'on-accent': '#10161a',
             'signature': '#B99A70', 'header-ink': '#EAE2CC', 'header-tint': '#2C1F15',
             'glow-core': '#6E553C', 'glow-mid': '#3D2C1Ea0', 'gel': '#2F9AA0', 'on-gel': '#061416', 'frost-ink': '#EAE2CC'},
    'derived': {
        'light': {'surface-top': (0.972, None), 'surface-bottom': (0.959, None), 'raised': (0.968, None), 'raised-bottom': (0.952, None),
                  'float': (0.978, 0.014), 'inset': (0.893, None), 'field': (0.982, 0.012),
                  'ink-2': (0.42, 'ink'), 'ink-3': (0.48, 'ink'), 'edge': (0.85, 0.022), 'edge-control': (0.56, 0.02),
                  'neutral': (0.53, 0.02), 'neutral-tint': (0.905, 0.02), 'neutral-edge': (0.80, 0.02)},
        'dark': {'surface-top': (0.30, None), 'surface-bottom': (0.286, None), 'raised': (0.315, None), 'raised-bottom': (0.30, None),
                 'float': (0.345, 0.016), 'inset': (0.215, None), 'field': (0.225, None),
                 'ink-2': (0.79, 'ink'), 'ink-3': (0.72, 'ink'), 'edge': (0.37, 0.016), 'edge-control': (0.62, 0.02),
                 'neutral': (0.64, 0.02), 'neutral-tint': (0.33, 0.016), 'neutral-edge': (0.43, 0.016)}},
}}
# Each other product's corner tone: the theme colour its hue and chroma come from. The owner settled
# the header on the front page, then made it every product's skin, each in its own theme's deep tone.
GLOW_FROM = {'stone': ('Nord slate', '#4c566a'), 'silo': ('Jade Horse jade', '#8bcbb1'),
             'scythe': ('Praus gold', '#A18C60'), 'surge': ('Retro 82 navy', '#05182e'), 'piper': ('Piper burgundy', '#7a3341')}
