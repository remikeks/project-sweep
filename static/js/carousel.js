/**
 * Minimal, dependency-free "slide in one after another" carousel used by
 * the landing page's featured-courses rail. Safe to include on every page:
 * it silently does nothing if no [data-carousel] element is present, and
 * gracefully skips autoplay/controls entirely when there's only one slide
 * (e.g. today, with a single seeded course) — no changes needed as more
 * courses get added later.
 */
(function () {
  function initCarousel(root) {
    var track = root.querySelector("[data-carousel-track]");
    if (!track) return;

    var slides = Array.prototype.slice.call(track.children);
    if (slides.length <= 1) return; // nothing to animate/control

    var dotsWrap = root.querySelector("[data-carousel-dots]");
    var dots = dotsWrap ? Array.prototype.slice.call(dotsWrap.children) : [];
    var prevBtn = root.querySelector("[data-carousel-prev]");
    var nextBtn = root.querySelector("[data-carousel-next]");

    var index = 0;
    var timer = null;
    var AUTOPLAY_MS = 5000;

    function go(i) {
      index = ((i % slides.length) + slides.length) % slides.length;
      track.style.transform = "translateX(-" + index * 100 + "%)";
      dots.forEach(function (dot, di) {
        dot.classList.toggle("active", di === index);
      });
    }

    function next() { go(index + 1); }
    function prev() { go(index - 1); }

    function start() { timer = window.setInterval(next, AUTOPLAY_MS); }
    function stop() { if (timer) { window.clearInterval(timer); timer = null; } }
    function restart() { stop(); start(); }

    if (nextBtn) nextBtn.addEventListener("click", function () { next(); restart(); });
    if (prevBtn) prevBtn.addEventListener("click", function () { prev(); restart(); });
    dots.forEach(function (dot, di) {
      dot.addEventListener("click", function () { go(di); restart(); });
    });

    root.addEventListener("mouseenter", stop);
    root.addEventListener("mouseleave", start);
    root.addEventListener("focusin", stop);
    root.addEventListener("focusout", start);

    go(0);
    start();
  }

  document.addEventListener("DOMContentLoaded", function () {
    var carousels = document.querySelectorAll("[data-carousel]");
    carousels.forEach(initCarousel);
  });
})();
