"""Map lines redesign (option B, approved Oct 8):
- route: done steps filled in solid with their own colour, what's ahead is the same colour as an outline,
  lifts ridden turn solid, lifts ahead are dashed with one arrow, no chevrons, no glow
- the current step splits at where you are: behind you filled, ahead outlined
- daily tracks (the same first/last steps every day) are slate grey and fold into one row in Steps
- your track: small dark dots on top of the route; a new piece on every Start and after a jump, so no
  straight lines across town when tracking was off
- while tracking: only the next step is labelled, cafes and restaurants hide, a 'done today' chip
- Settings: Clear tracking history
Usage: python3 tools/lines_patch.py index.html nyc.html"""
import sys

def rep(s, old, new, count=1):
    n = s.count(old)
    assert n == count, (old[:90], n)
    return s.replace(old, new)

LAYERS_NEW = r"""{ id:'route-case', type:'line', source:'route', layout:{'line-cap':'round','line-join':'round'}, paint:{'line-color':'#ffffff','line-width':['case',['get','lift'],8,['get','active'],15,12],'line-opacity':['case',['get','far'],.4,.95]} },
      { id:'route', type:'line', source:'route', filter:['!',['get','lift']], layout:{'line-cap':'round','line-join':'round'}, paint:{'line-color':['case',['get','daily'],'#64748b',['match',['get','col'],'green',t.green,'red',t.red,'black',t.black,t.blue]],'line-width':['case',['get','active'],11,['get','done'],8,9],'line-opacity':['case',['get','far'],.4,1]} },
      { id:'route-core', type:'line', source:'route', filter:['all',['!',['get','lift']],['!',['get','done']]], layout:{'line-cap':'round','line-join':'round'}, paint:{'line-color':'#ffffff','line-width':['case',['get','active'],5,4],'line-opacity':['case',['get','far'],.4,1]} },
      { id:'route-lift-done', type:'line', source:'route', filter:['all',['get','lift'],['get','done']], layout:{'line-cap':'round','line-join':'round'}, paint:{'line-color':['case',['get','daily'],'#64748b',t.lift],'line-width':4.5} },
      { id:'route-lift', type:'line', source:'route', filter:['all',['get','lift'],['!',['get','done']]], layout:{'line-cap':'butt','line-join':'round'}, paint:{'line-color':['case',['get','daily'],'#64748b',t.lift],'line-width':['case',['get','active'],4.5,3.5],'line-opacity':['case',['get','far'],.4,1],'line-dasharray':[2,1.4]} },
      { id:'lift-arrows', type:'symbol', source:'route', filter:['all',['get','lift'],['!',['get','done']]], layout:{'symbol-placement':'line-center','icon-image':'arr-lift','icon-size':1,'icon-allow-overlap':true,'icon-ignore-placement':true,'icon-rotation-alignment':'map','icon-pitch-alignment':'map'} },
      { id:'trail', type:'line', source:'trail', layout:{'line-cap':'round','line-join':'round'}, paint:{'line-color':TRAIL,'line-width':['interpolate',['linear'],['zoom'],11,3,16,5],'line-opacity':['case',['get','lift'],.45,.85],'line-dasharray':[0.1,2]} },
      """

