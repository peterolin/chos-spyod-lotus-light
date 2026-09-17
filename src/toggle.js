/* Reader preferences that must outlive a page turn.
 *
 * Every spine item is its own document, so a checkbox ticked on the key page
 * is forgotten the moment the reader turns to the next file. This script,
 * linked from the <head> of every document, restores the choice from
 * localStorage before the page paints, by putting a class on <html> that the
 * stylesheet keys its rules on. Where the reading system strips scripts
 * (Kindle) or refuses storage, nothing here runs and the book reads exactly
 * as before; the control on the key page stays hidden (.needsjs) so the
 * reader is never shown a switch that does nothing.
 *
 * Preferences, one class each:
 *   yigchung-green   yig chung in green ink instead of the body ink.
 *
 * It also marks <html> with the class `js` (so the stylesheet knows a script
 * runs) and, for every big prayer title, measures whether the title fits on
 * one line beside its arrows; where it does not, the heading gets the class
 * `wrapped` and the arrows move to a row above the title (stylesheet, F14).
 */
(function () {
  var KEY = 'chosspyod.yigchungGreen';
  var CLASS = 'yigchung-green';
  var root = document.documentElement;

  function read() {
    try { return localStorage.getItem(KEY) === '1'; } catch (e) { return false; }
  }
  function write(on) {
    try { localStorage.setItem(KEY, on ? '1' : '0'); return true; } catch (e) { return false; }
  }
  function apply(on) {
    var rest = root.className.replace(new RegExp('(^|\\s)' + CLASS + '(?=\\s|$)', 'g'), '').replace(/^\s+/, '');
    root.className = on ? (rest ? rest + ' ' : '') + CLASS : rest;
  }

  apply(read());
  root.className = (root.className ? root.className + ' ' : '') + 'js';

  /* TITLE FIT (F14). A title is never squeezed between its arrows: measure
     its natural one-line width against the room beside them; if it does not
     fit, class `wrapped` moves the arrows to their own row. Measured with
     white-space:nowrap so the width is the whole title on one line, then
     restored. Runs when the DOM is ready, again when the embedded fonts have
     arrived (widths change with the face), and on resize and rotation. */
  function fitTitles() {
    var heads = document.querySelectorAll('.tocpage1, .tocpage2');
    for (var i = 0; i < heads.length; i++) {
      var h = heads[i];
      if (/\bminor\b/.test(h.className)) { continue; }
      var title = h.querySelector('.title'), left = h.querySelector('.left'), right = h.querySelector('.right');
      if (!title || !left || !right) { continue; }
      h.className = h.className.replace(/(^|\s)wrapped(?=\s|$)/g, '');
      var prev = title.style.whiteSpace;
      title.style.whiteSpace = 'nowrap';
      var need = title.getBoundingClientRect().width;
      title.style.whiteSpace = prev;
      var room = h.clientWidth - left.offsetWidth - right.offsetWidth - 16;
      if (need > room) { h.className += ' wrapped'; }
    }
  }
  var fitTimer = null;
  function fitSoon() { if (fitTimer) { clearTimeout(fitTimer); } fitTimer = setTimeout(fitTitles, 60); }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fitTitles, false);
  } else { fitTitles(); }
  window.addEventListener('load', fitTitles, false);
  window.addEventListener('resize', fitSoon, false);
  window.addEventListener('orientationchange', fitSoon, false);
  if (document.fonts && document.fonts.ready && document.fonts.ready.then) { document.fonts.ready.then(fitTitles); }

  /* The control lives on the key page only. It is a LINK, not a checkbox:
     Apple Books gives taps on form controls to its page turner, so a
     checkbox there can be seen but never ticked. Taps on links do arrive.
     Reveal it, show the stored state as its text, and store + apply on
     every tap. */
  function wire() {
    var sw = document.getElementById('yigchungGreen');
    if (!sw) { return; }
    function show() { sw.innerHTML = read() ? 'green ink' : "eBook reader's ink"; }
    show();
    sw.onclick = function (ev) {
      var on = !read();
      write(on); apply(on); show();
      if (ev && ev.preventDefault) { ev.preventDefault(); }
      return false;
    };
    var host = document.getElementById('prefs');
    if (host) { host.className = host.className.replace(/(^|\s)needsjs(?=\s|$)/g, ''); }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire, false);
  } else { wire(); }
})();
