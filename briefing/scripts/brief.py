#!/usr/bin/env python3
"""Start, build and check a brief, then place a reader's returned comments against it.

new → write → html (HTML only) → check → deliver → feedback / resolve. `doctor` says what works here."""
import argparse
from collections import Counter
import hashlib
from html import escape as html_escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
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
VOID_TAGS = set('area base br col embed hr img input link meta param source track wbr'.split())
# An HTML build reads these from the sibling skills; Markdown needs none of them.
KIT_FILES = [KIT / 'assets/base.css', KIT / 'assets/notes.css', KIT / 'assets/notes.js',
             KIT / 'reference/notes-markup.html', KIT / 'scripts/brief-wall', LOOK / 'assets/sections.js']
# A scaffold's unwritten passages. `check` refuses a brief that still carries one.
UNWRITTEN = 'TODO(brief)'


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
        if tag in ('img', 'source') and attrs.get('src'):
            self.links.append(attrs['src'])


def heading_slug(heading):
    return re.sub(r'[^\w\- ]', '', re.sub(r'\s+#+\s*$', '', heading).strip().lower()).replace(' ', '-')


def markdown_prose(text):
    """Markdown with fenced code removed, so an example inside a fence is not a link or an anchor."""
    return re.sub(r'^ {0,3}(`{3,}|~{3,})[^\n]*\n.*?^ {0,3}\1\s*$', '', text, flags=re.M | re.S)


def markdown_links(prose):
    """Inline links and images, with or without a title or angle brackets, plus reference definitions."""
    prose = re.sub(r'(`+)[^`\n]+?\1', '', prose)
    inline = re.findall(r'\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+(?:"[^"\n]*"|\'[^\'\n]*\'|\([^)\n]*\)))?\s*\)', prose)
    defined = re.findall(r'^ {0,3}\[(?!\^)[^\]\n]+\]:\s*(<[^>\n]+>|\S+)', prose, re.M)
    return [link[1:-1] if link.startswith('<') else link for link in inline + defined]


def anchors_in(text):
    """Every anchor a link may name in a linked Markdown or HTML file."""
    prose = markdown_prose(text)
    return Page(prose).ids + block_ids(prose) + [heading_slug(h) for h in re.findall(r'^#{1,6}\s+(.+)$', prose, re.M)]


def block_ids(prose):
    """Obsidian block ids: `^name` alone on a line, or ending a paragraph's line after a space."""
    return re.findall(r'(?:^|[ \t])\^([a-z][a-z0-9-]*)[ \t]*$', prose, re.M)


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
        if 'data-depth' in attrs:
            attrs.pop('hidden', None)  # Evidence depth is a reader control.
        if tag == 'details':
            attrs.pop('open', None)
        if 'class' in attrs:
            classes = set(attrs['class'].split()) - {'notable', 'has-note', 'concurrable', 'has-concur', 'concur-jolt'}
            if classes:
                attrs['class'] = ' '.join(sorted(classes))
            else:
                del attrs['class']
        if tag != 'tbody' or attrs:
            self.parts.append(('start', tag, sorted(attrs.items())))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.skip:
            if tag == 'nav':
                self.skip -= 1
            return
        if tag != 'tbody':
            self.parts.append(('end', tag))

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(('text', data))


def content_revision(text, identity, purpose):
    regions = list(CONTENT.finditer(text))
    if len(regions) != 1:
        raise Refusal('expected one brief-content region around authored header and main')
    return digest(json.dumps([identity, purpose, Content(regions[0][1]).parts], ensure_ascii=False))


