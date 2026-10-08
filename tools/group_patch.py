"""Group: invite link, join flow, members, friends on the map, meet point, route to a friend, shared plan style."""
import sys, json
PEOPLE = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3.5"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c0-3.5 2.7-6 6-6s6 2.5 6 6M15 14.5c3 0 5.5 2 5.5 5"/></svg>'
BACK = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>'
CHECK = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--ok)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
COLORS = ['#C2410C', '#7C3AED', '#0F766E', '#BE185D', '#A16207', '#1D5FE0']

GROUP_PANE = f'''    <div class="mpane" id="menuGroup" hidden>
      <div class="drawerhead sethead"><button class="xbtn" id="groupBack" type="button" aria-label="Back to the week">{BACK}</button><div><h2>Group</h2><p id="groupSub"></p></div></div>
      <div id="groupStart" class="gcard" hidden>
        <span class="eyebrow">Ski together</span>
        <p class="gtext">Start a group and send your friends a link. Everyone gets the plan and sees each other on the map while skiing.</p>
        <label class="glabel" for="gOwnerName">Your name</label>
        <input id="gOwnerName" class="ginput" maxlength="30" autocomplete="given-name" placeholder="Your name">
        <button class="btn primary gbtn" id="gCreate" type="button">Start a group</button>
        <p class="gerr" id="gStartErr" hidden></p>
      </div>
      <div id="groupOn" hidden>
        <div class="group" id="gMembers"></div>
        <div class="gcard" id="gInvite">
          <span class="eyebrow">Invite friends</span>
          <p class="gtext">Send this link on WhatsApp. They tap it, type their name and they’re in. No password.</p>
          <div class="gcode" id="gLink"></div>
          <div class="ggrid"><button class="btn primary" id="gShare" type="button">Share link</button><button class="btn ghost" id="gCopy" type="button">Copy</button></div>
        </div>
        <button class="grow toggle gtoggle" id="gSharing" type="button" role="switch" aria-pressed="true"><span>Share my location<small>Only while skiing, only with this group</small></span><span class="sw"></span></button>
        <button class="btn ghost" id="gLeave" type="button">Leave group</button>
      </div>
      <p class="gerr" id="gErr" hidden></p>
    </div>
'''

JOIN = f'''<div class="joinflow" id="joinFlow" hidden>
  <div class="jstep" id="j1">
    <div class="jhero"><span class="jlogo" aria-hidden="true"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#FF8A3D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 20l7-11 4 6 3-4 4 9z"/></svg></span>
      <span class="jinv" id="jInviter">You’re invited to</span><h1 id="jTrip">Avoriaz week</h1><span class="jdates" id="jDates"></span></div>
    <div class="jsheet">
      <ul class="jlist"><li><b>The plan for each day</b>, which runs and lifts, on a map that works offline</li><li><b>See where everyone is</b> on the mountain, and find each other</li><li><b>Your speed, km and runs</b> for every day</li></ul>
      <button class="btn primary jbtn" id="jGo1" type="button">Join the trip</button>
      <p class="jnote">Takes 30 seconds. No account or password.</p>
      <p class="gerr" id="jErr1" hidden></p>
    </div>
  </div>
  <div class="jstep jplain" id="j2" hidden>
    <div class="jprog" aria-label="Step 1 of 2"><i class="on"></i><i></i></div>
    <h2>What should we call you?</h2><p class="jsub">Your friends see this name next to your dot on the map.</p>
    <label class="glabel" for="jName">Name</label><input id="jName" class="ginput" maxlength="30" autocomplete="given-name" placeholder="Your name">
    <span class="glabel">Your color on the map</span><div class="jcolors" id="jColors"></div>
    <button class="btn primary jbtn jbottom" id="jGo2" type="button" disabled>Continue</button>
  </div>
  <div class="jstep jplain" id="j3" hidden>
    <div class="jprog" aria-label="Step 2 of 2"><i class="on"></i><i class="on"></i></div>
    <h2>Find each other on the mountain</h2><p class="jsub">Share your location with the group so everyone can see where you are and meet up.</p>
    <ul class="jchecks"><li>{CHECK}Only the people in this trip</li><li>{CHECK}Only while you’re skiing (stops when you tap Stop, and after 6pm)</li><li>{CHECK}Pause any time. It’s all deleted after the trip.</li></ul>
    <div class="jbottom jcol"><button class="btn primary jbtn" id="jShare" type="button">Share my location</button><button class="btn ghost jbtn" id="jNotNow" type="button">Not now</button></div>
    <p class="gerr" id="jErr3" hidden></p>
  </div>
</div>

<div class="sheet" id="friendSheet" hidden>
  <div class="sheetin" role="dialog" aria-label="Friend">
    <div class="fhead"><span class="favatar" id="fAvatar"></span><div class="fwho"><h3 id="fName"></h3><span id="fStatus"></span></div><button class="xbtn" id="fClose" type="button" aria-label="Close">✕</button></div>
    <div class="ftiles"><div class="rtile"><b id="fDist">-</b><span>Away</span></div><div class="rtile"><b id="fEta">-</b><span>To reach</span></div><div class="rtile"><b id="fKm">-</b><span>Today</span></div></div>
    <div class="ggrid"><button class="btn primary" id="fRoute" type="button">Route to them</button><button class="btn ghost" id="fMeet" type="button">Meet here</button></div>
  </div>
</div>

<div class="sheet" id="meetSheet" hidden>
  <div class="sheetin" role="dialog" aria-label="Meeting point">
    <div class="sheethead"><h3 id="meetTitle">Meet here</h3><button class="btn ghost sm" id="meetClose" type="button">Done</button></div>
    <p class="note" id="meetSub" style="margin:0"></p>
    <div class="ggrid"><button class="btn primary" id="meetRoute" type="button">Route there</button><button class="btn ghost" id="meetClear" type="button">Clear</button></div>
  </div>
</div>

<div class="sheet" id="sheet" hidden>'''

