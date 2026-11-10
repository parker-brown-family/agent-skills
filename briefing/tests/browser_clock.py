"""Exercise the real browser clock against a temporary original, never a human brief."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import brief
from review_server import ReviewServer

SOURCE = '''<!doctype html><html><head><title>Synthetic browser clock fixture</title><!--BRIEF:head-->
<style>section.pane{min-height:1100px}svg{display:block;width:100%;height:auto}</style></head><body>
<!--brief-content--><header class="top"><div class="wrap"><div class="opening" id="top" data-brief-anchor="top"><h1>Synthetic browser clock fixture</h1><p class="lede">Automated exposure, never a person's reading record.</p></div><nav class="sections"></nav></div></header>
<main class="wrap"><section class="pane"><h2 id="sec-one" data-brief-anchor="sec-one">One visible section</h2><p id="entry-one" data-brief-anchor="entry-one">The first section is tall enough to test scrolling.</p>
<figure id="fig-one" data-brief-anchor="fig-one"><span class="lbl">A test picture</span><svg viewBox="0 0 400 90" aria-label="Synthetic geometry"><rect x="10" y="10" width="380" height="70" fill="var(--bg2)"/><text x="30" y="50" fill="var(--fg)">Synthetic content</text></svg><figcaption>Geometry is measured independently from the heading.</figcaption></figure></section>
<section class="pane"><h2 id="sec-two" data-brief-anchor="sec-two">The next section</h2><p>This remains below the first viewport.</p></section>
<section class="pane"><h2 id="sec-three" data-brief-anchor="sec-three">The last section</h2><p>Another known target.</p></section></main><!--/brief-content--><!--BRIEF:notes--></body></html>'''

with tempfile.TemporaryDirectory(prefix='brief-clock-') as directory:
    work = Path(directory)
    source, page = work / 'clock.src.html', work / 'clock.html'
    source.write_text(SOURCE)
    brief.build(source, page, 'synthetic-browser-clock', 'engineering', no_wall=True)
    server = ReviewServer(page, brief)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        env = {**os.environ, 'BRIEF_REVIEW_URL': server.url, 'BRIEF_CLOCK_QA': '1',
               'BRIEF_QA_DIR': '/tmp/briefing-clock-qa'}
        result = subprocess.run(['node', str(ROOT / 'tests/browser.mjs'), str(page)], env=env, timeout=120)
        if result.returncode:
            raise SystemExit(result.returncode)
        record = brief.reading_support().read_record(page.read_text(), brief)
        assert record['sessions'] and any(t['visible_ms'] and t['visible_ms'] > 0 for s in record['sessions'] for t in s['targets'])
        assert brief.notes(page.read_text())[1]['sec-one'][0]['text'] == 'Browser clock test note.'
        assert not brief.check(page)['edited_since_build']
        print(json.dumps({'originalFileVerified': True, 'readingSessions': len(record['sessions']),
                          'noteReopened': True, 'sourceRevisionUnchanged': True}))
    finally:
        server.shutdown()
        server.server_close()
        worker.join(5)
