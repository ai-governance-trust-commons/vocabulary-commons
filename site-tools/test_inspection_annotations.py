"""Reject unsupported provenance values and stale historical classifications."""
from copy import deepcopy
import json
from pathlib import Path
from jsonschema import Draft202012Validator, ValidationError
from source_inspection import inspection_index, inspection_schema

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/'docs/evidence/evidence.json').read_text())
index = inspection_index(data)
entries = {e['source_id']: e for e in index['sources']}
assert entries['SRC-136']['basis'] == 'relayed'
assert entries['SRC-153']['basis'] == 'mixed'
assert entries['SRC-154']['basis'] == 'relayed'
assert entries['SRC-098']['basis'] == 'abstract_only'
assert entries['SRC-001']['basis'] == 'unspecified'
assert entries['SRC-009']['basis'] == 'unspecified'  # Worker reading does not prove preparing-assistant access.
assert entries['SRC-148']['basis'] == 'direct'
for field in ['status', 'scope', 'review_date']:
    changed = deepcopy(data)
    changed['sources'][0]['verification'][field] += ' changed'
    try:
        inspection_index(changed)
    except ValueError as error:
        assert 'Stale inspection annotation' in str(error)
    else:
        raise AssertionError('Historical ' + field + ' drift was accepted')
changed = deepcopy(data)
changed['sources'].pop()
try:
    inspection_index(changed)
except ValueError as error:
    assert 'one reviewed entry per source' in str(error)
else:
    raise AssertionError('Missing source annotation was accepted')
changed = deepcopy(index)
changed['sources'][0]['basis'] = 'verified'
try:
    Draft202012Validator(inspection_schema()).validate(changed)
except ValidationError:
    pass
else:
    raise AssertionError('Unsupported verification upgrade was accepted')
print('PASS: conservative provenance cases, stale attribution, source coverage and invalid enum rejected.')
