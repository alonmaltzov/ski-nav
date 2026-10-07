"""One-off patch: map-first home, tracking card, Sun mode, day recap. Applied to index.html and nyc.html."""
import sys
CSS = r"""
/* ===== redesign: map-first home, floating tracking card, Sun mode, day recap ===== */
.daybar{display:none!important}
.app{--sheet-r:24px}
.app:not(.tracking) .top{display:none}
.prog-view .top{display:none}
.mapwrap{margin-bottom:calc(-1 * var(--sheet-r))}
.bottom{position:relative;z-index:2;border-top:0;border-radius:var(--sheet-r) var(--sheet-r) 0 0;box-shadow:0 -6px 24px rgb(11 22 32/.14);padding-top:20px}
.bottom::before{content:"";position:absolute;top:7px;left:50%;width:40px;height:5px;margin-left:-20px;border-radius:3px;background:color-mix(in srgb,var(--muted) 40%,transparent)}
.floatmenu{position:absolute;left:12px;top:12px;z-index:500;width:50px;height:50px;border-radius:25px;border:1px solid var(--line);background:var(--panel);color:var(--ink);display:grid;place-items:center;box-shadow:0 3px 12px rgb(11 22 32/.16)}
.floatmenu svg{width:22px;height:22px}
.app:not(.tracking) .floatmenu,.app:not(.tracking) .mapbtns,.app:not(.tracking) .offroute,.app:not(.tracking) .homebanner,.app:not(.tracking) .placesbox{top:calc(12px + env(safe-area-inset-top,0px))}
.offroute,.homebanner{left:74px}
/* home sheet */
.homesum{display:grid;gap:4px}
.homesum h2{margin:0;font:800 1.75rem/1.05 var(--f-num);letter-spacing:-.01em;text-wrap:balance}
.homesum p{margin:0;color:var(--muted);font-size:1rem}
.app.tracking .homesum{display:none}
.app:not(.tracking) .next,.app:not(.tracking) .then{display:none}
.app:not(.tracking) .actions{grid-template-columns:1fr 1fr}
.app:not(.tracking) #goBtn{grid-column:1/-1;min-height:62px;font-size:1.25rem;font-weight:700;background:var(--ink);color:var(--panel);border-radius:18px}
.app.tracking .actions{grid-template-columns:1fr 1fr 1.3fr}
.app.tracking #goBtn{order:3}
/* tracking: one card, speed left, four numbers right */
.app.tracking .top{grid-template-columns:auto 1fr;align-items:center;column-gap:16px;row-gap:0;padding-bottom:12px}
.app.tracking .speedrow{flex-direction:column;align-items:flex-start;gap:6px}
.app.tracking .speed{font-size:4.6rem;font-weight:800}
.app.tracking .speed small{font-size:1rem;margin-left:4px}
.app.tracking .gps{flex-direction:row;align-items:center}
.app.tracking .pill{font-size:.75rem;padding:5px 8px}
.app.tracking .stats{grid-template-columns:repeat(2,minmax(0,1fr));row-gap:10px}
.app.tracking .stat b{font-size:1.5rem;font-weight:700}
/* Sun mode: black on white, fewer and bigger numbers */
.app.sun{--ink:#000;--muted:#1f2a33;--line:#000;--panel:#fff;--bg:#f1f1f1}
.app.sun.tracking .top{background:#000;color:#fff;border-bottom:0}
.app.sun.tracking .speed{font-size:6rem;font-weight:900}
.app.sun.tracking .speed small,.app.sun.tracking .stat span{color:#fff;font-weight:800}
.app.sun.tracking .stats{grid-template-columns:1fr}
.app.sun.tracking .stat:nth-child(n+3){display:none}
.app.sun.tracking .stat b{font-size:2rem;font-weight:900}
.app.sun .pill{background:#fff;color:#000;font-weight:800}
.app.sun .nexttxt h2{font-size:1.6rem;font-weight:900}
.app.sun .nexttxt p,.app.sun .then,.app.sun .eyebrow{color:#000;font-weight:700}
.app.sun .mbtn,.app.sun .floatmenu{border:2px solid #000}
.app.sun .legend{border:2px solid #000;background:#fff}
/* day recap */
.recapin{max-height:92%;gap:12px}
.recap .eyebrow{display:block}
.recap h3{margin:0;font:800 1.7rem/1.05 var(--f-num);text-wrap:balance}
.rgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.rtile{background:var(--bg);border-radius:16px;padding:12px 14px;display:grid;gap:2px}
.rtile b{font:800 2rem/1 var(--f-num);font-variant-numeric:tabular-nums}
.rtile span{font-size:.78rem;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);font-weight:600}
.rgoal{background:var(--bg);border-radius:16px;padding:14px;display:grid;gap:10px}
.rgoal .big{font:800 1.6rem/1 var(--f-num)}
.rgoal .plus{color:var(--ok);font-weight:700;margin-left:8px;font-size:1rem}
.rbar{height:10px;border-radius:5px;background:color-mix(in srgb,var(--muted) 22%,transparent);overflow:hidden}
.rbar i{display:block;height:100%;border-radius:5px}
.rruns{display:grid;gap:8px}
.rrun{display:flex;align-items:center;gap:10px;font-size:1rem}
.rrun i{width:12px;height:12px;border-radius:3px;flex:none}
.ractions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:4px}
.ractions .btn.primary{background:var(--ink);color:var(--panel)}
"""

