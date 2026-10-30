/* Progressive enhancement: all glossary entries are rendered in static HTML. */
(() => {
 'use strict';
 const toggle=document.querySelector('.nav-toggle');
 const nav=document.querySelector('#primary-nav');
 if(toggle && nav) toggle.addEventListener('click',()=>{
   const open=toggle.getAttribute('aria-expanded')==='true';
   toggle.setAttribute('aria-expanded',String(!open));
   nav.classList.toggle('open',!open);
 });
 const search=document.querySelector('#term-search');
 const vocab=document.querySelector('#vocab-filter');
 const claim=document.querySelector('#claim-filter');
 const kind=document.querySelector('#kind-filter');
 const list=document.querySelector('#term-list');
 if(!search||!vocab||!claim||!kind||!list)return;
 const items=Array.from(list.querySelectorAll('.term-item'));
 const count=document.querySelector('#results-count');
 const empty=document.querySelector('#no-results');
 function filter(){
   const words=search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
   let hits=0;
   items.forEach(item=>{
     const text=item.dataset.search||'';
     const match=words.every(word=>text.includes(word))&&(!vocab.value||item.dataset.vocabulary===vocab.value)&&(!claim.value||item.dataset.claim===claim.value)&&(!kind.value||item.dataset.kind===kind.value);
     item.hidden=!match;if(match)hits++;
   });
   if(count)count.textContent=`${hits} ${hits===1?'term':'terms'}`;
   if(empty)empty.hidden=hits!==0;
 }
 search.addEventListener('input',filter);
 vocab.addEventListener('change',filter);
 claim.addEventListener('change',filter);
 kind.addEventListener('change',filter);
})();