CSS = r"""
/* ===== group: join flow, members, friends on the map ===== */
.hbtns .xbtn[aria-pressed="true"]{background:var(--accent);color:#fff}
.gcard{background:var(--panel);border-radius:18px;padding:14px 16px;display:grid;gap:10px}
.gtext{margin:0;font-size:1rem;line-height:1.35}
.glabel{font-size:.8rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
.ginput{height:52px;border-radius:14px;border:2px solid var(--line);background:var(--panel);padding:0 14px;font:600 1.15rem var(--f-ui);color:var(--ink);box-sizing:border-box;width:100%;-webkit-user-select:text;user-select:text}
.ginput:focus{border-color:var(--ink);outline:none}
.gbtn{width:100%}
.gerr{margin:0;color:var(--bad);font-weight:600;font-size:.95rem}
.gcode{height:48px;border-radius:12px;background:var(--bg);display:flex;align-items:center;padding:0 14px;font:600 .95rem var(--f-ui);color:var(--muted);overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.ggrid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.gtoggle{background:var(--panel)!important;border-radius:18px!important}
.mrow{display:flex;align-items:center;gap:12px;min-height:62px;padding:6px 14px;box-sizing:border-box}
.mav{width:40px;height:40px;border-radius:20px;color:#fff;font:700 .95rem var(--f-ui);display:grid;place-items:center;flex:none}
.mwho{flex:1;min-width:0;display:grid}
.mwho b{font-weight:600;font-size:1.05rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mwho span{font-size:.88rem;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mrm{min-height:44px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--bad);font:600 .9rem var(--f-ui);padding:0 10px}
.fdot{display:grid;justify-items:center;cursor:pointer}
.fdot b{width:36px;height:36px;border-radius:18px;color:#fff;font:700 .85rem/36px var(--f-ui);text-align:center;border:3px solid #fff;box-shadow:0 2px 8px rgb(11 22 32/.35);box-sizing:content-box}
.fdot span{margin-top:2px;font:700 .72rem var(--f-ui);background:var(--panel);color:var(--ink);border-radius:6px;padding:1px 5px;white-space:nowrap}
.fdot.old{opacity:.6}
.meetpin{display:grid;justify-items:center;cursor:pointer}
.meetpin b{background:var(--ink);color:var(--panel);font:700 .85rem var(--f-ui);padding:6px 10px;border-radius:10px;white-space:nowrap;box-shadow:0 2px 8px rgb(11 22 32/.3)}
.meetpin i{width:2px;height:12px;background:var(--ink)}
@media (max-width:389px){.drawerhead h2{font-size:1.5rem;white-space:nowrap}.drawerhead .hbtns{gap:6px}}
.tpill.friends{gap:0;padding:0 12px}
.tpill.friends .av{width:24px;height:24px;border-radius:50%;box-sizing:border-box;display:block;border:2px solid var(--panel);margin-left:-8px;flex:none}
.tpill.friends .av:first-child{margin-left:0}
.tpill.friends span{margin-left:6px}
.fhead{display:flex;align-items:center;gap:12px}
.favatar{width:52px;height:52px;border-radius:26px;color:#fff;font:700 1.1rem var(--f-ui);display:grid;place-items:center;flex:none}
.fwho{flex:1;min-width:0;display:grid}
.fwho h3{margin:0;font:800 1.5rem/1.05 var(--f-num)}
.fwho span{font-size:.95rem;color:var(--muted)}
.ftiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.ftiles .rtile b{font-size:1.4rem;white-space:nowrap}
.joinflow{position:fixed;inset:0;z-index:1300;background:var(--bg);overflow:auto}
.jstep{min-height:100%;display:flex;flex-direction:column}
.jhero{flex:1;background:linear-gradient(#4d6f8c,#2e4a63);color:#fff;padding:calc(56px + env(safe-area-inset-top,0px)) 24px 40px;display:flex;flex-direction:column;gap:8px;justify-content:flex-end}
.jlogo{width:56px;height:56px;border-radius:16px;background:#0b1620;display:grid;place-items:center}
.jinv{font-size:1.05rem;font-weight:600;opacity:.9}
.jhero h1{margin:0;font:800 3rem/.95 var(--f-num)}
.jdates{font-size:1.1rem;font-weight:600}
.jsheet{background:var(--panel);border-radius:26px 26px 0 0;margin-top:-24px;padding:24px 20px calc(24px + env(safe-area-inset-bottom,0px));display:grid;gap:16px}
.jlist{margin:0;padding-left:20px;display:grid;gap:10px;font-size:1.05rem;line-height:1.3}
.jbtn{width:100%;min-height:58px;font-size:1.15rem;font-weight:700}
.jbtn.primary{background:var(--ink);color:var(--panel)}
.jbtn[disabled]{opacity:.4}
.jnote{margin:0;text-align:center;color:var(--muted);font-size:.9rem}
.jplain{padding:calc(56px + env(safe-area-inset-top,0px)) 20px calc(24px + env(safe-area-inset-bottom,0px));gap:14px;box-sizing:border-box}
.jplain h2{margin:6px 0 0;font:800 2.2rem/1 var(--f-num)}
.jsub{margin:0;color:var(--muted);font-size:1.05rem;line-height:1.35}
.jprog{display:flex;gap:6px}
.jprog i{flex:1;height:5px;border-radius:3px;background:var(--line)}
.jprog i.on{background:var(--ink)}
.jcolors{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;padding:0 4px}
.jcolors button{width:100%;aspect-ratio:1;max-width:52px;border-radius:50%;border:0}
.jcolors button[aria-pressed="true"]{box-shadow:0 0 0 3px var(--bg),0 0 0 6px var(--ink)}
.jchecks{list-style:none;margin:0;padding:14px 16px;background:var(--panel);border-radius:18px;display:grid;gap:10px;font-size:1rem;line-height:1.3}
.jchecks li{display:flex;gap:10px;align-items:flex-start}
.jchecks svg{flex:none}
.jbottom{margin-top:auto}
.jcol{display:grid;gap:8px}
"""