JS_ROUTE_NEW = r"""/* daily tracks: the same steps that open and close every day of the week (walk to the first lift, the home run) */
function dailySet(){
  const out=new Set(), n=WEEK.length; if(n<3 || !steps) return out;
  const cnt={}; WEEK.forEach(d=>{ new Set(d.steps.map(s=>s.type+':'+s.name)).forEach(k=>cnt[k]=(cnt[k]||0)+1); });
  const daily=s=>s.type!=='end' && cnt[s.type+':'+s.name]>=n;
  for(let i=0;i<steps.length && daily(steps[i]);i++) out.add(i);
  for(let i=steps.length-1;i>=0;i--){ if(steps[i].type==='end') continue; if(!daily(steps[i])) break; out.add(i); }
  if(out.size >= steps.length-1) out.clear();
  return out;
}
function shortName(s){ return !s ? '' : s.type==='run' && s.legs && s.legs.length ? s.legs[0].name : s.name; }
function routeData(){
  const f=[], D=dailySet(), me=(mode!=='off') ? (myPos()||[0,0]) : null;
  const add=(c,col,props)=>{ if(c && c.length>1) f.push({ type:'Feature', properties:{...props, col}, geometry:{ type:'LineString', coordinates:c.map(x=>[x[1],x[0]]) } }); };
  for(const s of steps){
    if(s.type==='end') continue;
    const base={ lift:s.type==='lift', daily:D.has(s.i), far: !!me && s.i>cur+2 };
    const parts = (s.type==='run' && s.segs) ? s.segs.map(g=>({col:g.color, c:g.c})) : [{col:s.color||'', c:s.coords}];
    if(s.i!==cur){ for(const p of parts) add(p.c, p.col, {...base, done:s.i<cur, active:false}); continue; }
    // the step I'm on: behind me is filled in, the rest is still to ski
    let bp=-1, bk=-1, bd=60;
    if(me) parts.forEach((p,pi)=>p.c.forEach((x,k)=>{ const d=hav(me,[x[0],x[1]]); if(d<bd){ bd=d; bp=pi; bk=k; } }));
    parts.forEach((p,pi)=>{
      if(bp<0 || pi>bp) add(p.c, p.col, {...base, done:false, active:true});
      else if(pi<bp) add(p.c, p.col, {...base, done:true, active:false});
      else { add(p.c.slice(0,bk+1), p.col, {...base, done:true, active:false}); add(p.c.slice(bk), p.col, {...base, done:false, active:true}); }
    });
  }
  const rank=p=>p.done?0:p.active?2:1;
  f.sort((a,b)=>rank(a.properties)-rank(b.properties));
  return { type:'FeatureCollection', features:f };
}"""

DRAW_NEW = r"""function drawRoute(){
  if(mapReady) map.getSource('route').setData(routeData());
  // while tracking only the next step is labelled; numbers come back when you stop
  const trk = mode!=='off', nx = Math.min(cur+1, steps.length-1);
  stepMarkers.forEach(({g,m})=>{ const el=m.getElement(); if(el.dataset.nums==null) el.dataset.nums=el.textContent;
    const isNext = trk && g.idx.includes(nx);
    el.textContent = isNext ? 'Next · '+shortName(steps[nx]) : el.dataset.nums; el.classList.toggle('next', isNext);
    el.style.opacity = (!trk && g.idx.every(i=>i<cur)) ? .35 : 1; el.classList.toggle('on', !trk && g.idx.includes(cur));
    el.hidden = view!=='nav' || (trk && !isNext); });
  renderDoneChip();
}
function renderDoneChip(){
  const c=$('doneChip'); if(!c || !steps) return;
  const all=steps.filter(s=>s.type!=='end'), done=steps.slice(0,cur).filter(s=>s.type!=='end');
  const reds=done.filter(s=>s.type==='run' && (s.color==='red' || (s.legs||[]).some(l=>l.color==='red'))).length;
  c.hidden = !done.length;
  c.lastChild.textContent = done.length+' of '+all.length+' done'+(reds ? ' · '+reds+' red'+(reds>1?'s':'') : '');
}"""

CSS = r"""
/* ===== map lines: done filled in, ahead outlined, dotted track ===== */
.stepnum.next{background:var(--ink);color:var(--panel);font:700 13px/1 var(--f-ui);height:auto;padding:5px 10px;border-radius:10px;border:2px solid var(--panel)}
.lowzoom .stepnum.next{display:block}
.lg-ahead{background:var(--panel)!important;box-shadow:inset 0 0 0 2.5px var(--p-red);height:9px!important;border-radius:5px!important}
.lg-done{background:var(--p-red)!important;height:7px!important}
.lg-you{background:radial-gradient(circle,#334155 1.8px,transparent 2.2px) 0 50%/7px 7px repeat-x!important;height:7px!important;border-radius:0!important}
.donechip{position:absolute;left:74px;top:12px;z-index:500;display:none;align-items:center;gap:7px;background:var(--panel);color:var(--ink);border:2px solid #000;border-radius:18px;padding:6px 12px 6px 7px;font:700 .95rem var(--f-ui);pointer-events:none}
.app.tracking .donechip:not([hidden]){display:flex}
.donechip svg{flex:none}
.badge.daily{background:#475569}
@media (max-height:700px){#menuSettings .grow{min-height:44px}#menuSettings .note{display:none}}
.srow.fold .t small{display:block;font-weight:500;color:var(--muted);font-size:.85rem}
"""

LEGEND_OLD = '<span><i class="lg-run"></i>Ski down ›</span><span><i class="lg-lift"></i>Lift up »</span>'
LEGEND_NEW = '<span><i class="lg-ahead"></i>Ahead</span><span><i class="lg-done"></i>Done</span><span><i class="lg-you"></i>You</span>'
CHIP = '<div class="donechip" id="doneChip" hidden><svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="11" fill="#15803d"/><path d="M7 12.5l3.2 3.2L17 8.8" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg><span></span></div>'

