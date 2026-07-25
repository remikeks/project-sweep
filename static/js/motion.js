/**
 * Small, dependency-free motion layer shared by every page:
 *  - Sticky nav gains a shadow/background once the page scrolls.
 *  - Any element marked [data-reveal] fades/slides into place the first
 *    time it enters the viewport (IntersectionObserver, one-shot).
 * Both are no-ops if the relevant elements/APIs aren't present, so this
 * script is safe to include on every template unconditionally.
 */
(function () {
  function initNavScroll() {
    var nav = document.querySelector(".sw-nav");
    if (!nav) return;

    function update() {
      nav.classList.toggle("is-scrolled", window.scrollY > 8);
    }

    update();
    window.addEventListener("scroll", update, { passive: true });
  }

  function initScrollReveal() {
    var targets = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));
    if (!targets.length) return;

    if (!("IntersectionObserver" in window)) {
      // No IO support: just show everything immediately.
      targets.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;
          var delay = el.getAttribute("data-reveal-delay");
          if (delay) {
            el.style.transitionDelay = delay + "ms";
          }
          el.classList.add("is-visible");
          observer.unobserve(el);
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );

    targets.forEach(function (el) { observer.observe(el); });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initNavScroll();
    initScrollReveal();
  });
})();
