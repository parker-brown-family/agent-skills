import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('brief', Path(__file__).resolve().parents[1] / 'scripts/brief.py')
brief = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(brief)
SOURCE = '''<!doctype html><html><head><title>Fixture</title><!--BRIEF:head--></head><body>
<!--brief-content--><header><h1>A reader's comment</h1><nav class="sections"></nav></header>
<main><h2 id="sec-result" data-brief-anchor="sec-result">Result</h2>
<p>A comment stays attached to its passage.</p></main><!--/brief-content-->
<!--BRIEF:notes--></body></html>'''
MD = '''<!-- briefing: {"id":"example-md","medium":"markdown","purpose":"engineering"} -->
# Example
<a id="sec-result"></a>
## Result
A comment stays attached to its passage.
'''


class BriefTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.src, self.out = self.root / 'source.html', self.root / 'brief.html'
        self.src.write_text(SOURCE)
        self.markdown = self.root / 'brief.md'
        self.markdown.write_text(MD)
        self.fake_wall = patch.object(brief.subprocess, 'run')
        process = self.fake_wall.start()
        process.return_value.stdout = '<style id="brief-wall">/* test wall */</style>'
        self.addCleanup(self.fake_wall.stop)

    def build(self):
        return brief.build(self.src, self.out, 'example-html', 'engineering')

    def annotate(self):
        self.build()
        original = brief.read(self.out)
        empty, _ = brief.island(original, 'report-notes')
        payload = {'sec-result': [{'text': 'Keep </script> and <!-- this exact text.', 'title': 'Result', 'ts': '2026-10-30 12:00'}]}
        note_block = '<script type="application/json" id="report-notes" data-format="1" data-rev="reader-revision">' + brief.encode(payload) + '</script>'
        original = original.replace(empty, note_block)
        empty, _ = brief.island(original, 'report-concurs')
        original = original.replace(empty, '<script id="report-concurs" data-format="1" data-rev="reader-revision">{"sec-result":"2026-10-30 12:00"}</script>')
        mirror = '<!--\nREADER NOTES —\n[sec-result] Result\n  · Keep this.\n-->'
        original = original.replace('</body>', mirror + '</body>')
        self.out.write_text(original)
        return original

    def map_for(self, path):
        data = brief.feedback(path)
        data['comments'] = [{'target': 'sec-result', 'title': 'Result', 'text': 'Explain the boundary.', 'stance': None, 'at': None}]
        map_path = self.root / 'brief.feedback.json'
        map_path.write_text(json.dumps(data))
        return map_path

    def test_rebuild_preserves_islands_mirror_wall_and_backup(self):
        original = self.annotate()
        self.build()
        revised = brief.read(self.out)
        for name in ('report-notes', 'report-concurs'):
            self.assertEqual(brief.island(original, name)[0], brief.island(revised, name)[0])
        self.assertEqual(brief.MIRROR.search(original)[0], brief.MIRROR.search(revised)[0])
        self.assertEqual(list(self.root.glob('brief.html.*.bak'))[0].read_bytes(), original.encode())
        self.assertEqual(brief.feedback(self.out)['comments'][0]['text'], 'Keep </script> and <!-- this exact text.')
        self.assertEqual(brief.island(revised, 'brief-meta')[1]['feedback_revision'], brief.inspect(self.out)[2])

    def test_changed_content_retains_notes_with_unknown_revision(self):
        self.annotate()
        self.src.write_text(SOURCE.replace('>Result<', '>Outcome<'))
        self.build()
        exported = brief.feedback(self.out)
        self.assertIsNone(exported['document']['revision'])
        self.assertEqual(exported['comments'][0]['target'], 'sec-result')
        map_path = self.root / 'feedback.json'
        map_path.write_text(json.dumps(exported))
        resolved = brief.resolve(self.out, map_path)
        self.assertIn('revision_unknown', resolved['comments'][0]['reasons'])

    def test_malformed_island_refuses_without_replacement(self):
        self.build()
        bad = brief.read(self.out).replace('data-format="1">{}', 'data-format="1">{bad', 1)
        self.out.write_text(bad)
        with self.assertRaises(brief.Refusal):
            self.build()
        self.assertEqual(brief.read(self.out), bad)
        self.assertEqual(list(self.root.glob('*.bak')), [])

    def test_unknown_annotation_format_refuses(self):
        self.build()
        self.out.write_text(brief.read(self.out).replace('data-format="1"', 'data-format="99"', 1))
        with self.assertRaises(brief.Refusal):
            self.build()

    def test_duplicate_anchor_and_unknown_slot_refuse(self):
        for changed in (SOURCE.replace('</main>', '<div id="sec-result"></div></main>'), SOURCE.replace('<!--BRIEF:head-->', '<!--BRIEF:nope-->')):
            self.src.write_text(changed)
            with self.assertRaises(brief.Refusal):
                self.build()
        self.assertFalse(self.out.exists())

    def test_concurrent_edit_is_retained(self):
        self.out.write_text('reader changed this')
        with self.assertRaises(brief.Refusal):
            brief.atomic(self.out, 'stale replacement', b'previous bytes')
        self.assertEqual(self.out.read_text(), 'reader changed this')

    def test_matching_markdown_comment_resolves(self):
        data = brief.resolve(self.markdown, self.map_for(self.markdown))
        self.assertEqual(data['comments'][0]['status'], 'resolved')
        self.assertEqual(data['comments'][0]['text'], 'Explain the boundary.')

    def test_changed_revision_and_removed_target_both_survive(self):
        map_path = self.map_for(self.markdown)
        self.markdown.write_text(MD.replace('sec-result', 'sec-new'))
        data = brief.resolve(self.markdown, map_path)
        self.assertEqual(data['comments'][0]['reasons'], ['revision_changed', 'target_missing'])
        self.assertEqual(data['comments'][0]['text'], 'Explain the boundary.')

    def test_unknown_revision_and_wrong_identity_are_not_accepted(self):
        map_path = self.map_for(self.markdown)
        data = json.loads(map_path.read_text())
        data['document']['revision'] = None
        data['document']['id'] = 'other-document'
        map_path.write_text(json.dumps(data))
        self.assertEqual(brief.resolve(self.markdown, map_path)['comments'][0]['reasons'], ['document_mismatch', 'revision_unknown'])

    def test_empty_comment_does_not_imply_agreement(self):
        map_path = self.map_for(self.markdown)
        data = json.loads(map_path.read_text())
        data['comments'][0]['text'] = ''
        map_path.write_text(json.dumps(data))
        with self.assertRaises(brief.Refusal):
            brief.resolve(self.markdown, map_path)
        data['comments'][0]['stance'] = 'agree'
        map_path.write_text(json.dumps(data))
        self.assertEqual(brief.resolve(self.markdown, map_path)['comments'][0]['stance'], 'agree')

    def test_unknown_feedback_format_refuses(self):
        map_path = self.map_for(self.markdown)
        map_path.write_text(map_path.read_text().replace('"format": 1', '"format": 9'))
        with self.assertRaises(brief.Refusal):
            brief.resolve(self.markdown, map_path)

    def test_broken_evidence_path_and_fragment_are_detected(self):
        self.markdown.write_text(MD + '\n[Proof](proof.md#validation)\n')
        with self.assertRaises(brief.Refusal):
            brief.check(self.markdown)
        (self.root / 'proof.md').write_text('# Proof\n')
        with self.assertRaises(brief.Refusal):
            brief.check(self.markdown)
        (self.root / 'proof.md').write_text('# Proof\n\n## Validation\n\nChecked.\n')
        self.assertEqual(brief.check(self.markdown)['links'], 1)

    def test_manual_html_content_edit_changes_fingerprint(self):
        self.build()
        map_path = self.map_for(self.out)
        self.out.write_text(brief.read(self.out).replace('>Result<', '>Outcome<'))
        data = brief.resolve(self.out, map_path)
        self.assertEqual(data['comments'][0]['reasons'], ['revision_changed'])

    def test_snapshot_attributes_and_generated_rail_do_not_change_revision(self):
        initial = brief.content_revision(SOURCE, 'example-html', 'engineering')
        snapshot = SOURCE.replace('data-brief-anchor="sec-result"', 'data-brief-anchor="sec-result" data-nid="sec-result" data-ntitle="Result" class="notable"')
        snapshot = snapshot.replace('<nav class="sections"></nav>', '<nav class="sections"><a href="#sec-result">Result</a></nav>')
        self.assertEqual(brief.content_revision(snapshot, 'example-html', 'engineering'), initial)

    def test_mp4_is_not_implemented(self):
        movie = self.root / 'future.mp4'
        movie.write_bytes(b'placeholder')
        with self.assertRaisesRegex(brief.Refusal, 'MP4 is reserved'):
            brief.inspect(movie)

    def test_browser_boolean_attribute_serialization_keeps_revision(self):
        original = SOURCE.replace('</main>', '<select><option selected>Default</option></select></main>')
        saved = original.replace('option selected>', 'option selected="">')
        self.assertEqual(brief.content_revision(original, 'example-html', 'engineering'), brief.content_revision(saved, 'example-html', 'engineering'))

    def test_upstream_anchor_hook_drift_refuses(self):
        original_read = brief.read
        def changed_read(path):
            text = original_read(path)
            return text.replace("if (num) id = pre + '-' + num.textContent.trim();", '/* changed upstream */') if Path(path).name == 'notes.js' else text
        with patch.object(brief, 'read', side_effect=changed_read):
            with self.assertRaisesRegex(brief.Refusal, 'anchor hook changed'):
                self.build()
        self.assertFalse(self.out.exists())

    def test_malformed_document_metadata_refuses(self):
        self.markdown.write_text(MD.replace('{"id":"example-md","medium":"markdown","purpose":"engineering"}', '{}'))
        with self.assertRaises(brief.Refusal):
            brief.inspect(self.markdown)

    def test_script_markup_in_reader_words_is_not_an_island(self):
        self.build()
        original = brief.read(self.out)
        empty, _ = brief.island(original, 'report-notes')
        words = "π 🦉\u2028 Explain <script id='report-notes'> and <script id='report-concurs'>."
        payload = {'sec-result': [{'text': words}]}
        block = '<script id="report-notes" data-format="1">' + brief.encode(payload) + '</script>'
        self.out.write_text(original.replace(empty, block))
        self.build()
        self.assertEqual(brief.feedback(self.out)['comments'][0]['text'], words)

    def test_reader_evidence_depth_does_not_change_content_revision(self):
        original = SOURCE.replace('</main>', '<div data-depth="2">Supporting proof</div></main>')
        collapsed = original.replace('data-depth="2"', 'data-depth="2" hidden=""')
        self.assertEqual(brief.content_revision(original, 'example-html', 'engineering'), brief.content_revision(collapsed, 'example-html', 'engineering'))

    def test_valid_void_and_implicit_table_serialization_keeps_revision(self):
        original = SOURCE.replace('</main>', '<p>First<br/>second</p><table><tr><td>Evidence</td></tr></table></main>')
        saved = original.replace('<br/>', '<br>').replace('<table><tr>', '<table><tbody><tr>').replace('</tr></table>', '</tr></tbody></table>')
        self.assertEqual(brief.content_revision(original, 'example-html', 'engineering'), brief.content_revision(saved, 'example-html', 'engineering'))

    def test_reader_disclosure_state_does_not_change_content_revision(self):
        original = SOURCE.replace('</main>', '<details><summary>Evidence</summary>Proof</details></main>')
        expanded = original.replace('<details>', '<details open="">')
        self.assertEqual(brief.content_revision(original, 'example-html', 'engineering'), brief.content_revision(expanded, 'example-html', 'engineering'))

    def test_real_duplicate_and_unclosed_islands_still_refuse(self):
        self.build()
        original = brief.read(self.out)
        block, _ = brief.island(original, 'report-notes')
        variants = [original.replace('</body>', block + '</body>'), original.replace(block, block.removesuffix('</script>'))]
        for damaged in variants:
            with self.subTest(damaged=damaged[-80:]):
                self.out.write_text(damaged)
                with self.assertRaises(brief.Refusal):
                    self.build()
                self.assertEqual(brief.read(self.out), damaged)


if __name__ == '__main__':
    unittest.main()
