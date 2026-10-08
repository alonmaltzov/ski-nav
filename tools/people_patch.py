"""Friends: choose who you see (approved Oct 8).
- people pill shows who you follow ("All 3" / "2 of 3") and opens "On your map": Everyone or Choose, a switch per person,
  tap a name to fly to them. The choice is kept on this phone only.
- friend dots: lift badge when on a lift; fade + "x min ago" when stale (already)
- ALL zooms to you + today's route + everyone you're showing
Usage: python3 tools/people_patch.py index.html nyc.html"""
import sys

def rep(s, old, new, count=1):
    n = s.count(old); assert n == count, (old[:90], n); return s.replace(old, new)

HTML = """
<div class="sheet" id="pickSheet" hidden>
  <div class="sheetin" role="dialog" aria-label="Who is on your map">
    <div class="sheethead"><h3>On your map</h3><button class="btn ghost sm" id="pickDone" type="button">Done</button></div>
    <div class="seg pickseg" id="pickSeg"><button type="button" data-v="all" aria-pressed="true">Everyone</button><button type="button" data-v="choose" aria-pressed="false">Choose</button></div>
    <div class="picklist" id="pickList"></div>
    <p class="note" style="margin:0;text-align:center">Tap a name to fly to them. ALL shows you, today's route and everyone you're showing. Only you see this choice.</p>
  </div>
</div>
"""

CSS = """
/* ===== friends: choose who you see ===== */
.fdot b{position:relative}
.fdot.lift b::after{content:"";position:absolute;right:-7px;bottom:-5px;width:18px;height:18px;border-radius:50%;border:2px solid #fff;background:#0b1620 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 18L18 6M11 6h7v7'/%3E%3C/svg%3E") center/11px no-repeat}
.pickseg{display:grid;grid-template-columns:1fr 1fr}
.picklist{display:flex;flex-direction:column;background:var(--bg);border-radius:16px;overflow:hidden}
.prow{display:flex;align-items:center;gap:12px;padding:10px 12px;border-top:1px solid var(--line)}
.prow:first-child{border-top:0}
.prow .pav{width:44px;height:44px;border-radius:50%;color:#fff;font:700 1rem/44px var(--f-ui);text-align:center;flex:none}
.prow.off .pav{opacity:.45}
.prow .pwho{flex:1;min-width:0;display:flex;flex-direction:column;align-items:flex-start;border:0;background:none;padding:0;text-align:left;color:var(--ink);font:inherit}
.prow .pwho b{font-size:1.05rem}
.prow .pwho span{font-size:.9rem;color:var(--muted)}
.prow .pdist{font-weight:700;color:var(--muted);white-space:nowrap}
.prow .ptog{display:flex;border:0;background:none;padding:6px 0;flex:none}
.prow .ptog .sw{display:block;width:51px;height:31px;border-radius:16px;position:relative;flex:none;background:color-mix(in srgb,var(--muted) 35%,transparent)}
.prow .ptog .sw::after{content:"";position:absolute;top:2px;left:2px;width:27px;height:27px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgb(0 0 0/.25);transition:left .15s}
.prow .ptog[aria-pressed="true"] .sw{background:var(--accent)}
.prow .ptog[aria-pressed="true"] .sw::after{left:22px}
.picklist.all .ptog{display:none}
"""

