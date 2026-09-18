/* A reader preference that must outlive a page turn.
 *
 * Every spine item is its own document, so a choice made on one page is
 * forgotten the moment the reader turns to the next file. This script,
 * linked from the <head> of every document, restores the choice from
 * localStorage before the page paints, by putting a class on <html> that the
 * stylesheet keys its rules on. Where the reading system strips scripts
 * (Kindle) or refuses storage, nothing here runs and the book reads exactly
 * as before; the control stays hidden (.needsjs) so the reader is never shown
 * a switch that does nothing.
 *
 * One preference, one class:
 *   toc-gloss   English titles shown under the Tibetan on the dkar chag.
 *
 * (A second preference, yig chung in green ink, lived here from 2026-09-15
 * to 2026-09-17 and was removed: not needed, and Books' Night theme
 * repainted it away.)
 */
(function () {
  var KEY = 'chosspyod.tocGloss';
  var CLASS = 'toc-gloss';
  var root = document.documentElement;

  function read() {
    try { return localStorage.getItem(KEY) === '1'; } catch (e) { return false; }
  }
  function write(on) {
    try { localStorage.setItem(KEY, on ? '1' : '0'); } catch (e) {}
  }
  function apply(on) {
    var rest = root.className.replace(new RegExp('(^|\\s)' + CLASS + '(?=\\s|$)', 'g'), '').replace(/^\s+/, '');
    root.className = on ? (rest ? rest + ' ' : '') + CLASS : rest;
  }

  apply(read());

  /* The control lives on the dkar chag only. It is a LINK, not a checkbox:
     Apple Books gives taps on form controls to its page turner, so a
     checkbox there can be seen but never ticked. Taps on links do arrive.
     Reveal it, show the stored state as its text, and store + apply on
     every tap. */
  function wire() {
    var sw = document.getElementById('tocGloss');
    if (!sw) { return; }
    function show() { sw.innerHTML = read() ? 'Hide English titles' : 'Show English titles'; }
    show();
    sw.onclick = function (ev) {
      var on = !read();
      write(on); apply(on); show();
      if (ev && ev.preventDefault) { ev.preventDefault(); }
      return false;
    };
    var host = sw.parentNode;   /* the span that wraps the switch in the hint line */
    if (host) { host.className = host.className.replace(/(^|\s)needsjs(?=\s|$)/g, ''); }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire, false);
  } else { wire(); }
})();

/* THE LANDING MARK. Mark the element a jump has just brought the reader to
 * with the class .landed, which the stylesheet rings (see THE LANDING
 * MARK there). Three triggers, because reading systems differ in how they
 * navigate to a fragment:
 *   1. :target, set by the engine — pure CSS, nothing here.
 *   2. location.hash on load and on hashchange, for a system that navigates
 *      by URL but does not set :target.
 *   3. the TAP itself: every jump link's click is seen here, the target id
 *      is marked at once when it is in this document, and written to
 *      localStorage when it is in another — where the destination document
 *      picks it up on load, or, if it is already loaded, through the
 *      'storage' event that fires in every other document of the book.
 *      Apple Books scrolls to the anchor itself and sets neither :target
 *      nor a fragment (build 323, macOS), so this is the trigger it needs.
 * The class is removed after 2.5 s (Books paints no CSS animation, so the
 * mark is static; see THE LANDING MARK in the stylesheet). Where scripts do
 * not run, nothing happens.
 */
