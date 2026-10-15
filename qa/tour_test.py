"""First-time tour: 5 steps over the real screen, Skip, Replay from Settings, joiners greeted by name.
Usage: python3 qa/tour_test.py -> qa-out/web-tour/ (log.txt + a screenshot per step, iPhone 16 and SE)"""
import asyncio, datetime, json, os
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.environ.get('QA_OUT', os.path.join(ROOT, 'qa-out')), 'web-tour'); os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(OUT, 'log.txt'), 'w'); fails = []
def result(check, ok, detail=''):
    log.write('[web] QA RESULT ' + json.dumps({'check': check, 'ok': bool(ok), 'detail': str(detail)}) + '\n'); log.flush()
    print(('PASS ' if ok else 'FAIL ') + check + (' - ' + str(detail) if detail != '' else ''))
    if not ok: fails.append(check)
GEOM = '''() => { const b = document.getElementById('tourBub').getBoundingClientRect(), rings = [...document.querySelectorAll('#tourRings .tring')].map(r => r.getBoundingClientRect());
  return {top: b.top, bottom: b.bottom, h: innerHeight, rings: rings.length, overlap: rings.some(r => !(r.bottom <= b.top || r.top >= b.bottom || r.right <= b.left || r.left >= b.right)),
          text: document.getElementById('tourTxt').innerText, next: document.getElementById('tourNext').innerText, view: window.__ski.tour.i}; }'''
async def device(p, name, vp):
    b = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
    ctx = await b.new_context(viewport=vp, device_scale_factor=2, is_mobile=True, has_touch=True)
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: (errs.append(str(e)), print('PAGEERROR', name, str(e)[:300])))
    await pg.clock.install(time=datetime.datetime(2027, 1, 17, 8, 40))
    await pg.goto('file://' + os.path.join(ROOT, 'index.html'))
    await pg.wait_for_function('window.__ski && window.__ski.map && window.__ski.steps', timeout=60000)
    await pg.clock.run_for(1500)
    result(f'[{name}] tour opens on first launch', await pg.is_visible('#tourBub'))
    result(f'[{name}] no clip over the tour', 'today' not in await pg.evaluate('window.__ski.sfx.log'), await pg.evaluate('window.__ski.sfx.log'))
    want = [(0, 'Allow location'), (1, 'Next'), (2, 'Next'), (2, 'Next'), (1, 'Let’s ski')]
    for k, (rings, nxt) in enumerate(want):
        await pg.wait_for_timeout(700)
        g = await pg.evaluate(GEOM)
        await pg.screenshot(path=os.path.join(OUT, f'{name}-{k + 1}.png'))
        result(f'[{name}] step {k + 1}: bubble on screen, nothing it points at is covered', g['top'] >= 0 and g['bottom'] <= g['h'] and g['rings'] == rings and not g['overlap'], {kk: g[kk] for kk in ('top', 'bottom', 'h', 'rings', 'overlap')})
        result(f'[{name}] step {k + 1}: button says {nxt}', g['next'] == nxt, g['next'])
        if k == 3: result(f'[{name}] step 4 opens the week', await pg.evaluate("document.getElementById('progPanel') && !document.getElementById('progPanel').hidden && document.getElementById('progPanel').offsetParent!==null"))
        await pg.click('#tourNext')
    await pg.wait_for_timeout(1500)
    result(f'[{name}] Let’s ski closes the tour and remembers it', not await pg.is_visible('#onb') and await pg.evaluate("localStorage.getItem('skinav-onb')") == '1')
    result(f'[{name}] back on today, not the week', await pg.evaluate("window.__ski.tour.i") == -1 and await pg.is_visible('#goBtn'))
    result(f'[{name}] today\'s clip plays after the tour', 'today' in await pg.evaluate('window.__ski.sfx.log'), await pg.evaluate('window.__ski.sfx.log'))
    # replay from Settings, skip halfway
    await pg.click('#menuBtn'); await pg.wait_for_timeout(500)
    if await pg.is_visible('#settingsBtn'): await pg.click('#settingsBtn'); await pg.wait_for_timeout(400)
    result(f'[{name}] Replay the tour is in Settings (Tour button)', await pg.is_visible('#tourBtn'))
    if name == 'iphoneSE':
        sb = await pg.evaluate("(()=>{ const e=document.getElementById('tourBtn'); const r=e.getBoundingClientRect(); return [r.bottom, innerHeight]; })()")
        result(f'[{name}] Settings still fit without scrolling', sb[0] <= sb[1], sb)
    await pg.screenshot(path=os.path.join(OUT, f'{name}-settings.png'))
    await pg.click('#tourBtn'); await pg.wait_for_timeout(500)
    result(f'[{name}] Replay starts at step 1', await pg.is_visible('#tourBub') and await pg.evaluate('window.__ski.tour.i') == 0)
    await pg.click('#tourNext'); await pg.wait_for_timeout(500); await pg.click('#tourNext'); await pg.wait_for_timeout(500); await pg.click('#tourNext'); await pg.wait_for_timeout(700)
    await pg.click('#tourSkip'); await pg.wait_for_timeout(500)
    result(f'[{name}] Skip on the week step closes the tour and the week', not await pg.is_visible('#onb') and await pg.is_visible('#goBtn'))
    # a friend who joined
    await pg.evaluate("window.__ski.showOnb({name:'Dana'})"); await pg.wait_for_timeout(500)
    t = await pg.inner_text('#tourTxt')
    result(f'[{name}] friends who join are greeted by name', t.startswith('Hi Dana, welcome to'), t[:60])
    await pg.screenshot(path=os.path.join(OUT, f'{name}-join.png'))
    await pg.click('#tourSkip')
    result(f'[{name}] no page errors', not errs, errs[:3])
    await b.close()
async def main():
    async with async_playwright() as p:
        await asyncio.gather(device(p, 'iphone16', {'width': 393, 'height': 852}), device(p, 'iphoneSE', {'width': 375, 'height': 667}))
    log.close()
    if fails: raise SystemExit(1)
asyncio.run(main())
