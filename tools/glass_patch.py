"""Liquid glass redesign (web app, so iPhone and Android get the same look):
- frosted glass panels floating over the map (top bar, map buttons, day card, every sheet), light and dark
- Sun mode keeps solid panels; phones without blur get near-solid panels
- Shai's hub: tap Shai, the crew's clip plays, then his lines; 4 tiles: Start skiing, Weather & lifts, Call the crew, Splitwise
  (the separate Slopes & lifts pill and the Ask chat go; call + Splitwise leave the crew sheet)
- Swiss days: Start skiing stays locked until that day's passport slide; the menu marks Swiss days and their check"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90]); s = s.replace(old, new)
SH = re.search(r'<svg class="gface" viewBox="0 0 120 120" aria-hidden="true">.*?</svg>', s, re.S).group(0)
SKI = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="15" cy="4.5" r="2"/><path d="M4 20l16-6M8 11l4-3 3 4-4 3"/></svg>'
PHONE = '<svg viewBox="0 0 24 24" width="22" height="22" fill="#fff" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 006.6 6.6l2.2-2.2a1 1 0 011-.25 11.4 11.4 0 003.6.57 1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1c0 1.25.2 2.45.57 3.57a1 1 0 01-.25 1z"/></svg>'
BILL = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/></svg>'
PLAY = '<svg viewBox="0 0 14 16" width="11" height="12" aria-hidden="true"><path d="M1 1.5v13a1 1 0 001.5.86l11-6.5a1 1 0 000-1.72l-11-6.5A1 1 0 001 1.5z" fill="currentColor"/></svg>'
BOOK = '<svg viewBox="0 0 60 76" width="20" height="25" aria-hidden="true"><rect x="2" y="2" width="56" height="72" rx="7" fill="#fff"/><path d="M24 18h12v10h10v12H36v10H24V40H14V28h10z" fill="#D81F26"/></svg>'
LOCK = '<svg viewBox="0 0 16 18" width="14" height="16" aria-hidden="true"><rect x="2" y="8" width="12" height="9" rx="2" fill="currentColor"/><path d="M4.5 8V5.5a3.5 3.5 0 017 0V8" fill="none" stroke="currentColor" stroke-width="2.2"/></svg>'

# ---------- markup ----------
# Shai pill: status under the name (weather · lifts) and a play badge
rep('<span id="wxPillTxt">Today</span></small></span></button>',
    '<span id="wxPillTxt">Today</span><span id="wxLiftTxt"></span></small></span><span class="gplay" aria-hidden="true">' + PLAY + '</span></button>')
# the Slopes & lifts pill retires (Shai's hub has it); kept in the page, hidden, so old links don't break
rep('<button class="tpill" id="liftsPill" type="button"', '<button class="tpill" id="liftsPill" hidden type="button"')
# the brief becomes Shai's hub
a = s.index('<div class="gsheet" id="briefSheet"'); b = s.index('<div class="gsheet light" id="askSheet"')
s = s[:a] + f'''<div class="sheet hub" id="briefSheet" hidden><div class="sheetin hubin" role="dialog" aria-label="Shai">
  <div class="hubhead"><span class="hubface">{SH}</span><div class="hubmeta"><span class="eyebrow" id="bEyebrow">MORNING BRIEF</span><div class="gbars" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div></div><button class="xbtn" id="bClose" type="button" aria-label="Close">✕</button></div>
  <p class="gcap" id="bCap" aria-live="polite"></p>
  <div class="gwear" id="bWear" hidden></div>
  <button class="hubagain" id="bPause" type="button" hidden><span>{PLAY}</span>Play again</button>
  <div class="hubgrid">
    <button class="htile go" id="bGo" type="button"><i class="hic">{SKI}</i><b id="bGoTxt">Start skiing</b><small id="bGoSub"></small></button>
    <button class="htile" id="bToday" type="button"><span class="hbig" id="bTemp">--</span><b>Weather &amp; lifts</b><small><i class="ldot" id="bLiftDot"></i><span id="bLiftSub">Tap to check</span></small></button>
    <a class="htile" id="hubCall" href="#"><i class="hic call">{PHONE}</i><b>Call the crew</b><small id="hubCallSub">WhatsApp group</small></a>
    <a class="htile" id="hubSplit" href="#"><i class="hic split">{BILL}</i><b>Splitwise</b><small id="hubSplitSub">Trip expenses</small></a>
  </div>
  <div class="gchips" id="bChips" hidden></div>
</div></div>

''' + s[b:]
# call + Splitwise leave the crew sheet (they live in Shai's hub now)
s, n = re.subn(r'\s*<div class="linkrow"><a class="btn primary callbtn" id="pickCall".*?</div>(?=\s*<div class="picklist")', '', s, count=1, flags=re.S)
assert n == 1
# Swiss days: a passport button above Start skiing
rep('<button class="btn primary" id="goBtn" type="button">Start skiing</button>',
    '<button class="btn passbtn" id="passBtn" type="button" hidden><span class="pbk">' + BOOK + '</span>Passport check</button>\n      <button class="btn primary" id="goBtn" type="button"><span class="glock" aria-hidden="true">' + LOCK + '</span><span id="goTxt">Start skiing</span></button>')
# after the slide: Start skiing right there
rep('<button class="btn primary" id="passOk" type="button">Done</button>',
    '<button class="btn primary" id="passGo" type="button">' + SKI + 'Start skiing</button>\n  <button class="btn ghost" id="passOk" type="button">Done</button>')

# ---------- script ----------
# the Start button keeps its lock icon: set the label, not the whole button
s = s.replace("$('goBtn').textContent='Stop';", "goLabel('Stop');").replace("$('goBtn').textContent='Start skiing';", "goLabel('Start skiing');").replace("$('goBtn').textContent='Stop test';", "goLabel('Stop test');")
rep("function stopGPS(){", "function goLabel(t){ const x=$('goTxt'); if(x) x.textContent=t; else $('goBtn').textContent=t; renderPassGate(); }\nfunction stopGPS(){")
# Start skiing: on a Swiss day the passport comes first
rep("else { playSfx('start'); startGPS(); showPass('start'); } };",
    "else { if(passLocked()){ showPass('start'); return; } playSfx('start'); startGPS(); } };\n"
    "/* Swiss days: Start skiing waits for that day's passport slide */\n"
    "function passLocked(){ try{ return mode==='off' && daySwiss() && !games.pass[passKey()]; }catch(e){ return false; } }\n"
    "function renderPassGate(){ const l=passLocked(); const pb=$('passBtn'); if(pb) pb.hidden=!l; $('goBtn').classList.toggle('locked', l); $('goBtn').setAttribute('aria-label', l ? 'Start skiing (passport check first)' : ($('goTxt')?$('goTxt').textContent:'Start skiing')); }\n"
    "$('passBtn').onclick=()=>showPass('start');")
rep("view='nav'; applyView(); renderDayBar(); renderStats(); renderStep();", "view='nav'; applyView(); renderDayBar(); renderStats(); renderStep(); renderPassGate();")
rep("$('passOk').onclick=()=>{ $('passDoneSheet').hidden=true; };",
    "$('passOk').onclick=()=>{ $('passDoneSheet').hidden=true; renderPassGate(); };\n"
    "$('passGo').onclick=()=>{ $('passDoneSheet').hidden=true; renderPassGate(); if(mode==='off'){ playSfx('start'); startGPS(); } };")
rep("renderPassList(k); $('passDoneSheet').hidden=false; }", "renderPassList(k); $('passGo').hidden = mode!=='off'; $('passDoneSheet').hidden=false; renderPassGate(); renderMenu(); }")
# the menu: Swiss days get a flag and their passport check
rep("    b.querySelector('.dt b').textContent=d.title;\n",
    "    const sw=/^Switzerland/i.test(d.title); b.querySelector('.dt b').textContent=sw ? d.title.replace(/^Switzerland:\\s*/i,'') : d.title;\n"
    "    if(sw){ b.classList.add('swiss'); const t=CONFIG.trip && CONFIG.trip[i]; const pk=t ? gDay(new Date(t[0],t[1],t[2])) : ''; const ok=!!(pk && typeof games!=='undefined' && games.pass[pk]); const c=document.createElement('i'); c.className='pchip'+(ok?' ok':''); c.textContent=ok?'✓ Passport':'Passport'; b.querySelector('.dt').appendChild(c); }\n")
# Swiss days are the plan's Switzerland days (3, 4, 6), not any day whose route brushes the border
rep("function daySwiss(){ try{ return steps.some(st_=>(st_.coords||[]).some(c=>gSwiss(c[0], c[1]))); }catch(e){ return false; } }",
    "function daySwiss(){ try{ return /^Switzerland/i.test(DAY.title||''); }catch(e){ return false; } }")
# Shai's hub: one tap on Shai, every time
rep("$('wxPill').onclick=()=>{ if(mode!=='off') openAsk(true); else openBrief(); };", "$('wxPill').onclick=()=>openBrief();")
rep("$('bAsk').onclick=()=>{ stopSpeak(); $('briefSheet').hidden=true; openAsk(true); };\n", "")
rep("$('bGo').onclick=()=>{ stopSpeak(); $('briefSheet').hidden=true; if(mode==='off'){ playSfx('start'); startGPS(); } };",
    "$('bGo').onclick=()=>{ stopSpeak(); $('briefSheet').hidden=true; if(mode==='off') $('goBtn').click(); else $('stepsBtn').click(); };\n"
    "$('briefSheet').onclick=e=>{ if(e.target.id==='briefSheet'){ stopSpeak(); $('briefSheet').hidden=true; } };\n"
    "for(const [id,fn] of [['hubCall',()=>callLink()],['hubSplit',()=>splitLink()]]) $(id).addEventListener('click', e=>{ if(!fn()){ e.preventDefault(); stopSpeak(); $('briefSheet').hidden=true; openDrawer(); showGroup(true); } });")
rep("$('bToday').onclick=()=>{ stopSpeak(); $('briefSheet').hidden=true; openToday(); };",
    "$('bToday').onclick=()=>{ stopSpeak(); $('briefSheet').hidden=true; liftCheck(); };")
rep("$('bPause').onclick=()=>{ if(!speakQ){ openBrief(); return; } const p=pauseSpeak(); $('bPause').textContent=p?'▶':'❚❚'; $('bPause').setAttribute('aria-label', p?'Resume':'Pause'); };",
    "$('bPause').onclick=()=>openBrief();")
rep("cap.textContent=''; $('briefSheet').hidden=false; $('bPause').textContent='❚❚'; $('bPause').setAttribute('aria-label','Pause');",
    "cap.textContent=''; $('briefSheet').hidden=false; $('bPause').hidden=true; renderHub();")
rep("const go=()=>{ setTalking(false); if($('briefSheet').hidden) return; showAll(); if(VOICE) speak(S, null, ()=>{ $('bPause').textContent='↻'; $('bPause').setAttribute('aria-label','Play again'); }); };",
    "const go=()=>{ setTalking(false); if($('briefSheet').hidden) return; showAll(); $('bPause').hidden=false; if(VOICE) speak(S, null, ()=>{}); };")
rep("function openBrief(auto){",
    "function renderHub(){\n"
    "  const on=mode!=='off'; $('bGoTxt').textContent = on ? 'Steps' : 'Start skiing';\n"
    "  $('bGoSub').textContent = on ? 'Where next' : (passLocked() ? 'Passport first 🇨🇭' : DAY.title.replace(/^Switzerland:\\s*/i,'')+' · '+(units==='imp' ? (DAY.km*0.6214).toFixed(0)+' mi' : Math.round(DAY.km)+' km'));\n"
    "  $('bTemp').textContent = (typeof wx!=='undefined' && wx) ? tUnit(wx.now.temperature_2m) : '--';\n"
    "  $('bLiftSub').textContent = ($('wxLiftTxt').textContent||'').replace(/^ · /,'') || 'Tap to check'; $('bLiftDot').className=$('wxLiftDot').className; $('bLiftDot').hidden=$('wxLiftDot').hidden;\n"
    "  const c=callLink(), sp=splitLink(); $('hubCall').classList.toggle('off', !c); $('hubSplit').classList.toggle('off', !sp);\n"
    "  $('hubCallSub').textContent = c ? 'WhatsApp group' : 'Add the link in Group'; $('hubSplitSub').textContent = sp ? 'Trip expenses' : 'Add the link in Group';\n"
    "}\n"
    "function openBrief(auto){")
# hub links follow the same rules as the old buttons (new tab on the web, WhatsApp straight from the app)
rep("for(const id of ['gCall','pickCall']){ const a=$(id); if(!a) continue; a.hidden=!u; a.href=u||'#';", "for(const id of ['gCall','hubCall']){ const a=$(id); if(!a) continue; a.hidden=id==='gCall' && !u; a.href=u||'#';")
rep("for(const id of ['gSplit','pickSplit']){ const a=$(id); if(!a) continue; a.hidden=!u; a.href=u||'#';",
    "for(const id of ['gSplit','hubSplit']){ const a=$(id); if(!a) continue; a.hidden=id==='gSplit' && !u; a.href=u||'#';")
# Shai's pill: just the temperature and the lift word, so it fits
rep("$('wxPillTxt').textContent = tUnit(n.temperature_2m)+' '+(cond.split(' ').pop()||'').toLowerCase();", "$('wxPillTxt').textContent = tUnit(n.temperature_2m);")
# lift status under Shai's name
rep("if(!liftStat){ dot.hidden=true; $('liftsPillTxt').textContent='& lifts';", "if(!liftStat){ dot.hidden=true; $('wxLiftTxt').textContent=''; $('liftsPillTxt').textContent='& lifts';")
rep("if(off){ dot.classList.add('off'); $('liftsPillTxt').textContent='& lifts'; }\n  else if(closed.length){ dot.classList.add('part'); $('liftsPillTxt').textContent=closed.length+' shut'; }\n  else { dot.classList.add('ok'); $('liftsPillTxt').textContent='& lifts'; }",
    "if(off){ dot.classList.add('off'); $('liftsPillTxt').textContent='& lifts'; $('wxLiftTxt').textContent=' · lifts shut'; }\n  else if(closed.length){ dot.classList.add('part'); $('liftsPillTxt').textContent=closed.length+' shut'; $('wxLiftTxt').textContent=' · '+closed.length+' shut'; }\n  else { dot.classList.add('ok'); $('liftsPillTxt').textContent='& lifts'; $('wxLiftTxt').textContent=' · all open'; }")
# the floating panels: the map runs under them, and the map keeps the route clear of them
rep("function fitMapBtns(){",
    "function glassInsets(){ const A=document.querySelector('.app'); if(!A) return; const tr=A.classList.contains('tracking') && !A.classList.contains('prog-view');\n"
    "  const top=tr ? $('navPanel').parentElement.querySelector('.top') : null, bot=[$('navPanel'),$('progPanel')].find(x=>x && !x.hidden), H=A.clientHeight;\n"
    "  const t = top ? Math.round(top.getBoundingClientRect().bottom) : 0, b = bot ? Math.round(H - bot.getBoundingClientRect().top) : 0;\n"
    "  A.style.setProperty('--topovl', t+'px'); A.style.setProperty('--botovl', b+'px'); fitMapBtns();\n"
    "  try{ if(typeof map!=='undefined' && map.setPadding){ const cur=map.getPadding(); if(cur.top!==t || cur.bottom!==b){ if(map.isMoving()){ if(!glassInsets.wait){ glassInsets.wait=true; map.once('moveend', ()=>{ glassInsets.wait=false; glassInsets(); }); } } else map.setPadding({top:t, bottom:b, left:0, right:0}); } } }catch(e){} }\n"
    "try{ const ro=new ResizeObserver(()=>glassInsets()); ['navPanel','progPanel'].forEach(id=>$(id) && ro.observe($(id))); const tp=document.querySelector('.app .top'); tp && ro.observe(tp); ro.observe(document.querySelector('.app')); }catch(e){}\n"
    "new MutationObserver(()=>glassInsets()).observe(document.querySelector('.app'), {attributes:true, attributeFilter:['class']});\n"
    "function fitMapBtns(){")
rep("function fitMapBtns(){ const w=document.querySelector('.mapwrap'), b=document.querySelector('.mapbtns'); if(!w||!b) return; w.classList.remove('short'); if(b.offsetHeight + 24 > w.clientHeight) w.classList.add('short'); }",
    "function fitMapBtns(){ const w=document.querySelector('.mapwrap'), b=document.querySelector('.mapbtns'), A=document.querySelector('.app'); if(!w||!b) return; w.classList.remove('short'); const cs=getComputedStyle(A), room=w.clientHeight - (parseFloat(cs.getPropertyValue('--topovl'))||0) - (parseFloat(cs.getPropertyValue('--botovl'))||0) - 90; if(b.offsetHeight > room) w.classList.add('short'); }")
rep("function setTalking(on){ ['briefSheet','askSheet','onb'].forEach(", "function setTalking(on){ ['briefSheet','askSheet','onb'].forEach(")

# the tour's brief step points at the hub
rep("say:()=>'Brief at '+bset().time+'. Then Start skiing, phone in pocket. I’ll do the talking.',\n    html:()=>'<b>Brief</b> at '+esc(bset().time)+'. Then <b>Start skiing</b> and put the phone away.' },",
    "say:()=>'Tap me for the brief, weather, lifts and the crew call. Then Start skiing, phone in pocket.',\n    html:()=>'<b>Tap me</b>: brief, weather, lifts, call the crew. Then <b>Start skiing</b> and put the phone away.' },")
# ---------- style ----------
CSS = r'''
/* ===== liquid glass: frosted panels over the map (iPhone + Android, same page) ===== */
:root{--glass:rgb(255 255 255/.6);--glass-2:rgb(255 255 255/.76);--glass-in:rgb(255 255 255/.55);--glass-brd:rgb(255 255 255/.75);--glass-hi:rgb(255 255 255/.95);--glass-sh:0 10px 30px rgb(11 22 32/.18);--glass-blur:blur(22px) saturate(180%);--glass-dim:rgb(11 22 32/.16);--pri:#0d1b26;--pri-ink:#fff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--glass:rgb(24 34 44/.6);--glass-2:rgb(20 30 40/.78);--glass-in:rgb(255 255 255/.08);--glass-brd:rgb(255 255 255/.14);--glass-hi:rgb(255 255 255/.2);--glass-sh:0 10px 30px rgb(0 0 0/.45);--glass-dim:rgb(0 0 0/.3);--pri:#eaf1f6;--pri-ink:#0d1b26}}
:root[data-theme="dark"]{--glass:rgb(24 34 44/.6);--glass-2:rgb(20 30 40/.78);--glass-in:rgb(255 255 255/.08);--glass-brd:rgb(255 255 255/.14);--glass-hi:rgb(255 255 255/.2);--glass-sh:0 10px 30px rgb(0 0 0/.45);--glass-dim:rgb(0 0 0/.3);--pri:#eaf1f6;--pri-ink:#0d1b26}
@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){:root{--glass:color-mix(in srgb,var(--panel) 94%,transparent);--glass-2:var(--panel);--glass-in:var(--bg)}}
@media (prefers-reduced-transparency: reduce){:root{--glass:var(--panel);--glass-2:var(--panel);--glass-in:var(--bg);--glass-blur:none}}
.floatmenu,.tpill,.mapbtns,.legend,.donechip,.app .bottom,.app.tracking .top,.sheetin,.drawerin,.tbub,.offroute,.homebanner,.toast{-webkit-backdrop-filter:var(--glass-blur);backdrop-filter:var(--glass-blur)}
.floatmenu,.tpill,.mapbtns,.legend,.donechip{background:var(--glass);border:1px solid var(--glass-brd);box-shadow:var(--glass-sh),inset 0 1px 1px var(--glass-hi);color:var(--ink)}
/* the map fills the screen; the panels float on it */
.app{grid-template-rows:auto 1fr auto}
.mapwrap{grid-row:1/4;grid-column:1;margin-bottom:0}
.app .top{grid-row:1;grid-column:1;position:relative;z-index:3}
.app .bottom{grid-row:3;grid-column:1;position:relative;z-index:3}
.app{grid-template-columns:minmax(0,1fr)}
.app .bottom{margin:0 10px calc(10px + env(safe-area-inset-bottom,0px));border-radius:34px;background:var(--glass-2);border:1px solid var(--glass-brd);box-shadow:var(--glass-sh),inset 0 1px 1px var(--glass-hi);padding:18px 16px 16px}
.app .bottom::before{display:none}
.app.tracking .top{margin:calc(6px + env(safe-area-inset-top,0px)) 10px 0;border-radius:30px;background:var(--glass-2);border:1px solid var(--glass-brd);box-shadow:var(--glass-sh),inset 0 1px 1px var(--glass-hi);padding:12px 18px}
.app.tracking .floatmenu,.app.tracking .mapbtns,.app.tracking .offroute,.app.tracking .placesbox{top:calc(var(--topovl,0px) + 10px)}
.app.tracking .toppills{top:calc(var(--topovl,0px) + 10px)}
.app.tracking .donechip{top:calc(var(--topovl,0px) + 70px)}
.legend{bottom:calc(var(--botovl,0px) + 10px);border-radius:17px;padding:7px 12px}
.app:not(.tracking) .legend{left:12px}
/* map buttons: one glass column */
.mapbtns{gap:0;border-radius:26px;padding:1px;overflow:hidden;max-height:calc(100% - var(--topovl,0px) - var(--botovl,0px) - 30px)}
.mbtn{background:none;border:0;box-shadow:none;border-radius:24px;width:50px;height:50px;color:var(--ink);position:relative}
.mbtn+.mbtn::before{content:"";position:absolute;top:0;left:12px;right:12px;height:1px;background:color-mix(in srgb,var(--ink) 12%,transparent)}
.mbtn[aria-pressed="true"]{background:var(--accent);color:#fff}
.mbtn[aria-pressed="true"]::before,.mbtn[aria-pressed="true"]+.mbtn::before{display:none}
.mapwrap.short .mapbtns{gap:0}
.floatmenu{border-radius:25px}
.tpill{border-radius:25px}
/* Shai: one pill, his status under the name, play badge */
.guidepill{padding:0 6px 0 4px;gap:9px;min-width:0;flex:1 1 auto;max-width:250px;justify-content:flex-start}
.guidepill .gtxt{flex:1}
.gtxt small span{white-space:nowrap}
.gplay{width:30px;height:30px;border-radius:15px;background:var(--pri);color:var(--pri-ink);display:grid;place-items:center;flex:none;margin-left:2px}
.gplay svg{margin-left:2px}
.app.tracking .guidepill .gplay{display:none}
.app.tracking .guidepill{flex:none;width:50px;max-width:50px;padding:0;justify-content:center}
.hubin{max-height:calc(100% - 30px - env(safe-area-inset-top,0px))}
@media (max-height:720px){.hubface{width:54px;height:54px}.hub .gcap{font-size:1rem}.htile{min-height:96px;padding:12px;border-radius:22px}.hic{width:34px;height:34px}.hic svg{width:18px;height:18px}.hbig{font-size:1.6rem}.hub .gwear{display:none}}
/* join flow and first-open tour */
.jsheet{background:var(--glass-2);-webkit-backdrop-filter:var(--glass-blur);backdrop-filter:var(--glass-blur);border-top:1px solid var(--glass-brd);border-radius:32px 32px 0 0}
.jhero{background:radial-gradient(circle at 70% 20%,rgb(255 255 255/.18),transparent 50%),linear-gradient(#4d6f8c,#2e4a63)}
.jcolors button[aria-pressed="true"]{box-shadow:0 0 0 3px var(--panel),0 0 0 6px var(--ink)}
.jchecks{background:var(--glass-in);border:1px solid var(--glass-brd)}
.tbub{border-radius:28px;box-shadow:var(--glass-sh),inset 0 1px 1px var(--glass-hi)}
.tchips span{background:var(--glass-in);border:1px solid var(--glass-brd)}
.tring{border-radius:28px}
.app.tracking .guidepill .gmic{display:none}
.guidepill.fresh .gplay{background:#ff8a3d;color:#0b1620}
/* buttons */
.btn{border-radius:999px}
.btn.ghost{background:var(--glass-in);border:1px solid var(--glass-brd);box-shadow:inset 0 1px 1px var(--glass-hi)}
.btn.primary{box-shadow:0 8px 20px color-mix(in srgb,var(--accent) 30%,transparent),inset 0 1px 0 rgb(255 255 255/.2)}
.app:not(.tracking) #goBtn{border-radius:999px;background:linear-gradient(180deg,color-mix(in srgb,var(--pri) 88%,#fff),var(--pri));color:var(--pri-ink);box-shadow:0 8px 20px rgb(11 22 32/.3),inset 0 1px 0 rgb(255 255 255/.18);display:flex;align-items:center;justify-content:center;gap:10px}
.glock{display:none}
#goBtn.locked{background:color-mix(in srgb,var(--ink) 8%,transparent)!important;color:var(--muted)!important;box-shadow:none!important;min-height:52px!important;font-size:1.06rem!important}
#goBtn.locked .glock{display:inline-flex}
.passbtn{grid-column:1/-1;min-height:62px;display:flex;align-items:center;justify-content:center;gap:12px;background:linear-gradient(180deg,#E42A31,#C4141B);color:#fff;font-weight:800;font-size:1.2rem;box-shadow:0 8px 20px rgb(216 31 38/.35),inset 0 1px 0 rgb(255 255 255/.25)}
.passbtn[hidden]{display:none}
.pbk{display:inline-flex}
.skip button{border-radius:28px;background:var(--glass-in);border:1px solid var(--glass-brd)}
.badge{border-radius:16px}
.xbtn{background:var(--glass-in);border:1px solid var(--glass-brd)}
/* sheets: glass cards floating up from the bottom */
.sheet{background:var(--glass-dim)}
.sheetin{width:calc(100% - 16px);margin:0 8px calc(8px + env(safe-area-inset-bottom,0px));border-radius:36px;background:var(--glass-2);border:1px solid var(--glass-brd);box-shadow:var(--glass-sh),inset 0 1px 1px var(--glass-hi);padding:22px 18px 18px}
.drawer{background:var(--glass-dim)}
.drawerin{width:calc(100% - 16px);margin:0 8px calc(8px + env(safe-area-inset-bottom,0px));border-radius:36px;background:var(--glass-2);border:1px solid var(--glass-brd);box-shadow:var(--glass-sh),inset 0 1px 1px var(--glass-hi)}
.tcard,.rtile,.rgoal,.picklist,.group,.goalcard,.gcard,.gtoggle,.gchips div,.gcode{background:var(--glass-in)!important;border:1px solid var(--glass-brd);box-shadow:inset 0 1px 1px var(--glass-hi);border-radius:22px}
.group{overflow:hidden}
.seg{background:color-mix(in srgb,var(--ink) 8%,transparent);border-radius:14px}
.seg button{border-radius:11px}
.ginput{background:var(--glass-in);border-color:var(--glass-brd)}
.tbub{background:var(--glass-2);border:1px solid var(--glass-brd)}
.ttail{background:var(--glass-2)}
/* menu: Swiss days and their passport */
.daycard.swiss .dt b::before{content:"";display:inline-block;width:15px;height:15px;border-radius:4px;margin-right:6px;vertical-align:-2px;background:#D81F26 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'%3E%3Cpath d='M4 1.5h2v2.5h2.5v2H6v2.5H4V6H1.5V4H4z' fill='white'/%3E%3C/svg%3E") center/11px no-repeat}
.pchip{display:inline-flex;align-items:center;height:22px;padding:0 9px;border-radius:11px;font:700 .75rem var(--f-ui);font-style:normal;background:rgb(216 31 38/.12);color:#B3161C;margin-top:4px;width:max-content}
.pchip.ok{background:rgb(22 163 74/.15);color:#15803d}
.dt{display:flex;flex-direction:column;align-items:flex-start}
/* Shai's hub */
.hubin{gap:10px}
.hubhead{display:flex;align-items:center;gap:14px}
.hubface{width:70px;height:70px;border-radius:50%;overflow:hidden;flex:none;box-shadow:0 0 0 3px var(--glass-brd),0 4px 14px rgb(11 22 32/.18);transition:box-shadow .2s}
.hub.talking .hubface{box-shadow:0 0 0 3px #0a84ff,0 0 0 9px rgb(10 132 255/.25)}
.hubmeta{flex:1;display:grid;gap:6px;min-width:0}
.hub .gbars{opacity:0;height:22px}
.hub.talking .gbars{opacity:1}
.hub .gbars i{background:#0a84ff}
.hub .gcap{margin:2px 2px 0;font-size:1.12rem;line-height:1.4;text-align:left;min-height:0;color:var(--ink)}
.hub .gcap:empty{min-height:3.6em}
.hub .gcap span{opacity:.72}
.hub .gwear{border-radius:16px;background:rgb(255 244 234/.8)}
.hubagain{align-self:flex-start;display:inline-flex;align-items:center;gap:8px;border:0;background:none;color:var(--muted);font:600 .95rem var(--f-ui);padding:2px 0;min-height:36px}
.hubagain span{width:28px;height:28px;border-radius:14px;background:var(--pri);color:var(--pri-ink);display:grid;place-items:center}
.hubagain[hidden]{display:none}
.hubgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:4px}
.htile{min-height:122px;border-radius:26px;padding:14px;box-sizing:border-box;display:flex;flex-direction:column;align-items:flex-start;justify-content:space-between;gap:6px;text-align:left;text-decoration:none;font:inherit;color:var(--ink);background:var(--glass-in);border:1px solid var(--glass-brd);box-shadow:inset 0 1px 1px var(--glass-hi)}
.htile b{font-weight:800;font-size:1.08rem;line-height:1.15}
.htile small{display:flex;align-items:center;gap:5px;font-size:.85rem;color:var(--muted);line-height:1.2}
.htile.go{background:linear-gradient(180deg,color-mix(in srgb,var(--pri) 88%,#fff),var(--pri));color:var(--pri-ink);border-color:transparent;box-shadow:0 8px 20px rgb(11 22 32/.28)}
.htile.go small{color:inherit;opacity:.75}
.hic{width:42px;height:42px;border-radius:21px;display:grid;place-items:center;font-style:normal;background:rgb(255 255 255/.16)}
.hic.call{background:#25A35A}.hic.split{background:#1AA39A}
.htile.off .hic{filter:grayscale(1);opacity:.5}
.hbig{font:800 2rem/1 var(--f-num)}
/* full-screen moments: glass over a blurred map */
.pfull,.gzfull{background:radial-gradient(circle at 50% 20%,rgb(216 31 38/.28),transparent 55%),rgb(11 22 32/.72);-webkit-backdrop-filter:blur(18px) saturate(140%);backdrop-filter:blur(18px) saturate(140%)}
.gzfull{background:radial-gradient(circle at 50% 22%,rgb(255 138 61/.4),transparent 55%),rgb(11 22 32/.7)}
#kingSheet{background:radial-gradient(circle at 50% 30%,rgb(255 194 26/.35),transparent 55%),rgb(11 22 32/.72)}
.gzcard{background:rgb(255 255 255/.8);-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px);border:1px solid rgb(255 255 255/.7);border-radius:30px}
.gzghost{background:rgb(255 255 255/.16);border:1px solid rgb(255 255 255/.3)}
.ptrack{background:rgb(255 255 255/.14);border-color:rgb(255 255 255/.3)}
.pknob{background:#fff;color:#D81F26;box-shadow:0 4px 14px rgb(0 0 0/.3)}
.peb{color:#FFB4B4}
#passGo{display:flex;align-items:center;justify-content:center;gap:10px;background:linear-gradient(180deg,color-mix(in srgb,var(--pri) 88%,#fff),var(--pri));color:var(--pri-ink)}
#passGo[hidden]{display:none}
/* Sun mode: solid, black on white, no glass */
.app.sun .floatmenu,.app.sun .tpill,.app.sun .mapbtns,.app.sun .legend,.app.sun .bottom,.app.sun.tracking .top{-webkit-backdrop-filter:none;backdrop-filter:none;background:#fff;border:2px solid #000;box-shadow:0 4px 14px rgb(0 0 0/.25)}
.app.sun.tracking .top{background:#000;color:#fff}
.app.sun .mbtn{border:0}
.app.sun .btn.ghost{background:#fff;border:2px solid #000}
'''
i = s.index('<style>\n/* Layout: one-screen instrument.'); j = s.index('</style>', i)
s = s[:j] + CSS + s[j:]
open(p, 'w', encoding='utf-8').write(s)
print('glass patch applied')
