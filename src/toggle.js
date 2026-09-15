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

  /* The control lives on the key page only. It is a LINK, not a checkbox:
     Apple Books gives taps on form controls to its page turner, so a
     checkbox there can be seen but never ticked. Taps on links do arrive.
     Reveal it, show the stored state as its text, and store + apply on
     every tap. */
  function wire() {
    var sw = document.getElementById('yigchungGreen');
    if (!sw) { return; }
    function show() { sw.innerHTML = read() ? 'green ink' : "reader's ink"; }
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
