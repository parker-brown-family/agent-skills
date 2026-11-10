"""Real Python HTTP writer / Rust writer race on one temporary original HTML.

Run with --worker pointing to the compiled reading_record integration test.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import brief
import reading
from review_server import ReviewServer
from test_reading import SOURCE

parser = argparse.ArgumentParser()
parser.add_argument('--worker', type=Path, required=True)
args = parser.parse_args()
with tempfile.TemporaryDirectory(prefix='brief-native-race-') as directory:
    root = Path(directory)
    os.environ['XDG_STATE_HOME'] = str(root / 'state')
    source, page = root / 'race.src.html', root / 'race.html'
    source.write_text(SOURCE)
    brief.build(source, page, 'test-reading', 'engineering', no_wall=True)
    before = page.read_text()
    revision = brief.inspect(page)[2]

    def session(name, host):
        return {'session': name, 'document': 'test-reading', 'revision': revision,
                'host': host, 'method': 1, 'gaps': [], 'targets': [
                    {'anchor': 'sec-test', 'title': 'One counter', 'kind': 'section',
                     'parent': None, 'visible_ms': 1000}]}

    native = [session('native-' + str(i), 'terminal-delight') for i in range(16)]
    input_path = root / 'worker.json'
    input_path.write_text(json.dumps({'path': str(page), 'sessions': native + native}))
    server = ReviewServer(page, brief)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        def browser_writer():
            for i in range(16):
                connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=15)
                body = {'format': 1, 'reading': session('browser-' + str(i), 'browser'),
                        'note_edits': [{'op': 'add', 'anchor': 'sec-test', 'note': {
                            'text': 'Concurrent note ' + str(i), 'ts': '2026-11-10 00:00'}}]}
                connection.request('POST', server.route + '/save', json.dumps(body),
                                   {'Host': server.origin.removeprefix('http://'), 'Origin': server.origin,
                                    'Content-Type': 'application/json'})
                response = connection.getresponse()
                result = response.read()
                assert response.status == 200, result
                connection.close()

        with ThreadPoolExecutor(max_workers=2) as pool:
            browser = pool.submit(browser_writer)
            process = subprocess.run([str(args.worker.resolve()), '--exact', 'checkpoint_worker'],
                                     env={**os.environ, 'TD_READING_TEST_INPUT': str(input_path)},
                                     capture_output=True, timeout=60)
            assert process.returncode == 0, process.stdout + process.stderr
            browser.result()
        after = page.read_text()
        record = reading.read_record(after, brief)
        assert len(record['sessions']) == 32
        assert all(s['targets'][0]['visible_ms'] == 1000 for s in record['sessions'])
        assert len(brief.notes(after)[1]['sec-test']) == 16
        assert brief.content_revision(after, 'test-reading', 'engineering') == revision
        for name in ('report-reading', 'report-notes', 'report-concurs'):
            old, _ = brief.island(before, name)
            new, _ = brief.island(after, name)
            before, after = before.replace(old, '<DATA>'), after.replace(new, '<DATA>')
        # The notes mirror is explicitly regenerated; the author's content is unchanged.
        assert not brief.check(page)['edited_since_build']
        print(json.dumps({'passed': True, 'separateWriterProcesses': True, 'sessionsPreserved': 32,
                          'notesPreserved': 16, 'duplicateCheckpointsDoNotAddTime': True,
                          'authoredRevisionUnchanged': True}))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(5)
