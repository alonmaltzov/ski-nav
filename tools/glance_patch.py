"""v3 Glance: ~5 things on screen while skiing.
Top card: where you are (one line), the next turn or lift, how far (one big number).
On a lift: minutes to the top + which way after. Off route: red, how far back, Replan.
Far from the resort: "Go to the start" instead of thousands of km.
Bottom: speed + Hold to stop. Max / km / vert / time / GPS move into the steps sheet (swipe up).
Side rail keeps Shai, ME, ALL, Speed King, STOPPP. Crew dots lose their name tags while skiing."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:80]); s = s.replace(old, new)

# where you are, above the next step
rep('  <footer class="bottom" id="navPanel">\n    <div class="homesum" id="homeSum">',
    '  <footer class="bottom" id="navPanel">\n    <div class="nhere" id="nHere" hidden><i id="nHereDot"></i><span id="nHereTxt"></span></div>\n    <div class="homesum" id="homeSum">')
# your numbers live in the steps sheet while skiing
rep('    <p class="note" id="sheetSub" style="margin:0 0 6px"></p>',
    '    <div class="sstats" id="sStats" hidden><div><b id="sMax">0</b><span>Max</span></div><div><b id="sDist">0.00</b><span>Km</span></div><div><b id="sVert">0</b><span>Vert m</span></div><div><b id="sClock">0:00</b><span>Time</span></div></div>\n'
    '    <p class="note" id="sheetSub" style="margin:0 0 6px"></p>')
rep("  const e = Math.floor(st.elapsed); $('clock').textContent = Math.floor(e/3600)+':'+String(Math.floor(e%3600/60)).padStart(2,'0');\n}",
    "  const e = Math.floor(st.elapsed); $('clock').textContent = Math.floor(e/3600)+':'+String(Math.floor(e%3600/60)).padStart(2,'0');\n"
    "  if($('sMax')){ $('sMax').textContent=$('maxv').textContent; $('sDist').textContent=$('dist').textContent; $('sVert').textContent=$('vert').textContent; $('sClock').textContent=$('clock').textContent;\n"
    "    $('sMax').nextElementSibling.textContent = units==='imp' ? 'Max mph' : 'Max'; $('sDist').nextElementSibling.textContent = units==='imp' ? 'Miles' : 'Km'; $('sVert').nextElementSibling.textContent = units==='imp' ? 'Vert ft' : 'Vert m'; }\n}")

# the glance text, computed at the end of renderStep
rep("  $('nMeta').textContent = meta; if($('nDist')) $('nDist').textContent = big;\n",
    "  $('nMeta').textContent = meta; if($('nDist')) $('nDist').textContent = big;\n"
    "  glance(s);\n")
G = r'''
/* ---------- v3 glance: where you are, what's next, how far ---------- */
const RUNCOL={green:'#16A34A',blue:'#1E5BD8',red:'#D81F26',black:'#111',lift:'#F07A1A'};
function shortLabel(s){
  if(!s) return '';
  if(s.type==='lift') return /^Walk |^Bus /.test(s.name) ? s.name : s.name;
  if(s.type==='end') return s.name;
  if(s.traverse) return 'Traverse to ' + nextLiftName(s.i);
  const l = s.legs && s.legs.length ? s.legs[0] : s;
  return l.name + (l.color ? ' ('+l.color+')' : '');
}
function setHere(txt, col){ const h=$('nHere'); if(!h) return; h.hidden=!txt; $('nHereTxt').textContent=txt||''; $('nHereDot').style.background=col||'#9AA7B2'; }
function glance(s){
  const app=document.querySelector('.app'); const trk = app && app.classList.contains('tracking');
  const dEl=$('nDist'); dEl.classList.remove('txt'); $('nThen').classList.remove('show');
  if($('sStats')) $('sStats').hidden=!trk;
  if(!trk || !s){ setHere(''); return; }
  const n=steps[cur+1], pt = st.last ? [st.last.lat, st.last.lon] : null;
  const off = !$('offroute').hidden;
  const onIt = pt && s.coords && s.coords.length>1 && distToLine(pt, s.coords) < 40;
  const d0 = pt && s.coords ? hav(pt, s.coords[0]) : 0;
  const m = st.match && !String(st.match.id).startsWith('s') ? st.match : null;
  let here='', col='', title='', big=dEl.textContent;
  if(off){
    here='Off route'; col='#FF6B6B'; title='Back to your run';
    if(pt && s.coords && s.coords.length>1) big=fmtLen(distToLine(pt, s.coords));
  } else if(pt && d0 > 20000 && !onIt){
    here='Not at the resort yet'; col='#9AA7B2'; title='Go to the start'; big=shortLabel(s).replace(/ \((green|blue|red|black)\)$/,''); dEl.classList.add('txt');
  } else if(onIt && s.type==='lift'){
    const e=hav(pt, s.coords[s.coords.length-1]);
    here='On '+shortLabel(s); col=RUNCOL.lift; title='To the top'; big=Math.max(1, Math.round(e/4/60))+' min';
    if(n){ $('nThen').textContent='Then: '; const b=document.createElement('b'); b.textContent=shortLabel(n); $('nThen').appendChild(b); $('nThen').classList.add('show'); }
  } else if(onIt){
    here='On '+shortLabel(s); col=RUNCOL[(s.legs&&s.legs[0]||{}).color]||RUNCOL[s.color]||'#9AA7B2';
    title = n ? 'Next: '+shortLabel(n) : 'Last run'; big=fmtLen(hav(pt, s.coords[s.coords.length-1]));
  } else {
    if(m){ here='On '+m.name+(m.color && m.color!=='lift' ? ' ('+m.color+')' : ''); col=RUNCOL[m.color]||'#9AA7B2'; }
    title = s.type==='end' ? s.name : 'Next: '+shortLabel(s);
  }
  setHere(here, col); $('nTitle').textContent=title; dEl.textContent=big;
}
'''
rep("/* tell the iPhone app which step we're on", G + "/* tell the iPhone app which step we're on")
# while skiing the steps sheet opens below the direction card, never over it
rep("$('stepsBtn').onclick=()=>{ playSfx('steps'); $('sheet').hidden=false;",
    "$('stepsBtn').onclick=()=>{ playSfx('steps'); { const a=document.querySelector('.app'), si=$('sheet').querySelector('.sheetin'); si.style.maxHeight = a && a.classList.contains('tracking') ? Math.max(320, innerHeight - $('navPanel').getBoundingClientRect().bottom - 16)+'px' : ''; } $('sheet').hidden=false;")
# off route flips re-render the card
s = s.replace("document.querySelector('.app').classList.toggle('offr', !$('offroute').hidden); })",
              "document.querySelector('.app').classList.toggle('offr', !$('offroute').hidden); if(steps && steps[cur]) glance(steps[cur]); })", 1)
assert "glance(steps[cur]); })" in s

CSS = '''
/* v3 glance: where you are + next + how far, speed + hold. The rest is a swipe away. */
.nhere{display:none}
.app.tracking .nhere:not([hidden]){display:flex;align-items:center;gap:10px;margin:2px 4px 12px;font:700 1.15rem/1.2 var(--f-ui);color:#E6ECF1;white-space:nowrap;overflow:hidden}
.app.tracking .nhere i{width:14px;height:14px;border-radius:50%;flex:none;box-shadow:0 0 0 3px rgb(255 255 255/.25)}
.app.tracking .nhere span{overflow:hidden;text-overflow:ellipsis}
.app.tracking #navPanel .eyebrow,.app.tracking #navPanel .nexttxt p{display:none}
.app.tracking #navPanel .then{display:none}
.app.tracking #navPanel .then.show{display:block;font:700 1.15rem/1.3 var(--f-ui);margin-top:12px;color:#C9D3DB}
.app.tracking #navPanel .then.show b{color:#FF8A3D}
.app.tracking #navPanel .nexttxt h2{font-size:1.35rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.app.tracking .ndist:not(:empty){font-size:3.2rem;line-height:1}
.app.tracking .ndist.txt{font-size:2.2rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.app.tracking .top .stats,.app.tracking .top .daybar,.app.tracking .top .gps{display:none!important}
.app.tracking .top{grid-template-columns:minmax(0,1fr) auto}
.app.tracking .top .holdstop{grid-column:2}
.app.tracking .spgrab span{display:none}
.app.tracking .spgrab{min-height:24px}
.app.tracking .speed{font-size:5.6rem;line-height:.9}
.app.tracking .speed small{font-size:1.1rem}
.app.tracking .donechip{display:none!important}
.app.tracking .fdot span{display:none}
.app.tracking #kingTop{display:none}
.sstats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin:4px 0 10px}
.sstats[hidden]{display:none}
.sstats div{background:var(--glass-in,rgb(255 255 255/.6));border-radius:18px;padding:10px 10px 8px}
.sstats b{display:block;font:800 1.45rem/1.1 var(--f-num);font-variant-numeric:tabular-nums}
.sstats span{font:800 .72rem var(--f-ui);letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
@media (max-width:370px){.app.tracking .speed{font-size:4.8rem}.app.tracking .ndist:not(:empty){font-size:2.8rem}.sstats b{font-size:1.2rem}}
'''
i = s.index('<style>\n/* Layout: one-screen instrument.'); j = s.index('</style>', i)
s = s[:j] + CSS + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('glance patch applied')
