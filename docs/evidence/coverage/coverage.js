(() => {
  'use strict';
  const grid = document.querySelector('.coverage-grid');
  const cards = [...grid.querySelectorAll('.coverage-card')];
  const search = document.getElementById('coverage-search');
  const filter = document.getElementById('coverage-filter');
  const sort = document.getElementById('coverage-sort');
  const filters = new Set([...filter.options].map(o => o.value));
  const sorts = new Set([...sort.options].map(o => o.value));
  document.querySelector('.coverage-controls').hidden = false;
  const params = new URL(window.location.href).searchParams;
  search.value = params.get('q') || '';
  filter.value = filters.has(params.get('show')) ? params.get('show') : 'all';
  sort.value = sorts.has(params.get('sort')) ? params.get('sort') : 'families';
  function draw() {
    const q = search.value.trim().toLocaleLowerCase();
    const numeric = (c, key) => Number(c.dataset[key]);
    const byName = (a,b) => a.dataset.name.localeCompare(b.dataset.name);
    const ordered = [...cards].sort((a,b) => sort.value === 'name' ? byName(a,b) : sort.value === 'most' ? numeric(b,'count')-numeric(a,'count') || byName(a,b) : sort.value === 'fewest' ? numeric(a,'count')-numeric(b,'count') || byName(a,b) : numeric(a,'families')-numeric(b,'families') || numeric(a,'count')-numeric(b,'count') || byName(a,b));
    let visible = 0;
    for (const card of ordered) {
      const matches = card.dataset.name.includes(q) && (filter.value === 'unlinked' ? numeric(card,'count') === 0 : filter.value === 'one-family' ? numeric(card,'families') === 1 : filter.value === 'qualifies' ? numeric(card,'qualifies') > 0 : filter.value === 'challenges' ? numeric(card,'challenges') > 0 : true);
      card.hidden = !matches;
      if (matches) visible++;
      grid.appendChild(card);
    }
    document.getElementById('coverage-results').textContent = visible + ' of ' + cards.length + ' terms shown. Counts describe recorded relationships, not validation.';
    document.getElementById('coverage-empty').hidden = visible !== 0;
    const url = new URL(window.location.href);
    for (const key of ['q','show','sort']) url.searchParams.delete(key);
    if (q) url.searchParams.set('q', search.value.trim());
    if (filter.value !== 'all') url.searchParams.set('show',filter.value);
    if (sort.value !== 'families') url.searchParams.set('sort',sort.value);
    window.history.replaceState(null,'',url.pathname + url.search + url.hash);
  }
  search.addEventListener('input',draw);filter.addEventListener('change',draw);sort.addEventListener('change',draw);
  document.getElementById('coverage-reset').addEventListener('click',() => {search.value='';filter.value='all';sort.value='families';draw();});
  for (const a of document.querySelectorAll('[data-quick]')) a.addEventListener('click',() => {search.value='';filter.value=a.dataset.quick;draw();});
  // Direct term anchors reveal their card even when shared filters exclude it.
  const anchor = window.location.hash.slice(1);
  if (cards.some(c => c.id === anchor)) {search.value='';filter.value='all';}
  draw();
})();
