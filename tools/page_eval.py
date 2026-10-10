"""Run JS inside the app's own scope (headless Chrome) and print the JSON result.
Usage: python3 tools/page_eval.py file.js 'expression' [variant] [index.html]"""
import json, os, sys
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
js = open(sys.argv[1], encoding='utf-8').read(); expr = sys.argv[2]
V = sys.argv[3] if len(sys.argv) > 3 else 'red'
H = sys.argv[4] if len(sys.argv) > 4 else os.path.join(ROOT, 'index.html')
src = open(H, encoding='utf-8').read()
anchor = 'window.__ski = {'; i = src.index(anchor); j = src.index('\n', i)
page = src[:j+1] + js + '\n' + src[j+1:]
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width': 390, 'height': 844})
    pg.add_init_script("localStorage.setItem('skinav-week2', JSON.stringify({variant:'%s', onb:1}))" % V)
    pg.route('**/index-eval.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=page))
    pg.route('**/*.tile*', lambda r: r.abort())
    pg.goto('http://skinav.local/index-eval.html')
    pg.wait_for_function('!!window.__ski', timeout=60000)
    out = pg.evaluate('async () => JSON.stringify(await (%s))' % expr)
    b.close()
sys.stdout.write(out)
