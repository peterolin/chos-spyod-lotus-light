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
