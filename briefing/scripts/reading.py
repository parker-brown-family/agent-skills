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