(function () {
  var KEY = 'chosspyod.landing';
  var TTL = 15000;

  function note(s) { /* diagnostics hook, kept quiet */ }

  /* The first stretch of text to recite after the landing point — about a
     line, cut at a tsheg or shad — is wrapped in a span for the same 2.5 s
     and unwrapped again, so the eye is told not only "here" but "read
     from here". The next text node in document order that is not inside a
     link (links follow many jewels) and holds Tibetan letters. */
  var TIB = /[\u0f40-\u0fbc]/;
  function nextText(from) {
    var n = from, hops = 0;
    while (n && hops++ < 400) {
      if (n.nextSibling) { n = n.nextSibling; }
      else { n = n.parentNode; while (n && !n.nextSibling) n = n.parentNode; if (!n) return null; n = n.nextSibling; }
      if (!n) return null;
      if (n.nodeType === 1) {
        if (n.nodeName === 'A' || /(^|\s)(pageno|ipnpx|lpn|tibyigchung|inlineAnchor|repeatAnchor)(\s|$)/.test(n.className || '')) {
          /* skip this subtree */
          while (n && !n.nextSibling) n = n.parentNode;
          if (!n) return null;
          continue;
        }
        if (n.firstChild) { n = n.firstChild; if (n.nodeType === 3 && TIB.test(n.nodeValue)) return n; continue; }
      } else if (n.nodeType === 3 && TIB.test(n.nodeValue)) {
        var p = n.parentNode;
        while (p && p.nodeType === 1 && p.nodeName !== 'A') p = p.parentNode;
        if (!p || p.nodeType !== 1) return n;
      }
    }
    return null;
  }
  /* Inside a repeat span the first text node is the passage's own start. */
  function firstTextInside(el) {
    var n = el.firstChild, hops = 0;
    while (n && hops++ < 200) {
      if (n.nodeType === 3 && TIB.test(n.nodeValue)) return n;
      if (n.nodeType === 1 && n.nodeName !== 'A' && n.firstChild) { n = n.firstChild; continue; }
      while (n && !n.nextSibling && n !== el) n = n.parentNode;
      if (!n || n === el) return null;
      n = n.nextSibling;
    }
    return null;
  }
  function lightText(from, inside) {
    var tn = inside ? firstTextInside(from) : nextText(from);
    if (!tn) return null;
    var s = tn.nodeValue, i = s.search(TIB), cut = -1;
    if (i < 0) return null;
    for (var k = i + 28; k < s.length && k < i + 60; k++) {
      if (s.charAt(k) === '\u0f0b' || s.charAt(k) === '\u0f0d' || s.charAt(k) === '\u0f14') { cut = k + 1; break; }
    }
    if (cut < 0) cut = Math.min(s.length, i + 40);
    var head = tn.splitText(i), tail = head.splitText(cut - i);
    var w = document.createElement('span');
    w.className = 'landedtext';
    head.parentNode.insertBefore(w, head);
    w.appendChild(head);
    return function () {
      var parent = w.parentNode;
      if (!parent) return;
      parent.insertBefore(head, w);
      parent.removeChild(w);
      parent.normalize();
    };
  }

  function mark(el, how) {
    if (!el) return;
    /* A repeat brace sends the reader back to the START of its own passage:
       light the passage's first line, inside the braces, and put no ring on
       the span (build 332 lit the text after the closing brace instead). */
    var isRepeat = /(^|\s)repeat(Wrap|End)3?(\s|$)/.test(el.className || '');
    if (!isRepeat) {
      var cls = el.className.replace(/(^|\s)landed(?=\s|$)/g, '').replace(/^\s+/, '');
      el.className = (cls ? cls + ' ' : '') + 'landed';
    }
    var undo = null;
    try { undo = lightText(el, isRepeat); } catch (e) { undo = null; }
    note('landed ' + how);
    setTimeout(function () {
      el.className = el.className.replace(/(^|\s)landed(?=\s|$)/g, '').replace(/^\s+/, '');
      if (undo) { try { undo(); } catch (e) {} }
    }, 2500);
  }
  function fromHash() {
    var id = location.hash ? location.hash.slice(1) : '';
    if (id) mark(document.getElementById(id), 'hash');
  }
  function fromStore() {
    var v;
    try { v = localStorage.getItem(KEY); } catch (e) { return; }
    if (!v) return;
    var i = v.lastIndexOf(':'), id = v.slice(0, i), t = +v.slice(i + 1);
    if (!(Date.now() - t < TTL)) return;
    var el = document.getElementById(id);
    if (el) {
      try { localStorage.removeItem(KEY); } catch (e) {}
      mark(el, 'store');
    }
  }
  function tapped(a) {
    var href = a.getAttribute('href') || '';
    var i = href.indexOf('#');
    note('tap ' + href);
    if (i < 0) return;
    var id = href.slice(i + 1), file = href.slice(0, i);
    var here = location.pathname.split('/').pop();
    if (!file || file === here) {
      mark(document.getElementById(id), 'tap');
    } else {
      try { localStorage.setItem(KEY, id + ':' + Date.now()); } catch (e2) {}
    }
  }
  function wireLinks() {
    var links = document.getElementsByTagName('a'), n = 0;
    for (var k = 0; k < links.length; k++) {
      var a = links[k];
      if (!/(^|\s)jump/.test(a.className || '')) continue;
      n++;
      (function (a) {
        var prev = a.onclick;
        a.onclick = function (ev) { tapped(a); if (prev) return prev.call(a, ev); };
      })(a);
    }
    note('js ready, ' + n + ' jump links wired');
  }

  function start() {
    wireLinks();
    fromHash();
    fromStore();
    window.addEventListener('hashchange', fromHash, false);
    window.addEventListener('storage', function (ev) { if (!ev.key || ev.key === KEY) fromStore(); }, false);
    window.addEventListener('pageshow', fromStore, false);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, false);
  } else {
    start();
  }
})();
