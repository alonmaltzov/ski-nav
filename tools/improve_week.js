/* Improves the week plan inside the page's own scope (injected by tools/improve_week.py):
 * 1. cuts laps (lift + run) that only repeat runs already skied that day or earlier in the week
 * 2. adds missing reds / blacks / blues where they cost the least extra time
 * Uses the app's own piste graph (buildGraph) and step builder (pathSteps), so the steps are the
 * same shape the app makes when it re-plans from where you are. */
window.__improveWeek = function(variant, opts){
  opts = Object.assign({latestArrive: 16*3600+15*60, maxAddPerDay: 5, maxDetour:{red:45*60, black:35*60, blue:35*60},
    swiss: [], crossBy: 15*3600+45*60, swap: null, rebuild: null}, opts||{});
  const swissDay = d => opts.swiss.includes(d.day);
  const swissNames = new Set(GROUPS.filter(x=>x.a==='Switzerland').map(x=>x.n+'|'+x.c));
  const frNames = new Set(GROUPS.filter(x=>x.a!=='Switzerland').map(x=>x.n+'|'+x.c));
  const isSwissStep = s => s.type==='run' && (s.legs||[]).some(l=>swissNames.has(l.name+'|'+l.color) && !frNames.has(l.name+'|'+l.color));
  const lastSwiss = d => { let k=-1; d.steps.forEach((s,i)=>{ if(isSwissStep(s)) k=i; }); return k; };
  if(!RG) RG = buildGraph();
  const g = RG, W = WEEKS[variant];
  const runSpeed = 3.3, liftTime = len => 240 + len/3.6;
  const stepTime = s => s.type==='lift' ? liftTime(s.len||0) : (s.len||0)/runSpeed;
  const ptOf = v => [g.vLat[v], g.vLon[v]];
  const startPt = s => { const c = s.coords && s.coords[0]; return c ? [c[0], c[1]] : null; };
  const endPt = s => { const c = s.coords && s.coords[s.coords.length-1]; return c ? [c[0], c[1]] : null; };

  // ---- dijkstra on the app graph, ignoring this season's lift feed (the trip is in January) ----
  function dij(sources, discount){
    const dist=new Float64Array(g.N).fill(Infinity), prev=new Int32Array(g.N).fill(-1), pe=new Array(g.N);
    const H=[]; const push=(d,v)=>{ H.push([d,v]); let i=H.length-1; while(i>0){ const p=(i-1)>>1; if(H[p][0]<=H[i][0]) break; [H[p],H[i]]=[H[i],H[p]]; i=p; } };
    const pop=()=>{ const top=H[0], last=H.pop(); if(H.length){ H[0]=last; let i=0; for(;;){ const l=2*i+1, r=l+1; let m=i; if(l<H.length&&H[l][0]<H[m][0]) m=l; if(r<H.length&&H[r][0]<H[m][0]) m=r; if(m===i) break; [H[m],H[i]]=[H[i],H[m]]; i=m; } } return top; };
    for(const [v,c] of sources){ if(c<dist[v]){ dist[v]=c; pe[v]=['start']; push(c,v); } }
    while(H.length){ const [d,v]=pop(); if(d>dist[v]) continue;
      for(const e of g.adj[v]){ let c=e[1];
        if(e[2]==='l' && isDragLift(BG[e[3]])) c+=1800;
        if(discount && e[2]==='r' && discount.has(e[3])) c*=0.08;
        const nd=d+c; if(nd<dist[e[0]]){ dist[e[0]]=nd; prev[e[0]]=v; pe[e[0]]=e; push(nd,e[0]); } } }
    return {dist,prev,pe};
  }
  const nearV = (pt, m, ok) => near(pt, m, ok).sort((a,b)=>a[1]-b[1]);
  const runOk = v => BG[g.vLine[v]][0]==='R' || g.vIdx[v]===0;
  // shortest-time search from a point, cached (one search per stop, reused for every candidate run)
  const cache = new Map();
  function from(a, discount, rad){
    const key = a[0].toFixed(5)+','+a[1].toFixed(5)+(discount?':d'+[...discount][0]:'')+(rad?':r'+rad:'');
    if(cache.has(key)) return cache.get(key);
    const src = nearV(a, rad||60, runOk).slice(0,12).map(([v,d])=>[v, 6+d/g.walkV]);
    const D = src.length ? dij(src, discount) : null; cache.set(key, D); return D;
  }
  function costTo(D, b, rad){
    if(!D) return null; let best=null;
    for(const [v,d] of nearV(b, rad||60, v=>g.usable(v))){ const c=D.dist[v]+d/g.walkV; if(isFinite(c) && (!best||c<best.c)) best={v,c}; }
    return best;
  }
  function stepsTo(D, best, a){ return pathSteps(D, best.v, a).filter(s=>s.type==='lift' || (s.len||0)>40); }
  function route(a, b, discount, rad){
    const D=from(a, discount, rad); const best=costTo(D,b,rad); if(!best) return null;
    const st=stepsTo(D,best,a); return [st, st.reduce((t,x)=>t+stepTime(x),0)];
  }

  // ---- what each target run is: its ways in order, top to bottom ----
  const groupWays = {};
  BG.forEach((b,bi)=>{ if(b[0]==='R' && b[5]>=0) (groupWays[b[5]]=groupWays[b[5]]||[]).push(bi); });
  const colorOf = gi => GROUPS[gi].c;
  const lenOf = bi => { const c=BG[bi][3]; let L=0; for(let i=0;i<c.length-1;i++) L+=hav(c[i],c[i+1]); return L; };
  function chainOf(gi){
    const ways = groupWays[gi]||[]; if(!ways.length) return null;
    // top = a way whose first point isn't another way's last point
    const ends = new Set(ways.map(bi=>{ const c=BG[bi][3]; const p=c[c.length-1]; return p[0].toFixed(4)+','+p[1].toFixed(4); }));
    const tops = ways.filter(bi=>{ const p=BG[bi][3][0]; return !ends.has(p[0].toFixed(4)+','+p[1].toFixed(4)); });
    const top = (tops.length?tops:ways).sort((a,b)=>lenOf(b)-lenOf(a))[0];
    // bottom: the way end furthest (by graph) from the top along the run; use the longest-way end as a proxy
    const bottomWay = ways.slice().sort((a,b)=>lenOf(b)-lenOf(a))[0];
    const bc = BG[bottomWay][3];
    const total = ways.reduce((t,bi)=>t+lenOf(bi),0);
    return {gi, ways:new Set(ways), top:[BG[top][3][0][0],BG[top][3][0][1]], bottom:[bc[bc.length-1][0], bc[bc.length-1][1]], total};
  }

  // ---- coverage bookkeeping (by named run, from the step legs) ----
  const legKey = (n,c) => n+'|'+c;
  const groupKey = gi => legKey(GROUPS[gi].n, GROUPS[gi].c);
  function coveredKeys(days){ const s=new Set(); days.forEach(d=>d.steps.forEach(st=>(st.legs||[]).forEach(l=>s.add(legKey(l.name,l.color))))); return s; }

  // ---- timing: re-stamp every step from 9:15, lunch 40 min nearest 12:30 ----
  const fmt = t => { t=Math.round(t/60); return Math.floor(t/60)+':'+String(t%60).padStart(2,'0'); };
  function retime(day){
    let t = day.steps[0] && day.steps[0].t0 || 33300;
    const t00 = t; let lunchIdx = -1, best = 1e9;
    // pick the lunch step first with a dry run
    let tt=t; day.steps.forEach((s,i)=>{ tt+=stepTime(s); const dd=Math.abs(tt-(12*3600+30*60)); if(s.type==='run' && dd<best){ best=dd; lunchIdx=i; } });
    day.steps.forEach((s,i)=>{ s.t0=t; s.at=fmt(t); t+=stepTime(s); s.t1=t; s.end=fmt(t); if(i===lunchIdx) t+=40*60; });
    day.lunch = lunchIdx; day.arrive = fmt(t); day._arriveS = t;
    day.km = Math.round(day.steps.filter(s=>s.type==='run').reduce((a,s)=>a+(s.len||0),0)/100)/10;
    day.lifts = day.steps.filter(s=>s.type==='lift').length;
    day.drags = day.steps.filter(s=>s.type==='lift' && s.drag).length;
    return t;
  }
  function wayHome(day){
    const fd=[day.end.lat, day.end.lon];
    const tg = nearV(fd, 120, v=>g.usable(v)).map(([v,d])=>[v,d]);
    day.steps.forEach(s=>{ const e=endPt(s); if(!e) return; const src=nearV(e,60,runOk).slice(0,8).map(([v,d])=>[v,6+d/g.walkV]); if(!src.length) return;
      const D=dij(src); let best=null; for(const [v,d] of tg){ const c=D.dist[v]; if(isFinite(c)&&(!best||c<best.c)) best={v,c}; }
      if(!best) return; const st=pathSteps(D,best.v,e); const via=[...new Set(st.filter(x=>x.type==='lift').map(x=>x.name))];
      const min=Math.round(st.reduce((t,x)=>t+stepTime(x),0)/60); s.way={min, via, by:fmt(16*3600+30*60-min*60)}; });
    day.cutoff = (()=>{ const h=day.steps.findIndex((s,i)=>i>=(day.homeStep||day.steps.length)); return day.steps[day.homeStep] ? day.steps[day.homeStep].at : day.arrive; })();
  }

  const log = [];
  // ---------- 0. move days around and build new ones from a list of runs ----------
  if(opts.swap){ for(const [a,b] of opts.swap){
    const A=W[a-1], B=W[b-1]; const keep=['day','date'];
    const ca=Object.assign({},A), cb=Object.assign({},B);
    Object.keys(A).forEach(k=>{ if(!keep.includes(k)) delete A[k]; }); Object.keys(B).forEach(k=>{ if(!keep.includes(k)) delete B[k]; });
    Object.keys(cb).forEach(k=>{ if(!keep.includes(k)) A[k]=cb[k]; }); Object.keys(ca).forEach(k=>{ if(!keep.includes(k)) B[k]=ca[k]; });
    log.push('Swapped days '+a+' and '+b);
  } }
  if(opts.rebuild){ for(const [dn, spec] of Object.entries(opts.rebuild)){
    const day=W[dn-1]; const start=[day.start.lat, day.start.lon], end=[day.end.lat, day.end.lon];
    let cur=start, steps=[];
    for(const name of spec.targets){
      const gi = GROUPS.findIndex(x=>x.n===name.n && x.c===name.c && (!name.a || x.a===name.a) && groupWays[GROUPS.indexOf(x)]);
      if(gi<0){ log.push('Rebuild: no run '+name.n); continue; }
      const T=chainOf(gi); const r1=route(cur, T.top) || route(cur, T.top, null, 200); const r2=route(T.top, T.bottom, T.ways) || route(T.top, T.bottom, T.ways, 150);
      if(!r1||!r2){ log.push('Rebuild: no way to '+name.n); continue; }
      if(!r2[0].some(s=>(s.legs||[]).some(l=>l.name===name.n))) log.push('Rebuild: route misses '+name.n);
      steps.push(...r1[0], ...r2[0]); cur=T.bottom;
    }
    const rh=route(cur, end) || route(cur, end, null, 200); if(!rh){ log.push('Rebuild: no way home from '+cur); continue; } day.homeStep=steps.length; steps.push(...rh[0]);
    day.steps=steps; Object.assign(day, spec.meta||{});
    log.push('Day '+dn+' built: '+steps.length+' steps');
  } }
  W.forEach(retime);
  // ---------- 1. cut laps that only repeat ----------
  // a lap only goes if every metre of its run was already skied (by the map, not just by name)
  const cell = p => Math.floor(p[0]*4000)+':'+Math.floor(p[1]*2800);
  const dense = coords => { const out=[]; for(let i=0;i<coords.length-1;i++){ const a=coords[i], b=coords[i+1]; const n=Math.max(1,Math.floor(hav(a,b)/10)); for(let q=0;q<n;q++) out.push([a[0]+(b[0]-a[0])*q/n, a[1]+(b[1]-a[1])*q/n]); } return out; };
  const runPts = st => dense((st.segs||[]).flatMap(sg=>sg.c));
  function addPts(set, st){ for(const p of runPts(st)) set.add(cell(p)); }
  function isSkied(set, st){ const pts=runPts(st).filter((p,i,a)=>i>8 && i<a.length-8); if(pts.length<5) return false;
    let hit=0; for(const p of pts){ const a=Math.floor(p[0]*4000), o=Math.floor(p[1]*2800); let ok=false;
      for(let da=-1;da<=1&&!ok;da++) for(let db=-1;db<=1&&!ok;db++) if(set.has((a+da)+':'+(o+db))) ok=true; if(ok) hit++; }
    return hit >= 0.95*pts.length; }
  const seenWeek = new Set();
  W.forEach(day=>{
    const fixedHead = 3, fixedTail = day.homeStep!=null ? day.homeStep : day.steps.length;
    const seenDay = new Set();
    const keep = [];
    for(let i=0;i<day.steps.length;i++){
      const s=day.steps[i], nx=day.steps[i+1];
      const inFixed = i<fixedHead || i>=fixedTail-1;
      if(!inFixed && s.type==='lift' && nx && nx.type==='run' && i+2<day.steps.length){
        const prevEnd = keep.length ? endPt(keep[keep.length-1]) : null, nextStart = startPt(day.steps[i+2]);
        if(prevEnd && nextStart && hav(prevEnd,nextStart) < 80 && (isSkied(seenDay, nx) || isSkied(seenWeek, nx))){
          log.push('Day '+day.day+': cut '+s.name+' + '+nx.name+' (already skied)');
          i++; continue;
        }
      }
      keep.push(s); if(s.type==='run') addPts(seenDay, s);
    }
    const removed = day.steps.length - keep.length;
    day.homeStep = day.homeStep!=null ? Math.max(0, day.homeStep - removed) : day.homeStep;
    day.steps = keep;
    seenDay.forEach(k=>seenWeek.add(k));
    retime(day);
  });

  // ---------- 2. add missing runs where they cost least ----------
  const weight = {red:3, black: opts.blacks===false?0:2.2, blue:1};
  let covered = coveredKeys(W);
  const targets = GROUPS.map((x,gi)=>({gi, x})).filter(o=>weight[o.x.c] && !covered.has(groupKey(o.gi)) && groupWays[o.gi])
    .map(o=>Object.assign(o, chainOf(o.gi))).filter(o=>o.top && o.total>140 && !(o.x.c==='blue' && (/^(Unnamed|Montée|Promenade|Rue|Accès|Zone|Snowpark|Retour|Liaison|Chemin)/i.test(o.x.n) || o.total<400)));
  // reds first, then blacks, then blues; longer first within a colour
  targets.sort((a,b)=>weight[b.x.c]-weight[a.x.c] || b.total-a.total);
  const added = {};
  for(const T of targets){
    if(covered.has(groupKey(T.gi))) continue;
    const r2=route(T.top, T.bottom, T.ways); if(!r2) { log.push('No way down '+T.x.n); continue; }
    if(!r2[0].some(s=>(s.legs||[]).some(l=>l.name===T.x.n))) { log.push('Route misses '+T.x.n); continue; }
    const Dback = from(T.bottom);
    let best=null; const cands=[];
    for(const day of W){
      if((added[day.day]||0) >= opts.maxAddPerDay) continue;
      if(opts.areas && opts.areas[day.day] && !opts.areas[day.day].includes(T.x.a)) continue;
      const lastK = (day.homeStep!=null ? day.homeStep : day.steps.length) - 1;
      for(let k=2; k<lastK; k++){
        const a=endPt(day.steps[k]), b=startPt(day.steps[k+1]); if(!a||!b) continue;
        if(hav(a,T.top) > 6000) continue;                       // only nearby detours
        const c1=costTo(from(a), T.top); if(!c1) continue;
        const c3=costTo(Dback, b); if(!c3) continue;
        const rough=c1.c+r2[1]+c3.c;              // graph time (fast skiing): a lower bound
        if(rough > opts.maxDetour[T.x.c]) continue;
        cands.push({day,k,rough,a,b,c1,c3});
      }
    }
    // check the best few with the same timing the day uses
    cands.sort((x,y)=>x.rough-y.rough);
    for(const c of cands.slice(0,8)){
      const st=[...stepsTo(from(c.a),c.c1,c.a), ...r2[0], ...stepsTo(Dback,c.c3,T.bottom)];
      const cost=st.reduce((t,x)=>t+stepTime(x),0);
      if(cost > opts.maxDetour[T.x.c]*1.6 || c.day._arriveS + cost > opts.latestArrive) continue;
      if(swissDay(c.day)){ const ls=lastSwiss(c.day);
        const newsSwiss = st.some(isSwissStep);
        const endSwiss = c.k < ls ? c.day.steps[ls].t1 + cost : (newsSwiss ? c.day.steps[c.k].t1 + cost : -1);
        if(endSwiss > opts.crossBy) continue; }
      if(!best || cost<best.cost) best=Object.assign(c,{cost,steps:st});
    }
    if(!best){ log.push('Could not fit '+T.x.c+' '+T.x.n+' ('+T.x.a+') without arriving after '+fmt(opts.latestArrive)); continue; }
    best.day.steps.splice(best.k+1, 0, ...best.steps);
    if(best.day.homeStep!=null) best.day.homeStep += best.steps.length;
    added[best.day.day]=(added[best.day.day]||0)+1;
    retime(best.day);
    covered = coveredKeys(W);
    log.push('Day '+best.day.day+': added '+T.x.c+' '+T.x.n+' ('+T.x.a+'), +'+Math.round(best.cost/60)+' min');
  }
  W.forEach(day=>{ retime(day); wayHome(day); });
  return {log, days: W.map(d=>({day:d.day, title:d.title, km:d.km, lifts:d.lifts, arrive:d.arrive, homeAt:d.steps[d.homeStep]&&d.steps[d.homeStep].at, swissOut: lastSwiss(d)>=0 ? fmt(d.steps[lastSwiss(d)].t1) : null, steps:d.steps.length}))};
};
window.__weekJSON = v => JSON.stringify(WEEKS[v]);