JS = r"""
/* ---------- group: invite link, join, members, friends on the map ---------- */
const GB = window.__GROUP_BACKEND || CONFIG.group || null;          // {url, key}
const GKEY = 'skinav-group';
const TRIP_NAME = 'Avoriaz week';
const JOIN_BASE = 'https://alonmaltzov.github.io/ski-nav/join.html?c=';
const GCOLORS = __GCOLORS__;
let grp = (()=>{ try{ return JSON.parse(localStorage.getItem(GKEY)||'null'); }catch(e){ return null; } })();
let gstate = null, gTimer = 0, lastPost = 0, friendMarkers = new Map(), meetMarker = null, openFriend = null;
const saveGrp = () => { try{ grp ? localStorage.setItem(GKEY, JSON.stringify(grp)) : localStorage.removeItem(GKEY); }catch(e){} };
const initials = n => (n||'?').trim().split(/\s+/).map(w=>w[0]).join('').slice(0,2).toUpperCase();
const ago = s => s==null ? '' : s < 60 ? 'just now' : s < 3600 ? Math.round(s/60)+' min ago' : Math.round(s/3600)+' h ago';
async function rpc(fn, args){
  if(!GB || !GB.url) throw new Error('The group server isn’t set up yet.');
  const r = await fetch(GB.url.replace(/\/$/,'')+'/rest/v1/rpc/'+fn, {method:'POST', headers:{'apikey':GB.key, 'Authorization':'Bearer '+GB.key, 'Content-Type':'application/json'}, body:JSON.stringify(args||{})});
  const d = await r.json().catch(()=>null);
  if(!r.ok) throw new Error((d && d.message) || ('Server error '+r.status));
  return d;
}
const platform = () => NATIVE ? 'ios' : /android/i.test(navigator.userAgent) ? 'android-web' : 'web';
function tellNative(){ if(NATIVE) toNative({cmd:'group', url:GB&&GB.url||'', key:GB&&GB.key||'', secret: grp ? grp.secret : '', sharing: !!(grp && grp.sharing!==false)}); }

/* members, invite, sharing (menu > people button) */
function showGroup(on){ $('menuMain').hidden=on; $('menuSettings').hidden=true; $('menuGroup').hidden=!on; if(on){ renderGroup(); refreshGroup(); } }
$('groupBtn').onclick=()=>showGroup(true); $('groupBack').onclick=()=>showGroup(false);
function renderGroup(){
  const has = !!grp;
  $('groupStart').hidden = has; $('groupOn').hidden = !has; $('gErr').hidden = true;
  $('groupSub').textContent = has ? TRIP_NAME + (gstate ? ' · '+gstate.members.length+' '+(gstate.members.length===1?'person':'people') : '') : TRIP_NAME;
  if(!has) return;
  $('gLink').textContent = JOIN_BASE + grp.invite_code;
  $('gSharing').setAttribute('aria-pressed', grp.sharing===false ? 'false' : 'true');
  $('gLeave').hidden = !gstate || gstate.role==='owner';
  const box=$('gMembers'); box.textContent='';
  for(const m of (gstate ? gstate.members : [{id:grp.member_id, name:grp.name, color:grp.color, role:grp.role||'member', sharing:grp.sharing!==false}])){
    const row=document.createElement('div'); row.className='mrow';
    const av=document.createElement('span'); av.className='mav'; av.style.background=m.color; av.textContent=initials(m.name);
    const who=document.createElement('span'); who.className='mwho'; const b=document.createElement('b'); b.textContent=m.name+(m.id===grp.member_id?' (you)':''); const s=document.createElement('span');
    const bits=[m.role==='owner'?'Organizer':null];
    if(!m.sharing) bits.push('not sharing location'); else if(m.pos) bits.push((m.pos.on_lift?'on a lift':(m.pos.run?'on '+m.pos.run:'on the mountain'))+' · '+ago(m.pos.age_s)); else bits.push('no location yet');
    s.textContent=bits.filter(Boolean).join(' · '); who.append(b,s); row.append(av,who);
    if(gstate && gstate.role==='owner' && m.id!==grp.member_id){ const rm=document.createElement('button'); rm.type='button'; rm.className='mrm'; rm.textContent='Remove';
      rm.onclick=async()=>{ if(rm.dataset.sure!=='1'){ rm.dataset.sure='1'; rm.textContent='Tap to confirm'; return; } try{ await rpc('remove_member',{p_secret:grp.secret, p_member:m.id}); refreshGroup(); }catch(e){ gErr(e); } };
      row.appendChild(rm); }
    box.appendChild(row);
  }
}
function gErr(e){ const el=$('gErr'); el.textContent=e.message||String(e); el.hidden=false; }
$('gCreate').onclick=async()=>{
  const name=$('gOwnerName').value.trim(); if(!name){ $('gOwnerName').focus(); return; }
  $('gCreate').disabled=true;
  try{ const T=CONFIG.trip&&CONFIG.trip.length ? CONFIG.trip : null; const d=t=>t?t[0]+'-'+String(t[1]+1).padStart(2,'0')+'-'+String(t[2]).padStart(2,'0'):null;
    const r=await rpc('create_trip',{p_name:TRIP_NAME, p_owner_name:name, p_color:'#1D5FE0', p_starts:d(T&&T[0]), p_ends:d(T&&T[T.length-1]), p_platform:platform()});
    grp={...r, name, color:'#1D5FE0', role:'owner', sharing:true}; saveGrp(); tellNative(); await refreshGroup(); renderGroup();
  }catch(e){ const el=$('gStartErr'); el.textContent=e.message; el.hidden=false; }
  $('gCreate').disabled=false;
};
async function shareInvite(){
  const url=JOIN_BASE+grp.invite_code, text='Join our ski trip on Ski Nav: the plan for every day and where everyone is on the mountain. '+url;
  try{ if(navigator.share){ await navigator.share({title:'Ski Nav · '+TRIP_NAME, text, url}); return; } }catch(e){ if(e && e.name==='AbortError') return; }
  try{ await navigator.clipboard.writeText(url); toast('Invite link copied. Paste it in WhatsApp.'); }catch(e){ toast(url); }
}
$('gShare').onclick=shareInvite;
$('gCopy').onclick=async()=>{ try{ await navigator.clipboard.writeText(JOIN_BASE+grp.invite_code); toast('Invite link copied.'); }catch(e){ toast(JOIN_BASE+grp.invite_code); } };
$('gSharing').onclick=async()=>{ const on = grp.sharing===false; try{ await rpc('set_sharing',{p_secret:grp.secret, p_on:on}); grp.sharing=on; saveGrp(); tellNative(); renderGroup(); refreshGroup(); }catch(e){ gErr(e); } };
$('gLeave').onclick=async()=>{ if($('gLeave').dataset.sure!=='1'){ $('gLeave').dataset.sure='1'; $('gLeave').textContent='Tap again to leave'; return; }
  try{ await rpc('remove_member',{p_secret:grp.secret, p_member:grp.member_id}); }catch(e){}
  grp=null; gstate=null; saveGrp(); tellNative(); clearFriends(); renderGroup(); renderFriendsPill(); };

/* join flow: ?join=CODE in the link, or the app opened from the invite */
let joinCode=null, joinColor=GCOLORS[0];
async function startJoin(code){
  joinCode=String(code||'').trim().toUpperCase(); if(!joinCode) return;
  if(grp && grp.invite_code===joinCode){ toast('You’re already in this trip.'); return; }
  $('joinFlow').hidden=false; ['j1','j2','j3'].forEach((id,i)=>$(id).hidden=i!==0); $('jErr1').hidden=true;
  try{ const p=await rpc('trip_preview',{p_code:joinCode}); if(!p) throw new Error('This invite link isn’t valid any more. Ask for a new one.');
    $('jInviter').textContent=(p.organizer||'Your friend')+' invited you to'; $('jTrip').textContent=p.name;
    $('jDates').textContent = p.starts_on ? new Date(p.starts_on+'T12:00').toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric'})+' to '+new Date(p.ends_on+'T12:00').toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric'})+' · Portes du Soleil' : '';
  }catch(e){ $('jErr1').textContent=e.message; $('jErr1').hidden=false; $('jGo1').disabled=true; }
}
const jc=$('jColors'); GCOLORS.forEach((c,i)=>{ const b=document.createElement('button'); b.type='button'; b.style.background=c; b.setAttribute('aria-label','Color '+(i+1)); b.setAttribute('aria-pressed', i===0?'true':'false');
  b.onclick=()=>{ joinColor=c; jc.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed', x===b?'true':'false')); }; jc.appendChild(b); });
$('jGo1').onclick=()=>{ $('j1').hidden=true; $('j2').hidden=false; setTimeout(()=>$('jName').focus(),50); };
$('jName').oninput=()=>{ $('jGo2').disabled=!$('jName').value.trim(); };
$('jGo2').onclick=()=>{ $('j2').hidden=true; $('j3').hidden=false; };
async function finishJoin(share){
  $('jErr3').hidden=true; $('jShare').disabled=$('jNotNow').disabled=true;
  try{ const name=$('jName').value.trim(); const r=await rpc('join_trip',{p_code:joinCode, p_name:name, p_color:joinColor, p_platform:platform()});
    grp={...r, name, color:joinColor, role:'member', sharing:share}; saveGrp();
    if(!share) await rpc('set_sharing',{p_secret:grp.secret, p_on:false});
    tellNative(); $('joinFlow').hidden=true;
    try{ history.replaceState(null,'',location.pathname); }catch(e){}
    if(share){ if(NATIVE) toNative({cmd:'locate'}); else if(navigator.geolocation) navigator.geolocation.getCurrentPosition(()=>{},()=>{}); }
    toast(share ? 'You’re in. Your friends see you while you ski.' : 'You’re in. Turn on location sharing any time in the group menu.');
    refreshGroup();
  }catch(e){ $('jErr3').textContent=e.message; $('jErr3').hidden=false; }
  $('jShare').disabled=$('jNotNow').disabled=false;
}
$('jShare').onclick=()=>finishJoin(true); $('jNotNow').onclick=()=>finishJoin(false);

/* friends on the map */
function clearFriends(){ friendMarkers.forEach(m=>m.remove()); friendMarkers.clear(); if(meetMarker){ meetMarker.remove(); meetMarker=null; } }
function renderFriends(){
  if(!gstate){ clearFriends(); return; }
  const keep=new Set();
  for(const m of gstate.members){ if(m.id===grp.member_id || !m.pos || m.pos.age_s > 3*3600) continue; keep.add(m.id);
    let mk=friendMarkers.get(m.id);
    if(!mk){ const el=document.createElement('div'); el.className='fdot'; el.innerHTML='<b></b><span></span>'; el.onclick=e=>{ e.stopPropagation(); openFriendCard(m.id); };
      mk=new maplibregl.Marker({element:el}).setLngLat([m.pos.lon,m.pos.lat]).addTo(map); friendMarkers.set(m.id, mk); }
    const el=mk.getElement(); el.querySelector('b').style.background=m.color; el.querySelector('b').textContent=initials(m.name);
    const old=m.pos.age_s > 300; el.classList.toggle('old', old); el.querySelector('span').textContent = old ? ago(m.pos.age_s) : m.name.split(' ')[0];
    el.setAttribute('aria-label', m.name+', '+ago(m.pos.age_s)); mk.setLngLat([m.pos.lon,m.pos.lat]); }
  for(const [id,mk] of friendMarkers) if(!keep.has(id)){ mk.remove(); friendMarkers.delete(id); }
  const mt=gstate.meet;
  if(mt){ if(!meetMarker){ const el=document.createElement('div'); el.className='meetpin'; el.innerHTML='<b></b><i></i>'; el.onclick=e=>{ e.stopPropagation(); openMeet(); }; meetMarker=new maplibregl.Marker({element:el, anchor:'bottom'}).setLngLat([mt.lon,mt.lat]).addTo(map); }
    meetMarker.setLngLat([mt.lon,mt.lat]); meetMarker.getElement().querySelector('b').textContent='Meet'+(mt.label?' · '+mt.label:'')+(mt.at_time?' · '+mt.at_time:''); }
  else if(meetMarker){ meetMarker.remove(); meetMarker=null; }
  if(openFriend) fillFriend(openFriend);
}
function renderFriendsPill(){
  let p=$('friendsPill');
  const others = gstate ? gstate.members.filter(m=>m.id!==(grp&&grp.member_id)) : [];
  if(!grp){ if(p) p.hidden=true; return; }
  if(!p){ p=document.createElement('button'); p.type='button'; p.id='friendsPill'; p.className='tpill friends'; p.onclick=()=>{ openDrawer(); showGroup(true); }; $('topPills').appendChild(p); }
  p.hidden=false; p.textContent='';
  if(!others.length){ const s=document.createElement('span'); s.textContent='Invite'; s.style.marginLeft='0'; p.appendChild(s); p.setAttribute('aria-label','Invite friends'); return; }
  others.slice(0,3).forEach(m=>{ const a=document.createElement('i'); a.className='av'; a.style.background=m.color; p.appendChild(a); });
  const live=others.filter(m=>m.pos && m.pos.age_s<300).length; const s=document.createElement('span'); s.textContent=String(others.length); p.appendChild(s);
  p.setAttribute('aria-label', others.length+' friends, '+live+' on the map now');
}
async function refreshGroup(){
  if(!grp || !GB || !GB.url) return;
  try{ gstate=await rpc('trip_state',{p_secret:grp.secret}); grp.role=gstate.role; saveGrp();
    // the organizer's plan style is the group's plan style
    const pv=gstate.trip.plan && gstate.trip.plan.variant;
    if(gstate.role!=='owner' && pv && WEEKS[pv] && pv!==variant){ setVariant(pv); toast('Plan style set by the organizer.'); }
  }catch(e){ if(/not a member/i.test(e.message)){ grp=null; gstate=null; saveGrp(); tellNative(); clearFriends(); toast('You’re no longer in the group.'); } return; }
  renderFriends(); renderFriendsPill(); if(!$('menuGroup').hidden) renderGroup();
}
function groupLoop(){ clearInterval(gTimer); gTimer=setInterval(()=>{ if(document.visibilityState==='visible') refreshGroup(); }, 15000); }

/* friend card: where they are, route to them, meet there */
function openFriendCard(id){ openFriend=id; $('sheet').hidden=true; $('meetSheet').hidden=true; fillFriend(id); $('friendSheet').hidden=false; }
function fillFriend(id){
  const m=gstate && gstate.members.find(x=>x.id===id); if(!m || !m.pos){ $('friendSheet').hidden=true; openFriend=null; return; }
  $('fAvatar').style.background=m.color; $('fAvatar').textContent=initials(m.name); $('fName').textContent=m.name;
  const sp = m.pos.speed!=null && m.pos.speed>0.5 ? Math.round(speedOut(m.pos.speed))+(units==='imp'?' mph':' km/h') : '';
  $('fStatus').textContent=[m.pos.on_lift?'On a lift':(m.pos.run?'On '+m.pos.run:'On the mountain'), sp, ago(m.pos.age_s)].filter(Boolean).join(' · ');
  const me=myPos(); $('fDist').textContent = me ? fmtLen(hav(me,[m.pos.lat,m.pos.lon])) : '-';
  $('fKm').textContent = m.pos.km!=null ? (units==='imp'?(m.pos.km*0.6214).toFixed(1)+' mi':(+m.pos.km).toFixed(1)+' km') : '-';
  const eta = me ? routeTo([m.pos.lat,m.pos.lon], m.name, true) : null; $('fEta').textContent = eta ? eta.minutes+' min' : '-';
}
$('fClose').onclick=()=>{ $('friendSheet').hidden=true; openFriend=null; };
$('friendSheet').onclick=e=>{ if(e.target.id==='friendSheet'){ $('friendSheet').hidden=true; openFriend=null; } };
$('fRoute').onclick=()=>{ const m=gstate.members.find(x=>x.id===openFriend); $('friendSheet').hidden=true; openFriend=null; if(m && m.pos) routeTo([m.pos.lat,m.pos.lon], m.name, false); };
$('fMeet').onclick=async()=>{ const m=gstate.members.find(x=>x.id===openFriend); if(!m||!m.pos) return;
  const t=new Date(Date.now()+15*60e3); const at=t.getHours()+':'+String(Math.round(t.getMinutes()/5)*5%60).padStart(2,'0');
  try{ await rpc('set_meet',{p_secret:grp.secret, p_lat:m.pos.lat, p_lon:m.pos.lon, p_label:m.pos.run && !m.pos.on_lift ? m.pos.run : 'at '+m.name.split(' ')[0], p_at:at}); $('friendSheet').hidden=true; openFriend=null; toast('Meeting point set. Everyone sees it on the map.'); refreshGroup(); }catch(e){ toast(e.message); } };
function openMeet(){ const mt=gstate && gstate.meet; if(!mt) return; $('meetTitle').textContent='Meet'+(mt.label?' '+mt.label:''); 
  $('sheet').hidden=true; $('friendSheet').hidden=true; openFriend=null; const me=myPos(); $('meetSub').textContent=[mt.at_time?'At '+mt.at_time:null, mt.by?'set by '+mt.by:null, me?fmtLen(hav(me,[mt.lat,mt.lon]))+' from you':null].filter(Boolean).join(' · '); $('meetSheet').hidden=false; }
$('meetClose').onclick=()=>{ $('meetSheet').hidden=true; };
$('meetRoute').onclick=()=>{ const mt=gstate.meet; $('meetSheet').hidden=true; if(mt) routeTo([mt.lat,mt.lon], 'the meeting point', false); };
$('meetClear').onclick=async()=>{ try{ await rpc('set_meet',{p_secret:grp.secret, p_lat:null, p_lon:null, p_label:null, p_at:null}); $('meetSheet').hidden=true; refreshGroup(); }catch(e){ toast(e.message); } };

/* route to any point (a friend, the meeting point): same router as Plan from here */
function routeTo(pt, label, estimateOnly){
  const p=myPos(); if(!p){ if(!estimateOnly) showPlanNote('Need your location first: tap ME, then try again.'); return null; }
  if(!RG) RG=buildGraph();
  const src=near(p, 150, v=>BG[RG.vLine[v]][0]==='R' || RG.vIdx[v]===0).map(([v,d])=>[v, 10+d/RG.walkV]);
  let tg=near(pt, 120, v=>RG.usable(v)); if(!tg.length) tg=near(pt, 300, v=>RG.usable(v)); if(!tg.length){ let bv=-1, bd=2000; for(let v=0;v<RG.N;v++){ if(!RG.usable(v)) continue; const d=hav(pt,[RG.vLat[v],RG.vLon[v]]); if(d<bd){ bd=d; bv=v; } } if(bv>=0) tg=[[bv,bd]]; }  // e.g. a friend on a lift: the nearest place you can get to
  if(!src.length || !tg.length){ if(!estimateOnly) showPlanNote('No route on the runs between you and '+label+' right now. They’re '+fmtLen(hav(p,pt))+' away.'); return null; }
  const D=dijkstra(src); let best=null; for(const [v,d] of tg){ const c=D.dist[v]+d/RG.walkV; if(isFinite(c) && (!best||c<best.c)) best={v,c}; }
  if(!best){ if(!estimateOnly) showPlanNote('No way to reach '+label+' on open runs and lifts from here.'); return null; }
  const minutes=Math.max(1,Math.round(best.c/60));
  if(estimateOnly) return {minutes};
  const routed=pathSteps(D, best.v, p); const now=new Date(); let t=now.getHours()*60+now.getMinutes();
  routed.forEach(s=>{ s.at=fmtHM(Math.round(t)%1440); t += (s.type==='lift' ? 4+s.len/270 : s.len/(CONFIG.flat?84:300)); });
  applySteps(steps.slice(0,cur).concat(routed, [{type:'end', name:label.charAt(0).toUpperCase()+label.slice(1), coords:[[pt[0],pt[1],null]], len:0, at:fmtHM(Math.round(t)%1440)}]), cur);
  showPlanNote('Route to '+label+': '+routed.length+' step'+(routed.length===1?'':'s')+', about '+minutes+' min. “Back to original plan” returns to today’s plan.');
  return {minutes, steps:routed.length};
}

/* send my position while I ski (the iPhone app sends it natively, even when locked) */
function postPosition(here, p){
  if(!grp || grp.sharing===false || NATIVE || mode==='off' || !GB || !GB.url) return;
  const n=Date.now(); if(n-lastPost < 20000 || new Date().getHours() >= 18) return; lastPost=n;
  rpc('post_position',{p_secret:grp.secret, p_lat:here[0], p_lon:here[1], p_acc:p.acc||null, p_speed:st.speed||0, p_on_lift:!!st.onLift,
    p_run: st.match ? st.match.name : (steps[cur] && steps[cur].type!=='end' ? stepLabel(steps[cur]).replace(/^(Ski|Take) /,'') : null), p_km: +(st.dist/1000).toFixed(2)}).catch(()=>{});
}
/* organizer's plan style becomes the group's */
const _setVariant = setVariant;
setVariant = function(v){ _setVariant(v); if(grp && gstate && gstate.role==='owner') rpc('set_plan',{p_secret:grp.secret, p_plan:{variant:v}}).catch(()=>{}); };
document.querySelectorAll('#styleSeg button').forEach(b=>b.onclick=()=>setVariant(b.dataset.v));

if(window.__native){ const ev=window.__native.event; window.__native.event=function(name){ if(typeof name==='string' && name.startsWith('join:')){ startJoin(name.slice(5)); return; } return ev.apply(this, arguments); }; }
tellNative(); groupLoop(); refreshGroup(); renderFriendsPill();
{ const q=new URLSearchParams(location.search).get('join') || (location.hash.match(/join=([A-Za-z0-9-]+)/)||[])[1]; if(q) setTimeout(()=>startJoin(q), 300); }
"""

