"""Adds 'From home' practice day to nyc.html: M15 bus down 2nd Ave (a 'lift'), 86th St, John Finley Walk, home via York Ave."""
import json, math, sys
OSM = sys.argv[1]
H = 'nyc.html'
s = open(H).read()
def grab(name):
    i = s.index('const ' + name + ' = ') + len('const ' + name + ' = '); j = s.index('\n', i)
    import re
    txt = re.sub(r'([{,]\s*)(red|std|black)\s*:', r'\1"\2":', s[i:j].rstrip().rstrip(';'))
    return i, j, json.loads(txt)
def hav(a, b):
    R = 6371000; t = math.pi / 180
    h = math.sin((b[0]-a[0])*t/2)**2 + math.cos(a[0]*t)*math.cos(b[0]*t)*math.sin((b[1]-a[1])*t/2)**2
    return 2 * R * math.asin(math.sqrt(h))
def dens(pts, step=25):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(hav(a, b) // step))
        for k in range(1, n + 1): out.append((a[0] + (b[0]-a[0])*k/n, a[1] + (b[1]-a[1])*k/n))
    return [[round(p[0], 7), round(p[1], 7)] for p in out]
def length(c): return round(sum(hav(a, b) for a, b in zip(c, c[1:])))

X = json.load(open(OSM + '/xings.json'))
home = tuple(X['East 96th Street & 2nd Avenue'])
a2_86 = tuple(X['2nd Avenue & East 86th Street'])
y86 = tuple(X['York Avenue & East 86th Street']); e86 = tuple(X['East End Avenue & East 86th Street'])
y90 = tuple(X['York Avenue & East 90th Street']); e90 = tuple(X['East End Avenue & East 90th Street'])
# avenue/street steps on the Manhattan grid (from the measured crossings)
av = ((y90[0]-X['2nd Avenue & East 90th Street'][0]) / 2, (y90[1]-X['2nd Avenue & East 90th Street'][1]) / 2)  # one avenue east
st = ((X['2nd Avenue & East 90th Street'][0]-a2_86[0]) / 4, (X['2nd Avenue & East 90th Street'][1]-a2_86[1]) / 4)  # one street north
a1_86 = (a2_86[0]+av[0], a2_86[1]+av[1])
y96 = (y90[0]+6*st[0], y90[1]+6*st[1]); a1_96 = (home[0]+av[0], home[1]+av[1])
E = json.load(open(OSM + '/home.json'))['elements']
jfw = [(p['lat'], p['lon']) for e in E if e['id'] == 226015245 for p in e['geometry']]   # runs from ~90th south
# John Finley Walk point level with 86th St: closest to the 86th St line continued east
k86 = min(range(len(jfw)), key=lambda i: abs((jfw[i][0]-e86[0]) * av[1] - (jfw[i][1]-e86[1]) * av[0]))
walk = list(reversed(jfw[:k86 + 1]))          # 86th -> 90th, north
lift_c = dens([home, a2_86])
run1 = dens([a2_86, a1_86, y86, e86, walk[0]])
run2 = dens(walk, 15)
run3 = dens([walk[-1], e90, y90, y96, a1_96, home])

ALT = 10
def run(name, color, c, at):
    L = length(c)
    return {"type": "run", "name": name, "legs": [{"name": name, "color": color, "len": L}], "segs": [{"color": color, "c": c}], "color": color,
            "traverse": False, "coords": [[p[0], p[1], ALT] for p in c], "len": L, "top": ALT, "bottom": ALT, "at": at, "way": {"min": 10, "via": [], "by": "23:59"}}
lift = {"type": "lift", "name": "M15 bus, 96th to 86th", "drag": False, "len": length(lift_c), "bottom": ALT, "top": ALT, "at": "10:00",
        "way": {"min": 10, "via": [], "by": "23:59"}, "coords": [[p[0], p[1], ALT] for p in lift_c]}
steps = [lift, run("86th St to Carl Schurz Park", "red", run1, "10:08"), run("John Finley Walk", "blue", run2, "10:18"), run("Home via York Ave", "blue", run3, "10:25")]
km = round(sum(x["len"] for x in steps if x["type"] == "run") / 1000, 1)
day = {"day": 3, "date": "Any day", "title": "From home: bus, river, back", "lunch": None, "cutoff": "23:59", "homeStep": 3, "arrive": "10:45",
       "km": km, "vert": 0, "lifts": 1, "drags": 0, "start": {"name": "Home · 96th & 2nd", "lat": home[0], "lon": home[1]}, "end": {"name": "Home · 96th & 2nd", "lat": home[0], "lon": home[1]}, "steps": steps}

i, j, W = grab('WEEKS')
for v in W: W[v] = [d for d in W[v] if d['day'] != 3] + [day]
s = s[:i] + json.dumps(W, ensure_ascii=False, separators=(',', ':')) + ';' + s[j:]
i, j, G = grab('GROUPS')
G = [g for g in G if g['a'] != 'Home loop']
base = len(G)
G += [{"n": "86th St to Carl Schurz Park", "a": "Home loop", "c": "red"}, {"n": "John Finley Walk", "a": "Home loop", "c": "blue"}, {"n": "Home via York Ave", "a": "Home loop", "c": "blue"}]
s = s[:i] + json.dumps(G, ensure_ascii=False, separators=(',', ':')) + ';' + s[j:]
i, j, BG = grab('BG')
BG = [b for b in BG if not (len(b) > 5 and b[6] == 3 and b[7] == 3)]
BG += [["R", "int", "86th St to Carl Schurz Park", run1, 1, base, 3, 3, 3], ["R", "eas", "John Finley Walk", run2, 1, base + 1, 3, 3, 3],
       ["R", "eas", "Home via York Ave", run3, 1, base + 2, 3, 3, 3], ["L", "gon", "M15 bus (2nd Ave)", lift_c, 1, -1, 0, 0, 0]]
s = s[:i] + json.dumps(BG, ensure_ascii=False, separators=(',', ':')) + ';' + s[j:]
# a Home pin
ci = s.index('const CONFIG = ') + len('const CONFIG = '); cj = s.index('\n', ci)
C = json.loads(s[ci:cj].rstrip().rstrip(';'))
C['pins'] = [p for p in C['pins'] if p['label'] != 'Home'] + [{"label": "Home", "sub": "96th & 2nd", "lon": home[1], "lat": home[0], "cls": "home"}]
s = s[:ci] + json.dumps(C, ensure_ascii=False) + ';' + s[cj:]
open(H, 'w').write(s)
print('day 3:', km, 'km of runs,', [(x['name'], x['len']) for x in steps])
