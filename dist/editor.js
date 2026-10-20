'use strict';
const SITE_ROOT=new URL('./',document.currentScript.src).pathname;
const DRAFT_KEY='josh-fidelity-draft',form=document.querySelector('#editor-form'),status=document.querySelector('#status');let data;
function validate(d){
 if(!d||d.schema!==2||!d.pages||typeof d.pages!=='object')throw Error('Use this site’s schema 2 content file. Older preview files are not compatible.');
 for(const page of ['index','events']){
  const blocks=d.pages[page];if(!Array.isArray(blocks)||blocks.length>200)throw Error('Invalid page blocks.');
  const ids=new Set();for(const b of blocks){if(!b||typeof b.id!=='string'||!b.id||ids.has(b.id)||typeof b.label!=='string'||typeof b.html!=='string'||b.html.length>200000)throw Error('Invalid or duplicate content block.');ids.add(b.id);}
 }return d;
}
// Keep text formatting and links, but never execute imported markup in the editor.
function safeHTML(html){const t=document.createElement('template');t.innerHTML=html;
 t.content.querySelectorAll('script,iframe,object,embed,form,input,button,textarea,select,meta,link,base,style,svg,math').forEach(n=>n.remove());
 for(const el of t.content.querySelectorAll('*'))for(const a of [...el.attributes]){
  if(/^on/i.test(a.name)||['srcdoc','contenteditable'].includes(a.name))el.removeAttribute(a.name);
  else if(['href','src','action','xlink:href'].includes(a.name)&&! /^(https?:|mailto:|tel:|#|\/|\.\/|\.\.\/)/i.test(a.value.trim()))el.removeAttribute(a.name);
  else if(a.name==='style'&&/url\s*\(|expression\s*\(|@import/i.test(a.value))el.removeAttribute(a.name);
 }return t.innerHTML;
}
function show(){for(const page of ['index','events']){const root=document.querySelector('#'+page+'-editor');root.replaceChildren();data.pages[page].forEach((block,i)=>{
 const label=document.createElement('label');label.id=page+'-label-'+i;label.textContent=block.label||block.id;
 const box=document.createElement('div');box.className='rich-block';box.contentEditable='true';box.setAttribute('role','textbox');box.setAttribute('aria-multiline','true');box.setAttribute('aria-labelledby',label.id);box.dataset.page=page;box.dataset.index=i;box.innerHTML=safeHTML(block.html);box.dataset.dirty='false';box.addEventListener('input',()=>{box.dataset.dirty='true';});root.append(label,box);
 });}}
function collect(){if(!data)throw Error('Load a content file first.');for(const box of document.querySelectorAll('.rich-block'))if(box.dataset.dirty==='true'){data.pages[box.dataset.page][Number(box.dataset.index)].html=safeHTML(box.innerHTML);}return validate(data);}
async function load(restore=true){try{let saved;try{saved=restore?sessionStorage.getItem(DRAFT_KEY):null;}catch{}if(saved){try{data=validate(JSON.parse(saved));show();status.textContent='Local schema 2 draft restored. It has not been published.';return;}catch{try{sessionStorage.removeItem(DRAFT_KEY);}catch{}}}const r=await fetch(SITE_ROOT+'content.json',{cache:'no-store'});if(!r.ok)throw Error();data=validate(await r.json());show();status.textContent='Published content loaded. Edits remain local until exported and published.';}catch{status.textContent='Could not load schema 2 content. Refresh or import a valid content file.';}}
form.onsubmit=e=>{e.preventDefault();try{const value=collect(),blob=new Blob([JSON.stringify(value,null,2)+'\n'],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='content.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);status.textContent='Downloaded content.json. Commit it to the configured publishing repository, or provide it to your site maintainer. Nothing was committed or published by this editor.';}catch(err){status.textContent=err.message;}};
function preview(path){try{sessionStorage.setItem(DRAFT_KEY,JSON.stringify(collect()));location.href=SITE_ROOT+path.replace(/^\//,'')+'?draft=1';}catch(err){status.textContent='Could not store the local preview. Download your content instead. '+err.message;}}
document.querySelector('#preview-index').onclick=()=>preview('/');document.querySelector('#preview-events').onclick=()=>preview('/events');
document.querySelector('#reset').onclick=()=>{if(confirm('Discard local edits and reload published content?')){try{sessionStorage.removeItem(DRAFT_KEY);}catch{}load(false);}};
document.querySelector('#import').onchange=async e=>{const f=e.target.files[0];if(!f)return;if(f.size>1000000){status.textContent='File is too large. Maximum 1 MB.';return;}try{const imported=validate(JSON.parse(await f.text()));for(const page of ['index','events'])for(const b of imported.pages[page])b.html=safeHTML(b.html);data=imported;show();status.textContent='Imported locally. Review the formatting, preview, then export. The public site is unchanged.';}catch(err){status.textContent=err.message||'Invalid JSON file.';}};
load();