GRAPH_OLD = "        if(d <= ((isEnd(v)||isEnd(u)) ? 35 : 12)) adj[v].push([u, 6+d/walkV, 'w', -1]); } } }\n  return {vLat"
GRAPH_NEW = '        if(d <= ((isEnd(v)||isEnd(u)) ? 35 : 12)) adj[v].push([u, 6+d/walkV, \'w\', -1]); } } }\n  // lift stations often sit a little away from where the run lines end: walk up to 60 m to or from a lift\n  for(let v=0;v<N;v++){ if(BG[vLine[v]][0]!==\'L\' || !isEnd(v)) continue; const a=Math.floor(vLat[v]*1500), o=Math.floor(vLon[v]*1100);\n    for(let da=-2;da<=2;da++) for(let db=-2;db<=2;db++){ const cell=G[(a+da)+\':\'+(o+db)]; if(!cell) continue;\n      for(const u of cell){ if(BG[vLine[u]][0]!==\'R\') continue; const d=hav([vLat[v],vLon[v]],[vLat[u],vLon[u]]);\n        if(d>35 && d<=60){ adj[v].push([u, 6+d/walkV, \'w\', -1]); adj[u].push([v, 6+d/walkV, \'w\', -1]); } } } }\n  // in the city the practice "lifts" (tram, bus) are reached on foot along streets the map doesn\'t have as runs\n  if(flat) for(let v=0;v<N;v++){ if(BG[vLine[v]][0]!==\'L\' || !isEnd(v)) continue; let best=null;\n    for(let u=0;u<N;u++){ if(BG[vLine[u]][0]!==\'R\') continue; const d=hav([vLat[v],vLon[v]],[vLat[u],vLon[u]]); if(d<=1200 && (!best||d<best[1])) best=[u,d]; }\n    if(best && best[1]>35){ const t=6+best[1]*1.3/walkV; adj[v].push([best[0], t, \'w\', -1]); adj[best[0]].push([v, t, \'w\', -1]); } }\n  return {vLat'

