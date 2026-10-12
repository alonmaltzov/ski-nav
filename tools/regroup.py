"""Rebuild GROUPS (the week's run goal) by area: one entry per named run (and unnamed runs of 300 m+)
in the six areas the plan skis. Sets BG[5] (group index, -1 = not a goal run). Usage: python3 tools/regroup.py"""
import json, math, re
S = open('index.html', encoding='utf-8').read()
def span(name):
    i = S.index('const ' + name + ' = ') + len('const ' + name + ' = '); j = S.index(';\n', i); return i, j
def hav(a, b):
    t = math.pi/180; h = math.sin((b[0]-a[0])*t/2)**2 + math.cos(a[0]*t)*math.cos(b[0]*t)*math.sin((b[1]-a[1])*t/2)**2
    return 2*6371000*math.asin(math.sqrt(h))
BORDER = [[46.10,6.800],[46.172,6.794],[46.190,6.807],[46.215,6.826],[46.240,6.846],[46.258,6.866],[46.275,6.874],[46.288,6.858],[46.300,6.836],[46.330,6.805]]
def blon(lat):
    for (a0,o0),(a1,o1) in zip(BORDER, BORDER[1:]):
        if lat <= a1: return o0+(o1-o0)*max(0,(lat-a0)/(a1-a0))
    return BORDER[-1][1]
sw = lambda p: p[1] > blon(p[0])
box = lambda p,a0,a1,o0,o1: a0<p[0]<a1 and o0<p[1]<o1
def area(p):
    if not sw(p) and box(p,46.150,46.212,6.738,6.83): return 'Avoriaz'
    if box(p,46.115,46.200,6.58,6.738): return 'Morzine + Les Gets'
    if sw(p) and box(p,46.150,46.198,6.78,6.92): return 'Les Crosets + Champéry'
    if sw(p) and box(p,46.198,46.262,6.80,6.92): return 'Champoussin + Morgins'
    if not sw(p) and box(p,46.212,46.300,6.74,6.835): return 'Châtel'
    if (sw(p) and box(p,46.262,46.340,6.78,6.92)) or (not sw(p) and box(p,46.255,46.300,6.835,6.90)): return 'Super-Châtel + Torgon'
    return None
COL = {'eas':'blue','int':'red','adv':'black','exp':'black','fre':'black'}
SKIP = re.compile(r'^(Montée|Promenade|Rue|Accès|Zone|Snowpark|Retour|Liaison|Chemin|Piste de luge|Luge|Raquette|Itinéraire)', re.I)
bi, bj = span('BG'); BG = json.loads(S[bi:bj])
groups, idx, L = [], {}, {}
for i, b in enumerate(BG):
    if b[0] != 'R': continue
    c = COL.get(b[1]); a = area(b[3][len(b[3])//2]); nm = b[2] or ''
    b[5] = -1
    if not c or not a or SKIP.match(nm): continue
    k = (nm, c, a) if nm else ('', c, a, i)
    if k not in idx: idx[k] = len(groups); groups.append({'n': nm or 'Unnamed ' + c, 'a': a, 'c': c})
    b[5] = idx[k]; L[idx[k]] = L.get(idx[k], 0) + sum(hav(p, q) for p, q in zip(b[3], b[3][1:]))
# drop short unnamed bits
keep = {g for g, l in L.items() if l >= (300 if groups[g]['n'].startswith('Unnamed') else 150)}
remap, out = {}, []
for g, x in enumerate(groups):
    if g in keep: remap[g] = len(out); out.append(x)
for b in BG:
    if b[0] == 'R' and b[5] >= 0: b[5] = remap.get(b[5], -1)
gi, gj = span('GROUPS')
S2 = S[:bi] + json.dumps(BG, ensure_ascii=False, separators=(',', ':')) + S[bj:gi] + json.dumps(out, ensure_ascii=True, separators=(',', ':')) + S[gj:] if bi < gi else None
assert S2, 'BG must come before GROUPS'
open('index.html', 'w', encoding='utf-8').write(S2)
from collections import Counter
print(len(out), 'goal runs', Counter((x['a'], x['c']) for x in out))
