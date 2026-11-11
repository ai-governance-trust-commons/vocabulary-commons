"""Validate candidate projections, preserved baseline, references and exact hashes."""
from pathlib import Path
import argparse,json,hashlib,re,subprocess,csv,io
from collections import Counter
R=Path(__file__).resolve().parents[1];D=R/'docs';M=D/'evidence/machine'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline-ref', default='HEAD', help='Reviewed navigation baseline; use the PR base SHA when reviewing a committed branch')
parser.add_argument('--allow-new-page', action='append', default=[], help='Explicit repository-relative HTML path added by a reviewed presentation change; repeat per page')
parser.add_argument('--allow-navigation-page', action='append', default=[], help='Explicit repository-relative HTML path whose navigation is intentionally updated; repeat per page')
args=parser.parse_args()
def base(p):return subprocess.check_output(['git','show','b4d26d5:'+str(p.relative_to(R))],cwd=R)
d=read(D/'evidence/evidence.json');old=json.loads(base(D/'evidence/evidence.json'));checks=[]
def check(name,ok):
 assert ok,name
 checks.append(name)
check('Founding Markdown, glossary JSON and 35 dataset terms unchanged',base(R/'FOUNDING_GLOSSARY_v1.0.2.md')==(R/'FOUNDING_GLOSSARY_v1.0.2.md').read_bytes() and base(D/'data/glossary.json')==(D/'data/glossary.json').read_bytes() and d['terms']==old['terms'] and len(d['terms'])==35)
check('All four schema files byte-identical',all(base(p)==p.read_bytes() for p in (M/'schemas').glob('*.json')))
check('Two withdrawals unchanged',d['withdrawals']==old['withdrawals'] and {w['id'] for w in d['withdrawals']}=={'EVID-139','EVID-144'})
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
export_rows=list(csv.DictReader(io.StringIO((M/'exports/evidence.csv').read_text(encoding='utf-8-sig'))))
records={r['id']:r for r in d['evidence']}
for row in export_rows:
 cited=json.loads(row['cited_source_ids']);context=json.loads(row['context_source_ids'])
 bundled={s['id'] for s in json.loads(row['sources'])}
 expected=records.get(row['id'],{}).get('source_ids',[])
 check(row['id']+' CSV source roles preserve direct citations and separate context',cited==expected and not set(cited)&set(context) and set(cited)|set(context)==bundled and set(cited)<=set(json.loads(row['source_locations'] or '{}')))
checksums=read(M/'checksums.json');check('All machine checksums match',all(sha(D/k)==v for k,v in checksums['files'].items()))
m=read(D/'evidence/release-manifest.json');check('Manifest counts derived from data',m['evidence_count']==len(d['evidence']) and m['source_count']==len(d['sources']))

from datetime import datetime
check('Manifest generation timestamp refreshed by build',m['generated_at']==m['presentation_updated_at'] and datetime.fromisoformat(m['generated_at'])>=datetime.fromisoformat(d['generated_at']))

check('Manifest evidence payload hashes match',all(sha(D/'evidence'/k)==v for k,v in m['files_sha256'].items()))
check('Machine checksum manifest hash matches',m['machine_checksums_sha256']==sha(M/'checksums.json'))
for section,root in [('coverage_view',D/'evidence/coverage'),('research_paths',D),('term_navigation',D)]:
 check(section+' hashes and dataset identity',m[section]['dataset_version']==d['dataset_version'] and m[section]['dataset_sha256']==sha(D/'evidence/evidence.json') and all(sha(root/k)==v for k,v in m[section]['files_sha256'].items()))
