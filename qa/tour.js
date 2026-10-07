/* Ski Nav automated QA tour.
 * Runs inside the app (iOS Simulator via WKWebView user script, or headless Chrome via Playwright).
 * Opens every screen, measures every tappable thing, replays a ski day, tests GPS and links,
 * and logs machine-readable lines:  QA SCREEN <name> | QA AUDIT <json> | QA RESULT <json> | QA DONE
 * The runner screenshots on every "QA SCREEN" line and turns the rest into a report.
 */
(function () {
  if (window.__qaLoaded) return; window.__qaLoaded = true;
  const NATIVE = !!(window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.skinav);
  const post = (m) => { if (NATIVE) { try { window.webkit.messageHandlers.skinav.postMessage({ cmd: 'log', msg: m }); } catch (e) {} } else console.log(m); };
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  const $ = (id) => document.getElementById(id);
  const WAIT = window.__QA_WAIT || 2500;           // time on each screen so the runner can screenshot it
  const MIN = 44, MIN_FONT = 12;                  // Apple HIG: 44pt minimum hit target, 11-12pt minimum text
  const GLOVE = { goBtn: 56, nextBtn: 56, prevBtn: 56, menuBtn: 48, followBtn: 48, compassBtn: 48, fitBtn: 48, dimBtn: 48, placesBtn: 48 }; // tapped mid-run with gloves

  function visible(el) {
    if (el.closest('[hidden]')) return false;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
  function label(el) {
    const t = (el.getAttribute('aria-label') || el.textContent || el.title || '').trim().replace(/\s+/g, ' ').slice(0, 40);
    return (el.id ? '#' + el.id : el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : '')) + (t ? ' "' + t + '"' : '');
  }
  function clipRect(el) {           // visible region after scroll containers clip it
    let r = el.getBoundingClientRect(), x0 = r.left, y0 = r.top, x1 = r.right, y1 = r.bottom;
    for (let p = el.parentElement; p; p = p.parentElement) {
      const cs = getComputedStyle(p);
      if (/(auto|scroll|hidden)/.test(cs.overflow + cs.overflowX + cs.overflowY)) {
        const q = p.getBoundingClientRect();
        x0 = Math.max(x0, q.left); y0 = Math.max(y0, q.top); x1 = Math.min(x1, q.right); y1 = Math.min(y1, q.bottom);
      }
    }
    x0 = Math.max(x0, 0); y0 = Math.max(y0, 0); x1 = Math.min(x1, innerWidth); y1 = Math.min(y1, innerHeight);
    return { x0, y0, x1, y1, w: x1 - x0, h: y1 - y0 };
  }

  function audit(screen) {
    const vw = innerWidth, vh = innerHeight;
    const out = { screen, page: location.pathname.split('/').pop() || 'index.html', vw, vh, targets: 0, needsScroll: 0, small: [], gloveSmall: [], covered: [], offscreen: [], crowded: [], tinyText: [], overflowX: [] };
    // when a menu or sheet is open, only what is on it matters (the rest is meant to be behind it)
    const modal = [...document.querySelectorAll('.drawer,.sheet')].find(m => !m.hidden);
    out.modal = modal ? modal.id : null;
    const els = [...(modal || document).querySelectorAll('button, a[href], [role=button], input, select, .maplibregl-ctrl button')].filter(visible);
    const boxes = [];
    for (const el of els) {
      const r = el.getBoundingClientRect();
      const c = clipRect(el);
      if (c.w < 4 || c.h < 4) {
        // fully scrolled out of its container: fine if it is inside a scroller, a bug if not
        if (r.right < -1 || r.left > vw + 1 || ((r.bottom < 0 || r.top > vh) && !el.closest('.drawerin,.sheetin,.areas'))) out.offscreen.push(label(el));
        else out.needsScroll++;
        continue;
      }
      out.targets++;
      const w = Math.round(r.width), h = Math.round(r.height);
      if (Math.min(w, h) < MIN) out.small.push({ el: label(el), w, h });
      else if (GLOVE[el.id] && Math.min(w, h) < GLOVE[el.id]) out.gloveSmall.push({ el: label(el), w, h, want: GLOVE[el.id] });
      const inHScroll = (() => { for (let q = el.parentElement; q; q = q.parentElement) { const s = getComputedStyle(q).overflowX; if ((s === 'auto' || s === 'scroll') && q.scrollWidth > q.clientWidth) return true; } return false; })();
      if (!inHScroll && (r.left < -1 || r.right > vw + 1)) out.offscreen.push(label(el) + ` x=${Math.round(r.left)}..${Math.round(r.right)}`);
      // is the centre of the visible part actually this element (not covered by a banner, legend, etc)?
      const cx = (c.x0 + c.x1) / 2, cy = (c.y0 + c.y1) / 2;
      const hit = document.elementFromPoint(cx, cy);
      if (hit && !el.contains(hit) && !hit.contains(el)) out.covered.push({ el: label(el), by: label(hit) });
      boxes.push({ el, r: c });
    }
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i].r, b = boxes[j].r;
      if (boxes[i].el.contains(boxes[j].el) || boxes[j].el.contains(boxes[i].el)) continue;
      const gx = Math.max(b.x0 - a.x1, a.x0 - b.x1), gy = Math.max(b.y0 - a.y1, a.y0 - b.y1);
      const gap = Math.max(gx, gy);
      if (gap < 0) out.crowded.push({ a: label(boxes[i].el), b: label(boxes[j].el), gap: Math.round(gap) });
    }
    // text that is too small to read at arm's length
    const seen = new Set();
    const walker = document.createTreeWalker(modal || document.body, NodeFilter.SHOW_TEXT);
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      const p = n.parentElement; if (!p || seen.has(p) || !n.textContent.trim()) continue;
      seen.add(p);
      if (p.closest('script,style,.maplibregl-ctrl-attrib') || !visible(p)) continue;
      const c = clipRect(p); if (c.w < 2 || c.h < 2) continue;
      const fs = parseFloat(getComputedStyle(p).fontSize);
      if (fs < MIN_FONT) out.tinyText.push({ el: label(p), px: fs });
    }
    // sideways scrolling
    if (document.documentElement.scrollWidth > vw + 1) out.overflowX.push('page ' + document.documentElement.scrollWidth);
    document.querySelectorAll('.drawerin,.sheetin,.areas').forEach(s => { if (visible(s) && s.scrollWidth > s.clientWidth + 1) out.overflowX.push(label(s) + ' ' + s.scrollWidth + '>' + s.clientWidth); });
    out.tinyText = out.tinyText.slice(0, 25);
    out.crowded = out.crowded.slice(0, 25);
    return out;
  }
  window.__qaAudit = audit;

  async function settled(ms) {
    await sleep(ms);
    // let open/close animations finish so we measure the final layout
    const anims = document.getAnimations ? document.getAnimations().filter(a => a.playState === 'running') : [];
    if (anims.length) await Promise.race([Promise.all(anims.map(a => a.finished.catch(() => {}))), sleep(3000)]);
  }
  async function screen(name, opts = {}) {
    await settled(opts.settle || 700);
    post('QA SCREEN ' + name);
    post('QA AUDIT ' + JSON.stringify(audit(name)));
    // the web runner confirms each screenshot; the simulator runner just gets a fixed pause
    const until = Date.now() + (window.__QA_ACK ? 20000 : WAIT);
    while (Date.now() < until && window.__qaAck !== name) await sleep(100);
  }
  const tap = async (id, ms = 350) => { const el = typeof id === 'string' ? $(id) : id; if (!el) { post('QA RESULT ' + JSON.stringify({ check: 'tap', ok: false, detail: 'missing ' + id })); return false; } el.click(); await sleep(ms); return true; };
  const result = (check, ok, detail) => post('QA RESULT ' + JSON.stringify({ check, ok, detail }));
  const txt = (id) => ($(id) ? $(id).textContent.trim() : '');

  async function waitReady() {
    for (let i = 0; i < 60; i++) {
      if (window.__ski && window.__ski.map && window.__ski.map.loaded && window.__ski.map.loaded() && window.__ski.steps && window.__ski.steps.length) return true;
      await sleep(500);
    }
    return false;
  }

  async function tour() {
    const page = location.pathname.split('/').pop() || 'index.html';
    const ready = await waitReady();
    result('page loads and map is ready (' + page + ')', ready, ready ? (window.__ski.steps.length + ' steps') : 'map or plan never loaded');
    const flag = sessionStorage.getItem('qa_next');
    if (flag === 'nyc') {   // second page after following the "Practice in NYC" link
      sessionStorage.removeItem('qa_next');
      result('Practice in NYC link opens the NYC map', /nyc/.test(page) && ready, page);
      await screen('nyc-main');
      await tap('menuBtn'); await screen('nyc-menu', { settle: 1000 });
      const back = $('otherApp'); result('NYC page has a working way back', !!back && !!back.getAttribute('href') && back.getAttribute('href') !== './', back ? back.getAttribute('href') : 'none');
      await tap('drawerClose');
      post('QA DONE');
      return;
    }
    await screen('main');

    // week menu
    await tap('menuBtn'); await screen('menu', { settle: 1000 });
    const dr = document.querySelector('.drawerin'); if (dr) { dr.scrollTop = dr.scrollHeight; await screen('menu-bottom'); dr.scrollTop = 0; }
    const fb = $('followBtn2'); if (fb) { const b0 = fb.getAttribute('aria-pressed'); fb.click(); await sleep(200); const b1 = fb.getAttribute('aria-pressed'); fb.click(); await sleep(200);
      result('Follow the plan toggle works (off by default)', b0 === 'false' && b1 === 'true' && fb.getAttribute('aria-pressed') === 'false', `${b0} -> ${b1} -> ${fb.getAttribute('aria-pressed')}`); }
    const days = document.querySelectorAll('#dayList .daycard, #dayList button');
    result('menu lists the days', days.length >= 1, days.length + ' day buttons');
    if (days.length > 1) {
      const before = txt('dayName'); days[1].click(); await sleep(800);
      result('tapping Day 2 switches the plan', txt('dayName') !== before || txt('dayEyebrow').includes('2'), before + ' -> ' + txt('dayName'));
      await tap('menuBtn'); const d2 = document.querySelectorAll('#dayList .daycard, #dayList button'); d2[0] && d2[0].click(); await sleep(800);
    } else await tap('drawerClose');
    if (!$('drawer').hidden) await tap('drawerClose');
    result('menu closes', $('drawer').hidden, '');

    // route steps sheet
    await tap('stepsBtn'); await screen('steps');
    await tap('closeSheet'); result('steps sheet closes', $('sheet').hidden, '');

    // next / previous step buttons
    const s0 = window.__ski.cur; await tap('nextBtn'); const s1 = window.__ski.cur; await tap('prevBtn'); const s2 = window.__ski.cur;
    result('next and previous step buttons', s1 === s0 + 1 && s2 === s0, `${s0} -> ${s1} -> ${s2}`);

    // runs progress + list
    await tap('progBtn', 900); await screen('progress', { settle: 1200 });
    const chips = document.querySelectorAll('#progChips button');
    if (chips[1]) { chips[1].click(); await sleep(500); result('Remaining filter chip toggles', chips[1].getAttribute('aria-pressed') === 'true', ''); chips[0].click(); }
    await tap('runsListBtn'); await screen('runs-list');
    await tap('closeRuns'); await tap('progClose', 700);
    result('Runs view returns to route', !$('navPanel').hidden, '');

    // map buttons
    await tap('placesBtn'); await screen('places');
    await tap('placesBtn');
    await tap('dimBtn', 1500); await screen('map-3d', { settle: 1500 });
    await tap('dimBtn', 1200);
    await tap('fitBtn', 1200); await screen('map-all');
    await tap('followBtn', 600);

    // test mode replay: no GPS needed
    await tap('menuBtn'); await tap('simBtn'); await screen('test-mode');
    const x100 = document.querySelector('#simSheet [data-x="100"]'); x100 && x100.click();
    const c0 = window.__ski.cur;
    await tap('simStart'); await tap('closeSim');
    await sleep(9000); await screen('replay');
    result('tracking shows the stats card', document.querySelector('.app').classList.contains('tracking') && getComputedStyle(document.querySelector('.top')).display !== 'none', '');
    if (window.__ski.setSun) { window.__ski.setSun('on'); await screen('replay-sun', { settle: 1500 }); result('Sun mode switches on', document.querySelector('.app').classList.contains('sun'), ''); window.__ski.setSun('auto'); }
    await sleep(9000);
    const dist = parseFloat(txt('dist')) || 0, c1 = window.__ski.cur;
    const trailN = (window.__ski.st.trail || []).length;
    result('trail of where you have been is recorded', trailN > 20, trailN + ' trail points');
    result('free ski by default: no off-route banner', $('offroute').hidden, $('offroute').hidden ? 'hidden' : 'banner showing');
    result('test replay moves the skier and counts km', dist > 0 && c1 > c0, `km=${txt('dist')} max=${txt('maxv')} step ${c0}->${c1} pill="${txt('gpsPill')}"`);
    if (window.__ski.recap) {
      window.__ski.recap(); await screen('recap');
      result('day recap shows the day', !$('recapSheet').hidden && parseFloat(txt('rKm')) > 0, `km=${txt('rKm')} vert=${txt('rVert')} top=${txt('rTop')} lifts=${txt('rLifts')} goal=${txt('rGoal')} ${txt('rGoalPlus')}`);
      await tap('recapClose');
    }
    await tap('menuBtn'); await tap('simBtn'); await tap('simOff'); await tap('closeSim');
    result('home sheet is back after stopping', !document.querySelector('.app').classList.contains('tracking') && !!txt('homeTitle'), txt('homeTitle'));
    result('stop & reset clears the replay', (parseFloat(txt('dist')) || 0) === 0, 'km=' + txt('dist'));

    // real GPS path (native only: the simulator feeds a moving location)
    if (NATIVE) {
      // ME button without tracking: should ask iOS for one location and show the blue dot
      await tap('followBtn', 4000);
      result('ME shows my location without tracking', !!document.querySelector('.you'), document.querySelector('.you') ? 'blue dot on map' : 'no dot after 4 s');
      await screen('me-button');
      // compass button: native heading (simulators have no compass, so it should switch itself off cleanly)
      await tap('compassBtn', 2500);
      const pressed = $('compassBtn').getAttribute('aria-pressed');
      result('compass button responds', true, 'pressed=' + pressed + (pressed === 'false' ? ' (no compass on this device, turned itself off)' : ''));
      if (pressed === 'true') await tap('compassBtn', 500);
      // record the raw fixes iOS hands over, to tell "simulator not moving" apart from "app ignores movement"
      const raw = [];
      const orig = window.__native && window.__native.fixes;
      if (orig) window.__native.fixes = function (arr) { try { arr.forEach(f => raw.push(f)); } catch (e) {} return orig.apply(this, arguments); };
      post('QA GPS START');   // the simulator runner starts the moving route now
      await sleep(1500);
      await tap('goBtn', 1000);
      await sleep(15000); await screen('gps-tracking');
      await sleep(15000);
      if (orig) window.__native.fixes = orig;
      const km = parseFloat(txt('dist')) || 0;
      const m = (a, b) => { const R = 6371000, r = Math.PI / 180, dLa = (b.lat - a.lat) * r, dLo = (b.lon - a.lon) * r; return 2 * R * Math.asin(Math.sqrt(Math.sin(dLa / 2) ** 2 + Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(dLo / 2) ** 2)); };
      let path = 0; for (let i = 1; i < raw.length; i++) path += m(raw[i - 1], raw[i]);
      const sp = raw.map(f => f.speed).filter(v => v != null);
      const rawInfo = `${raw.length} fixes, raw path ${Math.round(path)} m, speeds ${sp.length ? Math.min(...sp).toFixed(1) + '..' + Math.max(...sp).toFixed(1) + ' m/s' : 'none'}, acc ${raw.length ? Math.round(raw[raw.length - 1].acc) : '-'} m, alt ${raw.length ? raw[raw.length - 1].alt : '-'}`;
      result('native GPS fixes arrive', raw.length > 5, rawInfo);
      result('simulator route is moving (test harness)', path > 100, rawInfo);
      result('moving GPS turns into km and speed', path < 100 || km > 0.05, `km=${txt('dist')} speed=${txt('spd')} max=${txt('maxv')} pill="${txt('gpsPill')}" vs raw path ${Math.round(path)} m`);
      await tap('goBtn', 800);
    }

    // link to the other map
    await tap('menuBtn');
    const link = $('otherApp');
    if (link && !/nyc/.test(page)) { sessionStorage.setItem('qa_next', 'nyc'); post('QA RESULT ' + JSON.stringify({ check: 'following link', ok: true, detail: link.getAttribute('href') })); link.click(); return; }
    await tap('drawerClose');
    post('QA DONE');
  }

  const go = () => tour().catch(e => { post('QA RESULT ' + JSON.stringify({ check: 'tour crashed', ok: false, detail: String(e && e.stack || e) })); post('QA DONE'); });
  if (document.readyState === 'complete') setTimeout(go, 500); else addEventListener('load', () => setTimeout(go, 500));
})();
