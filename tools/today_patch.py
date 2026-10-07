"""Lift status (Intermaps), weather + what to wear (Open-Meteo), Plan from here (on-device router). Applied to index.html and nyc.html."""
import sys, json, re, unicodedata

def liftmap(html, intermaps_json):
    s = open(html).read(); i = s.index('const BG = ') + len('const BG = '); BG = json.loads(s[i:s.index('\n', i)].rstrip().rstrip(';'))
    im = json.load(open(intermaps_json))['lifts']
    def norm(x):
        x = unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode().lower()
        x = re.sub(r"\b((tsd|tsf|ts|td|tc|tk|tph|tb|tm|ttc|tlc|tpv)\d*|tapis|telesiege|telecabine|teleski|telepherique|chairlift|gondola|express|du|de|la|le|les|des|d|l)\b", ' ', x)
        return re.sub(r'[^a-z0-9]+', ' ', x).strip()
    by = {}
    for l in im: by.setdefault(norm(l['popup']['title']), []).append(str(l['popup']['oid']))
    out = {}
    for bi, b in enumerate(BG):
        if b[0] != 'L' or not b[2]: continue
        n = {'Morgins – Foilleuse': 'foilleuse'}.get(b[2]) or norm(b[2])
        if not n: continue
        m = by.get(n)
        if not m:
            cand = [k for k in by if k and (set(n.split()) <= set(k.split()) or set(k.split()) <= set(n.split()))]
            if len(cand) == 1: m = by[cand[0]]
        if m: out[bi] = m
    return out

HTML_PILLS = '''    <div class="toppills" id="topPills">
      <button class="tpill" id="wxPill" type="button" aria-label="Weather and what to wear"><span id="wxPillTxt">Weather</span></button>
      <button class="tpill" id="liftsPill" type="button" aria-label="Lift status"><i class="ldot" id="liftsDot"></i><span id="liftsPillTxt">Lifts</span></button>
    </div>
'''
HTML_SHEET = '''<div class="sheet" id="todaySheet" hidden>
  <div class="sheetin" role="dialog" aria-label="Today">
    <div class="sheethead"><h3>Today</h3><button class="btn ghost sm" id="closeToday" type="button">Done</button></div>
    <div class="tcard" id="wxCard">
      <div class="wxtop"><b id="wxTemp">--</b><div><span id="wxCond">Loading weather…</span><small id="wxRange"></small></div></div>
      <div class="wxrow" id="wxRow"></div>
    </div>
    <div class="tcard">
      <span class="eyebrow">What to wear</span>
      <ul class="wear" id="wearList"></ul>
    </div>
    <div class="tcard" id="liftCard">
      <div class="lhead"><span class="eyebrow">Lifts</span><small id="liftsUpdated"></small></div>
      <b class="lbig" id="liftsBig">--</b>
      <p class="note" id="liftsNote" style="margin:0"></p>
      <div class="lrows" id="liftRows"></div>
    </div>
    <button class="btn ghost" id="todayRefresh" type="button">Refresh</button>
  </div>
</div>

<div class="sheet" id="sheet" hidden>'''

