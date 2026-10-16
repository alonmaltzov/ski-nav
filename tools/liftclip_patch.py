"""Weather & lifts: the crew's clip plays the moment you tap (not after the network check, which some phones block)."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80]); s = s.replace(old, new)
rep("  const b=$('liftsPill'); b.classList.add('busy');\n  renderWx(); renderLifts(); $('todaySheet').hidden=false;",
    "  const b=$('liftsPill'); b.classList.add('busy');\n  playSfx('closed');   /* right on the tap, so the phone lets it play */\n  renderWx(); renderLifts(); $('todaySheet').hidden=false;")
rep("  const say_=()=>{ try{ speak([line]); }catch(e){} };\n  playSfx('closed', say_);   // the crew's clip every tap, then the guide reads the status\n",
    "  try{ speak([line]); }catch(e){}\n")
open(p, 'w', encoding='utf-8').write(s); print('lift clip patch applied')
