#!/usr/bin/env python3
"""Read-only example consumer. Standard library only; never executes source text.

Default: fetch the public machine catalog and one record. --root permits an
offline test against a local docs/ directory. This example checks checksums
and essential interpretation context; it is not a full JSON Schema validator.
"""
import argparse,hashlib,json,re
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlsplit

HOST='https://ai-governance-trust-commons.github.io/vocabulary-commons/'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('record_id');p.add_argument('--root',type=Path);args=p.parse_args()
 if not re.fullmatch(r'EVID-[0-9]{3,}',args.record_id):raise ValueError('Use a public EVID identifier')
 cache={}
 def fetch(url):
  if not url.startswith(HOST) or urlsplit(url).query or urlsplit(url).fragment:raise ValueError('Unexpected public resource URL')
  rel=url[len(HOST):]
  if url in cache:return cache[url]
  if args.root:
   root=args.root.resolve();path=(root/rel).resolve();path.relative_to(root);data=path.read_bytes()
  else:
   with urlopen(Request(url,headers={'User-Agent':'Commons-Example-Research-Client/1.0'}),timeout=30) as response:data=response.read()
  cache[url]=data;return data
 catalog_url=HOST+'evidence/machine/catalog.json';catalog=json.loads(fetch(catalog_url))
 manifest=json.loads(fetch(catalog['checksums_url']))
 def checked(url):
  raw=fetch(url);expected=manifest['files'].get(url[len(HOST):])
  if not expected or hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Checksum mismatch or missing manifest entry; do not mix releases')
  return json.loads(raw)
 checked(catalog_url)
 index=checked(catalog['record_index_url'])
 entry=next((r for r in index['records'] if r['id']==args.record_id),None)
 if not entry:raise ValueError('Identifier is absent from the public index')
 record=checked(entry['url'])
 if record['dataset_sha256']!=catalog['dataset_sha256'] or record['dataset_version']!=catalog['dataset_version']:raise ValueError('Mixed dataset versions')
 if record['status']=='temporarily_withdrawn':
  if record['evidence'] is not None or record['sources']:raise ValueError('Withdrawal improperly includes held claim material')
  print(json.dumps({'id':record['id'],'status':record['status'],'withdrawal':record['withdrawal']},ensure_ascii=False,indent=2));return
 finding=record['evidence']
 for key in ['observation','limitations','support_assessment','verification_status','source_locations','publication_record']:
  if not finding.get(key):raise ValueError('Missing interpretation context: '+key)
 if not record['sources']:raise ValueError('Source context missing')
 print(json.dumps({'id':record['id'],'status':record['status'],'source_reported_finding':finding['observation'],'limitations':finding['limitations'],'commons_interpretation':finding['support_assessment'],'independent_verification':finding['verification_status'],'individual_human_review':finding['publication_record']['individual_human_review'],'source_citations':[{'id':s['id'],'title':s['title'],'url':s['url'],'inspection_scope':s['verification']['scope']} for s in record['sources']],'relationship_explanations':[r['explanation'] for r in record['relationships']],'rights_url':record['rights_url'],'notice':record['notice']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