for folder,key in [('records','evidence'),('sources','sources')]:
 for p in (M/folder).glob('*.json'):
  if p.name=='index.json':continue
  b=read(p);check(p.stem+' bundle version/hash',b['dataset_version']==d['dataset_version'] and b['dataset_sha256']==sha(D/'evidence/evidence.json'))
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
from source_inspection import inspection_index, inspection_schema
inspection=read(M/'source-inspection.json')
check('Inspection annotations match reviewed attribution and exact dataset',inspection==inspection_index(d))
check('Inspection annotation schema matches declared contract',read(M/'source-inspection-v1.schema.json')==inspection_schema())
Draft202012Validator(inspection_schema()).validate(inspection)
annotations={e['source_id']:e for e in inspection['sources']}
check('Catalog discovers versioned inspection extension',read(M/'catalog.json')['source_inspection_url'].endswith('/source-inspection.json') and read(M/'catalog.json')['source_inspection_schema_url'].endswith('/source-inspection-v1.schema.json'))
for row in export_rows:
 check(row['id']+' CSV inspection annotations cover direct citations only',json.loads(row['source_inspection'])==[annotations[sid] for sid in records.get(row['id'],{}).get('source_ids',[])])
for row in csv.DictReader(io.StringIO((M/'exports/sources.csv').read_text(encoding='utf-8-sig'))):
 check(row['id']+' source CSV inspection annotation matches',json.loads(row['inspection_annotation'])==annotations[row['id']])
from bs4 import BeautifulSoup
from publication_security import CSP, REFERRER, presentation_files
from publication_views import NAVIGATION, navigation
from publication_views import curation_content
from urllib.parse import urlsplit,unquote
identity=read(D/'publication.json')
identity_files=presentation_files(D)
for name in ['evidence/evidence.json','data/glossary.json','evidence/machine/exports/evidence.csv']:identity_files[name]=sha(D/name)
check('Publication fingerprint and file inventory match',identity['files_sha256']==identity_files and identity['content_fingerprint_sha256']==hashlib.sha256(json.dumps(identity_files,sort_keys=True,separators=(',',':')).encode()).hexdigest())
fallback=BeautifulSoup((D/'evidence/index.html').read_text(),'html.parser')
check('Browser inspection annotations equal versioned extension',json.loads(fallback.select_one('#inspection-data').get_text())==inspection)
check('Inspection filter exposes controlled values', {o.get('value') for o in fallback.select('#inspection-filter option')}=={''}|set(inspection['basis_labels']))
cards=fallback.select('#items > article.evidence-card')
check('Static Library includes exactly all published findings',len(cards)==len(records) and {c['id'] for c in cards}==set(records))
for card in cards:
 record=records[card['id']];text=card.get_text(' ',strip=True)
 check(card['id']+' readable fallback preserves finding and limitations',all(value in text for value in [record['observation'],record['limitations'],record['verification_status'],record['support_assessment']]) and bool(card.select('a[href="machine/records/'+record['id']+'.json"]')))
 check(card['id']+' readable fallback preserves inspection provenance and scope',all(inspection['basis_labels'][annotations[sid]['basis']] in text and annotations[sid]['recorded_scope'] in text and annotations[sid]['basis_note'] in text for sid in record['source_ids']))
