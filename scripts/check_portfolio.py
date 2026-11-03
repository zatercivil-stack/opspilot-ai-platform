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
    'samples/review_policy.py', 'docs/PROCESS_DESIGN.md', 'docs/PILOT_MEASUREMENTS.csv',
    'docs/INTEGRATION.md', 'docs/media/opspilot-demo.webm',
    'docs/screenshots/request.png', 'docs/screenshots/document.png',
    'docs/screenshots/documents.png', 'docs/screenshots/crm.png',
    'evaluation/README.md', 'evaluation/requests.jsonl', 'evaluation/invoices.jsonl',
    'evaluation/reports/local.json', 'evaluation/reports/local-baseline.json',
}
tracked = set(subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines())
assert tracked == ALLOWED, f'Unexpected or missing portfolio files: {tracked ^ ALLOWED}'
links = 0
for name in sorted(tracked):
    file = ROOT / name
    limit = 25_000_000 if name.endswith('.webm') else 1_000_000
    assert file.stat().st_size < limit, f'Unexpected large file: {name}'
    if name.endswith('.webm'):
        assert file.read_bytes().startswith(bytes.fromhex('1a45dfa3')), name
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


# Validate the declared dataset hashes and totals, not just JSON syntax.
import hashlib
import json
report = json.loads((ROOT / 'evaluation/reports/local.json').read_text())
for filename, expected in report['dataset_sha256'].items():
    assert filename in {'requests.jsonl', 'invoices.jsonl'}
    assert hashlib.sha256((ROOT / 'evaluation' / filename).read_bytes()).hexdigest() == expected
assert len(report['requests']) == report['request_summary']['count'] == 60
assert len(report['invoices']) == report['invoice_summary']['count'] == 12
assert report['mode'] == 'local'

print(f'PASS: {len(tracked)} allowed files; {links} local links; image/video signatures; evaluation hashes and totals')