class Scripts(HTMLParser):
    """Locate actual script (or style) elements, ignoring tag-shaped words inside their data."""
    def __init__(self, text, tag='script'):
        super().__init__()
        self.text, self.tag, self.blocks, self.active = text, tag, [], None
        self.offsets = [0] + [match.end() for match in re.finditer('\n', text)]
        self.feed(text)

    def position(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag == self.tag:
            start = self.position()
            self.active = (dict(attrs), start, start + len(self.get_starttag_text()))

    def handle_endtag(self, tag):
        if tag == self.tag and self.active is not None:
            start = self.position()
            end = self.text.find('>', start) + 1
            self.blocks.append((*self.active, start, end))
            self.active = None


def island(text, name):
    scripts = Scripts(text)
    matches = [block for block in scripts.blocks if block[0].get('id') == name]
    if len(matches) != 1 or (scripts.active and scripts.active[0].get('id') == name):
        raise Refusal(f'{name}: expected exactly one island')
    attrs, start, content_start, content_end, end = matches[0]
    payload = text[content_start:content_end]
    if name.startswith('report-'):
        if attrs.get('data-format') != '1':
            raise Refusal(f'{name}: unsupported annotation format')
    try:
        value = json.loads(payload)
    except ValueError as exc:
        raise Refusal(f'{name}: malformed JSON') from exc
    if not isinstance(value, dict):
        raise Refusal(f'{name}: expected object')
    return text[start:end], value


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
        prose = markdown_prose(text)
        page = Page(prose)
        anchors = page.ids + block_ids(prose)
        # Heading links are accepted; stable feedback targets still use explicit ids.
        explicit = anchors[:]
        for heading in re.findall(r'^#{1,6}\s+(.+)$', prose, re.M):
            slug = heading_slug(heading)
            if slug not in anchors:
                anchors.append(slug)
        links = page.links + markdown_links(prose)
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


def local_target(path, link):
    """The local file a link opens, or None for a link to another machine."""
    parsed = urlsplit(link)
    if parsed.scheme == 'file' and parsed.netloc in ('', 'localhost'):
        return Path(unquote(parsed.path)), parsed.fragment
    if parsed.scheme or parsed.netloc:
        return None, None  # External source links are references, never fetched by this checker.
    return ((path.parent / unquote(parsed.path)).resolve() if parsed.path else path), parsed.fragment


def check(path):
    text, meta, revision, anchors, links = inspect(path)
    result = {'id': meta['id'], 'revision': revision, 'anchors': len(anchors), 'links': len(links)}
    if path.suffix == '.html':
        page = Page(text)
        if not page.headings or not all(page.headings + page.figures):
            raise Refusal('every h2 and figure needs an explicit data-brief-anchor')
        notes(text)
        # Only a built page has a recorded revision to compare; Markdown leaves this undeclared.
        result['edited_since_build'] = revision != meta['revision']
        result['wallpaper'] = wall_label(text)
        result['comment_targets'] = len(page.targets)
        region = CONTENT.search(text)[1]
    else:
        region = markdown_prose(text)
        # Explicit ids and ^blocks survive a heading rename; heading slugs, also counted in anchors, do not.
        result['comment_targets'] = len(set(Page(region).ids + block_ids(region)))
    if UNWRITTEN in region:
        raise Refusal(f'unwritten scaffold passage: replace every {UNWRITTEN} before delivery')
    external, broken = 0, []
    for link in links:
        target, fragment = local_target(path, link)
        if target is None:
            external += 1
            continue
        if not target.exists():
            broken.append(f'broken local link: {link}')
        elif fragment:
            if target == path:
                target_anchors = anchors
            elif target.suffix in ('.md', '.html') and target.is_file():
                target_anchors = anchors_in(read(target))
            else:
                broken.append(f'cannot verify local fragment: {link}')
                continue
            if unquote(fragment).removeprefix('^') not in target_anchors:
                broken.append(f'broken local fragment: {link}')
    if broken:
        # Every bad link at once, so one pass of fixes is enough.
        raise Refusal('; '.join(dict.fromkeys(broken)))
    result['external_links_unchecked'] = external
    return result


def atomic(path, text, expected=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(text.encode())
        # mkstemp makes 0600; a page is for readers, so keep its old mode or honour the umask.
        if path.exists():
            os.chmod(temporary, path.stat().st_mode & 0o777)
        else:
            umask = os.umask(0)
            os.umask(umask)
            os.chmod(temporary, 0o666 & ~umask)
        # Refuse a concurrent annotation write instead of replacing it with an older copy.
        actual = path.read_bytes() if path.exists() else None
        if actual != expected:
            raise Refusal('output changed during build; retry from the latest file')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def kit_missing():
    return [str(path) for path in KIT_FILES if not path.is_file()]


WALL_IMAGE = re.compile(r'url\("data:image/[a-z+]+;base64,[A-Za-z0-9+/=]{100,}')


def wall_of(text):
    """The page's real <style id="brief-wall"> element, if it carries a wallpaper image.

    base.css names that element inside its own comment, so a text search finds the comment
    first; only the parser sees the element itself. An imageless wall is damage, not a wall."""
    for attrs, start, content_start, content_end, end in reversed(Scripts(text or '', 'style').blocks):
        if attrs.get('id') == 'brief-wall':
            return text[start:end] if WALL_IMAGE.search(text[content_start:content_end]) else None
    return None


def wall_label(text):
    wall = wall_of(text)
    if not wall:
        return None
    named = re.search(r'brief-wall — theme ([^\s(]+)[^,]*, wallpaper ([^\s·*]+)', wall)
    return f'{named[1]} · {named[2]}' if named else 'unlabelled wallpaper'


def pick_wall(old, no_wall):
    """Keep the wallpaper a rebuilt page already wears; otherwise ask brief-wall for one."""
    if no_wall:
        return ''
    kept = wall_of(old)
    if kept:
        return kept
    try:
        return subprocess.run([sys.executable, str(KIT / 'scripts/brief-wall')], check=True, capture_output=True, text=True).stdout
    except subprocess.CalledProcessError as exc:
        reason = ((exc.stderr or '').strip().splitlines() or ['brief-wall failed without a message'])[-1]
        raise Refusal(f'no wallpaper: {reason}. Pass --no-wall to build on the stylesheet\'s own dark ground, '
                      'outside the Omarchy house look.') from exc


def source_identity(text, identity, purpose):
    """Fill --id and --purpose from the source's own <!-- briefing: {...} --> comment, which `new` writes."""
    found = [json.loads(match[1]) for match in META.finditer(text)]
    if len(found) > 1 or (found and not isinstance(found[0], dict)):
        raise Refusal('a source carries at most one <!-- briefing: {...} --> identity object')
    declared = found[0] if found else {}
    for name, given in (('id', identity), ('purpose', purpose)):
        if given and declared.get(name) and given != declared[name]:
            raise Refusal(f'--{name} {given} disagrees with the source, which says {declared[name]}; change one of them')
    identity, purpose = identity or declared.get('id'), purpose or declared.get('purpose')
    if not identity or not purpose:
        raise Refusal('name the brief: pass --id and --purpose, or put <!-- briefing: {"id": "…", "purpose": "…"} --> in the source')
    return identity, purpose


def build(source, output, identity=None, purpose=None, no_wall=False, discard_edits=False):
    if output.suffix != '.html':
        raise Refusal('HTML output needs an .html suffix')
    if source.resolve() == output.resolve():
        raise Refusal('source and output must be different files')
    missing = kit_missing()
    if missing:
        raise Refusal('an HTML build reads the decision-brief and fancy-pants-brief skills installed beside this one, '
                      'and these are missing: ' + ', '.join(missing) + '. Install the three directories side by side, '
                      'or write the brief in Markdown, which needs nothing else. `brief.py doctor` lists what works here.')
    text = read(source)
    identity, purpose = source_identity(text, identity, purpose)
    for slot in ('head', 'notes'):
        if text.count('<!--BRIEF:' + slot + '-->') != 1:
            raise Refusal(f'expected one BRIEF:{slot} placeholder')
    if re.findall(r'<!--BRIEF:(.*?)-->', text) != ['head', 'notes']:
        raise Refusal('unknown or out-of-order BRIEF placeholder')
    regions = list(CONTENT.finditer(text))
    if len(regions) == 1 and '<!--BRIEF:' in regions[0][1]:
        # Assembled UI inside the fingerprinted region would make every feedback map stale at birth.
        raise Refusal('keep <!--BRIEF:head--> and <!--BRIEF:notes--> outside the <!--brief-content--> region')
    page = Page(text)
    if len(page.ids) != len(set(page.ids)) or not page.headings or not all(page.headings + page.figures):
        raise Refusal('source needs unique ids and explicit anchors on every h2 and figure')
    if not SAFE_ID.fullmatch(identity):
        raise Refusal('use a stable lowercase brief id')
    old_bytes = output.read_bytes() if output.exists() else None
    old = old_bytes.decode('utf-8') if old_bytes is not None else None
    previous = None
    retained = None
    edited = False
    if old is not None:
        try:
            _, previous = island(old, 'brief-meta')
        except Refusal as exc:
            raise Refusal(f'{output} exists and was not built by this helper ({exc}); choose another output path or move that file aside') from exc
        if previous.get('id') != identity:
            raise Refusal(f"{output.name} belongs to the brief {previous.get('id')!r}, not {identity!r}; "
                          f"build with --id {previous.get('id')} or choose another output path")
        retained = notes(old)
        try:
            edited = content_revision(old, identity, previous.get('purpose')) != previous.get('revision')
        except Refusal:
            edited = True
        if edited and not discard_edits:
            # A rebuild from the source would silently drop an edit made to the page itself.
            raise Refusal(f'{output.name} was edited after its last build and {source.name} does not have those edits. '
                          'Port them into the source and rebuild, or pass --discard-output-edits '
                          '(the edited page is kept as a .bak file).')
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
    wall = pick_wall(old, no_wall)
    revision = content_revision(text, identity, purpose)
    meta = {'id': identity, 'medium': 'html', 'purpose': purpose, 'revision': revision, 'feedback_revision': revision}
    if previous and retained and (retained[1] or retained[3]):
        # Format 1 has no per-comment content revision. Mixed-origin notes stay unknown, and so
        # do notes a reader left on hand-edited wording that this rebuild discards.
        same = previous.get('revision') == revision and not edited
        meta['feedback_revision'] = previous.get('feedback_revision') if same else None
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
    # Validate all islands, and that the page fingerprints as its source did, before touching the previous file.
    notes(text)
    if content_revision(text, identity, purpose) != revision:
        raise Refusal('the assembled page fingerprints differently from its source; report this with the source attached')
    if old_bytes is not None:
        backup = output.with_name(output.name + '.' + hashlib.sha256(old_bytes).hexdigest()[:12] + '.bak')
        if backup.exists() and backup.read_bytes() != old_bytes:
            raise Refusal('backup collision')
        if not backup.exists():
            with backup.open('xb') as stream:
                stream.write(old_bytes)
    atomic(output, text, old_bytes)
    result = {'output': str(output), 'id': identity, 'revision': revision, 'feedback_revision': meta['feedback_revision'],
              'wallpaper': wall_label(text)}
    if old_bytes is not None:
        result['backup'] = str(backup)
    if edited:
        result['discarded_output_edits'] = str(backup)
    return result


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


def copy_map(text):
    """Normalize the HTML reader's Copy map text into a format-1 envelope, or None if it is not one.

    The text names the page as `NOTES — <id>-<first 12 hex of its revision>`. It joins each note's
    lines with spaces, so the envelope says so rather than passing the words off as exact."""
    text = text.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')
    head = re.search(r'^NOTES — (\S+)[ \t]*$', text, re.M)
    if not head and re.search(r'^> ?NOTES — ', text, re.M):
        text = re.sub(r'^> ?', '', text, flags=re.M)  # pasted as a chat quote
        head = re.search(r'^NOTES — (\S+)[ \t]*$', text, re.M)
    if not head:
        return None
    named = re.fullmatch(r'(.+)-([0-9a-f]{12})', head[1])
    identity, revision = (named[1], 'sha256:' + named[2]) if named else (head[1], None)
    # The bridge marks carried notes; a READER NOTES mirror inside a saved file never carries that mark.
    if 'REVISION UNKNOWN' in text or 'READER NOTES —' in text[:head.start()]:
        revision = None
    comments, target, title, orphan = [], None, None, False
    for line in text[head.end():].splitlines():
        block = re.match(r'\[([^\]\s]+)\] ?(.*)$', line)
        if block:
            target, rest = block[1], block[2].rstrip()
            orphan = rest.startswith('UNRESOLVED')
            title = None if orphan else (rest.removesuffix('✓ concur').rstrip() or None)
            if not orphan and rest.endswith('✓ concur'):
                comments.append({'target': target, 'title': title, 'text': '', 'stance': 'agree', 'at': None})
            continue
        note = re.match(r'  · (.*)$', line)
        if note and target:
            if orphan and note[1] == 'Explicit agreement on the earlier target':
                comments.append({'target': target, 'title': None, 'text': '', 'stance': 'agree', 'at': None})
            else:
                comments.append({'target': target, 'title': title, 'text': note[1], 'stance': None, 'at': None})
        elif not line.strip():
            target = None
    # `revision` is a full fingerprint by contract; the copy carries only its first twelve hex digits.
    return {'format': 1, 'document': {'id': identity, 'href': None, 'medium': 'html', 'revision': None, 'revision_prefix': revision},
            'comments': comments, 'source': 'copy-map', 'text_exact': False}


def load_map(map_path):
    raw = sys.stdin.read() if str(map_path) == '-' else read(map_path)
    try:
        return json.loads(raw)
    except ValueError:
        data = copy_map(raw)
        if data is None:
            raise Refusal('the map is neither a format-1 JSON envelope nor Copy map text, which starts with a line '
                          '"NOTES — <brief id>-<12 hex>". Ask the reader to press copy map again and paste all of it, '
                          'or read their message as ordinary feedback against the brief')
        return data


def resolve(path, map_path):
    _, meta, revision, anchors, _ = inspect(path)
    data = load_map(map_path)
    if not isinstance(data, dict) or data.get('format') != 1:
        raise Refusal('unsupported feedback format')
    doc, comments = data.get('document'), data.get('comments')
    if not isinstance(doc, dict) or not isinstance(comments, list):
        raise Refusal('feedback needs document and comments')
    common = []
    if doc.get('id') != meta['id'] or doc.get('medium') != meta['medium']:
        common.append('document_mismatch')
    claimed, prefix = doc.get('revision'), doc.get('revision_prefix')
    if claimed is None and not prefix:
        common.append('revision_unknown')
    elif (claimed is not None and claimed != revision) or (claimed is None and not revision.startswith(prefix)):
        # A Copy map carries only the first twelve hex digits of the revision it was made on.
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


QUESTIONS = {
    'summary': 'what happened, what matters, and what follows?',
    'engineering': 'how does this work, why was it shaped this way, and what establishes that it works?',
    'decision': 'what choice is mine, what do you recommend, and what follows from choosing it?',
}
HTML_SCAFFOLD = '''<!doctype html>
<html lang="en"><head><title>{title}</title><!-- briefing: {meta} --><!--BRIEF:head-->
<style>
/* This brief's own figures and notes. The house look arrives through BRIEF:head. */
svg{display:block;width:100%;height:auto}.small{font-size:13px;color:var(--dim)}
</style></head><body>
<!--brief-content-->
<header class="top"><div class="wrap"><div class="eyebrow">Briefing · {purpose} · HTML</div><h1>{title}</h1><p class="lede">TODO(brief): two sentences on why this brief exists, for this reader.</p><nav class="sections"></nav></div></header>
<main class="wrap">
<!-- The reader must be able to answer: {question}
     Each section answers the question the one before it raised. Give every h2 and figure an id equal to its
     data-brief-anchor. Rename these ids now; once anyone has commented, keep an id when its heading changes. -->
<section class="pane"><h2 id="sec-finding" data-brief-anchor="sec-finding"><span class="n">01</span> TODO(brief): the first answer</h2>
<p>TODO(brief): the passage. Name a mechanism before using its identifiers, and link evidence where a claim needs it.</p>
<figure id="fig-mechanism" data-brief-anchor="fig-mechanism"><span class="lbl">01 · TODO(brief): what this drawing shows</span>
<svg viewBox="0 0 640 160" role="img" aria-label="TODO(brief): what the drawing shows"><rect class="box struct" x="20" y="40" width="200" height="80" rx="10"/><text class="ink" x="120" y="86" text-anchor="middle" font-size="16">TODO(brief)</text><path class="wire" d="M220 80 H420" fill="none"/><rect class="box unk" x="420" y="40" width="200" height="80" rx="10"/><text class="ink" x="520" y="86" text-anchor="middle" font-size="16">unknown, labelled</text></svg>
<figcaption><b>TODO(brief): a claim the reader can argue with.</b></figcaption><p class="small">TODO(brief): drawn from the code, a measurement, a proposal or an estimate.</p></figure></section>
<section class="pane"><h2 id="sec-next" data-brief-anchor="sec-next"><span class="n">02</span> TODO(brief): what follows</h2>
<p>TODO(brief): the consequence, the open question or the ask.</p></section>
<footer><p>Primary artifact: this brief. Evidence notes, feedback maps and source are supporting links.</p></footer></main>
<!--/brief-content-->
<!--BRIEF:notes--></body></html>
'''
MARKDOWN_SCAFFOLD = '''<!-- briefing: {meta} -->

# {title}

TODO(brief): two sentences on why this brief exists, for this reader.

<!-- The reader must be able to answer: {question}
     Each section answers the question the one before it raised. Rename these anchors now;
     once anyone has commented, keep an anchor when its heading changes. -->

<a id="sec-finding"></a>
## TODO(brief): the first answer

TODO(brief): the passage. Name a mechanism before using its identifiers, and link evidence where a claim needs it.

<a id="sec-next"></a>
## TODO(brief): what follows

TODO(brief): the consequence, the open question or the ask.
'''


def scaffold(path, identity, purpose, title=None):
    """Write a starting source with every required marker; never overwrite."""
    if not SAFE_ID.fullmatch(identity):
        raise Refusal('use a stable lowercase brief id, such as cache-eviction-summary')
    if not purpose.strip():
        raise Refusal('name the purpose: summary, engineering, decision, or another outcome stated plainly')
    title = title or identity.replace('-', ' ').capitalize()
    question = QUESTIONS.get(purpose, f'what outcome does this {purpose} brief give its reader?')
    if path.suffix == '.md':
        meta = json.dumps({'id': identity, 'medium': 'markdown', 'purpose': purpose}, ensure_ascii=False)
        body = MARKDOWN_SCAFFOLD.replace('{meta}', meta).replace('{title}', title)
        steps = [f'python3 {Path(__file__).resolve()} check {path}']
    elif path.suffix == '.html':
        meta = json.dumps({'id': identity, 'purpose': purpose}, ensure_ascii=False).replace('--', '\\u002d\\u002d')
        body = HTML_SCAFFOLD.replace('{meta}', meta).replace('{title}', html_escape(title)).replace('{purpose}', html_escape(purpose))
        output = path.with_name(path.name.removesuffix('.src.html') + '.html') if path.name.endswith('.src.html') else path.with_suffix('.out.html')
        steps = [f'python3 {Path(__file__).resolve()} html {path} {output}',
                 f'python3 {Path(__file__).resolve()} check {output}']
    else:
        raise Refusal('name the source .md for Markdown or .src.html for HTML')
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('x', encoding='utf-8') as stream:
            stream.write(body.replace('{question}', html_escape(question) if path.suffix == '.html' else question))
    except FileExistsError as exc:
        raise Refusal(f'{path} exists; new never overwrites a file') from exc
    return {'created': str(path), 'medium': 'markdown' if path.suffix == '.md' else 'html', 'purpose': purpose,
            'unwritten': f'replace every {UNWRITTEN}; check refuses a brief that still has one', 'next': steps}


def find_chromium():
    named = os.environ.get('CHROMIUM')
    if named:
        return named if shutil.which(named) or Path(named).is_file() else None
    for name in ('chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable', 'chrome'):
        found = shutil.which(name)
        if found:
            return found
    mac = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    return str(mac) if mac.is_file() else None


def doctor():
    """Say which parts of the skill work on this machine, and why the rest do not."""
    report = {'python': sys.version.split()[0],
              'markdown': {'ready': True, 'why': 'new, check, feedback and resolve need only Python 3.9+'}}
    missing = kit_missing()
    report['html_build'] = {'ready': not missing, 'why': 'decision-brief and fancy-pants-brief are installed beside this skill'
                            if not missing else 'missing ' + ', '.join(missing)}
    if missing:
        report['wallpaper'] = {'ready': None, 'why': 'unknown until the decision-brief skill is installed'}
    else:
        listed = subprocess.run([sys.executable, str(KIT / 'scripts/brief-wall'), '--list'], capture_output=True, text=True)
        themes = listed.returncode == 0 and bool(listed.stdout.strip())
        vips = shutil.which('vips') is not None
        report['wallpaper'] = {'ready': themes and vips, 'why': 'Omarchy themes and vips found' if themes and vips else
                               ('no Omarchy themes; ' if not themes else '') + ('vips not on PATH; ' if not vips else '') +
                               'build with --no-wall for the stylesheet\'s own dark ground'}
    gate = LOOK / 'scripts/fancy-pants'
    report['glass_gate'] = {'ready': gate.is_file(), 'why': str(gate) if gate.is_file() else 'fancy-pants-brief is not installed beside this skill'}
    node = shutil.which('node')
    major = None
    if node:
        version = subprocess.run([node, '--version'], capture_output=True, text=True).stdout.strip()
        found = re.match(r'v(\d+)', version)
        major = int(found[1]) if found else None
    chromium = find_chromium()
    ready = bool(node and major and major >= 22 and chromium)
    report['browser_check'] = {'ready': ready, 'why': f'node {major} and {chromium}' if ready else
                               ('node not on PATH; ' if not node else '') +
                               (f'node {major} lacks a built-in WebSocket (needs 22+); ' if node and (major or 0) < 22 else '') +
                               ('no Chromium or Chrome found (set CHROMIUM=/path)' if not chromium else '')}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('new', help='write a starting .md or .src.html source; never overwrites')
    p.add_argument('source', type=Path)
    p.add_argument('--id', required=True)
    p.add_argument('--purpose', required=True)
    p.add_argument('--title')
    p = commands.add_parser('html', help='assemble a .src.html source into a self-contained, commentable page')
    p.add_argument('source', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--id', help='defaults to the source\'s <!-- briefing: --> comment')
    p.add_argument('--purpose', help='defaults to the source\'s <!-- briefing: --> comment')
    p.add_argument('--no-wall', action='store_true', help='build on the stylesheet\'s own dark ground, without an Omarchy wallpaper')
    p.add_argument('--discard-output-edits', action='store_true', help='rebuild over edits made to the page itself, keeping them in a .bak')
    helps = {'check': 'validate anchors, scaffold leftovers and every local link and fragment',
             'feedback': 'export embedded HTML notes, or a blank Markdown map, as a format-1 envelope',
             'resolve': 'place a returned map (JSON, Copy-map text, or - for stdin) against the current document'}
    for name in ('check', 'feedback', 'resolve'):
        p = commands.add_parser(name, help=helps[name])
        p.add_argument('document', type=Path)
        if name == 'resolve':
            p.add_argument('map', type=Path)
    commands.add_parser('doctor', help='report which commands work on this machine, and why the rest do not')
    args = parser.parse_args()
    try:
        if args.command == 'new':
            result = scaffold(args.source, args.id, args.purpose, args.title)
        elif args.command == 'html':
            result = build(args.source, args.output, args.id, args.purpose, args.no_wall, args.discard_output_edits)
        elif args.command == 'check':
            result = check(args.document)
        elif args.command == 'feedback':
            result = feedback(args.document)
        elif args.command == 'doctor':
            result = doctor()
        else:
            result = resolve(args.document, args.map)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if args.command == 'resolve' and any(c['status'] != 'resolved' for c in result['comments']) else 0
    except (Refusal, OSError, ValueError, subprocess.CalledProcessError) as exc:
        print('brief: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
