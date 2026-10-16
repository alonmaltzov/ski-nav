"""Passport check: Swiss days show a check you can only leave by sliding; the crew list; nudges bring it back.
Usage: python3 qa/passport_test.py -> qa-out/web-passport/"""
import asyncio, datetime, json, os
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.environ.get('QA_OUT', os.path.join(ROOT, 'qa-out')), 'web-passport'); os.makedirs(OUT, exist_ok=True)
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
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.clock.install(time=datetime.datetime(2026, 11, 2, 8, 30))
        await pg.goto('file://' + os.path.join(ROOT, 'index.html'))
        await pg.wait_for_function('window.__ski && window.__ski.steps', timeout=60000)
        await pg.clock.run_for(3000)
        result('not a trip day: no check on open', not await pg.is_visible('#passSheet'))
        await pg.click('#menuBtn'); await pg.wait_for_timeout(400)
        sw = await pg.evaluate("[...document.querySelectorAll('#dayList .daycard')].map(b=>b.classList.contains('swiss'))")
        result('the menu marks days 3, 4 and 6 as Swiss', sw == [False, False, True, True, False, True], sw)
        await pg.click('#drawerClose') if await pg.is_visible('#drawerClose') else await pg.evaluate("document.getElementById('drawer').hidden=true")
        # pick a French day: nothing; pick the Swiss Tuesday: the check
        await pg.click('#menuBtn'); await pg.wait_for_timeout(400); btns = await pg.query_selector_all('#dayList button')
        await btns[1].click(); await pg.wait_for_timeout(400)
        result('French day: no check', not await pg.is_visible('#passSheet'))
        result('French day: Start skiing is not locked', not await pg.evaluate("document.getElementById('goBtn').classList.contains('locked')"))
        await pg.click('#menuBtn'); await pg.wait_for_timeout(400); btns = await pg.query_selector_all('#dayList button')
        await btns[2].click(); await pg.wait_for_timeout(500)
        result('Swiss day: the passport check opens', await pg.is_visible('#passSheet'))
        await pg.evaluate("document.getElementById('passSheet').hidden=true"); await pg.wait_for_timeout(200)
        result('Swiss day: Start skiing is locked, Passport check sits above it', await pg.evaluate("document.getElementById('goBtn').classList.contains('locked')") and await pg.is_visible('#passBtn'))
        await pg.click('#goBtn'); await pg.wait_for_timeout(300)
        result('a locked Start skiing opens the check instead of starting', await pg.is_visible('#passSheet') and await pg.evaluate('window.__ski.st && !document.querySelector(".app").classList.contains("tracking")'))
        result('the passport clip plays', 'passport' in await pg.evaluate('window.__ski.sfx.log'))
        await pg.screenshot(path=os.path.join(OUT, '01-check.png'))
        await pg.keyboard.press('Escape'); await pg.mouse.click(200, 300); await pg.wait_for_timeout(300)
        result('it does not close by tapping or Escape', await pg.is_visible('#passSheet'))
        # a short slide springs back
        kb = await pg.query_selector('#passKnob'); bb = await kb.bounding_box(); tr = await (await pg.query_selector('#passTrack')).bounding_box()
        await pg.mouse.move(bb['x'] + 20, bb['y'] + 20); await pg.mouse.down(); await pg.mouse.move(bb['x'] + 120, bb['y'] + 20, steps=5); await pg.mouse.up(); await pg.wait_for_timeout(400)
        result('half a slide does not count', await pg.is_visible('#passSheet'))
        await pg.mouse.move(bb['x'] + 20, bb['y'] + 20); await pg.mouse.down(); await pg.mouse.move(tr['x'] + tr['width'] - 10, bb['y'] + 20, steps=8); await pg.mouse.up(); await pg.wait_for_timeout(600)
        result('a full slide confirms', not await pg.is_visible('#passSheet') and await pg.is_visible('#passDoneSheet'))
        result('Start skiing sits right in the crew sheet', await pg.is_visible('#passGo'))
        await pg.screenshot(path=os.path.join(OUT, '02-crew.png'))
        k = await pg.evaluate('window.__ski.passKey()')
        result('remembered for the day', await pg.evaluate('k => !!window.__ski.games.pass[k]', k), k)
        await pg.click('#passOk')
        result('after the slide, Start skiing unlocks', not await pg.evaluate("document.getElementById('goBtn').classList.contains('locked')") and await pg.is_hidden('#passBtn'))
        await pg.click('#menuBtn'); await pg.wait_for_timeout(400); btns = await pg.query_selector_all('#dayList button')
        await btns[2].click(); await pg.wait_for_timeout(400)
        result('once checked, it stays away', not await pg.is_visible('#passSheet'))
        # a friend nudges someone who hasn't checked
        await pg.evaluate("k => { delete window.__ski.games.pass[k]; }", k)
        await pg.evaluate("""k => { window.__ski.__gs = true; }""", k)
        shown = await pg.evaluate("""k => { const g = {trip:{invite_code:'X'}, members:[{id:'m1', name:'Avsha', color:'#7C3AED', games:{['nudge:'+k]: Date.now(), ['pass:'+k]: Date.now()-60000}}]};
            window.__ski.setGstate ? window.__ski.setGstate(g) : null; return !!window.__ski.setGstate; }""", k)
        if shown:
            await pg.evaluate('window.__ski.passNudgeCheck()'); await pg.wait_for_timeout(300)
            result('a nudge brings the check back', await pg.is_visible('#passSheet'), await pg.inner_text('#passNudged'))
        result('no page errors', not errs, errs[:3])
        await b.close()
    log.close()
    if fails: raise SystemExit(1)
asyncio.run(main())