LIST_OLD = """  steps.forEach((s,i)=>{
    const r = document.createElement('button'); r.type='button';"""
LIST_NEW = """  const D = dailySet();
  steps.forEach((s,i)=>{
    if(D.has(i) && !foldOpen){
      // the same steps every day fold into one row; tap to open them
      if(D.has(i-1) && i>0) return;
      let j=i; while(D.has(j+1)) j++;
      const grp=steps.slice(i,j+1), f=document.createElement('button'); f.type='button';
      f.className='srow fold'+(cur>=i && cur<=j ? ' cur' : '')+(cur>j ? ' done' : '');
      f.innerHTML='<div class="badge daily"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 2l4 4-4 4"/><path d="M3 11V9a3 3 0 0 1 3-3h15"/><path d="M7 22l-4-4 4-4"/><path d="M21 13v2a3 3 0 0 1-3 3H3"/></svg></div><div class="t"></div><div class="m"><span></span><small></small></div>';
      const t=f.querySelector('.t'); t.textContent=(i===0 ? 'Every morning: ' : 'Every day home: ')+grp.map(shortName).join(' → ');
      const sm=document.createElement('small'); sm.textContent='Same every day · '+grp.length+' step'+(grp.length>1?'s':'')+' · tap to see'; t.appendChild(sm);
      f.querySelector('.m span').textContent = grp[0].at || '';
      f.querySelector('.m small').textContent = fmtLen(grp.reduce((a,x)=>a+(x.len||0),0));
      f.onclick=()=>{ foldOpen=true; renderList(); };
      box.appendChild(f); return;
    }
    const r = document.createElement('button'); r.type='button';"""

CLEAR_BTN_OLD = '<button class="grow link" id="simBtn" type="button">Test mode</button>'
CLEAR_BTN_NEW = CLEAR_BTN_OLD + '\n        <button class="grow link" id="clearHist" type="button">Clear tracking history</button>'

CLEAR_JS = r"""
/* Settings > Clear tracking history: every day's track, km, runs skied and changed plans */
var foldOpen=false;
$('clearHist').onclick=()=>{
  const b=$('clearHist');
  if(mode!=='off'){ toast('Stop tracking first, then clear.'); return; }
  if(b.dataset.sure!=='1'){ b.dataset.sure='1'; b.textContent='Tap again: clears every day’s track, km and runs'; setTimeout(()=>{ b.dataset.sure=''; b.textContent='Clear tracking history'; }, 5000); return; }
  b.dataset.sure=''; b.textContent='Clear tracking history';
  store.vis={}; store.skied=[]; visFromStore();
  Object.assign(st, {trail:[], dist:0, vert:0, max:0, elapsed:0, last:null, onLift:false}); cur=0; store.days={};
  try{ localStorage.setItem(KEY, JSON.stringify(store)); }catch(e){}
  if(NATIVE) toNative({cmd:'clear'});
  selectDay(di); drawTrail(true); paintSkied(); renderProgress(); renderMenu();
  toast('Tracking history cleared. Fresh start.');
};
"""

