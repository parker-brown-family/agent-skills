"""Check actual review-page geometry without changing the reader's document."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import brief

with tempfile.TemporaryDirectory(prefix='brief-exposure-') as directory:
    page = Path(directory) / 'exposure.html'
    source = ROOT.parent / 'docs/plans/brief-attention-rail/07-native-reading.src.html'
    brief.build(source, page, None, None, no_wall=True)
    env = {**os.environ, 'BRIEF_EXPOSURE_QA': '1', 'BRIEF_QA_DIR': '/tmp/brief-exposure-qa'}
    subprocess.run(['node', str(ROOT / 'tests/browser.mjs'), str(page)], env=env, check=True, timeout=120)
