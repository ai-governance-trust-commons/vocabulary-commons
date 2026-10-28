#!/usr/bin/env python3
"""Build a static, source-faithful GitHub Pages front end for the vocabulary Commons.

All founding term wording, relationships, and classifications are read directly
from the root versioned Markdown source. This program makes no network calls.
"""
from __future__ import annotations
import html, json, hashlib, re, shutil, unicodedata
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape
from markdown_it import MarkdownIt
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'FOUNDING_GLOSSARY_v1.0.2.md'
SITE = ROOT / 'docs'
HOST = 'https://ai-governance-trust-commons.github.io/vocabulary-commons/'
REPO = 'https://github.com/ai-governance-trust-commons/vocabulary-commons'
DOI = 'https://doi.org/10.5281/zenodo.23626688'
md = MarkdownIt('commonmark', {'html': False, 'linkify': True})


def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'(^-|-$)', '', re.sub(r'[^a-z0-9]+','-',s))


def esc(s): return html.escape(str(s), quote=True)


def markdown(s): return md.render(s).strip()


def segment(text, heading):
    m=re.search(r'(?m)^## '+re.escape(heading)+r'\s*$', text)
    if not m: raise ValueError('Missing heading '+heading)
    end=re.search(r'(?m)^## ', text[m.end():]); return text[m.end():(m.end()+end.start() if end else len(text))].strip()

raw=SOURCE.read_text(encoding='utf-8')
b=SOURCE.read_bytes()
gitsha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
assert gitsha == '2e5a19de39653dac037b1c568f4c654870e911ba', 'Source has changed: verify before rebuilding'
block=raw.split('## Term index\n',1)[1]
idxpart, after=block.split('\n---\n',1)
index_terms=re.findall(r'^- \[([^\]]+)\]\(#[^\)]+\)',idxpart,flags=re.M)
content=after.split('\n## Use and evidence discipline\n',1)[0]
sections=re.findall(r'(?ms)^## ([^\n]+)\n\n(.*?)(?=\n---\n\n## |\Z)',content)
assert len(sections)==len(index_terms)==35,(len(sections),len(index_terms))
terms=[]
for term,body in sections:
    body=body.strip()
    m1=re.search(r'\*\*Vocabulary: ([^*]+)\*\*',body)
    m2=re.search(r'\*\*Claim: ([^*]+)\*\*',body)
    normative='**Normative proposal**' in body
    dm=re.search(r'(?:\*\*Claim: [^*]+\*\*|\*\*Normative proposal\*\*)\s*\n\n(.*?)\n\n\*\*Relationship:\*\*',body,re.S)
    rm=re.search(r'\*\*Relationship:\*\* (.*?)\n\n\*\*See also:\*\*',body,re.S)
    sm=re.search(r'\*\*See also:\*\* (.*)',body,re.S)
    if not all([m1,dm,rm,sm]) or (not m2 and not normative): raise ValueError('Parse error: '+term)
    term_refs=re.findall(r'\[([^\]]+)\]\(#[^)]+\)',sm.group(1))
    terms.append({'name':term,'slug':slug(term),'vocabulary':m1.group(1).strip(),'claim':(m2.group(1).strip() if m2 else None),'normative':normative,'definition':dm.group(1).strip(),'relationship':rm.group(1).strip(),'see_also':term_refs,'source_markdown':body})
assert [x['name'] for x in terms]==index_terms
lookup={t['name']:t for t in terms}
assert all(set(t['see_also']).issubset(lookup) for t in terms)
assert len(set(t['slug'] for t in terms))==35

