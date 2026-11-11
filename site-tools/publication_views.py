"""Shared navigation and readable Library records from approved public data."""
import html
import json
import posixpath
import re
import hashlib
from markdown_it import MarkdownIt
from source_inspection import inspection_index, LABELS
from publication_security import inline_json

NAVIGATION = [('Home', ''), ('Glossary', 'terms/'), ('Evidence Library', 'evidence/'),
              ('Resources', 'resources/'), ('Explore questions', 'questions/'),
              ('Considerations', 'considerations/'), ('How to use', 'method/'),
              ('Participate', 'participate/')]

def esc(value):
    return html.escape(str(value), quote=True)

def navigation(page, docs):
    directory = page.parent.relative_to(docs).as_posix()
    current = page.relative_to(docs).as_posix()
    links = []
    for label, route in NAVIGATION:
        href = posixpath.relpath(route or '.', directory)
        href = './' if href == '.' else href.rstrip('/') + '/'
        active = current == 'index.html' if not route else current.startswith(route)
        links.append('<a href="' + href + '"' + (' aria-current="page"' if active else '') + '>' + label + '</a>')
    return '<nav id="primary-nav" aria-label="Primary navigation">' + ''.join(links) + '</nav>'

def static_records(data):
    sources = {s['id']: s for s in data['sources']}
    inspection = {e['source_id']: e for e in inspection_index(data)['sources']}
    records = []
    for record in data['evidence']:
        rid = record['id']
        parts = ['<article class="evidence-card" id="' + rid + '">',
                 '<p>' + rid + ' · ' + esc(record['evidence_standing_label']) + '</p>',
                 '<h2>' + esc(record['title']) + '</h2>',
                 '<p>' + esc(record['observation']) + '</p>',
                 '<p><strong>Limits:</strong> ' + esc(record['limitations']) + '</p>',
                 '<p><strong>Commons interpretation:</strong> ' + esc(record['support_assessment']) + '</p>',
                 '<p><strong>Verification:</strong> ' + esc(record['verification_status']) + '</p>',
                 '<p><strong>Open questions:</strong> ' + esc(record['open_questions']) + '</p>',
                 '<p><strong>Disputes:</strong> ' + esc(record['dispute_status']) + '</p>',
                 '<h3>Directly cited sources</h3><ul>']
        for sid in record['source_ids']:
            source = sources[sid]
            title = esc(source['title'])
            if source['url'].startswith('https://'):
                title = '<a href="' + esc(source['url']) + '" rel="noopener noreferrer">' + title + '</a>'
            annotation = inspection[sid]
            detail = '<p>Inspection basis: ' + esc(LABELS[annotation['basis']]) + '. ' + esc(annotation['basis_note']) + '</p><p>Recorded inspection: ' + esc(source['verification']['status']) + '. ' + esc(source['verification']['scope']) + ' Review date: ' + esc(source['verification']['review_date']) + '.</p><p>Dispute-check limits: ' + esc(source['verification']['dispute_check_note'] or source['verification']['dispute_status']) + '</p>'
            parts.append('<li>' + sid + ' · ' + title + '<p>Supporting location: ' + esc(record['source_locations'][sid]) + '</p>' + detail + '</li>')
        parts += ['</ul><p><a href="machine/records/' + rid + '.json">Complete record, source-inspection details and relationships (JSON)</a></p>',
                  '<p>Provisional publication; inclusion is not independent verification. Individual human review: ' + esc(record['publication_record']['individual_human_review']) + '.</p></article>']
        records.append(''.join(parts))
    return ''.join(records)

