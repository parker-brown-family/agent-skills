#!/usr/bin/env python3
"""Build an HTML brief, check local links, or hand anchored feedback to an agent."""
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parents[1]
KIT = HERE.parent / 'decision-brief'
LOOK = HERE.parent / 'fancy-pants-brief'
SAFE_ID = re.compile(r'^[a-z][a-z0-9-]*$')
META = re.compile(r'<!-- briefing:\s*(\{.*?\})\s*-->', re.S)
MIRROR = re.compile(r'<!--\nREADER NOTES —.*?-->', re.S)
CONTENT = re.compile(r'<!--brief-content-->(.*?)<!--/brief-content-->', re.S)


class Refusal(ValueError):
    pass


def read(path):
    return Path(path).read_bytes().decode('utf-8')


def digest(text):
    return 'sha256:' + hashlib.sha256(text.encode()).hexdigest()


def encode(value):
    return json.dumps(value, ensure_ascii=False, indent=2).replace('</', '<\\/').replace('<!', '\\u003c!')


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.targets, self.links, self.headings, self.figures = [], [], [], [], []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if 'data-brief-anchor' in attrs:
            anchor = attrs['data-brief-anchor']
            if not anchor or attrs.get('id') != anchor or not SAFE_ID.fullmatch(anchor):
                raise Refusal('a data-brief-anchor must equal its explicit, lowercase id')
            self.targets.append(anchor)
        if tag == 'h2':
            self.headings.append(attrs.get('data-brief-anchor'))
        if tag == 'figure':
            self.figures.append(attrs.get('data-brief-anchor'))
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])


class Content(HTMLParser):
    """Hash authored meaning after browser snapshot serialization, without its note UI."""
    def __init__(self, text):
        super().__init__()
        self.parts, self.skip = [], 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = {key: '' if value is None else value for key, value in attrs}
        if tag == 'nav' and 'sections' in attrs.get('class', '').split():
            self.skip += 1
        if self.skip:
            return
        for name in ('data-nid', 'data-ntitle'):
            attrs.pop(name, None)
        if 'class' in attrs:
            classes = set(attrs['class'].split()) - {'notable', 'has-note', 'concurrable', 'has-concur', 'concur-jolt'}
            if classes:
                attrs['class'] = ' '.join(sorted(classes))
            else:
                del attrs['class']
        self.parts.append(('start', tag, sorted(attrs.items())))

    def handle_endtag(self, tag):
        if self.skip:
            if tag == 'nav':
                self.skip -= 1
            return
        self.parts.append(('end', tag))

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(('text', data))


def content_revision(text, identity, purpose):
    regions = list(CONTENT.finditer(text))
    if len(regions) != 1:
        raise Refusal('expected one brief-content region around authored header and main')
    return digest(json.dumps([identity, purpose, Content(regions[0][1]).parts], ensure_ascii=False))


def island(text, name):
    opens = list(re.finditer(r'<script\b[^>]*\bid\s*=\s*[\"\']' + re.escape(name) + r'[\"\'][^>]*>', text, re.I))
    if len(opens) != 1:
        raise Refusal(f'{name}: expected exactly one island')
    opening = opens[0]
    closing = re.search(r'</script\s*>', text[opening.end():], re.I)
    if not closing:
        raise Refusal(f'{name}: unclosed island')
    end = opening.end() + closing.end()
    payload = text[opening.end():opening.end() + closing.start()]
    if '<script' in payload.lower():
        raise Refusal(f'{name}: nested script in island')
    if name.startswith('report-'):
        version = re.search(r'\bdata-format=[\"\']([^\"\']+)', opening[0])
        if not version or version[1] != '1':
            raise Refusal(f'{name}: unsupported annotation format')
    try:
        value = json.loads(payload)
    except ValueError as exc:
        raise Refusal(f'{name}: malformed JSON') from exc
    if not isinstance(value, dict):
        raise Refusal(f'{name}: expected object')
    return text[opening.start():end], value


def notes(text):
    nb, nm = island(text, 'report-notes')
    cb, cm = island(text, 'report-concurs')
    if not all(isinstance(v, list) and all(isinstance(n, dict) and isinstance(n.get('text'), str) for n in v) for v in nm.values()):
        raise Refusal('report-notes: expected lists of reader comments')
    if not all(isinstance(v, str) for v in cm.values()):
        raise Refusal('report-concurs: expected timestamp strings')
    return nb, nm, cb, cm


