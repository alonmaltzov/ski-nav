/* ---------- games: STOPPP flask breaks, passport check, Speed King ----------
 * Every phone works out the same STOPPP times and whose round it is from the date and the group,
 * so they agree without a server. Stats (top speed, first border crossing, opt-outs) are shared
 * through the group (set_games). */
const GAMES_KEY='skinav-games';
let games = (()=>{ try{ return JSON.parse(localStorage.getItem(GAMES_KEY))||{}; }catch(e){ return {}; } })();
games.on = Object.assign({stop:true, border:true, speed:true}, games.on||{});
if(games.rounds==null) games.rounds = true;
games.fired = games.fired||{}; games.top = games.top||{}; games.swiss = games.swiss||{}; games.shown = games.shown||{};
const saveGames = () => { try{ localStorage.setItem(GAMES_KEY, JSON.stringify(games)); }catch(e){} };
const gDay = (t) => { const d=new Date(t||Date.now()); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'); };
function gHash(s){ let h=2166136261>>>0; for(let i=0;i<s.length;i++){ h^=s.charCodeAt(i); h=Math.imul(h,16777619)>>>0; } return h; }
function gRand(seed){ let a=gHash(seed); return ()=>{ a=(a+0x6D2B79F5)>>>0; let t=a; t=Math.imul(t^(t>>>15),t|1); t^=t+Math.imul(t^(t>>>7),t|61); return ((t^(t>>>14))>>>0)/4294967296; }; }
const gCode = () => (gstate && gstate.trip && gstate.trip.invite_code) || 'solo';
/* the people who take rounds: group members who haven't opted out, in a week-long shuffled order */
function gPeople(){
  const ms = gstate && gstate.members && gstate.members.length ? gstate.members : [{id:'me', name:'You', color:'#F97316', games:{rounds:games.rounds}}];
  const mine = m => m.id===(grp && grp.member_id) || m.id==='me';
  const ok = ms.filter(m => mine(m) ? games.rounds!==false : !(m.games && m.games.rounds===false));
  const list = (ok.length ? ok : ms).slice().sort((a,b)=>String(a.id).localeCompare(String(b.id)));
  const r = gRand('order:'+gCode()); for(let i=list.length-1;i>0;i--){ const j=Math.floor(r()*(i+1)); [list[i],list[j]]=[list[j],list[i]]; }
  return list.map(m=>({id:m.id, name: mine(m) ? (grp && grp.name) || m.name : m.name, color:m.color||'#F97316', me:mine(m)}));
}
/* today's 3 STOPPPs: one at a random time in each of 11:00-12:20, 12:20-13:40, 13:40-15:00 */
function stopPlan(t){
  const d=new Date(t||Date.now()), key=gDay(d), r=gRand('stop:'+gCode()+':'+key), people=gPeople();
  const T0=(CONFIG.trip&&CONFIG.trip[0]) ? new Date(CONFIG.trip[0][0],CONFIG.trip[0][1],CONFIG.trip[0][2]) : new Date(d.getFullYear(),0,1);
  const dIdx=Math.max(0, Math.round((new Date(d.getFullYear(),d.getMonth(),d.getDate()) - T0)/864e5));
  return [[660,740],[740,820],[820,900]].map(([a,b],i)=>{ const m=a+Math.floor(r()*(b-a-10)); const at=new Date(d.getFullYear(),d.getMonth(),d.getDate(),Math.floor(m/60),m%60).getTime();
    return {n:i+1, at, who:people[(dIdx*3+i) % people.length], day:key}; });
}
/* France or Switzerland (a line along the border through the ski area) */
const G_BORDER=[[46.10,6.800],[46.172,6.794],[46.190,6.807],[46.215,6.826],[46.240,6.846],[46.258,6.866],[46.275,6.874],[46.288,6.858],[46.300,6.836],[46.330,6.805]];
function gSwiss(lat, lon){ for(let i=0;i<G_BORDER.length-1;i++){ const [a0,o0]=G_BORDER[i],[a1,o1]=G_BORDER[i+1]; if(lat<=a1) return lon > o0+(o1-o0)*Math.max(0,(lat-a0)/(a1-a0)); } return lon > G_BORDER[G_BORDER.length-1][1]; }
/* share my numbers with the group (top speed, border crossing, opt-out) */
let gPostT=0, gPostPending=null;
function gPost(patch, now){
  gPostPending = Object.assign(gPostPending||{}, patch);
  if(!grp || !GB || !GB.url) return;
  if(!now && Date.now()-gPostT < 120000) return;
  const body=gPostPending; gPostPending=null; gPostT=Date.now();
  rpc('set_games',{p_secret:grp.secret, p_games:body}).catch(()=>{});
}
setInterval(()=>{ if(gPostPending) gPost({}, true); }, 150000);
/* per fix: long lift -> STOPPP; first crossing into Switzerland before noon; top speed on reds and blues */
let gLiftSince=null;
function gamesOnFix(p, good){
  if(!good || mode==='off') return;
  const fresh = Date.now()-p.t < 120000, day=gDay(p.t), d=new Date(p.t);
  if(st.onLift){ if(gLiftSince==null) gLiftSince=p.t;
    if(games.on.stop && fresh && p.t-gLiftSince >= 180000 && d.getHours() < 16){
      const due = stopPlan(p.t).filter(s=>p.t>=s.at && !(games.fired[day]||[]).includes(s.n));
      if(due.length) fireStop(due[0], true); } }
  else gLiftSince=null;
  if(games.on.border && d.getHours() < 12 && !games.swiss[day] && gSwiss(p.lat, p.lon)){
    games.swiss[day]=p.t; saveGames(); gPost({['swiss:'+day]:p.t}, true); if(fresh) showBorder(true); }
  if(!st.onLift && st.match && (st.match.color==='red' || st.match.color==='blue') && st.speed > (games.top[day]||0) && st.speed < 40){
    games.top[day]=st.speed; games.topRun=games.topRun||{}; games.topRun[day]=st.match.name; saveGames(); gPost({['top:'+day]:+st.speed.toFixed(2)}); }
}
function fireStop(s, loud){
  const day=s.day; games.fired[day]=(games.fired[day]||[]).concat([s.n]); saveGames();
  const who=s.who||{name:'Someone'}; const mine=!!who.me;
  $('stopNum').textContent='Stop number '+s.n+' of 3 today';
  $('stopWho').textContent= mine ? 'You' : who.name.split(' ')[0];
  const av=$('stopAv'); av.style.background=who.color; av.textContent=initials(who.name);
  $('stopWhere').textContent = (mine ? 'Your round: ' : who.name.split(' ')[0]+'’s round: ')+'flask out at the top'+(steps[cur] && steps[cur].type==='lift' ? ' of '+steps[cur].name : '')+'.';
  const nx=stopPlan(s.at).filter(x=>x.n>s.n).map(x=>x.who); const box=$('stopNext'); box.textContent='';
  nx.forEach(w=>{ const i=document.createElement('i'); i.className='gav sm'; i.style.background=w.color; i.textContent=initials(w.name); box.appendChild(i); });
  $('stopNextRow').hidden=!nx.length;
  $('stopSheet').hidden=false;
  if(loud){ try{ navigator.vibrate && navigator.vibrate([300,120,300,120,600]); }catch(e){}
    if(typeof speak==='function' && (!NATIVE || document.visibilityState==='visible')){ try{ speak(['STOPPP! '+(mine?'Your round.':who.name.split(' ')[0]+'’s round.')+' Flask out at the top.']); }catch(e){} } }
}
$('stopOk').onclick=()=>{ $('stopSheet').hidden=true; };
$('stopSkip').onclick=()=>{ $('stopSheet').hidden=true; games.rounds=false; saveGames(); gPost({rounds:false}, true); toast('You’re out of the rounds today. Turn it back on in Settings › Games.'); renderGames(); tellGamesNative(); };
/* who crossed into Switzerland first this morning */
function borderRank(day){
  const rows=[]; const ms = gstate && gstate.members ? gstate.members : [];
  ms.forEach(m=>{ const mine=m.id===(grp&&grp.member_id); const t = mine ? games.swiss[day] : (m.games||{})['swiss:'+day]; if(t) rows.push({name: mine ? 'You' : m.name, color:m.color, t, me:mine}); });
  if(!ms.length && games.swiss[day]) rows.push({name:'You', color:(grp&&grp.color)||'#F97316', t:games.swiss[day], me:true});
  return rows.sort((a,b)=>a.t-b.t);
}
const hhmm = t => { const d=new Date(t); return d.getHours()+':'+String(d.getMinutes()).padStart(2,'0'); };
function showBorder(fromFix){
  const day=gDay(), rows=borderRank(day); if(!rows.length) return;
  $('borderLine').textContent = (rows[0].me ? 'You were' : rows[0].name.split(' ')[0]+' was')+' first across the border at '+hhmm(rows[0].t)+'. Passports, everyone?';
  const box=$('borderList'); box.textContent='';
  rows.forEach((r,k)=>{ const d=document.createElement('div'); d.className='grank';
    d.innerHTML='<span class="gpos"></span><i class="gav"></i><div class="gnm"><b></b><small></small></div><span class="gval"></span>';
    d.querySelector('.gpos').textContent=k+1; const a=d.querySelector('.gav'); a.style.background=r.color; a.textContent=initials(r.name); if(k===0) a.classList.add('flag');
    d.querySelector('b').textContent=r.name; d.querySelector('small').textContent = k===0 ? 'First across' : '+'+Math.max(1,Math.round((r.t-rows[0].t)/60000))+' min';
    d.querySelector('.gval').textContent=hhmm(r.t); box.appendChild(d); });
  games.shown['border:'+day]=1; saveGames(); $('borderSheet').hidden=false;
  if(fromFix){ try{ navigator.vibrate && navigator.vibrate([200,100,200]); }catch(e){} }
}
$('borderOk').onclick=()=>{ $('borderSheet').hidden=true; };
/* Speed King: top speed on reds and blues today */
function speedRank(day){
  const rows=[]; const ms = gstate && gstate.members ? gstate.members : [];
  ms.forEach(m=>{ const mine=m.id===(grp&&grp.member_id); const v = mine ? games.top[day] : (m.games||{})['top:'+day]; if(v) rows.push({name: mine ? 'You' : m.name, color:m.color, v:+v, me:mine}); });
  if(!ms.length && games.top[day]) rows.push({name:'You', color:(grp&&grp.color)||'#F97316', v:games.top[day], me:true});
  return rows.sort((a,b)=>b.v-a.v);
}
function showKing(){
  const day=gDay(), rows=speedRank(day); if(!rows.length){ toast('No top speeds yet today. Ski a red or a blue.'); return; }
  const u = units==='imp' ? 'mph' : 'km/h', sp = v => Math.round(speedOut(v));
  $('kingLine').textContent = (rows[0].me ? 'You hit ' : rows[0].name.split(' ')[0]+' hit ')+sp(rows[0].v)+' '+u+(games.topRun&&rows[0].me&&games.topRun[day]?' on '+games.topRun[day]:'')+'. Top speed counts on reds and blues only.';
  const pod=$('kingPod'); pod.textContent='';
  [1,0,2].forEach(k=>{ const r=rows[k]; if(!r) return; const c=document.createElement('div'); c.className='gstep s'+(k+1);
    c.innerHTML='<i class="gav big"></i><div class="gsp"><b></b> <small></small></div><div class="gblock"><span></span></div>';
    const a=c.querySelector('.gav'); a.style.background=r.color; a.textContent=initials(r.name); if(k===0) a.classList.add('crown');
    c.querySelector('b').textContent=sp(r.v); c.querySelector('small').textContent=u; c.querySelector('.gblock span').textContent=k+1; pod.appendChild(c); });
  const last=rows.length>3 ? rows[rows.length-1] : null; $('kingSnail').hidden=!last;
  if(last){ const a=$('kingSnailAv'); a.style.background=last.color; a.textContent=initials(last.name); $('kingSnailTxt').textContent=last.name.split(' ')[0]+' · '+rows.length+'th, '+sp(last.v)+' '+u; }
  games.shown['king:'+day]=1; saveGames(); $('kingSheet').hidden=false;
}
$('kingOk').onclick=()=>{ $('kingSheet').hidden=true; };
/* badges: crown for yesterday's Speed King, red cross for today's first into Switzerland */
function gBadges(){
  const day=gDay(), y=gDay(Date.now()-864e5), out={};
  if(games.on.speed){ const k=speedRank(y)[0]; if(k) out[k.me?'me':k.name]=Object.assign(out[k.me?'me':k.name]||{}, {crown:true}); }
  if(games.on.border){ const b=borderRank(day)[0]; if(b) out[b.me?'me':b.name]=Object.assign(out[b.me?'me':b.name]||{}, {flag:true}); }
  return out;
}
function paintBadges(){
  const B=gBadges();
  if(gstate) for(const m of gstate.members){ const mk=friendMarkers.get(m.id); if(!mk) continue; const b=B[m.name]||{}, el=mk.getElement().querySelector('b');
    el.classList.toggle('crown', !!b.crown); el.classList.toggle('flag', !!b.flag); }
  if(typeof youEl!=='undefined' && youEl){ const b=B.me||{}; youEl.classList.toggle('crown', !!b.crown); youEl.classList.toggle('flag', !!b.flag); }
}
/* Settings > Games */
function renderGames(){
  const set=(id,on)=>{ const b=$(id); if(b) b.setAttribute('aria-pressed', on?'true':'false'); };
  set('gStop', games.on.stop); set('gRounds', games.rounds!==false); set('gBorder', games.on.border); set('gSpeed', games.on.speed);
  const today=stopPlan(), fired=games.fired[gDay()]||[];
  const box=$('gToday'); if(!box) return; box.textContent='';
  today.forEach(s=>{ const r=document.createElement('div'); r.className='grank';
    r.innerHTML='<span class="gpos"></span><i class="gav"></i><div class="gnm"><b></b><small></small></div><span class="gval"></span>';
    r.querySelector('.gpos').textContent=s.n; const a=r.querySelector('.gav'); a.style.background=s.who.color; a.textContent=initials(s.who.name);
    r.querySelector('b').textContent = s.who.me ? 'You' : s.who.name; r.querySelector('small').textContent = 'STOPPP '+s.n+' · between '+['11:00 and 12:20','12:20 and 1:40','1:40 and 3:00'][s.n-1];
    r.querySelector('.gval').textContent = fired.includes(s.n) ? 'Done 🥃' : ''; box.appendChild(r); });
  const k=speedRank(gDay()); $('gKingNow').textContent = k.length ? 'Fastest today: '+(k[0].me?'you':k[0].name.split(' ')[0])+', '+Math.round(speedOut(k[0].v))+(units==='imp'?' mph':' km/h') : 'No top speeds yet today';
}
$('gamesBtn').onclick=()=>{ renderGames(); $('gamesSheet').hidden=false; };
$('gamesDone').onclick=()=>{ $('gamesSheet').hidden=true; };
$('gKingShow').onclick=()=>{ $('gamesSheet').hidden=true; showKing(); };
$('gStop').onclick=()=>{ games.on.stop=!games.on.stop; saveGames(); renderGames(); tellGamesNative(); };
$('gRounds').onclick=()=>{ games.rounds = games.rounds===false; saveGames(); gPost({rounds:games.rounds}, true); renderGames(); tellGamesNative(); };
$('gBorder').onclick=()=>{ games.on.border=!games.on.border; saveGames(); renderGames(); tellGamesNative(); paintBadges(); };
$('gSpeed').onclick=()=>{ games.on.speed=!games.on.speed; saveGames(); renderGames(); paintBadges(); };
/* the native apps watch for the long lift and the border while the phone is locked */
let gNativeSent='';
function tellGamesNative(){
  if(!NATIVE) return;
  const msg={cmd:'games', on:{stop:!!games.on.stop, border:!!games.on.border}, stops: stopPlan().map(s=>({n:s.n, at:s.at, who: s.who.me ? 'Your' : s.who.name.split(' ')[0]+'’s'})), border:G_BORDER, day:gDay()};
  const k=JSON.stringify(msg); if(k===gNativeSent) return; gNativeSent=k; toNative(msg);
}
/* after the day: Speed King at La Folie Douce (from 4:30 pm, once a day) */
function gamesTick(){
  const now=new Date(), day=gDay();
  tellGamesNative(); paintBadges();
  if(games.on.speed && now.getHours()*60+now.getMinutes() >= 990 && now.getHours() < 21 && !games.shown['king:'+day] && speedRank(day).length && document.visibilityState==='visible' && $('stopSheet').hidden) showKing();
  if(games.on.border && !games.shown['border:'+day] && borderRank(day).length && document.visibilityState==='visible') showBorder(false);
}
setInterval(gamesTick, 30000); setTimeout(gamesTick, 3000);
document.addEventListener('visibilitychange', ()=>{ if(document.visibilityState==='visible') setTimeout(gamesTick, 1500); });
/* a STOPPP the native app already fired while the phone was locked */
function gamesNativeEvent(name){
  const m=/^stop:(\d+)$/.exec(name); if(m){ const s=stopPlan().find(x=>x.n===+m[1]); if(s && !(games.fired[s.day]||[]).includes(s.n)) fireStop(s, false); return true; }
  return false;
}
