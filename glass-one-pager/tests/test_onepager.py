"""Run: python3 tests/test_onepager.py"""
import copy
import importlib.util
import json
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "onepager.py"
spec = importlib.util.spec_from_file_location("onepager", SCRIPT)
op = importlib.util.module_from_spec(spec)
spec.loader.exec_module(op)

STATES = {"done": {"mark": "✓", "means": "merged", "colour": "good", "pull_request": "MERGED"},
          "open": {"mark": "○", "means": "open", "colour": "waiting", "pull_request": "OPEN"}}
GOOD = {"name": "Ada Example", "title": "what I build", "states": STATES, "note": {"title": "GO", "lines": ["see"]}, "prompt": "which first?",
        "projects": [{"name": "Thing", "by": "someone", "url": "https://example.com", "why": "A thing.", "love": "It works.",
                      "items": [{"state": "done", "text": "fixed a bug", "url": "https://github.com/o/r/pull/1"}]}]}


class Base(unittest.TestCase):
    def setUp(self):
        self.d = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.d)

    def write(self, c):
        f = self.d / "content.json"
        f.write_text(json.dumps(c), encoding="utf-8")
        return f

    def load(self, **change):
        c = copy.deepcopy(GOOD)
        c.update(change)
        return op.load_content(self.write(c))

    def refused(self, words, fn, *a, **k):
        with self.assertRaises(op.Problem) as e:
            fn(*a, **k)
        self.assertIn(words, str(e.exception))


class Content(Base):
    def test_good_content_loads(self):
        self.assertEqual(self.load()["name"], "Ada Example")

    def test_the_template_is_refused_until_filled(self):
        self.refused("placeholder", op.load_content, ROOT / "templates" / "content.json")

    def test_a_greater_than_sign_is_not_a_placeholder(self):
        self.load(title="Install > AI, and 3 < 4")

    def test_missing_fields(self):
        self.refused("missing: projects", self.load, projects=[])

    def test_unknown_state(self):
        p = copy.deepcopy(GOOD["projects"]); p[0]["items"][0]["state"] = "maybe"
        self.refused("not one of", self.load, projects=p)

    def test_private_and_unsafe_links(self):
        for u in ("file:///etc/passwd", "javascript:alert(1)", "http://localhost:3000", "http://192.168.1.4/x", "https://nas.local/x", "https://a.b/\"onclick=x"):
            p = copy.deepcopy(GOOD["projects"]); p[0]["url"] = u
            self.refused("not a public", self.load, projects=p)

    def test_public_hosts_that_only_look_private(self):
        for u in ("https://localhost.example.com", "https://test.example.com/a", "https://local.dev"):
            p = copy.deepcopy(GOOD["projects"]); p[0]["url"] = u
            self.load(projects=p)

    def test_contact_details_need_saying(self):
        for t in ("ada@example.com", "(555) 010-9999", "/home/ada/secret"):
            self.refused("holds", self.load, title=t)
        self.refused("publishes an address", self.load, links=[{"label": "write", "url": "mailto:ada@example.com"}])
        self.load(title="ada@example.com", contact_is_public=True)

    def test_dates_and_versions_are_not_phone_numbers(self):
        for t in ("since 2026-11-24", "version 1.2.345", "14 pull requests"):
            self.load(title=t)

    def test_colour_must_be_hex(self):
        p = copy.deepcopy(GOOD["projects"]); p[0]["colour"] = 'red" onload="x'
        self.refused("hex", self.load, projects=p)


