"""Stage an archived report JSON for review; no network, merge or deployment."""
import argparse, hashlib, json
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def ingest(payload, out):
    day=payload['date'];date.fromisoformat(day)
    if day != date.fromisoformat(day).isoformat(): raise ValueError('Use ISO date')
    for key in ['title','description','preservation','markdown']:
        if not isinstance(payload[key],str) or not payload[key].strip(): raise ValueError('Missing '+key)
    raw=payload['markdown'].encode();digest=hashlib.sha256(raw).hexdigest()
    index=out/'index.json';data=json.loads(index.read_text())
    for old in data['reports']:
        if old['date']==day:
            if old['sha256']==digest and (out/old['file']).read_bytes()==raw: return 'Already preserved; no change'
            raise ValueError('Date already preserved: append a dated correction to index.json; do not overwrite')
    path=out/(day+'.md')
    if path.exists():raise ValueError('Unindexed file exists; review before import')
    record={k:payload[k] for k in ['date','title','description','preservation']}
    record.update(file=path.name,sha256=digest,related_evidence=[],corrections=[])
    # Exclusive creation protects preserved originals; build validates related links separately.
    with path.open('xb') as f:f.write(raw)
    data['reports'].append(record)
    temp=index.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');temp.replace(index)
    return 'Staged for review; run supported build and validation'
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('capture',type=Path);a=p.parse_args()
    print(ingest(json.loads(a.capture.read_text()),ROOT/'docs/reports'))
