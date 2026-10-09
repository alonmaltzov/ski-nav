"""Android QA on an emulator (run by CI inside android-emulator-runner).
1. Screen tour: the same qa/tour.js as iPhone and web, screenshots of every screen.
2. Tracking test: Start, GPS fixes, screen OFF while more fixes come in, screen back on:
   the page must have every fix, the ongoing "Skiing" notification must show while tracking, and go away on Stop.
Writes qa-out/android/{log.txt,results.json,*.png}. Exit code 1 on failure."""
import json, math, os, re, subprocess, sys, time, urllib.request

PKG = 'com.alonmaltzov.skinav'
ACT = PKG + '/.MainActivity'
OUT = 'qa-out/android'; os.makedirs(OUT, exist_ok=True)
APK = sys.argv[1] if len(sys.argv) > 1 else 'android/app/build/outputs/apk/release/app-release.apk'
results = []
def res(check, ok, detail=''):
    results.append({'check': check, 'ok': bool(ok), 'detail': str(detail)[:400]}); print(('PASS ' if ok else 'FAIL ') + check, detail)
def adb(*a, check=False, timeout=60):
    r = subprocess.run(['adb', *a], capture_output=True, text=True, timeout=timeout)
    if check and r.returncode: raise RuntimeError(' '.join(a) + ': ' + r.stderr)
    return r.stdout
def shot(name):
    with open(f'{OUT}/{name}.png', 'wb') as f: f.write(subprocess.run(['adb', 'exec-out', 'screencap', '-p'], capture_output=True, timeout=30).stdout)

adb('install', '-r', '-g', APK, check=True, timeout=180)
for p in ['ACCESS_FINE_LOCATION', 'ACCESS_COARSE_LOCATION', 'POST_NOTIFICATIONS', 'RECORD_AUDIO']:
    adb('shell', 'pm', 'grant', PKG, 'android.permission.' + p)
adb('shell', 'dumpsys', 'deviceidle', 'whitelist', '+' + PKG)
adb('shell', 'settings', 'put', 'secure', 'location_mode', '3')
adb('shell', 'svc', 'power', 'stayon', 'true')
adb('shell', 'wm', 'dismiss-keyguard')

# ---------- 1. screen tour ----------
adb('logcat', '-c')
adb('shell', 'am', 'start', '-n', ACT, '--ez', 'qaTour', 'true', check=True)
log = open(f'{OUT}/log.txt', 'w')
proc = subprocess.Popen(['adb', 'logcat', '-v', 'brief', 'SkiNav:D', 'SkiNav-web:*', 'AndroidRuntime:E', 'ActivityManager:W', 'TextToSpeech:*', 'chromium:W', '*:S'], stdout=subprocess.PIPE, text=True)
t0 = time.time(); n = 0; done = False; loaded = False; tour = []
os.set_blocking(proc.stdout.fileno(), False)
while time.time() - t0 < 600:
    line = proc.stdout.readline()
    if not line: time.sleep(0.2); continue
    log.write(line); log.flush()
    if 'page loaded, map=true' in line: loaded = True
    if 'FATAL EXCEPTION' in line: res('app did not crash', False, line)
    m = re.search(r'QA SCREEN (.+)$', line)
    if m:
        n += 1; time.sleep(0.6); shot('tour-%02d-%s' % (n, re.sub(r'[^A-Za-z0-9]+', '-', m.group(1).strip())[:40]))
    m = re.search(r'QA RESULT (\{.*\})', line)
    if m:
        try: tour.append(json.loads(m.group(1)))
        except Exception: pass
    if 'QA DONE' in line: done = True; break
proc.kill()
if not done:
    shot('tour-stalled')
    open(f'{OUT}/stall-logcat.txt', 'w').write(adb('logcat', '-d', '-t', '400', timeout=60))
    open(f'{OUT}/stall-activity.txt', 'w').write(adb('shell', 'dumpsys', 'activity', 'top', timeout=60)[:20000])