# Navigation questions are editorial aids, NOT additions to the published glossary.
questions=[
("When is human oversight more than an approval step?", ["Chaperoning","Meaningful human control","Horizon compression","Trajectory persistence"]),
("How can monitoring miss consequential relationships?", ["Observability","Observability boundary","Beyond visual range (BVR)","Sleight-of-hand effect"]),
("What changes when AI lowers the barriers to action?", ["Constraint compression","Capability feasibility progression","Attacker-model change"]),
("How can interacting activities affect pace and consequences?", ["Cross-system feedback","Feedback acceleration","Feedback amplification","Horizon compression"]),
("How does organizational reliance affect the ability to evaluate work?", ["Organizational dependency","Operational trust","Competency decay","Assurance independence"]),
("What can make apparently credible evidence unreliable?", ["Reference environment integrity","Evidence laundering through AI","Environmental redirection"]),
("What should be examined when AI-enabled capabilities evolve?", ["Successor assurance","Outcome–purpose divergence","Purpose preservation","Purposeful continuity"]),
("What does governability mean beyond one agent or control?", ["Governability","Distributed adaptive control environment","System-level autonomy","Control air gap"]),
]
assert all(name in lookup for _,ls in questions for name in ls)

def relink_markup(text, prefix):
    soup=BeautifulSoup(markdown(text),'html.parser')
    for a in soup.select('a[href^="#"]'):
        label=a.get_text()
        if label in lookup: a['href']=prefix+'terms/'+lookup[label]['slug']+'/'
    return str(soup)

# Globally shared page elements.
def nav(prefix, active=''):
    menu=[('Home',prefix),('Glossary',prefix+'terms/'),('Explore questions',prefix+'questions/'),('How to read',prefix+'method/'),('Participate',prefix+'participate/')]
    links=''.join('<a href="'+esc(u)+'"'+(' aria-current="page"' if label==active else '')+'>'+esc(label)+'</a>' for label,u in menu)
    return f'''<header class="site-header"><div class="wrap masthead">
<a class="brand" href="{prefix}" aria-label="Governance and Trust Vocabulary Commons, home"><span class="mark" aria-hidden="true"><span></span><span></span><span></span></span><span class="brand-name">Governance <em>&amp;</em> Trust <small>Vocabulary Commons</small></span></a>
<button type="button" class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false" aria-controls="primary-nav">Menu <span aria-hidden="true">☰</span></button><nav id="primary-nav" aria-label="Primary navigation">{links}</nav></div></header>'''

def footer(prefix):
    return f'''<footer class="site-footer"><div class="wrap footer-cols"><div><strong>Governance &amp; Trust Vocabulary Commons</strong><p>Meaningful discussion requires sufficiently precise, shared language.</p></div><div><span class="footer-label">Source &amp; participation</span><a href="{DOI}">Founding publication · DOI</a><a href="{REPO}">GitHub repository</a><a href="{REPO}/blob/main/EDITORIAL_REVIEW.md">Editorial policy</a></div></div><div class="wrap foot-end"><span>Founding baseline v1.0.2 · 24 October 2026 · CC BY 4.0</span><span>Shared understanding, not shared conclusions.</span></div></footer>'''

