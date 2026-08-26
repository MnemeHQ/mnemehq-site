(function () {
  'use strict';

  var articleBody = document.querySelector('.article-wrap .article-body');
  var firstProof = null;

  if (articleBody && articleBody.dataset.integrationEnhanced !== 'true') {
    articleBody.dataset.integrationEnhanced = 'true';

    var originalChildren = Array.from(articleBody.children);
    var currentSection = null;
    var sectionIndex = 0;

    originalChildren.forEach(function (node) {
      if (node.matches && node.matches('h2')) {
        if (node.id === 'related-reading') {
          currentSection = null;
          return;
        }

        sectionIndex += 1;
        var section = document.createElement('section');
        section.className = 'integration-reading-section';

        if (!node.id) node.id = 'integration-section-' + sectionIndex;
        section.setAttribute('aria-labelledby', node.id);
        articleBody.insertBefore(section, node);
        section.appendChild(node);
        currentSection = section;
        return;
      }

      if (currentSection) currentSection.appendChild(node);
    });

    firstProof = articleBody.querySelector('.integration-reading-section');
  } else {
    firstProof = document.querySelector('main > .section.narrow');
  }

  if (!firstProof) return;

  var currentLabel = document.querySelector('.breadcrumb [aria-current="page"]');
  var integrationName = currentLabel ? currentLabel.textContent.trim() : 'this integration';

  if (!document.querySelector('.integration-mid-cta')) {
    var midCta = document.createElement('aside');
    midCta.id = 'setup-mneme';
    midCta.className = 'integration-mid-cta';
    midCta.setAttribute('aria-labelledby', 'integration-mid-cta-title');
    midCta.innerHTML =
      '<div>' +
        '<span class="integration-mid-cta__eyebrow">Next step</span>' +
        '<h2 id="integration-mid-cta-title">Set up Mneme with ' + integrationName + '</h2>' +
        '<p>Start with the quickstart, then use the integration-specific guidance on this page to connect the enforcement boundary.</p>' +
      '</div>' +
      '<a href="/docs/#quickstart" class="cta-btn-primary" data-cta-intent="setup" data-cta-position="mid" data-cta-component="cta_band">Open the quickstart <span aria-hidden="true">&rarr;</span></a>';

    firstProof.insertAdjacentElement('afterend', midCta);
  }

  var endCta = document.querySelector('.article-wrap .cta-block, main > .cta-band');
  if (!endCta) return;
  if (endCta.classList.contains('integration-end-cta')) return;

  endCta.classList.add('integration-end-cta');
  endCta.innerHTML =
    '<span class="integration-end-cta__eyebrow">Continue</span>' +
    '<h2>Ready to govern ' + integrationName + '?</h2>' +
    '<p>Complete the quickstart, then apply the integration-specific setup above in your repository.</p>' +
    '<div class="integration-end-cta__actions">' +
      '<a href="/docs/#quickstart" class="cta-btn-primary" data-cta-intent="setup" data-cta-position="end" data-cta-component="end_block">Open the setup guide</a>' +
      '<a href="/pilot/" class="integration-end-cta__secondary" data-cta-intent="pilot" data-cta-position="end" data-cta-component="end_block">Planning a team rollout? Request a pilot <span aria-hidden="true">&rarr;</span></a>' +
    '</div>';
})();