CSS = r"""
/* ===== today: weather + lift pills, Today sheet, Plan from here ===== */
.toppills{position:absolute;left:74px;right:74px;top:12px;z-index:500;display:flex;gap:8px}
.app:not(.tracking) .toppills{top:calc(12px + env(safe-area-inset-top,0px))}
.app.tracking .toppills,.mapwrap:has(#placesBox:not([hidden])) .toppills{display:none}
.tpill{flex:0 1 auto;min-width:0;height:50px;border-radius:25px;border:1px solid var(--line);background:var(--panel);color:var(--ink);font:600 .95rem var(--f-ui);display:flex;align-items:center;justify-content:center;gap:7px;padding:0 10px;box-shadow:0 3px 12px rgb(11 22 32/.16);white-space:nowrap;overflow:hidden}
.tpill span{overflow:hidden;text-overflow:ellipsis}
.ldot{width:10px;height:10px;border-radius:5px;background:var(--muted);flex:none}
.ldot.ok{background:var(--ok)} .ldot.part{background:var(--warn)} .ldot.off{background:var(--muted)}
.tcard{background:var(--bg);border-radius:16px;padding:14px;display:grid;gap:8px}
.wxtop{display:flex;align-items:center;gap:14px}
.wxtop b{font:800 2.6rem/1 var(--f-num)}
.wxtop span{display:block;font-weight:700;font-size:1.1rem}
.wxtop small{display:block;color:var(--muted);font-size:.95rem}
.wxrow{display:flex;flex-wrap:wrap;gap:6px 14px;color:var(--muted);font-size:.95rem}
.wear{margin:0;padding-left:20px;display:grid;gap:4px;font-size:1rem}
.lhead{display:flex;justify-content:space-between;align-items:baseline}
.lhead small{color:var(--muted)}
.lbig{font:800 1.5rem/1.1 var(--f-num)}
.lrows{display:grid;gap:6px}
.lrow{display:flex;justify-content:space-between;gap:10px;font-size:1rem}
.lrow span:last-child{font-weight:700;white-space:nowrap}
.lrow .open{color:var(--ok)} .lrow .closed{color:var(--bad)} .lrow .soon{color:var(--warn)}
.srow .closedtag{color:var(--bad);font-weight:700}
.toast{position:fixed;left:74px;right:74px;top:calc(72px + env(safe-area-inset-top,0px));pointer-events:none;z-index:1200;background:var(--ink);color:var(--panel);border-radius:14px;padding:12px 14px;font:600 1rem/1.3 var(--f-ui);box-shadow:0 6px 24px rgb(0 0 0/.25)}
.app:not(.tracking) #replanBtn{display:none}
.app.tracking #replanBtn{font-size:.95rem;padding:0 8px;line-height:1.15}
.tpill{font-size:.9rem;padding:0 12px}
.app.tracking #progBtn{display:none}
.sheethead .hb{display:flex;gap:8px}
"""

