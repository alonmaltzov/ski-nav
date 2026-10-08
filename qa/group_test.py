"""End-to-end test of the group features: organizer creates the trip, a friend joins from the invite link,
both appear on each other's map, route to a friend, meeting point, sharing off, remove member.
Runs against qa/fake_supabase.py (local Postgres) or any Supabase URL.
Usage: GROUP_URL=http://127.0.0.1:54400 python3 qa/group_test.py   ->  qa-out/web-group/ (log.txt + screenshots)"""
import asyncio, datetime, json, os, sys, urllib.request
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.environ.get('QA_OUT', os.path.join(ROOT, 'qa-out')), 'web-group')
URL = os.environ.get('GROUP_URL', 'http://127.0.0.1:54400'); KEY = os.environ.get('GROUP_KEY', 'test')
PAGE = os.environ.get('GROUP_PAGE', 'index.html')
os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(OUT, 'log.txt'), 'w'); fails = []; n = [0]

def result(check, ok, detail=''):
    log.write('[web] QA RESULT ' + json.dumps({'check': check, 'ok': bool(ok), 'detail': str(detail)}) + '\n'); log.flush()
    print(('PASS ' if ok else 'FAIL ') + check + (' - ' + str(detail) if detail else ''))
    if not ok: fails.append(check)

