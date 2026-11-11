"""Versioned inspection annotations, separate from the unchanged dataset contract."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = {
    'direct': 'Direct reading recorded for preparing assistant',
    'relayed': 'Relayed inspection report',
    'mixed': 'Direct extract plus relayed full-source report',
    'abstract_only': 'Abstract and metadata only',
    'unspecified': 'Inspection route not established',
}

def inspection_index(data):
    reviewed = json.loads((ROOT/'site-tools/reviews/source-inspection-basis.json').read_text())
    sources = {s['id']: s for s in data['sources']}
    entries = reviewed['sources']
    if len(entries) != len(sources) or {e['source_id'] for e in entries} != set(sources):
        raise ValueError('Inspection annotations require one reviewed entry per source')
    for entry in entries:
        if entry['basis'] not in LABELS:
            raise ValueError('Unknown inspection basis: ' + entry['source_id'])
        verification = sources[entry['source_id']]['verification']
        if any(entry['recorded_' + field] != verification[field]
               for field in ['status', 'scope', 'review_date']):
            raise ValueError('Stale inspection annotation: ' + entry['source_id'])
    return {
        'inspection_contract_version': '1.0',
        'dataset_version': data['dataset_version'],
        'dataset_sha256': hashlib.sha256((ROOT/'docs/evidence/evidence.json').read_bytes()).hexdigest(),
        'classified_at': reviewed['classified_at'],
        'notice': reviewed['notice'],
        'basis_labels': LABELS,
        'sources': entries,
    }

def inspection_schema():
    string = {'type': 'string'}
    def obj(properties):
        return {'type': 'object', 'properties': properties,
                'required': list(properties), 'additionalProperties': False}
    entry = obj({
        'source_id': {'type': 'string', 'pattern': '^SRC-[0-9]{3,}$'},
        'basis': {'enum': list(LABELS)}, 'actors': {'type': 'array', 'items': string},
        **{key: string for key in ['basis_note', 'recorded_status', 'recorded_scope', 'recorded_review_date']},
    })
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema',
            'title': 'Source inspection annotation contract 1.0', **obj({
                'inspection_contract_version': {'const': '1.0'},
                **{key: string for key in ['dataset_version', 'dataset_sha256', 'classified_at', 'notice']},
                'basis_labels': obj({key: {'const': value} for key, value in LABELS.items()}),
                'sources': {'type': 'array', 'items': entry},
            })}
