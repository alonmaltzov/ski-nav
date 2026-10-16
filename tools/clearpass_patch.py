"""Clear tracking history also resets the passport checks, STOPPP rounds done and top speeds (and tells the group)."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80]); s = s.replace(old, new)
rep("b.textContent='Tap again: clears every day’s track, km and runs';",
    "b.textContent='Tap again: clears tracks, km, runs, passports and games';")
rep("  Object.assign(st, {trail:[], dist:0, vert:0, max:0, elapsed:0, last:null, onLift:false}); cur=0; store.days={};\n",
    "  Object.assign(st, {trail:[], dist:0, vert:0, max:0, elapsed:0, last:null, onLift:false}); cur=0; store.days={};\n"
    "  /* passports, STOPPP rounds done and top speeds start over too; the crew sees your checks cleared */\n"
    "  try{ const out={}; Object.keys(games.pass||{}).forEach(k=>out['pass:'+k]=0); Object.keys(games.top||{}).forEach(k=>out['top:'+k]=0);\n"
    "    games.pass={}; games.fired={}; games.top={}; games.topRun={}; games.swiss={}; games.nudgeSeen={}; saveGames();\n"
    "    if(Object.keys(out).length && typeof gPost==='function') gPost(out, true);\n"
    "    renderPassGate(); renderStopBtn(); renderKingBtn(); tellGamesNative(); }catch(e){}\n")
open(p, 'w', encoding='utf-8').write(s); print('clear-history patch applied')
