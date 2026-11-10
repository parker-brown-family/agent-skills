"""Reading the saved visible time back: what was scrolled past, how long a brief is, and where across briefs."""
import contextlib
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import brief
import reading

HERE = Path(__file__).resolve().parents[1]
LONG = ' '.join(['word'] * 160)
SOURCE = f'''<!doctype html><html><head><title>Attention fixture</title><!--BRIEF:head--></head><body>
<!--brief-content--><header><div class="opening" id="top" data-brief-anchor="top"><h1>Attention fixture</h1>
<p class="lede">Synthetic times, not a person's reading.</p></div></header>
<main>
<section><h2 id="sec-short" data-brief-anchor="sec-short">Short</h2><p>Four words of prose.</p>
<figure id="fig-one" data-brief-anchor="fig-one"><svg viewBox="0 0 10 10" aria-label="x"><text>ten figure words here one two three four five six</text></svg>
<figcaption>Caption.</figcaption></figure></section>
<section><h2 id="sec-long" data-brief-anchor="sec-long">Long</h2><p>{LONG}</p></section>
<section><h2 id="sec-seen-none" data-brief-anchor="sec-seen-none">Never on screen</h2><p>Three more words.</p></section>
<section><h2 id="sec-unknown" data-brief-anchor="sec-unknown">No record</h2><p>Unknown is not zero.</p></section>
</main><!--/brief-content--><!--BRIEF:notes--></body></html>'''


class AttentionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.source, self.page = root / 'a.src.html', root / 'a.html'
        self.source.write_text(SOURCE)
        brief.build(self.source, self.page, 'test-attention', 'engineering', no_wall=True)

    def tearDown(self):
        self.tmp.cleanup()

    def save(self, times, name='session-one', revision=None):
        text = self.page.read_text()
        _, meta = brief.island(text, 'brief-meta')
        session = {'session': name, 'document': meta['id'], 'revision': revision or meta['revision'],
                   'host': 'browser', 'method': 1, 'gaps': [], 'targets': [
                       {'anchor': a, 'title': a, 'kind': 'figure' if a.startswith('fig') else 'opening' if a == 'top' else 'section',
                        'parent': 'sec-short' if a == 'fig-one' else None, 'visible_ms': ms} for a, ms in times.items()]}
        if revision:  # an earlier version's session is kept in the record, never written through the current page
            _, record = brief.island(text, 'report-reading')
            record['sessions'].append(session)
            old, _ = brief.island(text, 'report-reading')
            text = text.replace(old, '<script type="application/json" id="report-reading" data-format="1">' + brief.encode(record) + '</script>')
        else:
            text, _ = reading.plan_reading_write(text, session, brief.reading_api())
        self.page.write_text(text)

    def report(self):
        return {r['anchor']: r for r in reading.attention(self.page.read_text(), brief.reading_api())['passages']}

    def test_words_follow_the_measured_box(self):
        found = reading.Passages(self.page.read_text()).found
        self.assertEqual(found['sec-short']['words'], 1 + 4 + 10 + 1)  # heading, prose, figure, caption
        self.assertEqual(found['sec-short']['prose_words'], 5)          # the figure is a picture, not prose
        self.assertEqual(found['fig-one']['words'], 11)
        self.assertEqual(found['sec-long']['prose_words'], 161)
        self.assertEqual(found['top']['kind'], 'opening')
        self.assertEqual(found['sec-unknown']['title'], 'No record')

    def test_verdicts_keep_unknown_apart_from_zero(self):
        self.save({'top': 9000, 'sec-short': 6000, 'fig-one': 1000, 'sec-long': 3000, 'sec-seen-none': 0})
        rows = self.report()
        self.assertEqual(rows['sec-short']['verdict'], 'had_time')   # 16 words needs the 4 s floor; 6 s is room
        self.assertEqual(rows['fig-one']['verdict'], 'passed')       # 1 s of a 4 s floor
        self.assertEqual(rows['sec-long']['verdict'], 'passed')      # 3 s of ~42 s
        self.assertEqual(rows['sec-seen-none']['verdict'], 'unseen')
        self.assertEqual(rows['sec-unknown']['verdict'], 'unmeasured')
        self.assertIsNone(rows['sec-unknown']['visible_ms'])

    def test_sessions_sum_and_earlier_versions_are_not_counted(self):
        self.save({'sec-long': 10000}, 'session-one')
        self.save({'sec-long': 10000}, 'session-two')
        self.save({'sec-long': 999999}, 'session-old', revision='sha256:' + '0' * 64)
        report = reading.attention(self.page.read_text(), brief.reading_api())
        self.assertEqual((report['sessions'], report['earlier_revision_sessions']), (2, 1))
        row = next(r for r in report['passages'] if r['anchor'] == 'sec-long')
        self.assertEqual((row['visible_ms'], row['verdict']), (20000, 'had_time'))

    def test_no_reading_says_unknown_and_draws_no_conclusion(self):
        text = reading.attention_text(reading.attention(self.page.read_text(), brief.reading_api()))
        self.assertIn('Unknown, not zero', text)
        self.assertNotIn('PASSED', text)

    def test_text_names_both_explanations_for_a_passed_passage(self):
        self.save({'sec-long': 1000})
        text = reading.attention_text(reading.attention(self.page.read_text(), brief.reading_api()))
        self.assertIn('not needed here, or needed and missed', text)
        self.assertRegex(text, r'\[sec-long\] section · .* 0:01 of ~0:42')

    def test_across_briefs_tallies_by_kind_and_place(self):
        self.save({'sec-short': 1000, 'sec-long': 1000, 'sec-seen-none': 0, 'fig-one': 9000})
        reports = [reading.attention(self.page.read_text(), brief.reading_api())]
        text, tally = reading.attention_across(reports)
        self.assertEqual(tally['section'], (3, 3))
        self.assertEqual(tally['figure'], (1, 0))
        self.assertIn('section · first', tally)
        self.assertIn('1 with reading time', text)

    def test_check_reports_brevity_without_refusing(self):
        result = brief.check(self.page)
        self.assertEqual(result['long_sections'], [{'anchor': 'sec-long', 'prose_words': 161}])
        self.assertGreater(result['reading_minutes'], 0.7)

    def test_cli_refuses_a_source_and_prints_json(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sys.argv = ['brief.py', 'attention', '--json', str(self.page)]
            self.assertEqual(brief.main(), 0)
        self.assertEqual(json.loads(out.getvalue())['document'], 'test-attention')
        sys.argv = ['brief.py', 'attention', str(self.source)]
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertNotEqual(brief.main(), 0)
        self.assertIn('not a source', err.getvalue())

    def test_browser_and_python_share_one_estimate(self):
        js = (HERE / 'assets/reading.js').read_text()
        found = dict(re.findall(r'(wordsPerMinute|floorMs|passedShare):([0-9.]+)', js))
        self.assertEqual(float(found['wordsPerMinute']), reading.WORDS_PER_MINUTE)
        self.assertEqual(float(found['floorMs']), reading.FLOOR_MS)
        self.assertEqual(float(found['passedShare']), reading.PASSED_SHARE)


if __name__ == '__main__':
    unittest.main()