res('page loads with the map', loaded)
res('screen tour ran to the end', done, f'{n} screens')
bad = [r for r in tour if not r.get('ok')]
res('tour checks', not any('crash' in r.get('check', '') for r in bad), '; '.join(r.get('check', '') + ': ' + str(r.get('detail', ''))[:80] for r in bad[:8]) or 'all ok')
json.dump(tour, open(f'{OUT}/tour.json', 'w'), indent=1)

# ---------- 2. tracking with the screen off ----------
adb('shell', 'am', 'force-stop', PKG)
adb('logcat', '-c')
adb('shell', 'am', 'start', '-n', ACT, '--ez', 'noWebUpdate', 'true', check=True)
deadline = time.time() + 90
while time.time() < deadline and 'page loaded' not in adb('logcat', '-d', '-s', 'SkiNav-web:*'): time.sleep(2)
time.sleep(4)
pid = adb('shell', 'pidof', PKG).strip()
adb('forward', 'tcp:9222', f'localabstract:webview_devtools_remote_{pid}', check=True)
import websocket  # websocket-client
pages = json.load(urllib.request.urlopen('http://127.0.0.1:9222/json'))
ws = websocket.create_connection([p for p in pages if p.get('type') == 'page'][0]['webSocketDebuggerUrl'], timeout=30, suppress_origin=True)
mid = [0]
def ev(expr):
    mid[0] += 1; ws.send(json.dumps({'id': mid[0], 'method': 'Runtime.evaluate', 'params': {'expression': expr, 'returnByValue': True, 'awaitPromise': True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get('id') == mid[0]: return r.get('result', {}).get('result', {}).get('value')

res('bridge: page sees the app', ev('NATIVE && !!window.__ANDROID && platform()') == 'android')
ev("document.querySelectorAll('[hidden]').length")  # warm up
# close any sheet the first open shows, then Start
ev("(function(){ document.querySelectorAll('#onb, .sheet').forEach(e=>{ if(e.id==='onb') e.hidden=true; }); return 1 })()")
ev("document.getElementById('goBtn').click()")
time.sleep(3)
res('tracking started', ev('mode') == 'gps' and 'Skiing' in adb('shell', 'dumpsys', 'notification', '--noredact'), ev('mode'))
shot('track-1-started')
# a straight line down from Avoriaz, ~12 m per second
lat0, lon0 = 46.1936, 6.7689
def feed(i0, i1):
    for i in range(i0, i1):
        lat = lat0 - i * 0.0001; lon = lon0 + i * 0.00005
        adb('emu', 'geo', 'fix', f'{lon:.6f}', f'{lat:.6f}', f'{1800 - i * 2}')
        time.sleep(1)
feed(0, 25)
on1 = ev('st.dist')
res('fixes reach the page (screen on)', on1 and on1 > 150, f'{on1} m')
# screen off: the page sleeps, the service keeps collecting
adb('shell', 'input', 'keyevent', 'KEYCODE_SLEEP'); time.sleep(2)
feed(25, 55)
notif = adb('shell', 'dumpsys', 'notification', '--noredact')
m = re.search(r'Skiing · ([0-9.]+) km', notif)
res('notification counts km with the screen off', m and float(m.group(1)) > 0.3, m.group(0) if m else 'no Skiing notification')
adb('shell', 'input', 'keyevent', 'KEYCODE_WAKEUP'); time.sleep(1); adb('shell', 'wm', 'dismiss-keyguard'); time.sleep(4)
on2 = ev('st.dist')
res('screen-off fixes arrive when the screen comes back', on2 and on1 and on2 > on1 + 250, f'{on1} m before, {on2} m after')
shot('track-2-after-screen-off')
ev("document.getElementById('goBtn').click()"); time.sleep(3)
res('Stop ends tracking and the notification', ev('mode') == 'off' and 'Skiing ·' not in adb('shell', 'dumpsys', 'notification', '--noredact'))
res('a day log was saved', 'track-' in adb('shell', 'run-as', PKG, 'ls', 'files'))
ws.close()

json.dump(results, open(f'{OUT}/results.json', 'w'), indent=1)
fails = [r for r in results if not r['ok']]
print(f"\n{len(results) - len(fails)}/{len(results)} passed")
sys.exit(1 if fails else 0)
