"""The guide (Oct 8): morning brief by voice, Ask by voice, first-open setup.
- Top row: the Today pill becomes the guide (face + "Brief" + weather). Orange ring until today's brief is heard.
  While tracking it's just the face: tap to ask.
- Brief: a script with blanks filled from the plan, weather, lifts and crew + a persona line per day from brief.json
  (on the website, editable without an app update; cached on the phone). Spoken by the iPhone voice (native) or the
  browser voice (web). Captions follow; key numbers stay on screen.
- Ask: hold/tap, speak, fixed phrases do things in the app (where's X, what's next, lifts closed, plan from here,
  lunch, call the group, split costs, stats, weather, start/stop, brief). Anything else goes to Apple's on-phone
  model when the iPhone has it.
- First open: welcome, location, morning brief (8:30, on by default, iPhone voice).
- Settings: one row "Morning brief" opens time / voice / on-off / play now.
Usage: python3 tools/guide_patch.py index.html nyc.html"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def rep(s, old, new, count=1):
    n = s.count(old); assert n == count, (old[:90], n); return s.replace(old, new)

FACE = ('<svg class="gface" viewBox="14 14 92 100" aria-hidden="true"><circle cx="60" cy="64" r="44" fill="#fff" stroke="#d6e0e8" stroke-width="3"/>'
        '<rect x="30" y="30" width="60" height="20" rx="10" fill="#ff8a3d" stroke="#0b1620" stroke-width="4"/>'
        '<circle cx="47" cy="60" r="5" fill="#2b3640"/><circle cx="73" cy="60" r="5" fill="#2b3640"/>'
        '<circle cx="38" cy="72" r="5" fill="#ffc9c9" opacity=".8"/><circle cx="82" cy="72" r="5" fill="#ffc9c9" opacity=".8"/>'
        '<path class="gm-smile" d="M48 76 Q60 88 72 76" fill="none" stroke="#2b3640" stroke-width="4" stroke-linecap="round"/>'
        '<ellipse class="gm-talk" cx="60" cy="80" rx="10" ry="7" fill="#7a1f2b"/>'
        '<ellipse class="gm-o" cx="60" cy="80" rx="5" ry="4.5" fill="#2b3640"/>'
        '<path d="M28 98 Q60 114 92 98 L94 108 Q60 124 26 108 Z" fill="#d81f26"/></svg>')

PILL_OLD = '<button class="tpill" id="wxPill" type="button" aria-label="Today: weather, what to wear and lifts"><i class="ldot" id="wxLiftDot" hidden></i><span id="wxPillTxt">Today</span></button>'
PILL_NEW = ('<button class="tpill guidepill" id="wxPill" type="button" aria-label="Today\'s brief: the day, weather, what to wear and lifts">'
            '<span class="gpface">' + FACE + '<i class="gmic" aria-hidden="true"></i></span>'
            '<span class="gtxt"><b>Brief</b><small><i class="ldot" id="wxLiftDot" hidden></i><span id="wxPillTxt">Today</span></small></span></button>')

HTML = """
<div class="gsheet" id="briefSheet" hidden role="dialog" aria-label="Morning brief">
  <div class="gtop"><span id="bEyebrow">MORNING BRIEF</span><button class="xbtn gx" id="bClose" type="button" aria-label="Close">✕</button></div>
  <div class="gstage"><div class="gbig" id="bFace">%FACE%</div><div class="gbars" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div></div>
  <p class="gcap" id="bCap" aria-live="polite"></p>
  <div class="gbottom">
    <div class="gchips" id="bChips"></div>
    <div class="gwear" id="bWear" hidden></div>
    <div class="gbtns"><button class="btn ghost" id="bPause" type="button" aria-label="Pause">❚❚</button><button class="btn ghost" id="bAsk" type="button">Ask</button><button class="btn primary" id="bGo" type="button">Start skiing</button></div>
    <button class="btn ghost sm" id="bToday" type="button">Weather and lifts in detail</button>
  </div>
</div>

<div class="gsheet light" id="askSheet" hidden role="dialog" aria-label="Ask the guide">
  <div class="gtop"><span class="ahead"><span class="gmid" id="aFace">%FACE%</span><span><b id="aState">Ask me anything about today</b><small id="aSub">Works on your phone, no signal needed</small></span></span><button class="xbtn" id="aClose" type="button" aria-label="Close">✕</button></div>
  <div class="aconvo" id="aConvo"></div>
  <div class="abottom">
    <span class="eyebrow">Try</span>
    <div class="asugs" id="aSugs"></div>
    <button class="ahold" id="aHold" type="button"><span class="gmicbig" aria-hidden="true"></span><span id="aHoldTxt">Tap and talk</span></button>
  </div>
</div>

<div class="sheet" id="briefSet" hidden>
  <div class="sheetin" role="dialog" aria-label="Morning brief settings">
    <div class="sheethead"><h3>Morning brief</h3><button class="btn ghost sm" id="bsDone" type="button">Done</button></div>
    <button class="grow toggle" id="bsOn" type="button" role="switch" aria-pressed="true"><span>Every trip morning<small>A notification; tap it to hear the brief</small></span><span class="sw"></span></button>
    <label class="grow"><span>Time</span><input class="tinput" id="bsTime" type="time" value="08:30"></label>
    <div class="grow col"><span>Voice</span><div class="seg" id="bsVoice"><button type="button" data-v="default" aria-pressed="true">iPhone voice</button><button type="button" data-v="personal" aria-pressed="false">My voice</button></div></div>
    <p class="note" id="bsVoiceNote" style="margin:0" hidden>“My voice” uses Personal Voice. Make it once in iPhone Settings › Accessibility › Personal Voice (about 15 minutes), then allow Ski Nav to use it.</p>
    <button class="btn primary" id="bsPlay" type="button">Play today’s brief</button>
  </div>