JS = r"""
/* ---------- lift status (Intermaps feed behind the official Portes du Soleil map) ---------- */
const LIFT_FEED = CONFIG.liftFeed || null;
let liftStat = store.lifts || null;   // {t, last, by:{oid:status}, open, total}
function liftStatusOf(bi){
  if(!liftStat || !LIFTMAP[bi]) return null;
  const ss = LIFTMAP[bi].map(o=>liftStat.by[o]).filter(Boolean);
  if(!ss.length) return null;
  return ss.includes('open') ? 'open' : ss.includes('in_preparation') ? 'soon' : 'closed';
}
/* only route around closures while the resort is actually running (not before the season) */
function resortRunning(){ return !!(liftStat && liftStat.total && liftStat.open/liftStat.total >= 0.2 && Date.now()-liftStat.t < 3*3600e3); }
function liftClosed(bi){ return resortRunning() && liftStatusOf(bi) && liftStatusOf(bi)!=='open'; }
function stepLiftBi(s){
  if(s.type!=='lift' || !s.coords || !s.coords.length) return -1;
  if(s._bi!=null) return s._bi;
  const a=s.coords[0], z=s.coords[s.coords.length-1]; let best=-1, bd=1e9;
  BG.forEach((b,bi)=>{ if(b[0]!=='L') return; const c=b[3]; const d=hav(a,c[0])+hav(z,c[c.length-1]); if(d<bd){ bd=d; best=bi; } });
  return (s._bi = bd < 150 ? best : -1);
}
async function fetchLifts(force){
  if(!LIFT_FEED) return;
  if(!force && liftStat && Date.now()-liftStat.t < 30*60e3) return;
  try{
    const r = await fetch(LIFT_FEED, {cache:'no-store'}); const d = await r.json();
    const by={}; let open=0;
    for(const l of d.lifts||[]){ const p=l.popup||{}; by[String(p.oid)] = p.status || l.status; if((p.status||l.status)==='open') open++; }
    liftStat = {t:Date.now(), last:d.lastUpdate||'', by, open, total:(d.lifts||[]).length};
    store.lifts = liftStat; persist(); renderLifts(); renderStep();
  }catch(e){ console.warn('lift status unavailable', e && e.message); renderLifts(); }
}
function planLifts(){ return steps.filter(s=>s.type==='lift').map(s=>({s, bi:stepLiftBi(s)})).filter((x,i,a)=>a.findIndex(y=>y.bi===x.bi)===i); }
function renderLifts(){
  if(!LIFT_FEED){ $('liftsPill').hidden=true; $('liftCard').hidden=true; return; }
  const dot=$('liftsDot'); dot.className='ldot';
  if(!liftStat){ $('liftsPillTxt').textContent='Lifts'; $('liftsBig').textContent='No lift data yet'; $('liftsNote').textContent='Needs a connection. Checks every 30 minutes.'; $('liftRows').textContent=''; return; }
  const running=resortRunning(), off = liftStat.open/Math.max(1,liftStat.total) < 0.2;
  const pl = planLifts(), closed = pl.filter(x=>liftStatusOf(x.bi) && liftStatusOf(x.bi)!=='open');
  if(off){ dot.classList.add('off'); $('liftsPillTxt').textContent='Lifts closed'; }
  else if(closed.length){ dot.classList.add('part'); $('liftsPillTxt').textContent=closed.length+' plan lift'+(closed.length>1?'s':'')+' closed'; }
  else { dot.classList.add('ok'); $('liftsPillTxt').textContent='Lifts open'; }
  $('liftsBig').textContent = liftStat.open+' of '+liftStat.total+' lifts open';
  const when = new Date(liftStat.t); $('liftsUpdated').textContent='checked '+when.getHours()+':'+String(when.getMinutes()).padStart(2,'0');
  $('liftsNote').textContent = off ? 'The ski area is not running yet (season starts in December). Closures will show here and Plan from here will avoid them.' : (closed.length ? 'Some lifts in today’s plan are closed. Use Plan from here to go around them.' : 'Every lift in today’s plan is open.');
  const box=$('liftRows'); box.textContent='';
  for(const x of pl){ const st_=liftStatusOf(x.bi); const row=document.createElement('div'); row.className='lrow';
    const a=document.createElement('span'); a.textContent=x.s.name; const b=document.createElement('span');
    b.textContent = !st_ ? 'no data' : st_==='open' ? 'Open' : st_==='soon' ? 'Opening soon' : 'Closed'; b.className = st_==='open'?'open':st_==='soon'?'soon':st_?'closed':'';
    row.append(a,b); box.appendChild(row); }
}

/* ---------- weather + what to wear (Open-Meteo, no key) ---------- */
const WX_CODES = {0:'Clear',1:'Mostly clear',2:'Partly cloudy',3:'Cloudy',45:'Fog',48:'Freezing fog',51:'Light drizzle',53:'Drizzle',55:'Heavy drizzle',56:'Freezing drizzle',57:'Freezing drizzle',61:'Light rain',63:'Rain',65:'Heavy rain',66:'Freezing rain',67:'Freezing rain',71:'Light snow',73:'Snow',75:'Heavy snow',77:'Snow grains',80:'Showers',81:'Showers',82:'Heavy showers',85:'Snow showers',86:'Heavy snow showers',95:'Thunderstorm',96:'Thunderstorm',99:'Thunderstorm'};
let wx = store.wx || null;
async function fetchWx(force){
  const W = CONFIG.wx; if(!W) return;
  if(!force && wx && Date.now()-wx.t < 60*60e3) return;
  const u='https://api.open-meteo.com/v1/forecast?latitude='+W.lat+'&longitude='+W.lon+(W.elev?'&elevation='+W.elev:'')+
    '&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_min,weather_code,snowfall_sum,wind_speed_10m_max,wind_gusts_10m_max,uv_index_max&timezone=auto&forecast_days=1';
  try{ const d=await (await fetch(u,{cache:'no-store'})).json(); if(!d.current) throw new Error(d.reason||'no data');
    wx={t:Date.now(), now:d.current, day:Object.fromEntries(Object.entries(d.daily||{}).map(([k,v])=>[k,Array.isArray(v)?v[0]:v]))}; store.wx=wx; persist(); }
  catch(e){ console.warn('weather unavailable', e && e.message); }
  renderWx();
}
const tUnit = c => units==='imp' ? Math.round(c*9/5+32)+'°F' : Math.round(c)+'°';
const wUnit = k => units==='imp' ? Math.round(k*0.6214)+' mph' : Math.round(k)+' km/h';
function wearFor(w){
  const a = w.day.apparent_temperature_min ?? w.now.apparent_temperature, wind = w.day.wind_gusts_10m_max ?? w.day.wind_speed_10m_max ?? 0, snow = w.day.snowfall_sum || 0, code = w.day.weather_code ?? w.now.weather_code, uv = w.day.uv_index_max || 0;
  const L=[];
  if(a <= -15){ L.push('Thermal base layer, fleece and a puffy under your shell'); L.push('Mittens, neck gaiter, hand warmers'); }
  else if(a <= -7){ L.push('Base layer, fleece and your shell'); L.push('Warm gloves and a neck gaiter'); }
  else if(a <= 0){ L.push('Base layer, light fleece and your shell'); L.push('Gloves and a buff'); }
  else { L.push('Base layer and shell, open the vents'); L.push('Light gloves'); }
  if(snow >= 1 || [45,48,71,73,75,77,85,86].includes(code)) L.push('Low-light goggle lens, it will be flat light');
  else if(code <= 1){ L.push('Dark goggle lens'); }
  if(uv >= 3 || code <= 1) L.push('Sunscreen and lip balm');
  if(wind >= 40) L.push('Windy up top ('+wUnit(wind)+' gusts): hood under the helmet, cover your face. Exposed lifts may close.');
  return L;
}
function renderWx(){
  if(!CONFIG.wx){ $('wxPill').hidden=true; return; }
  if(!wx){ $('wxPillTxt').textContent='Weather'; $('wxCond').textContent='No weather yet (needs a connection)'; return; }
  const n=wx.now, d=wx.day, cond=WX_CODES[n.weather_code]||'';
  $('wxPillTxt').textContent = tUnit(n.temperature_2m)+' '+(cond.split(' ').pop()||'').toLowerCase();
  $('wxTemp').textContent = tUnit(n.temperature_2m); $('wxCond').textContent = cond + (CONFIG.wx.label?' · '+CONFIG.wx.label:'');
  $('wxRange').textContent = 'High '+tUnit(d.temperature_2m_max)+' · low '+tUnit(d.temperature_2m_min)+' · feels like '+tUnit(n.apparent_temperature);
  const row=$('wxRow'); row.textContent='';
  [['Wind', wUnit(n.wind_speed_10m)+(d.wind_gusts_10m_max?' (gusts '+wUnit(d.wind_gusts_10m_max)+')':'')], ['New snow', (d.snowfall_sum||0)>0 ? (units==='imp'?(d.snowfall_sum/2.54).toFixed(1)+' in':Math.round(d.snowfall_sum)+' cm') : 'none'], ['UV', Math.round(d.uv_index_max||0)]]
    .forEach(([k,v])=>{ const s=document.createElement('span'); s.textContent=k+': '+v; row.appendChild(s); });
  const ul=$('wearList'); ul.textContent=''; wearFor(wx).forEach(t=>{ const li=document.createElement('li'); li.textContent=t; ul.appendChild(li); });
}
function openToday(){ renderWx(); renderLifts(); $('todaySheet').hidden=false; fetchWx(false); fetchLifts(false); }
$('wxPill').onclick=openToday; $('liftsPill').onclick=openToday;
$('closeToday').onclick=()=>{ $('todaySheet').hidden=true; };
$('todaySheet').onclick=e=>{ if(e.target.id==='todaySheet') $('todaySheet').hidden=true; };
$('todayRefresh').onclick=()=>{ fetchWx(true); fetchLifts(true); };
/* 9am onwards, every 30 minutes while the app is open */
setInterval(()=>{ if(document.visibilityState!=='visible') return; const h=new Date().getHours(); if(h>=8 && h<18) fetchLifts(false); fetchWx(false); }, 5*60e3);
renderWx(); renderLifts(); fetchWx(false); fetchLifts(false);

/* ---------- Plan from here: route from where you are back into the plan, on the phone ---------- */
const DCOL={nov:'green',eas:'blue',int:'red',adv:'black',exp:'black'};
const isDragLift = b => b[0]==='L' && !['cha','gon','cab','mix','fun'].includes(b[1]);
let RG=null;
function buildGraph(){
  const flat=!!CONFIG.flat, runV=flat?1.4:8, walkV=flat?1.4:1.1;
  const vLat=[], vLon=[], vLine=[], vIdx=[], start=[];
  BG.forEach((b,li)=>{ start[li]=vLat.length; for(let j=0;j<b[3].length;j++){ vLat.push(b[3][j][0]); vLon.push(b[3][j][1]); vLine.push(li); vIdx.push(j); } });
  const N=vLat.length, adj=Array.from({length:N},()=>[]);
  BG.forEach((b,li)=>{ const c=b[3], s=start[li];
    if(b[0]==='R'){ for(let j=0;j<c.length-1;j++){ const t=hav(c[j],c[j+1])/runV; adj[s+j].push([s+j+1,t,'r',li]); if(flat) adj[s+j+1].push([s+j,t,'r',li]); } }
    else if(b[0]==='L'){ let len=0; for(let j=0;j<c.length-1;j++) len+=hav(c[j],c[j+1]); adj[s].push([s+c.length-1,(flat?120:240)+len/(flat?5:4.5),'l',li]); }
  });
  const key=(a,o)=>Math.floor(a*1500)+':'+Math.floor(o*1100), G={};
  const isEnd=v=>vIdx[v]===0 || vIdx[v]===BG[vLine[v]][3].length-1;
  const usable=v=>BG[vLine[v]][0]==='R' || isEnd(v);
  for(let v=0;v<N;v++) if(usable(v)) (G[key(vLat[v],vLon[v])]=G[key(vLat[v],vLon[v])]||[]).push(v);
  for(const k in G){ const [a,o]=k.split(':').map(Number);
    for(const v of G[k]) for(let da=-1;da<=1;da++) for(let db=-1;db<=1;db++){ const cell=G[(a+da)+':'+(o+db)]; if(!cell) continue;
      for(const u of cell){ if(vLine[u]===vLine[v]) continue; const d=hav([vLat[v],vLon[v]],[vLat[u],vLon[u]]);
        if(d <= ((isEnd(v)||isEnd(u)) ? 35 : 12)) adj[v].push([u, 6+d/walkV, 'w', -1]); } } }
  return {vLat,vLon,vLine,vIdx,adj,N,G,key,usable,walkV};
}
function near(pt, maxM, ok){
  const g=RG, out=[], a=Math.floor(pt[0]*1500), o=Math.floor(pt[1]*1100), r=Math.ceil(maxM/70)+1;
  for(let da=-r;da<=r;da++) for(let db=-r;db<=r;db++){ const cell=g.G[(a+da)+':'+(o+db)]; if(!cell) continue;
    for(const v of cell){ if(ok && !ok(v)) continue; const d=hav(pt,[g.vLat[v],g.vLon[v]]); if(d<=maxM) out.push([v,d]); } }
  return out;
}
function dijkstra(sources){
  const g=RG, dist=new Float64Array(g.N).fill(Infinity), prev=new Int32Array(g.N).fill(-1), pe=new Array(g.N);
  const H=[]; const push=(d,v)=>{ H.push([d,v]); let i=H.length-1; while(i>0){ const p=(i-1)>>1; if(H[p][0]<=H[i][0]) break; [H[p],H[i]]=[H[i],H[p]]; i=p; } };
  const pop=()=>{ const top=H[0], last=H.pop(); if(H.length){ H[0]=last; let i=0; for(;;){ const l=2*i+1, r=l+1; let m=i; if(l<H.length && H[l][0]<H[m][0]) m=l; if(r<H.length && H[r][0]<H[m][0]) m=r; if(m===i) break; [H[m],H[i]]=[H[i],H[m]]; i=m; } } return top; };
  for(const [v,c] of sources){ if(c<dist[v]){ dist[v]=c; pe[v]=['start']; push(c,v); } }
  while(H.length){ const [d,v]=pop(); if(d>dist[v]) continue;
    for(const e of g.adj[v]){ let c=e[1];
      if(e[2]==='l'){ const b=BG[e[3]]; if(liftClosed(e[3])) continue; if(isDragLift(b)) c+=1800; }
      const nd=d+c; if(nd<dist[e[0]]){ dist[e[0]]=nd; prev[e[0]]=v; pe[e[0]]=e; push(nd,e[0]); } } }
  return {dist,prev,pe};
}
const LIFT_WORD = {cha:'chair', gon:'gondola', cab:'cable car', mix:'gondola', fun:'funicular'};
function liftLabel(b){ const n=b[2]||'Lift'; if(CONFIG.flat || /chair|gondola|bus|tram|lift|t-bar|télé/i.test(n)) return n; return n+' '+(LIFT_WORD[b[1]]||'T-bar'); }
function pathSteps(D, v, from){
  const edges=[]; while(D.prev[v]>=0){ edges.push([D.prev[v], v, D.pe[v]]); v=D.prev[v]; } edges.reverse();
  const g=RG, pt=x=>[g.vLat[x],g.vLon[x]], out=[]; let run=null;
  const newRun=()=>({type:'run', name:'', legs:[], segs:[], color:'blue', traverse:false, coords:[], len:0, top:null, bottom:null, way:{min:15,via:[],by:'23:59'}});
  const close=()=>{ if(run && run.len>25){ out.push(run); } run=null; };
  const first = edges.length ? edges[0][0] : v;
  run=newRun(); run.coords.push([from[0],from[1],null]); run.coords.push([g.vLat[first],g.vLon[first],null]); run.len=hav(from,pt(first)); run.segs.push({color:'blue',c:[[from[0],from[1]],pt(first)]});
  for(const [a,b,e] of edges){
    if(e[2]==='l'){ close(); const B=BG[e[3]], c=B[3]; let len=0; for(let j=0;j<c.length-1;j++) len+=hav(c[j],c[j+1]);
      out.push({type:'lift', name:liftLabel(B), drag:isDragLift(B), len:Math.round(len), bottom:null, top:null, coords:c.map(p=>[p[0],p[1],null]), way:{min:15,via:[],by:'23:59'}, _bi:e[3]}); continue; }
    if(!run){ run=newRun(); run.coords.push([g.vLat[a],g.vLon[a],null]); }
    const A=pt(a), Bp=pt(b), d=hav(A,Bp); run.coords.push([Bp[0],Bp[1],null]); run.len+=d;
    const col = e[2]==='r' ? (DCOL[BG[e[3]][1]]||'blue') : null;
    if(e[2]==='r' && BG[e[3]][2]){ const nm=BG[e[3]][2]; let leg=run.legs[run.legs.length-1]; if(!leg || leg.name!==nm){ leg={name:nm,color:col,len:0}; run.legs.push(leg); } leg.len+=d; }
    let sg=run.segs[run.segs.length-1]; const sc = col || (sg ? sg.color : 'blue');
    if(!sg || sg.color!==sc){ sg={color:sc, c:[A]}; run.segs.push(sg); } sg.c.push(Bp);
  }
  close();
  const rank=['green','blue','red','black'];
  for(const s of out) if(s.type==='run'){
    s.len=Math.round(s.len); s.legs=s.legs.filter(l=>l.len>60).map(l=>({...l,len:Math.round(l.len)}));
    if(s.legs.length){ s.color=s.legs.reduce((m,l)=>rank.indexOf(l.color)>rank.indexOf(m)?l.color:m,'green'); s.name=s.legs[0].name; }
    else { s.traverse=true; s.name='Traverse'; }
  }
  return out;
}
function myPos(){ if(st.last) return [st.last.lat, st.last.lon]; if(located) return [located.lat, located.lon]; return null; }
let toastT=0;
function toast(msg){ let t=$('toast'); if(!t){ t=document.createElement('div'); t.id='toast'; t.className='toast'; t.setAttribute('role','status'); document.body.appendChild(t); } t.textContent=msg; t.hidden=false; clearTimeout(toastT); toastT=setTimeout(()=>{ t.hidden=true; }, 5000); }
function planFromHere(){
  const p = myPos();
  if(!p){ toast('Finding you first…'); locateMe(); setTimeout(()=>{ if(myPos()) planFromHere(); else toast('No location yet. Try again in a moment.'); }, 4000); return null; }
  if(!RG) RG=buildGraph();
  const src = near(p, 150, v=>BG[RG.vLine[v]][0]==='R' || RG.vIdx[v]===0).map(([v,d])=>[v, 10+d/RG.walkV]);
  if(!src.length){ toast('You are too far from the runs to plan a route. Get onto a run or near a lift first.'); return null; }
  const D = dijkstra(src);
  let best=null;
  for(let k=cur; k<steps.length; k++){
    const s=steps[k];
    if(s.type==='lift' && liftClosed(stepLiftBi(s))) continue;
    const tgt = s.type==='end' ? s.coords[0] : s.coords[0];
    const cands = near(tgt, s.type==='end'?80:40, v=> s.type==='lift' ? (BG[RG.vLine[v]][0]==='L' && RG.vIdx[v]===0) : RG.usable(v));
    for(const [v] of cands){ const c=D.dist[v]; if(!isFinite(c)) continue; const score=c + 240*(k-cur); if(!best || score<best.score) best={k,v,c,score}; }
  }
  if(!best){ toast('No way back into the plan from here. Free ski, or head to '+DAY.end.name+'.'); return null; }
  const routed = pathSteps(D, best.v, p);
  const now = new Date(), t0 = now.getHours()*60+now.getMinutes();
  let t=t0; const rest = steps.slice(best.k).map(s=>({...s}));
  routed.forEach(s=>{ s.at=fmtHM(Math.round(t)%1440); t += (s.type==='lift' ? 4+s.len/270 : s.len/(CONFIG.flat?84:300)); });
  const shift = rest.length && rest[0].at ? Math.round(t) - hm(rest[0].at) : 0;
  rest.forEach(s=>{ if(s.at) s.at=fmtHM(((hm(s.at)+shift)%1440+1440)%1440); });
  const done = steps.slice(0,cur);
  applySteps(done.concat(routed, rest), cur);
  const target = steps[cur+routed.length];
  toast(routed.length ? 'New route: '+routed.length+' step'+(routed.length>1?'s':'')+' to '+(target ? stepLabel(target).replace(/^(Ski|Take) /,'') : DAY.end.name)+'.' : 'You are already on the plan.');
  return {routed:routed.length, rejoin:best.k, minutes:Math.round(best.c/60)};
}
function applySteps(list, at){
  steps = list.map((s,k)=>({...s, i:k}));
  if(steps[steps.length-1].type!=='end') steps.push({type:'end', name:DAY.end.name, coords:[[DAY.end.lat,DAY.end.lon,null]], len:0, i:steps.length, at:DAY.arrive});
  cur = Math.min(at, steps.length-1); st.stepDist=0;
  const k=dayKey(DAY.day); store.days[k]=store.days[k]||{}; store.days[k].steps = steps.filter(s=>s.type!=='end').map(({i,_bi,...s})=>s);
  persist(); buildMarkers(); drawRoute(); renderStep(); nativeStepKey=null; nativeStep(); sendPlanToWatch(); renderLifts();
}
function resetPlan(){ const k=dayKey(DAY.day); if(store.days[k]) delete store.days[k].steps; const c=cur; loadDayKeep(); toast('Back to the original plan.'); }
function loadDayKeep(){ const c=cur, keep={dist:st.dist,vert:st.vert,max:st.max,elapsed:st.elapsed,trail:st.trail}; loadDay(di); Object.assign(st,keep); cur=Math.min(c,steps.length-1); persist(); buildMarkers(); drawRoute(); renderStep(); nativeStepKey=null; nativeStep(); sendPlanToWatch(); }
$('replanBtn').onclick=()=>planFromHere();
$('replan2').onclick=()=>{ $('sheet').hidden=true; planFromHere(); };
$('unplanBtn').onclick=()=>{ $('sheet').hidden=true; resetPlan(); };
"""