MENU_BTN_OLD = '<button class="menubtn" id="menuBtn" type="button" aria-label="Open week menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>'
MENU_BTN_NEW = MENU_BTN_OLD.replace('class="menubtn"', 'class="floatmenu"').replace('aria-label="Open week menu"', 'aria-label="Week, places and settings"')

HOME = '''    <div class="homesum" id="homeSum">
      <span class="eyebrow" id="homeEyebrow"></span>
      <h2 id="homeTitle"></h2>
      <p id="homeMeta"></p>
    </div>
    <div class="next">'''

RECAP = '''<div class="sheet recap" id="recapSheet" hidden>
  <div class="sheetin recapin" role="dialog" aria-label="Day recap">
    <div class="sheethead"><div><span class="eyebrow" id="recapEyebrow"></span><h3 id="recapTitle"></h3></div><button class="btn ghost sm" id="recapClose" type="button">Done</button></div>
    <div class="rgrid">
      <div class="rtile"><b id="rKm">0</b><span id="rKmU">Km skied</span></div>
      <div class="rtile"><b id="rVert">0</b><span id="rVertU">Vertical m</span></div>
      <div class="rtile"><b id="rTop">0</b><span id="rTopU">Top km/h</span></div>
      <div class="rtile"><b id="rLifts">0</b><span>Lifts ridden</span></div>
    </div>
    <div class="rgoal">
      <span class="eyebrow" id="rGoalLabel">Week goal</span>
      <div><span class="big" id="rGoal">0 of 0</span><span class="plus" id="rGoalPlus"></span></div>
      <div class="rbar"><i id="rGoalBar"></i></div>
      <div class="rruns" id="rRuns"></div>
    </div>
    <div class="ractions">
      <button class="btn ghost" id="recapShare" type="button">Share day</button>
      <button class="btn primary" id="recapNext" type="button">Plan tomorrow</button>
    </div>
  </div>
</div>

<div class="sheet" id="sheet" hidden>'''

SUN_SETTING = '''    <div class="toggle" style="display:grid;gap:8px;box-sizing:border-box"><span>Sun mode<small>Black on white with bigger numbers, for bright snow. Auto turns it on when your screen goes to full brightness.</small></span>
      <div class="chips" id="sunSeg"><button type="button" data-v="auto" aria-pressed="true">Auto</button><button type="button" data-v="on" aria-pressed="false">On</button><button type="button" data-v="off" aria-pressed="false">Off</button></div></div>
    <div class="setrow">'''

