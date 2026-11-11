/* Progressive enhancement: all glossary entries are rendered in static HTML. */
(() => {
 'use strict';
 const toggle=document.querySelector('.nav-toggle');
 const nav=document.querySelector('#primary-nav');
 // Existing generated pages have integrity-managed HTML. Supply the shared
 // Resources link now without rewriting evidence, glossary or research pages.
 // The source builder emits the link directly on subsequent full builds.
 if(nav && !Array.from(nav.querySelectorAll('a')).some(a=>a.textContent.trim()==='Resources')){
   const home=Array.from(nav.querySelectorAll('a')).find(a=>a.textContent.trim()==='Home');
   if(home){
     const link=document.createElement('a');
     link.textContent='Resources';
     link.href=new URL('resources/',home.href).href;
     const questions=Array.from(nav.querySelectorAll('a')).find(a=>a.textContent.trim()==='Explore questions');
     if(questions)nav.insertBefore(link,questions);else nav.appendChild(link);
   }
 }
 if(toggle && nav){
   const setMenuOpen=open=>{
     toggle.setAttribute('aria-expanded',String(open));
     nav.classList.toggle('open',open);
   };
   toggle.addEventListener('click',()=>setMenuOpen(toggle.getAttribute('aria-expanded')!=='true'));
   nav.addEventListener('click',event=>{
     if(event.target.closest('a'))setMenuOpen(false);
   });
   document.addEventListener('keydown',event=>{
     if(event.key==='Escape' && toggle.getAttribute('aria-expanded')==='true'){
       setMenuOpen(false);
       toggle.focus();
     }
   });
   document.addEventListener('click',event=>{
     if(!nav.contains(event.target) && !toggle.contains(event.target))setMenuOpen(false);
   });
   // Collapse only after handlers are installed; failed/disabled JS keeps links usable.
   toggle.closest('.site-header').classList.add('nav-ready');
 }
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

