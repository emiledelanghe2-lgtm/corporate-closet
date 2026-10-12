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
    return '<div class="card" data-colors="' + o.colors.join(' ') + '" data-style="' + o.style + '">' +
      '<a class="cl" href="' + root + 'outfits/' + o.slug + '/index.html"><div class="ph"><img src="' + root + 'img/' + o.pin +
      '.jpg" alt="' + esc(o.title) + '" loading="lazy" width="' + o.w + '" height="' + o.h + '"><b class="tag">Shop</b></div>' +
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
    var o = CC.outfits[week % CC.outfits.length];
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
    var cards = all('#grid .card');
    all('.chip', cf).forEach(function (chip) {
      chip.addEventListener('click', function () {
        var f = chip.getAttribute('data-filter');
        all('.chip', cf).forEach(function (c) { c.setAttribute('aria-pressed', String(c === chip)); });
        cards.forEach(function (c) { c.hidden = f !== 'all' && c.getAttribute('data-colors').split(' ').indexOf(f) < 0; });
      });
    });
  }

  /* style quiz */
  var quiz = document.getElementById('quiz');
  if (quiz) {
    var step = 0, score = {};
    function show(style) {
      var st = CC.styles[style], list = CC.outfits.filter(function (o) { return o.style === style; }).slice(0, 4);
      quiz.innerHTML = '<div class="result"><p class="eyebrow">Your office style</p><h2>' + esc(st.name) + '</h2><p class="lead">' + esc(st.desc) +
        '</p><div class="grid">' + list.map(card).join('') + '</div><div class="acts"><button class="btn ghost" id="retake" type="button">Retake the quiz</button>' +
        '<a class="btn solid" href="' + root + 'shop/index.html">Shop all outfits</a></div></div>';
      document.getElementById('retake').addEventListener('click', function () { step = 0; score = {}; history.replaceState(null, '', location.pathname); render(); });
      refreshHearts();
    }
    function render() {
      if (step >= CC.quiz.length) {
        var best = 'classic', max = -1;
        CC.styleOrder.forEach(function (k) { if ((score[k] || 0) > max) { max = score[k] || 0; best = k; } });
        history.replaceState(null, '', '#' + best);
        show(best);
        return;
      }
      var q = CC.quiz[step];
      quiz.innerHTML = '<div class="qbar"><i style="width:' + (step / CC.quiz.length * 100) + '%"></i></div><p class="qcount">Question ' + (step + 1) + ' of ' + CC.quiz.length +
        '</p><h2>' + esc(q.q) + '</h2><div class="opts">' + q.a.map(function (a, i) { return '<button class="opt" type="button" data-s="' + a.s + '">' + esc(a.t) + '</button>'; }).join('') + '</div>';
      all('.opt', quiz).forEach(function (b) {
        b.addEventListener('click', function () { var s = b.getAttribute('data-s'); score[s] = (score[s] || 0) + 1; step++; render(); });
      });
    }
    var h = location.hash.replace('#', '');
    if (CC.styles[h]) show(h); else render();
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
            amazon(b.getAttribute('data-q'), '') + '">Shop</a></li>';
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
