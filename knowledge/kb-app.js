/* 工程师知识库 · 公共交互 */
(function () {
  'use strict';
  var NAV_URL = '/knowledge/kb-nav.json';
  var SEARCH_URL = '/knowledge/search_index.json';
  var navCache = null, searchCache = null, searchLoading = false;

  /* ---------- 侧栏导航树 ---------- */
  function renderTree(node, container, current) {
    if (!node.children || !node.children.length) return;
    var ul = document.createElement('ul');
    ul.className = 'tree';
    node.children.forEach(function (child) {
      var li = document.createElement('li');
      li.className = child.type === 'dir' ? 'dir' : 'page';
      var a = document.createElement('a');
      a.href = child.url;
      a.textContent = child.name;
      a.title = child.name;
      if (child.url === current) { a.className = 'active'; }
      li.appendChild(a);
      if (child.type === 'dir' && child.children && child.children.length) {
        var caret = document.createElement('span');
        caret.className = 'caret'; caret.textContent = '▸';
        caret.addEventListener('click', function (e) {
          e.stopPropagation(); e.preventDefault();
          li.classList.toggle('open');
          sub.classList.toggle('open');
        });
        li.insertBefore(caret, a);
        var sub = document.createElement('ul');
        sub.className = 'group';
        renderTree(child, sub, current);
        li.appendChild(sub);
        var isAncestor = current.indexOf(child.url) === 0 && current !== child.url;
        if (isAncestor) { li.classList.add('open'); sub.classList.add('open'); }
      }
      ul.appendChild(li);
    });
    container.appendChild(ul);
  }
  function loadNav(cb) {
    if (navCache) { cb(navCache); return; }
    fetch(NAV_URL).then(function (r) { return r.json(); }).then(function (d) {
      navCache = d; cb(d);
    }).catch(function () {});
  }
  function initTree() {
    var box = document.getElementById('kb-side');
    if (!box) return;
    var current = location.pathname;
    if (!/\/$/.test(current) && !/\.html$/.test(current)) { current = current + '/'; }
    loadNav(function (nav) {
      var root = document.createElement('div');
      root.className = 'kb-toolbar';
      var t1 = document.createElement('span'); t1.className = 'kb-toggle'; t1.textContent = '展开全部';
      var t2 = document.createElement('span'); t2.className = 'kb-toggle'; t2.textContent = '折叠全部';
      root.appendChild(t1); root.appendChild(t2);
      box.appendChild(root);
      renderTree(nav.tree, box, current);
      var groups = box.querySelectorAll('.group');
      t1.addEventListener('click', function () {
        groups.forEach(function (g) { g.classList.add('open'); g.parentElement.classList.add('open'); });
      });
      t2.addEventListener('click', function () {
        groups.forEach(function (g) { g.classList.remove('open'); g.parentElement.classList.remove('open'); });
      });
    });
  }

  /* ---------- 全文搜索 ---------- */
  var panel = null, input = null, results = null;
  function loadSearch(cb) {
    if (searchCache) { cb(searchCache); return; }
    if (searchLoading) { setTimeout(function () { loadSearch(cb); }, 120); return; }
    searchLoading = true;
    fetch(SEARCH_URL).then(function (r) { return r.json(); }).then(function (d) {
      searchCache = d; searchLoading = false; cb(d);
    }).catch(function () { searchLoading = false; });
  }
  function stripTags(html) {
    var d = document.createElement('div'); d.innerHTML = html;
    return d.textContent || '';
  }
  function runSearch(q) {
    var terms = q.trim().toLowerCase().split(/[\s，,。；;、]+/).filter(Boolean);
    if (!terms.length) { results.innerHTML = '<div class="kb-search-empty">输入关键词开始搜索</div>'; return; }
    loadSearch(function (idx) {
      var out = [];
      for (var i = 0; i < idx.length; i++) {
        var it = idx[i];
        var t = it.t.toLowerCase(), x = it.x.toLowerCase();
        var score = 0, hitAll = true;
        for (var k = 0; k < terms.length; k++) {
          if (t.indexOf(terms[k]) >= 0) score += 3;
          else if (x.indexOf(terms[k]) >= 0) score += 1;
          else { hitAll = false; break; }
        }
        if (hitAll && score > 0) {
          out.push({ score: score, it: it });
          if (out.length >= 40) break;
        }
      }
      out.sort(function (a, b) { return b.score - a.score; });
      results.innerHTML = '';
      if (!out.length) {
        results.innerHTML = '<div class="kb-search-empty">未找到相关内容</div>';
        return;
      }
      var shown = out.slice(0, 15);
      shown.forEach(function (r) {
        var d = document.createElement('div');
        d.className = 'kb-search-result';
        var tn = document.createElement('div'); tn.className = 't';
        tn.textContent = r.it.t;
        var un = document.createElement('div'); un.className = 'u';
        un.textContent = r.it.c || '';
        var sn = document.createElement('div'); sn.className = 's';
        var x = r.it.x;
        var pos = -1;
        for (var k = 0; k < terms.length; k++) { var p = x.toLowerCase().indexOf(terms[k]); if (p >= 0 && (pos < 0 || p < pos)) pos = p; }
        var snippet = pos >= 0 ? x.slice(Math.max(0, pos - 40), pos + 90) : x.slice(0, 130);
        sn.innerHTML = escapeHtml(snippet) + (snippet.length >= 130 ? '…' : '');
        d.appendChild(tn); d.appendChild(un); d.appendChild(sn);
        d.addEventListener('click', function () { location.href = r.it.u; });
        results.appendChild(d);
      });
    });
  }
  function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function initSearch() {
    input = document.getElementById('kb-search-input');
    if (!input) return;
    panel = document.getElementById('kb-search-panel');
    results = document.getElementById('kb-search-results');
    var timer = null;
    input.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(function () { panel.classList.add('show'); runSearch(input.value); }, 180);
    });
    input.addEventListener('focus', function () { panel.classList.add('show'); });
    document.addEventListener('click', function (e) {
      if (panel && !panel.contains(e.target) && e.target !== input) panel.classList.remove('show');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') panel.classList.remove('show');
      if (e.key === '/' && e.target === document.body) { e.preventDefault(); input.focus(); }
      if (e.key === 'Enter' && input === document.activeElement && panel.classList.contains('show')) {
        var first = results.querySelector('.kb-search-result');
        if (first) first.click();
      }
    });
  }

  /* ---------- 复制代码按钮 ---------- */
  function initCopy() {
    document.querySelectorAll('.kb-article pre').forEach(function (pre) {
      var btn = document.createElement('button');
      btn.className = 'kb-copybtn'; btn.textContent = '复制';
      btn.addEventListener('click', function () {
        var code = pre.querySelector('code');
        var text = code ? code.innerText : pre.innerText;
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () {
            btn.textContent = '已复制'; setTimeout(function () { btn.textContent = '复制'; }, 1200);
          });
        } else {
          var ta = document.createElement('textarea');
          ta.value = text; document.body.appendChild(ta); ta.select();
          document.execCommand('copy'); document.body.removeChild(ta);
          btn.textContent = '已复制'; setTimeout(function () { btn.textContent = '复制'; }, 1200);
        }
      });
      pre.appendChild(btn);
    });
  }

  /* ---------- 进度条 / 返回顶部 / TOC 高亮 ---------- */
  function initScroll() {
    var bar = document.getElementById('kb-progress');
    var bt = document.getElementById('kb-backtop');
    var tocLinks = document.querySelectorAll('.kb-toc-rt a, .kb-toc-inline a');
    function onScroll() {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      var p = h > 0 ? (window.scrollY / h) * 100 : 0;
      if (bar) bar.style.width = p + '%';
      if (bt) bt.classList.toggle('show', window.scrollY > 400);
      if (tocLinks.length) {
        var cur = null;
        document.querySelectorAll('.kb-article h2, .kb-article h3').forEach(function (el) {
          if (el.getBoundingClientRect().top <= 90) cur = el.id;
        });
        if (cur) {
          tocLinks.forEach(function (a) {
            a.classList.toggle('active', a.getAttribute('href') === '#' + cur);
          });
        }
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    if (bt) bt.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initTree(); initSearch(); initCopy(); initScroll();
  });
})();
