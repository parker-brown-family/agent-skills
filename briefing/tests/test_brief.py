import importlib.util
from html.parser import HTMLParser
import io
import json
import os
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
# A wall shaped like brief-wall's: a labelled comment and an embedded image.
WALL = ('<style id="brief-wall">\n/* brief-wall — theme kanagawa (dark), wallpaper test.png */\n'
        ':root { --wall: url("data:image/webp;base64,' + 'QUJD' * 40 + '"); }\n</style>')
MD = '''<!-- briefing: {"id":"example-md","medium":"markdown","purpose":"engineering"} -->
# Example
<a id="sec-result"></a>
## Result
A comment stays attached to its passage.
'''


def wall_elements(text):
    found = []
    class Styles(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == 'style' and dict(attrs).get('id') == 'brief-wall':
                found.append(tag)
    Styles().feed(text)
    return len(found)


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
        process.return_value.stdout = WALL
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

    # ---- links the checker used to skip
    def test_titled_image_reference_and_file_links_are_checked(self):
        for link in ('[t](gone.md "a title")', '![chart](gone.png)', '[ref][r]\n\n[r]: gone.md', '[f](file:///nonexistent/gone.md)', '[a](<gone file.md>)'):
            with self.subTest(link=link):
                self.markdown.write_text(MD + '\n' + link + '\n')
                with self.assertRaisesRegex(brief.Refusal, 'broken local link'):
                    brief.check(self.markdown)
        (self.root / 'proof.md').write_text('# Proof\n\nA paragraph. ^held\n')
        url = (self.root / 'proof.md').as_uri()
        self.markdown.write_text(MD + f'\n[t](proof.md "title") ![i](proof.md) [f]({url}#held) [s](#sec-result)\n')
        self.assertEqual(brief.check(self.markdown)['links'], 4)

    def test_code_examples_are_not_links_and_external_links_are_counted(self):
        self.markdown.write_text(MD + '\n`[x](gone.md)`\n\n~~~\n[y](gone.md)\n~~~\n\n[web](https://example.com/a)\n')
        result = brief.check(self.markdown)
        self.assertEqual(result['links'], 1)
        self.assertEqual(result['external_links_unchecked'], 1)
        self.assertNotIn('edited_since_build', result)  # A Markdown brief has no build to compare.

    # ---- build guards
    def test_placeholder_inside_fingerprinted_region_refuses(self):
        self.src.write_text(SOURCE.replace('<!--BRIEF:notes--></body>', '</body>').replace('<!--/brief-content-->', '<!--BRIEF:notes--><!--/brief-content-->'))
        with self.assertRaisesRegex(brief.Refusal, 'outside the <!--brief-content--> region'):
            self.build()
        self.assertFalse(self.out.exists())

    def test_hand_edit_to_the_page_refuses_until_discarded_explicitly(self):
        self.annotate()
        edited = brief.read(self.out).replace('>Result<', '>Result, fixed by hand<')
        self.out.write_text(edited)
        self.assertTrue(brief.check(self.out)['edited_since_build'])
        with self.assertRaisesRegex(brief.Refusal, 'edited after its last build'):
            self.build()
        self.assertEqual(brief.read(self.out), edited)
        result = brief.build(self.src, self.out, 'example-html', 'engineering', discard_edits=True)
        self.assertEqual(Path(result['discarded_output_edits']).read_text(), edited)
        # The reader commented on wording this rebuild discarded; their revision is now unknown.
        self.assertIsNone(result['feedback_revision'])
        self.assertEqual(brief.feedback(self.out)['comments'][0]['text'], 'Keep </script> and <!-- this exact text.')
        self.assertFalse(brief.check(self.out)['edited_since_build'])

    def test_an_unrelated_page_at_the_output_path_is_not_overwritten(self):
        self.out.write_text('<html><body>Someone else\'s page</body></html>')
        with self.assertRaisesRegex(brief.Refusal, 'was not built by this helper'):
            self.build()
        self.assertEqual(self.out.read_text(), '<html><body>Someone else\'s page</body></html>')

    def test_missing_sibling_skills_refuse_and_name_the_markdown_route(self):
        with patch.object(brief, 'KIT_FILES', [self.root / 'absent/base.css']):
            with self.assertRaisesRegex(brief.Refusal, 'write the brief in Markdown'):
                self.build()
            report = brief.doctor()
        self.assertFalse(report['html_build']['ready'])
        self.assertIsNone(report['wallpaper']['ready'])  # Unknown, not false: nothing was looked at.
        self.assertTrue(report['markdown']['ready'])

    def test_wallpaper_failure_names_its_reason_and_no_wall_still_builds(self):
        reason = 'brief-wall: no Omarchy themes with backgrounds found under /usr/share/omarchy/themes'
        brief.subprocess.run.side_effect = brief.subprocess.CalledProcessError(1, 'brief-wall', stderr=reason + '\n')
        with self.assertRaisesRegex(brief.Refusal, 'no Omarchy themes.*--no-wall'):
            self.build()
        result = brief.build(self.src, self.out, 'example-html', 'engineering', no_wall=True)
        self.assertIsNone(result['wallpaper'])
        self.assertEqual(wall_elements(brief.read(self.out)), 0)  # base.css only names the block in a comment
        self.assertFalse(brief.check(self.out)['edited_since_build'])
        brief.subprocess.run.side_effect = None
        walled = self.root / 'walled.html'
        brief.build(self.src, walled, 'example-html', 'engineering')
        self.assertEqual(wall_elements(brief.read(walled)), 1)

    # ---- scaffold
    def test_html_scaffold_builds_and_check_refuses_until_written(self):
        source = self.root / 'fresh.src.html'
        created = brief.scaffold(source, 'fresh-brief', 'decision', 'A <fresh> brief')
        self.assertIn('fresh.html', created['next'][0])
        self.assertIn('what choice is mine', source.read_text())
        output = self.root / 'fresh.html'
        brief.build(source, output, 'fresh-brief', 'decision')
        with self.assertRaisesRegex(brief.Refusal, 'unwritten scaffold passage'):
            brief.check(output)
        written = source.read_text().replace('TODO(brief)', 'Written')
        source.write_text(written)
        brief.build(source, output, 'fresh-brief', 'decision', discard_edits=False)
        self.assertEqual(brief.check(output)['id'], 'fresh-brief')
        self.assertIn('A &lt;fresh&gt; brief', brief.read(output))

    def test_markdown_scaffold_checks_once_written_and_never_overwrites(self):
        source = self.root / 'fresh.md'
        brief.scaffold(source, 'fresh-md', 'summary')
        with self.assertRaisesRegex(brief.Refusal, 'unwritten scaffold passage'):
            brief.check(source)
        source.write_text(source.read_text().replace('TODO(brief)', 'Written'))
        self.assertEqual(brief.check(source)['anchors'], 2 + 3)  # two explicit anchors, three heading slugs
        with self.assertRaisesRegex(brief.Refusal, 'never overwrites'):
            brief.scaffold(source, 'fresh-md', 'summary')
        with self.assertRaises(brief.Refusal):
            brief.scaffold(self.root / 'fresh.txt', 'fresh-md', 'summary')

    # ---- the HTML reader's Copy map, pasted back
    def copy_text(self, revision, *, unknown=False, orphan=False):
        lines = ['NOTES — example-html-' + revision[7:19], '1 notes on 1 elements · 1 concur.',
                 'Each [anchor] is an element id in that file — search it to find the passage.', '',
                 '[sec-result] Result  ✓ concur', '  · Explain the boundary. [Not an anchor]', '']
        if unknown:
            lines.append('REVISION UNKNOWN — review the prior brief before acting.')
        if orphan:
            lines += ['', '[sec-gone] UNRESOLVED — target missing', '  · Said about a removed passage', '  · Explicit agreement on the earlier target']
        return '\n'.join(lines) + '\n'

    def test_copy_map_text_resolves_against_the_page_it_came_from(self):
        self.build()
        revision = brief.inspect(self.out)[2]
        pasted = self.root / 'pasted.txt'
        pasted.write_text('Here are my notes:\n\n' + self.copy_text(revision))
        data = brief.resolve(self.out, pasted)
        self.assertEqual(data['source'], 'copy-map')
        self.assertFalse(data['text_exact'])
        self.assertIsNone(data['document']['revision'])  # only a prefix travels, and it is labelled as one
        self.assertEqual(data['document']['revision_prefix'], revision[:19])
        self.assertEqual([(c['stance'], c['text'], c['status']) for c in data['comments']],
                         [('agree', '', 'resolved'), (None, 'Explain the boundary. [Not an anchor]', 'resolved')])

    def test_copy_map_from_another_revision_or_with_orphans_needs_review(self):
        self.build()
        pasted = self.root / 'pasted.txt'
        pasted.write_text(self.copy_text('sha256:' + '0' * 64))
        self.assertTrue(all(c['reasons'] == ['revision_changed'] for c in brief.resolve(self.out, pasted)['comments']))
        pasted.write_text(self.copy_text(brief.inspect(self.out)[2], unknown=True, orphan=True))
        comments = brief.resolve(self.out, pasted)['comments']
        self.assertEqual([c['target'] for c in comments], ['sec-result', 'sec-result', 'sec-gone', 'sec-gone'])
        self.assertEqual(comments[2]['reasons'], ['revision_unknown', 'target_missing'])
        self.assertEqual(comments[3]['stance'], 'agree')

    def test_copy_map_arrives_on_stdin_and_nonsense_refuses(self):
        self.build()
        with patch.object(brief.sys, 'stdin', io.StringIO(self.copy_text(brief.inspect(self.out)[2]))):
            self.assertEqual(brief.resolve(self.out, Path('-'))['comments'][1]['status'], 'resolved')
        with patch.object(brief.sys, 'stdin', io.StringIO('looks good to me')):
            with self.assertRaisesRegex(brief.Refusal, 'neither a format-1 JSON envelope nor Copy map text.*paste all of it'):
                brief.resolve(self.out, Path('-'))


    # ---- found by a clean-context agent following only the docs
    def test_rebuild_keeps_the_real_wallpaper_not_base_css_naming_it(self):
        self.build()
        first = brief.wall_of(brief.read(self.out))
        self.assertIn('base64,QUJD', first)
        brief.subprocess.run.reset_mock()
        result = self.build()
        self.assertEqual(brief.wall_of(brief.read(self.out)), first)
        self.assertEqual(result['wallpaper'], 'kanagawa · test.png')
        self.assertEqual(brief.check(self.out)['wallpaper'], 'kanagawa · test.png')
        brief.subprocess.run.assert_not_called()  # kept, not re-picked

    def test_an_imageless_wall_left_by_the_old_bug_is_replaced(self):
        self.build()
        damaged = brief.read(self.out).replace(brief.wall_of(brief.read(self.out)), '<style id="brief-wall"> block that goes straight after this */ :root{}</style>')
        self.out.write_text(damaged)
        self.assertIsNone(brief.check(self.out)['wallpaper'])
        self.build()
        self.assertIn('base64,QUJD', brief.wall_of(brief.read(self.out)))

    def test_a_built_page_is_readable_like_any_file(self):
        self.build()
        umask = os.umask(0)
        os.umask(umask)
        self.assertEqual(self.out.stat().st_mode & 0o777, 0o666 & ~umask)
        os.chmod(self.out, 0o640)
        self.build()
        self.assertEqual(self.out.stat().st_mode & 0o777, 0o640)

    def test_copy_map_survives_crlf_a_bom_and_a_chat_quote(self):
        self.build()
        text = self.copy_text(brief.inspect(self.out)[2])
        pasted = self.root / 'pasted.txt'
        for variant in ('\ufeff' + text.replace('\n', '\r\n'), ''.join('> ' + line + '\n' for line in text.splitlines())):
            with self.subTest(variant=variant[:12]):
                pasted.write_text(variant, newline='')
                self.assertEqual([c['status'] for c in brief.resolve(self.out, pasted)['comments']], ['resolved', 'resolved'])

    def test_check_lists_every_broken_link_at_once(self):
        self.markdown.write_text(MD + '\n[a](one.md) [b](two.md) [c](#sec-gone)\n')
        with self.assertRaises(brief.Refusal) as caught:
            brief.check(self.markdown)
        for part in ('one.md', 'two.md', '#sec-gone'):
            self.assertIn(part, str(caught.exception))

    def test_a_scaffolded_source_names_itself_so_rebuilds_need_no_flags(self):
        source = self.root / 'named.src.html'
        created = brief.scaffold(source, 'named-brief', 'summary')
        self.assertNotIn('--id', created['next'][0])
        output = self.root / 'named.html'
        self.assertEqual(brief.build(source, output)['id'], 'named-brief')
        with self.assertRaisesRegex(brief.Refusal, 'disagrees with the source'):
            brief.build(source, output, 'other-brief')
        with self.assertRaisesRegex(brief.Refusal, 'pass --id and --purpose'):
            brief.build(self.src, self.root / 'unnamed.html')

    def test_a_page_of_another_brief_names_its_id(self):
        self.build()
        with self.assertRaisesRegex(brief.Refusal, "belongs to the brief 'example-html'.*--id example-html"):
            brief.build(self.src, self.out, 'another-brief', 'engineering')


if __name__ == '__main__':
    unittest.main()


GRILL_SOURCE = SOURCE.replace('<p>A comment stays attached to its passage.</p>', '<p>A comment stays attached to its passage.</p>{grill}')


class WorkLoopFixture(unittest.TestCase):
    """A temporary directory, a screenshot, a ledger path and the helpers both work-loop suites use."""
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.ledger = self.root / 'work.calls.json'
        self.shot = self.root / 'shot.png'
        self.shot.write_bytes(b'\x89PNG\r\n\x1a\n' + b'pixels' * 10)
        fake = patch.object(brief.subprocess, 'run')
        fake.start().return_value.stdout = WALL
        self.addCleanup(fake.stop)

    def call(self, title, uncertainty='low', taste='low', **extra):
        return brief.record_call(self.ledger, title, 'the chosen option', 'the reason', uncertainty, taste, **extra)

    def run_main(self, *argv):
        out = io.StringIO()
        with patch.object(brief.sys, 'argv', ['brief.py', *map(str, argv)]), patch.object(brief.sys, 'stdout', out):
            code = brief.main()
        return code, out.getvalue()

    def page(self, name, grill, meta=None):
        source = self.root / (name + '.src.html')
        text = GRILL_SOURCE.replace('{grill}', grill)
        if meta:
            text = text.replace('<!--BRIEF:head-->', '<!-- briefing: ' + json.dumps(meta) + ' --><!--BRIEF:head-->')
        source.write_text(text)
        output = self.root / (name + '.html')
        brief.build(source, output, name, 'decision')
        return output

    def rebuild(self, name, grill, meta=None):
        source = self.root / (name + '.src.html')
        text = GRILL_SOURCE.replace('{grill}', grill)
        if meta:
            text = text.replace('<!--BRIEF:head-->', '<!-- briefing: ' + json.dumps(meta) + ' --><!--BRIEF:head-->')
        source.write_text(text)
        brief.build(source, self.root / (name + '.html'), name, 'decision')
        return self.root / (name + '.html')

    def stamp(self, page, concurs=None, notes=None):
        text = brief.read(page)
        for name, value in (('report-concurs', concurs), ('report-notes', notes)):
            if value is not None:
                empty, _ = brief.island(text, name)
                text = text.replace(empty, f'<script type="application/json" id="{name}" data-format="1">{brief.encode(value)}</script>')
        page.write_text(text)



class WorkLoopTests(WorkLoopFixture):
    """The loop while work runs: orient, call, calls, verdict, and the decision anchors they rely on."""
    def test_the_policy_stops_on_high_unknown_one_way_and_conflicts_and_tightens_with_posture(self):
        cases = [  # (uncertainty, taste, posture) -> outcome
            ('low', 'low', 'strict', 'carry-on'), ('medium', 'medium', 'relaxed', 'carry-on'),
            ('medium', 'medium', 'standard', 'stop'), ('medium', 'low', 'standard', 'carry-on'),
            ('medium', 'low', 'strict', 'stop'), ('high', 'low', 'relaxed', 'stop'), ('low', 'high', 'relaxed', 'stop'),
            ('unknown', 'low', 'relaxed', 'stop')]
        for uncertainty, taste, posture, expected in cases:
            with self.subTest(uncertainty=uncertainty, taste=taste, posture=posture):
                self.assertEqual(brief.decide(uncertainty, taste, posture)[0], expected)
        self.assertEqual(brief.decide('low', 'low', 'relaxed', door='one-way')[0], 'stop')
        outcome, reasons = brief.decide('low', 'low', 'relaxed', conflicts=['q-reserve'])
        self.assertEqual(outcome, 'stop')
        self.assertIn('q-reserve', reasons[0])

    def test_a_call_records_its_evidence_and_judgement_and_refuses_ambiguity(self):
        made = self.call('Footer at 28 px', taste='medium', posture='relaxed', evidence=[self.shot], passed_over=['40 px'])
        self.assertEqual((made['outcome'], made['status']), ('carry-on', 'open'))
        entry = brief.load_ledger(self.ledger)['calls'][0]
        self.assertEqual(entry['id'], 'call-footer-at-28-px')
        self.assertEqual(entry['evidence'][0]['href'], 'shot.png')
        self.assertTrue(entry['evidence'][0]['sha256'].startswith('sha256:'))
        self.assertEqual(entry['judgement']['slot'], brief.SLOT)
        self.assertEqual(entry['judgement']['filled_by'], 'agent')
        undeclared = self.call('Undeclared posture', 'medium', 'medium')
        self.assertEqual(undeclared['outcome'], 'stop')  # undeclared reads as standard, and says so
        self.assertFalse(brief.load_ledger(self.ledger)['calls'][1]['judgement']['posture_declared'])
        with self.assertRaisesRegex(brief.Refusal, 'already in the ledger'):
            self.call('Footer at 28 px')
        with self.assertRaisesRegex(brief.Refusal, 'is not a file'):
            self.call('Missing proof', evidence=[self.root / 'gone.png'])
        with self.assertRaisesRegex(brief.Refusal, 'NAME.calls.json'):
            brief.record_call(self.root / 'notes.json', 'x', 'y', 'z', 'low', 'low')
        with self.assertRaisesRegex(brief.Refusal, 'needs --because'):
            brief.record_call(self.ledger, 'x', 'y', ' ', 'low', 'low')

    def test_exit_codes_let_a_workflow_branch_without_parsing(self):
        code, out = self.run_main('call', self.ledger, '--title', 'Accent colour', '--chose', 'rose', '--because', 'cover',
                                  '--uncertainty', 'low', '--taste', 'high', '--posture', 'relaxed')
        self.assertEqual(code, 3)
        self.assertEqual(json.loads(out)['status'], 'asked')
        code, out = self.run_main('calls', self.ledger)
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(out)['settled'])
        code, _ = self.run_main('verdict', self.ledger, 'call-accent-colour', 'concurred')
        self.assertEqual(code, 0)
        self.assertEqual(self.run_main('calls', self.ledger)[0], 0)

    def test_work_settles_only_when_every_call_is_answered_and_its_evidence_unchanged(self):
        self.call('Footer at 28 px', evidence=[self.shot])
        self.call('Accent colour', taste='high')
        self.assertFalse(brief.calls_report(self.ledger)['settled'])
        with self.assertRaisesRegex(brief.Refusal, 'reason in --note'):
            brief.record_verdict(self.ledger, 'call-accent-colour', 'overturned')
        brief.record_verdict(self.ledger, 'call-accent-colour', 'overturned', note='use teal', follow_up='https://example.org/1')
        brief.record_verdict(self.ledger, 'call-footer-at-28-px', 'concurred')
        self.assertTrue(brief.calls_report(self.ledger)['settled'])
        self.shot.write_bytes(self.shot.read_bytes() + b'!')  # a concur covers the screenshot seen, not a later one
        report = brief.calls_report(self.ledger)
        self.assertFalse(report['settled'])
        self.assertIn('evidence changed since it was recorded', report['calls'][0]['needs'])
        with self.assertRaisesRegex(brief.Refusal, 'is not in'):
            brief.record_verdict(self.ledger, 'call-nope', 'concurred')

    def test_rendered_calls_build_into_a_stampable_brief_and_a_stamp_syncs_back(self):
        self.call('Footer at 28 px', evidence=[self.shot], context='The plan left it open', undo='one constant')
        self.call('Accent colour', taste='high')
        section = brief.render_calls(self.ledger)
        self.assertIn('data:image/png;base64,', section)
        self.assertIn(brief.SLOT, section)
        self.assertIn('Stopped:', section)
        page = self.page('closing', section, {'calls': 'work.calls.json'})
        found = {d['anchor']: d['title'] for d in brief.Decisions(brief.read(page)).decisions()}
        self.assertEqual(found, {'call-footer-at-28-px': 'Footer at 28 px', 'call-accent-colour': 'Accent colour'})
        self.assertEqual(brief.check(page)['calls'], {'ledger': 'work.calls.json', 'open': 1, 'asked': 1})
        self.stamp(page, concurs={'call-footer-at-28-px': '2026-11-01T07:00Z'},
                   notes={'call-accent-colour': [{'text': 'teal, not rose', 'title': 'Accent', 'ts': '2026-11-01T07:01Z'}]})
        synced = brief.sync_calls(self.ledger, page)
        self.assertEqual(synced['concurred'], ['call-footer-at-28-px'])
        self.assertEqual(synced['notes_to_answer'], {'call-accent-colour': ['teal, not rose']})
        verdict = brief.load_ledger(self.ledger)['calls'][0]['verdict']
        self.assertEqual((verdict['via'], verdict['brief']), ('concur stamp', 'closing'))
        self.assertEqual(verdict['revision'], brief.check(page)['revision'])
        self.assertFalse(synced['settled'])

    def test_check_refuses_a_brief_that_hides_an_open_call(self):
        self.call('Footer at 28 px')
        page = self.page('closing', '', {'calls': 'work.calls.json'})
        with self.assertRaisesRegex(brief.Refusal, 'open calls missing from the brief: call-footer-at-28-px'):
            brief.check(page)
        brief.record_verdict(self.ledger, 'call-footer-at-28-px', 'concurred')
        self.assertEqual(brief.check(page)['calls']['open'], 0)

    def test_a_decision_without_an_anchor_cannot_be_built_or_pass_check(self):
        loose = '<div class="grill"><div class="ask"><h3>Ship it?</h3></div></div>'
        with self.assertRaisesRegex(brief.Refusal, 'Unanchored: Ship it\\?'):
            self.page('loose', loose)
        anchored = '<div class="grill"><div class="ask" id="q-ship" data-brief-anchor="q-ship"><h3>Ship it?</h3><p class="q">sub</p></div></div>'
        page = self.page('anchored', anchored)  # a .q inside an .ask is part of that decision, not another one
        self.assertEqual([d['anchor'] for d in brief.Decisions(brief.read(page)).decisions()], ['q-ship'])
        page.write_text(brief.read(page).replace(' id="q-ship" data-brief-anchor="q-ship"', ''))
        with self.assertRaisesRegex(brief.Refusal, 'needs id="x" data-brief-anchor="x"'):
            brief.check(page)
        grill_q = '<div class="grill"><p class="q"><b>Which root?</b></p></div>'
        with self.assertRaisesRegex(brief.Refusal, 'Which root'):
            self.page('grillq', grill_q)

    def test_orient_reads_up_the_derivation_and_reconciles_the_ledger(self):
        plan = self.page('plan', '<div class="grill"><div class="ask" id="q-reserve" data-brief-anchor="q-reserve"><h3>Never move the page</h3></div>'
                                 '<div class="ask" id="q-fold" data-brief-anchor="q-fold"><h3>Fold the builder</h3></div></div>')
        self.stamp(plan, concurs={'q-reserve': '2026-10-28T14:02Z'},
                   notes={'q-fold': [{'text': 'not without asking me', 'title': 'Fold', 'ts': '2026-10-28T14:03Z'}]})
        self.call('Footer at 28 px')
        self.call('Accent colour', taste='high')
        closing = self.page('closing', brief.render_calls(self.ledger),
                            {'derives_from': ['plan.html', 'gone.html'], 'calls': 'work.calls.json'})
        brief.record_verdict(self.ledger, 'call-accent-colour', 'overturned', note='use teal')
        tree = brief.orient(closing)
        self.assertEqual([d['anchor'] for d in tree['approved']], [])
        self.assertEqual([d['anchor'] for d in tree['overturned']], ['call-accent-colour'])
        self.assertEqual([d['anchor'] for d in tree['unstamped']], [])  # an open call is listed once, under open calls
        self.assertEqual([c['id'] for c in tree['ledger']['open']], ['call-footer-at-28-px'])
        self.assertEqual(tree['parents'][1]['state'], 'unavailable: file missing')
        text = brief.orient_text(tree)
        self.assertIn('[q-reserve]  Never move the page   · from plan', text)
        self.assertIn('[q-fold]  Fold the builder   · from plan', text.split('NOT STAMPED')[1].split('OVERTURNED')[0])
        self.assertIn('"not without asking me"   · on plan', text)
        self.assertIn('gone.html · unavailable: file missing', text)
        self.assertIn('"use teal"', text)
        self.assertIn('SETTLED  no', text)
        brief.record_verdict(self.ledger, 'call-footer-at-28-px', 'concurred')  # a verdict in chat counts as a stamp
        self.assertEqual([d['anchor'] for d in brief.orient(closing)['approved']], ['call-footer-at-28-px'])
        bare = self.page('bare', '')
        self.assertIn('CALLS  no ledger named', brief.orient_text(brief.orient(bare)))

    def test_orient_survives_a_cycle_of_derivations(self):
        one = self.page('one', '', {'derives_from': ['two.html']})
        self.page('two', '', {'derives_from': ['one.html']})
        tree = brief.orient(one)
        self.assertEqual(tree['parents'][0]['parents'][0]['state'], 'already read')

    def test_scaffold_names_its_parents_and_ledger_relative_to_itself(self):
        parent = self.page('plan', '')
        source = self.root / 'sub' / 'closing.src.html'
        brief.scaffold(source, 'closing', 'summary', derives_from=[parent], calls=self.ledger)
        meta = json.loads(brief.META.search(source.read_text())[1])
        self.assertEqual(meta['derives_from'], ['../plan.html'])
        self.assertEqual(meta['calls'], '../work.calls.json')
        with self.assertRaisesRegex(brief.Refusal, 'not there'):
            brief.scaffold(self.root / 'x.src.html', 'x', 'summary', derives_from=[self.root / 'nope.html'])