def layout(title, desc, main, prefix='./', active='', canonical='', schema=None):
    canon=HOST+canonical
    title_full=(title+' | Governance & Trust Vocabulary Commons') if title!='Governance & Trust Vocabulary Commons' else title
    schema_str=(f'<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace("</","<\\/")}</script>' if schema else '')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="theme-color" content="#f7f8f6"><title>{esc(title_full)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{esc(canon)}"><meta property="og:title" content="{esc(title_full)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{esc(canon)}"><link rel="stylesheet" href="{prefix}assets/style.css">{schema_str}</head><body><a class="skip" href="#content">Skip to main content</a>{nav(prefix,active)}<main id="content">{main}</main>{footer(prefix)}<script defer src="{prefix}assets/app.js"></script></body></html>'''

def put(path,body):
    p=SITE/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body,encoding='utf-8')

def link(term, prefix, klass=''):
    return '<a'+(' class="'+klass+'"' if klass else '')+' href="'+prefix+'terms/'+lookup[term]['slug']+'/">'+esc(term)+'</a>'

def group_terms(names,prefix):return ''.join('<span class="related">'+link(n,prefix)+'</span>' for n in names)

# Homepage: introductory language for first-time readers. The glossary is unchanged.
# Keep one source text, presented in two responsive positions: in the hero on
# small screens, and in the full-width introduction on desktop.
welcome_copy = 'The Commons is a public collection of terms and definitions for describing how AI is used and how it affects people and organizations. Anyone can explore the language, question a definition, or help improve it.'
front=f'''<section class="hero"><div class="wrap hero-grid"><div>
<p class="eyebrow">An open place to explore language about AI</p>
<h1>Better language.<br>Better questions.<br><i>Better understanding.</i></h1>
<p class="hero-intro">AI is changing how people and organizations work, make decisions, and use technology. We need clear language to understand what's happening—and what it means.</p>
<section class="mobile-welcome" aria-labelledby="mobile-welcome-heading"><p class="eyebrow">What is the Commons?</p><h2 id="mobile-welcome-heading">An open place to make sense of AI.</h2><p>{welcome_copy}</p></section>
<div class="actions"><a class="button primary" href="terms/">Explore 35 founding terms <span aria-hidden="true">↗</span></a><a class="button secondary" href="questions/">Start with a question</a></div></div>
<aside class="hero-panel"><span class="panel-top">THE FOUNDING PRINCIPLE</span><blockquote>“Meaningful discussion requires sufficiently precise, shared language.”</blockquote><p>Not a compliance framework. Not a claim of final authority. A shared reference open to examination and revision.</p><span class="panel-bottom">Baseline v1.0.2 · 24 Oct 2026</span></aside></div></section>
<section class="wrap welcome" aria-labelledby="welcome-heading"><p class="eyebrow">What is the Commons?</p><div><h2 id="welcome-heading">An open place to make sense of AI.</h2><p>{welcome_copy}</p></div></section>
<section class="wrap section"><div class="section-heading"><p class="eyebrow">How to begin</p><h2>Three ways to explore</h2><p class="section-intro">The glossary starts with 35 terms that help describe AI capabilities, human oversight, organizational reliance, and emerging risks. You can look up a term, follow a question, or contribute a better explanation.</p></div>
<div class="three-card"><a class="feature" href="terms/"><span class="feature-number">01</span><h3>Browse the glossary</h3><p>Read the terms and their definitions. See how they relate and how much support their claims have.</p><span class="feature-cta">Explore terms →</span></a><a class="feature" href="questions/"><span class="feature-number">02</span><h3>Follow a question</h3><p>Start with a real question about AI and find terminology that helps you examine it.</p><span class="feature-cta">Explore questions →</span></a><a class="feature" href="participate/"><span class="feature-number">03</span><h3>Challenge or contribute</h3><p>Ask questions, share evidence, suggest another meaning, or propose a term. You don't need a finished research paper.</p><span class="feature-cta">Participate →</span></a></div></section>
<section class="fullband"><div class="wrap band-grid"><div><p class="eyebrow">How to read an entry</p><h2>Words are not evidence.</h2><p>A useful term does not prove that every claim associated with it is true. Each entry shows whether its wording is established or still being developed, and how strongly its associated claims are supported.</p><a class="text-link" href="method/">Understand the classifications →</a></div>
<div class="band-details"><div><strong>Vocabulary standing</strong><span>Is the term established, extended, or still working?</span><span>Established · Extended · Working</span></div><div><strong>Claim standing</strong><span>How well supported is an associated claim?</span><span>Foundation · Demonstrated (bounded) · Indicated · Hypothesis</span></div><div><strong>Normative proposals</strong><span>Recommendations are distinguished from descriptions of what happens.</span></div></div></div></section>
<section class="wrap section source-section"><div><p class="eyebrow">Where this started</p><h2>A published starting point.<br>An open future.</h2><p>The first 35 definitions come from <em>Describing the Environment We Are Trying to Govern</em> by Lance J. Johnson. That version is preserved on Zenodo. The Commons makes it easier to explore and creates a place to question, refine, and add terminology without rewriting the original publication.</p><div class="actions"><a class="button secondary" href="{DOI}">Read on Zenodo ↗</a><a class="text-link" href="{REPO}">Explore the GitHub Commons →</a></div></div><div class="source-stamp"><span>01 / FOUNDING REFERENCE</span><strong>35</strong><p>alphabetical entries<br><span>version 1.0.2</span></p><small>Preserved with definitions, relationships, classifications and citations.</small></div></section>'''
put(Path('index.html'),layout('Governance & Trust Vocabulary Commons','Better language. Better questions. Better understanding. An open glossary for describing AI and its effects on people and organizations.',front,'./','Home','',{'@context':'https://schema.org','@type':'Dataset','name':'Governance and Trust Vocabulary Commons — Founding Glossary v1.0.2','description':'Navigable 35-term baseline vocabulary for AI-enabled human, organizational and technical environments.','url':HOST,'citation':DOI,'license':'https://creativecommons.org/licenses/by/4.0/','creator':{'@type':'Person','name':'Lance J. Johnson'}}))

# Term browse page + local, client-side query and filter.
items=[]
for t in terms:
    claim=t['claim'] if not t['normative'] else 'Normative proposal'
    summary=t['definition']
    search=(t['name']+' '+t['definition']+' '+t['relationship']+' '+claim).lower()
    items.append(f'''<li class="term-item" data-vocabulary="{esc(t['vocabulary'])}" data-claim="{esc(claim)}" data-search="{esc(search)}"><a class="term-card" href="{t['slug']}/"><div class="card-row"><h2>{esc(t['name'])}</h2><span aria-hidden="true">↗</span></div><div class="chips"><span>{esc(t['vocabulary'])}</span><span>{esc(claim)}</span></div><p>{esc(summary)}</p></a></li>''')
page='''<section class="small-hero wrap"><p class="eyebrow">The founding reference</p><h1>Browse the vocabulary</h1><p>Thirty-five alphabetical entries from the fixed v1.0.2 glossary. Each term retains its original definition, relationship, and status; linked terms reveal nearby concepts.</p></section>
<section class="wrap filterbar"><label for="term-search">Search terms and definitions</label><input type="search" id="term-search" placeholder="Try ‘oversight’, ‘dependency’, ‘evidence’…" autocomplete="off" aria-describedby="results-count"><div class="filter-row"><label for="vocab-filter">Vocabulary <select id="vocab-filter"><option value="">All statuses</option><option>Established</option><option>Extended</option><option>Working</option></select></label><label for="claim-filter">Claim standing <select id="claim-filter"><option value="">All statuses</option><option>Foundation</option><option>Demonstrated (bounded)</option><option>Indicated</option><option>Hypothesis</option><option>Normative proposal</option></select></label><span id="results-count" role="status" aria-live="polite">35 terms</span></div></section>
<section class="wrap term-results"><ul id="term-list" class="terms-grid">'''+''.join(items)+'''</ul><p id="no-results" hidden>No matching terms. Try fewer words or clear the filters.</p><p class="tiny-note">The listed entries are a transcription of the founding baseline, not a new edition or a guarantee that every claim is established.</p><noscript><p>Search and filters require JavaScript. All 35 terms remain browseable without it.</p></noscript></section>'''
put(Path('terms/index.html'),layout('Founding glossary — all 35 terms','Search and browse the 35 founding AI governance vocabulary terms, with evidence standing and interlinked definitions.',page,'../','Glossary','terms/'))

# Individual term pages are generated from exact source body text.
for i,t in enumerate(terms):
    claim=t['claim'] if not t['normative'] else 'Normative proposal'
    next_term=terms[(i+1)%len(terms)];prev_term=terms[(i-1)%len(terms)]
    def_html=relink_markup(t['definition'],'../../')
    rel_html=relink_markup(t['relationship'],'../../')
    raw_ref=relink_markup(t['source_markdown'],'../../')
    schema={'@context':'https://schema.org','@type':'DefinedTerm','name':t['name'],'description':t['definition'],'url':HOST+'terms/'+t['slug']+'/','inDefinedTermSet':{'@type':'DefinedTermSet','name':'Governance and Trust Vocabulary Commons — Founding Glossary v1.0.2','url':HOST+'terms/'},'citation':DOI,'license':'https://creativecommons.org/licenses/by/4.0/','additionalProperty':[{'@type':'PropertyValue','name':'Vocabulary standing','value':t['vocabulary']},{'@type':'PropertyValue','name':'Claim standing','value':claim}]}
    page=f'''<section class="wrap term-detail"><nav aria-label="Breadcrumb" class="crumbs"><a href="../../terms/">Glossary</a><span aria-hidden="true">/</span><span aria-current="page">{esc(t['name'])}</span></nav><p class="eyebrow">Founding glossary / v1.0.2</p><h1>{esc(t['name'])}</h1><div class="chips large"><span>Vocabulary · {esc(t['vocabulary'])}</span><span>{'Normative proposal' if t['normative'] else 'Claim · '+esc(claim)}</span></div><section class="definition"><h2>Definition</h2>{def_html}</section><section class="relationship"><h2>Relationship to other concepts</h2>{rel_html}</section><section class="related-section"><h2>See also</h2><div class="related-links">{group_terms(t['see_also'],'../../')}</div></section><div class="source-banner"><strong>Source &amp; standing</strong><p>This is a faithful web presentation of the founding entry. Its vocabulary and claim classifications describe the standing given in v1.0.2—not a claim of universal validity.</p><a href="{DOI}">Consult the publication of record ↗</a> <span aria-hidden="true">·</span> <a href="{REPO}/blob/main/FOUNDING_GLOSSARY_v1.0.2.md">See full source glossary ↗</a></div><details class="source-detail"><summary>View source Markdown for this entry</summary><pre>{esc('## '+t['name']+'\n\n'+t['source_markdown'])}</pre></details><nav class="term-prevnext" aria-label="Adjacent glossary terms"><a href="../{prev_term['slug']}/"><span>← Previous term</span><strong>{esc(prev_term['name'])}</strong></a><a href="../{next_term['slug']}/"><span>Next term →</span><strong>{esc(next_term['name'])}</strong></a></nav></section>'''
    put(Path('terms')/t['slug']/'index.html',layout(t['name'],t['definition'][:165],page,'../../','Glossary','terms/'+t['slug']+'/',schema))

# Question-based navigation.
qs=''.join(f'''<article class="question"><span class="question-no">{i:02d}</span><div><h2>{esc(q)}</h2><p>Related founding terms:</p><div class="related-links">{group_terms(ls,'../')}</div></div></article>''' for i,(q,ls) in enumerate(questions,1))
page=f'''<section class="small-hero wrap"><p class="eyebrow">Start with the problem</p><h1>Questions that lead to terms</h1><p>This is an editorial navigation aid, not part of the frozen 2026 publication. These questions direct visitors to relevant founding entries without claiming to answer the questions or validate their application.</p></section><section class="wrap questions">{qs}</section><section class="wrap afterword"><h2>Have a different question?</h2><p>Propose alternative terminology or challenge a relationship through the open Commons. Relevance is not endorsement.</p><a class="button primary" href="../participate/">Explore participation →</a></section>'''
put(Path('questions/index.html'),layout('Explore by question','Start from common AI oversight, assurance, dependency, and evidence questions; explore related glossary terms.',page,'../','Explore questions','questions/'))

# Method: foundational methodology excerpts copied as is where practical.
intro=segment(raw,'How to read each entry').strip()
relationships=segment(raw,'Relationships at a glance').split('## Term index')[0].strip()
evidence=segment(raw,'Use and evidence discipline')
references=segment(raw,'Nearest public reference points')
page=f'''<section class="small-hero wrap"><p class="eyebrow">Reading the founding baseline</p><h1>How to read the glossary</h1><p>Vocabulary status and the evidentiary standing of a claim are separate. A useful name does not prove a behavior occurred, and a bounded observation does not establish general prevalence.</p></section><section class="wrap prose method"><h2>Classification guide</h2>{relink_markup(intro,'../')}<h2>Relationships at a glance</h2>{relink_markup(relationships,'../')}<h2>Use and evidence discipline</h2>{relink_markup(evidence,'../')}<h2 id="references">Nearest public reference points</h2>{relink_markup(references,'../')}</section>'''
put(Path('method/index.html'),layout('How to read the glossary','Interpret vocabulary and claim standing, normative proposals, evidence limitations, and the source references.',page,'../','How to read','method/'))

page=f'''<section class="small-hero wrap"><p class="eyebrow">An invitation to examine and improve</p><h1>Participate in the Commons</h1><p>We welcome critique, alternate meanings, evidence, unfamiliar domain usage, and working terminology. A contribution need not be complete to warrant consideration.</p></section><section class="wrap section"><div class="three-card"><a class="feature" href="{REPO}/discussions"><span class="feature-number">DISCUSS</span><h2>Explore ideas</h2><p>Ask questions, compare interpretations and examine contradictory evidence.</p><span class="feature-cta">Open Discussions ↗</span></a><a class="feature" href="{REPO}/issues/new/choose"><span class="feature-number">PROPOSE</span><h2>Submit a term</h2><p>Use the structured proposal template, including uncertainties and context.</p><span class="feature-cta">Propose a Term ↗</span></a><a class="feature" href="{REPO}/blob/main/EDITORIAL_REVIEW.md"><span class="feature-number">REVIEW</span><h2>See how curation works</h2><p>Equal consideration, documented decisions, and definitions that remain revisable.</p><span class="feature-cta">Editorial review policy ↗</span></a></div></section><section class="wrap prose section"><h2>Principles worth preserving</h2><p>Proposals and alternative definitions may remain publicly visible even if they are not incorporated into the curated glossary. Inclusion represents a current best fit, not an institutional guarantee.</p><p>Contributors and reviewers may work together to supply clarification, provenance, or supporting and contradictory evidence. New terminology should improve a meaningful distinction rather than needlessly replace established usage.</p><p><a href="{REPO}/blob/main/CONTRIBUTING.md">Read the full contribution guidelines ↗</a></p></section>'''
put(Path('participate/index.html'),layout('Participate in the Commons','Discuss terminology, propose definitions, challenge claims, and examine the Commons’ open editorial process.',page,'../','Participate','participate/'))

# Structured export: no invented domain metadata or inferred statuses.
export={'title':'Governance and Trust Vocabulary Commons — Founding Glossary v1.0.2','status':'baseline transcription; not a new edition','published':'2026-10-24','source_repository_file':REPO+'/blob/main/FOUNDING_GLOSSARY_v1.0.2.md','source_git_blob_sha1':gitsha,'publication_of_record':DOI,'license':'CC BY 4.0','terms':[{'term':t['name'],'slug':t['slug'],'vocabulary_standing':t['vocabulary'],'claim_standing':t['claim'],'normative_proposal':t['normative'],'definition':t['definition'],'relationship':t['relationship'],'see_also':t['see_also'],'source_markdown_exact':t['source_markdown']} for t in terms]}
put(Path('data/glossary.json'),json.dumps(export,ensure_ascii=False,indent=2)+'\n')
# Keep exact baseline available from website, byte-identical to GitHub version.
(SITE/'source').mkdir(exist_ok=True,parents=True)
shutil.copyfile(SOURCE,SITE/'source/FOUNDING_GLOSSARY_v1.0.2.md')
assert (SITE/'source/FOUNDING_GLOSSARY_v1.0.2.md').read_bytes()==b

urls=['','terms/','questions/','method/','participate/']+['terms/'+t['slug']+'/' for t in terms]
sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+xml_escape(HOST+x)+'</loc></url>\n' for x in urls)+'</urlset>\n'
put(Path('sitemap.xml'),sitemap)
put(Path('robots.txt'),'User-agent: *\nAllow: /\n\nSitemap: '+HOST+'sitemap.xml\n')
put(Path('.nojekyll'),'')

print('Built',len(terms),'terms /',len(urls),'HTML pages, source git SHA:',gitsha)
