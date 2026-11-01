"""Offline checks for the curated portfolio; never connects to application data."""
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    'README.md', 'LICENSE.md', '.gitignore', '.github/workflows/portfolio.yml',
    'docs/CASE_STUDY.md', 'docs/ARCHITECTURE.md', 'docs/DEMO.md',
    'docs/VERIFICATION.md', 'docs/RIGHTS.md', 'docs/screenshots/overview.png',
    'docs/screenshots/approvals.png', 'samples/README.md',
    'samples/atomic-decision.md', 'samples/concurrency-check.md',
    'licenses/MIT-legacy.txt', 'scripts/check_portfolio.py',
}
tracked = set(subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines())
assert tracked == ALLOWED, f'Unexpected or missing portfolio files: {tracked ^ ALLOWED}'
links = 0
for name in sorted(tracked):
    file = ROOT / name
    assert file.stat().st_size < 1_000_000, f'Unexpected large file: {name}'
    if name.endswith('.png'):
        assert file.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'), name
    if name.endswith('.md'):
        content = file.read_text()
        assert content.count('```') % 2 == 0, f'Unclosed code block: {name}'
        for target in re.findall(r'\]\(([^)]+)\)', content):
            if target.startswith(('https://', 'mailto:', '#')):
                continue
            target = unquote(target.split('#')[0])
            resolved = (file.parent / target).resolve()
            assert resolved.is_relative_to(ROOT) and resolved.is_file(), (name, target)
            links += 1
print(f'PASS: {len(tracked)} allowed files; {links} local links; PNG signatures; Markdown fences')
