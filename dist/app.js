/* Small replacement for the original platform runtime. No forms, analytics or credentials. */
(()=>{
'use strict';
const ROOT=new URL('./',document.currentScript.src).pathname;
const body=document.body,header=document.querySelector('#header');
function measureHeader(){const first=document.querySelector('main .page-section');if(header&&first)first.style.paddingTop=header.offsetHeight+'px';}
measureHeader();window.addEventListener('resize',measureHeader);document.fonts?.ready.then(measureHeader);
const menu=document.querySelector('.header-menu');
menu?.querySelector('[data-folder="root"]')?.classList.add('header-menu-nav-folder--active');
function closeMenu(){body.classList.remove('header--menu-open');document.querySelectorAll('.header-burger-btn').forEach(b=>{b.classList.remove('burger--active');b.setAttribute('aria-expanded','false');});}
document.querySelectorAll('.header-burger-btn').forEach(b=>b.addEventListener('click',()=>{const open=!body.classList.contains('header--menu-open');body.classList.toggle('header--menu-open',open);document.querySelectorAll('.header-burger-btn').forEach(x=>{x.classList.toggle('burger--active',open);x.setAttribute('aria-expanded',String(open));});}));
document.querySelectorAll('.header-nav-folder-title').forEach(b=>b.addEventListener('click',()=>{const open=b.getAttribute('aria-expanded')!=='true';b.setAttribute('aria-expanded',String(open));b.parentElement.classList.toggle('static-folder-open',open);}));
document.querySelectorAll('.header-menu [data-folder-id]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();const target=a.dataset.folderId;menu.querySelectorAll('[data-folder]').forEach(f=>f.classList.toggle('header-menu-nav-folder--active',f.dataset.folder===target));}));
document.querySelectorAll('.header-menu [data-action="back"]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();menu.querySelectorAll('[data-folder]').forEach(f=>f.classList.toggle('header-menu-nav-folder--active',f.dataset.folder==='root'));}));
document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeMenu();document.querySelectorAll('.static-folder-open').forEach(f=>f.classList.remove('static-folder-open'));document.querySelectorAll('.header-nav-folder-title').forEach(b=>b.setAttribute('aria-expanded','false'));}});
function layoutGrids(){document.querySelectorAll('.gallery-grid').forEach(g=>{const w=g.querySelector('.gallery-grid-wrapper');if(!w)return;const n=window.innerWidth<=767?2:Number(g.dataset.columns||5),gap=Number(g.dataset.gutter||29)/20;w.style.cssText=`grid-template-columns:repeat(${n},1fr);gap:${gap}vw;width:auto`;g.querySelectorAll('.gallery-grid-item').forEach(i=>i.dataset.show='true');});}
layoutGrids();window.addEventListener('resize',layoutGrids);
// Match source masonry column proportions without relying on Squarespace JavaScript.
function layoutMasonry(){document.querySelectorAll('.gallery-masonry').forEach(g=>{let p={};try{p=JSON.parse(g.dataset.props||'{}');}catch{}const gs=getComputedStyle(g),width=g.clientWidth-parseFloat(gs.paddingLeft)-parseFloat(gs.paddingRight),gap=p.gutter||20,n=window.innerWidth<=767?2:(p.numColumns||3),col=(width-gap*(n-1))/n,heights=Array(n).fill(0);const wrapper=g.querySelector('.gallery-masonry-wrapper');if(!wrapper)return;g.querySelectorAll('.gallery-masonry-item').forEach(item=>{const img=item.querySelector('img'),c=heights.indexOf(Math.min(...heights)),ratio=(Number(img?.getAttribute('height'))||1)/(Number(img?.getAttribute('width'))||1);item.style.cssText=`position:absolute;left:${c*(col+gap)}px;top:${heights[c]}px;width:${col}px;opacity:1;transform:none`;const w=item.querySelector('.gallery-masonry-item-wrapper');if(w)w.style.height=col*ratio+'px';heights[c]+=col*ratio+gap;});wrapper.style.height=Math.max(...heights)-gap+'px';g.style.opacity='1';});}
layoutMasonry();window.addEventListener('resize',layoutMasonry);
document.querySelectorAll('.gallery-fullscreen-slideshow').forEach(g=>{const slides=[...g.querySelectorAll('.gallery-fullscreen-slideshow-item')];let i=0;function show(n){i=(n+slides.length)%slides.length;slides.forEach((s,k)=>{s.dataset.active=String(i===k);s.dataset.in=String(i===k);});}if(slides.length){show(0);g.querySelector('[data-next]')?.addEventListener('click',()=>show(i+1));g.querySelector('[data-previous]')?.addEventListener('click',()=>show(i-1));if(slides.length>1&&!matchMedia('(prefers-reduced-motion: reduce)').matches)setInterval(()=>show(i+1),5000);}});
// The only editable fields are preserved source text blocks. Preview drafts stay in this browser.
function safeHTML(html){const t=document.createElement('template');t.innerHTML=html;
 t.content.querySelectorAll('script,iframe,object,embed,form,input,button,textarea,select,meta,link,base,style,svg,math').forEach(n=>n.remove());
 for(const el of t.content.querySelectorAll('*'))for(const a of [...el.attributes]){
  if(/^on/i.test(a.name)||['srcdoc','contenteditable'].includes(a.name))el.removeAttribute(a.name);
  else if(['href','src','action','xlink:href'].includes(a.name)&&! /^(https?:|mailto:|tel:|#|\/|\.\/|\.\.\/)/i.test(a.value.trim()))el.removeAttribute(a.name);
  else if(a.name==='style'&&/url\s*\(|expression\s*\(|@import/i.test(a.value))el.removeAttribute(a.name);
 }if(ROOT!=='/')t.content.querySelectorAll('a[href^="/"]').forEach(a=>{const h=a.getAttribute('href');if(!h.startsWith('//')&&!h.startsWith(ROOT))a.setAttribute('href',ROOT+h.slice(1));});return t.innerHTML;
}
async function content(){try{let d;const draft=new URLSearchParams(location.search).get('draft')==='1';if(draft)d=JSON.parse(sessionStorage.getItem('josh-fidelity-draft')||'null');if(!d){const r=await fetch(ROOT+'content.json');if(r.ok)d=await r.json();}if(d?.schema!==2)return;for(const b of d.pages[body.dataset.pageSlug]||[]){const target=document.querySelector(`[data-content-block="${CSS.escape(b.id)}"]`);if(target)target.innerHTML=safeHTML(b.html);}measureHeader();}catch{}}
content();
})();
