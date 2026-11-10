"""Loopback review of one explicitly selected HTML file. No directory or path API."""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import time
import urllib.request
import urllib.error
from urllib.parse import urlsplit

import reading

LIMIT = 1024 * 1024


def backup(path, before):
    state = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state'))
    if not state.is_absolute():
        state = Path.home() / '.local/state'
    directory = state / 'briefing/backups' / hashlib.sha256(os.fsencode(path)).hexdigest()[:24]
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = directory / (str(time.time_ns()) + '.html')
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(before)
        stream.flush()
        os.fsync(stream.fileno())
    for old in sorted(directory.glob('*.html'))[:-8]:
        old.unlink()


class ReviewServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, path, api, port=0):
        if type(port) is not int or not 0 <= port <= 65535:
            raise reading.ReadingError('review port must be between 0 and 65535')
        self.path = Path(os.path.abspath(path))
        self.api = api
        if reading.fcntl is None or not hasattr(os, 'O_NOFOLLOW'):
            raise reading.ReadingError('original-file review saving needs POSIX file locks')
        reading.checked_file(self.path)
        text, meta, revision, _, _ = api.inspect(self.path)
        if self.path.suffix != '.html' or revision != meta['revision']:
            raise reading.ReadingError('review needs a built, unchanged HTML brief')
        # A server writes existing explicit data regions only.
        api.island(text, 'report-reading')
        reading.read_record(text, api)
        api.notes(text)
        self.document, self.revision = meta['id'], revision
        self.route = '/review/' + secrets.token_urlsafe(32)
        super().__init__(('127.0.0.1', port), Handler)
        self.origin = 'http://127.0.0.1:' + str(self.server_port)
        self.url = self.origin + self.route

    def current(self):
        reading.checked_file(self.path)
        text, meta, revision, _, _ = self.api.inspect(self.path)
        if meta['id'] != self.document or revision != self.revision or meta['revision'] != revision:
            raise reading.ReadingError('content changed; restart review for this version')
        return text


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass  # Never put the session capability in request logs.

    def respond(self, status, data, mime='application/json'):
        body = data.encode('utf-8') if isinstance(data, str) else json.dumps(data, allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src data:; media-src data:; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def allowed(self, post=False):
        host = self.server.origin.removeprefix('http://')
        if self.headers.get_all('Host') != [host]:
            self.respond(403, {'state': 'failed', 'reason': 'wrong review host'})
            return False
        if post and self.headers.get_all('Origin') != [self.server.origin]:
            self.respond(403, {'state': 'failed', 'reason': 'wrong review origin'})
            return False
        if not post and self.headers.get('Origin') not in (None, self.server.origin):
            self.respond(403, {'state': 'failed', 'reason': 'wrong review origin'})
            return False
        return True

    def do_GET(self):
        if not self.allowed():
            return
        if self.path != self.server.route:
            self.respond(404, {'state': 'failed', 'reason': 'not this review document'})
            return
        try:
            with reading.review_lock(self.server.path):
                text = self.server.current()
            config = {'save': self.server.route + '/save', 'document': self.server.document,
                      'revision': self.server.revision}
            inject = '<script data-review-connection>window.BRIEF_REVIEW=Object.freeze(' + self.server.api.encode(config) + ');</script>'
            text, n = re.subn(r'(<head\b[^>]*>)', lambda m: m[0] + inject, text, count=1, flags=re.I)
            if n != 1:
                raise reading.ReadingError('document has no head for the review adapter')
            self.respond(200, text, 'text/html')
        except (OSError, ValueError) as exc:
            self.respond(409, {'state': 'pending', 'reason': str(exc)})

    def do_POST(self):
        if not self.allowed(post=True):
            return
        if self.path != self.server.route + '/save':
            self.respond(404, {'state': 'failed', 'reason': 'not this review document'})
            return
        lengths = self.headers.get_all('Content-Length') or []
        if self.headers.get('Transfer-Encoding') or len(lengths) != 1 or not lengths[0].isdigit():
            self.respond(411, {'state': 'failed', 'reason': 'one content length is required'})
            return
        if len(lengths[0]) > 10:
            self.respond(413, {'state': 'failed', 'reason': 'review request exceeds 1 MiB'})
            return
        length = int(lengths[0])
        if length > LIMIT:
            self.respond(413, {'state': 'failed', 'reason': 'review request exceeds 1 MiB'})
            return
        if self.headers.get_all('Content-Type') != ['application/json']:
            self.respond(415, {'state': 'failed', 'reason': 'application/json is required'})
            return
        self.connection.settimeout(10)
        try:
            def unique(pairs):
                result = {}
                for key, value in pairs:
                    if key in result:
                        raise reading.ReadingError('duplicate JSON field')
                    result[key] = value
                return result
            def invalid(_value):
                raise reading.ReadingError('nonfinite JSON number')
            request = json.loads(self.rfile.read(length), object_pairs_hook=unique, parse_constant=invalid)
            if not isinstance(request, dict) or set(request) != {'format', 'reading', 'note_edits'} or type(request['format']) is not int or request['format'] != 1:
                raise reading.ReadingError('unsupported checkpoint format')
            with reading.review_lock(self.server.path):
                original = self.server.current()
                changed, acknowledged = reading.plan_reading_write(original, request['reading'], self.server.api)
                changed = reading.plan_note_edits(changed, request['note_edits'], self.server.api)
                _, meta = self.server.api.island(changed, 'brief-meta')
                if self.server.api.content_revision(changed, meta['id'], meta['purpose']) != self.server.revision:
                    raise reading.ReadingError('review save changed authored content')
                if changed != original:
                    backup(self.server.path, original.encode('utf-8'))
                    self.server.api.atomic(self.server.path, changed, original.encode('utf-8'))
                    if self.server.path.read_bytes() != changed.encode('utf-8'):
                        raise reading.ReadingError('written file did not read back; checkpoint remains pending')
            self.respond(200, {'state': 'saved', 'acknowledged': acknowledged, 'file_revision': self.server.revision})
        except (OSError, ValueError, RecursionError) as exc:
            self.respond(409, {'state': 'pending', 'reason': str(exc)})


def persistent_server(path, api, port=0):
    """Keep a file's browser origin across CLI restarts so pending data is reachable."""
    if port:
        return ReviewServer(path, api, port)
    path = Path(os.path.abspath(path))
    state = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state'))
    if not state.is_absolute():
        state = Path.home() / '.local/state'
    directory = state / 'briefing/review-ports'
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = directory / (hashlib.sha256(os.fsencode(path)).hexdigest() + '.json')
    with reading.review_lock(path):
        previous = None
        if target.exists():
            previous = target.read_bytes()
            info = json.loads(previous)
            if set(info) != {'path', 'port'} or info['path'] != str(path) or type(info['port']) is not int or not 1 <= info['port'] <= 65535:
                raise reading.ReadingError('invalid remembered review origin')
            port = info['port']
        # A busy remembered port is an explicit error. Changing origin silently
        # would strand the browser's unacknowledged localStorage checkpoints.
        server = ReviewServer(path, api, port)
        try:
            api.atomic(target, json.dumps({'path': str(path), 'port': server.server_port}), previous)
        except Exception:
            server.server_close()
            raise
    return server


def session_file(path):
    state = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state'))
    if not state.is_absolute():
        state = Path.home() / '.local/state'
    directory = state / 'briefing/review-sessions'
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    return directory / (hashlib.sha256(os.fsencode(Path(os.path.abspath(path)))).hexdigest() + '.json')


def live_session(path, api):
    """Return a verified current connection, never a stale or non-loopback URL."""
    try:
        target = session_file(path)
        reading.checked_file(target)
        info = json.loads(target.read_bytes())
        _, meta, revision, _, _ = api.inspect(path)
        if (set(info) != {'path', 'url', 'document', 'revision'} or
                info['path'] != str(Path(os.path.abspath(path))) or
                info['document'] != meta['id'] or info['revision'] != revision or revision != meta['revision']):
            return None
        url = urlsplit(info['url'])
        if (url.scheme != 'http' or url.hostname != '127.0.0.1' or not url.port or
                url.netloc != '127.0.0.1:' + str(url.port) or url.query or url.fragment or
                not re.fullmatch(r'/review/[A-Za-z0-9_-]{43}', url.path)):
            return None
        # No redirects or environment proxy: this checks only the remembered local server.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *_args, **_kwargs):
                return None
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        with opener.open(info['url'], timeout=1) as response:
            text = response.read(32 * 1024 * 1024 + 1).decode('utf-8')
            if len(text) > 32 * 1024 * 1024 or response.status != 200:
                return None
            _, served = api.island(text, 'brief-meta')
            if served['id'] != meta['id'] or served['revision'] != revision or 'data-review-connection' not in text:
                return None
        return info
    except (OSError, ValueError, KeyError, TypeError, urllib.error.URLError):
        return None


def review(path, *, open_browser=True, api=None):
    """Start/reuse a per-file user service, then open its connected browser page."""
    if api is None:
        import brief as api
    path = Path(os.path.abspath(path))
    reading.checked_file(path)
    target = session_file(path)
    unit = 'brief-review-' + target.stem[:24] + '.service'
    with reading.review_lock(target):
        info = live_session(path, api)
        if info is None:
            loaded = subprocess.run(['systemctl', '--user', 'show', '--property=LoadState', '--value', unit],
                                    capture_output=True, text=True)
            if loaded.returncode == 0 and loaded.stdout.strip() == 'loaded':
                command = ['systemctl', '--user', 'restart', unit]
            else:
                command = ['systemd-run', '--user', '--unit=' + unit, '--collect',
                           '--property=Restart=on-failure', '--property=MemoryMax=256M',
                           '--property=CPUWeight=20', sys.executable,
                           str(Path(__file__).with_name('brief.py').resolve()), 'serve', str(path)]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode:
                raise reading.ReadingError('Could not start browser saving: ' + result.stderr.strip())
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                info = live_session(path, api)
                if info is not None:
                    break
                time.sleep(0.1)
            if info is None:
                raise reading.ReadingError('Browser saving did not start; inspect journalctl --user -u ' + unit)
    if open_browser:
        opened = subprocess.run(['xdg-open', info['url']], capture_output=True, text=True)
        if opened.returncode:
            raise reading.ReadingError('Browser could not open; copy this URL into Chrome: ' + info['url'])
    return info


def serve_review(path, *, port=0, api=None):
    if api is None:
        import brief as api
    server = persistent_server(path, api, port)
    target = session_file(path)
    target.touch(mode=0o600, exist_ok=True)
    reading.checked_file(target)
    os.chmod(target, 0o600)
    api.atomic(target, json.dumps({'path': str(server.path), 'url': server.url,
                                  'document': server.document, 'revision': server.revision}), target.read_bytes())
    print(json.dumps({'url': server.url, 'document': server.document, 'revision': server.revision}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
