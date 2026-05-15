/* Crossfading video background — three videos loop in sequence */
(function () {
  'use strict';

  var CROSSFADE_S   = 2.4;   /* seconds for opacity transition */
  var TRIGGER_EARLY = 6;     /* start fade this many seconds before video ends */
  var vids          = [];
  var current       = 0;
  var fading        = false;

  function init() {
    vids = ['vid-0', 'vid-1', 'vid-2']
      .map(function (id) { return document.getElementById(id); })
      .filter(Boolean);

    if (!vids.length) return;

    /* Activate first video */
    vids[0].style.opacity = '1';
    vids[0].play().catch(function () { /* autoplay blocked */ });

    vids.forEach(function (v, i) {
      v.addEventListener('timeupdate', function () {
        if (fading) return;
        var remaining = v.duration - v.currentTime;
        if (!isNaN(remaining) && remaining > 0 && remaining <= TRIGGER_EARLY) {
          crossfadeTo((i + 1) % vids.length);
        }
      });

      /* Fallback: if video ends without crossfade firing */
      v.addEventListener('ended', function () {
        if (!fading) crossfadeTo((i + 1) % vids.length);
      });
    });
  }

  function crossfadeTo(nextIdx) {
    if (fading) return;
    fading = true;

    var from = vids[current];
    var to   = vids[nextIdx];

    to.currentTime = 0;
    to.style.opacity = '0';
    to.play().catch(function () {});

    /* Small delay so browser registers the opacity reset before fading in */
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        to.style.opacity = '1';
        from.style.opacity = '0';
      });
    });

    setTimeout(function () {
      from.pause();
      from.currentTime = 0;
      current = nextIdx;
      fading  = false;
    }, (CROSSFADE_S + 0.6) * 1000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      setTimeout(init, 400);
    });
  } else {
    setTimeout(init, 400);
  }
})();