def inspect(path):
    text = read(path)
    if path.suffix == '.html':
        _, meta = island(text, 'brief-meta')
        page = Page(text)
        anchors, links = page.ids, page.links
        if meta.get('medium') != 'html':
            raise Refusal('brief-meta: medium must be html')
        if not isinstance(meta.get('revision'), str):
            raise Refusal('brief-meta: missing content revision')
        if not isinstance(meta.get('id'), str) or not isinstance(meta.get('purpose'), str):
            raise Refusal('brief-meta: missing identity or purpose')
        revision = content_revision(text, meta['id'], meta['purpose'])
    elif path.suffix == '.md':
        matches = list(META.finditer(text))
        if len(matches) != 1:
            raise Refusal('Markdown needs one <!-- briefing: {...} --> identity comment')
        meta = json.loads(matches[0][1])
        if not isinstance(meta, dict):
            raise Refusal('Markdown identity: expected object')
        if meta.get('medium') != 'markdown':
            raise Refusal('Markdown identity: medium must be markdown')
        prose = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)
        page = Page(prose)
        anchors = page.ids + re.findall(r'^\^([a-z][a-z0-9-]*)\s*$', prose, re.M)
        # Heading links are accepted; stable feedback targets still use explicit ids.
        explicit = anchors[:]
        for heading in re.findall(r'^#{1,6}\s+(.+)$', prose, re.M):
            slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
            if slug not in anchors:
                anchors.append(slug)
        links = page.links + re.findall(r'(?<!!)\[[^\]\n]+\]\(([^\s)]+)\)', prose)
        revision = digest(text)
    else:
        raise Refusal('supported now: .md and .html; MP4 is reserved')
    if not isinstance(meta.get('id'), str) or not SAFE_ID.fullmatch(meta['id']):
        raise Refusal('brief identity needs a stable lowercase id')
    if not isinstance(meta.get('purpose'), str) or not meta['purpose'].strip():
        raise Refusal('brief metadata needs an explicit purpose')
    duplicates = [k for k, v in Counter(explicit if path.suffix == '.md' else anchors).items() if v > 1]
    if duplicates:
        raise Refusal('duplicate anchors: ' + ', '.join(duplicates))
    return text, meta, revision, anchors, links


def check(path):
    text, meta, revision, anchors, links = inspect(path)
    if path.suffix == '.html':
        page = Page(text)
        if not page.headings or not all(page.headings + page.figures):
            raise Refusal('every h2 and figure needs an explicit data-brief-anchor')
        notes(text)
    for link in links:
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc:
            continue  # External source links are references, never fetched by this checker.
        target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
        if not target.is_file():
            raise Refusal(f'broken local link: {link}')
        if parsed.fragment:
            if target == path:
                target_anchors = anchors
            elif target.suffix in ('.md', '.html'):
                linked = read(target)
                target_anchors = Page(linked).ids
                target_anchors += re.findall(r'^\^([a-z][a-z0-9-]*)\s*$', linked, re.M)
                target_anchors += [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in re.findall(r'^#{1,6}\s+(.+)$', linked, re.M)]
            else:
                raise Refusal(f'cannot verify local fragment: {link}')
            if unquote(parsed.fragment).removeprefix('^') not in target_anchors:
                raise Refusal(f'broken local fragment: {link}')
    return {'id': meta['id'], 'revision': revision, 'anchors': len(anchors), 'links': len(links)}


