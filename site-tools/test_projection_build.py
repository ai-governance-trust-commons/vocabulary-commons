"""Regression test: a no-content evidence rebuild must preserve reviewed pages."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
from publication_security import finalize

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='commons-build-test-') as tmp:
    copy = Path(tmp)/'repo'
    shutil.copytree(root, copy, ignore=shutil.ignore_patterns('__pycache__', '.venv', 'node_modules'))
    docs = copy/'docs'
    before = {str(p.relative_to(docs)):p.read_bytes() for p in docs.rglob('*') if p.is_file()}
    manifest = json.loads(before['evidence/release-manifest.json'])
    for run in range(2):
        subprocess.run([sys.executable, str(copy/'site-tools/build_machine_access.py')], check=True, capture_output=True)
        after = {str(p.relative_to(docs)):p.read_bytes() for p in docs.rglob('*') if p.is_file()}
        assert before.keys() == after.keys(), 'Build added or removed public files'
        changes = {p for p in before if before[p] != after[p]}
        allowed = {'evidence/machine/catalog.json', 'evidence/machine/checksums.json', 'evidence/release-manifest.json'}
        assert changes <= allowed, f'Unrelated rebuild drift: {changes-allowed}'
        assert json.loads(after['evidence/release-manifest.json'])['presentation_version'] == manifest['presentation_version']
        subprocess.run([sys.executable, str(copy/'site-tools/validate_release.py')], check=True, capture_output=True)
    # Ensure the checks reject regressions, rather than merely accepting today's output.
    target = docs/'evidence/release-manifest.json'
    good = target.read_bytes()
    bad = json.loads(good);bad['presentation_version']='0.0.0'
    target.write_text(json.dumps(bad))
    result = subprocess.run([sys.executable, str(copy/'site-tools/validate_release.py')], capture_output=True, text=True)
    assert result.returncode != 0 and 'Presentation version preserved' in result.stderr
    target.write_bytes(good)
    # Presentation exceptions are explicit and cannot hide unlisted additions.
    extra = docs/'presentation-test.html'
    extra.write_bytes((docs/'index.html').read_bytes())
    finalize(docs)  # Keep integrity metadata valid while probing inventory allowances.
    command = [sys.executable, str(copy/'site-tools/validate_release.py')]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0 and 'HTML page inventory' in result.stderr
    subprocess.run(command + ['--allow-new-page', 'docs/presentation-test.html'], check=True, capture_output=True)
    result = subprocess.run(command + ['--allow-new-page', 'docs/missing.html'], capture_output=True, text=True)
    assert result.returncode != 0 and 'allowances name existing HTML pages' in result.stderr
    extra.unlink()
    finalize(docs)
    page = docs/'resources/index.html'
    good = page.read_text()
    page.write_text(good.replace('<nav ', '<nav data-regression-test="changed" ', 1))
    finalize(docs)  # A refreshed hash must not bypass the separate navigation guard.
    result = subprocess.run([sys.executable, str(copy/'site-tools/validate_release.py')], capture_output=True, text=True)
    assert result.returncode != 0 and 'navigation markup unchanged' in result.stderr
    subprocess.run(command + ['--allow-navigation-page', 'docs/resources/index.html'], check=True, capture_output=True)
print('PASS: two builds preserve all public content; version and navigation regressions rejected.')
