/* Ways between ski areas the piste map doesn't have: riding a gondola down, a short walk or the
 * village bus. Added to BG as extra "lifts" so the router (and Plan from here) can use them. */
window.__addLinks = function(){
  if(window.__linksAdded) return; window.__linksAdded = true;
  const L = (kind, name, a, b) => BG.push(['L', kind, name, [a, b], null, -1, 0, 0, 0]);
  const byName = n => BG.find(b => b[0]==='L' && b[2]===n);
  const sm = byName('Super – Morzine'), sc = byName('Super – Châtel');
  // Avoriaz <-> Morzine: Super-Morzine gondola both ways, then a short walk to the Pléney / Crusaz lifts
  if(sm){ const c=sm[3]; L('gon', 'Super-Morzine gondola down', c[c.length-1], c[0]);
    L('gon', 'Walk to Pléney', c[0], [46.1799, 6.7019]); L('gon', 'Walk to Super-Morzine', [46.1799, 6.7019], c[0]); }
  if(sc){ const c=sc[3]; L('gon', 'Super-Châtel gondola down', c[c.length-1], c[0]);
    // Chatel village: the free bus between the Linga lifts and the Super-Chatel gondola
    const lg = byName('Linga'); if(lg){ const b=lg[3][0]; L('gon', 'Bus to Super-Châtel', b, c[0]); L('gon', 'Bus to Linga', c[0], b); } }
};
