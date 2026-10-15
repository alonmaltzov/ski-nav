"""Names from the official Portes du Soleil site (per-resort openings pages), status from the Intermaps feed.
  1. official catalog: resort, sector, lift/slope, colour, name  (qa/fixtures/official.json, refresh: --scrape)
  2. every map line (BG) gets the official name when one matches by name, colour and nearest resort
  3. official entries are tied to Intermaps oids, so the live status reads the right lift/slope
Writes into index.html: renamed BG + WEEKS, SLOPEMAP (name -> [[difficulty, oid]]), LIFTMAP (BG index -> oids),
OIDRES (oid -> resort, for the whole-area list). Prints what stayed unmatched.
Usage: python3 tools/official_names.py <intermaps feed.json> [--scrape] [--dry]"""
import json, re, sys, os, math, difflib, collections, unicodedata, html as H
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from slopemap import norm
RESORTS = {  # official page -> resort group, anchor villages
  'avoriaz-1800-ski-lifts': ('Avoriaz', ['Avoriaz', 'Les Lindarets', 'Montriond']),
  'montriond-ski-slopes-and-lifts': ('Avoriaz', ['Avoriaz', 'Les Lindarets', 'Montriond']),
  'morzine-ski-lifts': ('Morzine', ['Morzine']),
  'champery-lifts': ('Champéry · Les Crosets', ['Les Crosets', 'Champéry', 'Champoussin']),
  'val-dilliez-ski-lifts-les-crosets-champoussin': ('Champéry · Les Crosets', ['Les Crosets', 'Champéry', 'Champoussin']),
  'morgins-ski-lifts': ('Morgins', ['Morgins']),
  'chatel-ski-lifts': ('Châtel', ['Châtel']),
  'ski-lifts-la-chapelle-dabondance': ('La Chapelle', ['La Chapelle d’Abondance']),
  'saint-jean-daulps-ski-lifts': ('Saint-Jean-d’Aulps', ['Saint-Jean-d’Aulps']),
}
EXTRA = {'Les Gets': ['Les Gets'], 'Torgon': ['Torgon'], 'Abondance': ['Abondance']}   # not on the official pages
STOP = r'\b(tsd\d*|tsf\d*|ts\d*|td\d*|tc\d*|tk\d*|tph|tb|tm|tapis|telesiege|telecabine|teleski|chairlift|gondola|chair|lift|t bar|express|3s|piste|glisse|\d+)\b'
def n2(x): return ' '.join(re.sub(STOP, ' ', norm(x)).split())
ALIAS = {  # our map name (normalised) -> official name (normalised), checked by hand
  'snowcross crosats': 'crozats snowcross', 'stade tete au boeuf': 'stade tete boeuf', 'dronaire': 'dronnaire',
  'chavanette mur suisse': 'chavanette', 'pauvre couvre': 'pauvre conche', 'planachaux croset': 'planachaux',
  'snowcross pschott': 'pschott snowcross', 'snowcross marmotte': 'marmotte snowcross', 'blanchot': 'blanchots',
  'chaux fleurie': 'chaux fleurie', 'jonction mossette': 'mossette', 'jonction vautna': 'vautna', 'vautna noire': 'vautna',
}
SEG = {'superieure', 'inferieure', 'bleue', 'bleu', 'rouge', 'noire', 'verte', 'haut', 'bas'}
def strict(a, b):
    if not a or not b: return 0
    a = _ALIAS().get(a, a)
    if a == b: return 1
    bw = b.split()
    if len(bw) > 1 and bw[-1] in SEG and ' '.join(bw[:-1]) == a: return .95
    return 0
_AL = None
def _ALIAS():
    global _AL
    if _AL is None: _AL = {n2(k): n2(v) for k, v in ALIAS.items()}
    return _AL
def score(a, b):
    if not a or not b: return 0
    if a == b: return 1
    sa, sb = set(a.split()), set(b.split())
    if (sa <= sb or sb <= sa) and min(len(a), len(b)) >= 5: return .9
    return difflib.SequenceMatcher(None, a, b).ratio()
SMALL = {'de', 'du', 'des', 'la', 'le', 'les', 'et', 'a', 'au', 'aux', 'sur', 'en'}
def pretty(t, lift=False):
    t = H.unescape(t).strip()
    t = re.sub(r'^\d+\s+', '', t)                                     # Swiss piste numbers
    if lift: t = re.sub(r'^(tsd\d*|tsf\d*|ts\d*|td\d*|tc\d*|tk\d*|tph|tb|tm|tapis)\s+(de |du |des |d’|d\')?', '', t, flags=re.I)
    w = re.split(r'(\s+|-|’|\')', t.lower())
    out = []
    for i, x in enumerate(w):
        if not x.strip() or x in ('-', '’', "'"): out.append(x); continue
        if i and x in SMALL: out.append(x); continue
        if x in ('d', 'l') and i + 1 < len(w) and w[i + 1] in ('’', "'"): out.append(x.upper() if i == 0 else x); continue
        out.append(x[:1].upper() + x[1:])
    return ''.join(out).replace("'", '’')
