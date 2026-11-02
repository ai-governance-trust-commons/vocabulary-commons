#!/usr/bin/env python3
"""Derive coverage from published evidence only; never infer validation or independence."""
from pathlib import Path
import json,re,html,hashlib
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs';OUT=D/'evidence/coverage'
HOST='https://ai-governance-trust-commons.github.io/vocabulary-commons/'
PRESENTATION='0.5.4'

def derive(d):
    ev={e['id']:e for e in d['evidence']};ss={s['id']:s for s in d['sources']};terms={t['id']:t for t in d['terms']}
    links={t:{} for t in terms};linked=set()
    for r in d['relationships']:
        if r['from_id'] not in ev or r['to_id'] not in terms:continue
        links[r['to_id']].setdefault(r['relationship_type'],set()).add(r['from_id']);linked.add(r['from_id'])
    rows=[]
    for tid,t in terms.items():
        groups=links[tid];ids=set().union(*groups.values()) if groups else set()
        source_ids={sid for eid in ids for sid in ev[eid]['source_ids']};families={ss[sid]['independence_group'] for sid in source_ids if ss[sid].get('independence_group')}
        unknown=sorted(sid for sid in source_ids if not ss[sid].get('independence_group'))
        q=set().union(*(v for k,v in groups.items() if k=='qualifies')) if 'qualifies' in groups else set()
        challenge=set().union(*(v for k,v in groups.items() if k.casefold().startswith('challenges'))) if any(k.casefold().startswith('challenges') for k in groups) else set()
        rows.append(dict(id=tid,name=t['name'],finding_ids=sorted(ids),finding_count=len(ids),source_ids=sorted(source_ids),recorded_family_ids=sorted(families),recorded_family_count=len(families),sources_without_family=unknown,qualifying_finding_ids=sorted(q),challenging_finding_ids=sorted(challenge),relationships={k:sorted(v) for k,v in sorted(groups.items())}))
    return dict(dataset_version=d['dataset_version'],terms=sorted(rows,key=lambda x:x['name'].casefold()),unmatched_finding_ids=sorted(set(ev)-linked),counts=dict(terms=len(terms),terms_with_links=sum(bool(r['finding_count']) for r in rows),terms_without_links=sum(not r['finding_count'] for r in rows),terms_with_one_recorded_family=sum(r['recorded_family_count']==1 for r in rows),public_findings=len(ev),findings_with_term_links=len(linked),findings_without_term_links=len(ev)-len(linked),withdrawal_notices=len(d['withdrawals'])))

