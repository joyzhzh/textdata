'use strict';
const data=window.CATALOGUE;
const byId=new Map(data.records.map(r=>[r.id,r]));
const familyName=id=>data.families.find(f=>f.id===id).name;
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const link=(url,label)=>/^https?:\/\//.test(url)?`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`:esc(label);
let selected=[];
function option(select,value,label=value){const el=document.createElement('option');el.value=value;el.textContent=label;select.appendChild(el);}
data.families.forEach(f=>option($('family'),f.id,f.name));
[...new Set(data.records.map(r=>r.kind))].sort().forEach(k=>option($('kind'),k));
function render(){
 const query=$('search').value.trim().toLocaleLowerCase();
 selected=data.records.filter(r=>(!$('family').value||r.family===$('family').value)&&(!$('kind').value||r.kind===$('kind').value)&&(!$('basis').value||r.evidence_basis===$('basis').value)&&(!query||[r.id,r.name,familyName(r.family),r.kind,r.mechanism,r.evidence,r.limitations,r.textdata_use,r.textdata_evaluation,r.source_version,r.credit].join(' ').toLocaleLowerCase().includes(query)));
 $('count').textContent=`${selected.length} of ${data.records.length} entries`;
 $('empty').hidden=selected.length>0;
 $('download').disabled=selected.length===0;
 $('cards').innerHTML=selected.map(r=>`<article class="card"><span class="number">${esc(r.id.slice(3))}</span><div><h3><button type="button" data-open="${r.id}">${esc(r.name)}</button></h3><p>${esc(r.mechanism)}</p><div class="meta"><span>${esc(familyName(r.family))}</span><span>${esc(r.kind)}</span><span class="origin">${esc(r.evidence_basis)}</span></div></div><button class="arrow" type="button" data-open="${r.id}" aria-label="Open ${esc(r.name)}">↗</button></article>`).join('');
}
function setView(view,changeHash=true){
 if(!['catalogue','reader','downloads'].includes(view))return;
 document.querySelectorAll('.view').forEach(el=>{el.hidden=el.id!==view;el.classList.toggle('active',el.id===view);});
 document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));
 if(changeHash)history.replaceState(null,'','#'+view);
}
function section(title,body){return `<section class="detail-section"><h3>${esc(title)}</h3>${body}</section>`;}
function openProfile(id,changeHash=true){
 const r=byId.get(id);if(!r)return;
 setView('catalogue',false);$('detail-id').textContent=r.id+' · '+r.evidence_basis;
 $('detail-body').innerHTML=`<p class="detail-family">${esc(familyName(r.family))} · ${esc(r.kind)}</p><h2 id="detail-title">${esc(r.name)}</h2><p class="detail-lead">${esc(r.mechanism)}</p><div class="detail-links">${link(r.primary_url,'Publication / documentation ↗')}${r.repository_urls.map((u,i)=>link(u,'Repository'+(r.repository_urls.length>1?' '+(i+1):'')+' ↗')).join('')}<a href="#${r.id}">Entry link ↗</a></div>`
 +section('Evidence',`<p>${esc(r.evidence)}</p><p class="small"><strong>${esc(r.evidence_basis)}.</strong> ${esc(r.reading_scope)}</p>`)
 +section('Limitations',`<p>${esc(r.limitations)}</p>`)
 +section('Relevance to TextData',`<p>${esc(r.textdata_use)}</p><p><strong>Evaluation question:</strong> ${esc(r.textdata_evaluation)}</p>`)
 +section('Version and credit',`<p>${esc(r.source_version)}</p><p class="small">${esc(r.primary_locator)}</p><p>${esc(r.credit)}</p><p class="small">${esc(r.implementation_status)}</p>`)
 +section('References',`<ul>${r.references.map(m=>`<li>${link(m.url,m.version||'Publication / documentation')}<span class="source-meta">${esc(m.locator||'See linked reference')}${m.observed_at?'<br>Observed '+esc(m.observed_at):''}</span></li>`).join('')}</ul>`);
 if(!$('detail').open)$('detail').showModal();
 $('detail').scrollTop=0;
 if(changeHash)history.replaceState(null,'','#'+id);
}
function closeProfile(){if($('detail').open)$('detail').close();history.replaceState(null,'','#catalogue');}
function route(){const h=decodeURIComponent(location.hash.slice(1));if(byId.has(h))openProfile(h,false);else if(['catalogue','reader','downloads'].includes(h)){if($('detail').open)$('detail').close();setView(h,false);}}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>setView(b.dataset.view)));
['search','family','kind','basis'].forEach(id=>$(id).addEventListener(id==='search'?'input':'change',render));
$('reset').addEventListener('click',()=>{['search','family','kind','basis'].forEach(id=>$(id).value='');render();});
$('cards').addEventListener('click',e=>{const b=e.target.closest('[data-open]');if(b)openProfile(b.dataset.open);});
$('close').addEventListener('click',closeProfile);
$('detail').addEventListener('cancel',()=>history.replaceState(null,'','#catalogue'));
$('detail').addEventListener('click',e=>{if(e.target===$('detail')){const r=$('detail').getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)closeProfile();}});
$('download').addEventListener('click',()=>{
 const familyIds=new Set(selected.map(r=>r.family));
 const payload={schema_version:data.schema_version,title:data.title,as_of:data.as_of,scope:data.scope,selection:{query:$('search').value,family:$('family').value,kind:$('kind').value,evidence_basis:$('basis').value},families:data.families.filter(f=>familyIds.has(f.id)),records:selected};
 const blob=new Blob([JSON.stringify(payload,null,2)+'\n'],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='textdata-agent-design-selection.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
$('print').addEventListener('click',()=>window.print());
$('families').innerHTML=data.families.map(f=>`<div class="family"><b>${esc(f.name)} <span class="category-count">${data.records.filter(r=>r.family===f.id).length} entries</span></b>${esc(f.question)}</div>`).join('');
window.addEventListener('hashchange',route);render();route();
