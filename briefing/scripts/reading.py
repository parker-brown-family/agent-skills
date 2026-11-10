"""Portable visible-time records and the shared review-file lock. Standard library only."""
from contextlib import contextmanager
from copy import deepcopy
try:
    import fcntl
except ImportError:
    fcntl = None
import os
from pathlib import Path
from html.parser import HTMLParser
import re
import stat

MAX_INTEGER = 2**53 - 1
MAX_SESSIONS = 10000
MAX_TARGETS = 2000
MAX_GAPS = 10000
ID = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]{0,127}$')
REVISION = re.compile(r'^sha256:[0-9a-f]{64}$')


class ReadingError(ValueError):
    pass


def integer(value):
    return type(value) is int and 0 <= value <= MAX_INTEGER


def identifier(value):
    return isinstance(value, str) and bool(ID.fullmatch(value))


def validate_session(value, document=None, revision=None):
    if not isinstance(value, dict) or set(value) != {
            'session', 'document', 'revision', 'host', 'method', 'targets', 'gaps'}:
        raise ReadingError('reading session: unexpected or missing fields')
    if not identifier(value['session']) or not identifier(value['document']):
        raise ReadingError('reading session: invalid identity')
    if not isinstance(value['revision'], str) or not REVISION.fullmatch(value['revision']):
        raise ReadingError('reading session: invalid content revision')
    if document is not None and value['document'] != document:
        raise ReadingError('reading session belongs to another document')
    if revision is not None and value['revision'] != revision:
        raise ReadingError('content changed; reopen the document before saving')
    if value['host'] not in ('browser', 'terminal-delight') or type(value['method']) is not int or value['method'] != 1:
        raise ReadingError('reading session: unsupported host or method')
    targets, gaps = value['targets'], value['gaps']
    if not isinstance(targets, list) or len(targets) > MAX_TARGETS:
        raise ReadingError('reading session: invalid target list')
    ids = set()
    for target in targets:
        if not isinstance(target, dict) or set(target) != {'anchor', 'title', 'kind', 'parent', 'visible_ms'}:
            raise ReadingError('reading target: unexpected or missing fields')
        anchor = target['anchor']
        if not identifier(anchor) or anchor in ids:
            raise ReadingError('reading target: duplicate or invalid anchor')
        ids.add(anchor)
        if not isinstance(target['title'], str) or len(target['title']) > 500:
            raise ReadingError('reading target: invalid title')
        if target['kind'] not in ('opening', 'section', 'figure', 'entry'):
            raise ReadingError('reading target: unsupported kind')
        if target['parent'] is not None and (not identifier(target['parent']) or target['parent'] == anchor):
            raise ReadingError('reading target: invalid parent')
        if target['visible_ms'] is not None and not integer(target['visible_ms']):
            raise ReadingError('reading target: invalid time')
    for target in targets:
        chain = set()
        parent = target['parent']
        parents = {t['anchor']: t['parent'] for t in targets}
        while parent is not None:
            if parent not in ids or parent in chain:
                raise ReadingError('reading target: missing or cyclic parent')
            chain.add(parent)
            parent = parents[parent]
    if not isinstance(gaps, list) or len(gaps) > MAX_GAPS:
        raise ReadingError('reading session: invalid observation gaps')
    sequences = set()
    for gap in gaps:
        if not isinstance(gap, dict) or set(gap) != {'sequence', 'reason', 'elapsed_ms'}:
            raise ReadingError('reading gap: unexpected or missing fields')
        if not integer(gap['sequence']) or gap['sequence'] in sequences or not integer(gap['elapsed_ms']):
            raise ReadingError('reading gap: invalid or duplicate sequence')
        sequences.add(gap['sequence'])
        if gap['reason'] not in ('clock_gap', 'activity_unknown'):
            raise ReadingError('reading gap: invalid reason')
    return deepcopy(value)


def validate_record(record):
    if not isinstance(record, dict) or set(record) != {'format', 'sessions'} or type(record['format']) is not int or record['format'] != 1:
        raise ReadingError('reading record: unsupported format')
    if not isinstance(record['sessions'], list) or len(record['sessions']) > MAX_SESSIONS:
        raise ReadingError('reading record: invalid sessions')
    seen = set()
    for session in record['sessions']:
        validate_session(session)
        if session['session'] in seen:
            raise ReadingError('reading record: duplicate session')
        seen.add(session['session'])
    return record


