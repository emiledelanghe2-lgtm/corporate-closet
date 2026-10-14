(function () {
  var CC = window.CC || {};
  var root = document.body.getAttribute('data-root') || '';
  var HEART = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7.5-4.6-9.6-9.2C.8 8.3 3 4.5 6.6 4.5c2 0 3.5 1.1 5.4 3.1 1.9-2 3.4-3.1 5.4-3.1 3.6 0 5.8 3.8 4.2 7.3C19.5 16.4 12 21 12 21z"/></svg>';
  function ls(k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }
  function ss(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function all(sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); }
  function amazon(q, x) {
    var u = 'https://' + CC.config.domain + '/s?k=' + encodeURIComponent(q) + (x || '');
    if (CC.config.tag) u += '&tag=' + encodeURIComponent(CC.config.tag);
    return u;
  }
  function byslug(s) { return CC.outfits.filter(function (o) { return o.slug === s; })[0]; }
  function card(o) {
    return '<div class="card" data-colors="' + o.colors.join(' ') + '" data-style="' + o.style + '" data-shop="' + (o.shop ? 1 : 0) + '">' +
      '<a class="cl" href="' + root + 'outfits/' + o.slug + '/index.html"><div class="ph"><img src="' + root + 'img/' + o.pin +
      '.jpg" alt="' + esc(o.title) + '" loading="lazy" width="' + o.w + '" height="' + o.h + '">' + (o.shop ? '<b class="tag">Shop</b>' : '<b class="tag inspo">Inspo</b>') + '</div>' +
      '<span class="t">' + esc(o.title) + '</span></a>' +
      '<button class="heart" type="button" data-slug="' + o.slug + '" aria-pressed="false" aria-label="Save this outfit">' + HEART + '</button></div>';
  }

  /* saved outfits (hearts) */
  function refreshHearts() {
    var s = ls('cc_saved', []);
    all('.heart').forEach(function (b) { b.setAttribute('aria-pressed', s.indexOf(b.getAttribute('data-slug')) > -1 ? 'true' : 'false'); });
    all('[data-saved-count]').forEach(function (n) { n.textContent = s.length; });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('.heart') : null;
    if (!b) return;
    e.preventDefault();
    var slug = b.getAttribute('data-slug'), s = ls('cc_saved', []), i = s.indexOf(slug);
    if (i > -1) s.splice(i, 1); else s.push(slug);
    ss('cc_saved', s);
    refreshHearts();
    var grid = document.getElementById('savedGrid');
    if (grid) renderSaved();
  });

  function renderSaved() {
    var grid = document.getElementById('savedGrid'), empty = document.getElementById('savedEmpty');
    if (!grid) return;
    var s = ls('cc_saved', []).map(byslug).filter(Boolean);
    grid.innerHTML = s.map(card).join('');
    if (empty) empty.hidden = s.length > 0;
    refreshHearts();
  }

  /* outfit of the week */
  var otw = document.getElementById('otw');
  if (otw && CC.outfits) {
    var week = Math.floor(Date.now() / 604800000);
    var pool = CC.outfits.filter(function (x) { return x.shop; });
    var o = pool[week % pool.length];
    otw.innerHTML = '<a href="' + root + 'outfits/' + o.slug + '/index.html"><img src="' + root + 'img/' + o.pin + '.jpg" alt="' + esc(o.title) + '"></a>' +
      '<div><p class="eyebrow">Outfit of the week</p><h3>' + esc(o.title) + '</h3><p class="lead">' + esc(o.intro) + '</p>' +
      '<a class="btn solid" href="' + root + 'outfits/' + o.slug + '/index.html">Shop this look</a></div>';
  }

  /* size preference rewrites Amazon search links */
  var sizeBox = document.getElementById('sizes');
  function applySize(key) {
    var prefix = '';
    CC.sizes.forEach(function (z) { if (z.key === key) prefix = z.prefix; });
    all('a[data-q]').forEach(function (a) {
      if (a.hasAttribute('data-fixed')) return;
      var q = (prefix ? prefix + ' ' : '') + a.getAttribute('data-q');
      a.href = amazon(q, a.getAttribute('data-x') || '');
    });
  }
  if (sizeBox) {
    var cur = ls('cc_size', 'regular');
    all('input[name=size]', sizeBox).forEach(function (r) {
      r.checked = r.value === cur;
      r.addEventListener('change', function () { ss('cc_size', r.value); applySize(r.value); });
    });
    applySize(cur);
  }

  /* shop page color filter */
  var cf = document.getElementById('colorfilter');
  if (cf) {
    var cards = all('.fgrid .card');
    all('.chip', cf).forEach(function (chip) {
      chip.addEventListener('click', function () {
        var f = chip.getAttribute('data-filter');
        all('.chip', cf).forEach(function (c) { c.setAttribute('aria-pressed', String(c === chip)); });
        cards.forEach(function (c) { c.hidden = f !== 'all' && c.getAttribute('data-colors').split(' ').indexOf(f) < 0; });
      });
    });
  }

  /* style quiz: pick a color combo, then real pieces */
  var quiz = document.getElementById('quiz');
  if (quiz) {
    var picks = [];
    function cap(t) { return t.charAt(0).toUpperCase() + t.slice(1); }
    function fill(t, p) { return t.replace(/\{A\}/g, p.a).replace(/\{B\}/g, p.b); }
    function pal(p) { return '<span class="pal"><i style="background:' + p.sa + '"></i><i style="background:' + p.sb + '"></i></span>'; }
    function dotColor(opt, p) { return opt.fix ? '#3B4E6B' : (opt.t.indexOf('{A}') > -1 ? p.sa : p.sb); }
    function result() {
      var p = CC.palettes[picks[0]], score = {};
      score[p.style] = 1;
      var chosen = CC.steps.map(function (st, i) { var op = st.opts[picks[i + 1]]; score[op.s] = (score[op.s] || 0) + 1; return op; });
      var best = CC.styleOrder[0], max = -1;
      CC.styleOrder.forEach(function (k) { if ((score[k] || 0) > max) { max = score[k] || 0; best = k; } });
      var st = CC.styles[best];
      var list = CC.outfits.filter(function (o) { return o.style === best; }).sort(function (x, y) { return (y.shop ? 1 : 0) - (x.shop ? 1 : 0); }).slice(0, 4);
      history.replaceState(null, '', '#' + picks.join('.'));
      quiz.innerHTML = '<div class="result"><p class="eyebrow">Your outfit</p><h2>' + esc(st.name) + '</h2><p class="lead">' + esc(st.desc) + '</p>' +
        '<div class="recipe"><div class="rp head">' + pal(p) + '<b>' + esc(p.label) + '</b></div>' +
        chosen.map(function (op) {
          return '<div class="rp"><i class="dot" style="background:' + dotColor(op, p) + '"></i><b>' + esc(cap(fill(op.t, p))) + '</b>' +
            '<a class="btn ghost small" target="_blank" rel="sponsored nofollow noopener" href="' + amazon(fill(op.q, p), '') + '">Find similar</a></div>';
        }).join('') + '</div>' +
        '<p class="disc">These open an Amazon search for similar pieces in your colors.</p>' +
        '<h3 class="rt">Looks that match your style</h3><div class="grid">' + list.map(card).join('') + '</div>' +
        '<div class="acts"><button class="btn ghost" id="retake" type="button">Retake the quiz</button><a class="btn solid" href="' + root + 'shop/index.html">Shop all outfits</a></div></div>';
      document.getElementById('retake').addEventListener('click', function () { picks = []; history.replaceState(null, '', location.pathname); render(); });
      refreshHearts();
    }
    function render() {
      var total = CC.steps.length + 1, n = picks.length;
      if (n >= total) { result(); return; }
      var head = '<div class="qbar"><i style="width:' + (n / total * 100) + '%"></i></div><p class="qcount">Step ' + (n + 1) + ' of ' + total + '</p>';
      if (n === 0) {
        quiz.innerHTML = head + '<h2>Choose your color combination</h2><div class="opts two">' + CC.palettes.map(function (p, i) {
          return '<button class="opt pick-pal" type="button" data-i="' + i + '">' + pal(p) + '<span>' + esc(p.label) + '</span></button>';
        }).join('') + '</div>';
      } else {
        var p = CC.palettes[picks[0]], st = CC.steps[n - 1];
        quiz.innerHTML = head + '<p class="chosen">' + pal(p) + '<span>' + esc(p.label) + '</span></p><h2>' + esc(st.title) + '</h2><div class="opts">' +
          st.opts.map(function (op, i) { return '<button class="opt" type="button" data-i="' + i + '"><i class="dot" style="background:' + dotColor(op, p) + '"></i><span>' + esc(cap(fill(op.t, p))) + '</span></button>'; }).join('') + '</div>' +
          '<p class="back"><button type="button" class="linkbtn" id="back">Back</button></p>';
        document.getElementById('back').addEventListener('click', function () { picks.pop(); render(); });
      }
      all('.opt', quiz).forEach(function (b) { b.addEventListener('click', function () { picks.push(parseInt(b.getAttribute('data-i'), 10)); render(); }); });
    }
    var m = /^#(\d)\.(\d)\.(\d)\.(\d)\.(\d)$/.exec(location.hash);
    if (m && CC.palettes[+m[1]] && CC.steps.every(function (st, i) { return st.opts[+m[i + 2]]; })) { picks = m.slice(1).map(Number); result(); } else render();
  }

  /* capsule builder */
  var bd = document.getElementById('builder');
  if (bd) {
    var boxes = all('input[type=checkbox]', bd), out = document.getElementById('sum');
    function calc() {
      var sel = boxes.filter(function (b) { return b.checked; }), g = {tops: 0, bottoms: 0, layers: 0, dresses: 0, shoes: 0};
      sel.forEach(function (b) { g[b.getAttribute('data-g')]++; });
      var combos = (g.tops * g.bottoms + g.dresses) * (1 + g.layers);
      var msg = sel.length === 0 ? 'Pick the pieces you own or want. Aim for 8 to 12.' :
        sel.length < 8 ? 'Add a few more pieces to unlock more outfits.' : 'A solid capsule. Every piece mixes with the rest.';
      out.innerHTML = '<div class="n">' + combos + '</div><p>possible outfit combinations from ' + sel.length + ' pieces. ' + msg + '</p>' +
        (sel.length ? '<ul>' + sel.map(function (b) {
          return '<li><span>' + esc(b.getAttribute('data-n')) + '</span><a target="_blank" rel="sponsored nofollow noopener" href="' +
            amazon(b.getAttribute('data-q'), '') + '">Find</a></li>';
        }).join('') + '</ul>' : '');
    }
    boxes.forEach(function (b) { b.addEventListener('change', calc); });
    calc();
  }

  /* print button */
  all('[data-print]').forEach(function (b) { b.addEventListener('click', function () { window.print(); }); });

  renderSaved();
  refreshHearts();
})();