JS = r"""
/* ---------- redesign: home sheet, tracking state, Sun mode, day recap ---------- */
const APP = document.querySelector('.app');
function renderHome(){
  if(!$('homeTitle')) return;
  const dateTxt = (DAY.date||'').toUpperCase();
  $('homeEyebrow').textContent = (dateTxt ? dateTxt+' · ' : '') + (store.follow ? "TODAY'S PLAN" : "TODAY'S SUGGESTION");
  $('homeTitle').textContent = DAY.title;
  const km = units==='imp' ? (DAY.km*0.6214).toFixed(1)+' mi' : DAY.km+' km';
  let meta = km+' of runs · '+DAY.lifts+' lifts · '+CONFIG.endName+' '+DAY.arrive;
  if(st.dist > 50) meta += ' · '+(units==='imp' ? (st.dist/1609.34).toFixed(1)+' mi' : (st.dist/1000).toFixed(1)+' km')+' skied so far';
  $('homeMeta').textContent = meta;
}
function setTrackUI(on){
  APP.classList.toggle('tracking', !!on);
  renderHome(); fitMapBtns();
  if(on){ const k=dayKey(WEEK[di].day), d=store.days[k]||(store.days[k]={}); if(!d.startSkied) d.startSkied=[...skiedWays]; }
}
/* Sun mode: auto follows screen brightness from the iPhone (full brightness = bright sun), or on/off by hand */
let sunBright=false, sunApplied=null;
function applySun(){
  const pref = store.sun || 'auto';
  const on = pref==='on' || (pref==='auto' && sunBright);
  document.querySelectorAll('#sunSeg [data-v]').forEach(b=>b.setAttribute('aria-pressed', b.dataset.v===pref?'true':'false'));
  if(on===sunApplied) return; sunApplied=on;
  APP.classList.toggle('sun', on);
  if(on) document.documentElement.setAttribute('data-theme','light'); else document.documentElement.removeAttribute('data-theme');
  if(mapReady){ map.setStyle(styleFor()); map.once('styledata',()=>{ drawRoute(); paintSkied(); applyView(); drawTrail(true); if(is3D) map.setTerrain({source:'dem',exaggeration:1.3}); }); }
}
function setSun(v){ store.sun=v; persist(); applySun(); }
document.querySelectorAll('#sunSeg [data-v]').forEach(b=>b.onclick=()=>setSun(b.dataset.v));
if(window.__native) window.__native.brightness = v => { const was=sunBright; sunBright = was ? v > 0.8 : v >= 0.92; if(was!==sunBright) applySun(); };
/* day recap, shown when you stop */
function liftsRidden(){ let n=0, prev=0; for(const q of (st.trail||[])){ if(q[2]===1 && prev!==1) n++; prev=q[2]; } return n; }
function openRecap(){
  const k=dayKey(WEEK[di].day), start=new Set((store.days[k]||{}).startSkied||[]);
  $('recapEyebrow').textContent = (DAY.date ? DAY.date+' · ' : '')+'Day '+DAY.day+' done';
  $('recapTitle').textContent = DAY.title;
  $('rKm').textContent = units==='imp' ? (st.dist/1609.34).toFixed(1) : (st.dist/1000).toFixed(1);
  $('rKmU').textContent = units==='imp' ? 'Miles skied' : 'Km skied';
  $('rVert').textContent = (units==='imp' ? Math.round(st.vert*3.28084) : Math.round(st.vert)).toLocaleString();
  $('rVertU').textContent = units==='imp' ? 'Vertical ft' : 'Vertical m';
  $('rTop').textContent = Math.round(speedOut(st.max));
  $('rTopU').textContent = units==='imp' ? 'Top mph' : 'Top km/h';
  $('rLifts').textContent = liftsRidden();
  const cols = GOALCOL(), word = cols.length===1 ? cols[0]+' runs' : cols.join(' & ')+' runs';
  const g = groupStats().filter(x=>cols.includes(x.c||x.color||'')), done = g.filter(x=>x.done).length;
  const goalGroups = g.length ? g : groupStats();
  const total = goalGroups.length, doneAll = goalGroups.filter(x=>x.done).length;
  const today = [...skiedWays].filter(bi=>!start.has(bi));
  $('rGoalLabel').textContent = 'Week goal: '+word;
  $('rGoal').textContent = doneAll+' of '+total;
  $('rGoalPlus').textContent = today.length ? '+'+today.length+' new today' : '';
  const bar=$('rGoalBar'); bar.style.width = (total ? Math.round(100*doneAll/total) : 0)+'%'; bar.style.background = 'var(--p-'+(cols[0]||'blue')+')';
  const box=$('rRuns'); box.textContent='';
  const named = new Map();
  for(const bi of today){ const b=BG[bi]; const nm=b[2]||'Unnamed run'; const col=b[1]||'blue'; const key=nm+'|'+col; named.set(key,{nm,col}); }
  [...named.values()].slice(0,8).forEach(r=>{ const row=document.createElement('div'); row.className='rrun'; const i=document.createElement('i'); i.style.background='var(--p-'+(['green','blue','red','black'].includes(r.col)?r.col:'blue')+')'; const s=document.createElement('span'); s.textContent=r.nm; row.append(i,s); box.appendChild(row); });
  if(!named.size){ const p=document.createElement('span'); p.className='note'; p.style.margin='0'; p.textContent='No new runs marked today.'; box.appendChild(p); }
  $('recapNext').hidden = di >= WEEK.length-1;
  $('recapSheet').hidden=false;
}
$('recapClose').onclick=()=>{ $('recapSheet').hidden=true; };
$('recapSheet').onclick=e=>{ if(e.target.id==='recapSheet') $('recapSheet').hidden=true; };
$('recapNext').onclick=()=>{ $('recapSheet').hidden=true; if(di < WEEK.length-1) selectDay(di+1); };
$('recapShare').onclick=async()=>{
  const t = 'Ski Nav · '+(DAY.date||'')+' · '+DAY.title+': '+$('rKm').textContent+' '+(units==='imp'?'mi':'km')+', '+$('rVert').textContent+(units==='imp'?' ft':' m')+' down, top '+$('rTop').textContent+(units==='imp'?' mph':' km/h')+', '+$('rLifts').textContent+' lifts.';
  try{ if(navigator.share) await navigator.share({text:t}); else { await navigator.clipboard.writeText(t); $('recapShare').textContent='Copied'; } }catch(e){}
};
"""