check('Static withdrawals preserve both notices without held claims',{n['id'] for n in fallback.select('#withdrawals > article')}=={w['id'] for w in d['withdrawals']})
policy_source,policy_html=curation_content(D)
policy_page=BeautifulSoup((D/'participate/curation/index.html').read_text(),'html.parser')
policy_body=policy_page.select_one('#curation-text')
check('Curation page faithfully renders the current policy source',policy_body is not None and policy_body.get('data-source-sha256')==hashlib.sha256(policy_source).hexdigest() and policy_body.get_text(' ',strip=True)==BeautifulSoup(policy_html,'html.parser').get_text(' ',strip=True))
participate=BeautifulSoup((D/'participate/index.html').read_text(),'html.parser')
check('Participate curation card stays on site',len(participate.select('a.feature[href="curation/"]'))==1)
security=m.get('presentation_security',{})
check('Shared presentation inventory and exact hashes match',security.get('files_sha256')==presentation_files(D))
check('Shared browser policy metadata matches supported policy',security.get('content_security_policy')==CSP and security.get('referrer_policy')==REFERRER)
pages=list(D.rglob('*.html'));broken=[];nav_changed=[]
baseline_pages=set(subprocess.check_output(['git','ls-tree','-r','--name-only',args.baseline_ref,'--','docs'],cwd=R,text=True).splitlines())
baseline_pages={p for p in baseline_pages if p.endswith('.html')}
actual_pages={str(p.relative_to(R)) for p in pages}
allowed_new=set(args.allow_new_page);allowed_nav=set(args.allow_navigation_page)
check('Explicit presentation allowances name existing HTML pages',allowed_new<=actual_pages and allowed_nav<=actual_pages and not allowed_new&baseline_pages)
check('HTML page inventory matches reviewed baseline plus explicit additions',actual_pages==baseline_pages|allowed_new)
prior_manifest=json.loads(subprocess.check_output(['git','show',args.baseline_ref+':docs/evidence/release-manifest.json'],cwd=R))
check('Presentation version preserved',m['presentation_version']==prior_manifest['presentation_version'])
for p in pages:
 soup=BeautifulSoup(p.read_text(),'html.parser')
 nav=soup.find('nav',id='primary-nav')
 expected_nav=BeautifulSoup(navigation(p,D),'html.parser').find('nav')
 check(str(p.relative_to(D))+' shared navigation routes and labels',nav is not None and [(a.get_text(),a.get('href')) for a in nav.find_all('a')]==[(a.get_text(),a.get('href')) for a in expected_nav.find_all('a')])
 policy=soup.find_all('meta',attrs={'http-equiv':re.compile('^Content-Security-Policy$',re.I)})
 referrers=soup.find_all('meta',attrs={'name':'referrer'})
 check(str(p.relative_to(D))+' shared browser policies',len(policy)==1 and policy[0].get('content')==CSP and len(referrers)==1 and referrers[0].get('content')==REFERRER)
 check(str(p.relative_to(D))+' no inline executable code or styles',not soup.find_all('style') and not soup.select('[style]') and all(node.get('src') or node.get('type','').lower() in {'application/json','application/ld+json'} for node in soup.find_all('script')) and not any(any(key.lower().startswith('on') for key in node.attrs) for node in soup.find_all()))
 for node in soup.find_all('script'):
  if node.get('type','').lower() in {'application/json','application/ld+json'}:
   json.loads(node.string or node.get_text())
   check(str(p.relative_to(D))+' inline JSON uses safe text encoding','<' not in (node.string or node.get_text()))
 for node in [*soup.find_all('script',src=True),*soup.find_all('link',rel='stylesheet')]:
  url=node.get('src') or node.get('href');parts=urlsplit(url)
  target=(p.parent/unquote(parts.path)).resolve()
  check(str(p.relative_to(D))+' runtime asset is local and inventoried',not parts.scheme and not parts.netloc and target.is_relative_to(D.resolve()) and str(target.relative_to(D.resolve())) in security['files_sha256'])
 relative=str(p.relative_to(R))
 if relative in baseline_pages and relative not in allowed_nav:
  prior=BeautifulSoup(subprocess.check_output(['git','show',args.baseline_ref+':'+relative],cwd=R),'html.parser')
  if [str(n) for n in soup.find_all('nav')]!=[str(n) for n in prior.find_all('nav')]:nav_changed.append(str(p))
 for node in soup.find_all(['a','script','link']):
  u=node.get('href') or node.get('src') or '';sp=urlsplit(u)
  if u=='https://github.com/ai-governance-trust-commons/vocabulary-commons/blob/main/EDITORIAL_REVIEW.md':
   check('Only an explicitly labeled policy-source link goes to GitHub',p==D/'participate/curation/index.html' and node.has_attr('data-policy-source'))
  if not u or sp.scheme or sp.netloc or u.startswith('#'):continue
  if not (p.parent/unquote(sp.path)).resolve().exists():broken.append((str(p),u))
check(f'All {len(pages)} HTML pages have valid local targets: {broken}',not broken)
check('All page navigation markup unchanged from reviewed baseline',not nav_changed)
print(json.dumps({'passed':len(checks),'dataset_sha256':sha(D/'evidence/evidence.json'),'counts':{k:len(d[k]) for k in ['evidence','sources','cases','terms','relationships','withdrawals']}},indent=2))
