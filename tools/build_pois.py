"""Rebuild the map's places (POIS) from current OpenStreetMap data, keeping only what's open in winter.
Usage: python3 tools/build_pois.py avo|nyc <osm json files...>  -> prints JSON list to stdout, report to stderr.
Entry format: [category, name, lon, lat, label, altitude_m]."""
import json, re, sys, urllib.request, urllib.parse

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
MRANGE = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?: \d{1,2})?(?:-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?: \d{1,2})?)?'

def months_of(spec):
    out = set()
    for part in spec.split(','):
        ms = re.findall(r'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec', part)
        if not ms: continue
        a = MONTHS.index(ms[0]); b = MONTHS.index(ms[-1])
        i = a
        while True:
            out.add(i)
            if i == b: break
            i = (i + 1) % 12
    return out

def open_in(oh, month):
    """False if the opening hours say the place is closed in that month (0 = Jan)."""
    if not oh: return True
    s = oh.strip().lower()
    if s in ('closed', 'off', '"closed"') or s.startswith('off ') or 'closed"' in s: return False
    open_m, closed_m, any_months = set(), set(), False
    for rule in oh.split(';'):
        m = re.match(r'\s*(' + MRANGE + r'(?:,' + MRANGE + r')*)\b(.*)', rule)
        if not m: continue
        any_months = True
        ms = months_of(m.group(1))
        if re.search(r'\b(off|closed)\b', m.group(2)): closed_m |= ms
        else: open_m |= ms
    if month in closed_m: return False
    if any_months and open_m and month not in open_m: return False
    return True

def cap(s): return s[:1].upper() + s[1:]
def cuisine(t): return ', '.join(cap(x.strip().replace('_', ' ')) for x in t.get('cuisine', '').split(';') if x.strip())

# summer-only or not useful to skiers in January
DROP_NAME = re.compile(r"luge d'été|tennis|pataugeoire|gymnase|stade|terrain de foot|wibit|indiana parc|organic adventure|arbr'acadabra|cascade aventure|secteur de l'oeil|scierie|place de l'office", re.I)

def classify(t, region):
    a, sh, tour, lei = t.get('amenity'), t.get('shop'), t.get('tourism'), t.get('leisure')
    oh = t.get('opening_hours', '')
    hours = (', ' + oh) if oh and len(oh) <= 60 else ''
    if a in ('restaurant', 'fast_food') or (tour == 'alpine_hut' and t.get('name')):
        c = cuisine(t); return 'food', (c + hours.replace(', ', ', ', 1) if c else (oh if oh and len(oh) <= 60 else ('Alpine hut' if tour == 'alpine_hut' else 'Restaurant' if a == 'restaurant' else 'Fast food')))
    if a in ('cafe', 'ice_cream'): return 'drink', ('Café' if a == 'cafe' else 'Ice cream') + hours
    if a in ('bar', 'pub', 'biergarten'): return 'drink', ('Pub' if a == 'pub' else 'Bar') + hours
    if a == 'toilets': return 'svc', 'Toilets'
    if a == 'pharmacy': return 'svc', 'Pharmacy'
    if a == 'drinking_water': return 'svc', 'Water fountain'
    if a == 'bicycle_rental': return 'svc', 'Citi Bike' if 'citi' in (t.get('brand', '') + t.get('network', '') + t.get('operator', '')).lower() else 'Bike rental'
    if sh in ('ski', 'sports'): return 'svc', 'Ski shop / rental' if region == 'avo' else 'Sports shop'
    if sh == 'bicycle': return 'svc', 'Bike shop'
    if sh == 'supermarket': return 'svc', 'Supermarket'
    if sh == 'bakery': return 'svc', 'Bakery'
    if t.get('piste:type') == 'snow_park': return 'park', 'Snow park'
    if tour == 'viewpoint': return 'view', 'Viewpoint'
    if tour == 'museum': return 'fun', 'Museum'
    if tour == 'attraction': return 'fun', 'Attraction'
    if lei == 'ice_rink': return 'fun', 'Ice skating'
    if lei == 'sports_centre':
        sp = t.get('sport', '').replace(';', ', ').replace('_', ' ')
        return 'fun', 'Sports centre' + (' · ' + sp if sp else '')
    if lei == 'swimming_pool' or lei == 'water_park':
        if region == 'avo' and t.get('indoor') != 'yes' and t.get('covered') != 'yes' and lei != 'water_park': return None, None
        return 'fun', 'Swimming pool'
    if lei == 'park': return 'park', 'Park'
    if lei == 'playground': return 'park', 'Playground'
    if lei == 'dog_park': return 'park', 'Dog run'
    return None, None

def name_of(t):
    n = t.get('name', '')
    if re.search('[Ѐ-ӿ]', n): n = t.get('name:en') or t.get('name:fr') or ''
    return n.strip()

