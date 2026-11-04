"""Validate candidate projections, preserved baseline, references and exact hashes."""
from pathlib import Path
import json,hashlib,re,subprocess,csv,io
from collections import Counter
R=Path(__file__).resolve().parents[1];D=R/'docs';M=D/'evidence/machine'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def base(p):return subprocess.check_output(['git','show','b4d26d5:'+str(p.relative_to(R))],cwd=R)
d=read(D/'evidence/evidence.json');old=json.loads(base(D/'evidence/evidence.json'));checks=[]
def check(name,ok):
 assert ok,name
 checks.append(name)
check('Founding Markdown, glossary JSON and 35 dataset terms unchanged',base(R/'FOUNDING_GLOSSARY_v1.0.2.md')==(R/'FOUNDING_GLOSSARY_v1.0.2.md').read_bytes() and base(D/'data/glossary.json')==(D/'data/glossary.json').read_bytes() and d['terms']==old['terms'] and len(d['terms'])==35)
check('All four schema files byte-identical',all(base(p)==p.read_bytes() for p in (M/'schemas').glob('*.json')))
check('Two withdrawals unchanged',d['withdrawals']==old['withdrawals'] and {w['id'] for w in d['withdrawals']}=={'EVID-139','EVID-144'})
for k in ['evidence','sources','cases']:
 lookup={r['id']:r for r in d[k]};check('All baseline '+k+' preserved',all(lookup[x['id']]==x for x in old[k]))
ids=[x['id'] for k in ['evidence','sources','cases','terms','relationships'] for x in d[k]]
check('Unique stable identifiers',len(ids)==len(set(ids)))
ss={s['id'] for s in d['sources']};cc={c['id'] for c in d['cases']}
check('Complete source and case references',all(e['case_id'] in cc and set(e['source_ids'])<=ss and set(e['source_ids'])<=set(e['source_locations']) for e in d['evidence']))
check('Relationship endpoints resolve',all(r['from_id'] in ids and r['to_id'] in ids for r in d['relationships']))
check('No duplicate source URLs',len({s['url'].rstrip('/') for s in d['sources']})==len(ss))
check('Retired relationships absent',not {'REL-283','REL-366'}&{r['id'] for r in d['relationships']})
check('Four relationships qualify',all(next(x for x in d['relationships'] if x['id']==rid)['relationship_type']=='qualifies' for rid in ['REL-092','REL-127','REL-144','REL-330']))
embedded=re.search(r'<script type="application/json" id="data">(.*?)</script>',(D/'evidence/index.html').read_text(),re.S)
check('Browser embedded dataset equals canonical JSON',json.loads(embedded[1])==d)
checksums=read(M/'checksums.json');check('All machine checksums match',all(sha(D/k)==v for k,v in checksums['files'].items()))
m=read(D/'evidence/release-manifest.json');check('Manifest counts derived from data',m['evidence_count']==len(d['evidence'])==192 and m['source_count']==len(d['sources'])==155)
check('Manifest evidence payload hashes match',all(sha(D/'evidence'/k)==v for k,v in m['files_sha256'].items()))
check('Machine checksum manifest hash matches',m['machine_checksums_sha256']==sha(M/'checksums.json'))
for section,root in [('coverage_view',D/'evidence/coverage'),('research_paths',D),('term_navigation',D)]:
 check(section+' hashes and dataset identity',m[section]['dataset_version']=='0.5.6' and m[section]['dataset_sha256']==sha(D/'evidence/evidence.json') and all(sha(root/k)==v for k,v in m[section]['files_sha256'].items()))
for folder,key in [('records','evidence'),('sources','sources')]:
 for p in (M/folder).glob('*.json'):
  if p.name=='index.json':continue
  b=read(p);check(p.stem+' bundle version/hash',b['dataset_version']=='0.5.6' and b['dataset_sha256']==sha(D/'evidence/evidence.json'))
  if folder=='records' and b['status']=='temporarily_withdrawn':check(p.stem+' is tombstone only',b['evidence'] is None and not b['sources'] and not b['relationships'])
for name in ['evidence','sources']:
 rows=list(csv.DictReader(io.StringIO((M/'exports'/f'{name}.csv').read_text(encoding='utf-8-sig'))))
 check(name+' CSV count',len(rows)==len(d[name])+(len(d['withdrawals']) if name=='evidence' else 0))
from jsonschema import Draft202012Validator
Draft202012Validator(read(M/'schemas/dataset-v1.schema.json')).validate(d)
Draft202012Validator(read(M/'schemas/glossary-v1.schema.json')).validate(read(D/'data/glossary.json'))
for folder,schema in [('records','record-bundle-v1.schema.json'),('sources','source-bundle-v1.schema.json')]:
 v=Draft202012Validator(read(M/'schemas'/schema))
 for p in (M/folder).glob('*.json'):
  if p.name!='index.json':v.validate(read(p))
check('Dataset, glossary and all bundles validate against unchanged JSON schemas',True)
print(json.dumps({'passed':len(checks),'dataset_sha256':sha(D/'evidence/evidence.json'),'counts':{k:len(d[k]) for k in ['evidence','sources','cases','terms','relationships','withdrawals']}},indent=2))
