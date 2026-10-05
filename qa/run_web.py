"""Run the QA tour in headless Chrome at iPhone sizes. Output: qa-out/web-<device>/ (log.txt + screenshots)."""
import asyncio, os, sys, time
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get('QA_OUT', os.path.join(ROOT, 'qa-out'))
DEVICES = {'iphone16': dict(width=393, height=852), 'iphoneSE': dict(width=375, height=667)}
TOUR = open(os.path.join(ROOT, 'qa', 'tour.js')).read()

async def run(p, name, vp):
    d = os.path.join(OUT, 'web-' + name); os.makedirs(d, exist_ok=True)
    b = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    ctx = await b.new_context(viewport=vp, device_scale_factor=2, is_mobile=True, has_touch=True)
    await ctx.add_init_script('window.__QA_ACK=true;\n' + TOUR)
    pg = await ctx.new_page()
    log = open(os.path.join(d, 'log.txt'), 'w'); n = [0]; done = asyncio.Event(); pending = []
    def on_console(m):
        t = m.text
        if m.type in ('error', 'warning'): log.write('[web] ' + m.type.upper() + ' ' + t[:500] + '\n')
        if not t.startswith('QA '): return
        log.write('[web] ' + t + '\n'); log.flush()
        if t.startswith('QA SCREEN '):
            n[0] += 1; name_ = t[10:].strip(); path = os.path.join(d, f'{n[0]:02d}-{name_}.png')
            async def shot():
                await pg.screenshot(path=path)
                await pg.evaluate('n => window.__qaAck = n', name_)
            pending.append(asyncio.ensure_future(shot()))
        if t.startswith('QA DONE'): done.set()
    pg.on('console', on_console)
    pg.on('pageerror', lambda e: log.write('[web] ERROR ' + str(e)[:500] + '\n'))
    await pg.goto('file://' + os.path.join(ROOT, 'index.html'))
    try: await asyncio.wait_for(done.wait(), 300)
    except asyncio.TimeoutError: log.write('[web] QA RESULT {"check":"tour finished in time","ok":false,"detail":"timeout"}\n')
    for f in pending:
        try: await f
        except Exception as e: log.write(f'[web] screenshot failed {e}\n')
    log.close(); await b.close()

async def main():
    async with async_playwright() as p:
        await asyncio.gather(*[run(p, k, v) for k, v in DEVICES.items()])
asyncio.run(main())
