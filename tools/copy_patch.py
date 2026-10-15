"""Shorter, punchier copy everywhere the guide talks (brief, tour, lifts, games) + a less robotic voice."""
import os, re, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    assert old in s, old[:90]
    s = s.replace(old, new, 1)
def sub(pat, new):
    global s
    s2, n = re.subn(pat, lambda m: new, s, count=1, flags=re.S)
    assert n == 1, pat[:80]; s = s2

# --- the brief: 3-4 short lines
sub(r"function buildBrief\(\)\{.*?\n  return \{S, f\};\n\}", r'''function buildBrief(){
  const f=briefFacts(), p=persona(), S=[];
  S.push(fill(p.open || 'Morning {me}.', f));
  const swiss=/^switzerland:\s*/i.test(DAY.title||'');
  S.push(fill('{title} today'+(swiss?', passports in':'')+'. {km}'+(f.endTime ? ', Folie Douce by {endTime}.' : '.'), {...f, title:f.title.replace(/^switzerland:\s*/i,'')}));
  if(f.weather) S.push(f.weather.charAt(0).toUpperCase()+f.weather.slice(1)+'.'+(f.wear ? ' '+f.wear.charAt(0).toUpperCase()+f.wear.slice(1)+'.' : ''));
  if(f.closed) S.push(f.closed+(f.closed===1?' plan lift is':' plan lifts are')+' shut. Plan from here fixes it.');
  if(p.joke) S.push(fill(p.joke, f));
  return {S, f};
}''')
rep("Math.round(DAY.km)+' kilometers';", "Math.round(DAY.km)+' k';")
rep("(DAY.km*0.6214).toFixed(1)+' miles'", "Math.round(DAY.km*0.6214)+' miles'")
rep("f.weather = sayNum(wx.now.temperature_2m)+' degrees'+(cond?' and '+cond:'');", "f.weather = sayNum(wx.now.temperature_2m)+' degrees'+(cond?', '+cond:'');")
rep("const w=wearFor(wx); f.wear = w[0] ? w[0].charAt(0).toLowerCase()+w[0].slice(1) : '';", "const w=wearFor(wx); f.wear = w[0] ? w[0].charAt(0).toLowerCase()+w[0].slice(1) : '';")

# --- the tour: one line each
rep("""    say:(o)=>(o.name ? 'Hi '+o.name+', welcome to '+CONFIG.title+'. ' : 'Hi, I’m your guide. ')+'Quick tour, 30 seconds. First: allow location and pick Always, so I can follow your runs with the phone in your pocket.',
    html:(o)=>(o.name ? '<b>Hi '+esc(o.name)+', welcome to '+esc(CONFIG.title)+'.</b> ' : '<b>Hi, I’m your guide.</b> ')+'Quick tour, 30 seconds.<br>First: allow location and pick <b>Always</b>, so I can follow your runs with the phone in your pocket.',
    note:'Only after you tap Start skiing. Only your group sees your dot.',""",
"""    say:(o)=>(o.name ? 'Hey '+o.name+'! ' : 'Hey! ')+'I’m your guide. Allow location, pick Always.',
    html:(o)=>'<b>'+(o.name ? 'Hey '+esc(o.name)+'!' : 'Hey!')+' I’m your guide.</b><br>Allow location, pick <b>Always</b>.',
    note:'Only while skiing. Only the crew sees you.',""")
rep("say:()=>'This is today. Thick lines are today’s runs, the arrows show the way, and we finish at '+DAY.end.name+'.',",
    "say:()=>'Today’s plan. Follow the arrows to '+DAY.end.name+'.',")
rep("html:()=>'This is <b>today</b>. Thick lines are today’s runs, the arrows show the way, and we finish at <b>'+esc(DAY.end.name)+'</b>.' },",
    "html:()=>'<b>Today’s plan.</b> Follow the arrows to <b>'+esc(DAY.end.name)+'</b>.' },")
