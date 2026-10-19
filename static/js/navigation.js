/* Progressive enhancement: links remain reachable when JavaScript is absent. */
(function () {
  var nav = document.querySelector('.sw-nav');
  if (!nav) return;
  var toggle = nav.querySelector('.sw-nav-toggle');
  var links = nav.querySelector('#sw-nav-links');
  var label = nav.querySelector('[data-nav-toggle-label]');
  var account = nav.querySelector('[data-user-menu]');
  var compact = window.matchMedia('(max-width: 1119px)');
  if (!toggle || !links) return;
  nav.classList.add('is-enhanced');

  function closeAccount() { if (account) account.open = false; }
  function setOpen(open, returnFocus) {
    links.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    if (label) label.textContent = open ? 'Close' : 'Menu';
    if (!open) closeAccount();
    if (returnFocus) toggle.focus();
  }
  toggle.addEventListener('click', function () {
    setOpen(toggle.getAttribute('aria-expanded') !== 'true', false);
  });
  document.addEventListener('click', function (event) {
    if (!nav.contains(event.target)) setOpen(false, false);
    else if (account && !account.contains(event.target)) closeAccount();
  });
  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;
    if (account && account.open) {
      closeAccount();
      account.querySelector('summary').focus();
    } else if (links.classList.contains('open')) setOpen(false, true);
  });
  nav.addEventListener('focusout', function (event) {
    if (event.relatedTarget && !nav.contains(event.relatedTarget)) setOpen(false, false);
  });
  compact.addEventListener('change', function () {
    var focusWouldHide = compact.matches && links.contains(document.activeElement);
    setOpen(false, focusWouldHide);
  });
})();
