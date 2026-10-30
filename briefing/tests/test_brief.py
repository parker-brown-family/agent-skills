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
