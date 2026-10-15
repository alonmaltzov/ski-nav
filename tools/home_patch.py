"""Home tweaks (Oct 15): Runs only from the menu with a clear way back, Lifts button that speaks,
Invite in the menu, Speed King button, clip changes (menu, every brief, Swiss day)."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    assert s.count(old) >= 1, old[:80]
    s = s.replace(old, new, n)

# 1. Runs button off the home screen; Steps takes the row
rep('      <button class="btn ghost" id="progBtn" type="button">Runs</button>\n', '')
rep("$('progBtn').onclick=openProgress; $('progClose').onclick=closeProgress;", "$('progClose').onclick=closeProgress;")
rep('.app:not(.tracking) .actions{grid-template-columns:1fr 1fr}', '.app:not(.tracking) .actions{grid-template-columns:1fr 1fr}\n.app:not(.tracking) #stepsBtn{grid-column:1/-1}')
# the menu card says where it goes
rep('<span class="maplink">Map ›</span>', '<span class="maplink">Runs ›</span>')

# 2. Runs view: a clear way back to today
a = s.index('<div class="proghead"><h2 id="progTitle">'); z = s.index('</div></div>', a) + len('</div></div>')
s = s[:a] + '<div class="proghead"><button class="btn ghost sm backtoday" id="progClose" type="button" aria-label="Back to today"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>Today</button><h2 id="progTitle">Blue &amp; red runs</h2><button class="btn ghost sm" id="runsListBtn" type="button">List</button></div>' + s[z:]
rep('.proghead h2{margin:0;font:700 1.35rem var(--f-num)}', '.proghead h2{margin:0;font:700 1.35rem var(--f-num);flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n.backtoday{display:flex;align-items:center;gap:4px;padding-left:10px}')

# 3. Invite lives in the menu (labelled), the home pill only shows when friends are in
rep('<button class="xbtn" id="groupBtn" type="button" aria-label="Group">', '<button class="xbtn invitebtn" id="groupBtn" type="button" aria-label="Invite friends">')
rep('<path d="M3 20c0-3.5 2.7-6 6-6s6 2.5 6 6M15 14.5c3 0 5.5 2 5.5 5"/></svg></button>', '<path d="M3 20c0-3.5 2.7-6 6-6s6 2.5 6 6M15 14.5c3 0 5.5 2 5.5 5"/></svg><span id="groupBtnTxt">Invite</span></button>')
rep('.hbtns{display:flex;gap:8px;flex:none}', '.hbtns{display:flex;gap:8px;flex:none}\n.invitebtn{width:auto!important;padding:0 12px;gap:6px;display:flex;align-items:center;font:700 .9rem var(--f-ui)}')
rep("  if(!others.length){ const s=document.createElement('span'); s.textContent='Invite'; s.style.marginLeft='0'; p.appendChild(s); p.setAttribute('aria-label','Invite friends'); return; }",
    "  { const t=$('groupBtnTxt'); if(t) t.textContent = others.length ? 'Group' : 'Invite'; }\n  if(!others.length){ p.hidden=true; return; }")

# 4. Lifts button on the home screen: the guide says the lift status, every tap
rep('<button class="tpill" id="liftsPill" type="button" aria-label="Lift status" hidden>', '<button class="tpill" id="liftsPill" type="button" aria-label="Check lift status">')
rep("$('liftsPill').onclick=openToday;", r'''$('liftsPill').onclick=liftCheck;
/* the Lifts button: fresh status, spoken every time; the change-of-plan clip first when a plan lift is closed */
async function liftCheck(){
  const b=$('liftsPill'); b.classList.add('busy');
  try{ await fetchLifts(true); }catch(e){}
  b.classList.remove('busy');
  let line, shut=[];
  if(!liftStat) line='I can’t reach the lift status right now. Try again with a connection.';
  else if(!resortRunning()) line='The lifts aren’t running right now. The season starts in December.';
  else { shut=planLifts().filter(x=>{ const v=liftStatusOf(x.bi); return v && v!=='open'; });
    line = shut.length ? (shut.length===1 ? shut[0].s.name+' is closed. Tap Plan from here when you get there.' : shut.length+' lifts on today’s plan are closed: '+shut.slice(0,3).map(x=>x.s.name).join(', ')+'. Tap Plan from here when you get there.')
                       : 'All '+planLifts().length+' lifts on today’s plan are open. '+liftStat.open+' of '+liftStat.total+' open across the area.'; }
  toast(line);
  const say_=()=>{ try{ speak([line]); }catch(e){} };
  if(shut.length) playSfx('closed', say_); else say_();
  return line;
}''')
rep(".tpill.friends", ".tpill.busy{opacity:.6}\n.tpill.friends", 1) if '.tpill.friends' in s else None

# 5. Speed King button under the map buttons
KING = '<svg viewBox="0 0 24 18" width="24" height="18" aria-hidden="true"><path d="M2 16 L1 4 L7 9 L12 1 L17 9 L23 4 L22 16 Z" fill="#FFC21A" stroke="#B7791F" stroke-width="1.4" stroke-linejoin="round"/></svg>'
a = s.index('<button class="mbtn" id="placesBtn"'); z = s.index('</button>', a) + len('</button>')
s = s[:z] + '\n      <button class="mbtn kingbtn" id="kingBtn" type="button" aria-label="Speed King">' + KING + '<small id="kingTop"></small></button>' + s[z:]
rep('.mbtn{width:50px;', '.kingbtn{display:flex;flex-direction:column;gap:1px;align-items:center;justify-content:center}.kingbtn small{font:800 .68rem var(--f-ui);line-height:1}.kingbtn small:empty{display:none}.kingbtn[hidden]{display:none}\n.mbtn{width:50px;')
rep("$('kingOk').onclick=()=>{ $('kingSheet').hidden=true; };", r'''$('kingOk').onclick=()=>{ $('kingSheet').hidden=true; };
$('kingBtn').onclick=showKing;
function renderKingBtn(){ const b=$('kingBtn'); if(!b) return; b.hidden=!games.on.speed; const k=speedRank(gDay())[0];
  $('kingTop').textContent = k ? (k.me ? 'You' : initials(k.name)) : ''; b.setAttribute('aria-label', k ? 'Speed King: '+(k.me?'you':k.name)+', '+Math.round(speedOut(k.v))+(units==='imp'?' mph':' km/h') : 'Speed King: no top speeds yet today'); }''')
rep("  tellGamesNative(); paintBadges();\n", "  tellGamesNative(); paintBadges(); renderKingBtn();\n")
rep("$('gSpeed').onclick=()=>{ games.on.speed=!games.on.speed; saveGames(); renderGames(); paintBadges();", "$('gSpeed').onclick=()=>{ games.on.speed=!games.on.speed; saveGames(); renderGames(); paintBadges(); renderKingBtn();")

# 6. clips: Lama Hacol on the menu button, Yuval every brief, passport on picking a Swiss day
rep("$('menuBtn').onclick=openDrawer;", "$('menuBtn').onclick=()=>{ playSfx('today'); openDrawer(); };")
rep("setTimeout(sfxToday, 1800);\ndocument.addEventListener('visibilitychange', ()=>{ if(document.visibilityState==='visible') setTimeout(sfxToday, 900); });\n", '')
rep("  sfxToday();   // inside the tap, so the browser lets it play\n", '')
rep("  if(firstToday) playSfx('brief', go); else go();", "  playSfx('brief', go);")
rep("  const firstToday = store.briefClip!==todayStr();\n", '')
rep(" playSfx('passport');", '')   # not at the border any more
rep("    b.onclick=()=>{ selectDay(i); closeDrawer(); };", "    b.onclick=()=>{ selectDay(i); closeDrawer(); if(daySwiss()){ playSfx('passport'); toast('Swiss day: bring your passports 🇨🇭'); } };")
rep("function selectDay(i){", "function daySwiss(){ try{ return steps.some(st_=>(st_.coords||[]).some(c=>gSwiss(c[0], c[1]))); }catch(e){ return false; } }\nfunction selectDay(i){")

# 7. the tour's week step: Runs is in the menu now
rep("say:()=>'Runs shows the whole week. Each colour is a day, and the bars show what’s left to ski. Route plays the day on the map.',",
    "say:()=>'Runs, in the menu, shows the whole week. Each colour is a day, and the bars show what’s left to ski. Today brings you back.',")
rep("html:()=>'<b>Runs</b> shows the whole week. Each colour is a day, and the bars show what’s left to ski. <b>Route</b> plays the day on the map.' },",
    "html:()=>'<b>Runs</b>, in the menu, shows the whole week. Each colour is a day, and the bars show what’s left to ski. <b>‹ Today</b> brings you back.' },")
rep("{ el:['legend'], el2:['runsListBtn','progClose'], prog:true,", "{ el:['legend'], el2:['progClose'], prog:true,")
rep("say:()=>'Tap All to see the crew on the map. And three games run by themselves: STOPPP, the passport race, and Speed King.',",
    "say:()=>'Tap All to see the crew on the map. And three games run by themselves: STOPPP, the passport race, and Speed King, right here under the crown.',")
rep("{ el:['fitBtn'], next:'Let’s ski',", "{ el:['fitBtn'], el2:['kingBtn'], next:'Let’s ski',")
rep('window.__ski = { map, st, ', 'window.__ski = { map, st, liftCheck, daySwiss, renderKingBtn, ', 1)
rep("""  if(off){ dot.classList.add('off'); $('liftsPillTxt').textContent='Lifts closed'; }
  else if(closed.length){ dot.classList.add('part'); $('liftsPillTxt').textContent=closed.length+' plan lift'+(closed.length>1?'s':'')+' closed'; }
  else { dot.classList.add('ok'); $('liftsPillTxt').textContent='Lifts open'; }""", """  /* the home button stays short: the dot says it, the guide reads it out on tap */
  const lp=$('liftsDot'); if(lp){ lp.className='ldot '+(off?'off':closed.length?'part':'ok'); }
  if(off){ dot.classList.add('off'); $('liftsPillTxt').textContent='Lifts'; }
  else if(closed.length){ dot.classList.add('part'); $('liftsPillTxt').textContent='Lifts · '+closed.length+' shut'; }
  else { dot.classList.add('ok'); $('liftsPillTxt').textContent='Lifts'; }""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