def patch(path):
    s = open(path).read()
    def rep(old, new, count=1):
        nonlocal s
        n = s.count(old)
        if n != count: sys.exit(f'{path}: expected {count} of {old[:70]!r}, found {n}')
        s = s.replace(old, new)
    # CSS at the end of the app stylesheet (second </style>)
    i = s.index('</style>', s.index('/* Layout: one-screen instrument'))
    s = s[:i] + CSS + s[i:]
    # menu button floats over the map
    rep(MENU_BTN_OLD, '')
    rep('<div id="map" role="application" aria-label="Piste map"></div>', '<div id="map" role="application" aria-label="Piste map"></div>\n    ' + MENU_BTN_NEW)
    # home summary in the bottom sheet
    rep('    <div class="next">', HOME)
    # recap sheet
    rep('<div class="sheet" id="sheet" hidden>', RECAP)
    # Sun mode setting, above the settings buttons
    rep('    <div class="setrow">', SUN_SETTING)
    # button text
    rep("textContent='Start tracking'", "textContent='Start skiing'", 2)
    rep('id="goBtn" type="button">Start tracking</button>', 'id="goBtn" type="button">Start skiing</button>')
    # tracking state on/off
    rep("$('goBtn').textContent='Stop'; $('goBtn').classList.add('stop');", "$('goBtn').textContent='Stop'; $('goBtn').classList.add('stop'); setTrackUI(true);", 2)
    rep("$('goBtn').textContent='Start skiing'; $('goBtn').classList.remove('stop');\n  try{ wakeLock", "$('goBtn').textContent='Start skiing'; $('goBtn').classList.remove('stop'); setTrackUI(false);\n  try{ wakeLock")
    rep("$('goBtn').textContent='Start skiing'; $('goBtn').classList.remove('stop'); setPill('GPS off'); renderStats(); }", "$('goBtn').textContent='Start skiing'; $('goBtn').classList.remove('stop'); setTrackUI(false); setPill('GPS off'); renderStats(); }")
    # recap when you stop a real ski day
    rep("$('goBtn').onclick=()=>{ if(mode==='gps') stopGPS();", "$('goBtn').onclick=()=>{ if(mode==='gps'){ stopGPS(); if(st.elapsed > 60 || st.dist > 100) openRecap(); }")
    # home text follows the step/day rendering
    rep("  drawRoute(); renderList();\n  nativeStep();", "  drawRoute(); renderList(); renderHome();\n  nativeStep();")
    # new code before the test hooks, and expose for QA
    rep("/* expose for automated tests */", JS + "\n/* expose for automated tests */")
    rep("skied:()=>skiedWays.size };", "skied:()=>skiedWays.size, recap:openRecap, setSun };")
    rep("renderUnits(); renderDayBar(); renderStats(); renderStep(); applyView();", "renderUnits(); renderDayBar(); renderStats(); renderStep(); applyView(); renderHome(); applySun();")
    open(path, 'w').write(s)
    print('patched', path)

for p in sys.argv[1:]: patch(p)
