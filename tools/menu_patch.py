"""Menu redesign: bottom sheet, week on one screen, settings behind a gear. Applied to index.html and nyc.html."""
import sys, re
GEAR = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>'
XSVG = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>'
BACK = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>'

DRAWER = f'''<div class="drawer" id="drawer" hidden>
  <nav class="drawerin" aria-label="Week menu">
    <div class="mpane" id="menuMain">
      <div class="drawerhead">
        <div><h2 id="tripTitle">Avoriaz week</h2><p id="tripSub"></p></div>
        <div class="hbtns"><button class="xbtn" id="settingsBtn" type="button" aria-label="Settings">{GEAR}</button><button class="xbtn" id="drawerClose" type="button" aria-label="Close menu">{XSVG}</button></div>
      </div>
      <button class="goalcard" id="goalCard" type="button">
        <span class="ghead"><span class="sub" id="goalLabel">Week goal</span><span class="maplink">Map ›</span></span>
        <span class="gline"><span class="big" id="goalBig">0 of 0</span><span class="sub" id="goalSub"></span></span>
        <div class="bar"><i class="b" id="goalBarDone"></i><i class="p" id="goalBarPlan"></i></div>
      </button>
      <div class="sect">Plan</div>
      <div class="group" id="dayList"></div>
    </div>
    <div class="mpane" id="menuSettings" hidden>
      <div class="drawerhead sethead"><button class="xbtn" id="settingsBack" type="button" aria-label="Back to the week">{BACK}</button><h2>Settings</h2></div>
      <div class="group">
        <div class="grow col"><span>Plan style</span><div class="seg seg3" id="styleSeg"><button type="button" data-v="red" aria-pressed="true">Reds first</button><button type="button" data-v="std" aria-pressed="false">Blue + red</button><button type="button" data-v="black" aria-pressed="false">With blacks</button></div></div>
        <div class="grow"><span>Sun mode</span><div class="seg" id="sunSeg"><button type="button" data-v="auto" aria-pressed="true">Auto</button><button type="button" data-v="on" aria-pressed="false">On</button><button type="button" data-v="off" aria-pressed="false">Off</button></div></div>
        <div class="grow"><span>Units</span><div class="seg" id="unitSeg"><button type="button" data-v="met" aria-pressed="true">km</button><button type="button" data-v="imp" aria-pressed="false">miles</button></div></div>
        <button class="grow toggle" id="followBtn2" type="button" role="switch" aria-pressed="false"><span>Follow the plan<small>Warn me when I leave the route</small></span><span class="sw"></span></button>
      </div>
      <div class="sect">More</div>
      <div class="group">
        <button class="grow link" id="menuRunsList" type="button">Every run in the plan</button>
        <button class="grow link" id="simBtn" type="button">Test mode</button>
        <a class="grow link" id="otherApp" href="#">Practice in NYC</a>
      </div>
      <p class="note">Chairs and gondolas only, no T-bars, every lift ridden up. Piste data from OpenStreetMap. Check lift status on the day.</p>
    </div>
  </nav>
</div>'''

