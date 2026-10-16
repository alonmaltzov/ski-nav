/* Ski-Paz Liquid Glass layer (demo): tab bar, glass material, Apple-style springs. The map is untouched. */
(function () {
  const $ = (id) => document.getElementById(id);
  const ua = navigator.userAgent;
  const CHROMIUM = /Chrome\//.test(ua) && !/iPhone|iPad|CriOS|EdgiOS/.test(ua);

  /* ---- springs: the same model SwiftUI uses (response + damping), sampled into a CSS linear() curve ---- */
  function spring(response = 0.42, damping = 0.72) {
    const w0 = 2 * Math.PI / response, z = damping, wd = w0 * Math.sqrt(1 - z * z);
    const x = (t) => 1 - Math.exp(-z * w0 * t) * (Math.cos(wd * t) + (z * w0 / wd) * Math.sin(wd * t));
    let T = 0; for (let t = 0; t < 3; t += 0.01) { if (Math.abs(1 - x(t)) > 0.002) T = t; }
    T = Math.max(T, 0.2);
    const pts = []; for (let i = 0; i <= 48; i++) pts.push(+x(T * i / 48).toFixed(4));
    return { css: 'linear(' + pts.join(', ') + ')', ms: Math.round(T * 1000) };
  }
  const SNAPPY = spring(0.38, 0.74), SOFT = spring(0.55, 0.82);
  if (CSS.supports('transition-timing-function', 'linear(0, 1)')) {
    document.documentElement.style.setProperty('--lg-spring', SOFT.css);
  }

  /* ---- glass on the existing controls ---- */
  const glassify = () => {
    document.querySelectorAll('.tpill, .mapbtns, #navPanel, .sheetin, .drawerin').forEach((el) => el.classList.add('lg'));
    document.querySelectorAll('.tpill, .mbtn, #navPanel .btn, .lg-tab, .lg-ask').forEach((el) => el.classList.add('lg-press'));
  };

  /* ---- tab bar ---- */
  const ICON = {
    today: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M2.5 20.5 9 8.2l3.6 6.1 2.2-3.4 6.7 9.6z"/></svg>',
    week: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15.5" rx="3.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>',
    crew: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="9" cy="8" r="3.6"/><path d="M2.6 19.5c.7-3.9 3.3-5.9 6.4-5.9s5.7 2 6.4 5.9z"/><circle cx="16.8" cy="9" r="2.8" opacity=".75"/><path d="M15.7 14c2.9 0 5 1.6 5.7 5.5h-4.5c-.2-2.2-.6-3.8-1.2-5.5z" opacity=".75"/></svg>',
    games: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.5 3.5h11v4a5.5 5.5 0 0 1-11 0z"/><path d="M11 13.5h2v3.5h-2z"/><rect x="7.5" y="17.5" width="9" height="3" rx="1.2"/><path d="M6.5 5H3.8a3 3 0 0 0 3.2 4.4M17.5 5h2.7a3 3 0 0 1-3.2 4.4" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>'
  };
  const TABS = [['today', 'Today'], ['week', 'Week'], ['crew', 'Crew'], ['games', 'Games']];
  const bar = document.createElement('div'); bar.id = 'lgTabs';
  const face = document.querySelector('#wxPill .gface');
  bar.innerHTML =
    '<nav class="lg-bar lg" role="tablist" aria-label="Ski-Paz">' +
    '<span class="lg-lens" aria-hidden="true"></span>' +
    TABS.map(([k, t], i) => `<button class="lg-tab" role="tab" data-tab="${k}" aria-selected="${i === 0}">${ICON[k]}<span>${t}</span></button>`).join('') +
    '</nav>' +
    `<button class="lg-ask lg" type="button" aria-label="Ask Shai">${face ? face.outerHTML : ''}</button>`;
  document.body.appendChild(bar);
  const lens = bar.querySelector('.lg-lens');
  const tabs = [...bar.querySelectorAll('.lg-tab')];
  let cur = 0;

  function placeLens(i, animate) {
    const t = tabs[i], nav = t.parentElement, r = t.getBoundingClientRect(), n = nav.getBoundingClientRect();
    const x = r.left - n.left - 4, w = r.width;
    lens.style.width = w + 'px';
    const to = `translateX(${x}px)`;
    if (!animate || !lens.animate) { lens.style.transform = to; return; }
    const from = getComputedStyle(lens).transform;
    const dist = Math.abs(x - (lens._x ?? x));
    const stretch = 1 + Math.min(dist / w, 3) * 0.12;   // the glass stretches more the further it travels
    lens.classList.add('moving');
    const a = lens.animate([
      { transform: from === 'none' ? to : from },
      { transform: `translateX(${((lens._x ?? x) + x) / 2}px) scale(${stretch}, ${1 / Math.sqrt(stretch)})`, offset: 0.45 },
      { transform: to }
    ], { duration: SNAPPY.ms + 120, easing: CSS.supports('transition-timing-function', 'linear(0, 1)') ? SNAPPY.css : 'cubic-bezier(.3,1.4,.5,1)' });
    a.onfinish = () => lens.classList.remove('moving');
    lens.style.transform = to;
    lens._x = x;
  }

  // the app's own buttons do the work, so every screen behaves exactly as it does today
  const click = (id) => { const el = $(id); if (el) el.click(); };
  function closeAll() {
    const d = $('drawer'); if (d && !d.hidden) click('drawerClose');
    document.querySelectorAll('.sheet,.gsheet').forEach((x) => (x.hidden = true));
    const pp = $('progPanel'); if (pp && !pp.hidden) click('progClose');
  }
  const ACTION = {
    today: () => closeAll(),
    week: () => { closeAll(); click('menuBtn'); },
    crew: () => { closeAll(); click('menuBtn'); click('groupBtn'); },
    games: () => { closeAll(); click('gamesBtn'); }
  };
  function select(i, run = true) {
    if (i === cur && run) { if (i === 0) closeAll(); return; }
    tabs.forEach((t, k) => t.setAttribute('aria-selected', k === i ? 'true' : 'false'));
    placeLens(i, true); cur = i;
    if (run) { try { ACTION[TABS[i][0]](); } catch (e) { console.warn('tab', e); } setTimeout(glassify, 30); }
  }
  tabs.forEach((t, i) => t.addEventListener('click', () => select(i)));
  bar.querySelector('.lg-ask').addEventListener('click', () => { closeAll(); $('briefSheet').hidden = false; click('bAsk'); setTimeout(glassify, 30); });

  // closing a sheet or the week with its own Done button brings the lens back to Today
  const watch = new MutationObserver(() => {
    const open = [...document.querySelectorAll('.sheet,.gsheet,.drawer')].some((x) => !x.hidden);
    if (!open && cur !== 0) select(0, false);
  });
  document.querySelectorAll('.sheet,.gsheet,.drawer').forEach((x) => watch.observe(x, { attributes: true, attributeFilter: ['hidden'] }));

  // touch feedback that also works while the finger slides (the :active state alone drops on iOS)
  document.addEventListener('pointerdown', (e) => { const b = e.target.closest('.lg-press'); if (b) b.classList.add('lg-down'); }, true);
  ['pointerup', 'pointercancel', 'pointerleave'].forEach((ev) => document.addEventListener(ev, () => document.querySelectorAll('.lg-down').forEach((b) => b.classList.remove('lg-down')), true));

  /* ---- lens refraction (Chrome / Android only: Safari doesn't run SVG filters on the backdrop) ---- */
  let svg;
  function displacementMap(w, h, r, bezel) {
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    const g = c.getContext('2d'), img = g.createImageData(w, h), d = img.data;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      // signed distance to the rounded rectangle's edge and the direction to it
      const px = x + 0.5 - w / 2, py = y + 0.5 - h / 2;
      const qx = Math.abs(px) - (w / 2 - r), qy = Math.abs(py) - (h / 2 - r);
      const ox = Math.max(qx, 0), oy = Math.max(qy, 0), out = Math.hypot(ox, oy);
      const dist = r - (out + Math.min(Math.max(qx, qy), 0));      // px from the edge, inward
      let nx = 0, ny = 0;
      if (out > 0) { nx = ox / out * Math.sign(px); ny = oy / out * Math.sign(py); }
      else if (qx > qy) nx = Math.sign(px); else ny = Math.sign(py);
      const k = dist < bezel ? Math.pow(1 - dist / bezel, 2.2) : 0;  // strongest right at the rim
      const i = (y * w + x) * 4;
      d[i] = 128 - nx * k * 127; d[i + 1] = 128 - ny * k * 127; d[i + 2] = 128; d[i + 3] = 255;
    }
    g.putImageData(img, 0, 0); return c.toDataURL();
  }
  function refract() {
    if (!CHROMIUM) return;
    document.documentElement.classList.add('lg-refract');
    if (!svg) {
      svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('width', 0); svg.setAttribute('height', 0); svg.style.position = 'absolute';
      document.body.appendChild(svg);
    }
    let n = 0;
    document.querySelectorAll('.lg').forEach((el) => {
      const b = el.getBoundingClientRect(); if (!b.width || !b.height || b.width * b.height > 420 * 420) return;
      const w = Math.round(b.width), h = Math.round(b.height);
      const r = Math.min(parseFloat(getComputedStyle(el).borderTopLeftRadius) || 0, h / 2, w / 2);
      const id = 'lgf' + (n++);
      const big = w * h > 160 * 160;
      svg.insertAdjacentHTML('beforeend',
        `<filter id="${id}" x="0" y="0" width="${w}" height="${h}" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">` +
        `<feGaussianBlur in="SourceGraphic" stdDeviation="${big ? 7 : 3}" result="b"/>` +
        `<feImage href="${displacementMap(w, h, r, Math.min(18, h / 2.6))}" x="0" y="0" width="${w}" height="${h}" result="m"/>` +
        `<feDisplacementMap in="b" in2="m" scale="${big ? 36 : 28}" xChannelSelector="R" yChannelSelector="G" result="d"/>` +
        `<feColorMatrix in="d" type="saturate" values="1.9"/></filter>`);
      el.style.backdropFilter = `url(#${id}) brightness(1.06)`;
    });
  }

  function init() {
    glassify();
    placeLens(0, false);
    if (CHROMIUM) { refract(); let t; addEventListener('resize', () => { clearTimeout(t); t = setTimeout(() => { svg && (svg.innerHTML = ''); refract(); placeLens(cur, false); }, 200); }); }
  }
  if (document.readyState === 'complete') setTimeout(init, 300); else addEventListener('load', () => setTimeout(init, 300));
  window.__lg = { select, refract, glassify, SNAPPY, SOFT };
})();
