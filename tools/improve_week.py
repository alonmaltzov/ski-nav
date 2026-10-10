"""Re-plan the 'reds first' week inside the app's own code (headless Chrome), then write it back.
Usage: python3 tools/improve_week.py [variant] [opts.json]   (default red)"""
import json, os, sys, math
from playwright.sync_api import sync_playwright
V = sys.argv[1] if len(sys.argv) > 1 else 'red'
OPTS = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = os.path.join(ROOT, 'index.html')
src = open(H, encoding='utf-8').read()
js = open(os.path.join(ROOT, 'tools/improve_week.js'), encoding='utf-8').read()
anchor = 'window.__ski = {'
i = src.index(anchor); j = src.index('\n', i)
page = src[:j+1] + js + '\n' + src[j+1:]
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width': 390, 'height': 844})
    pg.add_init_script("localStorage.setItem('skinav-week2', JSON.stringify({variant:'%s', onb:1}))" % V)
    pg.route('**/index-improve.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=page))
    pg.route('**/*.tile*', lambda r: r.abort())
    pg.goto('http://skinav.local/index-improve.html')
    pg.wait_for_function('typeof window.__improveWeek === "function" && !!window.__ski', timeout=60000)
    res = pg.evaluate("([v, o]) => window.__improveWeek(v, o)", [V, OPTS])
    week = json.loads(pg.evaluate("v => window.__weekJSON(v)", V))
    b.close()
print('\n'.join(res['log']))
for d in res['days']: print(d)
# strip helper fields
for d in week:
    d.pop('_arriveS', None)
    for s in d['steps']: s.pop('_bi', None); s.pop('i', None)
json.dump(week, open(os.path.join(ROOT, 'tools', 'week_%s.json' % V), 'w'))
