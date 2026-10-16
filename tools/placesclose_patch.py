"""Places on the map: a close button, and a tap anywhere outside the panel closes it."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80]); s = s.replace(old, new)
rep('<div class="placesbox" id="placesBox" hidden><b>Show on map</b>',
    '<div class="placesbox" id="placesBox" hidden><div class="phead"><b>Show on map</b><button class="xbtn" id="placesClose" type="button" aria-label="Close places">✕</button></div>')
rep("$('placesBtn').onclick=()=>{",
    "function closePlaces(){ if($('placesBox').hidden) return; $('placesBox').hidden=true; $('placesBtn').setAttribute('aria-pressed','false'); }\n"
    "$('placesClose').onclick=closePlaces;\n"
    "document.addEventListener('pointerdown', e=>{ const b=$('placesBox'); if(b.hidden) return; if(b.contains(e.target) || e.target.closest('#placesBtn,#menuPlaces')) return; closePlaces(); }, true);\n"
    "$('placesBtn').onclick=()=>{")
CSS = '''
/* places panel: header with a close button */
.phead{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:6px}
.phead .xbtn{width:56px;height:56px;flex:none}
/* Galaxy S24/S25 height: the week and Settings fit without scrolling */
@media (max-width:370px){.drawerhead .hbtns .xbtn{width:52px;height:52px}.drawerhead .hbtns{gap:6px}.drawerhead h2{font-size:1.3rem!important;white-space:nowrap!important}}
@media (max-height:800px){#menuSettings .grow{min-height:50px}#menuSettings .seg button{min-height:44px}#menuMain .daycard{min-height:56px}#menuPlaces{min-height:54px}}
'''
i = s.index('<style>\n/* Layout: one-screen instrument.'); j = s.index('</style>', i)
s = s[:j] + CSS + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('places close patch applied')
