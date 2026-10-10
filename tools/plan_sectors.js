/* Plans each day as one area of the Portes du Soleil, inside the app's own router.
 * Greedy: from where you are, take the next run (reds first, then blacks, then blues) that gives the
 * most new skiing per minute, as long as you still reach La Folie Douce by the finish time and, on
 * Swiss days, are back on the French side by the cut-off. Lunch is 40 min nearest 12:30.
 * Needs tools/links.js (Morzine and Chatel connections) loaded first. */
window.__planSectors = function(variant, opts){
  opts = Object.assign({start: 9*3600, runSpeed: 4.2, queue: 150, lookahead: true, finish: 16*3600+45*60, crossBy: 16*3600, lunchAt: 12*3600+30*60, lunchMin: 40,
    weight: {red: 3, black: 2.2, blue: 1.4, green: 0}, days: []}, opts||{});
  __addLinks(); RG = buildGraph();
  const g = RG, W = WEEKS[variant], log = [];
  // timing: skiing ~15 km/h average with stops; lifts = queue + ride at the lift's own speed
  const runSpeed = opts.runSpeed;
  const LIFT_V = {gon:5.5, cab:6, mix:5, fun:6, cha:4.2};
  const liftV = bi => (bi!=null && BG[bi]) ? (LIFT_V[BG[bi][1]] || 3) : 4;
  const stepTime = s => s.type==='lift' ? opts.queue + (s.len||0)/liftV(s._bi) : (s.len||0)/runSpeed;
  const fmt = t => { t=Math.round(t/60); return Math.floor(t/60)+':'+String(t%60).padStart(2,'0'); };
  const COL = {nov:'green', eas:'blue', int:'red', adv:'black', exp:'black', fre:'black'};

  // ---- France or Switzerland: a rough line along the border through the ski area ----
  const BORDER = [[46.10,6.800],[46.172,6.794],[46.190,6.807],[46.215,6.826],[46.240,6.846],[46.258,6.866],[46.275,6.874],[46.288,6.858],[46.300,6.836],[46.330,6.805]];
  function borderLon(lat){ for(let i=0;i<BORDER.length-1;i++){ const [a0,o0]=BORDER[i],[a1,o1]=BORDER[i+1]; if(lat<=a1) return o0+(o1-o0)*Math.max(0,(lat-a0)/(a1-a0)); } return BORDER[BORDER.length-1][1]; }
  const swissPt = p => p[1] > borderLon(p[0]);

  // ---- router helpers (same graph as Plan from here) ----
  function dij(sources, discount){
    const dist=new Float64Array(g.N).fill(Infinity), prev=new Int32Array(g.N).fill(-1), pe=new Array(g.N);
    const H=[]; const push=(d,v)=>{ H.push([d,v]); let i=H.length-1; while(i>0){ const p=(i-1)>>1; if(H[p][0]<=H[i][0]) break; [H[p],H[i]]=[H[i],H[p]]; i=p; } };
    const pop=()=>{ const top=H[0], last=H.pop(); if(H.length){ H[0]=last; let i=0; for(;;){ const l=2*i+1, r=l+1; let m=i; if(l<H.length&&H[l][0]<H[m][0]) m=l; if(r<H.length&&H[r][0]<H[m][0]) m=r; if(m===i) break; [H[m],H[i]]=[H[i],H[m]]; i=m; } } return top; };
    for(const [v,c] of sources){ if(c<dist[v]){ dist[v]=c; pe[v]=['start']; push(c,v); } }
    while(H.length){ const [d,v]=pop(); if(d>dist[v]) continue;
      for(const e of g.adj[v]){ let c=e[1];
        if(e[2]==='l'){ const b=BG[e[3]]; let len=0; for(let j=0;j<b[3].length-1;j++) len+=hav(b[3][j],b[3][j+1]); c = opts.queue + len/liftV(e[3]) + (isDragLift(b)&&!/^(Walk|Bus)/.test(b[2]||'')?600:0); }
        if(e[2]==='r') c *= 8/runSpeed;                                       // graph runs at 8 m/s
        if(discount && e[2]==='r' && discount.has(e[3])) c*=0.08;
        const nd=d+c; if(nd<dist[e[0]]){ dist[e[0]]=nd; prev[e[0]]=v; pe[e[0]]=e; push(nd,e[0]); } } }
    return {dist,prev,pe};
  }
  const nearV = (pt, m, ok) => near(pt, m, ok).sort((a,b)=>a[1]-b[1]);
  const runOk = v => BG[g.vLine[v]][0]==='R' || g.vIdx[v]===0;
  const cache = new Map();
  function from(a, discount){
    const key=a[0].toFixed(5)+','+a[1].toFixed(5)+(discount?':d'+[...discount].join('.'):'');
    if(cache.has(key)) return cache.get(key);
    let src=nearV(a,60,runOk).slice(0,12); if(!src.length) src=nearV(a,200,runOk).slice(0,12);
    const D = src.length ? dij(src.map(([v,d])=>[v,6+d/g.walkV]), discount) : null; cache.set(key,D); return D;
  }
  function costTo(D, b, rad){ if(!D) return null; let best=null;
    for(const [v,d] of nearV(b, rad||60, v=>g.usable(v))){ const c=D.dist[v]+d/g.walkV; if(isFinite(c) && (!best||c<best.c)) best={v,c}; } return best; }
  function route(a, b, discount){
    const D=from(a, discount); const best=costTo(D,b) || costTo(D,b,200); if(!best) return null;
    const st=pathSteps(D,best.v,a).filter(s=>s.type==='lift' || (s.len||0)>40);
    return {steps: st, t: st.reduce((t,x)=>t+stepTime(x),0)};
  }

  // ---- targets: every named piste in an area, as one run from its top to its bottom ----
  const lenOf = c => { let L=0; for(let i=0;i<c.length-1;i++) L+=hav(c[i],c[i+1]); return L; };
  function targetsIn(inArea){
    const by = {};
    BG.forEach((b,bi)=>{ if(b[0]!=='R') return; const col=COL[b[1]]||'blue'; if(!opts.weight[col]) return;
      const c=b[3]; if(!inArea(c[0]) && !inArea(c[c.length-1])) return;
      const name=b[2] || ('Unnamed '+col); const k=name+'|'+col+(b[2]?'':'|'+bi);
      (by[k]=by[k]||{name, color:col, ways:[]}).ways.push(bi); });
    const out=[];
    for(const T of Object.values(by)){
      const total=T.ways.reduce((t,bi)=>t+lenOf(BG[bi][3]),0);
      if(total < (T.name.startsWith('Unnamed') ? 300 : 150)) continue;
      if(/^(Montée|Promenade|Rue|Accès|Zone|Snowpark|Retour|Liaison|Chemin|Piste de luge|Luge|Raquette|Itinéraire)/i.test(T.name)) continue;
      const ends=new Set(T.ways.map(bi=>{ const p=BG[bi][3][BG[bi][3].length-1]; return p[0].toFixed(4)+','+p[1].toFixed(4); }));
      const tops=T.ways.filter(bi=>{ const p=BG[bi][3][0]; return !ends.has(p[0].toFixed(4)+','+p[1].toFixed(4)); });
      const top=(tops.length?tops:T.ways).sort((a,b)=>lenOf(BG[b][3])-lenOf(BG[a][3]))[0];
      const bw=T.ways.slice().sort((a,b)=>lenOf(BG[b][3])-lenOf(BG[a][3]))[0], bc=BG[bw][3];
      out.push(Object.assign(T, {total, set:new Set(T.ways), top:[BG[top][3][0][0],BG[top][3][0][1]], bottom:[bc[bc.length-1][0],bc[bc.length-1][1]]}));
    }
    return out;
  }
  // a step covers a target if it skis most of its length
  // a route covers a target if it passes over at least half of the target's points (geometry, so unnamed runs work too)
  const cell = p => Math.floor(p[0]*4000)+':'+Math.floor(p[1]*2800);
  function cellsOf(steps){ const set=new Set(); for(const s of steps) if(s.type==='run') for(const sg of (s.segs||[])){ const c=sg.c;
      for(let i=0;i<c.length-1;i++){ const a=c[i], b=c[i+1]; const n=Math.max(1,Math.floor(hav(a,b)/8)); for(let q=0;q<=n;q++) set.add(cell([a[0]+(b[0]-a[0])*q/n, a[1]+(b[1]-a[1])*q/n])); } } return set; }
  function coveredBy(steps, T, cells){ cells = cells || cellsOf(steps); let hit=0, all=0;
    for(const bi of T.ways){ const c=BG[bi][3]; for(const p of c){ all++; const a=Math.floor(p[0]*4000), o=Math.floor(p[1]*2800); let ok=false;
      for(let da=-1;da<=1&&!ok;da++) for(let db=-1;db<=1&&!ok;db++) if(cells.has((a+da)+':'+(o+db))) ok=true; if(ok) hit++; } }
    return all>0 && hit >= 0.5*all; }

  // ---- timing ----
  function retime(day){
    let t=opts.start, lunchIdx=-1, best=1e9, tt=t;
    day.steps.forEach((s,i)=>{ tt+=stepTime(s); const dd=Math.abs(tt-opts.lunchAt); if(s.type==='run' && dd<best){ best=dd; lunchIdx=i; } });
    day.steps.forEach((s,i)=>{ s.t0=t; s.at=fmt(t); t+=stepTime(s); s.t1=t; s.end=fmt(t); if(i===lunchIdx) t+=opts.lunchMin*60; });
    day.lunch=lunchIdx; day.arrive=fmt(t); day._arriveS=t;
    day.km=Math.round(day.steps.filter(s=>s.type==='run').reduce((a,s)=>a+(s.len||0),0)/100)/10;
    day.lifts=day.steps.filter(s=>s.type==='lift').length; day.drags=day.steps.filter(s=>s.type==='lift'&&s.drag).length;
    return t;
  }
  const stepSwiss = s => (s.coords||[]).some(p=>swissPt(p)) || (s.segs||[]).some(sg=>sg.c.some(p=>swissPt(p)));
  function lastSwissEnd(steps, t0){ let t=t0, last=null; steps.forEach(s=>{ const e=t+stepTime(s); if(stepSwiss(s)) last=e; t=e; }); return last; }

  // ---- plan one day ----
  const seenWeek = new Set();
  function planDay(day, spec){
    const start=[day.start.lat, day.start.lon], end=[day.end.lat, day.end.lon];
    const T = targetsIn(spec.area).filter(x=>!(spec.skipNames||[]).includes(x.name));
    const main = new Set(T); let filling=false;
    let cur=start, t=opts.start, steps=[], lunchDone=false, done=new Set();
    const lunchLeft = tnow => (!lunchDone && tnow < opts.lunchAt+3600) ? opts.lunchMin*60 : 0;
    for(let guard=0; guard<60; guard++){
      let best=null;
      for(const x of T){ if(done.has(x)) continue;
        const r1=route(cur, x.top); if(!r1) continue;
        const r2=route(x.top, x.bottom, x.set); if(!r2) continue;
        if(!coveredBy(r2.steps, x)) continue;
        const cost=r1.t+r2.t; if(cost > (steps.length ? 75 : 200)*60) continue;
        const rh=route(x.bottom, end); if(!rh) continue;
        const tEnd=t+cost+lunchLeft(t+cost);
        if(tEnd+rh.t > opts.finish) continue;
        if(spec.swiss){ const sw=lastSwissEnd([...r1.steps, ...r2.steps, ...rh.steps], t); if(sw!=null && sw+lunchLeft(t+cost) > opts.crossBy) continue; }
        const fresh = seenWeek.has(x.name+'|'+x.color) ? 0.35 : 1;
        const value = opts.weight[x.color] * Math.min(x.total, 2500) * fresh;
        let score = value / (cost + 120);
        if(opts.lookahead){ const D2=from(x.bottom); let bn=0;
          for(const y of T){ if(y===x||done.has(y)) continue; const c1=costTo(D2,y.top); if(!c1) continue; const r2y=route(y.top,y.bottom,y.set); if(!r2y) continue;
            const fy=seenWeek.has(y.name+'|'+y.color)?0.35:1; const v=opts.weight[y.color]*Math.min(y.total,2500)*fy/(c1.c*0.6+r2y.t+120); if(v>bn) bn=v; }
          score = 0.6*score + 0.4*bn; }
        if(!best || score>best.score) best={x, r1, r2, cost, score};
      }
      if(!best){ const why={}; const W_=k=>why[k]=(why[k]||0)+1;
        for(const x of T){ if(done.has(x)) continue; const r1=route(cur,x.top); if(!r1){W_('noway');continue;} const r2=route(x.top,x.bottom,x.set); if(!r2){W_('nodown');continue;}
          if(!coveredBy(r2.steps,x)){W_('miss');continue;} const cost=r1.t+r2.t; if(cost>75*60){W_('far');continue;} const rh=route(x.bottom,end); if(!rh){W_('nohome');continue;}
          if(t+cost+lunchLeft(t+cost)+rh.t>opts.finish){W_('late');continue;} W_('swiss'); }
        log.push('Day '+day.day+' stop at '+fmt(t)+': '+JSON.stringify(why));
        // time left on the way home: fill it with runs near home (Avoriaz) instead of arriving early
        if(!filling && spec.fill && t < opts.finish - 3600){ filling=true; for(const x of targetsIn(AREA[spec.fill])) if(!T.some(y=>y.name===x.name&&y.color===x.color&&y.top[0]===x.top[0])) T.push(x); continue; }
        break; }
      steps.push(...best.r1.steps, ...best.r2.steps);
      // anything else this stretch happened to ski counts as done too
      const cs=cellsOf([...best.r1.steps, ...best.r2.steps]); for(const x of T) if(!done.has(x) && coveredBy(null, x, cs)) done.add(x);
      done.add(best.x); cur=best.x.bottom; t+=best.cost; if(t>=opts.lunchAt){ if(!lunchDone){ t+=opts.lunchMin*60; lunchDone=true; } }
    }
    const rh=route(cur, end); day.homeStep=steps.length; if(rh) steps.push(...rh.steps); else log.push('Day '+day.day+': no way home!');
    day.steps=steps; retime(day);
    T.forEach(x=>{ if(done.has(x)) seenWeek.add(x.name+'|'+x.color); });
    const TM=T.filter(x=>main.has(x)); const miss=TM.filter(x=>!done.has(x));
    const byC=c=>[TM.filter(x=>x.color===c&&done.has(x)).length, TM.filter(x=>x.color===c).length];
    const swissOut = spec.swiss ? lastSwissEnd(steps, opts.start) : null;
    log.push('Day '+day.day+' '+spec.title+': '+day.km+' km, '+day.lifts+' lifts, done '+day.arrive+(swissOut?' · last Swiss step ends '+fmt(swissOut):'')+
      ' · reds '+byC('red').join('/')+' blacks '+byC('black').join('/')+' blues '+byC('blue').join('/'));
    day.missing = miss.map(x=>({n:x.name, c:x.color, L:Math.round(x.total)}));
    return day;
  }
  // ---- areas ----
  const box=(a0,a1,o0,o1)=>p=>p[0]>a0&&p[0]<a1&&p[1]>o0&&p[1]<o1;
  const AREA = {
    avoriaz: p => !swissPt(p) && box(46.150,46.212,6.738,6.83)(p),
    morzine: p => box(46.115,46.200,6.58,6.738)(p),
    crosets: p => swissPt(p) && box(46.150,46.198,6.78,6.92)(p),
    champoussin: p => swissPt(p) && box(46.198,46.262,6.80,6.92)(p),
    chatel: p => !swissPt(p) && box(46.212,46.300,6.74,6.835)(p),                       // Pré-la-Joux + Linga
    torgon: p => (swissPt(p) && box(46.262,46.340,6.78,6.92)(p)) || (!swissPt(p) && box(46.255,46.300,6.835,6.90)(p)),  // Super-Châtel + Torgon
  };
  for(const spec of opts.days){
    const day=W[spec.day-1]; Object.assign(day, spec.meta||{});
    planDay(day, Object.assign({}, spec, {area: AREA[spec.area]}));
  }
  return {log, days: W.map(d=>({day:d.day, title:d.title, km:d.km, lifts:d.lifts, arrive:d.arrive, steps:d.steps.length, missing:(d.missing||[]).length}))};
};
window.__weekJSON = v => JSON.stringify(WEEKS[v]);
