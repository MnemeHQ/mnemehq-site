(function(){
  'use strict';
  /* CTA analytics — synced by scripts/sync_shared.py. Inert until GTM tags
   * consume these dataLayer events. Schema: docs/site/cta-system.md
   *
   * cta_click  { cta_intent, cta_position, cta_component, page_type, cta_destination }
   * code_copy  { copy_context, page_type }
   * form_start / form_submit / form_error / form_success are emitted by the
   * pilot form page (PR 3) using the same page_type helper.
   */

  function pageType() {
    var p = window.location.pathname;
    if (p === '/' || p === '/index.html') return 'homepage';
    var map = [
      ['/docs', 'docs'],
      ['/demo', 'demo'],
      ['/integrations', 'integration'],
      ['/works-with', 'integration'],
      ['/use-cases', 'use_case'],
      ['/insights', 'insight'],
      ['/concepts', 'concept'],
      ['/for', 'team'],
      ['/pilot', 'pilot'],
      ['/pricing', 'pricing'],
      ['/benchmark', 'benchmark']
    ];
    for (var i = 0; i < map.length; i++) {
      if (p.indexOf(map[i][0]) === 0) return map[i][1];
    }
    return 'other';
  }

  var PAGE_TYPE = pageType();

  function push(event, params) {
    params.page_type = PAGE_TYPE;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(Object.assign({ event: event }, params));
  }

  document.addEventListener('click', function(e){
    if (!e.target.closest) return;
    var el = e.target.closest('[data-cta-intent], [data-code-copy]');
    if (!el) return;

    // Copy controls report code_copy, not cta_click.
    if (el.hasAttribute('data-code-copy')) {
      var ctx = el.getAttribute('data-copy-text');
      if (!ctx) {
        var codeEl = el.closest('.install-module');
        if (!codeEl) codeEl = el.parentElement;
        if (codeEl) {
          var found = codeEl.querySelector('pre code') || codeEl.querySelector('code');
          ctx = found ? (found.textContent || '').trim() : 'unknown';
        } else {
          ctx = 'unknown';
        }
      }
      push('code_copy', { copy_context: ctx });
      return;
    }

    push('cta_click', {
      cta_intent: el.getAttribute('data-cta-intent'),
      cta_position: el.getAttribute('data-cta-position'),
      cta_component: el.getAttribute('data-cta-component'),
      cta_destination: el.getAttribute('href')
    });
  }, true);
})();
