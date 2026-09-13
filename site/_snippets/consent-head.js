(function(){
  'use strict';
  /* Applies a returning visitor's stored consent choice before GTM loads, so
   * Consent Mode resolves analytics_storage on this pageview instead of only
   * from the next one. Paired with consent-banner.html, which collects the
   * choice and re-applies it on future accept/reject clicks. */
  try {
    var choice = localStorage.getItem('mneme_consent');
    if (choice === 'granted' || choice === 'denied') {
      gtag('consent', 'update', {
        'analytics_storage': choice,
        'ad_storage': 'denied',
        'ad_user_data': 'denied',
        'ad_personalization': 'denied'
      });
    }
  } catch (e) {}
})();