</div>

<div class="onb" id="onb" hidden>
  <div class="ostep" id="o1">
    <div class="ohero"><div class="gbig">%FACE%</div><span class="oinv">Hi, I’m Snowy, your ski guide.</span><h1 id="oTitle"></h1><span class="osub" id="oSub"></span></div>
    <div class="osheet">
      <ul class="jlist"><li><b>A plan for every day</b>, runs and lifts, on a map that works offline</li><li><b>A morning brief</b>, spoken: the day, the weather, what to wear</li><li><b>Your crew on the map</b>, one tap to talk or split costs</li></ul>
      <button class="btn primary jbtn" id="o1Go" type="button">Set me up · 1 minute</button>
      <p class="jnote">3 quick steps. Change anything later in Settings.</p>
    </div>
  </div>
  <div class="ostep oplain" id="o2" hidden>
    <div class="jprog"><i class="on"></i><i></i></div>
    <h2>Track every run, phone in your pocket</h2>
    <p class="jsub">Choose “Allow While Using App”, then “Change to Always Allow” when asked, so km and runs keep counting with the phone locked.</p>
    <ul class="jchecks"><li>Only after you tap Start skiing</li><li>Only your group sees your dot</li></ul>
    <div class="jbottom jcol"><button class="btn primary jbtn" id="o2Go" type="button">Allow location</button><button class="btn ghost jbtn" id="o2Skip" type="button">Not now</button></div>
  </div>
  <div class="ostep oplain" id="o3" hidden>
    <div class="jprog"><i class="on"></i><i class="on"></i></div>
    <div class="orow"><div class="gmid">%FACE%</div><div><h2>Your morning brief</h2><p class="jsub" style="margin:0">Every trip morning, the day in 60 seconds. A different joke each day.</p></div></div>
    <div class="ocard"><b>Every trip morning at 8:30</b><small>On automatically. Change it in Settings.</small></div>
    <div class="seg" id="oVoice"><button type="button" data-v="default" aria-pressed="true">iPhone voice</button><button type="button" data-v="personal" aria-pressed="false">My voice</button></div>
    <button class="btn ghost" id="oSample" type="button">▶ Hear a sample</button>
    <div class="jbottom jcol"><button class="btn primary jbtn" id="o3Go" type="button">Sounds good</button></div>
  </div>
