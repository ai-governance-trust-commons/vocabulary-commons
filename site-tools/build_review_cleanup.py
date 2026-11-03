#!/usr/bin/env python3
"""Refresh public navigation/reading aids, preserving frozen glossary content."""
from pathlib import Path
import json,re,html,hashlib
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs';VERSION='0.5.5'
def esc(s):return html.escape(str(s),quote=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def aid(t):
 if t.get('normative_proposal'):return 'A proposed principle or recommendation; this is not a claim that effective control has been achieved.'
 return {'Foundation':'Conceptual or theoretical framing, rather than an empirical finding.','Demonstrated (bounded)':'Observed in specified settings; the label does not establish general prevalence or independent verification by the Commons.','Indicated':'Supported by evidence or inference, but not established generally; the scope remains open to investigation.','Hypothesis':'An untested broader proposition; relevant research can inform the question without demonstrating that proposition.'}[t['claim_standing']]
def build():
 data=json.loads((D/'evidence/evidence.json').read_text());g=json.loads((D/'data/glossary.json').read_text());ev={e['id']:e for e in data['evidence']};terms={t['name']:t for t in data['terms']};count=0
 for t in g['terms']:
  tid=terms[t['term']]['id'];links=[r for r in data['relationships'] if r['to_id']==tid and r['from_id'] in ev];byid={}
  for r in links:byid.setdefault(r['from_id'],[]).append(r)
  n=len(byid);items=[]
  for eid,rels in sorted(byid.items()):
   e=ev[eid];items.append('<li><a href="../../evidence/#'+eid+'">'+eid+' · '+esc(e['title'])+'</a>'+''.join('<p>'+esc(r['relationship_type']+': '+r['explanation'])+'</p>' for r in rels)+'</li>')
  panel='<section class="related-evidence" id="linked-evidence"><h2>Related evidence</h2><p>Current curation links from dataset '+esc(data['dataset_version'])+'. A finding may illustrate, qualify or challenge an application; a link does not validate the definition, establish general prevalence or certify independent corroboration.</p><p><a href="../../evidence/?term='+tid+'">Search all '+str(n)+' linked findings and inspect their limits →</a> · <a href="../../evidence/coverage/#'+tid+'">Coverage and source-family context</a></p>'
  if n:panel+='<details><summary>View '+str(n)+' related evidence records</summary><ul>'+''.join(items)+'</ul></details>'
  else:panel+='<p>No evidence relationship is recorded. This is a curation gap, not proof that relevant research is absent.</p>'
  panel+='</section>'
  p=D/'terms'/t['slug']/'index.html';s=p.read_text();s,nreplace=re.subn(r'<section class="related-evidence"[^>]*>[\s\S]*?</section>',lambda m:panel,s);assert nreplace==1,t['term']
  note='<aside class="standing-context" id="standing-context"><p><strong>Reading aid — founding standing:</strong> '+esc(aid(t))+' <a href="../../method/#classification-guide">Read the classification guide</a>.</p><p>The v1.0.2 wording and classifications below are fixed. Evidence links use the current dataset; <a href="#linked-evidence">inspect each finding’s setting, source and limitations</a>.</p></aside>'
  if 'id="standing-context"' in s:s=re.sub(r'<aside class="standing-context"[\s\S]*?</aside>',lambda m:note,s)
  else:s=s.replace('<section class="definition">',note+'<section class="definition">',1)
  if t['claim_standing']=='Demonstrated (bounded)' and byid:
   # One clearly labeled current example; never substitute it for the founding definition or its evidence basis.
   illustrative=[r['from_id'] for r in links if r['relationship_type']=='illustrates'];eid=sorted(set(illustrative or byid))[0];e=ev[eid]
   example='<section class="current-evidence-example" id="current-evidence-example"><h2>One current Library example and its bounds</h2><p>This editorial reading aid is not a reassessment of the founding claim standing or a complete evidence review.</p><p><strong>'+eid+' · '+esc(e['evidence_standing_label'])+':</strong> '+esc(e['observation'])+'</p><p><strong>Recorded limits:</strong> '+esc(e['limitations'])+'</p><p><a href="../../evidence/#'+eid+'">Inspect the full record, source citations and verification →</a></p></section>'
   if 'id="current-evidence-example"' in s:s=re.sub(r'<section class="current-evidence-example"[\s\S]*?</section>',lambda m:example,s)
   else:s=s.replace(panel,example+panel,1)
  if '../../assets/research-notes.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="../../assets/research-notes.css"></head>')
  p.write_text(s);count+=1
 # Browse cards: keep exact words; make the founding citation range navigable and add separate reading aids.
 p=D/'terms/index.html';s=p.read_text()
 def card(m):
  text=m[0];slug=re.search(r'<h2><a href="([^"]+)/">',text)[1];t=next(t for t in g['terms'] if t['slug']==slug)
  if t['term']=='Trajectory persistence' and 'href="../method/#ref-8"' not in text:
   text=text.replace('[8–10]','<a href="../method/#ref-8" title="Founding bibliography references 8–10; these are not Evidence Library IDs">[8–10]</a>')
  if t['term']=='Trajectory persistence':text=text.replace('<p>A tendency','<p class="citation-bearing">A tendency',1)
  note='<div class="card-reading-aid"><p><strong>Reading aid:</strong> '+esc(aid(t))+'</p><p><a href="'+slug+'/#linked-evidence">Explore linked evidence and its limits →</a></p></div>'
  if 'class="card-reading-aid"' in text:text=re.sub(r'<div class="card-reading-aid">[\s\S]*?</div>',lambda m:note,text)
  else:text=text.replace('</article>',note+'</article>')
  return text
 s=re.sub(r'<article class="term-card">[\s\S]*?</article>',card,s)
 guide='<aside class="standing-context version-guide" id="version-guide"><p><strong>Two kinds of version:</strong> founding glossary v1.0.2 identifies the fixed definitions and classifications. Evidence dataset '+esc(data['dataset_version'])+' identifies the current findings, sources and relationships. Website presentation '+VERSION+' identifies this interface update.</p><p>Reading aids are editorial annotations, separate from the founding text. <a href="../method/#classification-guide">Compare Foundation, Demonstrated (bounded), Indicated and Hypothesis →</a></p></aside>'
 if 'id="version-guide"' in s:s=re.sub(r'<aside class="standing-context version-guide"[\s\S]*?</aside>',lambda m:guide,s)
 else:s=s.replace('<section class="wrap filterbar">','<div class="wrap">'+guide+'</div><section class="wrap filterbar">',1)
 if '../assets/research-notes.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="../assets/research-notes.css"></head>')
 p.write_text(s)
 # Explain bibliography IDs and add links to the exact original publications, not guessed evidence ID numbers.
 p=D/'method/index.html';s=p.read_text();s=s.replace('<h2>Classification guide</h2>','<h2 id="classification-guide">Classification guide</h2>',1)
 note='<aside class="standing-context" id="citation-guide"><p><strong>Founding references and Library records use different identifiers.</strong> Bracketed numbers such as [8–10] refer to the bibliography below. EVID identifiers refer to separately curated Library findings; matching numbers do not imply matching sources. Follow each bibliography entry’s original-source link.</p><p><a href="#ref-8">Reference [8]</a> · <a href="#ref-9">Reference [9]</a> · <a href="#ref-10">Reference [10]</a> · <a href="../evidence/">Search the Evidence Library</a></p></aside>'
 if 'id="citation-guide"' in s:s=re.sub(r'<aside class="standing-context" id="citation-guide">[\s\S]*?</aside>',lambda m:note,s)
 else:s=s.replace('<h2 id="references">Nearest public reference points</h2>','<h2 id="references">Nearest public reference points</h2>'+note)
 if '../assets/research-notes.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="../assets/research-notes.css"></head>')
 p.write_text(s)
 # Current per-record status is visible in the collapsed Library card, not only in its expanded metadata.
 p=D/'evidence/policy.html';s=p.read_text()
 s=s.replace('Demonstrated (bounded) retains an explicitly recorded bounded finding; it does not imply independent reproduction.','Attributed author and issuer accounts, including controlled demonstrations, are labeled Reported observation in this release. The glossary’s Demonstrated (bounded) standing is a different classification and is not a verification label for a Library record.')
 note='<section id="release-054"><h2>Release 0.5.4 corrections</h2><p>Dataset 0.5.4 corrects reporting labels and editorial wording; it adds no findings or sources. Reporting labels for EVID-001–003, EVID-005–006, EVID-179–180 and EVID-183 now read Reported observation. EVID-006 separates the source account from the Commons interpretation and removes workflow wording. EVID-020 and its CASE-017 grouping identify a systematic review and meta-analysis; SRC-015 removes obsolete internal shorthand. Source inspection dates and independent-verification status are unchanged. Founding glossary v1.0.2 remains fixed. Website presentation 0.5.4 identifies the interface release; machine contract 1.0 identifies the data structure, not the strength of evidence.</p><p>Provisional publication under POLICY-001 is separate from individual human review, source inspection and independent verification. Repeated timestamps can reflect one publication batch; they do not establish individual human review. Historical withdrawal-version references below describe when the holds were recorded, not the current dataset version.</p></section>'
 if 'id="release-054"' not in s:s=s.replace('</main>',note+'</main>')
 p.write_text(s)
 # Record content-to-page hashes after all presentation modifications.
 p=D/'evidence/release-manifest.json';m=json.loads(p.read_text());m['presentation_version']=VERSION;m['files_sha256']={n:sha(D/'evidence'/n) for n in ['index.html','evidence.json','policy.html','evidence.js','evidence.css']}
 targets=[D/'terms/index.html',D/'method/index.html',D/'assets/research-notes.css',*sorted((D/'terms').glob('*/index.html'))]
 m['term_navigation']={'dataset_version':data['dataset_version'],'dataset_sha256':sha(D/'evidence/evidence.json'),'term_pages':count,'files_sha256':{str(p.relative_to(D)):sha(p) for p in targets}}
 p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 return {'term_pages':count,'dataset_version':data['dataset_version']}
if __name__=='__main__':print(json.dumps(build()))
