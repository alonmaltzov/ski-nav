"""Slopes & lifts: live slope status next to the lifts (same Intermaps feed the official site uses),
checked once an hour and whenever the phone gets a connection; closed runs show in the plan and the router avoids them."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    assert old in s, old[:90]; s = s.replace(old, new, 1)

# fetch: slopes too, once an hour, and as soon as a connection comes back
rep("  if(!force && liftStat && Date.now()-liftStat.t < 30*60e3) return;", "  if(!force && liftStat && Date.now()-liftStat.t < 60*60e3) return;")
rep("""    liftStat = {t:Date.now(), last:d.lastUpdate||'', by, open, total:(d.lifts||[]).length};""",
"""    const sl={}; let slOpen=0;
    for(const x of d.slopes||[]){ const p=x.popup||{}; const v=p.status||x.status; sl[String(p.oid)]=v; if(v==='open') slOpen++; }
    liftStat = {t:Date.now(), last:d.lastUpdate||'', by, open, total:(d.lifts||[]).length, sl, slOpen, slTotal:(d.slopes||[]).length};""")
rep("function planLifts(){", r'''/* slopes: our run names (OpenStreetMap) matched to the resort's slope list by tools/slopemap.py */
function slNorm(x){ x=String(x||'').normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/\b(piste|variante|du|de|la|le|les|des|d|l|a|the)\b/g,' ').replace(/[^a-z0-9]+/g,' ').trim();
  return x.split(' ').filter(Boolean).map(w=>w.length>4 && w.endsWith('s') ? w.slice(0,-1) : w).join(' '); }
const SL_DIFF={green:['very-easy','easy'], blue:['easy','very-easy'], red:['medium'], black:['difficult','very-difficult'], nov:['very-easy','easy'], eas:['easy','very-easy'], int:['medium'], adv:['difficult','very-difficult'], exp:['very-difficult','difficult']};
function slopeStatus(name, color){
  if(!liftStat || !liftStat.sl) return null; const m=SLOPEMAP[slNorm(name)]; if(!m) return null;
  const want=SL_DIFF[color]||[]; const pick=m.filter(x=>want.includes(x[0])); const ss=(pick.length?pick:m).map(x=>liftStat.sl[x[1]]).filter(Boolean);
  if(!ss.length) return null; return ss.includes('open') ? 'open' : ss.includes('in_preparation') ? 'soon' : 'closed';
}
function planSlopes(){ const seen=new Set(), out=[];
  steps.forEach(s=>{ if(s.type!=='run') return; (s.legs||[]).forEach(l=>{ const k=slNorm(l.name); if(!k || seen.has(k)) return; seen.add(k); out.push({name:l.name, color:l.color, st:slopeStatus(l.name, l.color)}); }); });
  return out; }
function runClosed(s){ return resortRunning() && s.type==='run' && (s.legs||[]).some(l=>{ const v=slopeStatus(l.name,l.color); return v && v!=='open'; }); }
let lineMemo={t:0, m:{}};
function lineClosed(li){ const b=BG[li]; if(!b || b[0]!=='R' || !b[2] || !liftStat || !resortRunning()) return false;
  if(lineMemo.t!==liftStat.t) lineMemo={t:liftStat.t, m:{}}; if(li in lineMemo.m) return lineMemo.m[li];
  const v=slopeStatus(b[2], b[1]); return (lineMemo.m[li] = !!v && v!=='open'); }
function planLifts(){''')
rep("setInterval(()=>{ if(document.visibilityState!=='visible') return; const h=new Date().getHours(); if(h>=8 && h<18) fetchLifts(false); fetchWx(false); }, 5*60e3);",
    "setInterval(()=>{ if(document.visibilityState!=='visible') return; const h=new Date().getHours(); if(h>=8 && h<18) fetchLifts(false); fetchWx(false); }, 5*60e3);\n/* back on wifi or signal: check right away (if the last check is 10+ minutes old) */\naddEventListener('online', ()=>{ if(!liftStat || Date.now()-liftStat.t > 10*60e3) fetchLifts(true); });")

# the card: Slopes & lifts, plan items closed first
rep('<div class="lhead"><span class="eyebrow">Lifts</span><small id="liftsUpdated"></small></div>', '<div class="lhead"><span class="eyebrow">Slopes &amp; lifts</span><small id="liftsUpdated"></small></div>')
rep("  $('liftsBig').textContent = liftStat.open+' of '+liftStat.total+' lifts open';",
    "  $('liftsBig').textContent = liftStat.open+'/'+liftStat.total+' lifts · '+(liftStat.slOpen!=null ? liftStat.slOpen+'/'+liftStat.slTotal+' slopes' : 'slopes --');")
a = s.index("  const box=$('liftRows'); box.textContent='';"); z = s.index("    row.append(a,b); box.appendChild(row); }\n", a) + len("    row.append(a,b); box.appendChild(row); }\n")
s = s[:a] + r'''  const box=$('liftRows'); box.textContent='';
  const lab=v=>!v ? 'no data' : v==='open' ? 'Open' : v==='soon' ? 'Opening soon' : 'Closed', cls=v=>v==='open'?'open':v==='soon'?'soon':v?'closed':'';
  const rank=v=>v==='open'?2:v?0:1;
  const items = pl.map(x=>({name:x.s.name, st:liftStatusOf(x.bi), kind:'lift'})).concat(planSlopes().map(x=>({name:x.name, st:x.st, kind:'run', color:x.color})));
  items.sort((p,q)=>rank(p.st)-rank(q.st));
  const sub=t=>{ const h=document.createElement('div'); h.className='lsub'; h.textContent=t; box.appendChild(h); };
  let lastOpen=null;
  for(const x of items){ const isOpen=x.st==='open'; if(lastOpen!==isOpen){ sub(isOpen ? 'Open on today’s plan' : 'Not open on today’s plan'); lastOpen=isOpen; }
    const row=document.createElement('div'); row.className='lrow';
    const a=document.createElement('span'); if(x.kind==='run'){ const i=document.createElement('i'); i.className='lpiste '+(x.color||''); a.appendChild(i); } a.append(x.name+(x.kind==='lift'?'':' '));
    const b=document.createElement('span'); b.textContent=lab(x.st); b.className=cls(x.st);
    row.append(a,b); box.appendChild(row); }
''' + s[z:]
rep(".lrow .open{color:var(--ok)}", ".lsub{font-size:.75rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);margin:10px 0 2px}\n.lpiste{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:8px;background:var(--p-blue);vertical-align:middle}.lpiste.green{background:var(--p-green)}.lpiste.red{background:var(--p-red)}.lpiste.black{background:var(--p-black)}\n.lrow .open{color:var(--ok)}")
# counts include runs
rep("const pl = planLifts(), closed = pl.filter(x=>liftStatusOf(x.bi) && liftStatusOf(x.bi)!=='open');",
    "const pl = planLifts(), closed = pl.filter(x=>liftStatusOf(x.bi) && liftStatusOf(x.bi)!=='open').concat(planSlopes().filter(x=>x.st && x.st!=='open'));")
rep("$('liftsNote').textContent = off ? 'Not running yet. Season starts in December.' : (closed.length ? 'Some plan lifts are shut. Plan from here goes around them.' ",
    "$('liftsNote').textContent = off ? 'Not running yet. Season starts in December.' : (closed.length ? 'Some of today’s plan is shut. Plan from here goes around it.' ")
# home button label
rep('<span id="liftsPillTxt">Lifts</span>', '<span id="liftsPillTxt">Slopes &amp; lifts</span>')
s = s.replace("$('liftsPillTxt').textContent='Lifts';", "$('liftsPillTxt').textContent='Slopes & lifts';")
s = s.replace("$('liftsPillTxt').textContent='Lifts · '+closed.length;", "$('liftsPillTxt').textContent='Slopes & lifts · '+closed.length;")
rep('aria-label="Check lift status"', 'aria-label="Check slopes and lifts"')

# what the guide says
rep("""  else { shut=planLifts().filter(x=>{ const v=liftStatusOf(x.bi); return v && v!=='open'; });""",
    """  else { shut=planLifts().filter(x=>{ const v=liftStatusOf(x.bi); return v && v!=='open'; }).map(x=>({s:x.s})).concat(planSlopes().filter(x=>x.st && x.st!=='open').map(x=>({s:{name:x.name}})));""")
rep("line = shut.length ? (shut.length===1 ? shut[0].s.name+' is shut. Plan from here fixes it.' : shut.length+' plan lifts shut: '+shut.slice(0,3).map(x=>x.s.name).join(', ')+'. Plan from here fixes it.')",
    "line = shut.length ? (shut.length===1 ? shut[0].s.name+' is shut. Plan from here fixes it.' : shut.length+' things on the plan are shut: '+shut.slice(0,3).map(x=>x.s.name).join(', ')+'. Plan from here fixes it.')")
rep(": 'All '+planLifts().length+' plan lifts open. Go.'; }", ": 'Everything on today’s plan is open. Go.'; }")
rep("line='Lifts aren’t running yet. See you in December.';", "line='Nothing’s open yet. See you in December.';")
# brief + closed-lift alert count runs too
rep("f.closed = planLifts().filter(x=>liftStatusOf(x.bi) && liftStatusOf(x.bi)!=='open').length;", "f.closed = planLifts().filter(x=>liftStatusOf(x.bi) && liftStatusOf(x.bi)!=='open').length + planSlopes().filter(x=>x.st && x.st!=='open').length;")
rep("if(f.closed) S.push(f.closed+(f.closed===1?' plan lift is':' plan lifts are')+' shut. Plan from here fixes it.');", "if(f.closed) S.push(f.closed+(f.closed===1?' thing on the plan is':' things on the plan are')+' shut. Plan from here fixes it.');")
rep("const d=todayStr(), shut=planLifts().filter(x=>{ const v=liftStatusOf(x.bi); return v && v!=='open'; }).map(x=>String(x.bi));",
    "const d=todayStr(), shut=planLifts().filter(x=>{ const v=liftStatusOf(x.bi); return v && v!=='open'; }).map(x=>String(x.bi)).concat(planSlopes().filter(x=>x.st && x.st!=='open').map(x=>'r:'+slNorm(x.name)));")
# the plan shows closed runs; the router skips them
rep("  if(s.type==='lift' && typeof liftClosed==='function' && liftClosed(stepLiftBi(s))) meta = 'Closed right now · tap Plan from here · ' + meta;",
    "  if(s.type==='lift' && typeof liftClosed==='function' && liftClosed(stepLiftBi(s))) meta = 'Closed right now · tap Plan from here · ' + meta;\n  else if(s.type==='run' && typeof runClosed==='function' && runClosed(s)) meta = 'Run closed · tap Plan from here · ' + meta;")
rep("      if(e[2]==='l'){ const b=BG[e[3]]; if(liftClosed(e[3])) continue; if(isDragLift(b)) c+=1800; }",
    "      if(e[2]==='l'){ const b=BG[e[3]]; if(liftClosed(e[3])) continue; if(isDragLift(b)) c+=1800; }\n      else if(e[2]==='r' && lineClosed(e[3])) continue;")
rep("    if(s.type==='lift' && liftClosed(stepLiftBi(s))) continue;", "    if((s.type==='lift' && liftClosed(stepLiftBi(s))) || runClosed(s)) continue;")
rep('window.__ski = { map, st, ', 'window.__ski = { map, st, planSlopes, slopeStatus, slNorm, ', )
s = s.replace('<i class="ldot" id="liftsDot"></i><span id="liftsPillTxt">Slopes &amp; lifts</span>', '<span class="gtxt"><b>Slopes</b><small><i class="ldot" id="liftsDot"></i><span id="liftsPillTxt">&amp; lifts</span></small></span>')
s = s.replace("$('liftsPillTxt').textContent='Slopes & lifts';", "$('liftsPillTxt').textContent='& lifts';").replace("$('liftsPillTxt').textContent='Slopes & lifts · '+closed.length;", "$('liftsPillTxt').textContent=closed.length+' shut';")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