</div>
""".replace('%FACE%', FACE)

CSS = r"""
/* ===== the guide: pill, brief, ask, first open ===== */
.gface{display:block;width:100%;height:100%}
.gface .gm-talk,.gface .gm-o{display:none}
.talking .gface .gm-smile,.listening .gface .gm-smile{display:none}
.talking .gface .gm-talk{display:block;transform-origin:60px 80px;animation:gtalk .22s ease-in-out infinite alternate}
.listening .gface .gm-o{display:block}
@keyframes gtalk{from{transform:scaleY(.25)}to{transform:scaleY(1)}}
.guidepill{padding:0 12px 0 4px;gap:8px}
.gpface{position:relative;width:40px;height:40px;flex:none}
.gtxt{display:flex;flex-direction:column;align-items:flex-start;line-height:1.05;min-width:0}
.gtxt b{font-size:.95rem}
.gtxt small{display:flex;align-items:center;gap:5px;font:600 .78rem var(--f-ui);color:var(--muted)}
.guidepill.fresh{border:2px solid #ff8a3d;box-shadow:0 0 0 5px rgb(255 138 61/.22),0 3px 12px rgb(11 22 32/.16)}
.gmic{display:none;position:absolute;right:-5px;bottom:-5px;width:20px;height:20px;border-radius:50%;background:#ff8a3d url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230b1620' stroke-width='3' stroke-linecap='round'%3E%3Crect x='9' y='3' width='6' height='12' rx='3'/%3E%3Cpath d='M5 11a7 7 0 0 0 14 0M12 18v3'/%3E%3C/svg%3E") center/11px no-repeat;border:2px solid #fff}
.app.tracking .toppills>#wxPill.guidepill{display:flex!important}
.grow.link small{display:block;font-weight:500;color:var(--muted);font-size:.85rem;text-align:left}
.grow.link>span{text-align:left}
.app.tracking .guidepill{width:50px;padding:0;justify-content:center;border:2px solid #ff8a3d}
.app.tracking .guidepill .gtxt{display:none}
.app.tracking .guidepill .gmic{display:block}
.gsheet{position:fixed;inset:0;z-index:2600;display:flex;flex-direction:column;background:#0b1620;color:#fff;font-family:var(--f-ui)}
.gsheet[hidden]{display:none}
.gsheet.light{background:var(--bg);color:var(--ink)}
.gtop{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:calc(16px + env(safe-area-inset-top,0px)) 16px 8px 20px;font-size:.85rem;font-weight:700;letter-spacing:.06em}
.gx{background:rgb(255 255 255/.14);color:#fff}
.gstage{display:flex;flex-direction:column;align-items:center;gap:8px}
.gbig{width:150px;height:150px;border-radius:50%;box-shadow:0 0 0 4px rgb(255 138 61/.45)}
.gbars{display:flex;gap:3px;height:24px;align-items:center;opacity:0}
.talking .gbars,.gsheet.talking .gbars{opacity:1}
.gbars i{width:4px;height:6px;border-radius:2px;background:#ff8a3d;animation:gbar .5s ease-in-out infinite alternate}
.gbars i:nth-child(2n){animation-delay:.15s}.gbars i:nth-child(3n){animation-delay:.3s}
@keyframes gbar{to{height:22px}}
.gcap{margin:12px 22px 0;font-size:1.3rem;line-height:1.35;text-align:center;min-height:5.4em}
.gcap span{opacity:.5}.gcap b{opacity:1}
.gbottom{margin-top:auto;background:var(--panel);color:var(--ink);border-radius:26px 26px 0 0;padding:16px 16px calc(20px + env(safe-area-inset-bottom,0px));display:grid;gap:10px}
.gchips{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.gchips div{background:var(--bg);border-radius:14px;padding:9px 11px;display:flex;flex-direction:column;min-width:0}
.gchips b{font:700 1.45rem/1 var(--f-num)}
.gchips span{font-size:.72rem;font-weight:700;color:var(--muted);letter-spacing:.03em;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.gwear{background:#fff4ec;color:#0b1620;border-radius:14px;padding:10px 12px;font-size:.95rem}
.gbtns{display:grid;grid-template-columns:56px 1fr 1.2fr;gap:8px}
.gbtns .btn{min-height:54px}
.ahead{display:flex;align-items:center;gap:12px;letter-spacing:0;font-size:1rem;text-transform:none}
.ahead small{display:block;font-weight:500;color:var(--muted);font-size:.85rem}
.gmid{width:60px;height:60px;flex:none}
.aconvo{flex:1;overflow:auto;padding:8px 16px;display:flex;flex-direction:column;gap:10px}
.abub{max-width:85%;padding:11px 14px;border-radius:18px;font-size:1.05rem;line-height:1.35}
.abub.me{align-self:flex-end;background:var(--ink);color:var(--panel);border-bottom-right-radius:4px}
.abub.it{align-self:flex-start;background:var(--panel);border-bottom-left-radius:4px;display:grid;gap:10px}
.abub .ggrid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.abottom{padding:8px 16px calc(18px + env(safe-area-inset-bottom,0px));display:grid;gap:10px}
.asugs{display:flex;gap:8px;flex-wrap:wrap}
.asugs button{height:40px;border-radius:20px;border:1px solid var(--line);background:var(--panel);color:var(--ink);font:600 .95rem var(--f-ui);padding:0 14px}
.ahold{height:72px;border-radius:36px;border:0;background:#ff8a3d;color:#0b1620;font:800 1.15rem var(--f-ui);display:flex;align-items:center;justify-content:center;gap:10px}
.ahold.on{background:#0b1620;color:#fff;box-shadow:0 0 0 6px rgb(255 138 61/.35)}
.gmicbig{width:24px;height:24px;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230b1620' stroke-width='2.4' stroke-linecap='round'%3E%3Crect x='9' y='3' width='6' height='12' rx='3'/%3E%3Cpath d='M5 11a7 7 0 0 0 14 0M12 18v3'/%3E%3C/svg%3E") center/24px no-repeat}
.ahold.on .gmicbig{filter:invert(1)}
.tinput{height:44px;border-radius:12px;border:1px solid var(--line);background:var(--bg);color:var(--ink);font:700 1.1rem var(--f-ui);padding:0 10px}
.onb{position:fixed;inset:0;z-index:2700;background:var(--bg);display:flex;flex-direction:column}
.onb[hidden]{display:none}
.ostep{flex:1;display:flex;flex-direction:column;min-height:0}
.ostep[hidden]{display:none}
.ohero{flex:1;background:linear-gradient(#4d6f8c,#2e4a63);color:#fff;padding:calc(40px + env(safe-area-inset-top,0px)) 24px 44px;display:flex;flex-direction:column;justify-content:flex-end;gap:8px}
.ohero .gbig{width:120px;height:120px;align-self:center;margin-bottom:10px}
.ohero h1{margin:0;font:800 2.8rem/.95 var(--f-num)}
.oinv,.osub{font-size:1.02rem;opacity:.92}
.osheet{background:var(--panel);border-radius:24px 24px 0 0;margin-top:-22px;padding:22px 20px calc(22px + env(safe-area-inset-bottom,0px));display:grid;gap:12px}
.oplain{padding:calc(48px + env(safe-area-inset-top,0px)) 20px calc(22px + env(safe-area-inset-bottom,0px));gap:16px}
.oplain h2{margin:0;font:800 2.1rem/1 var(--f-num)}
.orow{display:flex;align-items:center;gap:14px}
.ocard{background:var(--panel);border-radius:16px;padding:14px 16px;display:grid;gap:2px}
.ocard small{color:var(--muted)}
.jchecks{margin:0;padding:14px 16px;background:var(--panel);border-radius:16px;display:grid;gap:8px;list-style:none}
.jchecks li{position:relative;padding-left:28px}
.jchecks li::before{content:'';position:absolute;left:0;top:1px;width:20px;height:20px;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2315803d' stroke-width='2.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 12.5l4.5 4.5L19 7.5'/%3E%3C/svg%3E") center/20px no-repeat}
"""

JS = r"""
/* ---------- the guide: morning brief + ask, spoken on the phone ---------- */
const BRIEF_URL='https://alonmaltzov.github.io/ski-nav/brief.json', BKEY='skinav-brief', ONB='skinav-onb';
const BRIEF_FALLBACK=__BRIEF__;
let briefScript=(()=>{ try{ return JSON.parse(localStorage.getItem(BKEY)||'null'); }catch(e){ return null; } })() || BRIEF_FALLBACK;
fetch(BRIEF_URL+'?t='+Math.floor(Date.now()/36e5), {cache:'no-cache'}).then(r=>r.ok?r.json():null).then(j=>{ if(j && j.days){ briefScript=j; try{ localStorage.setItem(BKEY, JSON.stringify(j)); }catch(e){} } }).catch(()=>{});
const bset = () => store.brief || (store.brief={on:true, time:'08:30', voice:'default'});
const todayStr = () => { const n=new Date(); return n.getFullYear()+'-'+(n.getMonth()+1)+'-'+n.getDate(); };
const heardToday = () => store.briefHeard===todayStr();
const sayNum = v => (v<0?'minus ':'')+Math.abs(Math.round(v));
function briefFacts(){
  const me = (typeof grp!=='undefined' && grp && grp.name ? grp.name.split(' ')[0] : '');
  const km = units==='imp' ? (DAY.km*0.6214).toFixed(1)+' miles' : Math.round(DAY.km)+' kilometers';
  const f = { me, title:DAY.title.replace(/\s*\+\s*/g,' and '), km, lifts:String(DAY.lifts), first:(steps[0]&&steps[0].at)||'', end:(CONFIG.flat && DAY.end && DAY.end.name) ? DAY.end.name : (CONFIG.endName||''), endTime:DAY.arrive||'',
    lunch: DAY.lunch!=null && steps[DAY.lunch+1] ? (steps[DAY.lunch+1].at||'') : '', weather:'', wear:'', crew:'', closed:0 };
  if(typeof wx!=='undefined' && wx){ const cond=(WX_CODES[wx.now.weather_code]||'').toLowerCase(); f.weather = sayNum(wx.now.temperature_2m)+' degrees'+(cond?' and '+cond:''); const w=wearFor(wx); f.wear = w[0] ? w[0].charAt(0).toLowerCase()+w[0].slice(1) : ''; }
  try{ if(typeof planLifts==='function' && typeof liftStatusOf==='function' && resortRunning()) f.closed = planLifts().filter(x=>liftStatusOf(x.bi) && liftStatusOf(x.bi)!=='open').length; }catch(e){}
  if(typeof gstate!=='undefined' && gstate && grp){ const n=gstate.members.filter(m=>m.id!==grp.member_id).length; if(n) f.crew = n+(n===1?' friend':' friends')+' in the group'; }
  return f;
}
function persona(){ const d=briefScript.days||{}; return (CONFIG.flat ? d.practice : d[String(DAY.day)]) || d.practice || {}; }
const fill = (t,f) => String(t||'').replace(/\{(\w+)\}/g, (m,k)=>f[k]!=null ? f[k] : '').replace(/\s+([!.,?])/g,'$1').replace(/\s{2,}/g,' ');
function buildBrief(){
  const f=briefFacts(), p=persona(), S=[];
  S.push(fill(p.open || 'Morning {me}.', f));
  S.push(fill('What are we doing today? We’re skiing {title}: {km} and {lifts} lifts.', f).replace(' and 1 lifts',' and 1 lift'));
  if(f.first) S.push('First move at '+f.first+'.');
  if(f.weather) S.push('It’s '+f.weather+(f.wear ? ', so '+f.wear+'.' : '.'));
  if(f.closed) S.push(f.closed+(f.closed===1?' lift on our plan is':' lifts on our plan are')+' closed right now. Tap Plan from here when you get there.');
  if(f.lunch) S.push('Sandwich stop around '+f.lunch+'.');
  if(f.end && f.endTime) S.push(f.end+' at '+f.endTime+'.');
  if(f.crew) S.push(f.crew.charAt(0).toUpperCase()+f.crew.slice(1)+' today.');
  if(p.joke) S.push(fill(p.joke, f));
  S.push(fill(p.close || 'Have fun out there.', f));
  return {S, f};
}
/* voice: the iPhone speaks natively (AVSpeechSynthesizer, Personal Voice if chosen); the web uses the browser voice */
let speakQ=null, speakIdx=-1, speakPaused=false;
function speak(parts, onPart, onDone){
  stopSpeak(); speakQ={parts, onPart, onDone}; setTalking(true);
  if(NATIVE){ toNative({cmd:'speak', parts, voice:bset().voice}); return; }
  if(!('speechSynthesis' in window)){ parts.forEach((_,i)=>onPart&&onPart(i)); setTalking(false); onDone&&onDone(); return; }
  parts.forEach((t,i)=>{ const u=new SpeechSynthesisUtterance(t); u.rate=1.02; u.onstart=()=>{ speakIdx=i; onPart&&onPart(i); }; if(i===parts.length-1) u.onend=()=>{ setTalking(false); speakQ=null; onDone&&onDone(); }; speechSynthesis.speak(u); });
}
function stopSpeak(){ if(NATIVE) toNative({cmd:'speak', stop:true}); else if('speechSynthesis' in window) speechSynthesis.cancel(); speakQ=null; speakPaused=false; setTalking(false); }
function pauseSpeak(){ if(!speakQ) return false; speakPaused=!speakPaused; if(NATIVE) toNative({cmd:'speak', pause:speakPaused}); else if(speakPaused) speechSynthesis.pause(); else speechSynthesis.resume(); setTalking(!speakPaused); return speakPaused; }
function setTalking(on){ ['briefSheet','askSheet'].forEach(id=>$(id).classList.toggle('talking', !!on)); }
/* events from the iPhone: {type:'part', i} {type:'done'} {type:'heard', text, final} {type:'listening', on} {type:'thought', text}  */
window.__guide = { on(e){
  if(e.type==='part' && speakQ){ speakIdx=e.i; speakQ.onPart && speakQ.onPart(e.i); }
  else if(e.type==='done' && speakQ){ const d=speakQ.onDone; speakQ=null; setTalking(false); d && d(); }
  else if(e.type==='heard') onHeard(e.text||'', !!e.final);
  else if(e.type==='listening'){ setListening(!!e.on); if(!e.on && pendingHeard && !heardFinal) onHeard(pendingHeard, true); }
  else if(e.type==='thought') onThought(e);
  else if(e.type==='error') { setListening(false); if(e.msg) aSay(e.msg); }
} };

/* ---- brief sheet ---- */
function openBrief(auto){
  closeDrawer(); $('askSheet').hidden=true;
  const {S, f}=buildBrief();
  $('bEyebrow').textContent=(DAY.date ? DAY.date.toUpperCase()+' · ' : '')+'MORNING BRIEF';
  const ch=$('bChips'); ch.textContent='';
  const chip=(b,s)=>{ const d=document.createElement('div'); const x=document.createElement('b'); x.textContent=b; const y=document.createElement('span'); y.textContent=s; d.append(x,y); ch.appendChild(d); };
  chip(units==='imp' ? (DAY.km*0.6214).toFixed(1)+' mi' : Math.round(DAY.km)+' km', DAY.lifts+(DAY.lifts===1?' lift':' lifts'));
  chip(f.first||'-', 'First move');
  chip(typeof wx!=='undefined' && wx ? tUnit(wx.now.temperature_2m) : '-', typeof wx!=='undefined' && wx ? (WX_CODES[wx.now.weather_code]||'') : 'No weather yet');
  $('bWear').hidden=!f.wear; $('bWear').innerHTML='<b>Wear:</b> '; $('bWear').append(f.wear);
  const cap=$('bCap'); const show=i=>{ cap.textContent=''; S.forEach((t,k)=>{ if(k<i-1 || k>i+1) return; const el=document.createElement(k===i?'b':'span'); el.textContent=t+' '; cap.appendChild(el); }); };
  show(0); $('briefSheet').hidden=false; $('bPause').textContent='❚❚'; $('bPause').setAttribute('aria-label','Pause');
  store.briefHeard=todayStr(); persist(); renderGuidePill();
  speak(S, show, ()=>{ $('bPause').textContent='↻'; $('bPause').setAttribute('aria-label','Play again'); });
}
$('bClose').onclick=()=>{ stopSpeak(); $('briefSheet').hidden=true; };
$('bPause').onclick=()=>{ if(!speakQ){ openBrief(); return; } const p=pauseSpeak(); $('bPause').textContent=p?'▶':'❚❚'; $('bPause').setAttribute('aria-label', p?'Resume':'Pause'); };
$('bAsk').onclick=()=>{ stopSpeak(); $('briefSheet').hidden=true; openAsk(true); };
$('bGo').onclick=()=>{ stopSpeak(); $('briefSheet').hidden=true; if(mode==='off') startGPS(); };
$('bToday').onclick=()=>{ stopSpeak(); $('briefSheet').hidden=true; openToday(); };

/* ---- the pill in the top row ---- */
function renderGuidePill(){ const p=$('wxPill'); if(!p) return; p.hidden=false; p.classList.toggle('fresh', !heardToday() && new Date().getHours()>=5); }
$('wxPill').onclick=()=>{ if(mode!=='off') openAsk(true); else openBrief(); };

/* ---- ask ---- */
let listening=false, heardFinal=false;
const SUGS=['What’s next?','Where’s lunch?','Any lifts closed?','Plan from here','How much today?','Call the group'];
function openAsk(listenNow){
  closeDrawer(); $('briefSheet').hidden=true; $('askSheet').hidden=false;
  const s=$('aSugs'); s.textContent=''; for(const q of SUGS.concat(friendNames().slice(0,2).map(n=>'Where’s '+n+'?'))){ const b=document.createElement('button'); b.type='button'; b.textContent=q; b.onclick=()=>{ aMe(q); answer(q); }; s.appendChild(b); }
  if(listenNow) startListen();
}
function friendNames(){ return (typeof gstate!=='undefined' && gstate && grp) ? gstate.members.filter(m=>m.id!==grp.member_id).map(m=>m.name.split(' ')[0]) : []; }
$('aClose').onclick=()=>{ stopListen(); stopSpeak(); $('askSheet').hidden=true; };
$('aHold').onclick=()=>{ if(listening) stopListen(); else startListen(); };
function setListening(on){ listening=on; $('aHold').classList.toggle('on', on); $('aHoldTxt').textContent = on ? 'Listening… tap when done' : 'Tap and talk'; $('askSheet').classList.toggle('listening', on); $('aState').textContent = on ? 'Listening…' : 'Ask me anything about today'; }
let webRec=null;
function startListen(){
  stopSpeak(); heardFinal=false; $('aSub').textContent='Works on your phone, no signal needed';
  if(NATIVE){ toNative({cmd:'listen', on:true}); setListening(true); return; }
  const R=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!R){ aSay('Voice isn’t available in this browser. Tap a question below.'); return; }
  webRec=new R(); webRec.lang='en-US'; webRec.interimResults=true; webRec.continuous=false;
  webRec.onresult=e=>{ const r=e.results[e.results.length-1]; onHeard(r[0].transcript, r.isFinal); };
  webRec.onend=()=>{ setListening(false); if(!heardFinal && pendingHeard) onHeard(pendingHeard, true); };
  webRec.onerror=()=>setListening(false);
  try{ webRec.start(); setListening(true); }catch(e){ setListening(false); }
}
function stopListen(){ if(NATIVE) toNative({cmd:'listen', on:false}); else if(webRec) try{ webRec.stop(); }catch(e){} setListening(false); }
let pendingHeard='';
function onHeard(text, final){
  pendingHeard=text; $('aState').textContent = text ? '“'+text+'”' : 'Listening…';
  if(final && text && !heardFinal){ heardFinal=true; pendingHeard=''; setListening(false); aMe(text); answer(text); }
}
function aMe(t){ const b=document.createElement('div'); b.className='abub me'; b.textContent=t; $('aConvo').appendChild(b); b.scrollIntoView({block:'end'}); }
function aSay(text, actions){
  const b=document.createElement('div'); b.className='abub it'; const p=document.createElement('span'); p.textContent=text; b.appendChild(p);
  if(actions && actions.length){ const g=document.createElement('div'); g.className='ggrid'; actions.slice(0,2).forEach((a,i)=>{ const x=document.createElement(a.href?'a':'button'); x.className='btn '+(i?'ghost':'primary'); x.textContent=a.label; if(a.href){ x.href=a.href; if(!NATIVE){ x.target='_blank'; x.rel='noopener'; } } else { x.type='button'; x.onclick=()=>{ $('askSheet').hidden=true; a.fn(); }; } g.appendChild(x); }); b.appendChild(g); }
  $('aConvo').appendChild(b); b.scrollIntoView({block:'end'});
  speak([text]);
}
/* fixed phrases: the things the app can do. Everything else goes to the phone's own model when it has one. */
function answer(q){
  const t=q.toLowerCase().replace(/[’']/g,"'"), r=ask(t);
  if(r){ aSay(r.say, r.actions); return; }
  if(NATIVE){ $('aState').textContent='Thinking…'; toNative({cmd:'think', q, context:askContext()}); return; }
  aSay('I can tell you what’s next, where your friends are, lifts, lunch, weather and today’s numbers. Try one of the buttons below.');
}
function onThought(e){ $('aState').textContent='Ask me anything about today'; if(e.text) aSay(e.text); else aSay('I can tell you what’s next, where your friends are, lifts, lunch, weather and today’s numbers. Try one of the buttons below.'); }
function askContext(){
  const f=briefFacts(); const s=steps[cur];
  const fr=(typeof gstate!=='undefined' && gstate && grp) ? gstate.members.filter(m=>m.id!==grp.member_id).map(m=>m.name+': '+(m.pos ? (m.pos.on_lift?'on a lift':(m.pos.run?'on '+m.pos.run:'on the mountain'))+', '+ago(m.pos.age_s) : 'no location')).join('; ') : '';
  return 'Trip: '+CONFIG.title+'. Today: '+DAY.title+', '+f.km+', '+f.lifts+' lifts. Now on step '+(cur+1)+' of '+steps.length+': '+(s?stepLabel(s):'')+'. Skied so far: '+(st.dist/1000).toFixed(1)+' km. '+(f.weather?'Weather: '+f.weather+'. ':'')+(f.end?'Ends at '+f.end+' '+f.endTime+'. ':'')+(fr?'Friends: '+fr+'.':'');
}
function ask(t){
  const has=(...w)=>w.some(x=>t.includes(x));
  // friends
  if(typeof gstate!=='undefined' && gstate && grp){
    const m=gstate.members.find(m=>m.id!==grp.member_id && t.includes(m.name.split(' ')[0].toLowerCase()));
    if(m){ if(!m.pos) return {say:m.name.split(' ')[0]+' hasn’t shared a location yet today.'};
      const me=myPos(), d=me?fmtLen(hav(me,[m.pos.lat,m.pos.lon])):'', eta=me?routeTo([m.pos.lat,m.pos.lon], m.name, true):null;
      const where = m.pos.on_lift ? 'on a lift' : (m.pos.run ? 'on '+m.pos.run : 'on the mountain');
      return {say: m.name.split(' ')[0]+' is '+where+(d?', '+d+' away':'')+(eta?', about '+eta.minutes+' minutes to reach':'')+'. Last update '+ago(m.pos.age_s)+'.',
        actions:[{label:'Route to '+m.name.split(' ')[0], fn:()=>routeTo([m.pos.lat,m.pos.lon], m.name, false)}, {label:'Show on map', fn:()=>{ setFollow(false); map.flyTo({center:[m.pos.lon,m.pos.lat], zoom:15}); }}]}; }
    if(has('where is everyone','where\'s everyone','everyone','the group','my friends','the crew') && !has('call','talk')){
      const L=gstate.members.filter(m=>m.id!==grp.member_id).map(m=>m.name.split(' ')[0]+(m.pos?(m.pos.on_lift?' on a lift':(m.pos.run?' on '+m.pos.run:' on the mountain')):' no location yet'));
      return {say: L.length ? L.join(', ')+'.' : 'Nobody else is in the group yet.', actions:[{label:'Show everyone', fn:()=>$('fitBtn').click()}]}; }
  }
  if(has('call','talk to the group','talk with the group','whatsapp')){ const u=typeof callLink==='function' && callLink(); return u ? {say:'Opening the group chat. Tap the phone icon there to call everyone.', actions:[{label:'Open WhatsApp group', href:u}]} : {say:'The organizer hasn’t added the WhatsApp group yet.'}; }
  if(has('split','splitwise','cost','owe','pay')){ const u=typeof splitLink==='function' && splitLink(); return u ? {say:'Here’s the Splitwise group.', actions:[{label:'Split costs', href:u}]} : {say:'The organizer hasn’t added Splitwise yet.'}; }
  if(has('lunch','eat','sandwich','food')){ const f=briefFacts(); return {say: f.lunch ? 'Sandwich stop around '+f.lunch+'.' : 'No lunch stop in today’s plan.', actions: DAY.lunch!=null ? [{label:'Show it', fn:()=>{ cur=Math.max(cur, 0); focusStepIdx(DAY.lunch); }}] : null}; }
  if(has('lift') && has('closed','open','status','running')){ const f=briefFacts(); return {say: !resortRunning() ? 'The lifts aren’t running right now.' : f.closed ? f.closed+(f.closed===1?' lift on our plan is':' lifts on our plan are')+' closed. Plan from here will route around them.' : 'Every lift on our plan is open.', actions:[{label:'Plan from here', fn:()=>planFromHere()}, {label:'Lift status', fn:()=>openToday()}]}; }
  if(has('plan from here','reroute','re-route','get back','lost','where am i')) return {say:'Working out the best way back into today’s plan.', actions:[{label:'Plan from here', fn:()=>planFromHere()}]};
  if(has('next','what now','where to','where do i go','what\'s after')){ const s=steps[Math.min(cur+(mode==='off'?0:1), steps.length-1)]; return {say: s ? (mode==='off'?'First up: ':'Next: ')+stepLabel(s)+(s.at?', planned for '+s.at:'')+'.' : 'That’s the end of today’s plan.', actions:[{label:'Steps', fn:()=>$('stepsBtn').click()}]}; }
  if(has('how much','how far','how many','stats','kilometers','km','speed','fast')){ return {say:'So far: '+fmtLen(st.dist)+' skied, '+Math.round(st.vert)+' meters down, top speed '+Math.round(speedOut(st.max))+(units==='imp'?' miles':' kilometers')+' an hour. '+cur+' of '+steps.filter(s=>s.type!=='end').length+' steps done.'}; }
  if(has('weather','cold','wear','temperature','snow','wind')){ const f=briefFacts(); return {say: f.weather ? 'It’s '+f.weather+'.'+(f.wear?' Wear '+f.wear+'.':'') : 'No weather yet, it needs a connection.', actions:[{label:'Weather and lifts', fn:()=>openToday()}]}; }
  if(has('folie','apres','après','end','finish','home','done for the day')){ const f=briefFacts(); return {say: f.end ? f.end+' at '+f.endTime+'.' : 'End of the day: '+DAY.arrive+'.'}; }
  if(has('start','let\'s go','go skiing')) return {say: mode==='off' ? 'Starting. Have fun!' : 'You’re already tracking.', actions: mode==='off' ? [{label:'Start skiing', fn:()=>startGPS()}] : null};
  if(has('stop','finish tracking','end tracking')) return {say: mode!=='off' ? 'Tap Stop when you’re done for the day.' : 'You’re not tracking right now.'};
  if(has('brief','today','plan for today','what are we doing')) return {say:'Here’s today’s brief.', actions:[{label:'Play the brief', fn:()=>openBrief()}]};
  return null;
}
function focusStepIdx(i){ cur=i; persist(); renderStep(); if(typeof focusStep==='function') focusStep(); }

/* ---- morning brief settings ---- */
function renderBriefSet(){ const b=bset(); $('bsOn').setAttribute('aria-pressed', b.on?'true':'false'); $('bsTime').value=b.time; $('bsVoice').querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed', x.dataset.v===b.voice?'true':'false')); $('bsVoiceNote').hidden = b.voice!=='personal'; }
function scheduleBrief(){
  if(!NATIVE) return; const b=bset();
  const dates=(CONFIG.trip||[]).map(([y,m,d])=>[y,m+1,d]);
  toNative({cmd:'briefSchedule', on:!!b.on, time:b.time, dates, title:'Your morning brief is ready', body:'Today’s plan, weather and what to wear. Tap to listen.'});
}
$('bsOn').onclick=()=>{ const b=bset(); b.on=!b.on; persist(); renderBriefSet(); scheduleBrief(); };
$('bsTime').onchange=()=>{ const b=bset(); if(/^\d\d:\d\d$/.test($('bsTime').value)){ b.time=$('bsTime').value; persist(); scheduleBrief(); } };
$('bsVoice').querySelectorAll('button').forEach(x=>x.onclick=()=>{ bset().voice=x.dataset.v; persist(); renderBriefSet(); if(x.dataset.v==='personal' && NATIVE) toNative({cmd:'personalVoice'}); });
$('bsPlay').onclick=()=>{ $('briefSet').hidden=true; openBrief(); };
$('bsDone').onclick=()=>{ $('briefSet').hidden=true; };
$('briefSetBtn').onclick=()=>{ closeDrawer(); renderBriefSet(); $('briefSet').hidden=false; };
function renderBriefRow(){ const b=bset(); $('briefSetSub').textContent = b.on ? b.time+' · '+(b.voice==='personal'?'my voice':'iPhone voice') : 'Off'; }

/* ---- first open ---- */
function showOnb(){
  $('oTitle').textContent=CONFIG.title; $('oSub').textContent=CONFIG.subtitle||'';
  ['o1','o2','o3'].forEach((id,i)=>$(id).hidden=i!==0); $('onb').hidden=false;
}
$('o1Go').onclick=()=>{ $('o1').hidden=true; $('o2').hidden=false; };
const o2next=()=>{ $('o2').hidden=true; $('o3').hidden=false; };
$('o2Go').onclick=()=>{ if(NATIVE) toNative({cmd:'locate'}); else if(navigator.geolocation) navigator.geolocation.getCurrentPosition(()=>{},()=>{}); setTimeout(o2next, 400); };
$('o2Skip').onclick=o2next;
$('oVoice').querySelectorAll('button').forEach(x=>x.onclick=()=>{ bset().voice=x.dataset.v; $('oVoice').querySelectorAll('button').forEach(y=>y.setAttribute('aria-pressed', y===x?'true':'false')); if(x.dataset.v==='personal' && NATIVE) toNative({cmd:'personalVoice'}); });
$('oSample').onclick=()=>speak(['Hi, I’m Snowy. Every morning I’ll tell you the plan, the weather and what to wear. Sound good?']);
$('o3Go').onclick=()=>{ stopSpeak(); try{ localStorage.setItem(ONB,'1'); }catch(e){} persist(); $('onb').hidden=true; scheduleBrief(); renderBriefRow(); };

/* the iPhone opened the app from the 8:30 notification */
if(window.__native){ const ev3=window.__native.event; window.__native.event=function(name){ if(name==='openBrief'){ setTimeout(()=>openBrief(true), 600); return; } return ev3.apply(this, arguments); }; }
/* friends who joined from an invite get the morning brief step after joining */
{ const _fj=finishJoin; finishJoin=async function(share){ await _fj(share); let seen=false; try{ seen=!!localStorage.getItem(ONB); }catch(e){} if(grp && !seen && !window.__QA_ACK){ ['o1','o2'].forEach(id=>$(id).hidden=true); $('o3').hidden=false; $('onb').hidden=false; } }; }
renderGuidePill(); renderBriefRow(); setInterval(renderGuidePill, 60e3);
{ let seen=false; try{ seen=!!localStorage.getItem(ONB); }catch(e){}
  const joining=/[?#&](join|c)=/.test(location.search+location.hash);
  if(!seen && !joining) setTimeout(()=>{ if(!window.__QA_ACK && !window.__QA_TOUR && !window.__QA_WAIT) showOnb(); }, 700);
  else if(seen) scheduleBrief(); }
"""

SETTINGS_OLD = '        <button class="grow link" id="simBtn" type="button">Test mode</button>'
SETTINGS_NEW = '        <button class="grow link" id="briefSetBtn" type="button"><span>Morning brief<small id="briefSetSub">8:30 · iPhone voice</small></span></button>\n' + SETTINGS_OLD

def patch(path):
    s = open(path).read()
    if 'id="briefSheet"' in s: print('already', path); return
    brief = json.load(open(os.path.join(ROOT, 'brief.json')))
    brief.pop('_help', None)
    s = rep(s, PILL_OLD, PILL_NEW)
    s = rep(s, '<div class="sheet" id="todaySheet" hidden>', HTML.strip() + '\n\n<div class="sheet" id="todaySheet" hidden>')
    s = rep(s, "/* ===== redesign: map-first home", CSS + "/* ===== redesign: map-first home")
    s = rep(s, SETTINGS_OLD, SETTINGS_NEW)
    # the pill opens the brief now (the guide's handler replaces the Today handler)
    s = rep(s, "$('wxPill').onclick=openToday; $('liftsPill').onclick=openToday;", "$('liftsPill').onclick=openToday;")
    s = rep(s, "  if(!CONFIG.wx){ $('wxPill').hidden=true; return; }", "  if(!CONFIG.wx){ return; }")
    s = rep(s, "tellNative(); groupLoop(); refreshGroup(); renderFriendsPill();", JS.replace('__BRIEF__', json.dumps(brief, ensure_ascii=False)).strip() + "\ntellNative(); groupLoop(); refreshGroup(); renderFriendsPill();")
    s = rep(s, "recap:openRecap,", "recap:openRecap, openBrief, openAsk, buildBrief, askQ:q=>ask(q.toLowerCase()), showOnb,")
    open(path, 'w').write(s); print('patched', path)

for p in sys.argv[1:]: patch(p)