class Drawing(Base):
    def page(self, theme="deep-quiet", **change):
        return op.draw(self.load(**change), op.load_theme(theme))

    def test_every_theme_draws_the_example(self):
        c = op.load_content(ROOT / "examples" / "open-source" / "content.json")
        for f in (ROOT / "themes").glob("*.json"):
            page, info = op.draw(c, op.load_theme(f.stem))
            self.assertGreaterEqual(info["type"], 16, f.stem)
            for p in c["projects"]:
                for it in p["items"]:
                    self.assertIn(op.E(it["url"]), page)

    def test_words_are_escaped(self):
        page, _ = self.page(title="A & B > C")
        self.assertIn("A &amp; B &gt; C", page)

    def test_type_shrinks_as_words_grow(self):
        _, few = self.page()
        many = [dict(GOOD["projects"][0], name=f"P{i}", why="word " * 30, items=[]) for i in range(6)]
        _, lots = self.page(projects=many, note=None)
        self.assertLess(lots["type"], few["type"])

    def test_too_many_words(self):
        many = [dict(GOOD["projects"][0], name=f"P{i}", why="word " * 120, items=[]) for i in range(9)]
        self.refused("more words than fit", self.page, projects=many)

    def test_too_many_rows(self):
        p = [dict(GOOD["projects"][0], items=GOOD["projects"][0]["items"] * 90)]
        self.refused("sidebar holds", self.page, projects=p)

    def test_a_long_row(self):
        p = copy.deepcopy(GOOD["projects"]); p[0]["items"][0]["text"] = "far too many words to ever fit on a single sidebar row here"
        self.refused("too long", self.page, projects=p)

    def test_the_note_covers_no_words(self):
        edges = [(y, 1840) for y in range(200, 1100, 30)]
        self.refused("no room", op.place_note, GOOD["note"], edges, 500, 160, 1366, 946)
        nx, ny, w, h = op.place_note(GOOD["note"], edges[:8], 500, 160, 1366, 946)
        self.assertFalse([e for e in edges[:8] if ny < e[0] < ny + h])

    def test_states_must_use_a_theme_colour(self):
        s = copy.deepcopy(STATES); s["done"]["colour"] = "nope"
        self.refused("does not have", self.page, states=s)

    def test_unknown_theme(self):
        self.refused("no theme", op.load_theme, "nope")


class Commands(Base):
    def run_(self, *a, **env):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, a)], capture_output=True, text=True, env={**os.environ, **env})

    def fake_gh(self, body):
        f = self.d / "gh"
        f.write_text("#!/bin/sh\n" + body)
        f.chmod(f.stat().st_mode | stat.S_IEXEC)
        return f"{self.d}:{os.environ['PATH']}"

    def test_check_passes_a_true_mark(self):
        self.assertEqual(self.run_("check", self.write(GOOD), PATH=self.fake_gh("echo MERGED")).returncode, 0)

    def test_check_fails_a_stale_mark(self):
        r = self.run_("check", self.write(GOOD), PATH=self.fake_gh("echo OPEN"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("STALE", r.stdout)

    def test_check_never_passes_what_it_could_not_read(self):
        r = self.run_("check", self.write(GOOD), PATH=self.fake_gh("exit 1"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("UNREAD", r.stdout)

    def test_new_never_overwrites(self):
        self.assertEqual(self.run_("new", self.d / "p").returncode, 0)
        self.assertEqual(self.run_("new", self.d / "p").returncode, 1)

    @unittest.skipUnless(any(map(shutil.which, ("google-chrome-stable", "google-chrome", "chromium"))) and shutil.which("pdfinfo"), "needs Chrome and pdfinfo")
    def test_build_is_one_page_with_live_links(self):
        r = self.run_("build", self.write(GOOD))
        self.assertEqual(r.returncode, 0, r.stderr)
        out = subprocess.run(["pdfinfo", "-url", str(self.d / "content.pdf")], capture_output=True, text=True).stdout
        self.assertIn("https://github.com/o/r/pull/1", out)
        self.assertNotIn(str(pathlib.Path.home()), (self.d / "content.pdf").read_bytes().decode("latin-1"))


class Shipped(unittest.TestCase):
    def test_nothing_shipped_holds_a_machine_path(self):
        for f in ROOT.rglob("*"):
            if f.is_file() and f.suffix in (".py", ".md", ".json", ".txt") and f.name != "test_onepager.py":
                for what in ("/home/", "/Users/"):
                    if f.name == "onepager.py":
                        continue
                    self.assertNotIn(what, f.read_text(encoding="utf-8"), f)


if __name__ == "__main__":
    unittest.main()
