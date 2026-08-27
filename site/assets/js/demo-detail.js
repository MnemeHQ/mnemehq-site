(function () {
  var terminal = document.getElementById('enforcement-terminal');
  var replay = document.getElementById('terminal-replay');
  var steps = terminal ? Array.from(terminal.querySelectorAll('[data-demo-step]')) : [];
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var timers = [];

  function clearTimers() {
    timers.forEach(window.clearTimeout);
    timers = [];
  }

  function showAll() {
    if (!terminal) return;
    terminal.classList.remove('is-playing');
    steps.forEach(function (step) { step.classList.add('is-visible'); });
  }

  function play() {
    if (!terminal || !steps.length) return;
    clearTimers();
    steps.forEach(function (step) { step.classList.remove('is-visible'); });
    if (reduceMotion) {
      showAll();
      return;
    }
    terminal.classList.add('is-playing');
    steps.forEach(function (step, index) {
      timers.push(window.setTimeout(function () {
        step.classList.add('is-visible');
      }, 500 + (index * 900)));
    });
    timers.push(window.setTimeout(showAll, 500 + (steps.length * 900)));
  }

  if (replay) replay.addEventListener('click', play);
  if (terminal && replay && 'IntersectionObserver' in window && !reduceMotion) {
    var observer = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) {
        observer.disconnect();
        play();
      }
    }, { threshold: 0.18 });
    observer.observe(terminal);
  } else {
    showAll();
  }

  document.querySelectorAll('[data-copy-target]').forEach(function (button) {
    button.addEventListener('click', function () {
      var target = document.getElementById(button.getAttribute('data-copy-target'));
      if (!target || !navigator.clipboard) return;
      navigator.clipboard.writeText(target.textContent.trim()).then(function () {
        var original = button.textContent;
        button.textContent = 'Copied';
        button.classList.add('copied');
        window.setTimeout(function () {
          button.textContent = original;
          button.classList.remove('copied');
        }, 1600);
      });
    });
  });

  var path = window.location.pathname;
  var best = null;
  var bestLength = 0;
  document.querySelectorAll('.nav-links a').forEach(function (link) {
    var href = link.getAttribute('href');
    if (href && href.charAt(0) === '/' && href !== '/' && path.indexOf(href) === 0 && href.length > bestLength) {
      best = link;
      bestLength = href.length;
    }
  });
  if (best) best.classList.add('active');

  var stake = document.querySelector('.decision-stake');
  var stakePreview = new URLSearchParams(window.location.search).get('stake');
  if (stake && ['quiet', 'edge', 'band'].indexOf(stakePreview) !== -1) {
    stake.classList.add('decision-stake--' + stakePreview);
  }

  var menuButton = document.querySelector('.nav-hamburger');
  var navLinks = document.querySelector('.nav-links');
  if (menuButton && navLinks) {
    function setOpen(open) {
      navLinks.classList.toggle('open', open);
      menuButton.setAttribute('aria-expanded', String(open));
    }
    menuButton.addEventListener('click', function () {
      setOpen(!navLinks.classList.contains('open'));
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') setOpen(false);
    });
    navLinks.addEventListener('click', function (event) {
      if (event.target.tagName === 'A') setOpen(false);
    });
  }
})();