def patch(path):
    s = open(path).read()
    s = s.replace(GRAPH_OLD, GRAPH_NEW) if GRAPH_NEW not in s else s
    def rep(old, new, count=1):
        nonlocal s
        n = s.count(old)
        if n != count: sys.exit(f'{path}: expected {count} of {old[:90]!r}, found {n}')
        s = s.replace(old, new)
    rep('<div class="hbtns"><button class="xbtn" id="settingsBtn"', f'<div class="hbtns"><button class="xbtn" id="groupBtn" type="button" aria-label="Group">{PEOPLE}</button><button class="xbtn" id="settingsBtn"')
    rep('    <div class="mpane" id="menuSettings" hidden>', GROUP_PANE + '    <div class="mpane" id="menuSettings" hidden>')
    rep('<div class="sheet" id="sheet" hidden>', JOIN)
    i = s.index('/* ===== redesign: map-first home'); s = s[:i] + CSS + s[i:]
    rep("function showSettings(on){ $('menuMain').hidden=on; $('menuSettings').hidden=!on;", "function showSettings(on){ $('menuMain').hidden=on; $('menuSettings').hidden=!on; if($('menuGroup')) $('menuGroup').hidden=true;")
    rep("function setVariant(v){", "var setVariant = function(v){")
    rep("  selectDay(di); renderMenu(); renderProgress();\n}", "  selectDay(di); renderMenu(); renderProgress();\n};")
    rep("  if(good) addTrail(here, !!st.onLift);", "  if(good) addTrail(here, !!st.onLift);\n  if(good && typeof postPosition==='function') postPosition(here, p);")
    rep("/* expose for automated tests */", JS.replace('__GCOLORS__', json.dumps(COLORS)) + "\n/* expose for automated tests */")
    rep("recap:openRecap,", "recap:openRecap, startJoin, refreshGroup, routeTo, get grp(){return grp;}, get gstate(){return gstate;},")
    open(path, 'w').write(s); print('patched', path)

for p in sys.argv[1:]: patch(p)
