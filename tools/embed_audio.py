"""Embed audio/<key>.mp3 into index.html between /*SFX:BEGIN*/ and /*SFX:END*/ (one file works everywhere:
web, the iPhone app and the Android app, including pages the apps download as updates)."""
import base64, glob, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = {os.path.basename(f)[:-4]: 'data:audio/mpeg;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
        for f in sorted(glob.glob(os.path.join(ROOT, 'audio', '*.mp3')))}
p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
new = '/*SFX:BEGIN*/const SFX_DATA=' + json.dumps(data, separators=(',', ':')) + ';/*SFX:END*/'
s2, n = re.subn(r'/\*SFX:BEGIN\*/.*?/\*SFX:END\*/', lambda m: new, s, flags=re.S)
assert n == 1, 'markers not found'
open(p, 'w', encoding='utf-8').write(s2)
print('embedded', ', '.join(data), round(len(new) / 1024), 'KB')
