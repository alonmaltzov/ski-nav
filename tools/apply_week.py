"""Write tools/week_<variant>.json into WEEKS[variant] of index.html and recompute which piste
segments each day covers (BG plan columns). Writes to the given output file (default index.html)."""
import json, math, sys, os, re
V = sys.argv[1] if len(sys.argv) > 1 else 'red'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'index.html'
VI = {'std': 0, 'black': 1, 'red': 2}
s = open('index.html', encoding='utf-8').read()
week = json.load(open('tools/week_%s.json' % V))
def span(name):
    i = s.index('const ' + name + ' = ') + len('const ' + name + ' = '); j = s.index(';\n', i); return i, j
# WEEKS: replace only this variant's array, keep the others byte for byte
i, j = span('WEEKS'); W = s[i:j]
k = W.index(V + ': ') + len(V + ': ')
depth = 0; e = k
for e in range(k, len(W)):
    ch = W[e]
    if ch == '[': depth += 1
    elif ch == ']':
        depth -= 1
        if depth == 0: break
W2 = W[:k] + json.dumps(week, ensure_ascii=False, separators=(',', ':')) + W[e+1:]
# BG: plan day per segment for this variant
bi, bj = span('BG'); BG = json.loads(s[bi:bj])
def hav(a, b):
    t = math.pi / 180; h = math.sin((b[0]-a[0])*t/2)**2 + math.cos(a[0]*t)*math.cos(b[0]*t)*math.sin((b[1]-a[1])*t/2)**2
    return 2 * 6371000 * math.asin(math.sqrt(h))
grid = {}
for d in week:
    for st in d['steps']:
        if st['type'] != 'run': continue
        pts = [p for sg in st.get('segs', []) for p in sg['c']]
        dense = []
        for a, b in zip(pts, pts[1:]):
            n = max(1, int(hav(a, b) // 10))
            dense += [(a[0] + (b[0]-a[0])*q/n, a[1] + (b[1]-a[1])*q/n) for q in range(n)]
        for p in dense: grid.setdefault((int(p[0]*3000), int(p[1]*2000)), []).append((p, d['day']))
col = 6 + VI[V]; changed = 0
orig_week = json.loads(W[k:e+1])
touched = {d['day'] for d, o in zip(week, orig_week) if [x.get('name') for x in d['steps']] != [x.get('name') for x in o['steps']]}
print('days changed:', sorted(touched))

for b in BG:
    if b[0] != 'R': continue
    votes = {}
    for p in b[3]:
        best = None
        for da in (-1, 0, 1):
            for db in (-1, 0, 1):
                for q, day in grid.get((int(p[0]*3000)+da, int(p[1]*2000)+db), []):
                    if hav(p, q) <= 25: best = day; break
                if best: break
            if best: break
        if best: votes[best] = votes.get(best, 0) + 1
    day = 0; orig = b[col] if len(b) > col else 0
    if votes:
        dmax = max(votes, key=votes.get)
        if sum(votes.values()) >= 0.6 * len(b[3]): day = dmax
        elif orig and votes.get(orig, 0) >= 0.3 * len(b[3]): day = orig   # the original planner's call, still on the route
    if not votes and orig and orig not in touched: day = orig
    if len(b) > col and b[col] != day: b[col] = day; changed += 1
s2 = s[:bi] + json.dumps(BG, ensure_ascii=False, separators=(',', ':')) + s[bj:]
i, j = (s2.index('const WEEKS = ') + len('const WEEKS = '), None); j = s2.index(';\n', i)
s2 = s2[:i] + W2 + s2[j:]
open(OUT, 'w', encoding='utf-8').write(s2)
print('wrote', OUT, '· segments re-assigned:', changed)
