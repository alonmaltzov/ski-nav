"""Onboarding: Shai's real photo instead of the cartoon, and the tour talks about today's games
(STOPPP + Speed King). The passport race is gone; the passport check is the Swiss-day gate, not a game."""
import os, re, base64
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80]); s = s.replace(old, new)

img = base64.b64encode(open(os.path.join(ROOT, 'tools/assets/shai.jpg'), 'rb').read()).decode()
photo = '<img class="gface gphoto" alt="" src="data:image/jpeg;base64,' + img + '">'
for wrap in ('<div class="tglow">', '<div class="tav">'):
    pat = re.compile(re.escape(wrap) + r'<svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="58" fill="#FFF4EA".*?</svg>', re.S)
    s, n = pat.subn(lambda m: wrap + photo, s, count=1); assert n == 1, wrap

# last tour step: point at the two game buttons, name only the real games
rep("  { el:['fitBtn'], el2:['kingBtn'], next:'Let’s ski',\n"
    "    say:()=>'All shows the crew. The crown is Speed King. Games run by themselves.',\n"
    "    html:()=>'<b>ALL</b> shows the crew. The crown is Speed King. Games run by themselves:',\n"
    "    chips:['🥃 STOPPP','🇨🇭 Passport check','👑 Speed King'] }",
    "  { el:['fitBtn'], el2:['kingBtn','stopBtn'], next:'Let’s ski',\n"
    "    say:()=>'All shows the crew. The crown is Speed King, the flask is STOPPP. Both run by themselves.',\n"
    "    html:()=>'<b>ALL</b> shows the crew. The crown is <b>Speed King</b>, the flask is <b>STOPPP</b>. Both run by themselves.',\n"
    "    note:'🇨🇭 Swiss days: passport check before Start.',\n"
    "    chips:['👑 Speed King','🥃 STOPPP'] }")

CSS = '''
/* onboarding: Shai's photo */
.tglow .gphoto{width:120px;height:120px}
.tav .gphoto{width:50px;height:50px}
'''
i = s.index('<style>\n/* Layout: one-screen instrument.'); j = s.index('</style>', i)
s = s[:j] + CSS + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('onboarding fix applied')