CSS = r"""
/* ===== menu: bottom sheet, week on one screen, settings behind the gear ===== */
.drawer{align-items:flex-end}
.drawerin{width:100%;height:auto;max-height:calc(100% - 40px - env(safe-area-inset-top,0px));background:var(--bg);border-radius:24px 24px 0 0;animation:sheetup .24s cubic-bezier(.2,.8,.2,1);padding:20px 16px calc(16px + env(safe-area-inset-bottom,0px));box-shadow:0 -6px 24px rgb(0 0 0/.2);position:relative;display:block}
.drawerin::before{content:"";position:absolute;top:7px;left:50%;width:40px;height:5px;margin-left:-20px;border-radius:3px;background:color-mix(in srgb,var(--muted) 40%,transparent)}
.mpane{display:grid;gap:12px;min-width:0}
.mpane>*{min-width:0}
.drawerhead{align-items:center}
.drawerhead h2{font:800 1.8rem/1.05 var(--f-num)}
.hbtns{display:flex;gap:8px;flex:none}
.xbtn{background:var(--panel)}
.sethead{justify-content:flex-start;gap:10px}
.sect{margin:4px 4px -4px}
.goalcard{border:0;background:var(--panel);border-radius:18px;padding:14px 16px;gap:10px}
.goalcard .ghead{display:flex;justify-content:space-between;align-items:baseline}
.goalcard .ghead .sub{font-size:.8rem;letter-spacing:.06em;text-transform:uppercase;font-weight:700}
.goalcard .maplink{color:var(--accent);font-weight:600;font-size:.95rem}
.goalcard .gline{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
.goalcard .big{font:800 2rem/1 var(--f-num)}
.goalcard .bar{height:10px;border-radius:5px}
.group{background:var(--panel);border-radius:18px;overflow:hidden;display:grid}
.group>*+*{border-top:1px solid var(--line)}
.daycard{border:0;border-radius:0;background:none;min-height:58px;padding:6px 14px;grid-template-columns:44px minmax(0,1fr) auto;gap:12px}
.daycard.sel{box-shadow:none;background:color-mix(in srgb,var(--accent) 12%,transparent)}
.daycard .dn{display:grid;justify-items:center;line-height:1}
.daycard .dn small{font-size:.7rem;font-weight:700;letter-spacing:.06em;color:var(--muted)}
.daycard .dn b{font:800 1.4rem var(--f-num)}
.daycard.sel .dn small,.daycard.sel .dn b,.daycard .today{color:var(--accent)}
.daycard .dt{min-width:0;display:grid}
.daycard .dt b{font-weight:600;font-size:1.05rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.daycard.sel .dt b{font-weight:700}
.daycard .dt small{font-size:.85rem;font-weight:600;color:var(--muted)}
.daycard .dr{font-size:.9rem;color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
.daycard .dr svg{display:block;color:var(--ok)}
.grow{display:flex;justify-content:space-between;align-items:center;gap:12px;min-height:56px;padding:8px 14px;box-sizing:border-box;width:100%;font:600 1.05rem var(--f-ui);color:var(--ink);background:none;border:0;border-radius:0;text-align:left}
.grow.col{display:grid;justify-content:stretch;gap:10px;padding:12px 14px}
.grow.toggle{border:0;border-radius:0;background:none}
.grow.link{text-decoration:none;font-weight:500}
.grow.link::after{content:"›";font-size:1.4rem;color:var(--muted);line-height:1}
.seg{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(58px,1fr);background:color-mix(in srgb,var(--muted) 14%,transparent);border-radius:12px;padding:3px;gap:2px}
.seg3{grid-auto-columns:minmax(0,1fr)}
.seg button{min-height:44px;border:0;border-radius:10px;background:none;color:var(--ink);font:600 .95rem var(--f-ui);padding:0 8px}
.seg button[aria-pressed="true"]{background:var(--panel);box-shadow:0 1px 4px rgb(11 22 32/.16);font-weight:700}
.mpane .note{margin:0 4px}
"""

JS_SWIPE = r"""
/* menu: gear opens settings, swipe down closes */
function showSettings(on){ $('menuMain').hidden=on; $('menuSettings').hidden=!on; document.querySelector('.drawerin').scrollTop=0; }
$('settingsBtn').onclick=()=>showSettings(true); $('settingsBack').onclick=()=>showSettings(false);
$('drawer').onclick=e=>{ if(e.target.id==='drawer') closeDrawer(); };
(()=>{ const s=document.querySelector('.drawerin'); let y0=null, dy=0;
  s.addEventListener('touchstart',e=>{ y0 = s.scrollTop<=0 ? e.touches[0].clientY : null; dy=0; },{passive:true});
  s.addEventListener('touchmove',e=>{ if(y0==null) return; dy=e.touches[0].clientY-y0; if(dy>0){ s.style.transform='translateY('+dy+'px)'; } },{passive:true});
  s.addEventListener('touchend',()=>{ if(y0==null) return; s.style.transform=''; if(dy>90) closeDrawer(); y0=null; });
})();
document.querySelectorAll('#unitSeg [data-v]').forEach(b=>b.onclick=()=>{ if(units===b.dataset.v) return; units=b.dataset.v; persist(); renderUnits(); renderStats(); renderStep(); renderMenu(); });
"""