def refresh(docs):
    data = json.loads((docs/'evidence/evidence.json').read_text())
    refresh_curation(docs)
    for page in docs.rglob('*.html'):
        text = page.read_text()
        policy_url = 'https://github.com/ai-governance-trust-commons/vocabulary-commons/blob/main/EDITORIAL_REVIEW.md'
        local_policy = posixpath.relpath('participate/curation', page.parent.relative_to(docs).as_posix()) + '/'
        # Keep the explicitly labeled source link external; ordinary policy routes stay on site.
        def policy_link(match):
            link = match[0]
            if 'data-policy-source' in link:
                return link
            return link.replace('href="' + policy_url + '"', 'href="' + local_policy + '"').replace('↗', '→')
        text = re.sub(r'<a\b[^>]*href="' + re.escape(policy_url) + r'"[^>]*>[\s\S]*?</a>', policy_link, text)
        text = text.replace('Editorial review policy ↗', 'Editorial review policy →')
        text = text.replace('href="' + policy_url + '">Editorial policy</a>', 'href="' + local_policy + '">Editorial policy</a>')
        text, count = re.subn(r'<nav\b(?=[^>]*\bid="primary-nav")[^>]*>[\s\S]*?</nav>', lambda _: navigation(page, docs), text)
        if count != 1:
            raise ValueError('Expected one shared navigation: ' + str(page))
        if page == docs/'evidence/index.html':
            annotation = '<script type="application/json" id="inspection-data">' + inline_json(inspection_index(data)) + '</script>'
            if 'id="inspection-data"' in text:
                text = re.sub(r'<script type="application/json" id="inspection-data">[\s\S]*?</script>', lambda _: annotation, text)
            else:
                text = text.replace('</head>', annotation + '</head>')
            control = '<label for="inspection-filter">Inspection basis (any cited source)<select id="inspection-filter" aria-label="Inspection basis (any cited source)"><option value="">All inspection routes</option>' + ''.join('<option value="' + key + '">' + esc(value) + '</option>' for key, value in LABELS.items()) + '</select></label>'
            if 'id="inspection-filter"' not in text:
                text = text.replace('<div class="library-filters">', '<div class="library-filters">' + control, 1)
            help_text = '<p id="inspection-help">Inspection basis describes recorded access, not source credibility or independent verification. A filter match means at least one directly cited source has that basis; other cited sources may differ. Unspecified routes remain unresolved. <a href="review-notes.md">Review corrections and remaining limits</a>.</p>'
            if 'id="inspection-help"' not in text:
                text = text.replace('</details><div class="search-actions">', help_text + '</details><div class="search-actions">', 1)
            text, count = re.subn(r'(<section\b[^>]*\bid="items"[^>]*>)[\s\S]*?(</section>)', lambda m: m[1] + static_records(data) + m[2], text)
            if count != 1:
                raise ValueError('Expected one Library record container')
            notices = ''.join('<article class="withdrawal-notice" id="' + w['id'] + '"><h3>' + w['id'] + ' — ' + esc(w['status']) + '</h3><p>' + esc(w['reason']) + ' Updated ' + esc(w['date']) + '.</p></article>' for w in data['withdrawals'])
            text = re.sub(r'(<div id="withdrawals">)[\s\S]*?(</div>)', lambda m: m[1] + notices + m[2], text)
        page.write_text(text)

def curation_content(docs):
    source = (docs.parent/'EDITORIAL_REVIEW.md').read_bytes()
    rendered = MarkdownIt('commonmark', {'html': False}).render(source.decode('utf-8'))
    rendered = rendered.replace('href="FOUNDING_GLOSSARY_v1.0.2.md#how-to-read-each-entry"', 'href="../../method/#classification-guide"')
    return source, rendered

def refresh_curation(docs):
    source, rendered = curation_content(docs)
    template = (docs/'evidence/machine/index.html').read_text()
    header = re.search(r'<header class="site-header">[\s\S]*?</header>', template)[0]
    footer = re.search(r'<footer class="site-footer">[\s\S]*?</footer>', template)[0]
    page = docs/'participate/curation/index.html'
    page.parent.mkdir(parents=True, exist_ok=True)
    policy_url = 'https://github.com/ai-governance-trust-commons/vocabulary-commons/blob/main/EDITORIAL_REVIEW.md'
    page.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Editorial Review and Curation | Vocabulary Commons</title><link rel="canonical" href="https://ai-governance-trust-commons.github.io/vocabulary-commons/participate/curation/"><link rel="stylesheet" href="../../assets/style.css"></head><body><a class="skip" href="#content">Skip to main content</a>' + header + '<main id="content" class="wrap prose method"><p class="eyebrow">Participate · Editorial guidance</p><p><a href="../">← Participate in the Commons</a></p><div id="curation-text" data-source-sha256="' + hashlib.sha256(source).hexdigest() + '">' + rendered + '</div><p><a data-policy-source href="' + policy_url + '" rel="noopener noreferrer">View policy source on GitHub ↗</a></p></main>' + footer + '<script defer src="../../assets/app.js"></script></body></html>')
    sitemap = docs/'sitemap.xml'
    text = sitemap.read_text()
    url = 'https://ai-governance-trust-commons.github.io/vocabulary-commons/participate/curation/'
    if url not in text:
        sitemap.write_text(text.replace('</urlset>', '<url><loc>' + url + '</loc></url>\n</urlset>'))
