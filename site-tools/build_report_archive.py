"""Render the separate historical report archive; never modify evidence findings."""
from pathlib import Path
import hashlib, html, json, re
from datetime import date
from markdown_it import MarkdownIt
ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'docs'
OUT = D / 'reports'
md = MarkdownIt('commonmark', {'html': False}).enable('table')
def esc(s): return html.escape(str(s), quote=True)
def render_report(text):
    tokens = md.parse(text)
    # The page owns its h1. Keep the original Markdown bytes and readable hierarchy.
    if any(token.type == 'heading_open' and token.tag == 'h1' for token in tokens):
        for token in tokens:
            if token.type in {'heading_open', 'heading_close'}:
                token.tag = 'h' + str(min(6, int(token.tag[1:]) + 1))
    return md.renderer.render(tokens, md.options, {})

def load():
    data = json.loads((OUT / 'index.json').read_text())
    evidence = {e['id'] for e in json.loads((D/'evidence/evidence.json').read_text())['evidence']}
    seen = set()
    for r in data['reports']:
        date.fromisoformat(r['date'])
        if r['date'] in seen or r['file'] != r['date']+'.md': raise ValueError('Duplicate date or unsafe report path')
        seen.add(r['date'])
        if hashlib.sha256((OUT/r['file']).read_bytes()).hexdigest() != r['sha256']: raise ValueError('Preserved report changed: '+r['date'])
        for link in r['related_evidence']:
            if link['id'] not in evidence or not link['note']: raise ValueError('Unknown evidence or missing relationship explanation')
        for c in r['corrections']:
            date.fromisoformat(c['date'])
            if not c['note']: raise ValueError('Empty correction')
    return data

def build():
    data=load();home=(D/'index.html').read_text()
    header=re.search(r'<header class="site-header">[\s\S]*?</header>',home)[0]
    footer=re.search(r'<footer class="site-footer">[\s\S]*?</footer>',home)[0]
    def relative(match):
        url=match[1]
        return 'href="'+(url if re.match(r'https?://|#',url) else '../'+url)+'"'
    header=re.sub(r'href="([^"]+)"',relative,header).replace(' aria-current="page"','')
    footer=re.sub(r'href="([^"]+)"',relative,footer)
    def page(name,title,body):
        (OUT/name).write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+' | Governance &amp; Trust Commons</title><link rel="stylesheet" href="../assets/style.css"><link rel="stylesheet" href="archive.css"></head><body><a class="skip" href="#content">Skip to content</a>'+header+'<main id="content" class="wrap report-archive"><p><a href="../evidence/">Commons Research Library</a> / <a href="./">High-Signal Report Archive</a></p><h1>'+esc(title)+'</h1><p class="notice">'+esc(data['notice'])+'</p>'+body+'</main>'+footer+'<script defer src="../assets/app.js"></script></body></html>\n')
    rows=[]
    for r in sorted(data['reports'],key=lambda x:x['date'],reverse=True):
        rows.append('<li><h2><a href="'+r['date']+'.html">'+esc(r['date']+' — '+r['title'])+'</a></h2><p>'+esc(r['description'])+'</p><p>'+esc(r['preservation'])+(' <strong>Correction recorded.</strong>' if r['corrections'] else '')+'</p></li>')
        corrections='<section aria-label="Corrections and subsequent notes"><h2>Corrections and subsequent notes</h2>'+(''.join('<p><strong>'+esc(c['date'])+'</strong> — '+esc(c['note'])+'</p>' for c in r['corrections']) or '<p>No later correction recorded in this archive. This is not a claim that all subsequent developments have been checked.</p>')+'</section>'
        related='<h2>Related evidence records</h2><p>These are comparisons, not additional corroboration or a finding that the report has been validated.</p>'+(''.join('<p><a href="../evidence/#'+esc(e['id'])+'">'+esc(e['id'])+'</a> — '+esc(e['note'])+'</p>' for e in r['related_evidence']) or '<p>No related published record linked in this edition.</p>')
        page(r['date']+'.html',r['date']+' — '+r['title'],'<p>'+esc(r['preservation'])+'</p><p><a href="'+r['file']+'" download>Download preserved report (Markdown)</a></p>'+corrections+'<article aria-label="Preserved report">'+render_report((OUT/r['file']).read_text())+'</article>'+('<h2>Repository status reported at the time</h2><p>'+esc(r['repository_status_at_time'])+'</p>' if r.get('repository_status_at_time') else '')+related)
    page('index.html','High-Signal Report Archive','<p>Dated research reports retain their sources, uncertainty and original assessments. Report dates differ from event and disclosure dates. Later corrections are appended visibly; the preserved report is not silently rewritten.</p><p>November 10–13 are reconstructed reading copies; November 14–15 come from complete recorded automation results. This selective archive is not a daily incident inventory. Missing dates do not establish that no report ran.</p><ul class="report-index">'+''.join(rows)+'</ul><h2>Earlier reports</h2><p><a href="earlier-index.html">October 3–November 9: partial historical index</a> — summaries and pointers, not full report transcripts.</p><p><a href="index.json">Archive metadata (JSON)</a> · <a href="../participate/">Suggest a correction</a></p>')
    page('earlier-index.html','Earlier reports — partial index',md.render((OUT/'earlier-index.md').read_text()))
if __name__=='__main__':build()
