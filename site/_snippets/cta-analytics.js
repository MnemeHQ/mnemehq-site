(function(){
  'use strict';
  /* CTA analytics — synced by scripts/sync_shared.py. Inert until GTM tags
   * consume these dataLayer events. Schema: docs/site/cta-system.md and
   * docs/site/gtm-tagging-requirements.md
   *
   * cta_click  { cta_intent, cta_position, cta_component, cta_destination,
   *              source_page, link_text, content_segment, page_type }
   * code_copy  { copy_context, source_page, content_segment, page_type }
   * pilot_form_* are emitted by the pilot form page using the same helpers.
   *
   * source_page/link_text/content_segment exist so a later report can ask which
   * CONTENT TYPE produced a conversion, not merely how many fired. Without
   * content_segment we cannot separate the developer/evaluation motion
   * (insight -> demo/quickstart -> install) from the architecture-leader motion
   * (insight -> audit -> pilot); both land in the same cta_click bucket.
   */

  /* Dev hosts must not reach the production property. localhost events were
   * observed in the GA4 export (page_location http://localhost:3456/...),
   * inflating outbound_link_clicked and landing-page counts. Suppress at the
   * source rather than filtering downstream, so BigQuery stays clean too. */
  function isDevHost() {
    var h = window.location.hostname;
    if (!h) return true;                       // file:// — never production
    if (h === 'localhost' || h === '127.0.0.1' || h === '0.0.0.0' || h === '::1') return true;
    if (h.indexOf('127.') === 0) return true;
    return /\.(local|test|localhost)$/.test(h);
  }

  if (isDevHost()) return;

  function pageType() {
    var p = window.location.pathname;
    if (p === '/' || p === '/index.html') return 'homepage';
    var map = [
      ['/docs', 'docs'],
      ['/demo', 'demo'],
      ['/audit', 'audit'],
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

  /* Declared per page by the CTA routing work:
   *   head meta name mneme:content-segment, e.g. developer_evaluation.
   * Absent on pages that have not been segmented; the parameter is then
   * omitted rather than guessed. */
  function contentSegment() {
    var m = document.querySelector('meta[name="mneme:content-segment"]');
    var v = m && m.getAttribute('content');
    return v ? v.trim() : undefined;
  }

  var PAGE_TYPE = pageType();
  var CONTENT_SEGMENT = contentSegment();
  var SOURCE_PAGE = window.location.pathname.replace(/\/+$/, '') || '/';

  function linkText(el) {
    var t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    return t ? t.slice(0, 100) : undefined;
  }

  function push(event, params) {
    params.page_type = PAGE_TYPE;
    params.source_page = SOURCE_PAGE;
    if (CONTENT_SEGMENT) params.content_segment = CONTENT_SEGMENT;
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
      cta_destination: el.getAttribute('href'),
      link_text: linkText(el)
    });
  }, true);
})();
