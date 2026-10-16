"""Games: STOPPP after 3 minutes on a lift (3 a day, 11:00-15:00, rotating rounds), passport check
(first into Switzerland before noon), Speed King podium. Usage: python3 qa/games_test.py -> qa-out/web-games/"""
import asyncio, datetime, json, os
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.environ.get('QA_OUT', os.path.join(ROOT, 'qa-out')), 'web-games'); os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(OUT, 'log.txt'), 'w'); fails = []
def result(check, ok, detail=''):
    log.write('[web] QA RESULT ' + json.dumps({'check': check, 'ok': bool(ok), 'detail': str(detail)}) + '\n'); log.flush()
    print(('PASS ' if ok else 'FAIL ') + check + (' - ' + str(detail) if detail != '' else ''))
    if not ok: fails.append(check)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 393, 'height': 852}, device_scale_factor=2, is_mobile=True, has_touch=True)
        await ctx.add_init_script("localStorage.setItem('skinav-onb','1'); window.__QA_ACK=true; if(!localStorage.getItem('skinav-games')) localStorage.setItem('skinav-games', JSON.stringify({pass:{'2027-01-19':1}}));")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.clock.install(time=datetime.datetime(2027, 1, 19, 9, 0))
        await pg.goto('file://' + os.path.join(ROOT, 'index.html'))
        await pg.wait_for_function('window.__ski && window.__ski.map && window.__ski.steps', timeout=60000)
        plan = await pg.evaluate('window.__ski.stopPlan().map(s=>({n:s.n, h:new Date(s.at).getHours()+new Date(s.at).getMinutes()/60, who:s.who.name}))')
        result('3 STOPPPs a day', len(plan) == 3, plan)
        result('all between 11:00 and 15:00', all(11 <= x['h'] < 15 for x in plan), [round(x['h'], 2) for x in plan])
        again = await pg.evaluate('window.__ski.stopPlan().map(s=>s.at)')
        result('same times every time it is worked out', again == await pg.evaluate('window.__ski.stopPlan().map(s=>s.at)'))
        # a fix on a lift at 12:50, 3+ minutes after boarding
        t0 = await pg.evaluate('window.__ski.stopPlan()[0].at + 60000')
        await pg.clock.set_system_time(datetime.datetime.fromtimestamp(t0 / 1000 + 200))
        await pg.evaluate("window.__ski._mode('gps')")
        await pg.evaluate('''t0 => { const s=window.__ski.st; s.onLift=true;
            window.__ski.gamesOnFix({lat:46.19, lon:6.77, acc:8, t:t0}, true);
            window.__ski.gamesOnFix({lat:46.191, lon:6.771, acc:8, t:t0+190000}, true); }''', t0)
        await pg.wait_for_timeout(500)
        result('STOPPP shows after 3 minutes on a lift', await pg.is_visible('#stopSheet'), await pg.inner_text('#stopWho'))
        await pg.screenshot(path=os.path.join(OUT, '01-stoppp.png'))
        await pg.click('#stopOk')
        fired = await pg.evaluate('JSON.stringify(window.__ski.games.fired)')
        result('only one STOPPP fires', sum(len(v) for v in json.loads(fired).values()) == 1, fired)
        await pg.evaluate('''t0 => window.__ski.gamesOnFix({lat:46.19, lon:6.77, acc:8, t:t0+250000}, true)''', t0)
        result('the same STOPPP does not fire twice', not await pg.is_visible('#stopSheet'))
        # the passport race is retired: crossing into Switzerland shows nothing
        await pg.clock.set_system_time(datetime.datetime(2027, 1, 20, 10, 5))
        tb = await pg.evaluate('Date.now()')
        await pg.evaluate('''t => { window.__ski.st.onLift=false; window.__ski.gamesOnFix({lat:46.1838, lon:6.8355, acc:8, t}, true); }''', tb)
        await pg.wait_for_timeout(400)
        result('no passport race popup on the first crossing', not await pg.is_visible('#borderSheet'))
        # STOPPP button on the map, like the crown
        result('STOPPP button shows today\'s count', await pg.is_visible('#stopBtn') and (await pg.inner_text('#stopBtnTxt')) == '1/3', await pg.inner_text('#stopBtnTxt'))
        await pg.click('#stopBtn'); await pg.wait_for_timeout(300)
        result('STOPPP button opens today\'s 3 rounds', await pg.is_visible('#stopInfo') and await pg.locator('#siList .gzrank').count() == 3)
        await pg.screenshot(path=os.path.join(OUT, '02-stoppp-today.png'))
        before = await pg.evaluate('JSON.stringify(window.__ski.games.fired)')
        await pg.click('#siTry'); await pg.wait_for_timeout(400)
        result('Try it now: a test STOPPP that says so', await pg.is_visible('#stopSheet') and 'Test' in await pg.inner_text('#stopNum'), await pg.inner_text('#stopNum'))
        result('the test doesn\'t count', await pg.evaluate('JSON.stringify(window.__ski.games.fired)') == before)
        await pg.click('#stopSkip'); await pg.wait_for_timeout(200)
        result('"Not me today" on a test keeps you in the rounds', await pg.evaluate('window.__ski.games.rounds') is not False)
        # Speed King
        await pg.evaluate('''() => { const g=window.__ski.games; const d=new Date(); const k=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'); g.top[k]=20.6; window.__ski.showKing(); }''')
        await pg.wait_for_timeout(400)
        result('Speed King podium', await pg.is_visible('#kingSheet') and await pg.locator('#kingPod .gzstep').count() >= 1, await pg.inner_text('#kingLine'))
        await pg.screenshot(path=os.path.join(OUT, '03-speed-king.png'))
        await pg.click('#kingOk')
        await pg.evaluate("document.getElementById('gamesBtn').click()"); await pg.wait_for_timeout(400)
        result('Settings > Games lists today’s rounds', await pg.locator('#gToday .gzrank').count() == 3)
        await pg.screenshot(path=os.path.join(OUT, '04-games.png'))
        await pg.click('#gStop'); result('STOPPP can be switched off', await pg.get_attribute('#gStop', 'aria-pressed') == 'false')
        result('no page errors', not errs, errs[:3])
        await b.close()
    print('\n%d failed' % len(fails)); raise SystemExit(1 if fails else 0)
asyncio.run(main())