def atomic(path, text, expected=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(text.encode())
        # Refuse a concurrent annotation write instead of replacing it with an older copy.
        actual = path.read_bytes() if path.exists() else None
        if actual != expected:
            raise Refusal('output changed during build; retry from the latest file')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def build(source, output, identity, purpose):
    if output.suffix != '.html':
        raise Refusal('HTML output needs an .html suffix')
    if source.resolve() == output.resolve():
        raise Refusal('source and output must be different files')
    text = read(source)
    for slot in ('head', 'notes'):
        if text.count('<!--BRIEF:' + slot + '-->') != 1:
            raise Refusal(f'expected one BRIEF:{slot} placeholder')
    if re.findall(r'<!--BRIEF:(.*?)-->', text) != ['head', 'notes']:
        raise Refusal('unknown or out-of-order BRIEF placeholder')
    page = Page(text)
    if len(page.ids) != len(set(page.ids)) or not page.headings or not all(page.headings + page.figures):
        raise Refusal('source needs unique ids and explicit anchors on every h2 and figure')
    if not SAFE_ID.fullmatch(identity):
        raise Refusal('use a stable lowercase brief id')
    old_bytes = output.read_bytes() if output.exists() else None
    old = old_bytes.decode('utf-8') if old_bytes is not None else None
    previous = None
    retained = None
    if old is not None:
        _, previous = island(old, 'brief-meta')
        if previous.get('id') != identity:
            raise Refusal('output belongs to a different brief')
        retained = notes(old)
    base = read(KIT / 'assets/base.css')
    note_css = read(KIT / 'assets/notes.css')
    note_js = read(KIT / 'assets/notes.js')
    # Checked adaptation at assembly time; the shared source and wire format stay intact.
    hook = 'if (num) id = pre + \'-\' + num.textContent.trim();'
    if note_js.count(hook) != 1:
        raise Refusal('canonical notes anchor hook changed; review the adapter before building')
    note_js = note_js.replace(hook, "if (el.hasAttribute('data-brief-anchor')) id = el.getAttribute('data-brief-anchor');\n        else " + hook)
    if '</script' in note_js.lower():
        raise Refusal('canonical notes script contains a closing script tag')
    wall = re.search(r'<style id="brief-wall">.*?</style>', old or '', re.S)
    wall = wall[0] if wall else subprocess.run([sys.executable, str(KIT / 'scripts/brief-wall')], check=True, capture_output=True, text=True).stdout
    revision = content_revision(text, identity, purpose)
    meta = {'id': identity, 'medium': 'html', 'purpose': purpose, 'revision': revision, 'feedback_revision': revision}
    if previous and retained and (retained[1] or retained[3]):
        # Format 1 has no per-comment content revision. Mixed-origin notes stay unknown.
        meta['feedback_revision'] = previous.get('feedback_revision') if previous.get('revision') == revision else None
    markup = read(KIT / 'reference/notes-markup.html')
    markup = re.sub(r'<script>.*?</script>', '', markup, flags=re.S)
    if retained:
        for name, block in (('report-notes', retained[0]), ('report-concurs', retained[2])):
            empty, _ = island(markup, name)
            markup = markup.replace(empty, block, 1)
        mirrors = list(MIRROR.finditer(old))
        if mirrors:
            markup += mirrors[-1][0]
    head = '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark">'
    head += '<style>' + base + '</style>' + wall + '<style>' + note_css + '</style>'
    config = '<script>window.NOTES_TARGETS=[[\'[data-brief-anchor]\',\'brief\']];window.NOTES_FILE=' + encode(identity + '-' + revision[7:19]) + ';</script>'
    payload = markup + '<script type="application/json" id="brief-meta">' + encode(meta) + '</script>' + config
    bridge = read(HERE / 'assets/feedback-bridge.js')
    if '</script' in bridge.lower():
        raise Refusal('feedback bridge contains a closing script tag')
    payload += '<script>' + read(LOOK / 'assets/sections.js') + '</script><script>' + note_js + '</script><script>' + bridge + '</script>'
    text = text.replace('<!--BRIEF:head-->', head).replace('<!--BRIEF:notes-->', payload)
    # Validate all islands before touching the previous file.
    notes(text)
    if old_bytes is not None:
        backup = output.with_name(output.name + '.' + hashlib.sha256(old_bytes).hexdigest()[:12] + '.bak')
        if backup.exists() and backup.read_bytes() != old_bytes:
            raise Refusal('backup collision')
        if not backup.exists():
            with backup.open('xb') as stream:
                stream.write(old_bytes)
    atomic(output, text, old_bytes)
    return {'output': str(output), 'revision': revision, 'feedback_revision': meta['feedback_revision']}


def feedback(path):
    text, meta, revision, anchors, _ = inspect(path)
    comments = []
    if path.suffix == '.html':
        _, nm, _, cm = notes(text)
        for anchor, entries in nm.items():
            for entry in entries:
                comments.append({'target': anchor, 'title': entry.get('title'), 'text': entry['text'], 'stance': None, 'at': entry.get('ts')})
        comments += [{'target': a, 'title': None, 'text': '', 'stance': 'agree', 'at': ts} for a, ts in cm.items()]
        revision = meta.get('feedback_revision')
    return {'format': 1, 'document': {'id': meta['id'], 'href': path.name, 'medium': meta['medium'], 'revision': revision}, 'comments': comments}


def resolve(path, map_path):
    _, meta, revision, anchors, _ = inspect(path)
    data = json.loads(read(map_path))
    if not isinstance(data, dict) or data.get('format') != 1:
        raise Refusal('unsupported feedback format')
    doc, comments = data.get('document'), data.get('comments')
    if not isinstance(doc, dict) or not isinstance(comments, list):
        raise Refusal('feedback needs document and comments')
    common = []
    if doc.get('id') != meta['id'] or doc.get('medium') != meta['medium']:
        common.append('document_mismatch')
    if doc.get('revision') is None:
        common.append('revision_unknown')
    elif doc['revision'] != revision:
        common.append('revision_changed')
    for comment in comments:
        if not isinstance(comment, dict) or not isinstance(comment.get('target'), str) or not isinstance(comment.get('text'), str):
            raise Refusal('each comment needs a target and text')
        if comment.get('stance') not in (None, 'agree', 'disagree'):
            raise Refusal('invalid stance; unknown is null')
        if not comment['text'].strip() and comment.get('stance') is None:
            raise Refusal('empty comment without an explicit stance')
        reasons = common + ([] if comment['target'] in anchors else ['target_missing'])
        comment['status'] = 'needs_review' if reasons else 'resolved'
        comment['reasons'] = reasons
    data['current_revision'] = revision
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('html')
    p.add_argument('source', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--id', required=True)
    p.add_argument('--purpose', required=True)
    for name in ('check', 'feedback', 'resolve'):
        p = commands.add_parser(name)
        p.add_argument('document', type=Path)
        if name == 'resolve':
            p.add_argument('map', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'html':
            result = build(args.source, args.output, args.id, args.purpose)
        elif args.command == 'check':
            result = check(args.document)
        elif args.command == 'feedback':
            result = feedback(args.document)
        else:
            result = resolve(args.document, args.map)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if args.command == 'resolve' and any(c['status'] != 'resolved' for c in result['comments']) else 0
    except (Refusal, OSError, ValueError, subprocess.CalledProcessError) as exc:
        print('brief: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
