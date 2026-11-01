'use strict';
(() => {
  const data = JSON.parse(document.getElementById('data').textContent);
  const byId = new Map([...data.sources, ...data.cases, ...data.terms, ...data.evidence].map(r => [r.id, r]));
  const termEdges = data.relationships.filter(r => r.to_id.startsWith('TERM-') && byId.has(r.from_id));
  const selected = new Set();
  const ids = ['search', 'term-filter', 'category-filter', 'publisher-filter', 'relation-filter', 'year-from', 'year-to', 'sort-order', 'group-family'];
  const controls = Object.fromEntries(ids.map(id => [id, document.getElementById(id)]));
  const box = document.getElementById('items');
  const noticeBox = document.getElementById('withdrawals');
  const fields = {search: 'q', 'term-filter': 'term', 'category-filter': 'category', 'publisher-filter': 'publisher', 'relation-filter': 'relation', 'year-from': 'from', 'year-to': 'to', 'sort-order': 'sort'};
  let visible = [];
  const base = 'https://ai-governance-trust-commons.github.io/vocabulary-commons/evidence/';
  const el = (tag, text, parent, cls) => {
    const n = document.createElement(tag);
    if (text !== undefined) n.textContent = text;
    if (cls) n.className = cls;
    if (parent) parent.appendChild(n);
    return n;
  };
  const link = (text, url, parent) => {
    const a = el('a', text, parent);
    if (typeof url === 'string' && url.startsWith('https://')) {
      a.href = url; a.target = '_blank'; a.rel = 'noopener noreferrer';
    }
    return a;
  };
  const shorten = (s, n) => s.length > n ? s.slice(0, n).replace(/\s+\S*$/, '') + '…' : s;
  const edges = id => termEdges.filter(r => r.from_id === id);
  const sources = r => r.source_ids.map(id => byId.get(id));
  const family = r => sources(r)[0].independence_group || sources(r)[0].id;
  const years = r => sources(r).map(s => /^(\d{4})(?:\D|$)/.exec(s.publication_date || '')?.[1]).filter(Boolean).map(Number);
  const latestYear = r => Math.max(0, ...years(r));
  const searchIndex = new Map(data.evidence.map(r => [r.id, [r.id, r.title, r.observation, r.limitations, r.open_questions, r.support_assessment, r.dispute_status, r.evidence_standing, Object.values(r.source_locations).join(' '), r.keywords?.join(' '), byId.get(r.case_id)?.title, byId.get(r.case_id)?.summary, ...sources(r).map(s => [s.title, s.authors?.join(' '), s.publisher, s.issuing_body, s.version_note, s.publication_date, s.url].join(' ')), ...edges(r.id).map(e => [byId.get(e.to_id)?.name, e.explanation].join(' '))].filter(Boolean).join(' ').toLocaleLowerCase()]));
  function options(control, values) {
    for (const value of [...new Set(values)].sort((a, b) => a.localeCompare(b))) {
      const option = el('option', value, control); option.value = value;
    }
  }
  for (const term of [...data.terms].sort((a, b) => a.name.localeCompare(b.name))) {
    const option = el('option', term.name, controls['term-filter']); option.value = term.id;
  }
  options(controls['category-filter'], data.evidence.map(r => r.evidence_standing_label));
  options(controls['publisher-filter'], data.sources.map(s => s.publisher).filter(Boolean));
  options(controls['relation-filter'], termEdges.map(r => r.relationship_type));
  function restore() {
    const p = new URLSearchParams(window.location.search);
    for (const [id, key] of Object.entries(fields)) {
      const c = controls[id], value = p.get(key) || (id === 'sort-order' ? 'id' : '');
      if (c.tagName === 'SELECT') c.value = [...c.options].some(o => o.value === value) ? value : (id === 'sort-order' ? 'id' : '');
      else c.value = value;
    }
    controls['group-family'].checked = p.get('group') === 'family';
    if (Object.keys(fields).some(id => id !== 'search' && id !== 'sort-order' && controls[id].value)) document.getElementById('advanced-filters').open = true;
  }
  function saveState() {
    const p = new URLSearchParams();
    for (const [id, key] of Object.entries(fields)) if (controls[id].value && !(id === 'sort-order' && controls[id].value === 'id')) p.set(key, controls[id].value);
    if (controls['group-family'].checked) p.set('group', 'family');
    const q = p.toString();
    window.history.replaceState(null, '', window.location.pathname + (q ? '?' + q : '') + window.location.hash);
  }
  const tokens = value => (value.match(/"[^"]+"|\S+/g) || []).map(t => t.replace(/^"|"$/g, '').toLocaleLowerCase());
  function matches(r) {
    if (!tokens(controls.search.value).every(word => searchIndex.get(r.id).includes(word))) return false;
    const term = controls['term-filter'].value, relation = controls['relation-filter'].value;
    // A combined term + relationship must describe the same edge.
    if (term === '__unmatched__') { if (edges(r.id).length || relation) return false; }
    else if ((term || relation) && !edges(r.id).some(e => (!term || e.to_id === term) && (!relation || e.relationship_type === relation))) return false;
    if (controls['category-filter'].value && r.evidence_standing_label !== controls['category-filter'].value) return false;
    if (controls['publisher-filter'].value && !sources(r).some(s => s.publisher === controls['publisher-filter'].value)) return false;
    const from = controls['year-from'].value, to = controls['year-to'].value;
    if ((from || to) && !years(r).some(y => (!from || y >= Number(from)) && (!to || y <= Number(to)))) return false;
    return true;
  }
  function selectionStatus() {
    const hiddenCount = [...selected].filter(id => !visible.some(r => r.id === id)).length;
    document.getElementById('selection-count').textContent = selected.size + ' selected' + (hiddenCount ? ' · ' + hiddenCount + ' outside current results' : '');
    for (const id of ['export-csv', 'export-citations', 'clear-selection']) document.getElementById(id).disabled = selected.size === 0;
    document.getElementById('select-visible').disabled = visible.length === 0;
  }
  function addField(dl, name, value) {
    if (!value) return;
    el('dt', name, dl); el('dd', value, dl);
  }
  function renderRecord(r, parent) {
    const a = el('article', undefined, parent, 'evidence-card'); a.id = r.id;
    const head = el('div', undefined, a, 'record-head');
    const label = el('label', undefined, head, 'record-select');
    const checkbox = el('input', undefined, label); checkbox.type = 'checkbox'; checkbox.checked = selected.has(r.id);
    checkbox.setAttribute('aria-label', 'Select ' + r.id + ' for export');
    checkbox.addEventListener('change', () => { checkbox.checked ? selected.add(r.id) : selected.delete(r.id); selectionStatus(); });
    const heading = el('div', undefined, head); el('p', r.id + ' · ' + r.evidence_standing_label, heading, 'record-label');
    el('h2', r.title, heading);
    const ss = sources(r);
    el('p', ss.map(s => s.publisher + ' · ' + (s.publication_date || 'publication date not established')).join(' / '), a, 'record-source');
    el('p', shorten(r.observation, 300), a, 'finding-preview');
    el('p', 'Limits: ' + shorten(r.limitations, 190), a, 'limits-preview');
    const quick = el('div', undefined, a, 'record-actions');
    const permalink = el('a', 'Record link', quick); permalink.href = '#' + r.id;
    const details = el('details', undefined, a, 'record-details');
    el('summary', 'Read finding, limits and sources', details);
    el('p', 'Provisional · ' + (r.verification_status || 'Independent verification not established'), details, 'record-status');
    el('p', r.observation, details);
    const dl = el('dl', undefined, details);
    for (const [name, key] of [['Limits', 'limitations'], ['Commons support assessment', 'support_assessment'], ['Dispute status', 'dispute_status'], ['Open questions', 'open_questions'], ['Original assessment', 'evidence_standing'], ['Relationship scope', 'glossary_fit']]) addField(dl, name, r[key]);
    const c = byId.get(r.case_id); addField(dl, 'Study or case grouping', c.title + ' · ' + c.kind); addField(dl, 'Grouping context', c.summary);
    el('h3', 'Glossary relationships', details);
    const ee = edges(r.id);
    if (!ee.length) el('p', 'No glossary relationship is published. Relevant unmatched evidence is retained without forcing a connection.', details);
    for (const e of ee) {
      const p = el('p', undefined, details), t = byId.get(e.to_id);
      const termLink = el('a', t.name, p);
      // Routes come from the unchanged founding glossary export, not external source URLs.
      termLink.href = '../terms/' + termSlugs.get(t.name) + '/';
      el('span', ' — ' + e.relationship_type + ': ' + e.explanation, p);
    }
    const related = data.relationships.filter(e => (e.from_id === r.id || e.to_id === r.id) && e.from_id.startsWith('EVID-') && e.to_id.startsWith('EVID-'));
    if (related.length) el('h3', 'Related evidence', details);
    for (const e of related) {
      const other = e.from_id === r.id ? e.to_id : e.from_id;
      const p = el('p', e.relationship_type + ': ' + e.explanation + ' ', details), ref = el('a', other, p); ref.href = '#' + other;
    }
    el('h3', 'Original sources', details);
    for (const s of ss) {
      const section = el('div', undefined, details, 'source-entry');
      link(s.title, s.url, section);
      el('p', (s.authors?.length ? s.authors.join(', ') : s.issuing_body || s.publisher) + ' · ' + s.publisher, section);
      el('p', 'Published: ' + (s.publication_date || 'not established') + ' · Source examined: ' + s.access_date, section);
      el('p', 'Supporting location: ' + r.source_locations[s.id], section);
      el('p', s.version_note, section);
      el('p', 'Source inspection: ' + s.verification.status + '. ' + s.verification.scope, section);
      el('p', 'Independent corroboration: ' + s.verification.independent_corroboration, section);
      el('p', 'Disputes: ' + s.verification.dispute_status, section);
      if (s.verification.dispute_check_note) el('p', s.verification.dispute_check_note, section);
      el('p', 'Preservation: ' + (s.preservation.status || 'No preserved source copy recorded'), section);
      if (s.preservation.sha256) el('p', 'SHA-256: ' + s.preservation.sha256 + ' · Captured ' + s.preservation.captured_at, section);
    }
    for (const e of data.relationships.filter(e => e.from_id.startsWith('SRC-') && r.source_ids.some(id => id === e.from_id || id === e.to_id))) {
      el('p', 'Source dependence: ' + byId.get(e.from_id).title + ' / ' + byId.get(e.to_id).title + ' — ' + e.explanation, details, 'dependency-note');
    }
    const correction = 'https://github.com/ai-governance-trust-commons/vocabulary-commons/issues/new?title=' + encodeURIComponent('Evidence Library correction: ' + r.id) + '&body=' + encodeURIComponent('Record: ' + r.id + '\nSource or supporting passage:\nProposed correction and reason:\n');
    link('Report a correction or dispute', correction, details);
    el('p', 'Publication authority: ' + r.publication_record.authority_policy_id, details, 'publication-note');
    el('p', 'Prepared by ' + r.publication_record.prepared_by + ' · ' + r.publication_record.date + ' · Individual human review: ' + r.publication_record.individual_human_review, details, 'publication-note');
  }
  const termSlugs = new Map(JSON.parse(document.getElementById('term-routes').textContent));
  function draw() {
    box.replaceChildren();
    visible = data.evidence.filter(matches);
    const sort = controls['sort-order'].value;
    visible.sort(sort === 'newest' ? (a, b) => latestYear(b) - latestYear(a) || a.id.localeCompare(b.id) : sort === 'oldest' ? (a, b) => (latestYear(a) || 9999) - (latestYear(b) || 9999) || a.id.localeCompare(b.id) : sort === 'title' ? (a, b) => a.title.localeCompare(b.title) : (a, b) => a.id.localeCompare(b.id));
    if (controls['group-family'].checked) {
      const groups = new Map(); for (const r of visible) { if (!groups.has(family(r))) groups.set(family(r), []); groups.get(family(r)).push(r); }
      for (const records of groups.values()) {
        const section = el('section', undefined, box, 'family-group');
        el('h2', sources(records[0])[0].title, section, 'family-heading');
        el('p', records.length + ' matching record' + (records.length === 1 ? '' : 's') + ' · Shared source family; related publications are not independent corroboration.', section, 'family-note');
        for (const r of records) renderRecord(r, section);
      }
    } else for (const r of visible) renderRecord(r, box);
    if (!visible.length) {
      el('h2', 'No evidence records match these choices.', box, 'empty-heading');
      el('p', 'Try fewer words, a different phrase, or clear the filters. Missing results do not establish that no relevant evidence exists.', box);
    }
    const invalidRange = controls['year-from'].value && controls['year-to'].value && Number(controls['year-from'].value) > Number(controls['year-to'].value);
    document.getElementById('count').textContent = invalidRange ? 'The starting publication year must be no later than the ending year.' : visible.length + ' of ' + data.evidence.length + ' published evidence records';
    const active = ['term-filter', 'category-filter', 'publisher-filter', 'relation-filter', 'year-from', 'year-to'].filter(id => controls[id].value).length;
    document.getElementById('filter-label').textContent = 'Filter the collection' + (active ? ' · ' + active + ' active' : '');
    document.getElementById('family-guidance').hidden = !controls['group-family'].checked;
    selectionStatus();
  }
  function clearFilters() {
    for (const id of Object.keys(fields)) controls[id].value = id === 'sort-order' ? 'id' : '';
    controls['group-family'].checked = false;
    saveState(); draw();
  }
  function reveal() {
    const id = window.location.hash.slice(1);
    if (!/^EVID-[0-9]+$/.test(id)) return;
    let target = document.getElementById(id);
    if (!target && data.evidence.some(r => r.id === id)) {
      clearFilters(); target = document.getElementById(id);
      document.getElementById('action-status').textContent = 'Filters cleared to show ' + id + '.';
    }
    if (target) {
      const details = target.querySelector('details'); if (details) details.open = true;
      target.scrollIntoView({block: 'start'});
    } else document.getElementById('action-status').textContent = id + ' is not available in this public release.';
  }
  function download(filename, text, mime) {
    const url = URL.createObjectURL(new Blob([text], {type: mime})), a = document.createElement('a');
    a.href = url; a.download = filename; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  // Neutralize spreadsheet formula prefixes in CSV cells as well as quote separators/newlines.
  const cell = value => { let s = String(value ?? ''); if (/^[\s]*[=+@-]/.test(s)) s = "'" + s; return '"' + s.replace(/"/g, '""') + '"'; };
  const chosen = () => data.evidence.filter(r => selected.has(r.id));
  document.getElementById('export-csv').addEventListener('click', () => {
    const rows = [['Record ID', 'Finding title', 'Source-reported observation', 'Limitations', 'Commons interpretation', 'Reporting category', 'Publication status', 'Independent verification', 'Source titles', 'Authors', 'Original source URLs', 'Publication dates', 'Supporting locations', 'Source family IDs', 'Record URL', 'Dataset version']];
    for (const r of chosen()) rows.push([r.id, r.title, r.observation, r.limitations, r.support_assessment, r.evidence_standing_label, 'Provisional', r.verification_status, sources(r).map(s => s.title).join(' | '), sources(r).map(s => s.authors?.join('; ') || s.issuing_body).join(' | '), sources(r).map(s => s.url).join(' | '), sources(r).map(s => s.publication_date || 'Not established').join(' | '), sources(r).map(s => r.source_locations[s.id]).join(' | '), sources(r).map(s => s.independence_group || s.id).join(' | '), base + '#' + r.id, data.dataset_version]);
    download('Commons-evidence-selection.csv', '\uFEFF' + rows.map(row => row.map(cell).join(',')).join('\r\n'), 'text/csv;charset=utf-8');
    document.getElementById('action-status').textContent = selected.size + ' selected records exported with findings, limitations and citations.';
  });
  document.getElementById('export-citations').addEventListener('click', () => {
    const ss = new Map(chosen().flatMap(r => sources(r).map(s => [s.id, s])));
    const text = 'Governance & Trust Vocabulary Commons — Evidence Library\nDataset ' + data.dataset_version + '\nSelected records: ' + chosen().map(r => r.id).join(', ') + '\nProvisional inclusion; underlying findings not independently verified by the Commons. Source versions and shared families are not independent corroboration.\n\n' + [...ss.values()].map(s => (s.authors?.join('; ') || s.issuing_body || s.publisher) + '. ' + s.title + '. ' + (s.publication_date || 'Date not established') + '. ' + s.publisher + '.\n' + s.url + '\nVersion/dependence notes: ' + s.version_note).join('\n\n');
    download('Commons-source-reading-list.txt', text, 'text/plain;charset=utf-8');
    document.getElementById('action-status').textContent = ss.size + ' unique source records exported. Shared research families may contain multiple source records.';
  });
  document.getElementById('select-visible').addEventListener('click', () => { for (const r of visible) selected.add(r.id); draw(); });
  document.getElementById('clear-selection').addEventListener('click', () => { selected.clear(); draw(); });
  document.getElementById('clear-filters').addEventListener('click', clearFilters);
  document.getElementById('share-search').addEventListener('click', async () => {
    saveState(); const url = new URL(window.location.href); url.hash = '';
    try { await navigator.clipboard.writeText(url.href); document.getElementById('action-status').textContent = 'Search link copied.'; }
    catch { const field = document.getElementById('share-url'); field.hidden = false; field.value = url.href; field.focus(); field.select(); document.getElementById('action-status').textContent = 'Copy the search link from the field below.'; }
  });
  let timer;
  controls.search.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(() => {saveState(); draw();}, 160); });
  document.getElementById('search-form').addEventListener('submit', e => { e.preventDefault(); clearTimeout(timer); saveState(); draw(); });
  for (const id of ids.filter(id => id !== 'search')) controls[id].addEventListener('change', () => {saveState(); draw();});
  window.addEventListener('popstate', () => {restore(); draw(); reveal();});
  window.addEventListener('hashchange', reveal);
  document.getElementById('notice').textContent = data.notice;
  document.getElementById('release').textContent = 'Dataset ' + data.dataset_version + ' · ' + data.evidence.length + ' published records · ' + data.sources.length + ' source records. Counts are not independent studies or incidents.';
  for (const w of data.withdrawals || []) {
    const a = el('article', undefined, noticeBox, 'withdrawal-notice'); a.id = w.id;
    el('h3', w.id + ' — ' + w.status, a); el('p', w.reason + ' Updated ' + w.date + '; identifier and private history retained.', a);
  }
  restore(); draw(); reveal();
})();