def merge_record(saved, incoming):
    validate_record(saved)
    incoming = validate_session(incoming)
    out = deepcopy(saved)
    old = next((s for s in out['sessions'] if s['session'] == incoming['session']), None)
    if old is None:
        if len(out['sessions']) >= MAX_SESSIONS:
            raise ReadingError('reading record is full; preserve it and start another document')
        out['sessions'].append(incoming)
        return out
    for key in ('document', 'revision', 'host', 'method'):
        if old[key] != incoming[key]:
            raise ReadingError('reading session identity changed')
    current = {t['anchor']: t for t in old['targets']}
    for target in incoming['targets']:
        prior = current.get(target['anchor'])
        if prior is None:
            old['targets'].append(target)
            continue
        if any(prior[k] != target[k] for k in ('title', 'kind', 'parent')):
            raise ReadingError('reading target identity changed')
        before, after = prior['visible_ms'], target['visible_ms']
        if after is not None:
            prior['visible_ms'] = after if before is None else max(before, after)
    gaps = {g['sequence']: g for g in old['gaps']}
    for gap in incoming['gaps']:
        if gap['sequence'] in gaps:
            prior = gaps[gap['sequence']]
            if prior['reason'] != gap['reason']:
                raise ReadingError('reading gap identity changed')
            prior['elapsed_ms'] = max(prior['elapsed_ms'], gap['elapsed_ms'])
        else:
            old['gaps'].append(gap)
    validate_record(out)
    return out


def read_record(text, api):
    blocks = [b for b in api.Scripts(text).blocks if b[0].get('id') == 'report-reading']
    if not blocks:
        return {'format': 1, 'sessions': []}
    record = validate_record(api.island(text, 'report-reading')[1])
    _, meta = api.island(text, 'brief-meta')
    if any(s['document'] != meta['id'] for s in record['sessions']):
        raise ReadingError('reading record contains another document')
    return record


def plan_reading_write(text, incoming, api):
    _, meta = api.island(text, 'brief-meta')
    actual = api.content_revision(text, meta['id'], meta['purpose'])
    if actual != meta['revision']:
        raise ReadingError('document was edited after build; rebuild before saving')
    incoming = validate_session(incoming, meta['id'], actual)
    anchors = set(api.Page(text).targets)
    if any(t['anchor'] not in anchors for t in incoming['targets']):
        raise ReadingError('reading target does not exist in this document')
    saved = read_record(text, api)
    merged = merge_record(saved, incoming)
    if merged == saved:
        return text, next(s for s in saved['sessions'] if s['session'] == incoming['session'])
    old, _ = api.island(text, 'report-reading')
    block = '<script type="application/json" id="report-reading" data-format="1">' + api.encode(merged) + '</script>'
    changed = text.replace(old, block, 1)
    # Only the data island can move; source, scripts and notes stay byte-for-byte.
    if api.content_revision(changed, meta['id'], meta['purpose']) != actual:
        raise ReadingError('reading write changed authored content')
    return changed, next(s for s in merged['sessions'] if s['session'] == incoming['session'])