def patch(path, liftmap_obj, cfg_extra):
    s = open(path).read()
    def rep(old, new, count=1):
        nonlocal s
        n = s.count(old)
        if n != count: sys.exit(f'{path}: expected {count} of {old[:90]!r}, found {n}')
        s = s.replace(old, new)
    # data: LIFTMAP after BG, CONFIG extras
    i = s.index('const BG = '); j = s.index('\n', i)
    s = s[:j+1] + 'const LIFTMAP = ' + json.dumps(liftmap_obj, separators=(',', ':')) + ';\n' + s[j+1:]
    ci = s.index('const CONFIG = ') + len('const CONFIG = '); cj = s.index('\n', ci)
    C = json.loads(s[ci:cj].rstrip().rstrip(';')); C.update(cfg_extra)
    s = s[:ci] + json.dumps(C, ensure_ascii=False) + ';' + s[cj:]
    # pills on the map, Today sheet, buttons
    rep('    <div class="placesbox" id="placesBox" hidden>', HTML_PILLS + '    <div class="placesbox" id="placesBox" hidden>')
    rep('<div class="sheet" id="sheet" hidden>', HTML_SHEET)
    rep('      <button class="btn ghost" id="progBtn" type="button">Runs</button>', '      <button class="btn ghost" id="progBtn" type="button">Runs</button>\n      <button class="btn ghost" id="replanBtn" type="button">Plan from here</button>')
    rep('<div class="sheethead"><h3 id="sheetTitle">Day 1</h3><button class="btn ghost sm" id="closeSheet" type="button">Done</button></div>',
        '<div class="sheethead"><h3 id="sheetTitle">Day 1</h3><div class="hb"><button class="btn ghost sm" id="unplanBtn" type="button" hidden>Original plan</button><button class="btn ghost sm" id="replan2" type="button">Plan from here</button><button class="btn ghost sm" id="closeSheet" type="button">Done</button></div></div>')
    i = s.index('/* ===== redesign: map-first home'); s = s[:i] + CSS + s[i:]
    # persist keeps extra per-day fields (start-of-day runs, a re-planned route)
    rep("store.days[dayKey(WEEK[di].day)]={cur, dist:st.dist, vert:st.vert, max:st.max, elapsed:st.elapsed, trail:st.trail};",
        "store.days[dayKey(WEEK[di].day)]=Object.assign(store.days[dayKey(WEEK[di].day)]||{}, {cur, dist:st.dist, vert:st.vert, max:st.max, elapsed:st.elapsed, trail:st.trail});")
    # a re-planned day loads its own steps
    rep("  steps = DAY.steps.map((s,k)=>({...s, i:k}));\n  steps.push(",
        "  const sd0 = store.days[dayKey(DAY.day)] || {};\n  steps = (Array.isArray(sd0.steps) && sd0.steps.length ? sd0.steps : DAY.steps).map((s,k)=>({...s, i:k}));\n  steps.push(")
    # steps list: show the Original plan button when re-planned; mark closed lifts
    rep("function renderList(){", "function renderList(){\n  { const sd=store.days[dayKey(DAY.day)]||{}; $('unplanBtn').hidden = !(Array.isArray(sd.steps) && sd.steps.length); }")
    rep("  let meta = stepMeta(s);", "  let meta = stepMeta(s);\n  if(s.type==='lift' && typeof liftClosed==='function' && liftClosed(stepLiftBi(s))) meta = 'Closed right now · tap Plan from here · ' + meta;")
    rep("/* expose for automated tests */", JS + "\n/* expose for automated tests */")
    rep("recap:openRecap, setSun };", "recap:openRecap, setSun, planFromHere, applySteps, get liftStat(){return liftStat;}, set liftStat(v){liftStat=v;}, renderLifts, wearFor, resetPlan, setWx(v){ wx=v; renderWx(); } };")
    open(path, 'w').write(s); print('patched', path)

if __name__ == '__main__':
    im = sys.argv[1]
    patch('index.html', liftmap('index.html', im), {"liftFeed": "https://winter.intermaps.com/portes_du_soleil/data?lang=en", "wx": {"lat": 46.1915, "lon": 6.7745, "elev": 1800, "label": "Avoriaz 1,800 m"}})
    patch('nyc.html', {}, {"wx": {"lat": 40.7812, "lon": -73.9533, "label": "Upper East Side"}})
