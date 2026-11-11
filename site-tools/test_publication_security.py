"""Security regression probes in disposable copies, never in public files."""
from html.parser import HTMLParser
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
from publication_security import inline_json

ROOT = Path(__file__).resolve().parents[1]
class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]; self.text=[]
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
    def handle_data(self, text):
        self.text.append(text)

fixtures = ['</script><script>void 0</script>', '</ScRiPt><img src=x onerror=void(0)>', '<!--<script>comment', '<>& " \' café \u2028']
for value in fixtures:
    data={'title':value}; encoded=inline_json(data)
    parser=Scripts();parser.feed('<script type="application/json">'+encoded+'</script>')
    assert parser.tags==['script'] and json.loads(''.join(parser.text))==data

with tempfile.TemporaryDirectory(prefix='commons-security-test-') as tmp:
    copy=Path(tmp)/'repo'
    shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('__pycache__','.venv','node_modules'))
    docs=copy/'docs'
    def run(name):
        return subprocess.run([sys.executable,str(copy/'site-tools'/name)],cwd=copy,capture_output=True,text=True)
    before={str(p.relative_to(docs)):p.read_bytes() for p in docs.rglob('*') if p.is_file()}
    result=run('build_site.py')
    assert result.returncode!=0 and 'Retired full-site generator' in result.stderr
    assert before=={str(p.relative_to(docs)):p.read_bytes() for p in docs.rglob('*') if p.is_file()}
    for name in ['assets/app.js','assets/style.css']:
        path=docs/name;original=path.read_bytes();path.write_text('/* empty asset probe */\n')
        result=run('validate_release.py')
        assert result.returncode!=0 and 'Shared presentation inventory' in result.stderr
        path.write_bytes(original)
    # Canonical input remains schema-valid, while the browser projection cannot gain markup.
    path=docs/'evidence/evidence.json';data=json.loads(path.read_text())
    data['evidence'][0]['title']=fixtures[0]
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    result=run('build_machine_access.py');assert result.returncode==0,result.stderr
    result=run('validate_release.py');assert result.returncode==0,result.stderr
    from bs4 import BeautifulSoup
    soup=BeautifulSoup((docs/'evidence/index.html').read_text(),'html.parser')
    embedded=json.loads(soup.find('script',id='data').string)
    assert embedded==data
    assert not any((node.string or '').strip()=='void 0' for node in soup.find_all('script'))
print('PASS: safe JSON round-trips, retired build refusal, broken shared-asset rejection, adversarial canonical-input integration.')
