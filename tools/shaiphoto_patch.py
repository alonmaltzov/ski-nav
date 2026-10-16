"""Shai's real photo instead of the cartoon, everywhere his face shows (pill, hub, tour, passport).
A photo can't talk, so while a clip plays it pulses gently instead."""
import base64, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
src = 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(ROOT, 'tools/assets/shai.jpg'), 'rb').read()).decode()
IMG = '<img class="gface gphoto" src="' + src + '" alt="" aria-hidden="true" draggable="false">'
s, n = re.subn(r'<svg class="gface" viewBox="0 0 120 120" aria-hidden="true">.*?</svg>', IMG, s, flags=re.S)
assert n >= 3, n
CSS = '''
/* Shai's photo */
.gphoto{object-fit:cover;border-radius:50%;-webkit-user-drag:none;pointer-events:none}
.talking .gphoto,.listening .gphoto{animation:gbob .32s ease-in-out infinite alternate}
@keyframes gbob{from{transform:scale(1)}to{transform:scale(1.06)}}
'''
i = s.index('<style>\n/* Layout: one-screen instrument.'); j = s.index('</style>', i)
s = s[:j] + CSS + s[j:]
open(p, 'w', encoding='utf-8').write(s)
print('shai photo in', n, 'places')
