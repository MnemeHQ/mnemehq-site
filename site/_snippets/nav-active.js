(function(){
  var path = window.location.pathname;
  var best = null, bestLen = 0;
  document.querySelectorAll('.nav-links a').forEach(function(a){
    var href = a.getAttribute('href');
    if (href && href.charAt(0) === '/' && href !== '/' && path.indexOf(href) === 0 && href.length > bestLen) {
      best = a; bestLen = href.length;
    }
  });
  if (best) best.classList.add('active');
})();