def elevations(pts, html='index.html'):
    """Altitude from the terrain tiles already embedded in the app (Terrarium PNGs), best zoom first."""
    import base64, io, math
    from PIL import Image
    s = open(html).read(); i = s.index('const DEM = ') + len('const DEM = '); j = s.index('\n', i)
    D = json.loads(s[i:j].rstrip().rstrip(';')); cache = {}
    def at(lon, lat):
        for z in (13, 12, 11, 10):
            n = 2 ** z; x = (lon + 180) / 360 * n
            y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
            k = f'{z}/{int(x)}/{int(y)}'
            if k not in D: continue
            if k not in cache: cache[k] = Image.open(io.BytesIO(base64.b64decode(D[k]))).convert('RGB')
            im = cache[k]; r, g, b = im.getpixel((int((x % 1) * im.width), int((y % 1) * im.height)))
            return int(round(r * 256 + g + b / 256 - 32768))
        return 0
    return [at(lon, lat) for lon, lat in pts]

def main():
    region = sys.argv[1]; files = sys.argv[2:]
    seen, out, dropped = set(), [], []
    for f in files:
        for e in json.load(open(f))['elements']:
            t = e.get('tags', {}); lat = e.get('lat') or e.get('center', {}).get('lat'); lon = e.get('lon') or e.get('center', {}).get('lon')
            if lat is None: continue
            key = (e['type'], e['id'])
            if key in seen: continue
            seen.add(key)
            cat, label = classify(t, region)
            if not cat: continue
            n = name_of(t)
            if not n:
                if cat == 'svc' and label in ('Toilets', 'Water fountain', 'Citi Bike', 'Bike rental'): n = label if label != 'Citi Bike' else 'Citi Bike dock'
                elif cat == 'park' and region == 'avo': n = 'Snow park'
                else: continue
            if region == 'avo':
                if DROP_NAME.search(n) or (t.get('sport') == 'tennis'): dropped.append((n, 'summer / not for skiers')); continue
                if 'summer' in t.get('seasonal', '') and 'winter' not in t.get('seasonal', ''): dropped.append((n, 'summer only')); continue
                if not open_in(t.get('opening_hours', ''), 0): dropped.append((n, 'closed in January: ' + t.get('opening_hours', ''))); continue
            else:
                if t.get('opening_hours', '').strip().lower() in ('closed', 'off'): dropped.append((n, 'closed')); continue
            if any(k.startswith(('disused:', 'abandoned:')) for k in t): dropped.append((n, 'disused')); continue
            out.append([cat, n, round(lon, 5), round(lat, 5), label])
    if region == 'avo':
        # one marker per snow park (OSM draws The Stash and Chapelle as several pieces)
        for p in out:
            if p[0] == 'park' and 'Stash' in p[1] and 'Lil' not in p[1]: p[1] = 'The Stash'
            if p[0] == 'park' and p[1] == 'Chapelle': p[1] = 'Snowpark Chapelle'
            if p[0] == 'park' and p[1] == 'Arare': p[1] = 'Snowpark Arare'
        merged = []
        for p in out:
            if p[0] == 'park' and any(q[0] == 'park' and q[1] == p[1] and p[1] != 'Snow park' for q in merged): continue
            merged.append(p)
        out = merged
        # keep the winter extras the first build took from piste data (snowcross, sledging, ice rinks) if OSM still has nothing there
        try:
            src = open('index.html').read(); i = src.index('const POIS = ') + len('const POIS = ')
            old = json.loads(src[i:src.index('\n', i)].rstrip().rstrip(';'))
            for q in old:
                if q[4] in ('Snowcross', 'Toboggan', 'Sledging', 'Ice skating') and not DROP_NAME.search(q[1]) and not any(abs(q[2] - p[2]) < 0.002 and abs(q[3] - p[3]) < 0.0015 and p[0] == q[0] for p in out):
                    out.append(q[:5])
        except ValueError: pass
    # same name + category within 60 m: keep one (e.g. a snow park drawn as several shapes)
    uniq = []
    for p in out:
        if any(q[0] == p[0] and q[1] == p[1] and abs(q[2] - p[2]) < 0.0008 and abs(q[3] - p[3]) < 0.0006 for q in uniq): continue
        uniq.append(p)
    alts = elevations([(p[2], p[3]) for p in uniq]) if region == 'avo' else [0] * len(uniq)
    for p, a in zip(uniq, alts): p.append(a)
    print(json.dumps(uniq, ensure_ascii=False, separators=(',', ':')))
    from collections import Counter
    print('kept', len(uniq), dict(Counter(p[0] for p in uniq)), file=sys.stderr)
    for d in dropped: print('dropped', d, file=sys.stderr)

if __name__ == '__main__': main()