class ReviewFindingTests(WorkLoopFixture):
    """One test per finding of the Codex review of the first cut, each written to fail on that cut."""
    def test_a_stamp_on_a_row_rendered_from_other_words_is_not_applied(self):
        self.call('Footer at 28 px')
        page = self.page('closing', brief.render_calls(self.ledger), {'calls': 'work.calls.json'})
        other = self.root / 'other.calls.json'  # same id, other words: what the reader saw is not this call
        data = brief.load_ledger(self.ledger)
        data['calls'][0]['chose'] = 'a 60 px footer'
        other.write_text(json.dumps(data))
        self.stamp(page, concurs={'call-footer-at-28-px': '2026-11-01T07:00Z'})
        synced = brief.sync_calls(other, page)
        self.assertEqual((synced['concurred'], synced['mismatched']), ([], ['call-footer-at-28-px']))
        self.assertEqual(brief.load_ledger(other)['calls'][0]['status'], 'open')

    def test_check_refuses_rows_that_no_longer_match_their_ledger(self):
        self.call('Footer at 28 px')
        page = self.page('closing', brief.render_calls(self.ledger), {'calls': 'work.calls.json'})
        data = brief.load_ledger(self.ledger)
        data['calls'][0]['because'] = 'a different reason'
        self.ledger.write_text(json.dumps(data))
        with self.assertRaisesRegex(brief.Refusal, 'rendered from other words'):
            brief.check(page)

    def test_a_stamp_on_earlier_wording_is_not_approval(self):
        source = self.root / 'plan.src.html'
        keep = '<div class="grill"><div class="ask" id="q-data" data-brief-anchor="q-data"><h3>Keep all data</h3></div></div>'
        page = self.page('plan', keep)
        self.stamp(page, concurs={'q-data': '2020-01-01T00:00Z'})  # long before any build, so never current by time
        self.assertEqual([d['anchor'] for d in brief.orient(page)['approved']], ['q-data'])
        source.write_text(source.read_text().replace('Keep all data', 'Delete all data'))
        brief.build(source, page, 'plan', 'decision')
        tree = brief.orient(page)
        self.assertEqual(tree['approved'], [])
        self.assertEqual([d['title'] for d in tree['restamp']], ['Delete all data'])
        self.assertIn('STAMPED ON ANOTHER VERSION', brief.orient_text(tree))

    def test_a_later_overturn_outranks_a_stamp_left_on_the_page(self):
        self.call('Footer at 28 px')
        page = self.page('closing', brief.render_calls(self.ledger), {'calls': 'work.calls.json'})
        self.stamp(page, concurs={'call-footer-at-28-px': '2026-11-01T07:00Z'})
        brief.sync_calls(self.ledger, page)
        brief.record_verdict(self.ledger, 'call-footer-at-28-px', 'overturned', note='Do not use it')
        tree = brief.orient(page)
        self.assertEqual(tree['approved'], [])
        self.assertEqual([d['note'] for d in tree['overturned']], ['Do not use it'])

    def test_a_malformed_or_hollow_ledger_is_refused_not_trusted(self):
        hollow = {'format': 1, 'kind': 'briefing-calls', 'calls': [{'id': 'call-x', 'title': 'x', 'status': 'concurred'}]}
        self.ledger.write_text(json.dumps(hollow))
        with self.assertRaisesRegex(brief.Refusal, 'call-x has no chose'):
            brief.calls_report(self.ledger)
        # A well-formed ledger, then poison one field at a time.
        self.ledger.unlink()
        self.call('Footer at 28 px', evidence=[self.shot])
        good = brief.load_ledger(self.ledger)
        for field, value, message in (('id', 'call-"><script>', 'no valid call'), ('evidence', [{'href': 'shot.png', 'sha256': 'x', 'kind': 'screenshot'}], 'malformed evidence'),
                                      ('evidence', [{'href': 'shot.png', 'sha256': good['calls'][0]['evidence'][0]['sha256'], 'kind': '<img onerror=x>'}], 'malformed evidence')):
            with self.subTest(field=field):
                bad = json.loads(json.dumps(good))
                bad['calls'][0][field] = value
                self.ledger.write_text(json.dumps(bad))
                with self.assertRaisesRegex(brief.Refusal, message):
                    brief.render_calls(self.ledger)
        twice = json.loads(json.dumps(good))
        twice['calls'].append(twice['calls'][0])
        self.ledger.write_text(json.dumps(twice))
        with self.assertRaisesRegex(brief.Refusal, 'appears twice'):
            brief.calls_report(self.ledger)

    def test_concurrent_writers_lose_no_call(self):
        import threading
        errors = []
        def record(n):
            try:
                self.call(f'Call number {n}')
            except Exception as exc:  # noqa: BLE001 — any failure is the finding
                errors.append(exc)
        threads = [threading.Thread(target=record, args=(n,)) for n in range(16)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        self.assertEqual(len(brief.load_ledger(self.ledger)['calls']), 16)

    def test_settled_is_unknown_while_ancestry_or_a_ledger_cannot_be_read(self):
        self.ledger.write_text(json.dumps({'format': 1, 'kind': 'briefing-calls', 'calls': []}))
        parent = self.page('plan', '', {'calls': 'plan.calls.json'})  # names a ledger that is not there
        child = self.page('closing', '', {'derives_from': ['plan.html', 'gone.html'], 'calls': 'work.calls.json'})
        settled = brief.orient(child)['settled']
        self.assertEqual(settled['state'], 'unknown')
        self.assertTrue(any('gone.html' in why for why in settled['why']))
        self.assertTrue(any('plan.calls.json' in why for why in settled['why']))
        self.assertIn('SETTLED  unknown', brief.orient_text(brief.orient(child)))
        self.assertTrue(parent.exists())

    def test_retired_calls_may_change_evidence_but_standing_ones_may_not(self):
        self.call('Badges', evidence=[self.shot])
        brief.record_verdict(self.ledger, 'call-badges', 'overturned', note='a border instead')
        self.shot.write_bytes(b'the fix replaced the screenshot')  # the overturn is why it changed
        self.assertTrue(brief.calls_report(self.ledger)['settled'])
        other = self.root / 'other.png'
        other.write_bytes(b'one')
        self.call('Glow', evidence=[other])
        brief.record_verdict(self.ledger, 'call-glow', 'concurred')
        other.unlink()
        self.assertFalse(brief.calls_report(self.ledger)['settled'])

    def test_nested_questions_and_an_unclosed_paragraph_are_still_decisions(self):
        nested = '<div class="grill"><div class="grill-q" id="q-a" data-brief-anchor="q-a"><b>Which?</b><p class="q"><b>And this?</b></p></div></div>'
        with self.assertRaisesRegex(brief.Refusal, 'And this'):
            self.page('nested', nested)
        unclosed = '<div class="grill"><p class="ask" id="q-b" data-brief-anchor="q-b"><b>First</b><div class="q"><b>Second</b></div></div>'
        with self.assertRaisesRegex(brief.Refusal, 'Second'):
            self.page('unclosed', unclosed)

    def test_file_evidence_is_checked_before_it_is_rendered(self):
        log = self.root / 'run.log'
        log.write_text('passed')
        self.call('Ship the log', evidence=[log])
        log.write_text('failed')
        with self.assertRaisesRegex(brief.Refusal, 'changed since'):
            brief.render_calls(self.ledger)
        log.unlink()
        with self.assertRaisesRegex(brief.Refusal, 'is missing'):
            brief.render_calls(self.ledger)


class CallOrderTests(WorkLoopFixture):
    def test_stopped_calls_lead_heavier_calls_follow_and_routine_ones_are_compact(self):
        self.call('Routine one', undo='one line', passed_over=['other'])
        self.call('Taste call', taste='medium', undo='a rule')
        self.call('Stopped one', taste='high')
        section = brief.render_calls(self.ledger)
        order = [d['anchor'] for d in brief.Decisions(section).decisions()]
        self.assertEqual(order, ['call-stopped-one', 'call-taste-call', 'call-routine-one'])
        routine = section.split('id="call-routine-one"')[1]
        self.assertNotIn('Passed over', routine)
        self.assertIn('Undo', section.split('id="call-taste-call"')[1].split('id="call-routine-one"')[0])
        self.assertIn('The last one was routine, with both readings low, and shows', section)



class ReviewRoundTwoTests(WorkLoopFixture):
    """One test per finding of the second Codex round, each written to fail on the round-one fixes."""
    def test_a_stamp_from_before_a_rebuild_is_not_synced(self):
        self.call('Keep data')
        page = self.page('closing', brief.render_calls(self.ledger), {'calls': 'work.calls.json'})
        self.stamp(page, concurs={'call-keep-data': '2020-01-01T00:00Z'})
        data = brief.load_ledger(self.ledger)
        data['calls'][0]['chose'] = 'delete data'
        self.ledger.write_text(json.dumps(data))
        self.rebuild('closing', brief.render_calls(self.ledger), {'calls': 'work.calls.json'})
        synced = brief.sync_calls(self.ledger, page)
        self.assertEqual(synced['concurred'], [])
        self.assertEqual(synced['stamped_on_another_version'], ['call-keep-data'])

    def test_a_hand_edited_row_is_caught_by_what_it_shows(self):
        self.call('Keep data')
        section = brief.render_calls(self.ledger).replace('<dd>the chosen option</dd>', '<dd>delete everything</dd>')
        page = self.page('closing', section, {'calls': 'work.calls.json'})
        with self.assertRaisesRegex(brief.Refusal, 'differs from what the ledger renders'):
            brief.check(page)
        self.stamp(page, concurs={'call-keep-data': '2099-01-01T00:00Z'})
        self.assertEqual(brief.sync_calls(self.ledger, page)['mismatched'], ['call-keep-data'])

    def test_orient_does_not_approve_a_row_that_shows_another_call(self):
        self.call('Keep data')
        brief.record_verdict(self.ledger, 'call-keep-data', 'concurred')
        other = self.root / 'other.calls.json'
        brief.record_call(other, 'Delete data', 'delete it', 'reason', 'low', 'low', call_id='call-keep-data')
        page = self.page('closing', brief.render_calls(other), {'calls': 'work.calls.json'})
        tree = brief.orient(page)
        self.assertEqual(tree['approved'], [])
        self.assertEqual([m['anchor'] for m in tree['mismatched']], ['call-keep-data'])
        self.assertEqual(tree['settled']['state'], 'unknown')

    def test_an_empty_verdict_or_a_thin_judgement_is_refused(self):
        self.call('Keep data')
        good = brief.load_ledger(self.ledger)
        for mutate, message in ((lambda c: c.update(status='concurred', verdict={}), 'no verdict recorded'),
                                (lambda c: c['judgement'].pop('reasons'), 'no complete judgement'),
                                (lambda c: c['judgement'].pop('filled_by'), 'no complete judgement'),
                                (lambda c: c.update(verdict={'at': 'x', 'via': 'y'}), 'carries a verdict')):
            bad = json.loads(json.dumps(good))
            mutate(bad['calls'][0])
            self.ledger.write_text(json.dumps(bad))
            with self.subTest(message=message), self.assertRaisesRegex(brief.Refusal, message):
                brief.calls_report(self.ledger)

    def test_a_fresh_stamp_after_a_rebuild_counts(self):
        keep = '<div class="grill"><div class="ask" id="q-data" data-brief-anchor="q-data"><h3>Keep all data</h3></div></div>'
        page = self.page('plan', keep)
        self.stamp(page, concurs={'q-data': '2020-01-01T00:00Z'})
        page = self.rebuild('plan', keep.replace('Keep all data', 'Keep most data'))
        self.assertIsNone(brief.island(brief.read(page), 'brief-meta')[1]['feedback_revision'])
        self.assertEqual([d['anchor'] for d in brief.orient(page)['restamp']], ['q-data'])
        self.stamp(page, concurs={'q-data': '2099-01-01T00:00Z'})  # stamped again, after this build
        self.assertEqual([d['anchor'] for d in brief.orient(page)['approved']], ['q-data'])

    def test_a_paragraph_closes_through_inline_elements(self):
        hidden = '<div class="grill"><p class="ask" id="q-a" data-brief-anchor="q-a"><b>First<div class="q"><b>Second</b></div></div>'
        with self.assertRaisesRegex(brief.Refusal, 'Second'):
            self.page('hidden', hidden)

    def test_a_malformed_markdown_sidecar_is_refused(self):
        md = self.root / 'plan.md'
        md.write_text(MD.replace('example-md', 'plan-md'))
        (self.root / 'plan.feedback.json').write_text('{"document": ["bad"], "comments": []}')
        with self.assertRaisesRegex(brief.Refusal, 'format-1 envelope'):
            brief.orient(md)

    def test_a_retired_calls_moved_evidence_is_labelled_not_refused(self):
        log = self.root / 'run.log'
        log.write_text('before')
        self.call('Ship the log', evidence=[log])
        brief.record_verdict(self.ledger, 'call-ship-the-log', 'overturned', note='fix it first')
        log.write_text('after the fix')
        section = brief.render_calls(self.ledger, every=True)
        self.assertIn('is changed since; it is not shown', section)
        self.assertNotIn('run.log</a>', section)



class ReviewRoundThreeTests(WorkLoopFixture):
    """One test per finding of the third Codex round. A row is generated, never written: any edit is a mismatch."""
    def setUp(self):
        super().setUp()
        self.call('Keep data', evidence=[self.shot], undo='one line')

    def page_with(self, edit):
        section = edit(brief.render_calls(self.ledger))
        return self.page('closing', section, {'calls': 'work.calls.json'})

    def test_any_edit_to_a_rendered_row_is_refused(self):
        edits = {
            'a second chose': lambda s: s.replace('<dt>Chose</dt>', '<dt>Chose</dt><dd>delete everything</dd><dt>Chose</dt>', 1),
            'an invented fact': lambda s: s.replace('<dt>Judged</dt>', '<dt>Approved</dt><dd>by the owner</dd><dt>Judged</dt>', 1),
            'false prose': lambda s: s.replace('carrying on as if you concur.', 'approved already.', 1),
            'a swapped picture source': lambda s: s.replace('<img ', '<picture><source srcset="data:image/png;base64,QUJD"><img ', 1).replace('one.</figcaption>', 'one.</figcaption>', 1),
            'a row on a paragraph': lambda s: s.replace('<div class="ask call"', '<p class="ask call"', 1),
        }
        for name, edit in edits.items():
            with self.subTest(edit=name):
                if name == 'a row on a paragraph':
                    with self.assertRaises(brief.Refusal):
                        brief.check(self.page_with(edit))
                    continue
                with self.assertRaisesRegex(brief.Refusal, 'differs from what the ledger renders|not shown|open calls missing'):
                    brief.check(self.page_with(edit))

    def test_a_stamp_on_a_page_edited_after_its_build_is_not_approval(self):
        keep = '<div class="grill"><div class="ask" id="q-data" data-brief-anchor="q-data"><h3>Keep all data</h3></div></div>'
        with patch.object(brief, 'utc_minute', lambda now=None: '2030-01-01T00:00Z'):
            page = self.page('plan', keep)
        self.stamp(page, concurs={'q-data': '2030-01-01T00:01Z'})  # after the build
        page.write_text(brief.read(page).replace('Keep all data', 'Delete all data'))  # then edited by hand
        meta = brief.island(brief.read(page), 'brief-meta')[1]
        meta['feedback_revision'] = None  # as a rebuild over retained notes leaves it, so only the time rule is left
        old, _ = brief.island(brief.read(page), 'brief-meta')
        page.write_text(brief.read(page).replace(old, '<script type="application/json" id="brief-meta">' + brief.encode(meta) + '</script>'))
        tree = brief.orient(page)
        self.assertEqual(tree['approved'], [])
        self.assertEqual([d['title'] for d in tree['restamp']], ['Delete all data'])

    def test_a_question_hidden_behind_ins_or_label_is_found(self):
        for wrapper in ('ins', 'label'):
            hidden = f'<div class="grill"><p class="ask" id="q-a" data-brief-anchor="q-a"><{wrapper}><b>First<div class="q"><b>Second</b></div></div>'
            with self.subTest(wrapper=wrapper), self.assertRaisesRegex(brief.Refusal, 'Second'):
                self.page('hidden-' + wrapper, hidden)

    def test_a_parent_showing_call_rows_without_a_ledger_is_unknown(self):
        parent = self.page('plan', brief.render_calls(self.ledger))  # shows a call, names no ledger
        empty = self.root / 'empty.calls.json'
        empty.write_text(json.dumps({'format': 1, 'kind': 'briefing-calls', 'calls': []}))
        child = self.page('closing', '', {'derives_from': ['plan.html'], 'calls': 'empty.calls.json'})
        settled = brief.orient(child)['settled']
        self.assertEqual(settled['state'], 'unknown')
        self.assertTrue(any('yet shows call rows' in why for why in settled['why']))
        self.assertTrue(parent.exists())

    def test_an_unchanged_rebuild_keeps_a_fresh_stamp_current(self):
        keep = '<div class="grill"><div class="ask" id="q-data" data-brief-anchor="q-data"><h3>Keep all data</h3></div></div>'
        changed = keep.replace('Keep all data', 'Keep most data')
        with patch.object(brief, 'utc_minute', lambda now=None: '2030-01-01T00:00Z'):
            page = self.page('plan', keep)
        self.stamp(page, concurs={'q-data': '2020-01-01T00:00Z'})
        with patch.object(brief, 'utc_minute', lambda now=None: '2030-01-01T00:10Z'):
            page = self.rebuild('plan', changed)  # wording changed: old stamps go stale
        self.stamp(page, concurs={'q-data': '2030-01-01T00:20Z'})  # stamped again, after that build
        with patch.object(brief, 'utc_minute', lambda now=None: '2030-01-01T00:30Z'):
            page = self.rebuild('plan', changed)  # nothing changed this time
        self.assertEqual(brief.island(brief.read(page), 'brief-meta')[1]['built_at'], '2030-01-01T00:10Z')
        self.assertEqual([d['anchor'] for d in brief.orient(page)['approved']], ['q-data'])

    def test_optional_fields_of_the_wrong_type_are_refused(self):
        good = brief.load_ledger(self.ledger)
        for field, value in (('context', {'x': 1}), ('undo', 12), ('door', 'sideways'), ('at', None)):
            bad = json.loads(json.dumps(good))
            bad['calls'][0][field] = value
            self.ledger.write_text(json.dumps(bad))
            with self.subTest(field=field), self.assertRaisesRegex(brief.Refusal, 'malformed'):
                brief.render_calls(self.ledger)

    def test_routine_calls_sort_last_even_behind_an_evidence_call_of_equal_weight(self):
        self.ledger.unlink()
        self.call('Routine first')
        self.call('With proof', evidence=[self.shot])
        section = brief.render_calls(self.ledger)
        self.assertEqual([d['anchor'] for d in brief.Decisions(section).decisions()], ['call-with-proof', 'call-routine-first'])
        self.assertIn('The last one was routine', section)