CHECK = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-label="Skied"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'

def patch(path):
    s = open(path).read()
    def rep(old, new, count=1):
        nonlocal s
        n = s.count(old)
        if n != count: sys.exit(f'{path}: expected {count} of {old[:80]!r}, found {n}')
        s = s.replace(old, new)
    a = s.index('<div class="drawer" id="drawer" hidden>'); b = s.index('</nav>\n</div>', a) + len('</nav>\n</div>')
    s = s[:a] + DRAWER + s[b:]
    i = s.index('/* ===== redesign: map-first home')
    s = s[:i] + CSS + s[i:]
    # day rows: one line
    old_rows = s[s.index("    b.innerHTML='<div class=\"daynum\">"):s.index("    b.onclick=()=>{ selectDay(i); closeDrawer(); };")]
    new_rows = """    b.innerHTML='<span class="dn"><small></small><b></b></span><span class="dt"><b></b></span><span class="dr"></span>';
    b.querySelector('.dn small').textContent=wd.toUpperCase(); b.querySelector('.dn b').textContent=dn;
    b.querySelector('.dt b').textContent=d.title;
    const kmTxt=(units==='imp'?(d.km*0.6214).toFixed(1)+' mi':Math.round(d.km)+' km');
    if(i===ti || i===di){ const m=document.createElement('small'); if(i===ti) m.className='today'; m.textContent=(i===ti?'Today · ':'')+(sd.dist>500?'skied '+fmtLen(sd.dist):kmTxt+' · '+d.lifts+' lifts'); b.querySelector('.dt').appendChild(m); }
    if(sd.dist>500) b.querySelector('.dr').innerHTML='""" + CHECK + """'; else if(!(i===ti || i===di)) b.querySelector('.dr').textContent=kmTxt;
    b.setAttribute('aria-label', d.date+', '+d.title+(sd.dist>500?', skied':'')+(i===ti?', today':''));
"""
    s = s.replace(old_rows, new_rows)
    rep("$('goalBig').textContent=done+' of '+tot+' skied';", "$('goalBig').textContent=done+' of '+tot; $('goalBarDone').style.background = variant==='red' ? 'var(--p-red)' : 'var(--p-blue)';")
    rep("$('goalSub').textContent='The week plan covers '+plan+' of them. Tap to see the map.';", "$('goalSub').textContent='plan covers '+plan;")
    rep("""  document.querySelector('#goalCard .sub').textContent = variant==='red' ? 'Red runs we can reach this week' : variant==='black' ? 'Blue, red & black runs we can reach this week' : 'Blue & red runs we can reach this week';""",
        """  $('goalLabel').textContent = 'Week goal · ' + (variant==='red' ? 'red runs' : variant==='black' ? 'blue, red + black' : 'blue + red');""")
    rep("  $('unitBtn').textContent = units==='imp' ? 'Switch to km' : 'Switch to miles';", "  document.querySelectorAll('#unitSeg [data-v]').forEach(b=>b.setAttribute('aria-pressed', b.dataset.v===units?'true':'false'));")
    rep("function renderFollow(){ const b=$('followBtn2'); if(!b) return; b.setAttribute('aria-pressed', store.follow?'true':'false'); b.textContent = 'Follow the plan: ' + (store.follow?'on':'off'); }",
        "function renderFollow(){ const b=$('followBtn2'); if(!b) return; b.setAttribute('aria-pressed', store.follow?'true':'false'); }")
    rep("$('unitBtn').onclick=()=>{ units = units==='imp'?'met':'imp'; persist(); renderUnits(); renderStats(); renderStep(); renderMenu(); };", JS_SWIPE)
    rep("function openDrawer(){ renderMenu(); $('drawer').hidden=false; }", "function openDrawer(){ renderMenu(); showSettings(false); $('drawer').hidden=false; }")
    open(path, 'w').write(s)
    print('patched', path)

for p in sys.argv[1:]: patch(p)
