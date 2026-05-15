/* Scroll-triggered reveal animations via IntersectionObserver */
(function () {
  'use strict';

  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        e.target.classList.add('is-visible');
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.07, rootMargin: '0px 0px -60px 0px' });

  function attach() {
    document.querySelectorAll('.reveal').forEach(function (el) {
      if (!el.dataset.revealAttached) {
        el.dataset.revealAttached = '1';
        obs.observe(el);
      }
    });
  }

  /* Run once on load */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { setTimeout(attach, 250); });
  } else {
    setTimeout(attach, 250);
  }

  /* Re-run whenever Dash injects new nodes */
  new MutationObserver(function () { attach(); })
    .observe(document.body, { childList: true, subtree: true });
})();
