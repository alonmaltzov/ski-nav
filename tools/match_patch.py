"""Map matching: snap GPS to the run/lift you're on, step progress that survives loop routes, quiet re-route when you follow another run."""
import sys
MATCH_JS = r"""
/* ---------- snap to the run or lift you're on (map matching) ---------- */
const MG={}, mkey=(a,o)=>a+':'+o;
BG.forEach((b,bi)=>{ if(b[0]!=='R' && b[0]!=='L') return; const c=b[3];
  for(let j=0;j<c.length-1;j++){ const a0=Math.floor(Math.min(c[j][0],c[j+1][0])*2000), a1=Math.floor(Math.max(c[j][0],c[j+1][0])*2000), o0=Math.floor(Math.min(c[j][1],c[j+1][1])*1400), o1=Math.floor(Math.max(c[j][1],c[j+1][1])*1400);
    for(let a=a0;a<=a1;a++) for(let o=o0;o<=o1;o++) (MG[mkey(a,o)]=MG[mkey(a,o)]||[]).push(bi,j); } });
function projSeg(p,a,b){ const k=Math.cos(p[0]*Math.PI/180), ax=(a[1]-p[1])*111320*k, ay=(a[0]-p[0])*110540, bx=(b[1]-p[1])*111320*k, by=(b[0]-p[0])*110540;
  const dx=bx-ax, dy=by-ay, L=dx*dx+dy*dy; let t=L ? -(ax*dx+ay*dy)/L : 0; t=Math.max(0,Math.min(1,t));
  return { d:Math.hypot(ax+t*dx, ay+t*dy), pt:[a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])] }; }
function projLine(p,c){ let best=null; for(let j=0;j<c.length-1;j++){ const r=projSeg(p,c[j],c[j+1]); if(!best || r.d<best.d) best=r; } return best; }
/* best line within reach: planned steps get a head start, the line you're already on is sticky */
function matchFix(ll, acc, onLift){
  const R=Math.max(20, Math.min(40, (acc||10)*1.6)); let best=null;
  const consider=(id, name, color, r, bonus)=>{ if(!r || r.d>R) return; const score=r.d-bonus-(st.match && st.match.id===id ? 8 : 0); if(!best || score<best.score) best={id, name, color, d:r.d, pt:r.pt, score}; };
  for(const k of [cur, cur+1]){ const s=steps[k]; if(!s || s.type==='end' || !s.coords || s.coords.length<2) continue; if((s.type==='lift')!==!!onLift) continue;
    consider('s'+k, s.type==='lift' ? s.name : (s.legs&&s.legs.length ? s.legs[0].name : s.name), stepColor(s), projLine(ll, s.coords), 6); }
  const a=Math.floor(ll[0]*2000), o=Math.floor(ll[1]*1400), seen=new Set();
  for(let da=-1;da<=1;da++) for(let db=-1;db<=1;db++){ const L=MG[mkey(a+da,o+db)]; if(!L) continue;
    for(let i=0;i<L.length;i+=2){ const bi=L[i], j=L[i+1], key=bi*10000+j; if(seen.has(key)) continue; seen.add(key); const b=BG[bi];
      if((b[0]==='L')!==!!onLift) continue;
      consider('b'+bi, b[2]||(b[0]==='L'?'Lift':'Unnamed run'), b[0]==='L' ? 'lift' : ({nov:'green',eas:'blue',int:'red',adv:'black',exp:'black'}[b[1]]||'blue'), projSeg(ll,b[3][j],b[3][j+1]), 0); } }
  return best;
}
const onPlanNow = pt => [cur-1, cur, cur+1, cur+2, cur+3].some(k=>steps[k] && steps[k].type!=='end' && steps[k].coords.length>1 && distToLine(pt, steps[k].coords) < 30);
let lastAutoPlan=0;
"""

