import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import urllib.error


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("crosscheck", ROOT / "scripts/crosscheck.py")
crosscheck = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(crosscheck)


class Args:
    source_lang = "en"
    pause = 0
    plain = None
    out = None


def write(folder, name, data):
    path = Path(folder) / name
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(path)


class CrosscheckTests(unittest.TestCase):
    def setUp(self):
        crosscheck.REFUSED.clear()

    def test_plural_objects_spread_and_private_keys_are_left_out(self):
        flat = crosscheck.flatten({"a": "one", "n": {"one": "%1 file", "other": "%1 files"}, "_about": "note"})
        self.assertEqual(flat, {"a": "one", "n#one": "%1 file", "n#other": "%1 files"})

    def run_google(self, source, target, plain=None, answer=None):
        with tempfile.TemporaryDirectory() as folder:
            args = Args()
            args.source = write(folder, "en.json", source)
            args.target = write(folder, "ja.json", target)
            args.lang = "ja"
            args.plain = write(folder, "plain.json", plain) if plain else None
            args.out = str(Path(folder) / "out.json")
            with mock.patch.object(crosscheck, "ask", side_effect=answer), mock.patch("sys.stdout", io.StringIO()):
                code = crosscheck.google(args)
            return code, json.loads(Path(args.out).read_text(encoding="utf-8"))

    def test_sensitive_rows_are_translated_forward_from_the_plain_idea(self):
        asked = []
        def answer(texts, source, target, pause):
            asked.append((source, target, list(texts)))
            return [f"<{t}>" for t in texts]
        code, result = self.run_google({"warn": "It could be committed.", "ok": "Saved"}, {"warn": "W", "ok": "S"},
                                       plain={"warn": "Git could commit the key."}, answer=answer)
        self.assertEqual(code, 0)
        rows = {r["key"]: r for r in result["rows"]}
        self.assertTrue(rows["warn"]["sensitive"])
        self.assertEqual(rows["warn"]["forward_from"], "plain")
        self.assertEqual(rows["warn"]["google_forward"], "<Git could commit the key.>")
        self.assertEqual(rows["ok"]["forward_from"], "source")
        self.assertEqual(asked[0][:2], ("ja", "en"))      # back-translation first: ours into the source language

    def test_an_unanswered_string_is_null_and_counted_never_empty(self):
        code, result = self.run_google({"a": "Saved"}, {"a": "S"}, answer=lambda texts, *rest: [None] * len(texts))
        self.assertEqual(code, 1)
        self.assertIsNone(result["rows"][0]["google_back_of_ours"])
        self.assertEqual(result["summary"]["back_unavailable"], 1)

    def test_a_language_with_one_plural_form_is_not_reported_as_missing_strings(self):
        code, result = self.run_google({"n": {"one": "%1 file", "other": "%1 files"}}, {"n": {"other": "%1 F"}},
                                       answer=lambda texts, *rest: list(texts))
        self.assertEqual(result["summary"]["missing_from_target"], [])
        self.assertEqual(result["rows"][0]["source"], "%1 files")

    def test_a_refusing_address_is_not_asked_again(self):
        calls = []
        def fetch(url, params):
            calls.append(url)
            if "clients5" in url:
                raise urllib.error.HTTPError(url, 429, "Too Many Requests", None, None)
            return [[["eins\nzwei", None]]]
        with mock.patch.object(crosscheck, "fetch", side_effect=fetch), mock.patch.object(crosscheck.time, "sleep"):
            self.assertEqual(crosscheck.ask(["one", "two"], "en", "de", 0), ["eins", "zwei"])
            self.assertEqual(crosscheck.ask(["one", "two"], "en", "de", 0), ["eins", "zwei"])
        self.assertEqual(sum("clients5" in url for url in calls), 1)

    def test_percent_holes_are_put_back_together(self):
        self.assertEqual(crosscheck.tidy("Add % 1 to the file"), "Add %1 to the file")
        self.assertEqual(crosscheck.tidy("Add %1 to the file"), "Add %1 to the file")
        self.assertIsNone(crosscheck.tidy(None))


if __name__ == "__main__":
    unittest.main()