rep("say:()=>'Every morning at '+bset().time+' I play the brief, up top. Then tap Start skiing and put the phone away. I’ll call out every lift and run.',",
    "say:()=>'Brief at '+bset().time+'. Then Start skiing, phone in pocket. I’ll do the talking.',")
rep("html:()=>'Every morning at '+esc(bset().time)+' I play <b>the brief</b> up top. Then tap <b>Start skiing</b> and put the phone away. I’ll call out every lift and run.' },",
    "html:()=>'<b>Brief</b> at '+esc(bset().time)+'. Then <b>Start skiing</b>, phone in pocket. I’ll do the talking.' },")
rep("say:()=>'Runs, in the menu, shows the whole week. Each colour is a day, and the bars show what’s left to ski. Today brings you back.',",
    "say:()=>'The whole week, one colour a day. Today takes you back.',")
rep("html:()=>'<b>Runs</b>, in the menu, shows the whole week. Each colour is a day, and the bars show what’s left to ski. <b>‹ Today</b> brings you back.' },",
    "html:()=>'<b>The whole week</b>, one colour a day. It lives in the menu. <b>‹ Today</b> takes you back.' },")
rep("say:()=>'Tap All to see the crew on the map. And three games run by themselves: STOPPP, the passport race, and Speed King, right here under the crown.',",
    "say:()=>'All shows the crew. The crown is Speed King. Games run by themselves.',")
rep("html:()=>'Tap <b>ALL</b> to see the crew on the map. And 3 games run by themselves:',",
    "html:()=>'<b>ALL</b> shows the crew. The crown is Speed King. Games run by themselves:',")

# --- lifts button
rep("line='I can’t reach the lift status right now. Try again with a connection.';", "line='No signal for lift status. Try again in a bit.';")
rep("line='The lifts aren’t running right now. The season starts in December.';", "line='Lifts aren’t running yet. See you in December.';")
rep("line = shut.length ? (shut.length===1 ? shut[0].s.name+' is closed. Tap Plan from here when you get there.' : shut.length+' lifts on today’s plan are closed: '+shut.slice(0,3).map(x=>x.s.name).join(', ')+'. Tap Plan from here when you get there.')",
    "line = shut.length ? (shut.length===1 ? shut[0].s.name+' is shut. Plan from here fixes it.' : shut.length+' plan lifts shut: '+shut.slice(0,3).map(x=>x.s.name).join(', ')+'. Plan from here fixes it.')")
rep(": 'All '+planLifts().length+' lifts on today’s plan are open. '+liftStat.open+' of '+liftStat.total+' open across the area.'; }",
    ": 'All '+planLifts().length+' plan lifts open. Go.'; }")
rep("toast('Swiss day: bring your passports 🇨🇭');", "toast('Swiss day. Passports 🇨🇭');")

# --- games
rep("speak([(mine?'Your round.':who.name.split(' ')[0]+'’s round.')+' Flask out at the top.'])", "speak([(mine?'Your round.':who.name.split(' ')[0]+'’s round.')+' Flask out up top.'])")
rep("toast('No top speeds yet today. Ski a red or a blue.');", "toast('No speeds yet. Go fast on a red.');")
rep("toast('You’re out of the rounds today. Turn it back on in Settings › Games.');", "toast('You’re out of rounds today.');")
rep('<span>STOPPP flask breaks<small>3 a day between 11:00 and 3:00, at the bottom of a long lift. A different person’s round each time.</small></span>', '<span>STOPPP<small>3 flask breaks a day, on long lifts.</small></span>')
rep('<span>Count me in for rounds<small>Off: you still get the STOPPP, you’re just never the one picked.</small></span>', '<span>Count me in for rounds<small>Off: you drink, you don’t pour.</small></span>')
rep('<span>Passport check<small>Who crosses into Switzerland first in the morning.</small></span>', '<span>Passport race<small>First into Switzerland wins.</small></span>')
rep('<span>Speed King<small>Top speed on reds and blues, announced at La Folie Douce.</small></span>', '<span>Speed King<small>Fastest on reds and blues. Crowned at Folie Douce.</small></span>')
rep('<span>Sound clips<small>Start, Stop, the brief, Steps, closed lifts and the games.</small></span>', '<span>Sound clips<small>The crew’s voice notes.</small></span>')

