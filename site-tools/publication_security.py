"""Publication safety and integrity for the existing static site.

No external access. Canonical JSON is data; it must never become HTML syntax.
HTTP-header-only policies (including frame-ancestors) are not claimed here.
"""
import hashlib
import json
import re
from pathlib import Path

CSP = "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-src 'none'"
REFERRER = 'no-referrer'
JSON_SCRIPT = re.compile(r'(<script\b[^>]*\btype=[\"\']application/(?:ld\+)?json[\"\'][^>]*>)([\s\S]*?)(</script\s*>)', re.I)

def inline_json(value):
    # Escaping < prevents closing-script and script/comment parser transitions.
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')

def embed_dataset(page, dataset):
    pattern = r'(<script\b(?=[^>]*\bid=[\"\']data[\"\'])[^>]*>)[\s\S]*?(</script\s*>)'
    rendered, count = re.subn(pattern, lambda m: m[1] + inline_json(dataset) + m[2], page, flags=re.I)
    if count != 1:
        raise ValueError('Expected one embedded public dataset')
    return rendered

def harden_html(text):
    text = JSON_SCRIPT.sub(lambda m: m[1] + inline_json(json.loads(m[2])) + m[3], text)
    for key, value in [('http-equiv', 'Content-Security-Policy'), ('name', 'referrer')]:
        text = re.sub(r'<meta\b(?=[^>]*\b' + key + r'=[\"\']' + value + r'[\"\'])[^>]*>', '', text, flags=re.I)
    tags = '<meta http-equiv="Content-Security-Policy" content="' + CSP + '"><meta name="referrer" content="' + REFERRER + '">'
    text, count = re.subn(r'(<meta\b[^>]*\bcharset=[\"\'][^\"\']+[\"\'][^>]*>)', lambda m: m[1] + tags, text, count=1, flags=re.I)
    if count != 1:
        raise ValueError('Expected an early charset declaration')
    return text

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def presentation_files(docs):
    return {str(p.relative_to(docs)): sha(p) for p in sorted(docs.rglob('*')) if p.is_file() and p.suffix.lower() in {'.html', '.css', '.js'}}

def finalize(docs):
    docs = Path(docs)
    for path in docs.rglob('*.html'):
        path.write_text(harden_html(path.read_text()))
    machine = docs/'evidence/machine/checksums.json'
    checks = json.loads(machine.read_text())
    checks['files'] = {name: sha(docs/name) for name in checks['files']}
    machine.write_text(json.dumps(checks, ensure_ascii=False, indent=2) + '\n')
    path = docs/'evidence/release-manifest.json'
    manifest = json.loads(path.read_text())
    manifest['machine_checksums_sha256'] = sha(machine)
    manifest['files_sha256'] = {name: sha(docs/'evidence'/name) for name in manifest['files_sha256']}
    for section, root in [('coverage_view', docs/'evidence/coverage'), ('research_paths', docs), ('term_navigation', docs)]:
        manifest[section]['files_sha256'] = {name: sha(root/name) for name in manifest[section]['files_sha256']}
    manifest['presentation_security'] = {'policy_version': '1.0', 'content_security_policy': CSP, 'referrer_policy': REFERRER, 'files_sha256': presentation_files(docs)}
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
