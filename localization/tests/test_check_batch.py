import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_batch", ROOT / "scripts/check_batch.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.manifest = checker.load(ROOT / "examples/manifest.json")
        self.batch = checker.load(ROOT / "examples/translations.json")

    def test_complete_example_with_locale_specific_plural_shapes(self):
        self.assertEqual(checker.validate(self.manifest, self.batch),
                         {"entries": 3, "locales": 9, "values": 35})

    def test_omitted_extra_and_duplicate_rows_are_refused(self):
        for change in ("missing", "extra", "duplicate"):
            batch = copy.deepcopy(self.batch)
            if change == "missing":
                batch["entries"].pop()
            elif change == "extra":
                batch["entries"].append({"key": "invented", "translations": {}})
            else:
                batch["entries"].append(copy.deepcopy(batch["entries"][0]))
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "keys differ|duplicate"):
                checker.validate(self.manifest, batch)

    def test_missing_extra_and_duplicate_locales_are_refused(self):
        del self.batch["entries"][0]["translations"]["ja"]
        with self.assertRaisesRegex(ValueError, "required locales"):
            checker.validate(self.manifest, self.batch)
        self.setUp()
        self.batch["entries"][0]["translations"]["it"] = "Apri"
        with self.assertRaisesRegex(ValueError, "required locales"):
            checker.validate(self.manifest, self.batch)
        self.setUp()
        self.manifest["locales"].append("ja")
        with self.assertRaisesRegex(ValueError, "duplicate locale"):
            checker.validate(self.manifest, self.batch)

    def test_source_value_and_source_contract_cannot_change(self):
        self.batch["entries"][0]["translations"]["en"] = "Changed"
        with self.assertRaisesRegex(ValueError, "source-locale value changed"):
            checker.validate(self.manifest, self.batch)
        self.setUp()
        self.manifest["entries"][0]["source_by_locale"] = {"en": "Changed"}
        with self.assertRaisesRegex(ValueError, "source-locale contract differs"):
            checker.validate(self.manifest, self.batch)

    def test_lost_duplicated_and_renamed_placeholders_are_refused(self):
        for text in ("Ouvrir avec Ctrl+T", "{name} {name} Ctrl+T", "{title} Ctrl+T"):
            self.batch["entries"][0]["translations"]["fr"] = text
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "placeholders changed"):
                checker.validate(self.manifest, self.batch)

    def test_shortcut_and_range_endpoint_must_survive(self):
        entry = self.manifest["entries"][0]
        entry["source"] = "Press Alt+1 … 4 for {name}"
        entry["protected_tokens"] = ["Alt+1 … 4"]
        row = self.batch["entries"][0]["translations"]
        for locale in self.manifest["locales"]:
            row[locale] = f"{locale}: Alt+1 … 4 {{name}}"
        row["en"] = entry["source"]
        checker.validate(self.manifest, self.batch)
        for broken in ("Alt+1 で {name}", "Alt+1 … 44 で {name}", "Alt+1 … 4 / Alt+1 … 4 {name}"):
            row["ja"] = broken
            with self.subTest(broken=broken), self.assertRaisesRegex(ValueError, "protected token changed"):
                checker.validate(self.manifest, self.batch)

    def test_locale_contracts_cannot_invent_source_text_or_locales(self):
        entry = self.manifest["entries"][0]
        for contract in ({"it": entry["source"]}, {"fr": "Invented {name} Ctrl+T"}):
            entry["source_by_locale"] = contract
            with self.subTest(contract=contract), self.assertRaisesRegex(ValueError, "unknown locale|frozen source"):
                checker.validate(self.manifest, self.batch)

    def test_missing_or_extra_plural_form_is_refused(self):
        del self.batch["entries"][1]["translations"]["ru"]["few"]
        with self.assertRaisesRegex(ValueError, "form shape changed"):
            checker.validate(self.manifest, self.batch)
        self.setUp()
        self.batch["entries"][1]["translations"]["ja"]["one"] = "{n} ファイル"
        with self.assertRaisesRegex(ValueError, "form shape changed"):
            checker.validate(self.manifest, self.batch)

    def test_a_shortcut_prefix_is_not_a_preserved_shortcut(self):
        for chord in ("Ctrl+Tab", "Ctrl+T+X", "Ctrl+TT"):
            self.batch["entries"][0]["translations"]["fr"] = f"Ouvrir {{name}} avec {chord}"
            with self.subTest(chord=chord), self.assertRaisesRegex(ValueError, "protected token changed"):
                checker.validate(self.manifest, self.batch)

    def test_native_particles_can_touch_a_physical_shortcut(self):
        for text in ("Ctrl+T로 {name} 열기", "Ctrl+Tで{name}を開く"):
            self.batch["entries"][0]["translations"]["ko"] = text
            checker.validate(self.manifest, self.batch)

    def test_cognate_needs_a_target_locale_and_nonempty_reason(self):
        self.manifest["entries"][2].pop("same_as_source")
        with self.assertRaisesRegex(ValueError, "unchanged prose needs a reason"):
            checker.validate(self.manifest, self.batch)
        for reasons in ({"es": ""}, {"en": "source"}, {"it": "not required"}):
            self.manifest["entries"][2]["same_as_source"] = reasons
            with self.subTest(reasons=reasons), self.assertRaisesRegex(ValueError, "exceptions"):
                checker.validate(self.manifest, self.batch)

    def test_unsupported_icu_and_broken_braces_are_refused(self):
        for text in ("{n, plural, one{file} other{files}}", "{name", "{wrong-name}"):
            self.batch["entries"][0]["translations"]["de"] = text + " Ctrl+T"
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "unsupported brace syntax"):
                checker.validate(self.manifest, self.batch)

    def test_blank_text_and_non_string_leaves_are_refused(self):
        for value in (" ", None, False, [], {}, {"other": 2}):
            self.batch["entries"][0]["translations"]["de"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                checker.validate(self.manifest, self.batch)

    def test_explicit_token_inventory_and_its_spelling_are_checked(self):
        entry = self.manifest["entries"][0]
        for tokens in (None, [""], ["Ctrl+T", "Ctrl+T"], ["Ctrl+X"]):
            entry["protected_tokens"] = tokens
            with self.subTest(tokens=tokens), self.assertRaisesRegex(ValueError, "protected"):
                checker.validate(self.manifest, self.batch)

    def test_json_duplicate_keys_and_nonfinite_numbers_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            for raw in ('{"entries": [], "entries": []}', '{"n": NaN}', '{"x":{"en":1,"en":2}}'):
                path.write_text(raw)
                with self.subTest(raw=raw), self.assertRaises(ValueError):
                    checker.load(path)

    def test_plain_source_locale_is_configurable_and_literal_tokens_are_not_prose(self):
        manifest = {"source_locale": "de", "locales": ["de", "ja"], "entries": [
            {"key": "key", "source": "Ctrl+T {name}", "context": "Physical key label", "protected_tokens": ["Ctrl+T"]}]}
        batch = {"entries": [{"key": "key", "translations": {"de": "Ctrl+T {name}", "ja": "Ctrl+T {name}"}}]}
        self.assertEqual(checker.validate(manifest, batch)["locales"], 2)

    def test_cli_is_read_only_and_refusals_have_no_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest, batch = [Path(directory) / name for name in ("manifest.json", "batch.json")]
            manifest.write_text(json.dumps(self.manifest, ensure_ascii=False), encoding="utf-8")
            batch.write_text(json.dumps(self.batch, ensure_ascii=False), encoding="utf-8")
            before = (manifest.read_bytes(), batch.read_bytes())
            result = subprocess.run([sys.executable, str(ROOT / "scripts/check_batch.py"), str(manifest), str(batch)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("no catalogs written", result.stdout)
            self.assertEqual(before, (manifest.read_bytes(), batch.read_bytes()))
            batch.write_text('{"entries": null}')
            result = subprocess.run([sys.executable, str(ROOT / "scripts/check_batch.py"), str(manifest), str(batch)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
