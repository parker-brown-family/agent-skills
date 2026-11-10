"""Real user-service recovery and browser saving, on a temporary synthetic brief."""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import brief
from review_server import review, session_file

source = next(ast.literal_eval(n.value) for n in ast.parse((ROOT / 'tests/browser_clock.py').read_text()).body
              if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SOURCE' for t in n.targets))
with tempfile.TemporaryDirectory(prefix='brief-launcher-proof-') as directory:
    page, src = Path(directory) / 'clock.html', Path(directory) / 'clock.src.html'
    src.write_text(source)
    brief.build(src, page, 'synthetic-launcher', 'engineering', no_wall=True)
    unit = 'brief-review-' + session_file(page).stem[:24] + '.service'
    try:
        first = review(page, api=brief, open_browser=False)
        assert review(page, api=brief, open_browser=False) == first
        subprocess.run(['systemctl', '--user', 'stop', unit], check=True)
        restarted = review(page, api=brief, open_browser=False)
        assert first['url'].split('/review/')[0] == restarted['url'].split('/review/')[0]
        assert first['url'] != restarted['url']
        src.write_text(source.replace('The last section', 'A renamed last section'))
        brief.build(src, page, 'synthetic-launcher', 'engineering', no_wall=True)
        rebuilt = review(page, api=brief, open_browser=False)
        assert rebuilt['revision'] != restarted['revision'] and rebuilt['url'] != restarted['url']
        env = {**os.environ, 'BRIEF_REVIEW_URL': rebuilt['url'], 'BRIEF_CLOCK_QA': '1',
               'BRIEF_QA_DIR': '/tmp/brief-launcher-qa'}
        subprocess.run(['node', str(ROOT / 'tests/browser.mjs'), str(page)], env=env, check=True, timeout=120)
        record = brief.reading_support().read_record(page.read_text(), brief)
        assert any(t['visible_ms'] and t['visible_ms'] > 0 for s in record['sessions'] for t in s['targets'])
        assert brief.notes(page.read_text())[1]['sec-one'][0]['text'] == 'Browser clock test note.'
        assert not brief.check(page)['edited_since_build']
        print(json.dumps({'managedServiceStarts': True, 'liveConnectionReused': True,
                          'stoppedServiceRecovers': True, 'browserOriginPreserved': True,
                          'changedRevisionRestarts': True, 'originalNotesAndTimeVerified': True}))
    finally:
        subprocess.run(['systemctl', '--user', 'stop', unit], check=False)
