"""No spoken voice: the guide shows his words, he doesn't read them out (the crew's sound clips stay)."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    assert old in s, old[:80]; s = s.replace(old, new, 1)
# speak(): text only. Callers still get onPart/onDone so the screens behave the same.
rep("function speak(parts, onPart, onDone){\n  stopSpeak();",
    "const VOICE=false;   // the robot voice is off; words show on screen, sound clips still play\nfunction speak(parts, onPart, onDone){\n  if(!VOICE){ stopSpeak(); parts.forEach((_,i)=>onPart&&onPart(i)); onDone&&onDone(); return; }\n  stopSpeak();")
# the brief shows every line at once
rep("  const cap=$('bCap'); const show=i=>{ cap.textContent=''; S.forEach((t,k)=>{ if(k<i-1 || k>i+1) return;",
    "  const cap=$('bCap'); const show=i=>{ cap.textContent=''; S.forEach((t,k)=>{ if(VOICE && (k<i-1 || k>i+1)) return;")
rep('<button class="btn ghost" id="bPause" type="button" aria-label="Pause">❚❚</button>', '<button class="btn ghost" id="bPause" type="button" aria-label="Pause" hidden>❚❚</button>')
# tour: no "Speaking" state, no replay
rep("<button class=\"btn ghost\" id=\"tourReplay\" type=\"button\" aria-label=\"Say it again\">", "<button class=\"btn ghost\" id=\"tourReplay\" type=\"button\" aria-label=\"Say it again\" hidden>")
rep(".onb.talking .twave{display:flex}", ".onb.talking .twave{display:none}")
rep("html:()=>'<b>Brief</b> at '+esc(bset().time)+'. Then <b>Start skiing</b>, phone in pocket. I’ll do the talking.' },",
    "html:()=>'<b>Brief</b> at '+esc(bset().time)+'. Then <b>Start skiing</b> and put the phone away.' },")
# settings + notification wording
rep('<small>A notification; tap it to hear the brief</small>', '<small>A notification with today’s plan</small>')
rep("body:'Today’s plan, weather and what to wear. Tap to listen.'", "body:'Today’s plan, weather and what to wear.'")
s = s.replace('<div class="grow col"><span>Voice</span><div class="seg" id="bsVoice">', '<div class="grow col" hidden><span>Voice</span><div class="seg" id="bsVoice">', 1)
s = s.replace('<p class="note" style="margin:0">Sounds robotic? Download a Premium voice: Settings › Accessibility › Spoken Content › Voices › English.</p>', '', 1)
rep("$('bsPlay').onclick", "$('bsPlay').onclick")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
