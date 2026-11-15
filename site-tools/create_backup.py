#!/usr/bin/env python3
"""Back up one committed Commons revision, excluding untracked/private files.

Creates a source snapshot, self-contained Git history, hashes and restore notes.
Does not merge, deploy, upload or replace an earlier archive.
"""
import argparse
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--revision', default='HEAD')
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    revision = git('rev-parse', '--verify', a.revision + '^{commit}').decode().strip()
    output = a.output.resolve()
    if output.exists():
        raise SystemExit('Refusing to replace an existing backup')
    output.parent.mkdir(parents=True, exist_ok=True)
    payloads = {}
    with tarfile.open(fileobj=io.BytesIO(git('archive', '--format=tar', revision))) as archive:
        for entry in archive:
            if not entry.isfile():
                if entry.isdir():
                    continue
                raise SystemExit('Review non-regular Git entries before backup')
            payloads['source/' + entry.name] = archive.extractfile(entry).read()
    backup_ref = 'refs/commons-backup/' + revision
    git('update-ref', backup_ref, revision, '0' * 40)
    try:
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp) / 'repository.bundle'
            subprocess.run(['git', 'bundle', 'create', str(bundle), backup_ref], cwd=ROOT, check=True,
                           stdout=subprocess.DEVNULL)
            payloads['repository.bundle'] = bundle.read_bytes()
    finally:
        git('update-ref', '-d', backup_ref, revision)
    data = json.loads(payloads['source/docs/evidence/evidence.json'])
    identity = {'created_at': datetime.now(timezone.utc).isoformat(), 'commit': revision,
                'tree': git('rev-parse', revision + '^{tree}').decode().strip(),
                'dataset_version': data['dataset_version'],
                'counts': {key: len(data[key]) for key in
                           ['evidence', 'sources', 'cases', 'relationships', 'terms', 'withdrawals']},
                'scope': 'Committed repository snapshot and ancestry only. Private research, account settings, credentials, hosted issue/PR discussions and automation state are not included.'}
    payloads['REVISION.json'] = (json.dumps(identity, indent=2) + '\n').encode()
    payloads['RESTORE.md'] = ('''# Commons backup restoration

This is a committed source snapshot, not authorization to publish. Read REVISION.json
to distinguish the deployed baseline from an unapproved review candidate.
Extract into a new empty directory. Verify every entry in SHA256SUMS.json with
Python hashlib.sha256 before use. The checksums show byte consistency, not an
independent signature. source/docs contains the complete static site.

Restore the exact Git commit and its ancestry from the bundled repository:

    git init restored
    git -C restored fetch ../repository.bundle ''' + backup_ref + '''
    git -C restored checkout --detach FETCH_HEAD

The separate source/ tree provides access even without Git. Git history is needed
for the full publication validator. No remote credentials are included.

With Python 3.12, install the pinned dependencies (network access is required
unless they are already available):

    python -m pip install -r site-tools/requirements-lock.txt
    python site-tools/validate_release.py
    python site-tools/build_machine_access.py
    python site-tools/validate_release.py
    python site-tools/test_projection_build.py
    python site-tools/test_publication_security.py
    python site-tools/test_review_remediation.py
    python site-tools/test_inspection_annotations.py
    python site-tools/test_report_archive.py
    python -m playwright install chromium
    python site-tools/validate.py --chromium ''

Run those commands inside restored/. The matching browser and its operating-system
dependencies are separate requirements. Test the restored site before any approved
publication. Hosting settings, branch rules, account access, private reports and
automation configuration must be recovered separately if needed. Retain prior backups.
''').encode()
    hashes = {name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(payloads.items())}
    payloads['SHA256SUMS.json'] = (json.dumps(hashes, indent=2) + '\n').encode()
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, raw in sorted(payloads.items()):
            archive.writestr(name, raw)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert all(hashlib.sha256(archive.read(name)).hexdigest() == value for name, value in hashes.items())
    print(json.dumps({'path': str(output), 'commit': revision,
                      'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                      'entries': len(payloads), 'size_bytes': output.stat().st_size}))

if __name__ == '__main__':
    main()
