"""Real selected-file HTTP saves, preservation, conflicts and checkpoint merging."""
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import brief
import reading
from review_server import ReviewServer, LIMIT, persistent_server

SOURCE = '''<!doctype html><html><head><title>Synthetic save fixture</title><!--BRIEF:head--></head><body>
<!--brief-content--><header><h1 id="top" data-brief-anchor="top">Synthetic save fixture</h1></header>
<main><section><h2 id="sec-test" data-brief-anchor="sec-test">One counter</h2><p>Test values, not reader measurements.</p></section></main>
<!--/brief-content--><!--BRIEF:notes--></body></html>'''


class ReadingTests(unittest.TestCase):
    def test_note_mirror_uses_the_body_tag_not_the_instruction_comment(self):
        before = self.page.read_text()
        changed = reading.plan_note_edits(before, [{'op': 'add', 'anchor': 'sec-test',
            'note': {'text': 'A real note.', 'ts': '2026-11-10 00:00'}}], brief)
        self.assertIn('Paste immediately before the closing </body>. notes.js finds these by id.', changed)
        self.assertGreater(changed.index('<!--\nREADER NOTES —'), changed.index('id="report-reading"'))
        self.assertEqual(brief.content_revision(changed, 'test-reading', 'engineering'), self.revision)

    def test_portable_fixture_keeps_unknown_zero_and_both_hosts(self):
        record = json.loads((Path(__file__).parent / 'fixtures/reading/record.json').read_text())
        reading.validate_record(record)
        self.assertEqual([s['host'] for s in record['sessions']], ['browser', 'terminal-delight'])
        self.assertEqual(record['sessions'][0]['targets'][1]['visible_ms'], 0)
        self.assertIsNone(record['sessions'][1]['targets'][2]['visible_ms'])

    def test_cli_restart_keeps_origin_but_rotates_capability(self):
        first = persistent_server(self.page, brief)
        origin, url = first.origin, first.url
        first.server_close()
        second = persistent_server(self.page, brief)
        self.addCleanup(second.server_close)
        self.assertEqual(second.origin, origin)
        self.assertNotEqual(second.url, url)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {'XDG_STATE_HOME': str(self.root / 'state')})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.source, self.page = self.root / 'fixture.src.html', self.root / 'fixture.html'
        self.source.write_text(SOURCE)
        brief.build(self.source, self.page, 'test-reading', 'engineering', no_wall=True)
        self.revision = brief.inspect(self.page)[2]

    def session(self, name='session-one', milliseconds=12000):
        return {'session': name, 'document': 'test-reading', 'revision': self.revision,
                'host': 'browser', 'method': 1, 'gaps': [], 'targets': [
                    {'anchor': 'sec-test', 'title': 'One counter', 'kind': 'section',
                     'parent': None, 'visible_ms': milliseconds}]}

    def start(self):
        server = ReviewServer(self.page, brief)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        def finish():
            server.shutdown()
            server.server_close()
            thread.join(5)
        self.addCleanup(finish)
        return server

    def request(self, server, value=None, *, route=None, origin=None, host=None, raw=None, extra=None, edits=None):
        connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=10)
        headers = {'Host': host or server.origin.removeprefix('http://')}
        if value is None and raw is None:
            method, body = 'GET', None
            route = route or server.route
        else:
            method = 'POST'
            body = raw if raw is not None else json.dumps({'format': 1, 'reading': value, 'note_edits': edits or []})
            headers.update({'Origin': origin or server.origin, 'Content-Type': 'application/json'})
            route = route or server.route + '/save'
        headers.update(extra or {})
        try:
            connection.request(method, route, body, headers)
            result = connection.getresponse()
            content = result.read().decode('utf-8')
            return result.status, content
        finally:
            connection.close()

    def test_original_file_round_trip_preserves_authored_bytes_and_notes(self):
        before = self.page.read_text()
        empty, _ = brief.island(before, 'report-notes')
        note = '<script id="report-notes" data-format="1">' + brief.encode({'sec-test': [{'text': 'Keep this note.', 'ts': '2026-11-10 00:00'}]}) + '</script>'
        self.page.write_text(before.replace(empty, note))
        before = self.page.read_text()
        server = self.start()
        code, body = self.request(server, self.session())
        self.assertEqual(code, 200, body)
        self.assertEqual(json.loads(body)['state'], 'saved')
        after = self.page.read_text()
        old, _ = brief.island(before, 'report-reading')
        new, _ = brief.island(after, 'report-reading')
        self.assertEqual(before.replace(old, '<DATA>'), after.replace(new, '<DATA>'))
        self.assertEqual(reading.read_record(after, brief)['sessions'][0]['targets'][0]['visible_ms'], 12000)
        self.assertEqual(brief.feedback(self.page)['comments'][0]['text'], 'Keep this note.')
        code, html = self.request(server)
        self.assertEqual(code, 200)
        self.assertIn('12000', html)
        self.assertIn('window.BRIEF_REVIEW=', html)
        self.assertNotIn('window.BRIEF_REVIEW=', after)
        self.assertEqual(brief.inspect(self.page)[2], self.revision)

    def test_retry_and_out_of_order_checkpoint_do_not_add_time(self):
        server = self.start()
        for ms in (12000, 12000, 7000, 15000):
            code, data = self.request(server, self.session(milliseconds=ms))
            self.assertEqual(code, 200, data)
        saved = reading.read_record(self.page.read_text(), brief)
        self.assertEqual(saved['sessions'][0]['targets'][0]['visible_ms'], 15000)
        self.assertEqual(len(list((self.root / 'state').rglob('*.html'))), 2)

    def test_unknown_is_distinct_from_zero(self):
        unknown = self.session(milliseconds=None)
        saved = reading.merge_record({'format': 1, 'sessions': []}, unknown)
        self.assertIsNone(saved['sessions'][0]['targets'][0]['visible_ms'])
        saved = reading.merge_record(saved, self.session(milliseconds=0))
        self.assertEqual(saved['sessions'][0]['targets'][0]['visible_ms'], 0)
        saved = reading.merge_record(saved, unknown)
        self.assertEqual(saved['sessions'][0]['targets'][0]['visible_ms'], 0)

    def test_typed_notes_preserve_concurrent_entries_and_refresh_mirror(self):
        server = self.start()
        first = {'text': 'Keep </script> and <!-- this. -->', 'title': 'One counter', 'ts': '2026-11-10 01:00'}
        second = {'text': 'Another reader.', 'title': 'One counter', 'ts': '2026-11-10 01:01'}
        add = lambda n: {'op': 'add', 'anchor': 'sec-test', 'note': n}
        for name, entry in (('first', first), ('second', second), ('first', first)):
            code, body = self.request(server, self.session(name), edits=[add(entry)])
            self.assertEqual(code, 200, body)
        notes = brief.notes(self.page.read_text())[1]
        self.assertEqual(notes['sec-test'], [first, second])
        self.assertEqual(brief.inspect(self.page)[2], self.revision)
        self.assertIn('Another reader.', brief.MIRROR.search(self.page.read_text())[0])
        delete = {'op': 'delete', 'anchor': 'sec-test', 'note': first}
        self.assertEqual(self.request(server, self.session('first'), edits=[delete])[0], 200)
        self.assertEqual(brief.notes(self.page.read_text())[1]['sec-test'], [second])
        self.assertNotIn('Keep', brief.MIRROR.search(self.page.read_text())[0])

    def test_stale_concurrence_cannot_overwrite_another_reader(self):
        server = self.start()
        edit = {'op': 'concur', 'anchor': 'sec-test', 'before': None, 'value': '2026-11-10 01:00'}
        self.assertEqual(self.request(server, self.session(), edits=[edit])[0], 200)
        self.assertEqual(self.request(server, self.session(), edits=[edit])[0], 200)
        edit['value'] = '2026-11-10 01:02'
        before = self.page.read_bytes()
        self.assertEqual(self.request(server, self.session('different'), edits=[edit])[0], 409)
        self.assertEqual(self.page.read_bytes(), before)

    def test_gap_checkpoints_merge_cumulative_elapsed_time(self):
        first = self.session()
        first['gaps'] = [{'sequence': 1, 'reason': 'activity_unknown', 'elapsed_ms': 1000}]
        saved = reading.merge_record({'format': 1, 'sessions': []}, first)
        first['gaps'][0]['elapsed_ms'] = 2000
        saved = reading.merge_record(saved, first)
        self.assertEqual(saved['sessions'][0]['gaps'][0]['elapsed_ms'], 2000)

    def test_invalid_time_identity_and_target_cannot_write(self):
        server = self.start()
        original = self.page.read_bytes()
        mutations = [lambda s: s.update(document='different'), lambda s: s.update(revision='sha256:' + '1' * 64),
                     lambda s: s['targets'][0].update(anchor='missing'), lambda s: s['targets'][0].update(visible_ms=True),
                     lambda s: s['targets'][0].update(visible_ms=-1), lambda s: s['targets'][0].update(visible_ms=1.5),
                     lambda s: s['targets'][0].update(visible_ms=2**53)]
        for mutate in mutations:
            value = self.session()
            mutate(value)
            code, data = self.request(server, value)
            self.assertEqual(code, 409, data)
            self.assertEqual(self.page.read_bytes(), original)

    def test_identity_of_existing_session_cannot_change(self):
        saved = reading.merge_record({'format': 1, 'sessions': []}, self.session())
        other = self.session()
        other['host'] = 'terminal-delight'
        with self.assertRaises(reading.ReadingError):
            reading.merge_record(saved, other)

    def test_corrupt_record_cannot_pass_check_or_rebuild(self):
        html = self.page.read_text()
        empty, _ = brief.island(html, 'report-reading')
        corrupt = '<script id="report-reading" data-format="1">{"format":1,"sessions":[{}]}</script>'
        self.page.write_text(html.replace(empty, corrupt))
        with self.assertRaises(ValueError):
            brief.check(self.page)
        with self.assertRaises(ValueError):
            brief.build(self.source, self.page, 'test-reading', 'engineering', no_wall=True)

    def test_build_retains_nonposix_compare_before_replace_fallback(self):
        with patch.object(brief, 'fcntl', None):
            brief.build(self.source, self.page, 'test-reading', 'engineering', no_wall=True)
        self.assertEqual(brief.inspect(self.page)[2], self.revision)

    def test_reader_ui_is_excluded_without_hiding_authored_content(self):
        a = SOURCE.replace('</main>', '<output data-reader-ui>0:01</output><p>Authored claim.</p></main>')
        b = a.replace('>0:01<', '>0:42<')
        self.assertEqual(brief.content_revision(a, 'test-reading', 'engineering'), brief.content_revision(b, 'test-reading', 'engineering'))
        c = b.replace('Authored claim.', 'Changed claim.')
        self.assertNotEqual(brief.content_revision(a, 'test-reading', 'engineering'), brief.content_revision(c, 'test-reading', 'engineering'))

    def test_wrong_token_origin_host_and_path_cannot_write(self):
        server = self.start()
        original = self.page.read_bytes()
        for options, expected in [({'route': '/review/wrong/save'}, 404),
                                  ({'route': server.route + '/../../elsewhere'}, 404),
                                  ({'origin': 'https://elsewhere.example'}, 403),
                                  ({'host': 'elsewhere.example'}, 403)]:
            code, body = self.request(server, self.session(), **options)
            self.assertEqual(code, expected, body)
            self.assertEqual(self.page.read_bytes(), original)

    def test_malformed_duplicate_nonfinite_and_unsupported_requests_cannot_write(self):
        server = self.start()
        original = self.page.read_bytes()
        for raw in ('{', '{"format":1,"format":1}', '{"number":NaN}',
                    json.dumps({'format': 1, 'reading': self.session(), 'note_edits': [{'text': 'must not be dropped'}]})):
            code, body = self.request(server, raw=raw)
            self.assertEqual(code, 409, body)
        code, body = self.request(server, self.session(), extra={'Content-Length': str(LIMIT + 1)})
        self.assertEqual(code, 413, body)
        code, body = self.request(server, self.session(), extra={'Content-Type': 'text/plain'})
        self.assertEqual(code, 415, body)
        self.assertEqual(self.page.read_bytes(), original)

    def test_external_content_change_refuses_stale_save(self):
        server = self.start()
        self.page.write_text(self.page.read_text().replace('>One counter<', '>Changed words<'))
        changed = self.page.read_bytes()
        code, body = self.request(server, self.session())
        self.assertEqual(code, 409, body)
        self.assertEqual(self.page.read_bytes(), changed)

    def test_write_failure_stays_pending(self):
        server = self.start()
        original = self.page.read_bytes()
        with patch.object(brief, 'atomic', side_effect=OSError('disk failure')):
            code, body = self.request(server, self.session())
        self.assertEqual(code, 409)
        self.assertEqual(json.loads(body)['state'], 'pending')
        self.assertEqual(self.page.read_bytes(), original)

    def test_two_servers_and_a_rebuild_preserve_both_sessions(self):
        one, two = self.start(), self.start()
        def save(server, name):
            code, body = self.request(server, self.session(name))
            self.assertEqual(code, 200, body)
        with ThreadPoolExecutor(max_workers=3) as workers:
            futures = [workers.submit(save, one, 'one'), workers.submit(save, two, 'two'),
                       workers.submit(brief.build, self.source, self.page, 'test-reading', 'engineering', True)]
            for future in futures:
                future.result()
        record = reading.read_record(self.page.read_text(), brief)
        self.assertEqual({s['session'] for s in record['sessions']}, {'one', 'two'})

    def test_changed_revision_retains_history_without_reassigning_it(self):
        server = self.start()
        self.assertEqual(self.request(server, self.session())[0], 200)
        self.source.write_text(SOURCE.replace('>One counter<', '>New section<'))
        brief.build(self.source, self.page, 'test-reading', 'engineering', no_wall=True)
        self.assertNotEqual(brief.inspect(self.page)[2], self.revision)
        self.assertEqual(reading.read_record(self.page.read_text(), brief)['sessions'][0]['revision'], self.revision)
        self.assertEqual(self.request(server, self.session())[0], 409)

    def test_unsafe_file_and_lock_are_refused(self):
        link = self.root / 'link.html'
        link.symlink_to(self.page)
        with self.assertRaises(reading.ReadingError):
            ReviewServer(link, brief)
        hard = self.root / 'hard.html'
        os.link(self.page, hard)
        with self.assertRaises(reading.ReadingError):
            ReviewServer(hard, brief)
        hard.unlink()
        self.page.chmod(0o444)
        with self.assertRaises(reading.ReadingError):
            ReviewServer(self.page, brief)
        lock = self.page.with_name('.' + self.page.name + '.brief-review.lock')
        lock.chmod(0o644)
        with self.assertRaises(reading.ReadingError):
            with reading.review_lock(self.page):
                self.fail('unsafe lock acquired')


if __name__ == '__main__':
    unittest.main()
