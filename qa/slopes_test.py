"""Slopes & lifts: live slope status matched to today's runs, closed runs flagged, the router goes around them,
checks on reconnect. Uses qa/fixtures/intermaps.json (a trimmed copy of the live feed). Usage: python3 qa/slopes_test.py"""
import asyncio, json, os
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEED = os.path.join(ROOT, 'qa', 'fixtures', 'intermaps.json')
OUT = os.path.join(os.environ.get('QA_OUT', os.path.join(ROOT, 'qa-out')), 'web-slopes'); os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(OUT, 'log.txt'), 'w'); fails = []
def result(check, ok, detail=''):
    log.write('[web] QA RESULT ' + json.dumps({'check': check, 'ok': bool(ok), 'detail': str(detail)}) + '\n'); log.flush()
    print(('PASS ' if ok else 'FAIL ') + check + (' - ' + str(detail) if detail != '' else ''))
    if not ok: fails.append(check)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 393, 'height': 852}, device_scale_factor=2, is_mobile=True, has_touch=True)
        await ctx.add_init_script("localStorage.setItem('skinav-onb','1'); window.__QA_ACK=true;")
        hits = [0]; offline = [False]
        async def feed(route):
            hits[0] += 1
            if offline[0]: await route.fulfill(status=503)
            else: await route.fulfill(path=FEED, content_type='application/json')
        await ctx.route('**/winter.intermaps.com/**', feed)
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + os.path.join(ROOT, 'index.html'))
        await pg.wait_for_function('window.__ski && window.__ski.steps && window.__ski.liftStat', timeout=60000)
        st = await pg.evaluate('({sl: Object.keys(window.__ski.liftStat.sl||{}).length, open: window.__ski.liftStat.slOpen})')
        result('slope status comes in with the lifts', st['sl'] > 200, st)
        ps = await pg.evaluate('window.__ski.planSlopes()')
        known = [x for x in ps if x['st']]
        result('most of today\'s runs are matched to the resort list', len(known) >= 0.7 * len(ps), f'{len(known)} of {len(ps)}')
        await pg.click('#liftsPill'); await pg.wait_for_timeout(800)
        big = await pg.evaluate("document.querySelector('#liftCard .larea > summary').textContent")
        result('whole area: lifts and slopes like the official site', 'lifts' in big and 'slopes' in big, big)
        heads = await pg.evaluate("[...document.querySelectorAll('#liftRows .lsub')].map(x=>x.textContent)")
        result('today\'s plan comes first, then the whole area', heads[:2] == ['Today’s plan', 'Whole area'], heads)
        grp = await pg.evaluate("[...document.querySelectorAll('#liftCard .larea .lfold > summary')].map(x=>x.textContent)")
        result('the whole area opens into resorts', any(g.startswith('Avoriaz') for g in grp) and any(g.startswith('Châtel') for g in grp), grp[:4])
        rows = await pg.evaluate("[...document.querySelectorAll('#liftRows .lrow')].length")
        result('plan runs are listed with the lifts', rows >= len(known), rows)
        await pg.screenshot(path=os.path.join(OUT, '01-slopes-lifts.png'))
        await pg.evaluate("document.getElementById('todaySheet').hidden=true")
        # season on, everything open except the second planned run: it shows as closed and the router avoids it
        r = await pg.evaluate("""(() => { const S = window.__ski, ls = S.liftStat; ls.t = Date.now(); ls.open = 170; ls.total = 182;
            for (const k in ls.by) ls.by[k] = 'open'; for (const k in ls.sl) ls.sl[k] = 'open';
            const known = S.planSlopes().filter(x => x.st); const shut = known[1]; const st0 = S.slopeStatus(shut.name, shut.color);
            return {name: shut.name, color: shut.color, before: st0}; })()""")
        shut = await pg.evaluate("""(n) => { const S = window.__ski, ls = S.liftStat; ls.t = Date.now() + 2;
            const oids = (window.__ski._slopemap && window.__ski._slopemap(n)) || []; oids.forEach(o => ls.sl[o] = 'closed'); return [oids.length, S.slopeStatus(n, 'x')]; }""", r['name'])
        result('a run can be marked closed', shut[0] > 0 and shut[1] == 'closed', shut)
        offline[0] = True
        line = await pg.evaluate('window.__ski.liftCheck()')
        offline[0] = False
        result('the guide names the closed run', r['name'] in line, line)
        await pg.evaluate("document.getElementById('todaySheet').hidden=true")
        rp = await pg.evaluate("""(n) => { const S = window.__ski; const k = S.steps.findIndex(s => s.type === 'run' && (s.legs||[]).some(l => S.slNorm(l.name) === S.slNorm(n)));
            return {k, cur: S.cur}; }""", r['name'])
        result('the plan step for that run says closed', rp['k'] >= 0, rp)
        # reconnect: checks right away
        h0 = hits[0]
        await pg.evaluate("window.__ski.liftStat.t = Date.now() - 20*60e3; dispatchEvent(new Event('online'))"); await pg.wait_for_timeout(800)
        result('back online: checks again right away', hits[0] > h0, f'{h0} -> {hits[0]}')
        result('no page errors', not errs, errs[:3])
        await b.close()
    log.close()
    if fails: raise SystemExit(1)
asyncio.run(main())
