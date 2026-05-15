/* Insight carousel — arrow navigation + autoscroll */
(function () {
  'use strict';

  var INTERVAL = 4500;   /* ms between auto-advances */
  var timer    = null;
  var paused   = false;

  function cardWidth(rail) {
    var card = rail.querySelector('.insight-card');
    return card ? card.offsetWidth + 20 : 440;
  }

  function advance(rail) {
    var w    = cardWidth(rail);
    var max  = rail.scrollWidth - rail.clientWidth;
    var next = rail.scrollLeft + w;
    /* wrap around */
    rail.scrollTo({ left: next > max ? 0 : next, behavior: 'smooth' });
  }

  function startTimer(rail) {
    if (timer) clearInterval(timer);
    timer = setInterval(function () {
      if (!paused) advance(rail);
    }, INTERVAL);
  }

  function init() {
    var prev  = document.getElementById('carousel-prev');
    var next  = document.getElementById('carousel-next');
    var rail  = document.getElementById('insight-carousel');
    if (!prev || !next || !rail || prev._carinit) return;
    prev._carinit = true;

    prev.addEventListener('click', function () {
      paused = true;
      rail.scrollBy({ left: -cardWidth(rail), behavior: 'smooth' });
      /* resume autoscroll after a short pause */
      setTimeout(function () { paused = false; }, 6000);
    });

    next.addEventListener('click', function () {
      paused = true;
      rail.scrollBy({ left: cardWidth(rail), behavior: 'smooth' });
      setTimeout(function () { paused = false; }, 6000);
    });

    /* Pause on hover / touch */
    rail.addEventListener('mouseenter', function () { paused = true; });
    rail.addEventListener('mouseleave', function () { paused = false; });
    rail.addEventListener('touchstart', function () { paused = true;  }, { passive: true });
    rail.addEventListener('touchend',   function () {
      setTimeout(function () { paused = false; }, 4000);
    }, { passive: true });

    startTimer(rail);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { setTimeout(init, 400); });
  } else {
    setTimeout(init, 400);
  }

  /* Re-attach after Dash re-renders */
  new MutationObserver(function () { setTimeout(init, 100); })
    .observe(document.body, { childList: true, subtree: true });
})();