JS = r"""
/* ---------- who's on my map: everyone (default) or a chosen few; this phone only ---------- */
const GVKEY='skinav-gview';
let gview=(()=>{ try{ return JSON.parse(localStorage.getItem(GVKEY)||'null') || {mode:'all', hide:[]}; }catch(e){ return {mode:'all', hide:[]}; } })();
const saveGview=()=>{ try{ localStorage.setItem(GVKEY, JSON.stringify(gview)); }catch(e){} };
const shown=m=>gview.mode==='all' || !gview.hide.includes(m.id);
const friendsOf=()=>gstate && grp ? gstate.members.filter(m=>m.id!==grp.member_id) : [];
function openPick(){ renderPick(); $('pickSheet').hidden=false; }
function renderPick(){
  $('pickSeg').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed', b.dataset.v===gview.mode?'true':'false'));
  const box=$('pickList'); box.textContent=''; box.classList.toggle('all', gview.mode==='all');
  const me=myPos();
  for(const m of friendsOf()){
    const on=shown(m), r=document.createElement('div'); r.className='prow'+(on?'':' off');
    const av=document.createElement('span'); av.className='pav'; av.style.background=m.color; av.textContent=initials(m.name);
    const who=document.createElement('button'); who.type='button'; who.className='pwho';
    const b=document.createElement('b'); b.textContent=m.name; const st2=document.createElement('span');
    st2.textContent = !m.sharing ? 'Not sharing location' : !m.pos ? 'No location yet' : (m.pos.on_lift?'On a lift':(m.pos.run?'On '+m.pos.run:'On the mountain'))+' · '+ago(m.pos.age_s);
    who.append(b, st2);
    who.onclick=()=>{ if(!m.pos) return; if(!shown(m)){ gview.hide=gview.hide.filter(x=>x!==m.id); saveGview(); renderFriends(); renderFriendsPill(); }
      $('pickSheet').hidden=true; setFollow(false); map.flyTo({center:[m.pos.lon,m.pos.lat], zoom:Math.max(map.getZoom(),15)}); };
    const d=document.createElement('span'); d.className='pdist'; d.textContent = me && m.pos ? fmtLen(hav(me,[m.pos.lat,m.pos.lon])) : '';
    const t=document.createElement('button'); t.type='button'; t.className='ptog'; t.setAttribute('aria-pressed', on?'true':'false'); t.setAttribute('aria-label','Show '+m.name+' on my map');
    t.innerHTML='<span class="sw"></span>';
    t.onclick=()=>{ gview.hide = on ? [...gview.hide, m.id] : gview.hide.filter(x=>x!==m.id); saveGview(); renderPick(); renderFriends(); renderFriendsPill(); };
    r.append(av, who, d, t); box.appendChild(r);
  }
}
$('pickSeg').querySelectorAll('button').forEach(b=>b.onclick=()=>{ gview.mode=b.dataset.v; saveGview(); renderPick(); renderFriends(); renderFriendsPill(); });
$('pickDone').onclick=()=>{ $('pickSheet').hidden=true; };
$('pickSheet').onclick=e=>{ if(e.target.id==='pickSheet') $('pickSheet').hidden=true; };
/* ALL: me + today's route + everyone I'm showing */
$('fitBtn').onclick=()=>{
  setFollow(false);
  if(view==='prog'){ map.fitBounds(scopeBounds,{padding:PAD, pitch: is3D?55:0}); return; }
  const b=new maplibregl.LngLatBounds(routeBounds[0], routeBounds[1]);
  const me=myPos(); if(me) b.extend([me[1],me[0]]);
  for(const m of friendsOf()) if(shown(m) && m.pos && m.pos.age_s < 3*3600) b.extend([m.pos.lon, m.pos.lat]);
  map.fitBounds(b,{padding:{top:PAD.top+40, bottom:PAD.bottom+40, left:PAD.left+30, right:PAD.right+30}, pitch: is3D?55:0, maxZoom:16});
};
"""

def patch(path):
    s = open(path).read()
    if 'id="pickSheet"' in s: print('already', path); return
    s = rep(s, '<div class="sheet" id="meetSheet" hidden>', HTML.strip() + '\n\n<div class="sheet" id="meetSheet" hidden>')
    s = rep(s, "/* ===== redesign: map-first home", CSS + "/* ===== redesign: map-first home")
    # dots: hide people I'm not following, lift badge
    s = rep(s, "for(const m of gstate.members){ if(m.id===grp.member_id || !m.pos || m.pos.age_s > 3*3600) continue; keep.add(m.id);",
               "for(const m of gstate.members){ if(m.id===grp.member_id || !m.pos || m.pos.age_s > 3*3600 || !shown(m)) continue; keep.add(m.id);")
    s = rep(s, "const old=m.pos.age_s > 300; el.classList.toggle('old', old);",
               "const old=m.pos.age_s > 300; el.classList.toggle('old', old); el.classList.toggle('lift', !!m.pos.on_lift && !old);")
    # pill: who I follow, opens the picker
    s = rep(s, "p.onclick=()=>{ openDrawer(); showGroup(true); };",
               "p.onclick=()=>{ if(friendsOf().length) openPick(); else { openDrawer(); showGroup(true); } };")
    s = rep(s, "  others.slice(0,3).forEach(m=>{ const a=document.createElement('i'); a.className='av'; a.style.background=m.color; p.appendChild(a); });\n  const live=others.filter(m=>m.pos && m.pos.age_s<300).length; const s=document.createElement('span'); s.textContent=String(others.length); p.appendChild(s);\n  p.setAttribute('aria-label', others.length+' friends, '+live+' on the map now');",
               "  const vis=others.filter(shown); (vis.length?vis:others).slice(0,3).forEach(m=>{ const a=document.createElement('i'); a.className='av'; a.style.background=m.color; if(!vis.length) a.style.opacity=.4; p.appendChild(a); });\n  const live=vis.filter(m=>m.pos && m.pos.age_s<300).length; const s=document.createElement('span'); s.textContent = vis.length===others.length ? 'All '+others.length : vis.length+' of '+others.length; p.appendChild(s);\n  p.setAttribute('aria-label', 'Showing '+vis.length+' of '+others.length+' friends, '+live+' on the map now. Choose who to see');")
    # the old ALL handler is replaced by the one above
    s = rep(s, "$('fitBtn').onclick=()=>{ setFollow(false); map.fitBounds(view==='prog'?scopeBounds:routeBounds,{padding:PAD, pitch: is3D?55:0}); };", "")
    s = rep(s, "tellNative(); groupLoop(); refreshGroup(); renderFriendsPill();", JS.strip() + "\ntellNative(); groupLoop(); refreshGroup(); renderFriendsPill();")
    s = rep(s, "get grp(){return grp;},", "get grp(){return grp;}, get gview(){return gview;}, openPick,")
    open(path, 'w').write(s); print('patched', path)

for p in sys.argv[1:]: patch(p)
