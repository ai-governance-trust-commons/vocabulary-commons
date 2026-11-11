"""Shared navigation and readable Library records from approved public data."""
import html
import json
import posixpath
import re

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
            parts.append('<li>' + sid + ' · ' + title + '<p>Supporting location: ' + esc(record['source_locations'][sid]) + '</p></li>')
        parts += ['</ul><p><a href="machine/records/' + rid + '.json">Complete record, source-inspection details and relationships (JSON)</a></p>',
                  '<p>Provisional publication; inclusion is not independent verification. Individual human review: ' + esc(record['publication_record']['individual_human_review']) + '.</p></article>']
        records.append(''.join(parts))
    return ''.join(records)

def refresh(docs):
    data = json.loads((docs/'evidence/evidence.json').read_text())
    for page in docs.rglob('*.html'):
        text = page.read_text()
        text, count = re.subn(r'<nav\b(?=[^>]*\bid="primary-nav")[^>]*>[\s\S]*?</nav>', lambda _: navigation(page, docs), text)
        if count != 1:
            raise ValueError('Expected one shared navigation: ' + str(page))
        if page == docs/'evidence/index.html':
            text, count = re.subn(r'(<section\b[^>]*\bid="items"[^>]*>)[\s\S]*?(</section>)', lambda m: m[1] + static_records(data) + m[2], text)
            if count != 1:
                raise ValueError('Expected one Library record container')
            notices = ''.join('<article class="withdrawal-notice" id="' + w['id'] + '"><h3>' + w['id'] + ' — ' + esc(w['status']) + '</h3><p>' + esc(w['reason']) + ' Updated ' + esc(w['date']) + '.</p></article>' for w in data['withdrawals'])
            text = re.sub(r'(<div id="withdrawals">)[\s\S]*?(</div>)', lambda m: m[1] + notices + m[2], text)
        page.write_text(text)