def patch(path):
    s = open(path).read()
    if 'function dailySet()' in s:
        print('already patched', path); return
    # track: dark dots, broken into pieces
    s = rep(s, "const TRAIL = '#7c3aed';", "const TRAIL = '#334155';")
    s = rep(s, """    if(!seg || seg.lift!==lift){ const prev = seg && seg.c.length ? seg.c[seg.c.length-1] : null; seg={lift, c: prev?[prev]:[]}; f.push(seg); }""",
               """    if(!seg || seg.lift!==lift || q[3]){ const prev = !q[3] && seg && seg.c.length ? seg.c[seg.c.length-1] : null; seg={lift, c: prev?[prev]:[]}; f.push(seg); }""") if "for(const q of (st.trail||[])){ const lift=q[2]===1; if(!seg" not in s else rep(s,
               "for(const q of (st.trail||[])){ const lift=q[2]===1; if(!seg || seg.lift!==lift){ const prev = seg && seg.c.length ? seg.c[seg.c.length-1] : null; seg={lift, c: prev?[prev]:[]}; f.push(seg); }",
               "for(const q of (st.trail||[])){ const lift=q[2]===1; if(!seg || seg.lift!==lift || q[3]){ const prev = !q[3] && seg && seg.c.length ? seg.c[seg.c.length-1] : null; seg={lift, c: prev?[prev]:[]}; f.push(seg); }")
    s = rep(s, """  const tr=st.trail||(st.trail=[]); const l=tr[tr.length-1];
  if(l && hav([l[0],l[1]], ll) < 8 && (l[2]===1)===lift) return;
  tr.push([+ll[0].toFixed(6), +ll[1].toFixed(6), lift?1:0]);""",
               """  const tr=st.trail||(st.trail=[]); const l=tr[tr.length-1];
  // a new piece after Stop/Start or a jump (phone off, no GPS): never draw a straight line across the gap
  const brk = !!(l && (st.trailBreak || hav([l[0],l[1]], ll) > 300));
  if(!brk && l && hav([l[0],l[1]], ll) < 8 && (l[2]===1)===lift) return;
  const q=[+ll[0].toFixed(6), +ll[1].toFixed(6), lift?1:0]; if(brk) q.push(1); st.trailBreak=false;
  tr.push(q);""")
    s = rep(s, "mode='gps'; st.last=null; st.sm=null; st.prevSp=null; st.ema=null; st.lastT=null;",
               "mode='gps'; st.last=null; st.sm=null; st.prevSp=null; st.ema=null; st.lastT=null; st.trailBreak=true;", 2)
    # layers: replace trail + route layers, track on top
    i = s.index("{ id:'trail-case'"); j = s.index("{ id:'bg-run-arrows'")
    s = s[:i] + LAYERS_NEW + s[j:]
    # route data + labels
    i = s.index("function routeData(){"); j = s.index("let stepMarkers = [];")
    s = s[:i] + JS_ROUTE_NEW + "\n" + s[j:]
    i = s.index("function drawRoute(){"); j = s.index("\n}\n", i) + 2
    s = s[:i] + DRAW_NEW + s[j:]
    # keep the split current step fresh while moving
    s = rep(s, "if(good) addTrail(here, !!st.onLift);",
               "if(good) addTrail(here, !!st.onLift);\n  if(good && mode!=='off' && Date.now()-(st.rdT||0) > 4000){ st.rdT=Date.now(); drawRoute(); }")
    # cafes hide while tracking (unless you turn a category on while tracking)
    s = rep(s, "function catsOn(){ const on=Object.keys(placeCats).filter(k=>placeCats[k]); return on.length?on:['none']; }",
               "var TRACKING_POI=false, poiTrackOn=false;\nfunction catsOn(){ if(TRACKING_POI && !poiTrackOn) return ['none']; const on=Object.keys(placeCats).filter(k=>placeCats[k]); return on.length?on:['none']; }")
    s = rep(s, "b.onclick=()=>{ placeCats[k]=placeCats[k]?0:1;", "b.onclick=()=>{ if(TRACKING_POI && !poiTrackOn){ poiTrackOn=true; for(const x in placeCats) placeCats[x]=0; } placeCats[k]=placeCats[k]?0:1;")
    s = rep(s, "  APP.classList.toggle('tracking', !!on);\n",
               "  APP.classList.toggle('tracking', !!on);\n  TRACKING_POI=!!on; poiTrackOn=false; if(mapReady){ map.setFilter('pois', poiFilter()); map.setFilter('pois-valley', poiValleyFilter()); }\n  if(typeof drawRoute==='function' && steps) drawRoute();\n")
    s = rep(s, "['route-glow','route-case','route','route-lift','route-arrows','lift-arrows'].forEach(id=>vis2(id,nav));", "['route-case','route','route-core','route-lift-done','route-lift','lift-arrows'].forEach(id=>vis2(id,nav));")
    # legend + chip
    s = rep(s, LEGEND_OLD, LEGEND_NEW, 2)
    s = rep(s, '<div class="legend" id="legend" aria-hidden="true">', CHIP + '\n    <div class="legend" id="legend" aria-hidden="true">')
    s = rep(s, "/* ===== redesign: map-first home", CSS + "/* ===== redesign: map-first home")
    # steps list: daily steps fold
    s = rep(s, LIST_OLD, LIST_NEW)
    # settings: clear
    s = rep(s, CLEAR_BTN_OLD, CLEAR_BTN_NEW)
    s = rep(s, "function renderFollow(){", CLEAR_JS.strip() + "\nfunction renderFollow(){")
    s = rep(s, "recap:openRecap,", "recap:openRecap, routeData, dailySet, trailFC,")
    open(path, 'w').write(s)
    print('patched', path)

for p in sys.argv[1:]:
    patch(p)
