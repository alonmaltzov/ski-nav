"""Games: the passport race goes (the passport slide check stays); STOPPP gets its own map button like the crown,
with today's 3 rounds and a 'Try it now' test that doesn't count."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90]); s = s.replace(old, new)
FLASK = ('<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M9 2.5h6v3l-1 1v1.2c2.4.6 4 2.3 4 4.8v6.5a2.5 2.5 0 0 1-2.5 2.5h-7A2.5 2.5 0 0 1 6 19v-6.5c0-2.5 1.6-4.2 4-4.8V6.5l-1-1z" fill="#FF8A3D" stroke="#9A4A12" stroke-width="1.3" stroke-linejoin="round"/>'
         '<path d="M8.5 14h7" stroke="#fff" stroke-width="1.6" stroke-linecap="round" opacity=".85"/></svg>')

# ---- the passport race retires ----
rep("games.on = Object.assign({stop:true, border:true, speed:true}, games.on||{});",
    "games.on = Object.assign({stop:true, border:true, speed:true}, games.on||{}); games.on.border = false;   /* the passport race retired; the passport check stays */")
s, n = re.subn(r'\s*<button class="grow toggle" id="gBorder" type="button" role="switch" aria-pressed="true"><span>Passport race<small>First into Switzerland wins\.</small></span><span class="sw"></span></button>', '', s)
assert n == 1
rep("$('gBorder').onclick=()=>{ games.on.border=!games.on.border; saveGames(); renderGames(); tellGamesNative(); paintBadges(); };", "")
rep("chips:['🥃 STOPPP','🇨🇭 Passport race','👑 Speed King'] }", "chips:['🥃 STOPPP','🇨🇭 Passport check','👑 Speed King'] }")

# ---- STOPPP button on the map, under the crown ----
rep('<small id="kingTop"></small></button>',
    '<small id="kingTop"></small></button>\n      <button class="mbtn stopbtn" id="stopBtn" type="button" aria-label="STOPPP">' + FLASK + '<small id="stopBtnTxt"></small></button>')
rep('<div class="sheet" id="gamesSheet" hidden>',
    '''<div class="sheet" id="stopInfo" hidden><div class="sheetin" role="dialog" aria-label="STOPPP today">
  <div class="sheethead"><div><span class="eyebrow">STOPPP · today</span><h3 id="siTitle">3 flask breaks</h3></div><button class="btn ghost sm" id="siDone" type="button">Done</button></div>
  <p class="note" style="margin:0 0 4px">It goes off on a long lift (7+ min) in each window, so everyone stops together at the top.</p>
  <div class="tcard" id="siList"></div>
  <button class="btn primary" id="siTry" type="button">🥃 Try it now</button>
  <p class="note" style="margin:0;text-align:center">A test: only on your phone, nobody's round.</p>
</div></div>
<div class="sheet" id="gamesSheet" hidden>''')
rep("$('kingBtn').onclick=showKing;",
    "$('kingBtn').onclick=showKing;\n"
    "function renderStopBtn(){ const b=$('stopBtn'); if(!b) return; b.hidden=!games.on.stop; const n=(games.fired[gDay()]||[]).length; $('stopBtnTxt').textContent=n+'/3'; b.setAttribute('aria-label','STOPPP: '+n+' of 3 today'); }\n"
    "function stopRows(box){ box.textContent=''; const fired=games.fired[gDay()]||[], now=Date.now();\n"
    "  stopPlan().forEach(s=>{ const r=document.createElement('div'); r.className='gzrank';\n"
    "    r.innerHTML='<span class=\"gzpos\"></span><i class=\"gzav\"></i><div class=\"gznm\"><b></b><small></small></div><span class=\"gzval\"></span>';\n"
    "    r.querySelector('.gzpos').textContent=s.n; const a=r.querySelector('.gzav'); a.style.background=s.who.color; a.textContent=initials(s.who.name);\n"
    "    r.querySelector('b').textContent = s.who.me ? 'Your round' : s.who.name.split(' ')[0]+'’s round'; r.querySelector('small').textContent = 'between '+['11:00 and 12:20','12:20 and 1:40','1:40 and 3:00'][s.n-1];\n"
    "    r.querySelector('.gzval').textContent = fired.includes(s.n) ? 'Done 🥃' : (now > s.at ? 'Next long lift' : ''); box.appendChild(r); }); }\n"
    "$('stopBtn').onclick=()=>{ stopRows($('siList')); const n=(games.fired[gDay()]||[]).length; $('siTitle').textContent = n>=3 ? 'All 3 done. Legends.' : n ? n+' of 3 done' : '3 flask breaks'; $('stopInfo').hidden=false; };\n"
    "$('siDone').onclick=()=>{ $('stopInfo').hidden=true; };\n"
    "$('stopInfo').onclick=e=>{ if(e.target.id==='stopInfo') $('stopInfo').hidden=true; };\n"
    "$('siTry').onclick=()=>{ $('stopInfo').hidden=true; const p=stopPlan(); fireStop(Object.assign({}, p[0], {test:true}), true); };")
# a test run doesn't count and says so
rep("  const day=s.day; games.fired[day]=(games.fired[day]||[]).concat([s.n]); saveGames();",
    "  const day=s.day; if(!s.test){ games.fired[day]=(games.fired[day]||[]).concat([s.n]); saveGames(); renderStopBtn(); }")
rep("  $('stopNum').textContent='Stop number '+s.n+' of 3 today';",
    "  $('stopNum').textContent = s.test ? 'Test run · doesn’t count' : 'Stop number '+s.n+' of 3 today';")
rep("$('stopSkip').onclick=()=>{ $('stopSheet').hidden=true; games.rounds=false;",
    "$('stopSkip').onclick=()=>{ $('stopSheet').hidden=true; if($('stopNum').textContent.startsWith('Test')) return; games.rounds=false;")
# keep it in step with the crown
rep("function renderKingBtn(){ const b=$('kingBtn'); if(!b) return;", "function renderKingBtn(){ renderStopBtn(); const b=$('kingBtn'); if(!b) return;")
CSS = '''
/* STOPPP button under the crown */
.stopbtn{display:flex;flex-direction:column;gap:1px;align-items:center;justify-content:center}.stopbtn small{font:800 .68rem var(--f-ui);line-height:1}.stopbtn[hidden]{display:none}
#siList{gap:0}
'''
i = s.index('<style>\n/* Layout: one-screen instrument.'); j = s.index('</style>', i)
s = s[:j] + CSS + s[j:]
open(p, 'w', encoding='utf-8').write(s)
print('stop button patch applied')
