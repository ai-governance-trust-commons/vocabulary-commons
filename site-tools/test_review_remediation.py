"""Ensure normalized hashes cannot hide missing navigation, citations or records."""
import csv
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='commons-review-regression-') as tmp:
    copy=Path(tmp)/'repo'
    shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('__pycache__','.venv','node_modules'))
    docs=copy/'docs'
    def reject(expected):
        subprocess.run([sys.executable,'-c','from pathlib import Path; from publication_security import finalize; finalize(Path("docs"), refresh_views=False)'],cwd=copy,env={**__import__('os').environ,'PYTHONPATH':str(copy/'site-tools')},check=True)
        result=subprocess.run([sys.executable,str(copy/'site-tools/validate_release.py')],cwd=copy,capture_output=True,text=True)
        assert result.returncode!=0 and expected in result.stderr,result.stderr
    page=docs/'resources/index.html';good=page.read_text()
    page.write_text(good.replace('>Resources</a>','>Missing route</a>',1))
    reject('shared navigation routes and labels');page.write_text(good)
    page=docs/'evidence/index.html';good=page.read_text()
    page.write_text(good.replace('id="EVID-058"','id="MISSING-058"',1))
    reject('Static Library includes exactly');page.write_text(good)
    path=docs/'evidence/machine/exports/evidence.csv';good=path.read_bytes()
    rows=list(csv.DictReader(io.StringIO(good.decode('utf-8-sig'))));row=next(r for r in rows if r['id']=='EVID-005')
    row['cited_source_ids']=json.dumps(['SRC-005','SRC-006','SRC-007'])
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    path.write_text('\ufeff'+out.getvalue())
    reject('CSV source roles preserve direct citations');path.write_bytes(good)
print('PASS: resealed missing navigation, missing static record and false direct-citation role rejected.')
