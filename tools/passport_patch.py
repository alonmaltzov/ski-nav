"""Passport check: on Swiss days a full-screen check you can only leave by sliding "passport's on me";
the crew list shows who has checked, and anyone can nudge the rest."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    assert old in s, old[:80]; s = s.replace(old, new, 1)
SH = re.search(r'<svg class="gface" viewBox="0 0 120 120" aria-hidden="true">.*?</svg>', s, re.S).group(0)
PASS = ('<svg class="pbook" viewBox="0 0 120 150" aria-hidden="true"><rect x="6" y="4" width="108" height="142" rx="12" fill="#B3121B" stroke="#7d0b12" stroke-width="3"/>'
        '<g transform="translate(60 62)"><rect x="-16" y="-32" width="32" height="64" fill="#fff"/><rect x="-32" y="-16" width="64" height="32" fill="#fff"/></g>'
        '<text x="60" y="124" text-anchor="middle" font-family="system-ui,sans-serif" font-weight="800" font-size="13" fill="#FFD7D9" letter-spacing="2">PASSPORT</text></svg>')
rep('<div class="gzfull" id="kingSheet" hidden role="dialog" aria-label="Speed King">', f'''<div class="pfull" id="passSheet" hidden role="dialog" aria-modal="true" aria-labelledby="passTitle">
  <div class="pbody">
    <div class="peb" id="passEb">SWISS DAY</div>
    <div class="pfig">{PASS}<span class="pshai">{SH}</span></div>
    <h2 id="passTitle">Passport check</h2>
    <p class="ptxt" id="passTxt">We cross into Switzerland today.<br><b>Got it on you?</b></p>
    <p class="pnudge" id="passNudged" hidden></p>
  </div>
  <div class="pcrew" id="passCrew"></div>
  <div class="ptrack" id="passTrack"><span class="plabel">Slide: passport’s on me</span><div class="pfill" id="passFill"></div>
    <button class="pknob" id="passKnob" type="button" role="slider" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" aria-label="Slide to confirm your passport is on you"><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M13 6l6 6-6 6"/></svg></button></div>
  <p class="pfoot">No close button. Slide to carry on.</p>
</div>
<div class="sheet" id="passDoneSheet" hidden><div class="sheetin" role="dialog" aria-label="Passports">
  <div class="pdhead"><span class="pdface">{SH}</span><div><h3>Passport: on you ✓</h3><small id="passQuip"></small></div></div>
  <div id="passList"></div>
  <button class="btn ghost" id="passNudge" type="button">Nudge everyone who hasn’t</button>
  <button class="btn primary" id="passOk" type="button">Done</button>
</div></div>
<div class="gzfull" id="kingSheet" hidden role="dialog" aria-label="Speed King">''')
rep('.gzfull{', '''.pfull{position:fixed;inset:0;z-index:2900;background:linear-gradient(180deg,#0B1620,#1b2a38);color:#fff;display:flex;flex-direction:column;padding:calc(44px + env(safe-area-inset-top,0px)) 20px calc(26px + env(safe-area-inset-bottom,0px));gap:14px;overflow:auto}
.pfull[hidden]{display:none}
.pbody{display:flex;flex-direction:column;align-items:center;gap:12px;text-align:center}
.peb{font:800 .8rem var(--f-ui);letter-spacing:.1em;color:#FF8A3D}
.pfig{position:relative}.pbook{width:110px;height:138px;display:block}
.pshai{position:absolute;right:-34px;bottom:-10px;width:66px;height:66px;border-radius:50%;box-shadow:0 0 0 4px #0B1620;overflow:hidden}.pshai svg,.pdface svg{width:100%;height:100%;display:block}
.pfull h2{margin:6px 0 0;font:800 2.6rem/.95 var(--f-num)}
.ptxt{margin:0;font-size:1.1rem;line-height:1.35;color:#C9D3DB}.ptxt b{color:#fff}
.pnudge{margin:0;background:rgba(255,138,61,.18);color:#FFB37A;border-radius:12px;padding:8px 12px;font-weight:700}
.pcrew{display:flex;justify-content:center;align-items:center;gap:10px;flex-wrap:wrap;margin-top:auto}
.pcrew i{position:relative;width:40px;height:40px;border-radius:50%;border:3px solid #fff;display:flex;align-items:center;justify-content:center;font:800 .8rem var(--f-ui);font-style:normal;color:#fff}
.pcrew i.ok::after{content:'✓';position:absolute;right:-5px;bottom:-5px;width:18px;height:18px;border-radius:9px;background:#16A34A;border:2px solid #fff;font-size:.65rem;display:flex;align-items:center;justify-content:center}
.pcrew small{color:#C9D3DB;font-weight:600}
.ptrack{position:relative;height:68px;border-radius:34px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);overflow:hidden;touch-action:none;flex:none}
.plabel{position:absolute;inset:0 16px 0 72px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1.05rem}
.pfill{position:absolute;left:0;top:0;bottom:0;width:0;background:rgba(22,163,74,.85)}
.pknob{position:absolute;left:6px;top:6px;width:56px;height:56px;border-radius:28px;border:none;background:#FF8A3D;color:#0B1620;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(255,138,61,.5);touch-action:none;cursor:grab}
.pknob:focus-visible{outline:3px solid #fff;outline-offset:2px}
.pfoot{margin:0;text-align:center;color:#8193A2;font-size:.85rem}
.pdhead{display:flex;align-items:center;gap:12px}.pdface{width:56px;height:56px;border-radius:50%;overflow:hidden;flex:none}.pdhead h3{margin:0}.pdhead small{color:var(--muted)}
#passList{display:grid;gap:10px;margin:12px 0}
.prow{display:flex;align-items:center;gap:12px}.prow i{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font:800 .75rem var(--f-ui);font-style:normal}.prow b{flex:1}.prow .ok{color:var(--ok);font-weight:700}.prow .no{color:var(--warn);font-weight:700}
.gzfull{''')
rep("/* Speed King: top speed on reds and blues today */", r'''/* ---- passport check (Swiss days) ---- */
games.pass = games.pass||{}; games.nudgeSeen = games.nudgeSeen||{};
function passKey(){ const t=CONFIG.trip && CONFIG.trip[di]; return t ? gDay(new Date(t[0],t[1],t[2])) : gDay(); }
function passCrew(k){
  const ms = gstate && gstate.members && gstate.members.length ? gstate.members : [];
  const me = grp && grp.member_id;
  const out = ms.map(m=>{ const mine=m.id===me; const t = mine ? games.pass[k] : (m.games||{})['pass:'+k]; return {name: mine ? 'You' : m.name, color:m.color||'#F97316', t:t||0, me:mine}; });
  if(!out.some(x=>x.me)) out.unshift({name:'You', color:(grp&&grp.color)||'#F5B700', t:games.pass[k]||0, me:true});
  return out; }
function renderPassCrew(k){
  const c=$('passCrew'); c.textContent=''; const crew=passCrew(k);
  crew.forEach(x=>{ const i=document.createElement('i'); i.style.background=x.color; i.textContent=initials(x.name==='You'&&grp?grp.name:x.name); if(x.t) i.classList.add('ok'); i.title=x.name; c.appendChild(i); });
  const n=crew.filter(x=>x.t).length; const sm=document.createElement('small'); sm.textContent=n+' of '+crew.length+' checked'; c.appendChild(sm); }
function showPass(why, by){
  if(!daySwiss()) return false;
  const k=passKey(); if(games.pass[k]) return false;
  const t=CONFIG.trip && CONFIG.trip[di]; $('passEb').textContent=((DAY.date||'')+' · Swiss day').toUpperCase();
  $('passTxt').innerHTML='We cross into Switzerland today. No passport, no '+esc(DAY.title.replace(/^Switzerland:\s*/,'').split(/\s*\+\s*/)[0])+'.<br><b>Got it on you?</b>';
  $('passNudged').hidden=!by; if(by) $('passNudged').textContent=by+' says: passport. Now.';
  renderPassCrew(k); resetKnob(); $('passSheet').hidden=false; playSfx('passport'); return true; }
function resetKnob(){ const kb=$('passKnob'); kb.style.transition='left .25s ease'; kb.style.left='6px'; $('passFill').style.transition='width .25s ease'; $('passFill').style.width='0'; kb.setAttribute('aria-valuenow','0'); }
const PASS_QUIPS=['Look at you, an adult.','The Swiss thank you.','Customs officer Shai approves.','One less thing to forget. Now the gloves.'];
function passConfirm(){
  const k=passKey(), now=Date.now(); games.pass[k]=now; saveGames(); gPost({['pass:'+k]:now}, true);
  $('passSheet').hidden=true; $('passQuip').textContent='Shai: “'+PASS_QUIPS[Math.floor(Math.random()*PASS_QUIPS.length)]+'”';
  renderPassList(k); $('passDoneSheet').hidden=false; }
function renderPassList(k){
  const box=$('passList'); box.textContent=''; const crew=passCrew(k);
  crew.forEach(x=>{ const r=document.createElement('div'); r.className='prow'; const i=document.createElement('i'); i.style.background=x.color; i.textContent=initials(x.name==='You'&&grp?grp.name:x.name);
    const b=document.createElement('b'); b.textContent=x.name; const st=document.createElement('span'); st.className=x.t?'ok':'no'; st.textContent=x.t ? 'Checked '+hhmm(x.t) : 'Not yet'; r.append(i,b,st); box.appendChild(r); });
  const left=crew.filter(x=>!x.t).length; $('passNudge').hidden=!left || !grp; $('passNudge').textContent = left===1 ? 'Nudge '+crew.find(x=>!x.t).name : 'Nudge the '+left+' who haven’t'; }
{ /* the slide: drag the knob to the end; keyboard: arrow right / Enter */
  const kb=$('passKnob'), tr=$('passTrack'), fill=$('passFill'); let x0=null, max=0;
  const set=x=>{ kb.style.left=(6+x)+'px'; fill.style.width=(x+34)+'px'; kb.setAttribute('aria-valuenow', String(Math.round(100*x/Math.max(1,max)))); };
  kb.addEventListener('pointerdown', e=>{ max=tr.clientWidth-68; x0=e.clientX-(kb.offsetLeft-6); kb.setPointerCapture(e.pointerId); kb.style.transition='none'; fill.style.transition='none'; });
  kb.addEventListener('pointermove', e=>{ if(x0==null) return; set(Math.max(0, Math.min(max, e.clientX-x0))); });
  const end=e=>{ if(x0==null) return; const x=kb.offsetLeft-6; x0=null; if(x >= max*0.85){ set(max); setTimeout(passConfirm, 150); } else resetKnob(); };
  kb.addEventListener('pointerup', end); kb.addEventListener('pointercancel', end);
  kb.addEventListener('keydown', e=>{ if(e.key==='ArrowRight' || e.key==='Enter'){ e.preventDefault(); max=tr.clientWidth-68; set(max); setTimeout(passConfirm, 150); } });
}
$('passOk').onclick=()=>{ $('passDoneSheet').hidden=true; };
$('passNudge').onclick=()=>{ const k=passKey(); gPost({['nudge:'+k]:Date.now()}, true); $('passNudge').textContent='Nudged 👊'; $('passNudge').disabled=true; setTimeout(()=>{ $('passNudge').disabled=false; renderPassList(k); }, 4000); };
/* someone nudged: the check comes back for whoever hasn't done it */
function passNudgeCheck(){
  if(!gstate || !daySwiss()) return; const k=passKey(); if(games.pass[k]) return;
  let who=null, at=0; for(const m of gstate.members){ if(m.id===(grp&&grp.member_id)) continue; const t=(m.games||{})['nudge:'+k]; if(t && t>at){ at=t; who=m.name.split(' ')[0]; } }
  if(at && at>(games.nudgeSeen[k]||0)){ games.nudgeSeen[k]=at; saveGames(); showPass('nudge', who); }
}
setTimeout(()=>{ if(passKey()===gDay() && $('onb').hidden) showPass('morning'); }, 2500);
/* Speed King: top speed on reds and blues today */''')
rep("  if(typeof paintBadges==='function'){ paintBadges(); tellGamesNative(); }", "  if(typeof paintBadges==='function'){ paintBadges(); tellGamesNative(); }\n  if(typeof passNudgeCheck==='function') passNudgeCheck();")
rep("if(daySwiss()){ playSfx('passport'); toast('Swiss day. Passports 🇨🇭'); } };", "if(daySwiss() && !showPass('pick')){ playSfx('passport'); toast('Swiss day. Passports 🇨🇭'); } };")
rep("else { playSfx('start'); startGPS(); } };", "else { playSfx('start'); startGPS(); showPass('start'); } };")
rep('window.__ski = { map, st, ', 'window.__ski = { map, st, showPass, passKey, passNudgeCheck, ')
s = s.replace('get gstate(){return gstate;}, ', 'get gstate(){return gstate;}, setGstate(g){ gstate=g; }, ', 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