def checked_file(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ReadingError('review target must be an ordinary file, with no symlink or hardlink')
    if info.st_uid != os.getuid() or not info.st_mode & stat.S_IWUSR:
        raise ReadingError('review target must be owned and writable by this user')
    return info


def plan_note_edits(text, edits, api):
    """Apply exact add/delete operations to fresh islands; preserve concurrent entries."""
    if not isinstance(edits, list) or len(edits) > MAX_TARGETS:
        raise ReadingError('invalid note edit list')
    if not edits:
        return text
    notes_block, notes, concurs_block, concurs = api.notes(text)
    notes, concurs = deepcopy(notes), deepcopy(concurs)
    anchors = set(api.Page(text).targets)
    for edit in edits:
        if not isinstance(edit, dict) or not identifier(edit.get('anchor')):
            raise ReadingError('invalid note edit anchor')
        anchor, operation = edit['anchor'], edit.get('op')
        if operation in ('add', 'delete'):
            if set(edit) != {'op', 'anchor', 'note'}:
                raise ReadingError('invalid note operation')
            note = edit['note']
            if (not isinstance(note, dict) or not set(note) <= {'text', 'title', 'ts'} or
                    not isinstance(note.get('text'), str) or len(note['text']) > 100000 or
                    any(not isinstance(note.get(k, ''), str) for k in ('title', 'ts')) or
                    len(note.get('title', '')) > 500 or len(note.get('ts', '')) > 64):
                raise ReadingError('invalid note entry')
            if operation == 'add':
                if anchor not in anchors:
                    raise ReadingError('new note target is missing')
                if note not in notes.setdefault(anchor, []):
                    notes[anchor].append(note)
            else:
                notes[anchor] = [n for n in notes.get(anchor, []) if n != note]
                if not notes[anchor]:
                    notes.pop(anchor, None)
        elif operation == 'concur':
            if set(edit) != {'op', 'anchor', 'before', 'value'} or anchor not in anchors:
                raise ReadingError('invalid concurrence edit')
            if any(v is not None and (not isinstance(v, str) or len(v) > 64) for v in (edit['before'], edit['value'])):
                raise ReadingError('invalid concurrence value')
            if concurs.get(anchor) not in (edit['before'], edit['value']):
                raise ReadingError('concurrence changed in another reader; reopen before replacing it')
            if edit['value'] is None:
                concurs.pop(anchor, None)
            else:
                concurs[anchor] = edit['value']
        else:
            raise ReadingError('unsupported note edit')
    if notes == api.notes(text)[1] and concurs == api.notes(text)[3]:
        return text
    from datetime import datetime, timezone
    rev = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    for name, old, value in (('report-notes', notes_block, notes), ('report-concurs', concurs_block, concurs)):
        block = '<script type="application/json" id="' + name + '" data-format="1" data-rev="' + rev + '">' + api.encode(value) + '</script>'
        text = text.replace(old, block, 1)
    _, meta = api.island(text, 'brief-meta')
    lines = ['NOTES — ' + meta['id'] + '-' + meta['revision'][7:19],
             str(sum(len(n) for n in notes.values())) + ' notes on ' + str(len(notes)) + ' elements · ' + str(len(concurs)) + ' concur.',
             'Each [anchor] is an element id in that file — search it to find the passage.', '']
    for anchor in dict.fromkeys(list(notes) + list(concurs)):
        entries = notes.get(anchor, [])
        title = next((n.get('title', anchor) for n in entries), anchor)
        lines.append('[' + anchor + '] ' + title + ('  ✓ concur' if anchor in concurs else ''))
        lines.extend('  · ' + ' '.join(n['text'].splitlines()) for n in entries)
        lines.append('')
    mirror = '<!--\nREADER NOTES —\n' + '\n'.join(lines).replace('--!>', '--! >').replace('-->', '-- >') + '\n-->'
    matches = list(api.MIRROR.finditer(text))
    if matches:
        last = matches[-1]
        text = text[:last.start()] + mirror + text[last.end():]
    else:
        class BodyEnd(HTMLParser):
            CDATA_CONTENT_ELEMENTS = ('script', 'style', 'textarea', 'title')

            def handle_endtag(self, tag):
                if tag == 'body':
                    line, column = self.getpos()
                    self.at = sum(len(s) for s in text.splitlines(keepends=True)[:line - 1]) + column

        parser = BodyEnd()
        parser.at = None
        parser.feed(text)
        if parser.at is None:
            raise ReadingError('document has no closing body for its reader-note mirror')
        text = text[:parser.at] + mirror + text[parser.at:]
    api.notes(text)
    return text


@contextmanager
def review_lock(path):
    if fcntl is None or not hasattr(os, 'O_NOFOLLOW'):
        raise ReadingError('original-file review saving needs POSIX file locks')
    path = Path(os.path.abspath(path))
    lock = path.with_name('.' + path.name + '.brief-review.lock')
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
            raise ReadingError('unsafe review lock file')
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


# ---- Reading the record back: which passages were on screen too briefly to have been read ----
#
# Visible time can only prove a negative. A passage on screen for less time than reading it takes was
# not read; one on screen long enough may or may not have been. So the verdict names the passages a
# reader scrolled past, and leaves the reason (not needed here, or needed and missed) to the writer.
# reading.js carries the same three numbers for the Copy map; tests/test_reading.py keeps them equal.
WORDS_PER_MINUTE = 230   # an adult reading ordinary prose on screen; an estimate, stated as one
FLOOR_MS = 4000          # even a heading-sized passage takes a few seconds to take in
PASSED_SHARE = 0.4       # on screen for under 40% of its reading time = scrolled past
LONG_SECTION_WORDS = 150 # prose words in one section (figures excluded) before check calls it long
VOID_TAGS = set('area base br col embed hr img input link meta param source track wbr'.split())
SKIPPED_SUBTREES = {'script', 'style', 'template', 'nav', 'dialog', 'noscript'}


class Passages(HTMLParser):
    """Words in every anchored passage of a built brief, counted the way reading.js measures its box:
    a section heading's passage is its whole enclosing <section>; everything else is its own element."""

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.stack, self.found, self.skip = [], {}, 0
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag in VOID_TAGS:
            return
        attrs = {k: v or '' for k, v in attrs}
        classes = attrs.get('class', '').split()
        skip = (tag in SKIPPED_SUBTREES or 'data-reader-ui' in attrs or attrs.get('id') == 'last-time'
                or 'last-time-strip' in classes)
        frame = {'tag': tag, 'skip': skip, 'anchor': None, 'section': tag == 'section', 'words': 0,
                 'prose': 0, 'heading': None, 'figure': tag == 'figure', 'text': ''}
        if not self.skip and not skip and attrs.get('data-brief-anchor'):
            anchor = attrs['data-brief-anchor']
            kind = ('opening' if tag == 'h1' or {'opening', 'lede'} & set(classes) else 'section' if tag == 'h2'
                    else 'figure' if tag == 'figure' else 'entry')
            if anchor not in self.found:
                frame['anchor'] = anchor
                self.found[anchor] = {'anchor': anchor, 'kind': kind, 'words': 0, 'prose_words': None,
                                      'order': len(self.found), 'title': ''}
                if kind == 'section':
                    box = next((f for f in reversed(self.stack) if f['section']), None)
                    if box is not None and box['heading'] is None:
                        box['heading'] = anchor
        self.skip += skip
        self.stack.append(frame)

    def handle_endtag(self, tag):
        if not any(f['tag'] == tag for f in self.stack):
            return
        while self.stack:
            frame = self.stack.pop()
            self.skip -= frame['skip']
            if frame['anchor']:
                self.found[frame['anchor']].update(words=frame['words'], title=' '.join(frame['text'].split())[:80])
            if frame['heading']:
                self.found[frame['heading']].update(words=frame['words'], prose_words=frame['prose'])
            if frame['tag'] == tag:
                break

    def handle_data(self, data):
        if self.skip:
            return
        words = len(data.split())
        if not words:
            return
        in_figure = any(f['figure'] for f in self.stack)
        for frame in self.stack:
            frame['words'] += words
            if frame['anchor'] and len(frame['text']) < 80:
                frame['text'] += ' ' + data
            if not in_figure:
                frame['prose'] += words


def reading_ms(words):
    return max(FLOOR_MS, round(words * 60000 / WORDS_PER_MINUTE))


def clock(ms):
    seconds = round(ms / 1000)
    return f'{seconds // 60}:{seconds % 60:02d}'


def brevity(text):
    """Estimated reading time for the whole brief, and the sections whose prose runs long."""
    passages = Passages(text).found
    sections = [p for p in passages.values() if p['kind'] == 'section']
    opening = sum(p['words'] for p in passages.values() if p['kind'] == 'opening')
    total = opening + sum(p['words'] for p in sections)
    long = [{'anchor': p['anchor'], 'prose_words': p['prose_words']} for p in sections
            if (p['prose_words'] or 0) > LONG_SECTION_WORDS]
    return {'reading_minutes': round(total / WORDS_PER_MINUTE, 1), 'long_sections': long}


def attention(text, api):
    """Per passage: words, total visible time on this revision, and whether it was scrolled past."""
    _, meta = api.island(text, 'brief-meta')
    record = read_record(text, api)
    current = [s for s in record['sessions'] if s['revision'] == meta['revision']]
    passages = Passages(text).found
    seen, titles = {}, {}
    for session in current:
        for target in session['targets']:
            titles.setdefault(target['anchor'], target['title'])
            if target['visible_ms'] is not None:
                seen[target['anchor']] = seen.get(target['anchor'], 0) + target['visible_ms']
    rows = []
    for anchor, passage in sorted(passages.items(), key=lambda pair: pair[1]['order']):
        need = reading_ms(passage['words'])
        visible = seen.get(anchor)  # None: never measured on this revision, which is not zero
        verdict = ('unmeasured' if visible is None else 'unseen' if visible == 0
                   else 'passed' if visible < PASSED_SHARE * need else 'had_time')
        rows.append({'anchor': anchor, 'kind': passage['kind'], 'title': titles.get(anchor) or passage['title'] or anchor,
                     'words': passage['words'], 'visible_ms': visible, 'reading_ms': need, 'verdict': verdict})
    sections = [r for r in rows if r['kind'] == 'section']
    for index, row in enumerate(sections):
        row['third'] = ('first', 'middle', 'last')[min(2, index * 3 // max(1, len(sections)))]
    return {'document': meta['id'], 'revision': meta['revision'], 'sessions': len(current),
            'earlier_revision_sessions': len(record['sessions']) - len(current), 'passages': rows}


def attention_text(report):
    rows, out = report['passages'], []
    out.append(f"ATTENTION — {report['document']} · {report['revision'][7:19]} · {report['sessions']} reading "
               f"session{'s' if report['sessions'] != 1 else ''} on this version"
               + (f" ({report['earlier_revision_sessions']} on earlier versions, not counted)"
                  if report['earlier_revision_sessions'] else ''))
    if not report['sessions']:
        out.append('Nobody has read this version with the clock running. Unknown, not zero: draw no conclusion.')
        return '\n'.join(out) + '\n'
    out.append(f'Estimate: {WORDS_PER_MINUTE} words a minute, at least {FLOOR_MS // 1000} s a passage. '
               f'Passed = on screen for under {round(PASSED_SHARE * 100)}% of that.')
    groups = (('passed', 'PASSED — scrolled past. Either not needed here, or needed and missed: decide which.'),
              ('unseen', 'UNSEEN — never on screen while the page was active.'),
              ('had_time', 'HAD TIME — on screen long enough to read. That is room to read, not proof of it.'),
              ('unmeasured', 'UNMEASURED — no record on this version.'))
    for verdict, heading in groups:
        chosen = [r for r in rows if r['verdict'] == verdict]
        if not chosen:
            continue
        out.append('')
        out.append(f'{heading} ({len(chosen)})')
        for r in chosen:
            time = '' if r['visible_ms'] is None else f" · {clock(r['visible_ms'])} of ~{clock(r['reading_ms'])}"
            out.append(f"  [{r['anchor']}] {r['kind']} · {r['title'][:70]}{time} · {r['words']} words")
    return '\n'.join(out) + '\n'


def attention_across(reports):
    """Where across many briefs readers scroll past: by kind of passage, and by place among the sections."""
    tally = {}
    for report in reports:
        if not report['sessions']:
            continue
        for row in report['passages']:
            if row['verdict'] == 'unmeasured':
                continue
            for key in (row['kind'], 'section · ' + row['third'] if 'third' in row else None):
                if key:
                    measured, passed = tally.get(key, (0, 0))
                    tally[key] = (measured + 1, passed + (row['verdict'] in ('passed', 'unseen')))
    read = sum(1 for r in reports if r['sessions'])
    out = [f'ACROSS {len(reports)} BRIEFS · {read} with reading time · passed or unseen / measured']
    for key in sorted(tally):
        measured, passed = tally[key]
        out.append(f'  {key:<18} {passed:>4} / {measured:<4} {round(100 * passed / measured):>3}%')
    if not tally:
        out.append('  No measured passages. Unknown, not zero.')
    return '\n'.join(out) + '\n', tally
