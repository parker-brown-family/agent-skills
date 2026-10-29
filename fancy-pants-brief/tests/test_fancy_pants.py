"""The gate, against the shapes of page that came out white or flat, and the innocent ones.

Run: python3 -m unittest discover fancy-pants-brief/tests
"""
import importlib.machinery, importlib.util, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / 'scripts' / 'fancy-pants'
loader = importlib.machinery.SourceFileLoader('fancy_pants', str(TOOL))
spec = importlib.util.spec_from_loader('fancy_pants', loader)
fp = importlib.util.module_from_spec(spec)
loader.exec_module(fp)

BASE = f'<style>/* {fp.BASE_MARK} */ body{{background:transparent}} .glass{{background:#fff}}</style>'
WALL = '<style id="brief-wall">:root{--bg:#111;--wall:url("data:image/webp;base64,AAAA")}</style>'


def page(own='', body='<h1>x</h1>', look=True, head_extra=''):
    return (f'<!doctype html><html><head>{head_extra}{BASE + WALL if look else ""}'
            f'<style>{own}</style></head><body>{body}</body></html>')


def fails(doc):
    return fp.static_check(doc)[0]


class Gate(unittest.TestCase):
    def test_a_page_on_the_look_passes(self):
        self.assertEqual(fails(page('.card{padding:4px} h2{color:var(--acc)}')), [])

    def test_the_white_resume_shape_fails(self):
        f = fails(page('html,body{background:#fff;color:#111}', look=False))
        self.assertTrue(any('base.css' in x for x in f))
        self.assertTrue(any('wallpaper' in x for x in f))
        self.assertTrue(any('opaque ground' in x for x in f))

    def test_the_flat_review_page_shape_fails(self):
        # Cinema Delight's retell review, 2026-10-29: dark, but its own ground and its own --bg
        f = fails(page(':root{--bg:#0d1117;--ink:#e8ecf2;--mut:#9aa4b4} body{margin:0;background:var(--bg)}'))
        self.assertTrue(any('opaque ground' in x and 'body' in x for x in f))
        self.assertTrue(any('--bg' in x and '--mut' in x for x in f))
        self.assertFalse(any('--ink' in x for x in f))   # a name the theme does not own is the page's

    def test_a_wall_block_without_an_image_fails(self):
        doc = page().replace('url("data:image/webp;base64,AAAA")', 'none')
        self.assertTrue(any('carries no image' in x for x in fails(doc)))

    def test_network_dependencies_fail(self):
        for extra in ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter">',
                      '<link href="//cdn.example.com/x.css" rel="stylesheet">',
                      '<script src="https://cdn.jsdelivr.net/npm/mermaid"></script>'):
            self.assertTrue(any('network' in x for x in fails(page(head_extra=extra))), extra)
        self.assertTrue(any('network' in x for x in fails(page('@import url("https://x.example/a.css");'))))

    def test_a_light_colour_scheme_fails(self):
        self.assertTrue(any('light colour scheme' in x for x in fails(page(':root{color-scheme:light dark}'))))
        meta = '<meta name="color-scheme" content="light">'
        self.assertTrue(any('light colour scheme' in x for x in fails(page(head_extra=meta))))

    # ---- innocent pages, so the gate is never switched off for crying wolf

    def test_a_print_rule_that_whitens_paper_passes(self):
        # the Okanagan interview report, 2026-10-27
        own = '.x{padding:1px}\n@media print{body{background:white!important;color:#111!important}}'
        self.assertEqual(fails(page(own)), [])

    def test_a_see_through_ground_passes(self):
        self.assertEqual(fails(page('body{background:transparent} main{background:none}')), [])

    def test_html_background_is_the_canvas_and_passes(self):
        self.assertEqual(fails(page('html{background:#000}')), [])

    def test_a_milky_card_only_warns(self):
        f, w = fp.static_check(page('.verdict{background:#ffffff}'))
        self.assertEqual(f, [])
        self.assertTrue(any('.verdict' in x for x in w))

    def test_a_local_video_passes(self):
        self.assertEqual(fails(page(body='<video controls src="film.mp4"></video>')), [])

    def test_a_page_colour_named_differently_passes(self):
        self.assertEqual(fails(page(':root{--page-ink:#eee;--film-bg:#000}')), [])


@unittest.skipUnless(shutil.which('vips'), 'needs vips for brief-wall')
class Builders(unittest.TestCase):
    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True)

    def test_new_page_passes_the_static_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'p.html'
            r = self.run_tool('new', str(p), '--title', 'A <test> page')
            self.assertEqual(r.returncode, 0, r.stderr)
            doc = p.read_text()
            self.assertIn('A &lt;test&gt; page', doc)
            self.assertIn(fp.SECTIONS_MARK, doc)
            self.assertEqual(fails(doc), [])

    def test_dress_adds_the_look_and_names_what_still_fights_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'p.html'
            p.write_text('<html><head><style>body{background:#fff}</style></head><body><h1>x</h1></body></html>')
            r = self.run_tool('dress', str(p), '--no-render')
            self.assertEqual(r.returncode, 1)
            self.assertIn('opaque ground', r.stdout)
            doc = p.read_text()
            self.assertIn(fp.BASE_MARK, doc)
            self.assertIn('id="brief-wall"', doc)
            self.assertLess(doc.index(fp.BASE_MARK), doc.index('body{background:#fff}'))   # the page's CSS still follows

    def test_dress_twice_adds_nothing_the_second_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'p.html'
            p.write_text('<html><head></head><body><h1>x</h1></body></html>')
            self.run_tool('dress', str(p), '--no-render')
            once = p.read_text()
            self.run_tool('dress', str(p), '--no-render')
            self.assertEqual(p.read_text(), once)


if __name__ == '__main__':
    unittest.main()
