"""brief-wall's rolodex: what is in the draw, how a theme that is not installed is fetched,
and how the cache stays under its cap. A local git repository stands in for GitHub, so
nothing here needs the network or vips.

    python3 -m unittest discover -s decision-brief/tests -p 'test_brief_wall.py'
"""
import importlib.machinery, importlib.util, os, random, subprocess, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / 'scripts' / 'brief-wall'
loader = importlib.machinery.SourceFileLoader('brief_wall', str(SCRIPT))
spec = importlib.util.spec_from_loader('brief_wall', loader)
bw = importlib.util.module_from_spec(spec)
loader.exec_module(bw)

COLORS = 'mode = "dark"\nbackground = "#101014"\nforeground = "#e0e0e0"\naccent = "#e0a040"\n'


def sh(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


def make_repo(root, sub='', wallpapers=('one.png', 'two words.png', 'three.jpg')):
    """A theme repository, served over file:// with partial clone allowed, as GitHub does."""
    repo = Path(root) / 'origin'
    base = repo / sub if sub else repo
    (base / 'backgrounds').mkdir(parents=True)
    (base / 'colors.toml').write_text(COLORS)
    for w in wallpapers:
        (base / 'backgrounds' / w).write_bytes(os.urandom(2048))
    (base / 'backgrounds' / 'README.md').write_text('not a wallpaper')
    sh('git', 'init', '-q', cwd=repo)
    sh('git', 'config', 'uploadpack.allowFilter', 'true', cwd=repo)
    sh('git', 'config', 'uploadpack.allowAnySHA1InWant', 'true', cwd=repo)
    sh('git', 'add', '.', cwd=repo)
    sh('git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'theme', cwd=repo)
    return 'file://' + str(repo)


def make_installed(root, name, n=2):
    d = Path(root) / 'themes' / name
    (d / 'backgrounds').mkdir(parents=True)
    (d / 'colors.toml').write_text(COLORS)
    for i in range(n):
        (d / 'backgrounds' / f'{i}.png').write_bytes(b'x')
    return bw.themes([str(Path(root) / 'themes')])


class RolodexTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_cache = bw.CACHE
        bw.CACHE = str(self.root / 'cache')

    def tearDown(self):
        bw.CACHE = self.old_cache
        self.tmp.cleanup()

    def test_the_file_is_the_draw_and_a_hash_takes_a_theme_out(self):
        f = self.root / 'rolodex.txt'
        f.write_text('# header\n'
                     'ours        -                         # installed only\n'
                     'giants      dhh/omarchy-giants-theme  # 135 stars\n'
                     '# nord      -\n'
                     'mono        https://example.org/x.git themes/mono\n')
        pool = bw.rolodex(str(f))
        self.assertEqual(sorted(pool), ['giants', 'mono', 'ours'])
        self.assertEqual(pool['ours'], (None, ''))
        self.assertEqual(pool['giants'], ('https://github.com/dhh/omarchy-giants-theme.git', ''))
        self.assertEqual(pool['mono'], ('https://example.org/x.git', 'themes/mono'))
        self.assertIsNone(bw.rolodex(str(self.root / 'absent.txt')))  # no file: no rolodex, not an empty one

    def test_an_installed_theme_left_off_the_rolodex_is_never_drawn(self):
        make_installed(self.root, 'stock')
        installed = make_installed(self.root, 'ours')
        picks = {bw.draw(random.Random(s), {'ours': (None, '')}, installed)[0]['name'] for s in range(40)}
        self.assertEqual(picks, {'ours'})

    def test_a_fetch_brings_colours_the_list_and_one_wallpaper_only(self):
        url = make_repo(self.root, sub='themes/mono')
        image = bw.fetch('mono', url, 'themes/mono', random.Random(3))
        d = Path(bw.CACHE) / 'mono'
        self.assertEqual((d / 'colors.toml').read_text(), COLORS)
        self.assertEqual(sorted((d / 'wallpapers.txt').read_text().splitlines()),
                         ['one.png', 'three.jpg', 'two words.png'])  # a name with a space survives
        self.assertEqual([p.name for p in (d / 'backgrounds').iterdir()], [Path(image).name])

    def test_a_cached_wallpaper_is_served_when_the_repository_is_gone(self):
        url = make_repo(self.root)
        first = bw.fetch('mono', url, '', random.Random(0))
        for s in range(20):  # every later pick either hits the cache or falls back to it
            self.assertEqual(bw.fetch('mono', 'file:///nowhere/at/all', '', random.Random(s)), first)

    def test_an_unreachable_theme_is_skipped_and_the_draw_moves_on(self):
        url = make_repo(self.root)
        pool = {'gone': ('file:///nowhere/at/all', ''), 'mono': (url, '')}
        warned = []
        for s in range(6):
            theme, image = bw.draw(random.Random(s), pool, {}, warn=warned.append)
            self.assertEqual(theme['name'], 'mono')
            self.assertTrue(os.path.isfile(image))

    def test_nothing_reachable_falls_back_to_an_installed_theme_and_says_so(self):
        installed = make_installed(self.root, 'stock')
        warned = []
        theme, _ = bw.draw(random.Random(1), {'gone': ('file:///nowhere/at/all', '')}, installed, warn=warned.append)
        self.assertEqual(theme['name'], 'stock')
        self.assertTrue(any('installed theme' in w for w in warned))
        with self.assertRaises(bw.Unavailable):
            bw.draw(random.Random(1), {'gone': ('file:///nowhere/at/all', '')}, {}, warn=lambda m: None)

    def test_the_cache_drops_the_wallpaper_used_longest_ago_and_never_the_one_in_hand(self):
        d = Path(bw.CACHE) / 'mono'
        (d / 'backgrounds').mkdir(parents=True)
        (d / 'colors.toml').write_text(COLORS)
        files = []
        for i in range(4):
            p = d / 'backgrounds' / f'{i}.png'
            p.write_bytes(b'x' * 400_000)
            os.utime(p, (1000 + i, 1000 + i))
            files.append(p)
        os.utime(files[0], (9999, 9999))
        total = bw.prune(str(files[1]), cap_mb=1.0)
        self.assertLessEqual(total, 1_000_000 + 400_000)
        self.assertTrue(files[1].exists())   # the one being used, though not the newest
        self.assertTrue(files[0].exists())   # used most recently
        self.assertFalse(files[2].exists())  # the oldest the cap could spare

    def test_the_shipped_rolodex_parses_and_names_each_theme_once(self):
        f = HERE.parent / 'theme-rolodex.txt'
        names = [l.split('#', 1)[0].split()[0] for l in f.read_text().splitlines() if l.split('#', 1)[0].split()]
        self.assertEqual(len(names), len(set(names)))
        pool = bw.rolodex(str(f))
        self.assertGreater(len(pool), 50)
        for name, (url, _) in pool.items():
            self.assertTrue(url is None or url.startswith(('https://', 'git@')), name)


if __name__ == '__main__':
    unittest.main()