# --- voice: the best voice on the phone, a touch faster and warmer
rep("const u=new SpeechSynthesisUtterance(t); u.rate=1.02;", "const u=new SpeechSynthesisUtterance(t); u.rate=1.06; u.pitch=1.05; const bv=bestWebVoice(); if(bv) u.voice=bv;")
rep("function stopSpeak(){", r'''/* browsers: skip the robotic default, take the most natural English voice there is */
function bestWebVoice(){ try{ const vs=speechSynthesis.getVoices().filter(v=>/^en[-_]/i.test(v.lang)); if(!vs.length) return null;
  const pref=[/premium/i,/enhanced/i,/natural/i,/\b(ava|zoe|evan|nathan|serena|samantha)\b/i,/google (us|uk) english/i,/aria|jenny|guy/i];
  for(const r of pref){ const v=vs.find(x=>r.test(x.name)); if(v) return v; } return vs.find(v=>/en[-_]us/i.test(v.lang))||vs[0]; }catch(e){ return null; } }
function stopSpeak(){''')
rep('<p class="note" id="bsVoiceNote" style="margin:0" hidden>“My voice” uses Personal Voice. Make it once in iPhone Settings › Accessibility › Personal Voice (about 15 minutes), then allow Ski Nav to use it.</p>',
    '<p class="note" id="bsVoiceNote" style="margin:0" hidden>“My voice” needs Personal Voice: iPhone Settings › Accessibility › Personal Voice.</p>\n    <p class="note" style="margin:0">Sounds robotic? Download a Premium voice: Settings › Accessibility › Spoken Content › Voices › English.</p>')
open(p, 'w', encoding='utf-8').write(s)

# --- the script the brief reads from (edit brief.json any time)
b = json.load(open(os.path.join(ROOT, 'brief.json')))
b['days'] = {
  '1': {'open': 'Morning {me}. Day one. Fresh legs, zero excuses.', 'joke': 'Folie Douce is the finish line, not the warm-up.'},
  '2': {'open': 'Morning {me}. Day two. Legs still attached?', 'joke': 'Nobody ever regretted the second hot chocolate.'},
  '3': {'open': 'Morning {me}. Halfway. Look at you.', 'joke': 'Your thighs filed a complaint. Complaint ignored.'},
  '4': {'open': 'Morning {me}. Day four. Basically a local now.', 'joke': 'Locals don’t stop for photos. You will.'},
  '5': {'open': 'Morning {me}. Day five. Pace yourself. Or don’t.', 'joke': 'Slowest one today buys the vin chaud.'},
  '6': {'open': 'Morning {me}. Last day. Make it count.', 'joke': 'Fewest reds today buys the last round.'},
  'practice': {'open': 'Morning {me}. NYC practice run.', 'joke': 'The M15 counts as a gondola. Don’t tell anyone.'}}
b['_help'] = "The guide's script: one opener and one joke a day. Edit freely; the app picks it up next time it opens online. Blanks: {me} {title} {km} {endTime}. Days 1 to 6 (Sun Jan 17 = 1). 'practice' is the NYC page."
json.dump(b, open(os.path.join(ROOT, 'brief.json'), 'w'), indent=2, ensure_ascii=False)
s=open(p,encoding='utf-8').read(); fb={'name':b.get('name','Snowy'),'days':b['days']}
s=re.sub(r'const BRIEF_FALLBACK=\{.*?\};\n', lambda m:'const BRIEF_FALLBACK='+json.dumps(fb,ensure_ascii=False)+';\n', s, count=1, flags=re.S)
open(p,'w',encoding='utf-8').write(s)
print('ok')