def hav(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0]); dl = math.radians(b[1] - a[1])
    return 2 * 6371000 * math.asin(math.sqrt(math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2))
COLD = {'green': ['very-easy', 'easy'], 'blue': ['easy', 'very-easy'], 'red': ['medium'], 'black': ['difficult', 'very-difficult']}
BGC = {'nov': 'green', 'eas': 'blue', 'int': 'red', 'adv': 'black', 'exp': 'black', 'fre': 'black'}
def jline(s, prefix):
    i = s.index(prefix) + len(prefix); return i, s.index('\n', i)

def scrape():
    import urllib.request
    out = []
    for slug in list(RESORTS) + ['les-gets-ski-lifts', 'torgon-lifts', 'abondance-ski-lifts']:
        url = 'https://en.portesdusoleil.com/in-winter/slope-and-lift-openings/' + slug + '/'
        s = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8', 'replace')
        for sec in re.split(r'<div class="cell snowflake-sector-single', s)[1:]:
            m = re.search(r'class="sector-name">([^<]*)<', sec); sector = H.unescape(m.group(1)) if m else '?'
            for part in re.split(r'<div class="sector-sub-header"><span class="title">', sec)[1:]:
                kind = part[:part.index('<')]
                for it in re.finditer(r'<li class="item"\s*(?:data-color="([^"]*)")?[^>]*>(.*?)</li>', part, re.S):
                    t = re.search(r'<span class="title">([^<]*)<', it.group(2)); st = re.search(r'<span class="status ([^"]*)">([^<]*)<', it.group(2)); sr = re.search(r'class="show-for-sr">([^<]*)<', it.group(2))
                    if t: out.append({'resort': slug, 'sector': sector, 'kind': kind, 'color': it.group(1) or '', 'type': H.unescape(sr.group(1)) if sr else '', 'title': H.unescape(t.group(1)).strip(), 'status': st.group(2) if st else ''})
    json.dump(out, open(os.path.join(ROOT, 'qa', 'fixtures', 'official.json'), 'w'), ensure_ascii=False, indent=0)
    print('scraped', len(out))