def build():
    raw=(D/'evidence/evidence.json').read_bytes();d=json.loads(raw);c=derive(d);OUT.mkdir(parents=True,exist_ok=True)
    c.update(format_version='1.0',coverage_presentation_version=PRESENTATION,dataset_sha256=hashlib.sha256(raw).hexdigest(),basis='Explicit evidence-to-term relationships in the current published dataset. Withdrawals excluded. Counts describe recorded curation, not truth, completeness or independence.',family_method='Distinct recorded independence_group values across all sources cited by each term’s linked findings. Missing groups are disclosed separately; source-dependency relationships may identify further dependence.',source_dataset_url=HOST+'evidence/evidence.json')
    (OUT/'coverage.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
    esc=lambda x:html.escape(str(x),quote=True)
    glossary=json.loads((D/'data/glossary.json').read_text())
    slugs={t['term']:t['slug'] for t in glossary['terms']}
    termnames={t['id']:t['name'] for t in d['terms']}
    route=lambda tid:slugs[termnames[tid]]
    query=lambda **kw:'../?'+urlencode(kw)
    cards=[]
    for r in c['terms']:
        n=r['finding_count'];f=r['recorded_family_count'];q=len(r['qualifying_finding_ids']);ch=len(r['challenging_finding_ids'])
        if not n:note='No published evidence relationship is recorded. This is a curation gap, not evidence that no relevant research exists.'
        elif f==1:note='All linked findings cite one recorded source family. Inspect versions and dependencies before treating findings as separate corroboration.'
        else:note='Recorded families help describe breadth. Different family labels do not establish independent corroboration.'
        breakdown=''.join('<li><a href="'+esc(query(term=r['id'],relation=k))+'">'+esc(k.capitalize())+' <span>'+str(len(ids))+'</span></a></li>' for k,ids in r['relationships'].items())
        unknown=('<p>Family metadata is absent for '+str(len(r['sources_without_family']))+' cited sources.</p>') if r['sources_without_family'] else ''
        badge='No linked findings' if not n else 'One recorded family' if f==1 else 'Multiple recorded families'
        cards.append('<article class="coverage-card" id="'+esc(r['id'])+'" data-name="'+esc(r['name'].casefold())+'" data-count="'+str(n)+'" data-families="'+str(f)+'" data-qualifies="'+str(q)+'" data-challenges="'+str(ch)+'"><p class="coverage-label">'+badge+'</p><h3><a href="../../terms/'+route(r['id'])+'/">'+esc(r['name'])+'</a></h3><dl class="coverage-metrics"><div><dt>Linked findings</dt><dd>'+str(n)+'</dd></div><div><dt>Recorded families</dt><dd>'+str(f)+'</dd></div><div><dt>Qualifying</dt><dd>'+str(q)+'</dd></div><div><dt>Challenging</dt><dd>'+str(ch)+'</dd></div></dl><p class="coverage-note">'+note+'</p>'+unknown+('<details><summary>Explore relationship types</summary><ul class="relationship-list">'+breakdown+'</ul><p>These categories can overlap. Counts within a category count each finding once.</p></details>' if n else '<p><a href="../../participate/">Suggest publicly accessible evidence →</a></p>')+'<p class="coverage-card-link"><a href="'+esc(query(term=r['id']))+'">'+('Explore linked findings' if n else 'View this term’s Library results')+' →</a></p></article>')
    ev={e['id']:e for e in d['evidence']};unmatched=[]
    for eid in c['unmatched_finding_ids']:
        e=ev[eid]
        unmatched.append('<article class="unmatched-card"><p class="coverage-label">'+eid+' · No term relationship recorded</p><h3><a href="../#'+eid+'">'+esc(e['title'])+'</a></h3><p>'+esc(e['observation'])+'</p><p class="unmatched-limits"><strong>Limits:</strong> '+esc(e['limitations'])+'</p><p><a href="../#'+eid+'">Read source citations, context and open questions →</a></p></article>')
    n=c['counts'];home=(D/'index.html').read_text()
    header=re.search(r'<header class="site-header">[\s\S]*?</header>',home)[0].replace('href="./','href="../../')
    header=header.replace('aria-current="page"','').replace('href="../../evidence/"','href="../" aria-current="page"')
    footer=re.search(r'<footer class="site-footer">[\s\S]*?</footer>',home)[0].replace('href="./','href="../../')
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><title>Evidence coverage and gaps | Vocabulary Commons</title><meta name="description" content="Explore evidence links, recorded source families, qualifying findings and gaps across the founding vocabulary."><link rel="canonical" href="'''+HOST+'''evidence/coverage/"><link rel="stylesheet" href="../../assets/style.css"><link rel="stylesheet" href="coverage.css"><link rel="alternate" type="application/json" href="coverage.json" title="Derived evidence coverage"></head><body><a class="skip" href="#content">Skip to main content</a>'''+header+'''<main id="content" class="coverage-main"><p class="eyebrow">Look at the connections. Examine the gaps.</p><h1>Evidence coverage<br>and open gaps.</h1><p class="coverage-lead">See where the Library connects to the founding vocabulary, where findings qualify an interpretation, and where a connection has yet to be recorded.</p><p class="coverage-basis">Based on public dataset '''+esc(d['dataset_version'])+''' · '''+str(n['public_findings'])+''' findings · '''+str(n['withdrawal_notices'])+''' withdrawal notices excluded from coverage counts.</p><div class="coverage-summary"><div><strong>'''+str(n['terms_with_links'])+' / '+str(n['terms'])+'''</strong><span>terms with curated evidence links</span></div><a href="#term-coverage" data-quick="unlinked"><strong>'''+str(n['terms_without_links'])+'''</strong><span>term without linked evidence</span></a><a href="#term-coverage" data-quick="one-family"><strong>'''+str(n['terms_with_one_recorded_family'])+'''</strong><span>terms drawing on one recorded family</span></a><a href="#unmatched"><strong>'''+str(n['findings_without_term_links'])+'''</strong><span>findings without a term link</span></a></div><aside class="coverage-caution"><strong>Curation coverage describes recorded links.</strong><p>One finding can cite several source families, so family counts can exceed finding counts. These are curation counts, not validation scores. A link does not validate a definition. A qualifying or challenging finding is not a source-quality score. Distinct source-family labels do not prove independence; other dependencies may remain. One finding may connect to several terms.</p></aside><p class="coverage-nav"><a href="../">Search the Library</a><a href="coverage.json" download>Download coverage data</a><a href="../policy.html">Publication and verification</a><a href="#counting">How counts work</a></p><section id="term-coverage" aria-labelledby="coverage-heading"><h2 id="coverage-heading">Explore term coverage</h2><div class="coverage-controls" hidden><label for="coverage-search">Find a term<input id="coverage-search" type="search" placeholder="Try feedback or control" autocomplete="off"></label><label for="coverage-filter">Show<select id="coverage-filter"><option value="all">All terms</option><option value="unlinked">No linked evidence</option><option value="one-family">One recorded source family</option><option value="qualifies">Has qualifying findings</option><option value="challenges">Has challenging findings</option></select></label><label for="coverage-sort">Order<select id="coverage-sort"><option value="families">Fewest recorded families</option><option value="name">Term name</option><option value="fewest">Fewest linked findings</option><option value="most">Most linked findings</option></select></label><button id="coverage-reset" type="button">Reset</button></div><p id="coverage-results" role="status" aria-live="polite">'''+str(n['terms'])+''' terms. Open each term to read its definition; follow its findings to examine the underlying sources.</p><noscript><p>All terms and links are available below. JavaScript adds filtering and sorting.</p></noscript><div class="coverage-grid">'''+''.join(cards)+'''</div><p id="coverage-empty" hidden>No terms match these choices. Clear the search or choose another view.</p></section><section id="unmatched" class="coverage-section" aria-labelledby="unmatched-heading"><p class="eyebrow">Relevant evidence can remain unmatched</p><h2 id="unmatched-heading">Findings without a term link</h2><p>An unmatched finding can signal a missing relationship, a vocabulary question, or useful context that needs no new term. These findings remain in the Library with their original sources and limitations.</p><p><a href="../?term=__unmatched__">Explore all unmatched findings in the Library →</a></p>'''+''.join(unmatched)+'''</section><section id="counting" class="coverage-section coverage-method"><h2>How these counts work</h2><p><strong>Linked findings:</strong> distinct published evidence IDs with an explicit relationship to the term. Withdrawn records are excluded. Bibliography mentions and keyword matches alone do not count.</p><p><strong>Recorded families:</strong> distinct recorded source-family identifiers across all sources cited by those linked findings. Multiple source versions in one family count once. Family labels do not certify independence, and recorded source dependencies can reveal further overlap. Missing family metadata is disclosed separately.</p><p><strong>Qualifying and challenging:</strong> findings with those explicit relationship types. Other categories, including partial relationships, remain visible in the breakdown. Zero challenging links means none are recorded here; it does not establish consensus.</p><p><strong>What to investigate next:</strong> check existing records for a defensible missing connection, seek directly public root sources, and retain contrary findings and limits. A gap does not justify forcing a finding into a term or adding a new term automatically.</p><p>The founding definitions and their claim standings are unchanged. <a href="../../participate/">Contribute a source, correction or different interpretation →</a></p></section></main>'''+footer+'''<script defer src="../../assets/app.js"></script><script defer src="coverage.js"></script></body></html>'''
    (OUT/'index.html').write_text(page)
    # Idempotent discovery links; do not alter definitions, evidence or machine record objects.
    p=D/'evidence/index.html';s=p.read_text();tag='<a href="coverage/">Evidence coverage and gaps</a>'
    if tag not in s:s=s.replace('<div class="library-links">','<div class="library-links">'+tag,1)
    p.write_text(s)
    p=D/'terms/index.html';s=p.read_text();tag='<p class="coverage-discovery"><a href="../evidence/coverage/">Explore evidence coverage and open gaps across these terms →</a></p>'
    if tag not in s:s=s.replace('</section>',tag+'</section>',1)
    p.write_text(s)
    p=D/'sitemap.xml';s=p.read_text()
    if HOST+'evidence/coverage/' not in s:s=s.replace('</urlset>','<url><loc>'+HOST+'evidence/coverage/</loc></url>\n</urlset>')
    p.write_text(s)
    manifest=D/'evidence/release-manifest.json';m=json.loads(manifest.read_text());m['presentation_version']=PRESENTATION
    m['coverage_view']={'url':HOST+'evidence/coverage/','dataset_version':d['dataset_version'],'dataset_sha256':c['dataset_sha256'],'files_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file()}}
    m['files_sha256']['index.html']=hashlib.sha256((D/'evidence/index.html').read_bytes()).hexdigest();manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    return c

if __name__=='__main__':print(json.dumps(build()['counts']))