def rpc(fn, args):
    r = urllib.request.Request(URL.rstrip('/') + '/rest/v1/rpc/' + fn, json.dumps(args).encode(), {'apikey': KEY, 'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(r).read())

async def shot(pg, name):
    n[0] += 1; await pg.wait_for_timeout(700); await pg.screenshot(path=os.path.join(OUT, f'{n[0]:02d}-{name}.png'), timeout=90000)

async def new_page(b, who):
    ctx = await b.new_context(viewport=dict(width=393, height=852), device_scale_factor=2, is_mobile=True, has_touch=True)
    await ctx.add_init_script('window.__GROUP_BACKEND=%s; window.__QA_ACK=true;' % json.dumps({'url': URL, 'key': KEY}))
    await ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
    pg = await ctx.new_page()
    # sharing stops at 6 pm: run the test at 11 am the phone's time, whatever time CI runs
    await pg.clock.set_system_time(datetime.datetime.now().replace(hour=int(os.environ.get('QA_HOUR', '11')), minute=0))
    pg.on('pageerror', lambda e: (log.write(f'[{who}] ERROR {e}\n'), fails.append(f'{who} page error: {e}')))
    pg.on('console', lambda m: m.type == 'error' and log.write(f'[{who}] console error {m.text[:300]}\n'))
    return pg

async def ready(pg):
    await pg.wait_for_function('window.__ski && window.__ski.map && window.__ski.map.loaded() && window.__ski.steps && window.__ski.steps.length', timeout=60000)
    await pg.wait_for_timeout(800)

async def fix(pg, lat, lon, speed=0):
    await pg.evaluate('([a,b,s]) => window.__ski.onFix({lat:a, lon:b, acc:8, speed:s, t:Date.now(), alt:null})', [lat, lon, speed])

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        A = await new_page(b, 'organizer'); await A.goto('file://' + os.path.join(ROOT, PAGE)); await ready(A)

        # organizer: menu > people > start the group
        await A.click('#menuBtn'); await A.wait_for_timeout(500)
        result('people button is in the menu', await A.is_visible('#groupBtn'))
        await A.click('#groupBtn'); await shot(A, 'group-start')
        await A.fill('#gOwnerName', 'Alon'); await A.click('#gCreate')
        await A.wait_for_function('window.__ski.grp && window.__ski.gstate', timeout=10000)
        g = await A.evaluate('window.__ski.grp'); code = g['invite_code']
        result('organizer creates the trip', code.startswith('AVZ-'), code)
        result('invite link shows the code', code in (await A.inner_text('#gLink')), await A.inner_text('#gLink'))
        await shot(A, 'group-organizer')
        await A.click('#gCopy'); await A.wait_for_timeout(300)
        clip = await A.evaluate('navigator.clipboard.readText()')
        result('copy puts the invite link on the clipboard', clip.endswith(code), clip)

        # friend opens the invite link
        B = await new_page(b, 'friend'); await B.goto('file://' + os.path.join(ROOT, PAGE) + '?join=' + code); await ready(B)
        await B.wait_for_selector('#joinFlow:not([hidden]) #j1:not([hidden])', timeout=10000)
        await B.wait_for_function("document.getElementById('jTrip').textContent.length > 0", timeout=10000)
        result('join screen shows who invited you', 'Alon' in await B.inner_text('#jInviter'), await B.inner_text('#jInviter'))
        await shot(B, 'join-welcome')
        await B.click('#jGo1'); result('Continue is off until a name is typed', await B.is_disabled('#jGo2'))
        await B.fill('#jName', 'Dana Levi'); await B.click('#jColors button:nth-child(2)'); await shot(B, 'join-name')
        await B.click('#jGo2'); await shot(B, 'join-location')
        await B.click('#jShare')
        await B.wait_for_function('window.__ski.grp && window.__ski.gstate && document.getElementById("joinFlow").hidden', timeout=10000)
        gb = await B.evaluate('window.__ski.gstate')
        result('friend joins the trip', len(gb['members']) == 2 and gb['role'] == 'member', [m['name'] for m in gb['members']])
        result('join link is removed from the address bar', 'join=' not in B.url, B.url)
        await shot(B, 'joined')

        # both on the mountain: organizer at the start of the plan, friend further along
        st = await A.evaluate('window.__ski.steps.map(s => s.coords.map(c => [c[0], c[1]]))')
        a0 = st[0][0]; far = st[min(3, len(st) - 1)]; bpt = far[len(far) // 2]
        await A.evaluate('window.__ski._mode("gps")'); await fix(A, a0[0], a0[1]); await A.wait_for_timeout(800)
        await B.evaluate('window.__ski._mode("gps")'); await fix(B, bpt[0], bpt[1], 9); await B.wait_for_timeout(800)
        gb2 = rpc('trip_state', {'p_secret': (await B.evaluate('window.__ski.grp'))['secret']})
        # the friend's page posts while tracking; if not tracking in this headless run, post the same way the app does
        if not any(m['pos'] for m in gb2['members'] if m['name'] == 'Dana Levi'):
            await B.evaluate('([a,b]) => window.__ski.onFix({lat:a, lon:b, acc:8, speed:9, t:Date.now()})', bpt)
            await B.wait_for_timeout(800)
            gb2 = rpc('trip_state', {'p_secret': (await B.evaluate('window.__ski.grp'))['secret']})
        posted = any(m['pos'] for m in gb2['members'] if m['name'] == 'Dana Levi')
        result('friend\'s phone sends its position while skiing', posted)
        if not posted:
            rpc('post_position', {'p_secret': (await B.evaluate('window.__ski.grp'))['secret'], 'p_lat': bpt[0], 'p_lon': bpt[1], 'p_acc': 8, 'p_speed': 9, 'p_on_lift': False, 'p_run': 'test run', 'p_km': 4.2})

        await A.click('#groupBack'); await A.click('#drawerClose')
        await A.evaluate('window.__ski.refreshGroup()'); await A.wait_for_timeout(800)
        result('friend appears on the organizer\'s map', await A.locator('.fdot').count() == 1, await A.locator('.fdot').count())
        result('friends pill shows 1 friend', (await A.inner_text('#friendsPill')).strip() == 'All 1', await A.inner_text('#friendsPill'))
        await A.evaluate('window.__ski.map.jumpTo({center:[%f,%f], zoom:14})' % ((a0[1] + bpt[1]) / 2, (a0[0] + bpt[0]) / 2))
        await shot(A, 'organizer-map-friend')

        # a third friend skiing far away (Chatel side): ALL must show them, and the organizer can choose who to see
        Y = rpc('join_trip', {'p_code': code, 'p_name': 'Yoni Katz', 'p_color': '#0F766E', 'p_platform': 'test'})
        far = [bpt[0] + 0.07, bpt[1] + 0.06]   # ~8 km away, off the route
        rpc('post_position', {'p_secret': Y['secret'], 'p_lat': far[0], 'p_lon': far[1], 'p_acc': 10, 'p_speed': 3, 'p_on_lift': True, 'p_run': None, 'p_km': 9.1})
        await A.evaluate('window.__ski.refreshGroup()'); await A.wait_for_timeout(800)
        result('pill shows everyone by default', (await A.inner_text('#friendsPill')).strip() == 'All 2', await A.inner_text('#friendsPill'))
        result('friend on a lift gets the lift badge', await A.locator('.fdot.lift').count() == 1)
        inb = 'window.__ski.map.getBounds().contains([%f,%f])' % (far[1], far[0])
        await A.click('#fitBtn'); await A.wait_for_timeout(3500)
        result('ALL shows a friend who is off the route', await A.evaluate(inb))
        await shot(A, 'all-shows-everyone')
        await A.click('#friendsPill'); await A.wait_for_timeout(500)
        result('people pill opens "On your map"', await A.is_visible('#pickSheet') and await A.locator('#pickList .prow').count() == 2)
        result('Everyone mode hides the switches', not await A.locator('#pickList .ptog >> nth=0').is_visible())
        await A.click('#pickSeg button[data-v="choose"]'); await A.wait_for_timeout(300)
        await shot(A, 'choose-who')
        await A.click('#pickList .prow:has-text("Yoni") .ptog'); await A.wait_for_timeout(500)
        result('switching someone off removes their dot', await A.locator('.fdot').count() == 1)
        result('pill shows "1 of 2"', (await A.inner_text('#friendsPill')).strip() == '1 of 2', await A.inner_text('#friendsPill'))
        await A.click('#pickDone'); await A.click('#fitBtn'); await A.wait_for_timeout(3500)
        result('ALL leaves out people you hid', not await A.evaluate(inb))
        await A.reload(); await A.wait_for_function('window.__ski && window.__ski.map && window.__ski.map.loaded() && window.__ski.gstate', timeout=60000); await A.wait_for_timeout(800)
        await A.evaluate('window.__ski._mode("gps")'); await fix(A, a0[0], a0[1])
        result('your choice is remembered on this phone', (await A.inner_text('#friendsPill')).strip() == '1 of 2', await A.inner_text('#friendsPill'))
        await A.click('#friendsPill'); await A.wait_for_timeout(400)
        await A.click('#pickList .prow:has-text("Dana") .pwho'); await A.wait_for_timeout(2500)
        c = await A.evaluate('window.__ski.map.getCenter()')
        result('tapping a name flies to them', abs(c['lat'] - bpt[0]) < 0.003 and abs(c['lng'] - bpt[1]) < 0.003, c)
        await A.click('#friendsPill'); await A.click('#pickSeg button[data-v="all"]'); await A.click('#pickDone')
        rpc('remove_member', {'p_secret': g['secret'], 'p_member': Y['member_id']})
        await A.evaluate('window.__ski.refreshGroup()'); await A.wait_for_timeout(600)

        await A.evaluate('document.querySelector(".fdot").click()'); await A.wait_for_timeout(500)
        result('friend card opens', await A.is_visible('#friendSheet'))
        result('friend card has distance and ETA', (await A.inner_text('#fDist')) != '-' and (await A.inner_text('#fEta')).endswith('min'), (await A.inner_text('#fDist')) + ' / ' + (await A.inner_text('#fEta')))
        await shot(A, 'friend-card')
        await A.click('#fRoute'); await A.wait_for_timeout(800)
        last = await A.evaluate('(() => { const s = window.__ski.steps; return s[s.length-1].name; })()')
        result('Route to them ends at the friend', last == 'Dana Levi', last)
        await shot(A, 'route-to-friend')

        # meeting point
        await A.evaluate('document.querySelector(".fdot").click()'); await A.wait_for_timeout(400)
        await A.click('#fMeet'); await A.wait_for_timeout(1000)
        await B.evaluate('window.__ski.refreshGroup()'); await B.wait_for_timeout(800)
        result('meeting point shows on the friend\'s map', await B.locator('.meetpin').count() == 1)
        await B.evaluate('window.__ski.map.jumpTo({center:[%f,%f], zoom:14})' % (bpt[1], bpt[0]))
        await shot(B, 'friend-sees-meet')
        await B.evaluate('document.querySelector(".meetpin").click()'); await B.wait_for_timeout(400)
        result('meeting point card opens', await B.is_visible('#meetSheet'), await B.inner_text('#meetSub'))
        await shot(B, 'meet-card'); await B.click('#meetClose')
        result('friend sees the organizer on the map', await B.locator('.fdot').count() == 1)

        # organizer plan style is the group's
        await A.evaluate("window.__ski && document.querySelector('#styleSeg button[data-v=\"black\"]') && document.querySelector('#styleSeg button[data-v=\"black\"]').click()")
        await A.wait_for_timeout(800)
        await B.evaluate('window.__ski.refreshGroup()'); await B.wait_for_timeout(1000)
        pv = rpc('trip_state', {'p_secret': g['secret']})['trip']['plan']
        result('organizer\'s plan style is shared with the group', pv.get('variant') == 'black', pv)

        # friend can't change the plan or remove people
        try: rpc('set_plan', {'p_secret': (await B.evaluate('window.__ski.grp'))['secret'], 'p_plan': {'variant': 'red'}}); ok = False
        except Exception: ok = True
        result('a friend can\'t change the plan', ok)

        # friend turns sharing off -> disappears from the organizer's map
        await B.click('#menuBtn'); await B.wait_for_timeout(400); await B.click('#groupBtn'); await B.wait_for_timeout(600)
        await shot(B, 'group-friend')
        result('friend doesn\'t get Remove buttons', await B.locator('.mrm').count() == 0)
        await B.click('#gSharing'); await B.wait_for_timeout(800)
        await B.click('#groupBack'); await B.click('#drawerClose')
        await A.evaluate('window.__ski.refreshGroup()'); await A.wait_for_timeout(800)
        result('sharing off hides the friend from the map', await A.locator('.fdot').count() == 0)

        # organizer removes the friend
        await A.click('#menuBtn'); await A.wait_for_timeout(400); await A.click('#groupBtn'); await A.wait_for_timeout(800)
        await shot(A, 'group-organizer-2')
        await A.click('.mrm'); await A.click('.mrm')
        try: await A.wait_for_function('window.__ski.gstate.members.length === 1', timeout=10000); ok = True
        except Exception: ok = False
        result('organizer removes a member', ok)
        await B.evaluate('window.__ski.refreshGroup()'); await B.wait_for_timeout(800)
        result('removed friend leaves the group on their phone', (await B.evaluate('window.__ski.grp')) is None)

        # bad invite code
        C = await new_page(b, 'stranger'); await C.goto('file://' + os.path.join(ROOT, PAGE) + '?join=AVZ-ZZZZ'); await ready(C)
        await C.wait_for_selector('#jErr1:not([hidden])', timeout=10000)
        result('a bad invite link says so', 'valid' in await C.inner_text('#jErr1'), await C.inner_text('#jErr1'))
        await shot(C, 'join-bad-link')
        # the invite landing page (join.html): iPhone gets "Open in the app", Android gets the web app
        for name, ua in [('iphone', 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'),
                         ('android', 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36')]:
            ctx = await b.new_context(viewport=dict(width=393, height=852), device_scale_factor=2, is_mobile=True, has_touch=True, user_agent=ua)
            await ctx.add_init_script('window.__GROUP_BACKEND=%s;' % json.dumps({'url': URL, 'key': KEY}))
            J = await ctx.new_page(); await J.goto('file://' + os.path.join(ROOT, 'join.html') + '?c=' + code.lower())
            await J.wait_for_function("document.getElementById('inv').textContent.indexOf('Alon') >= 0", timeout=10000)
            if name == 'iphone':
                href = await J.get_attribute('#openApp', 'href')
                result('invite page on iPhone opens the app', href == 'skinav://join?c=' + code, href)
                await J.click('#noApp'); web = await J.get_attribute('#webIos', 'href')
            else:
                result('invite page on Android has no app button', not await J.is_visible('#openApp'))
                web = await J.get_attribute('#webOther', 'href')
            result('invite page (%s) links to the web app join' % name, web == 'index.html?join=' + code, web)
            await shot(J, 'invite-page-' + name); await ctx.close()
        await b.close()
    log.write('[web] QA DONE\n'); log.close()
    print('\n%d failed' % len(fails)); sys.exit(1 if fails else 0)

asyncio.run(main())