def main():
    if '--scrape' in sys.argv: scrape()
    feedp = sys.argv[1]; dry = '--dry' in sys.argv
    p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf-8').read()
    a, b = jline(s, 'const BG = '); BG = json.loads(s[a:b].rstrip().rstrip(';'))
    a2, b2 = jline(s, 'const WEEKS = '); wl = s[a2:b2].rstrip().rstrip(';')
    WEEKS = json.loads(re.sub(r'([{,]\s*)(red|std|black):', r'\1"\2":', wl))
    vm = re.search(r"const VILLAGES = \{ type:'FeatureCollection', features: \[(.*?)\]\.map", s, re.S).group(1)
    VIL = {m[0]: (float(m[2]), float(m[3])) for m in re.findall(r"\['([^']+)',(\d+),([\d.]+),([\d.]+),'[a-z]+'\]", vm)}
    off = json.load(open(os.path.join(ROOT, 'qa', 'fixtures', 'official.json')))
    feed = json.load(open(feedp))
    # 1. catalog, one entry per (resort, kind, colour, name)
    cat = {}
    for o in off:
        if o['kind'] not in ('Ski lifts', 'Slopes'): continue
        grp = RESORTS.get(o['resort'], (None,))[0]
        if not grp: continue
        k = (grp, o['kind'], o['color'], n2(o['title']))
        cat.setdefault(k, {'resort': grp, 'sector': o['sector'], 'kind': o['kind'], 'color': o['color'], 'title': o['title'], 'n': n2(o['title'])})
    cat = list(cat.values())
    anchors = {}
    for _, (g, vs) in RESORTS.items(): anchors[g] = [VIL[v] for v in vs if v in VIL]
    for g, vs in EXTRA.items(): anchors[g] = [VIL[v] for v in vs if v in VIL]
    # 2. official -> intermaps oids
    fl = [(n2(x['popup']['title']), x['popup']) for x in feed['lifts']]
    fs = [(n2(x['popup']['title']), x['popup']) for x in feed['slopes']]
    for e in cat:
        pool = fl if e['kind'] == 'Ski lifts' else fs
        best = []
        for nm, pp in pool:
            sc = score(e['n'], nm)
            if e['kind'] == 'Slopes' and pp.get('difficulty') in COLD.get(e['color'], []): sc += .05
            if sc >= .88: best.append((sc, str(pp['oid'])))
        best.sort(reverse=True)
        e['oids'] = [o for sc, o in best if sc >= best[0][0] - .02] if best else []
    # 3. every named map line -> official entry
    by_name = collections.defaultdict(list)
    for e in cat: by_name[e['kind']].append(e)
    rename, liftmap, slopemap, oidres, unmatched = {}, {}, collections.defaultdict(list), {}, collections.Counter()
    lines = []
    for bi, l in enumerate(BG):
        kind = 'Ski lifts' if l[0] == 'L' else 'Slopes' if l[0] == 'R' else None
        if not kind or not l[2]: continue
        nn = n2(l[2]); cands = [(strict(nn, e['n']), e) for e in by_name[kind]]
        cands = [c for c in cands if c[0]]
        lines.append((bi, l, kind, cands))
    pts = collections.defaultdict(list)                       # pass 1: where each resort is
    for bi, l, kind, cands in lines:
        if cands and len({c[1]['resort'] for c in cands}) == 1: pts[cands[0][1]['resort']] += l[3][::4]
    for g, vs in list(anchors.items()):
        if g not in pts: pts[g] = list(vs)
    def near_res(pt, among=None):
        best, bd = None, 1e18
        for g, ps in pts.items():
            if among and g not in among: continue
            d = min(hav(pt, q) for q in ps[::max(1, len(ps) // 300)])
            if d < bd: bd, best = d, g
        return best
    global resort_of  # used by tools that import this
    resort_of = near_res
    for bi, l, kind, cands in lines:                          # pass 2
        if not cands: unmatched[(kind, l[2], near_res(l[3][len(l[3]) // 2]))] += 1; continue
        mid = l[3][len(l[3]) // 2]; col = BGC.get(l[1], '')
        res = near_res(mid, {c[1]['resort'] for c in cands})
        pick = [c for c in cands if c[1]['resort'] == res]
        if kind == 'Slopes' and len(pick) > 1:
            pc = [c for c in pick if c[1]['color'] == col]
            if pc: pick = pc
        top = max(c[0] for c in pick); best = [c[1] for c in pick if c[0] >= top - .001]
        rename[bi] = best[0]['title']
        oids = [o for x in best for o in x['oids']]
        if kind == 'Ski lifts':
            if oids: liftmap[str(bi)] = oids
        else:
            key = norm(l[2]) + '|' + res
            for o in oids:
                d = next((pp.get('difficulty') or '' for _, pp in fs if str(pp['oid']) == o), '')
                if [d, o] not in slopemap[key]: slopemap[key].append([d, o])
        for x in best:
            for o in x['oids']: oidres[o] = x['resort']
    for bi, l, kind, cands in lines:
        if kind != 'Slopes' or cands: continue
        nn = n2(l[2]); oids = []
        for part in [nn] + [n2(x) for x in re.split(r'\s+[–-]\s+', l[2]) if x.strip()]:
            for fn, pp in fs:
                if strict(part, fn): oids.append([pp.get('difficulty') or '', str(pp['oid'])])
        if oids:
            key = norm(l[2]) + '|*'
            for x in oids:
                if x not in slopemap[key]: slopemap[key].append(x)
            unmatched.pop((kind, l[2], near_res(l[3][len(l[3]) // 2])), None)
    respts = {g: [[round(q[0], 4), round(q[1], 4)] for q in ps[::max(1, len(ps) // 80)]] for g, ps in pts.items()}
    globals()['RESPTS'] = respts
    return s, BG, WEEKS, wl, (a, b, a2, b2), rename, liftmap, slopemap, oidres, unmatched, cat, dry, p

def write(s, p, liftmap, slopemap, oidres, respts):
    def put(name, obj):
        nonlocal s
        line = 'const ' + name + ' = ' + json.dumps(obj, separators=(',', ':'), ensure_ascii=False) + ';\n'
        if 'const ' + name + ' = ' in s: s = re.sub(r'const ' + name + r' = .*?;\n', lambda m: line, s, count=1)
        else: s = s.replace('const LIFTMAP = ', line + 'const LIFTMAP = ', 1)
    i, j = jline(s, 'const LIFTMAP = '); old = json.loads(s[i:j].rstrip().rstrip(';'))
    old.update(liftmap); put('LIFTMAP', old)
    put('SLOPEMAP2', slopemap); put('OIDRES', oidres); put('RESPTS', respts)
    open(p, 'w', encoding='utf-8').write(s)
if __name__ == '__main__':
    s, BG, WEEKS, wl, pos, rename, liftmap, slopemap, oidres, unmatched, cat, dry, p = main()
    print('official entries', len(cat), 'tied to the live feed', sum(1 for e in cat if e['oids']))
    print('map lines renamed', len(rename), 'lifts with live status', len(liftmap), 'slope names', len(slopemap))
    json.dump({'rename': rename, 'liftmap': liftmap, 'slopemap': slopemap, 'oidres': oidres,
               'unmatched': [[k[0], k[1], k[2], v] for k, v in unmatched.most_common()]},
              open(os.path.join(ROOT, 'tools', 'official_names.out.json'), 'w'), ensure_ascii=False, indent=0)
    if not dry: write(s, p, liftmap, slopemap, oidres, RESPTS); print('written')
