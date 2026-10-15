"""Match the runs we ski (OpenStreetMap names) to the resort's live slope status (Intermaps oids).
Writes SLOPEMAP {normalised name: [[difficulty, oid], ...]} into index.html. Usage: python3 tools/slopemap.py feed.json"""
import json, re, sys, unicodedata, collections, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def norm(x):
    x = unicodedata.normalize('NFD', x or '').encode('ascii', 'ignore').decode().lower()
    x = re.sub(r"\b(piste|variante|du|de|la|le|les|des|d|l|a|the)\b", ' ', x)
    x = re.sub(r'[^a-z0-9]+', ' ', x).strip()
    return ' '.join(w[:-1] if len(w) > 4 and w.endswith('s') else w for w in x.split())
def build(feed):
    d = json.load(open(feed))
    by = collections.defaultdict(list)
    for sl in d['slopes']: by[norm(sl['popup']['title'])].append([sl['popup'].get('difficulty') or '', str(sl['popup']['oid'])])
    s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    i = s.index('const WEEKS = ') + len('const WEEKS = '); line = s[i:s.index('\n', i)].rstrip().rstrip(';')
    weeks = json.loads(re.sub(r'([{,]\s*)([a-z]+):', r'\1"\2":', line, count=0) if not line.startswith('{"') else line)
    names = set()
    for day in [d for v in weeks.values() for d in v]:
        for st in day['steps']:
            for leg in st.get('legs') or []: names.add(norm(leg.get('name')))
    out, miss = {}, []
    for n in sorted(names):
        if not n: continue
        m = by.get(n)
        if not m:
            cand = [k for k in by if k and (set(n.split()) <= set(k.split()) or set(k.split()) <= set(n.split()))]
            if len(cand) == 1: m = by[cand[0]]
        if m: out[n] = m
        else: miss.append(n)
    return out, miss, names
if __name__ == '__main__':
    out, miss, names = build(sys.argv[1])
    print(len(names), 'plan run names,', len(out), 'matched; missing:', miss)
    p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
    line = 'const SLOPEMAP = ' + json.dumps(out, separators=(',', ':')) + ';\n'
    if 'const SLOPEMAP = ' in s: s = re.sub(r'const SLOPEMAP = .*?;\n', lambda m: line, s, count=1)
    else: s = s.replace('const LIFTMAP = ', line + 'const LIFTMAP = ', 1)
    open(p, 'w', encoding='utf-8').write(s)
