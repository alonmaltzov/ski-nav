"""Demo crew: see the full group experience before the friends join.
Avsha (purple, Android), Kelner (green, Android) and Yuval (red, iPhone) ski along today's route next to you (Alon, yellow).
They show on the map, in the crew sheet, the passport list (Avsha already checked), STOPPP rounds and Speed King.
Local only: nothing is sent to the real group; with a real group they're added on your phone only."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80]); s = s.replace(old, new)

# the switch, in Test mode
rep('      <button type="button" id="simDrift">Simulate going off route</button>\n    </div>',
    '      <button type="button" id="simDrift">Simulate going off route</button>\n    </div>\n'
    '    <button class="grow toggle" id="demoCrew" type="button" role="switch" aria-pressed="false" style="margin-top:10px"><span>Demo crew<small>Avsha, Kelner and Yuval ski today\'s route with you. Only on this phone.</small></span><span class="sw"></span></button>')

# the demo group never touches the server
rep("async function rpc(fn, args){\n",
    "async function rpc(fn, args){\n"
    "  if(args && args.p_secret==='demo') return fn==='trip_state' ? demoState() : {};\n")
rep("const saveGrp = () => {", "const saveGrp = () => { if(grp && grp.demo) return;")
rep("function tellNative(){ if(NATIVE) toNative({cmd:'group', url:GB&&GB.url||'', key:GB&&GB.key||'', secret: grp ? grp.secret : '',",
    "function tellNative(){ if(NATIVE) toNative({cmd:'group', url:GB&&GB.url||'', key:GB&&GB.key||'', secret: grp && !grp.demo ? grp.secret : '',")
# with a real group, the demo friends are added on this phone
rep("  try{ gstate=await rpc('trip_state',{p_secret:grp.secret}); grp.role=gstate.role; saveGrp();",
    "  try{ gstate=await rpc('trip_state',{p_secret:grp.secret}); grp.role=gstate.role; saveGrp(); if(!grp.demo && store.demoCrew) addDemo(gstate);")

DEMO = r'''
/* ---------- demo crew (Test mode): the full group experience before the friends join ---------- */
const DEMO_CREW=[{id:'demo-avsha', name:'Avsha', color:'#7C3AED', platform:'android', lag:0.06, pass:true, top:19.4},
                 {id:'demo-kelner', name:'Kelner', color:'#16A34A', platform:'android', lag:0.17, pass:false, top:18.1},
                 {id:'demo-yuval', name:'Yuval', color:'#DC2626', platform:'ios', lag:0.31, pass:false, top:20.6}];
function demoTrack(){ const pts=[]; (steps||[]).forEach(s=>{ if(s.type==='end') return; (s.coords||[]).forEach(c=>pts.push({c, s})); }); return pts; }
function demoMembers(){
  const pts=demoTrack(), n=pts.length, k=gDay(), t=Date.now()/1000;
  return DEMO_CREW.map((d,i)=>{
    const at = n ? pts[Math.floor(((t/6 + d.lag*n)) % n)] : null;
    const g={rounds:true}; if(d.pass) (CONFIG.trip||[]).forEach((tr,j)=>{ if(/^Switzerland/i.test((WEEK[j]||{}).title||'')) g['pass:'+gDay(new Date(tr[0],tr[1],tr[2]))]=Date.now()-(40+i*7)*60000; }); g['top:'+k]=d.top;
    return {id:d.id, name:d.name, color:d.color, role:'member', sharing:true, platform:d.platform, games:g, demo:true,
      pos: at ? {lat:at.c[0], lon:at.c[1], acc:8, speed: at.s.type==='lift' ? 3 : 9+i, on_lift: at.s.type==='lift', run: at.s.type==='lift' ? '' : stepLabel(at.s).replace(/^Ski /,'').replace(/ \((blue|red|black|green)\).*$/,''), km: 4+i*2.5, age_s: 20+i*25} : null };
  });
}
function demoState(){
  const me={id:grp.member_id, name:grp.name||'Alon', color:grp.color||'#F5B700', role:'owner', sharing:true, platform: NATIVE ? 'ios' : 'web', games:{rounds: typeof games==='undefined' || games.rounds!==false}, pos: myPos() ? {lat:myPos()[0], lon:myPos()[1], acc:8, speed:0, on_lift:false, run:'', km:0, age_s:5} : null};
  return {trip:{id:'demo', name:CONFIG.title, invite_code:'DEMO', plan:{}, starts_on:null, ends_on:null}, me:me.id, role:'owner', members:[me].concat(demoMembers()), meet:null};
}
function addDemo(gs){ const have=new Set(gs.members.map(m=>m.name.split(' ')[0].toLowerCase())); demoMembers().forEach(m=>{ if(!have.has(m.name.toLowerCase())) gs.members.push(m); }); }
function setDemoCrew(on){
  store.demoCrew=!!on; persist(); $('demoCrew').setAttribute('aria-pressed', on?'true':'false');
  if(on && !grp){ grp={member_id:'demo-me', name:'Alon', color:'#F5B700', secret:'demo', role:'owner', sharing:true, demo:true}; }
  if(!on && grp && grp.demo){ grp=null; gstate=null; clearFriends(); renderFriendsPill(); renderPick && renderPick(); toast('Demo crew off.'); return; }
  refreshGroup(); if(on) toast('Demo crew on: Avsha, Kelner and Yuval.');
}
$('demoCrew').onclick=()=>setDemoCrew(store.demoCrew!==true);
if(store.demoCrew){ $('demoCrew').setAttribute('aria-pressed','true'); if(!grp) grp={member_id:'demo-me', name:'Alon', color:'#F5B700', secret:'demo', role:'owner', sharing:true, demo:true}; setTimeout(()=>refreshGroup(), 800); }
'''
rep("function groupLoop(){", DEMO + "function groupLoop(){")
# the faces say "everyone"; the count only shows when you picked some
rep("s.textContent = vis.length===others.length ? 'All '+others.length : vis.length+' of '+others.length; p.appendChild(s);",
    "s.textContent = vis.length===others.length ? 'All '+others.length : vis.length+' of '+others.length; if(vis.length===others.length) s.className='all'; p.appendChild(s);")
CSS = '''
/* top row: Shai keeps his name next to the crew faces */
.toppills .guidepill{min-width:132px}
#friendsPill{flex:none;padding:0 10px}
#friendsPill .av{width:22px;height:22px;margin-left:-9px}
#friendsPill span.all{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
.toppills{gap:6px}
@media (max-width:370px){.toppills{gap:4px}#friendsPill{padding:0 6px}#friendsPill .av{width:16px;height:16px;margin-left:-9px}#friendsPill .av:first-child{margin-left:0}.toppills .guidepill{min-width:150px}.toppills .guidepill .gplay{display:none}}
'''
i = s.index('<style>\n/* Layout: one-screen instrument.'); j = s.index('</style>', i)
s = s[:j] + CSS + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('demo crew patch applied')
