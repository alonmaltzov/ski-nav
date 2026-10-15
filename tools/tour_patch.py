"""First-time tour: the guide walks you through the real screen in 5 steps (replaces the 3 setup screens)."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()

# --- CSS: drop the old setup screens, add the tour
a = s.index('.onb{position:fixed'); z = s.index('.ocard small{color:var(--muted)}') + len('.ocard small{color:var(--muted)}')
s = s[:a] + r'''.onb{position:fixed;inset:0;z-index:2700}
.onb[hidden]{display:none}
.tdim{position:absolute;inset:0;width:100%;height:100%}
.tring{position:absolute;border:3px solid #ff8a3d;box-shadow:0 0 0 7px rgba(255,138,61,.3);pointer-events:none;transition:all .25s ease}
.thero{position:absolute;left:0;right:0;top:calc(70px + env(safe-area-inset-top,0px));display:flex;justify-content:center}
.thero[hidden]{display:none}
.tglow{width:150px;height:150px;border-radius:50%;background:rgba(255,138,61,.18);box-shadow:0 0 0 18px rgba(255,138,61,.1);display:flex;align-items:center;justify-content:center}
.tglow svg{width:120px;height:120px}
.onb.blur .tdimrect{fill:rgba(11,22,32,.72)}
.tbub{position:absolute;left:12px;right:12px;max-width:440px;margin:0 auto;background:var(--panel);color:var(--ink);border-radius:22px;box-shadow:0 14px 40px rgba(0,0,0,.35);padding:14px 16px 12px;transition:top .25s ease}
.ttail{position:absolute;width:20px;height:20px;background:var(--panel);transform:rotate(45deg);border-radius:3px}
.thead{display:flex;align-items:center;gap:10px;position:relative}
.tav{width:52px;height:52px;border-radius:50%;flex:none;box-shadow:0 0 0 2px var(--line);display:flex;align-items:center;justify-content:center}
.onb.talking .tav{box-shadow:0 0 0 3px #ff8a3d,0 0 0 8px rgba(255,138,61,.25)}
.tav svg{width:50px;height:50px}
.tmeta{flex:1;display:grid;gap:6px}
.tdots{display:flex;gap:5px}.tdots i{width:7px;height:7px;border-radius:4px;background:var(--line)}.tdots i.on{background:var(--ink)}.tdots i.cur{width:18px}
.tstat{display:flex;align-items:center;gap:7px;font-size:.8rem;font-weight:700;color:var(--muted);min-height:18px}
.twave{display:none;gap:2px;align-items:center;height:16px}.twave i{width:3px;border-radius:2px;background:#ff8a3d;height:6px}
.onb.talking .twave{display:flex}.onb.talking .twave i{animation:twv .9s ease-in-out infinite}
.twave i:nth-child(2){animation-delay:.15s!important}.twave i:nth-child(3){animation-delay:.3s!important}.twave i:nth-child(4){animation-delay:.45s!important}
@keyframes twv{0%,100%{height:5px}50%{height:16px}}
.tskip{border:none;background:none;color:var(--muted);font:600 .95rem var(--f-ui);align-self:flex-start;padding:4px 0 8px 8px;min-height:36px}
.ttxt{font-size:1.1rem;line-height:1.38;margin-top:8px}
.tnote{font-size:.85rem;color:var(--muted);margin-top:6px}.tnote:empty{display:none}
.tchips{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}.tchips:empty{display:none}
.tchips span{display:flex;align-items:center;gap:6px;height:34px;border-radius:17px;background:var(--bg);padding:0 11px;font-size:.88rem;font-weight:700}
.tbtns{display:flex;justify-content:flex-end;gap:8px;margin-top:10px}
.tbtns .btn{min-height:46px}
#tourReplay{width:46px;padding:0;display:flex;align-items:center;justify-content:center}''' + s[z:]

# --- markup
FACE = '<svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="64" r="44" fill="#fff" stroke="#d6e0e8" stroke-width="2"/><path d="M22 50 Q60 30 98 50 L98 44 Q60 22 22 44 Z" fill="#0b1620"/><rect x="30" y="30" width="60" height="20" rx="10" fill="#ff8a3d" stroke="#0b1620" stroke-width="3"/><rect x="36" y="34" width="22" height="12" rx="6" fill="#ffd0a8"/><rect x="62" y="34" width="22" height="12" rx="6" fill="#ffd0a8"/><circle cx="47" cy="58" r="4.5" fill="#2b3640"/><circle cx="73" cy="58" r="4.5" fill="#2b3640"/><circle cx="38" cy="70" r="5" fill="#ffc9c9" opacity=".8"/><circle cx="82" cy="70" r="5" fill="#ffc9c9" opacity=".8"/><ellipse cx="60" cy="78" rx="10" ry="7" fill="#7a1f2b"/><ellipse cx="60" cy="81" rx="6" ry="3" fill="#e5687a"/><path d="M28 96 Q60 112 92 96 L94 106 Q60 122 26 106 Z" fill="#d81f26"/></svg>'
a = s.index('<div class="onb" id="onb" hidden>'); z = s.index('<div class="sheet" id="todaySheet"')
s = s[:a] + '''<div class="onb" id="onb" hidden>
  <svg class="tdim" aria-hidden="true"><defs><mask id="tourMask"><rect width="100%" height="100%" fill="#fff"/><g id="tourHoles"></g></mask></defs><rect class="tdimrect" width="100%" height="100%" fill="rgba(11,22,32,.62)" mask="url(#tourMask)"/></svg>
  <div id="tourRings"></div>
  <div class="thero" id="tourHero" hidden><div class="tglow">''' + FACE + '''</div></div>
  <div class="tbub" id="tourBub" role="dialog" aria-modal="true" aria-label="Quick tour">
    <span class="ttail" id="tourTail"></span>
    <div class="thead"><div class="tav">''' + FACE + '''</div><div class="tmeta"><div class="tdots" id="tourDots"></div><div class="tstat"><span class="twave"><i></i><i></i><i></i><i></i></span><span id="tourStat"></span></div></div><button class="tskip" id="tourSkip" type="button">Skip</button></div>
    <div class="ttxt" id="tourTxt" aria-live="polite"></div><div class="tnote" id="tourNote"></div><div class="tchips" id="tourChips"></div>
    <div class="tbtns"><button class="btn ghost" id="tourReplay" type="button" aria-label="Say it again"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/></svg></button><button class="btn primary" id="tourNext" type="button">Next</button></div>
  </div>
</div>

''' + s[z:]

# --- settings row
old = '<button class="grow link" id="gamesBtn" type="button">Games</button>'
assert old in s
s = s.replace(old, old + '\n        <button class="grow link" id="tourBtn" type="button">Replay the tour</button>', 1)

# --- logic: replace showOnb .. o3Go
a = s.index('/* ---- first open ---- */'); z = s.index('/* the iPhone opened the app from the 8:30 notification */')
s = s[:a] + r'''/* ---- first open: the guide walks you through the real screen ---- */
const TOUR=[
  { hero:true, next:'Allow location',
    say:(o)=>(o.name ? 'Hi '+o.name+', welcome to '+CONFIG.title+'. ' : 'Hi, I’m your guide. ')+'Quick tour, 30 seconds. First: allow location and pick Always, so I can follow your runs with the phone in your pocket.',
    html:(o)=>(o.name ? '<b>Hi '+esc(o.name)+', welcome to '+esc(CONFIG.title)+'.</b> ' : '<b>Hi, I’m your guide.</b> ')+'Quick tour, 30 seconds.<br>First: allow location and pick <b>Always</b>, so I can follow your runs with the phone in your pocket.',
    note:'Only after you tap Start skiing. Only your group sees your dot.',
    go(){ if(NATIVE) toNative({cmd:'locate'}); else if(navigator.geolocation) navigator.geolocation.getCurrentPosition(()=>{},()=>{}); } },
  { el:['homeSum','legend'],
    say:()=>'This is today. Thick lines are today’s runs, the arrows show the way, and we finish at '+DAY.end.name+'.',
    html:()=>'This is <b>today</b>. Thick lines are today’s runs, the arrows show the way, and we finish at <b>'+esc(DAY.end.name)+'</b>.' },
  { el:['goBtn'], el2:['wxPill'],
    say:()=>'Every morning at '+bset().time+' I play the brief, up top. Then tap Start skiing and put the phone away. I’ll call out every lift and run.',
    html:()=>'Every morning at '+esc(bset().time)+' I play <b>the brief</b> up top. Then tap <b>Start skiing</b> and put the phone away. I’ll call out every lift and run.' },
  { el:['legend'], el2:['runsListBtn','progClose'], prog:true,
    say:()=>'Runs shows the whole week. Each colour is a day, and the bars show what’s left to ski. Route plays the day on the map.',
    html:()=>'<b>Runs</b> shows the whole week. Each colour is a day, and the bars show what’s left to ski. <b>Route</b> plays the day on the map.' },
  { el:['fitBtn'], next:'Let’s ski',
    say:()=>'Tap All to see the crew on the map. And three games run by themselves: STOPPP, the passport race, and Speed King.',
    html:()=>'Tap <b>ALL</b> to see the crew on the map. And 3 games run by themselves:',
    chips:['🥃 STOPPP','🇨🇭 Passport race','👑 Speed King'] }
];
const tour={i:-1, o:{}, voice:false};
function esc(t){ return String(t).replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function tourRect(ids){
  let r=null;
  for(const id of ids||[]){ const e=$(id); if(!e || e.hidden || !e.offsetParent) continue; const b=e.getBoundingClientRect(); if(!b.width || !b.height) continue;
    r = r ? {l:Math.min(r.l,b.left), t:Math.min(r.t,b.top), r:Math.max(r.r,b.right), b:Math.max(r.b,b.bottom)} : {l:b.left, t:b.top, r:b.right, b:b.bottom}; }
  return r && {x:r.l-4, y:r.t-4, w:r.r-r.l+8, h:r.b-r.t+8};
}
function tourPlace(){
  const S=TOUR[tour.i]; if(!S) return;
  const H=innerHeight, W=innerWidth, holes=$('tourHoles'), rings=$('tourRings'), bub=$('tourBub'), tail=$('tourTail');
  holes.textContent=''; rings.textContent='';
  const rs=[tourRect(S.el), tourRect(S.el2)].filter(Boolean);
  rs.forEach(r=>{ const rad=Math.min(18, r.h/2);
    const h=document.createElementNS('http://www.w3.org/2000/svg','rect'); h.setAttribute('x',r.x); h.setAttribute('y',r.y); h.setAttribute('width',r.w); h.setAttribute('height',r.h); h.setAttribute('rx',rad); holes.appendChild(h);
    const g=document.createElement('div'); g.className='tring'; Object.assign(g.style,{left:(r.x-4)+'px', top:(r.y-4)+'px', width:(r.w+2)+'px', height:(r.h+2)+'px', borderRadius:(rad+4)+'px'}); rings.appendChild(g); });
  $('onb').classList.toggle('blur', !!S.hero);
  const bh=bub.offsetHeight, top0=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--sat'))||0;
  let y, side=null, tx=W/2;
  if(S.hero){ y=Math.min(H-bh-20, 250); side='up'; }
  else { const r=rs[0]; tx=r.x+r.w/2;
    if(r.y+r.h/2 > H/2){ y=Math.max(12+top0, r.y-bh-18); side='down'; } else { y=Math.min(H-bh-12, r.y+r.h+18); side='up'; } }
  bub.style.top=y+'px';
  const bl=bub.getBoundingClientRect().left;
  tail.style.left=Math.max(22, Math.min(bub.offsetWidth-42, tx-bl-10))+'px';
  tail.style.top = side==='up' ? '-9px' : ''; tail.style.bottom = side==='down' ? '-9px' : ''; tail.hidden=!side;
}
function tourSay(){ const S=TOUR[tour.i]; if(!S || !tour.voice) return; $('tourStat').textContent='';
  try{ speak([S.say(tour.o)], null, ()=>{ $('tourStat').textContent=''; }); }catch(e){} }
function tourShow(i){
  const prev=TOUR[tour.i]; if(prev && prev.prog && !(TOUR[i]&&TOUR[i].prog) && view==='prog') closeProgress();
  tour.i=i; const S=TOUR[i];
  $('tourHero').hidden=!S.hero;
  const d=$('tourDots'); d.textContent=''; TOUR.forEach((_,k)=>{ const x=document.createElement('i'); if(k<=i) x.className='on'; if(k===i) x.classList.add('cur'); d.appendChild(x); });
  d.setAttribute('aria-label','Step '+(i+1)+' of '+TOUR.length);
  $('tourTxt').innerHTML=S.html(tour.o); $('tourNote').textContent=S.note||'';
  const c=$('tourChips'); c.textContent=''; (S.chips||[]).forEach(t=>{ const x=document.createElement('span'); x.textContent=t; c.appendChild(x); });
  $('tourNext').textContent=S.next||'Next';
  $('onb').hidden=false;
  if(S.prog && view!=='prog') openProgress();
  tourPlace(); setTimeout(tourPlace, S.prog ? 450 : 60);
  tourSay();
}
function showOnb(o){ closeDrawer(); document.querySelectorAll('.sheet,.gsheet').forEach(x=>x.hidden=true); if(view==='prog') closeProgress();
  tour.o=o||{}; tour.voice=NATIVE; tourShow(0); }
function tourEnd(){
  stopSpeak(); const S=TOUR[tour.i]; if(S && S.prog && view==='prog') closeProgress();
  tour.i=-1; $('onb').hidden=true;
  try{ localStorage.setItem(ONB,'1'); }catch(e){} persist(); scheduleBrief(); renderBriefRow();
  setTimeout(sfxToday, 300);
}
$('tourNext').onclick=()=>{ const S=TOUR[tour.i]; tour.voice=true; stopSpeak(); if(S && S.go) S.go(); if(tour.i>=TOUR.length-1) tourEnd(); else setTimeout(()=>tourShow(tour.i+1), S && S.go ? 400 : 0); };
$('tourSkip').onclick=tourEnd;
$('tourReplay').onclick=()=>{ tour.voice=true; tourSay(); };
$('tourBtn').onclick=()=>showOnb();
addEventListener('resize', ()=>{ if(tour.i>=0) tourPlace(); });

''' + s[z:]

# joiners get the tour too, greeted by name
old = "if(grp && !seen && !window.__QA_ACK){ ['o1','o2'].forEach(id=>$(id).hidden=true); $('o3').hidden=false; $('onb').hidden=false; }"
assert old in s
s = s.replace(old, "if(grp && !seen && !window.__QA_ACK) showOnb({name:(grp.name||'').split(' ')[0]});", 1)
s = s.replace("document.querySelectorAll('#bsVoice [data-v=\"default\"], #oVoice [data-v=\"default\"]')", "document.querySelectorAll('#bsVoice [data-v=\"default\"]')")
s = s.replace("document.querySelectorAll('#bsVoice [data-v=\"personal\"], #oVoice [data-v=\"personal\"]')", "document.querySelectorAll('#bsVoice [data-v=\"personal\"]')")
s = s.replace("function setTalking(on){ ['briefSheet','askSheet'].forEach(", "function setTalking(on){ ['briefSheet','askSheet','onb'].forEach(", 1)
s = s.replace('window.__ski = { map, st, ', 'window.__ski = { map, st, tour, tourShow, tourEnd, ', 1)
assert 'oVoice' not in s and "'o3'" not in s, 'old setup screens still referenced'
open(p, 'w', encoding='utf-8').write(s)
print('ok')
