(() => {
  'use strict';
  const search = document.getElementById('path-search');
  if (!search) return;
  const cards = [...document.querySelectorAll('.path-card')];
  document.querySelector('.path-search').hidden = false;
  search.value = new URL(window.location.href).searchParams.get('q') || '';
  function draw() {
    const words = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      card.hidden = !words.every(w => card.dataset.search.includes(w));
      if (!card.hidden) visible++;
    }
    document.getElementById('path-status').textContent = visible + ' of ' + cards.length + ' research paths shown.';
    document.getElementById('path-empty').hidden = visible !== 0;
    const url = new URL(window.location.href);
    if (words.length) url.searchParams.set('q', search.value.trim()); else url.searchParams.delete('q');
    window.history.replaceState(null, '', url.pathname + url.search + url.hash);
  }
  search.addEventListener('input', draw);
  document.getElementById('path-reset').addEventListener('click', () => {search.value = '';draw();search.focus();});
  draw();
})();
