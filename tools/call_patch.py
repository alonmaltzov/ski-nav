"""Group call via a WhatsApp call link (no phone numbers): the organizer pastes the link once in the group screen,
everyone in the group gets a "Call the group" button (group screen + "On your map" sheet).
Stored in the trip's plan (organizer only); the plan style update now merges instead of overwriting.
Usage: python3 tools/call_patch.py index.html nyc.html"""
import sys

def rep(s, old, new, count=1):
    n = s.count(old); assert n == count, (old[:90], n); return s.replace(old, new)

CALL_BTN = '<a class="btn primary callbtn" id="%s" href="#" hidden><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>Call the group</a>'

GROUP_HTML = """        %s
        <div class="gcard" id="gCallSet" hidden>
          <b>Group call</b>
          <p class="note" style="margin:0">In WhatsApp: Calls &gt; Create call link &gt; Voice, then copy and paste it here. One link for the whole week, no phone numbers needed.</p>
          <input class="ginput" id="gCallLink" type="url" inputmode="url" placeholder="https://call.whatsapp.com/voice/…" autocomplete="off">
          <div class="ggrid"><button class="btn primary" id="gCallSave" type="button">Save</button><button class="btn ghost" id="gCallClear" type="button">Remove</button></div>
        </div>
        <button class="grow toggle gtoggle" id="gSharing\"""" % (CALL_BTN % 'gCall')

CSS = """
/* ===== group call ===== */
.callbtn{display:flex;align-items:center;justify-content:center;gap:8px;text-decoration:none;background:#15803d;color:#fff;min-height:52px}
.callbtn[hidden]{display:none}
"""

JS = r"""
/* ---------- group call: a WhatsApp call link the organizer pastes once ---------- */
const callLink = () => { const u = gstate && gstate.trip && gstate.trip.plan && gstate.trip.plan.call; return typeof u==='string' && /^https:\/\//.test(u) ? u : ''; };
function renderCall(){
  const u = callLink();
  for(const id of ['gCall','pickCall']){ const a=$(id); if(!a) continue; a.hidden=!u; a.href=u||'#';
    // in the iPhone app a plain link opens WhatsApp; in a browser keep Ski Nav open in its tab
    if(NATIVE) a.removeAttribute('target'); else { a.target='_blank'; a.rel='noopener'; } }
  const owner = gstate && gstate.role==='owner';
  if($('gCallSet')){ $('gCallSet').hidden=!owner; if(owner && document.activeElement!==$('gCallLink')) $('gCallLink').value=u; $('gCallClear').hidden=!u; }
}
async function savePlan(patch){ const plan={...((gstate && gstate.trip && gstate.trip.plan) || {}), ...patch}; await rpc('set_plan',{p_secret:grp.secret, p_plan:plan}); if(gstate) gstate.trip.plan=plan; }
$('gCallSave').onclick=async()=>{ const v=$('gCallLink').value.trim();
  if(!/^https:\/\/\S+$/.test(v)){ gErr(new Error('Paste the call link from WhatsApp (it starts with https://).')); return; }
  try{ await savePlan({call:v}); toast('Group call link saved. Everyone sees “Call the group”.'); renderCall(); }catch(e){ gErr(e); } };
$('gCallClear').onclick=async()=>{ try{ await savePlan({call:null}); $('gCallLink').value=''; renderCall(); }catch(e){ gErr(e); } };
"""

def patch(path):
    s = open(path).read()
    if 'id="gCallSet"' in s: print('already', path); return
    s = rep(s, '        <button class="grow toggle gtoggle" id="gSharing"', GROUP_HTML)
    s = rep(s, '    <div class="picklist" id="pickList"></div>', '    ' + CALL_BTN % 'pickCall' + '\n    <div class="picklist" id="pickList"></div>')
    s = rep(s, "/* ===== redesign: map-first home", CSS + "/* ===== redesign: map-first home")
    # plan style no longer wipes other plan fields (the call link)
    s = rep(s, "if(grp && gstate && gstate.role==='owner') rpc('set_plan',{p_secret:grp.secret, p_plan:{variant:v}}).catch(()=>{}); };",
               "if(grp && gstate && gstate.role==='owner') savePlan({variant:v}).catch(()=>{}); };")
    s = rep(s, "  renderFriends(); renderFriendsPill(); if(!$('menuGroup').hidden) renderGroup();\n}",
               "  renderFriends(); renderFriendsPill(); renderCall(); if(!$('menuGroup').hidden) renderGroup();\n}")
    s = rep(s, "tellNative(); groupLoop(); refreshGroup(); renderFriendsPill();", JS.strip() + "\ntellNative(); groupLoop(); refreshGroup(); renderFriendsPill();")
    open(path, 'w').write(s); print('patched', path)

for p in sys.argv[1:]: patch(p)
