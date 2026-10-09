"""Split costs: the organizer pastes the Splitwise group invite link once; everyone gets a "Split costs" button
(group screen + "On your map" sheet) next to "Talk with the group". Stored in the trip plan like the WhatsApp link.
Usage: python3 tools/split_patch.py index.html nyc.html"""
import sys

def rep(s, old, new, count=1):
    n = s.count(old); assert n == count, (old[:90], n); return s.replace(old, new)

BTN = '<a class="btn splitbtn" id="%s" href="#" hidden><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="6" width="20" height="13" rx="2"/><path d="M2 10h20M6 15h4"/></svg>Split costs</a>'

CARD = """        <div class="gcard" id="gSplitSet" hidden>
          <b>Splitwise group</b>
          <p class="note" style="margin:0">In Splitwise: open the group &gt; Settings &gt; Invite via link, copy and paste it here. Everyone gets a "Split costs" button that opens the group.</p>
          <input class="ginput" id="gSplitLink" type="url" inputmode="url" placeholder="https://www.splitwise.com/join/…" autocomplete="off">
          <div class="ggrid"><button class="btn primary" id="gSplitSave" type="button">Save</button><button class="btn ghost" id="gSplitClear" type="button">Remove</button></div>
        </div>
"""

CSS = """
/* ===== split costs ===== */
.btn.splitbtn{display:flex;align-items:center;justify-content:center;gap:8px;text-decoration:none;background:var(--panel);color:var(--ink);border:2px solid #1cc29f;min-height:52px}
.btn.splitbtn[hidden]{display:none}
.linkrow{display:grid;grid-template-columns:1fr;gap:8px}
.linkrow>[hidden]{display:none}

"""

JS = r"""
/* ---------- split costs: the trip's Splitwise group link, pasted once by the organizer ---------- */
const splitLink = () => { const u = gstate && gstate.trip && gstate.trip.plan && gstate.trip.plan.split; return typeof u==='string' && /^https:\/\//.test(u) ? u : ''; };
function renderSplit(){
  const u = splitLink();
  for(const id of ['gSplit','pickSplit']){ const a=$(id); if(!a) continue; a.hidden=!u; a.href=u||'#';
    if(NATIVE) a.removeAttribute('target'); else { a.target='_blank'; a.rel='noopener'; } }
  const owner = gstate && gstate.role==='owner';
  if($('gSplitSet')){ $('gSplitSet').hidden=!owner; if(owner && document.activeElement!==$('gSplitLink')) $('gSplitLink').value=u; $('gSplitClear').hidden=!u; }
}
$('gSplitSave').onclick=async()=>{ const v=$('gSplitLink').value.trim(); $('gErr').hidden=true;
  if(!/^https:\/\/(www\.)?splitwise\.com\/\S+$/.test(v)){ gErr(new Error('Paste the invite link from Splitwise (it starts with https://www.splitwise.com/).')); return; }
  try{ await savePlan({split:v}); toast('Saved. Everyone sees “Split costs”.'); renderSplit(); }catch(e){ gErr(e); } };
$('gSplitClear').onclick=async()=>{ try{ await savePlan({split:null}); $('gSplitLink').value=''; renderSplit(); }catch(e){ gErr(e); } };
"""

def patch(path):
    s = open(path).read()
    if 'id="gSplitSet"' in s: print('already', path); return
    # buttons side by side: Talk with the group | Split costs
    i = s.index('<a class="btn primary callbtn" id="gCall"'); j = s.index('</a>', i) + 4
    s = s[:i] + '<div class="linkrow">' + s[i:j] + BTN % 'gSplit' + '</div>' + s[j:]
    i = s.index('<a class="btn primary callbtn" id="pickCall"'); j = s.index('</a>', i) + 4
    s = s[:i] + '<div class="linkrow">' + s[i:j] + BTN % 'pickSplit' + '</div>' + s[j:]
    s = rep(s, '        <button class="grow toggle gtoggle" id="gSharing"', CARD + '        <button class="grow toggle gtoggle" id="gSharing"')
    s = rep(s, "/* ===== redesign: map-first home", CSS + "/* ===== redesign: map-first home")
    s = rep(s, "renderFriends(); renderFriendsPill(); renderCall();", "renderFriends(); renderFriendsPill(); renderCall(); renderSplit();")
    s = rep(s, "tellNative(); groupLoop(); refreshGroup(); renderFriendsPill();", JS.strip() + "\ntellNative(); groupLoop(); refreshGroup(); renderFriendsPill();")
    open(path, 'w').write(s); print('patched', path)

for p in sys.argv[1:]: patch(p)
