"""Map lines redesign checks: route done/ahead split, daily steps fold, track breaks on Start (no straight
lines across a gap), cafes hidden while tracking, only the next step labelled, Clear tracking history.
Usage: python3 qa/lines_test.py  ->  qa-out/web-lines/ (log.txt + screenshots)"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.environ.get('QA_OUT', os.path.join(ROOT, 'qa-out')), 'web-lines')
os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(OUT, 'log.txt'), 'w'); fails = []; n = [0]

def result(check, ok, detail=''):
    log.write('[web] QA RESULT ' + json.dumps({'check': check, 'ok': bool(ok), 'detail': str(detail)}) + '\n'); log.flush()
    print(('PASS ' if ok else 'FAIL ') + check + (' - ' + str(detail) if detail else ''))
    if not ok: fails.append(check)

async def shot(pg, name):
    n[0] += 1; await pg.wait_for_timeout(900); await pg.screenshot(path=os.path.join(OUT, f'{n[0]:02d}-{name}.png'))

async def page(b, file, geo):
    ctx = await b.new_context(viewport=dict(width=393, height=852), device_scale_factor=2, is_mobile=True, has_touch=True,
                              geolocation=geo, permissions=['geolocation'])
    await ctx.add_init_script('window.__QA_ACK=true;')
    pg = await ctx.new_page()
    pg.on('pageerror', lambda e: (log.write(f'[{file}] ERROR {e}\n'), fails.append(f'{file} page error: {e}')))
    await pg.goto('file://' + os.path.join(ROOT, file))
    await pg.wait_for_function('window.__ski && window.__ski.map && window.__ski.map.loaded() && window.__ski.steps && window.__ski.steps.length', timeout=60000)
    await pg.wait_for_timeout(800)
    return ctx, pg

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])

        # ---------- Avoriaz ----------
        ctx, pg = await page(b, 'index.html', {'latitude': 46.19331, 'longitude': 6.76815})
        d = await pg.evaluate('[...window.__ski.dailySet()]')
        last = await pg.evaluate('window.__ski.steps.length')
        result('daily steps found (first lift in the morning, home run)', 0 in d and 1 in d and (last - 2) in d, d)

        await pg.evaluate("document.getElementById('stepsBtn').click()")
        await pg.wait_for_timeout(600)
        folds = await pg.locator('#stepList .srow.fold').count()
        result('daily steps fold into one row each in Steps', folds == 2, folds)
        txt = await pg.inner_text('#stepList .srow.fold >> nth=0')
        result('morning row says it is the same every day', 'Every morning' in txt and 'Same every day' in txt, txt.replace('\n', ' | '))
        await shot(pg, 'steps-folded')
        await pg.click('#stepList .srow.fold >> nth=0'); await pg.wait_for_timeout(300)
        result('tapping the row shows the steps', await pg.locator('#stepList .srow.fold').count() == 0)
        await pg.evaluate("document.getElementById('sheet').hidden=true")

        # replay to the middle of a run
        await pg.click('#menuBtn'); await pg.wait_for_timeout(400)
        await pg.evaluate("document.getElementById('settingsBtn').click()")
        await pg.evaluate("document.getElementById('simBtn').click()"); await pg.wait_for_timeout(400)
        await pg.evaluate("(()=>{ const x=document.querySelector('#simSheet [data-x=\"100\"]'); x && x.click(); })()")
        await pg.evaluate("document.getElementById('simStart').click()"); await pg.evaluate("document.getElementById('closeSim') && document.getElementById('closeSim').click()")
        await pg.evaluate("document.getElementById('drawer').hidden=true")
        await pg.wait_for_timeout(14000)
        rd = await pg.evaluate('window.__ski.routeData().features.map(f=>f.properties)')
        cur = await pg.evaluate('window.__ski.cur')
        result('replay moved along the plan', cur >= 2, 'step ' + str(cur + 1))
        result('done steps are drawn filled in (not removed)', any(p['done'] for p in rd), sum(1 for p in rd if p['done']))
        result('steps ahead are drawn as an outline', any((not p['done']) and (not p['lift']) for p in rd))
        result('daily steps are marked', any(p.get('daily') for p in rd))
        filt = await pg.evaluate("JSON.stringify(window.__ski.map.getFilter('pois'))")
        result('cafes and restaurants hide while tracking', 'none' in filt, filt[:80])
        vis_markers = await pg.evaluate("[...document.querySelectorAll('.stepnum')].filter(e=>!e.hidden).map(e=>e.textContent)")
        result('only the next step is labelled while tracking', len(vis_markers) == 1 and vis_markers[0].startswith('Next'), vis_markers)
        chip = await pg.evaluate("(()=>{ const c=document.getElementById('doneChip'); return c.hidden ? '' : c.textContent; })()")
        result('done today chip shows', ' done' in chip, chip)
        layers = await pg.evaluate("window.__ski.map.getStyle().layers.map(l=>l.id)")
        result('your track is drawn above the route', layers.index('trail') > layers.index('route-core'), '')
        await pg.evaluate("window.__ski.map.jumpTo({center: window.__ski.map.getCenter(), zoom: 15})")
        await shot(pg, 'avoriaz-tracking')
        await pg.evaluate("window.__ski.stopSim()"); await pg.wait_for_timeout(800)
        vis_markers = await pg.evaluate("[...document.querySelectorAll('.stepnum')].filter(e=>!e.hidden).length")
        result('step numbers come back when you stop', vis_markers > 3, vis_markers)
        await ctx.close()

        # ---------- NYC: Start, walk, Stop, walk without tracking, Start again ----------
        ctx, pg = await page(b, 'nyc.html', {'latitude': 40.78468, 'longitude': -73.94745})
        await pg.evaluate("window.__ski.st.trail=[]")
        await pg.click('#goBtn'); await pg.wait_for_timeout(800)
        t0 = 1_800_000_000_000
        walk1 = [[40.78468 - k * 0.0002, -73.94745 + k * 0.00012] for k in range(8)]
        for k, (la, lo) in enumerate(walk1):
            await pg.evaluate('([a,b,t]) => window.__ski.onFix({lat:a, lon:b, acc:8, speed:1.4, t:t})', [la, lo, t0 + k * 5000])
        await pg.click('#goBtn'); await pg.wait_for_timeout(500)          # stop
        await pg.evaluate("document.getElementById('recapClose') && document.getElementById('recapClose').click()")
        await pg.click('#goBtn'); await pg.wait_for_timeout(500)          # start again, 2 blocks away
        walk2 = [[40.7815 - k * 0.0002, -73.9520 + k * 0.00012] for k in range(6)]
        for k, (la, lo) in enumerate(walk2):
            await pg.evaluate('([a,b,t]) => window.__ski.onFix({lat:a, lon:b, acc:8, speed:1.4, t:t})', [la, lo, t0 + 600000 + k * 5000])
        fc = await pg.evaluate('window.__ski.trailFC()')
        segs = [f['geometry']['coordinates'] for f in fc['features']]
        def jump(c):
            import math
            return max((math.hypot((c[i+1][0]-c[i][0])*84000, (c[i+1][1]-c[i][1])*111000) for i in range(len(c)-1)), default=0)
        result('Stop then Start leaves a gap, no straight line across town', len(segs) >= 2 and max(jump(c) for c in segs) < 150, '%d pieces, longest hop %.0f m' % (len(segs), max(jump(c) for c in segs)))
        # a jump while tracking (phone off, GPS lost) also breaks the line
        await pg.evaluate('([a,b,t]) => window.__ski.onFix({lat:a, lon:b, acc:8, speed:1.4, t:t})', [40.7760, -73.9480, t0 + 900000])
        await pg.evaluate('([a,b,t]) => window.__ski.onFix({lat:a, lon:b, acc:8, speed:1.4, t:t})', [40.77585, -73.94792, t0 + 905000])
        fc = await pg.evaluate('window.__ski.trailFC()')
        segs = [f['geometry']['coordinates'] for f in fc['features']]
        result('a GPS jump while tracking also leaves a gap', max(jump(c) for c in segs) < 150, '%d pieces' % len(segs))
        await pg.evaluate("window.__ski.map.fitBounds([[-73.9535,40.7745],[-73.9465,40.7855]], {padding:40, duration:0})")
        await shot(pg, 'nyc-track-gap')
        await pg.click('#goBtn'); await pg.wait_for_timeout(500)
        await pg.evaluate("document.getElementById('recapClose') && document.getElementById('recapClose').click()")

        # Clear tracking history
        before = await pg.evaluate('window.__ski.st.trail.length')
        await pg.click('#menuBtn'); await pg.wait_for_timeout(400)
        await pg.evaluate("document.getElementById('settingsBtn').click()")
        await pg.wait_for_timeout(400)
        await shot(pg, 'settings-clear')
        await pg.click('#clearHist'); await pg.wait_for_timeout(200)
        result('clear asks for a second tap', 'Tap again' in await pg.inner_text('#clearHist'))
        await pg.click('#clearHist'); await pg.wait_for_timeout(800)
        after = await pg.evaluate('window.__ski.st.trail.length')
        stored = await pg.evaluate("(()=>{ for(const k of Object.keys(localStorage)){ try{ const v=JSON.parse(localStorage.getItem(k)); if(v && v.days) return JSON.stringify(Object.values(v.days).map(d=>[(d.trail||[]).length, d.dist||0])); }catch(e){} } return 'none'; })()")
        result('Clear tracking history empties the track and the saved days', before > 0 and after == 0 and all(x == [0, 0] for x in json.loads(stored)), '%d -> %d points, saved days %s' % (before, after, stored[:40]))
        await ctx.close(); await b.close()
    log.write('[web] QA DONE\n'); log.close()
    print('\n%d failed' % len(fails)); sys.exit(1 if fails else 0)

asyncio.run(main())
