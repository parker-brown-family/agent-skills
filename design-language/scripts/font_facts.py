#!/usr/bin/env python3
"""Read a font's facts from the file itself, before choosing it for a role.

    python3 font_facts.py FONT.ttf [FONT.woff2 ...]

Prints, per face: its weights (or variable axes), x-height and cap height in em, every digit's
width and whether the figures line up (all ten digits one width, or a tnum feature), the OpenType
features, glyphs a product interface often needs that the face lacks, and the licence and any
Reserved Font Name the file's own name table states. Read the licence again in the face's OFL.txt:
that file, not a web page, is the licence. Needs fontTools (pip install fonttools brotli).
Part of the design-language skill: github.com/parker-brown-family/agent-skills. MIT licence.
"""
import sys
from fontTools.ttLib import TTFont

NEEDED = '…→↗←✓×–—’“”€£·•'

def facts(path):
    f = TTFont(path)
    upm, os2, cmap, hm = f['head'].unitsPerEm, f['OS/2'], f.getBestCmap(), f['hmtx']
    name = lambda i: (f['name'].getDebugName(i) or '').strip()
    feats = sorted({r.FeatureTag for t in ('GSUB', 'GPOS') if t in f and f[t].table.FeatureList
                    for r in f[t].table.FeatureList.FeatureRecord})
    digits = {d: round(hm[cmap[ord(d)]][0] / upm, 3) for d in '0123456789' if ord(d) in cmap}
    line_up = len(set(digits.values())) == 1 or 'tnum' in feats
    print(f'== {name(4)}  ({path})')
    if 'fvar' in f:
        print('  axes      ', ', '.join(f'{a.axisTag} {a.minValue:g}-{a.maxValue:g}' for a in f['fvar'].axes))
    else:
        print('  weight    ', os2.usWeightClass, '(one static weight in this file)')
    print('  x-height  ', round(os2.sxHeight / upm, 3), 'em;  cap height', round(os2.sCapHeight / upm, 3), 'em')
    print('  digits    ', digits)
    print('  line up   ', 'yes' if line_up else 'NO: proportional figures and no tnum feature; tabular-nums will change nothing')
    print('  features  ', ' '.join(feats) or 'none')
    print('  lacks     ', ' '.join(c for c in NEEDED if ord(c) not in cmap) or f'nothing of {NEEDED}')
    print('  copyright ', name(0))
    lic = name(13)
    rfn = 'Reserved Font Name' in lic
    print('  licence   ', lic[:160].replace('\n', ' '), '|', name(14))
    print('  reserved  ', 'YES: a subset or converted copy may not use the name (OFL-FAQ 2.1, 2.6)' if rfn else 'none stated in the name table; check the OFL.txt header')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for p in sys.argv[1:]:
        facts(p)
