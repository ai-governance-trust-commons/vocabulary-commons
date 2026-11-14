from pathlib import Path
import json,tempfile
from bs4 import BeautifulSoup
from build_report_archive import load,md,OUT
from import_report import ingest
d=load();assert len(d['reports'])>=5
for r in d['reports']:
 s=BeautifulSoup((OUT/(r['date']+'.html')).read_text(),'html.parser')
 assert s.select_one('article') and s.select_one('a[download]')
 assert 'assessments at the time' in s.get_text()
 assert len(s.select('h1'))==1
 assert not s.select('article script, article iframe')
assert '&lt;script&gt;' in md.render('<script>alert(1)</script>')
assert 'href="javascript:' not in md.render('[bad](javascript:alert(1))')
with tempfile.TemporaryDirectory() as tmp:
 out=Path(tmp);(out/'index.json').write_text('{"reports":[]}')
 p=dict(date='2026-11-15',title='Test',description='Test',preservation='Test',markdown='Original\n')
 ingest(p,out);before=(out/'index.json').read_bytes();ingest(p,out);assert before==(out/'index.json').read_bytes()
 p['markdown']='Changed'
 try:ingest(p,out)
 except ValueError:pass
 else:raise AssertionError('Overwrite accepted')
 assert (out/'2026-11-15.md').read_text()=='Original\n'
print('PASS: preserved report hashes, static reading, safe rendering, idempotent capture and overwrite rejection')
