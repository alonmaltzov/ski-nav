"""Gloves first v2 (glass): glove-sized everything, and a new skiing screen.
Skiing: the direction card sits at the top in black (under the Dynamic Island), turns red off route with one big
Plan from here; speed and the day's numbers at the bottom with Hold to stop; swipe the speed card up for Steps;
map tools in one column on the right (Shai, ME, ALL, crown, STOPPP). Home: Start + Steps side by side.
Places moves into the menu."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90]); s = s.replace(old, new)
PHOTO = re.search(r'<img class="gface gphoto" src="[^"]+" alt="" aria-hidden="true" draggable="false">', s).group(0)

# ---------- markup ----------
# the step card: a big distance line
rep('<h2 id="nTitle">Loading route</h2>', '<h2 id="nTitle">Loading route</h2>\n        <b class="ndist" id="nDist"></b>')
# the speed card: swipe handle on top, Hold to stop on the right
rep('<header class="top">', '<header class="top">\n    <button class="spgrab" id="spGrab" type="button" aria-label="Steps"><i></i><span>Swipe up · steps</span></button>')
rep('      <div class="stat"><b id="clock">0:00</b><span>Time</span></div>\n    </div>\n  </header>',
    '      <div class="stat"><b id="clock">0:00</b><span>Time</span></div>\n    </div>\n'
    '    <button class="holdstop" id="holdStop" type="button" aria-label="Hold to stop"><svg viewBox="0 0 80 80" aria-hidden="true"><circle cx="40" cy="40" r="35" class="hs-track"/><circle cx="40" cy="40" r="35" class="hs-ring" id="holdRing"/></svg><span class="hs-in"><i></i><b>HOLD</b></span></button>\n  </header>')
# Shai joins the map tools while skiing
rep('<div class="mapbtns">', '<div class="mapbtns">\n      <button class="mbtn railshai" id="railShai" type="button" aria-label="Shai: brief, weather, lifts, call the crew">' + PHOTO + '</button>')
# Places moves into the menu
rep('      <div class="sect">Plan</div>\n      <div class="group" id="dayList"></div>',
    '      <div class="group"><button class="grow link" id="menuPlaces" type="button"><span>Places on the map<small>Restaurants, cafés, snow parks, toilets</small></span></button></div>\n'
    '      <div class="sect">Plan</div>\n      <div class="group" id="dayList"></div>')

# ---------- script ----------
# the big distance on the step card
rep("  let meta = stepMeta(s);\n", "  let meta = stepMeta(s), big='';\n")
rep("if(onIt){ const e=hav(pt, s.coords[s.coords.length-1]); meta = (s.type==='lift' ? 'Riding · ' : 'On it · ') + fmtLen(e) + ' to go'",
    "if(onIt){ const e=hav(pt, s.coords[s.coords.length-1]); big=fmtLen(e); meta = (s.type==='lift' ? 'Riding · ' : 'On it · ') + fmtLen(e) + ' to go'")
rep("    else if(d > 60) meta = fmtLen(d) + ' to start · ' + meta;", "    else if(d > 60){ big=fmtLen(d); meta = fmtLen(d) + ' to start · ' + meta; }")
rep("  $('nMeta').textContent = meta;\n", "  $('nMeta').textContent = meta; if($('nDist')) $('nDist').textContent = big;\n")
# the panels: direction card on top and speed card at the bottom while skiing
a = s.index('function glassInsets(){'); b = s.index('try{ const ro=new ResizeObserver(()=>glassInsets());')
s = s[:a] + ("function glassInsets(){ const A=document.querySelector('.app'); if(!A) return; const tr=A.classList.contains('tracking') && !A.classList.contains('prog-view');\n"
  "  const H=A.clientHeight, sp=A.querySelector('.top'), nav=$('navPanel'), prog=$('progPanel');\n"
  "  const topEl = tr ? nav : null, botEl = tr ? sp : [nav,prog].find(x=>x && !x.hidden);\n"
  "  const t = topEl ? Math.round(topEl.getBoundingClientRect().bottom) : 0, b = botEl ? Math.round(H - botEl.getBoundingClientRect().top) : 0;\n"
  "  A.style.setProperty('--topovl', t+'px'); A.style.setProperty('--botovl', b+'px'); fitMapBtns();\n"
  "  try{ if(typeof map!=='undefined' && map.setPadding){ const cur=map.getPadding(); if(cur.top!==t || cur.bottom!==b){ if(map.isMoving()){ if(!glassInsets.wait){ glassInsets.wait=true; map.once('moveend', ()=>{ glassInsets.wait=false; glassInsets(); }); } } else map.setPadding({top:t, bottom:b, left:0, right:0}); } } }catch(e){} }\n") + s[b:]
rep("new MutationObserver(()=>glassInsets()).observe(document.querySelector('.app'), {attributes:true, attributeFilter:['class']});",
    "new MutationObserver(()=>glassInsets()).observe(document.querySelector('.app'), {attributes:true, attributeFilter:['class']});\n"
    "/* off route: the direction card turns red and offers Plan from here */\n"
    "new MutationObserver(()=>{ document.querySelector('.app').classList.toggle('offr', !$('offroute').hidden); }).observe($('offroute'), {attributes:true, attributeFilter:['hidden']});\n"
    "/* Hold to stop: 1.5 s, the ring fills; a glove or a pocket can't do it by accident */\n"
    "{ const hb=$('holdStop'), ring=$('holdRing'), C=2*Math.PI*35; let t0=0, raf=0;\n"
    "  ring.style.strokeDasharray=C; ring.style.strokeDashoffset=C;\n"
    "  const reset=()=>{ cancelAnimationFrame(raf); raf=0; t0=0; ring.style.strokeDashoffset=C; hb.classList.remove('on'); };\n"
    "  const tick=()=>{ const f=Math.min(1,(performance.now()-t0)/1500); ring.style.strokeDashoffset=C*(1-f); if(f>=1){ reset(); try{ navigator.vibrate && navigator.vibrate(60); }catch(e){} $('goBtn').click(); return; } raf=requestAnimationFrame(tick); };\n"
    "  hb.addEventListener('pointerdown', e=>{ e.preventDefault(); if(raf) return; t0=performance.now(); hb.classList.add('on'); raf=requestAnimationFrame(tick); });\n"
    "  ['pointerup','pointerleave','pointercancel'].forEach(ev=>hb.addEventListener(ev, ()=>{ if(raf && performance.now()-t0 < 1500){ if(performance.now()-t0 < 250) toast('Hold to stop'); reset(); } }));\n"
    "  hb.addEventListener('contextmenu', e=>e.preventDefault()); }\n"
    "/* the speed card: tap the handle or swipe it up for the steps */\n"
    "$('spGrab').onclick=()=>$('stepsBtn').click();\n"
    "{ const sp=document.querySelector('.app .top'); let y0=null; sp.addEventListener('touchstart', e=>{ y0=e.touches[0].clientY; }, {passive:true}); sp.addEventListener('touchmove', e=>{ if(y0!=null && y0-e.touches[0].clientY > 40){ y0=null; if(document.querySelector('.app').classList.contains('tracking')) $('stepsBtn').click(); } }, {passive:true}); sp.addEventListener('touchend', ()=>{ y0=null; }); }\n"
    "$('railShai').onclick=()=>openBrief();\n"
    "$('menuPlaces').onclick=()=>{ closeDrawer(); $('placesBtn').click(); };")

# the step label: short while skiing
rep("  $('nEyebrow').textContent = (s.type==='end' ? 'Finish' : (store.follow ? 'Now' : 'Suggested')) + ' · step '+(cur+1)+' of '+steps.length + (s.at ? ' · plan '+s.at : '');",
    "  $('nEyebrow').textContent = mode!=='off' ? (s.type==='end' ? 'Finish' : (s.type==='lift' ? 'Lift' : 'Next')) + ' · step '+(cur+1)+'/'+steps.length + (s.at ? ' · '+s.at : '') : (s.type==='end' ? 'Finish' : (store.follow ? 'Now' : 'Suggested')) + ' · step '+(cur+1)+' of '+steps.length + (s.at ? ' · plan '+s.at : '');")
# crew sheet: big faces (Everyone), Call the crew and Invite under them
rep('<div class="picklist" id="pickList"></div>',
    '<div class="picklist" id="pickList"></div>\n    <a class="btn callbtn bigcall" id="pickCall" href="#" hidden>Call the crew</a>\n    <button class="btn ghost" id="pickInvite" type="button">Invite a friend</button>')
rep("for(const id of ['gCall','hubCall']){ const a=$(id); if(!a) continue; a.hidden=id==='gCall' && !u;",
    "for(const id of ['gCall','hubCall','pickCall']){ const a=$(id); if(!a) continue; a.hidden=id!=='hubCall' && !u;")
rep("$('pickDone').onclick=()=>{ $('pickSheet').hidden=true; };",
    "$('pickDone').onclick=()=>{ $('pickSheet').hidden=true; };\n$('pickInvite').onclick=()=>{ $('pickSheet').hidden=true; openDrawer(); showGroup(true); };")
rep("(parseFloat(cs.getPropertyValue('--botovl'))||0) - 90; if(b.offsetHeight > room) w.classList.add('short'); }", "(parseFloat(cs.getPropertyValue('--botovl'))||0) - 30; if(b.offsetHeight > room) w.classList.add('short'); }")
# Swiss days: the title drops "Switzerland:", the eyebrow says it
rep("  $('homeTitle').textContent = DAY.title;", "  const swT=/^Switzerland:\\s*/i.test(DAY.title||''); $('homeTitle').textContent = DAY.title.replace(/^Switzerland:\\s*/i,''); if(swT) $('homeEyebrow').textContent = (dateTxt ? dateTxt+' · ' : '') + '🇨🇭 SWISS DAY';")
# ---------- style ----------
CSS = r'''
/* ===== gloves first v2 ===== */
/* glove sizes */
.mbtn{width:60px;height:60px;border-radius:30px}
.mapbtns{border-radius:31px}
.floatmenu{width:60px;height:60px;border-radius:30px}
.floatmenu svg{width:26px;height:26px}
.tpill{height:60px;border-radius:30px}
.toppills{left:82px;right:80px}
.gpface{width:48px;height:48px}
.gplay{width:40px;height:40px;border-radius:20px}
.gtxt b{font-size:1.05rem}.gtxt small{font-size:.85rem}
.btn{min-height:60px}
.btn.sm{min-height:56px;padding:0 20px;font-size:1.05rem}
.xbtn{width:56px;height:56px}
.grow{min-height:60px;font-size:1.08rem}
.daycard{min-height:64px}
.seg button{min-height:52px}
.legend{font-size:.85rem}
#placesBtn{display:none!important}
.railshai{display:none!important;padding:0}
.railshai .gphoto{width:44px;height:44px}
/* home: one big Start, Steps beside it */
.app:not(.tracking) .actions{grid-template-columns:minmax(0,1fr) 112px;gap:10px}
.app:not(.tracking) #goBtn,.app:not(.tracking) #stepsBtn{grid-column:auto;min-height:84px;border-radius:42px;font-size:1.3rem}
.app:not(.tracking) #stepsBtn{font-weight:800}
#goBtn.locked{min-height:84px!important;font-size:1.1rem!important}
.passbtn{min-height:76px;font-size:1.25rem;border-radius:38px}
.homesum h2{font-size:2rem}
.homesum p{font-size:1.05rem}
/* skiing: direction card on top (black, under the island), speed card at the bottom */
.app.tracking #navPanel{grid-row:1;margin:calc(env(safe-area-inset-top,0px) + 4px) 8px 0;border-radius:38px;background:#07090b;color:#fff;border:0;box-shadow:0 12px 30px rgb(0 0 0/.35);-webkit-backdrop-filter:none;backdrop-filter:none;padding:16px 16px 16px;gap:8px}
.app.tracking .top{grid-row:3;margin:0 8px calc(8px + env(safe-area-inset-bottom,0px));border-radius:40px;padding:8px 16px 16px;grid-template-columns:auto minmax(0,1fr) auto;column-gap:14px;row-gap:4px;align-items:center}
.app.tracking .top .spgrab{grid-column:1/-1}
.app.tracking .top .holdstop{grid-column:3;grid-row:2}
.app.tracking .top .speedrow{grid-row:2}.app.tracking .top .stats{grid-row:2}
.app.tracking #navPanel .next{grid-template-columns:auto minmax(0,1fr);gap:14px}
.app.tracking #navPanel .badge{width:76px;height:76px;border-radius:24px;font-size:1.7rem}
.app.tracking #navPanel .eyebrow{color:#9AA7B2;font-weight:800;letter-spacing:.07em;font-size:.78rem}
.app.tracking #navPanel .nexttxt h2{color:#fff;font-size:1.45rem;line-height:1.12}
.app.tracking #navPanel .nexttxt p{color:#C9D3DB;font-size:.9rem}
.ndist{display:none}
.app.tracking .ndist:not(:empty){display:block;font:800 2.1rem/1 var(--f-num);color:#fff;font-variant-numeric:tabular-nums;margin-top:2px}
.app.tracking #navPanel .then{color:#9AA7B2}.app.tracking #navPanel .then b{color:#fff}
.app.tracking #navPanel .skip,.app.tracking #goBtn,.app.tracking #stepsBtn{display:none!important}
.app.tracking #navPanel .actions{display:none}
.app.tracking.offr #navPanel{background:#5A0E12}
.app.tracking.offr #navPanel .actions{display:grid;grid-template-columns:1fr}
.app.tracking.offr #replanBtn{display:flex;align-items:center;justify-content:center;min-height:64px;border-radius:32px;background:#fff;color:#B3161C;border:0;font:800 1.2rem var(--f-ui)}
.app.tracking .offroute{display:none}
/* speed card contents */
.spgrab{display:none}
.app.tracking .spgrab{display:flex;flex-direction:column;align-items:center;gap:3px;border:0;background:none;padding:2px 0 4px;color:var(--muted);font:800 .7rem var(--f-ui);letter-spacing:.06em;text-transform:uppercase;min-height:30px}
.spgrab i{width:44px;height:5px;border-radius:3px;background:color-mix(in srgb,var(--ink) 25%,transparent)}
.app.tracking .speed{font-size:4.4rem}
.app.tracking .stats{grid-template-columns:repeat(2,minmax(0,1fr));row-gap:6px}
.app.tracking .stat b{font-size:1.35rem}
.holdstop{display:none}
.app.tracking .holdstop{display:block;position:relative;width:80px;height:80px;border:0;background:none;padding:0;touch-action:none;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}
.holdstop svg{position:absolute;inset:0;width:80px;height:80px;transform:rotate(-90deg)}
.hs-track{fill:none;stroke:rgb(216 31 38/.18);stroke-width:6}
.hs-ring{fill:none;stroke:#D81F26;stroke-width:6;stroke-linecap:round}
.hs-in{position:absolute;inset:9px;border-radius:50%;background:#D81F26;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;transition:transform .15s}
.hs-in i{width:16px;height:16px;border-radius:4px;background:#fff}
.hs-in b{font:800 .62rem var(--f-ui);letter-spacing:.06em}
.holdstop.on .hs-in{transform:scale(.92)}
/* skiing: the map tools, Shai on top, no menu or pills over the map */
.app.tracking .railshai{display:grid!important}
.app.tracking #dimBtn,.app.tracking #compassBtn,.app.tracking .floatmenu{display:none!important}
.app.tracking .toppills{left:12px;right:auto;top:calc(var(--topovl,0px) + 10px)}
.app.tracking .donechip{top:calc(var(--topovl,0px) + 80px)!important}
.app.tracking .legend{display:none}
/* Sun mode while skiing: the speed card goes solid white with a black edge */
.app.sun.tracking .top{background:#fff;color:#000;border:3px solid #000}
.app.sun.tracking .speed small,.app.sun.tracking .stat span{color:#000}
.app.sun.tracking .stats{grid-template-columns:repeat(2,minmax(0,1fr))}
.app.sun.tracking .stat:nth-child(n+3){display:grid}
.app.sun.tracking .speed{font-size:4.6rem}
/* sheets: bigger rows and buttons */
.sheetin .btn,.drawerin .btn{min-height:60px}
.htile{min-height:140px}
.hubagain{min-height:52px;font-size:1.05rem}
.tbtns .btn{min-height:60px;padding:0 26px}
.jcolors button{max-width:64px}
.jbtn{min-height:68px}
.pknob{width:64px;height:64px;border-radius:32px;left:6px;top:6px}
.ptrack{height:78px;border-radius:39px}
.plabel{inset:0 16px 0 80px}
/* audit fixes: nothing under 12 px, the steps handle is a real target, Shai lives in the column while skiing */
.app.tracking .toppills>#wxPill.guidepill.guidepill{display:none!important}
.app.tracking .spgrab{min-height:44px;font-size:.78rem}
.kingbtn small,.stopbtn small{font-size:.78rem!important}
.hs-in b{font-size:.78rem}
.app.tracking .stat span{font-size:.75rem}
@media (max-width:370px){.drawerhead .invitebtn span{display:none}.drawerhead .hbtns .invitebtn.xbtn{width:56px;min-width:56px;flex:none;padding:0;justify-content:center}.drawerhead h2{font-size:1.45rem;white-space:normal!important}.drawerhead>div:first-child{min-width:0;flex:1}}
/* not enough height: drop the compass, keep one column */
.mapwrap.short .mapbtns{grid-template-columns:none!important;direction:ltr}
.mapwrap.short #compassBtn{display:none!important}
/* Galaxy S24 / S25 width (360): tighter speed card */
@media (max-width:370px){.app.tracking .speed{font-size:3.5rem}.app.tracking .speed small{font-size:.8rem}.app.tracking .stat b{font-size:1.1rem}.app.tracking .stat span{font-size:.75rem}.app.tracking .top{column-gap:10px;padding:8px 12px 14px}.app.tracking .holdstop{width:72px;height:72px}.holdstop svg{width:72px;height:72px}.hs-in{inset:8px}.app.tracking #navPanel .badge{width:64px;height:64px}.app.tracking #navPanel .nexttxt h2{font-size:1.3rem}.app.tracking .ndist:not(:empty){font-size:1.9rem}}
/* crew: big faces in Everyone mode, tap = go to them */
.picklist.all{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;background:none!important;border:0!important;box-shadow:none!important}
.picklist.all .prow{flex-direction:column;align-items:flex-start;gap:8px;border:1px solid var(--glass-brd);border-radius:26px;background:var(--glass-in);padding:14px;min-height:150px;box-sizing:border-box;position:relative}
.picklist.all .prow .pav{width:56px;height:56px;font-size:1.2rem;line-height:56px}
.picklist.all .prow .pwho b{font-size:1.15rem;font-weight:800}
.picklist.all .prow .pwho::after{content:"";position:absolute;inset:0}
.picklist.all .prow .pdist{color:var(--accent);font-size:1rem}
.prow{min-height:64px}
.prow .ptog .sw{width:60px;height:36px;border-radius:18px}.prow .ptog .sw::after{width:32px;height:32px}.prow .ptog[aria-pressed="true"] .sw::after{left:26px}
.bigcall{min-height:72px!important;border-radius:36px!important;font-size:1.2rem;font-weight:800}
#pickInvite{border-radius:32px}
'''
i = s.index('<style>\n/* Layout: one-screen instrument.'); j = s.index('</style>', i)
s = s[:j] + CSS + s[j:]
open(p, 'w', encoding='utf-8').write(s)
print('gloves v2 patch applied')