def patch(path):
    s = open(path).read()
    def rep(old, new, count=1):
        nonlocal s
        n = s.count(old)
        if n != count: sys.exit(f'{path}: expected {count} of {old[:90]!r}, found {n}')
        s = s.replace(old, new)
    rep("/* ---------- position pipeline (shared by real GPS and test replay) ---------- */", MATCH_JS + "\n/* ---------- position pipeline (shared by real GPS and test replay) ---------- */")
    rep("""  if(good && !st.onLift) markCoverage(ll, p.acc);
  if(good) addTrail(st.sm ? [st.sm.lat, st.sm.lon] : ll, !!st.onLift);
  updateProgress(p);""", """  // snap to the run or lift you're on: the dot, the trail, skied runs and step progress all use the snapped point
  let snap=null;
  if(good){ const sp = st.sm ? [st.sm.lat, st.sm.lon] : ll; const m = matchFix(sp, p.acc, !!st.onLift);
    if(m){ st.match = {...m, at:p.t}; snap = m.pt; } else if(st.match && p.t - st.match.at > 8000) st.match = null; }
  const here = snap || (st.sm ? [st.sm.lat, st.sm.lon] : ll);
  if(snap) setYou(snap, Math.min(p.acc||10, 8));
  if(good && !st.onLift) markCoverage(here, Math.min(p.acc||15, 20));
  if(good) addTrail(here, !!st.onLift);
  updateProgress(snap ? {...p, lat:snap[0], lon:snap[1]} : p);
  // following a different run than suggested for a while: quietly suggest a new way back into the plan
  if(good && mode!=='off' && st.match && !st.onLift && (p.speed==null || p.speed>1)){
    if(onPlanNow(here)) st.offFrom=null;
    else { st.offFrom = st.offFrom || here;
      if(hav(st.offFrom, here) > 150 && Date.now()-lastAutoPlan > 180000 && typeof planFromHere==='function'){ lastAutoPlan=Date.now(); st.offFrom=null; planFromHere({quiet:true}); } } }""")
    # step progress: finish a step only after travelling a good part of it (loop routes start and end at the same place)
    rep("  const nearEnd = hav(pt,endPt) < Math.max(35, p.acc||0) && (!isLoop || (st.stepDist||0) > 0.6*s.len);",
        "  const nearEnd = hav(pt,endPt) < Math.max(35, p.acc||0) && (st.stepDist||0) > (isLoop ? 0.6*s.len : Math.min(0.5*s.len, Math.max(0, s.len-80)));")
    # skip ahead only to a step you're clearly on (not its end), confirmed over a few fixes
    rep("""      if(distToLine(pt,q.coords) < 20 && hav(pt,q.coords[0]) > 30){ cur=k; st.stepDist=0; persist(); renderStep(); return; } } }""",
        """      if(distToLine(pt,q.coords) < 20 && hav(pt,q.coords[0]) > 30 && hav(pt,q.coords[q.coords.length-1]) > 80){
        st.skipCand = (st.skipCand && st.skipCand.k===k) ? {k, n:st.skipCand.n+1} : {k, n:1};
        if(st.skipCand.n >= 4){ st.skipCand=null; cur=k; st.stepDist=0; persist(); renderStep(); return; } break; } } }""")
    # say which run you're on
    rep("  $('nMeta').textContent = meta;",
        "  if(st.match && mode!=='off' && !String(st.match.id).startsWith('s')) meta = 'You\\u2019re on ' + st.match.name + (st.match.color && st.match.color!=='lift' ? ' ('+st.match.color+')' : '') + ' · ' + meta;\n  $('nMeta').textContent = meta;")
    # quiet re-plan
    rep("function planFromHere(){", "function planFromHere(opts){\n  const quiet = opts && opts.quiet; const say = msg => quiet ? null : showPlanNote(msg);")
    for a in ["  if(!p){ toast('Finding you first…');", "    showPlanNote('Plan from here re-routes", "  if(!best){ showPlanNote(", "  showPlanNote(routed.length ?"]:
        pass
    s = s.replace("  if(!p){ toast('Finding you first…');", "  if(!p){ if(quiet) return null; toast('Finding you first…');", 1)
    s = s.replace("    showPlanNote('Plan from here re-routes", "    say('Plan from here re-routes", 1)
    s = s.replace("  if(!best){ showPlanNote(", "  if(!best){ say(", 1)
    rep("  showPlanNote(routed.length ?", "  if(quiet){ if(routed.length) toast('Route updated from where you are: back on the plan at '+(target ? stepLabel(target).replace(/^(Ski|Take) /,'') : DAY.end.name)+'.'); return {routed:routed.length, rejoin:best.k, minutes:Math.round(best.c/60)}; }\n  showPlanNote(routed.length ?")
    rep("recap:openRecap,", "recap:openRecap, matchFix, get match(){return st.match;}, _mode(m){ mode=m; },")
    # in the city a brisk walk along the bus route is not riding the bus
    rep("  const moving = (p.speed!=null && p.speed > 1.5);", "  const moving = (p.speed!=null && p.speed > (CONFIG.flat ? 3 : 1.5));")
    rep("(onPlannedLift && (moving || rate==null))); }", "(onPlannedLift && (moving || (rate==null && !CONFIG.flat)))); }")
    rep("else if(nl > 60 || (!onPlannedLift && rate!=null && rate < 0.1)){ st.onLift = false; }",
        "else if(nl > 60 || (!onPlannedLift && rate!=null && rate < 0.1) || (CONFIG.flat && p.speed!=null && p.speed < 1.2 && (st.slowSince=st.slowSince||p.t) && p.t-st.slowSince > 45000)){ st.onLift = false; st.slowSince=null; }\n  if(CONFIG.flat && p.speed!=null && p.speed >= 1.2) st.slowSince=null;")
    rep("toNative({cmd:'ctx', lifts: liftLines, title: DAY.title}", "toNative({cmd:'ctx', lifts: liftLines, title: DAY.title, flat: !!CONFIG.flat}")
    open(path, 'w').write(s); print('patched', path)

for p in sys.argv[1:]: patch(p)
