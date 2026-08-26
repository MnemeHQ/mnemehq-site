(function () {
  'use strict';

  var articleBody = document.querySelector('.article-wrap .article-body');
  if (!articleBody || articleBody.dataset.integrationEnhanced === 'true') return;
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

  var firstSection = articleBody.querySelector('.integration-reading-section');
  if (!firstSection || articleBody.querySelector('.integration-install-cta')) return;

  var installCta = document.createElement('aside');
  installCta.id = 'install-mneme';
  installCta.className = 'integration-install-cta';
  installCta.setAttribute('aria-labelledby', 'integration-install-title');
  installCta.innerHTML =
    '<div>' +
      '<span class="integration-install-cta__eyebrow">Ready to try it?</span>' +
      '<h2 id="integration-install-title">Install the governance layer</h2>' +
      '<p>Add Mneme locally, then continue with the integration-specific setup below. Open source, self-hosted, and stored with your repository.</p>' +
    '</div>' +
    '<div>' +
      '<code class="integration-install-cta__command">pipx install &quot;mneme-hq&gt;=0.5.1&quot;</code>' +
      '<div class="integration-install-cta__actions">' +
        '<button class="integration-install-cta__copy" type="button">Copy install command</button>' +
        '<a class="integration-install-cta__docs" href="/docs/">Read the docs <span aria-hidden="true">&rarr;</span></a>' +
      '</div>' +
    '</div>';

  firstSection.insertAdjacentElement('afterend', installCta);

  var copyButton = installCta.querySelector('.integration-install-cta__copy');
  var command = 'pipx install "mneme-hq>=0.5.1"';

  copyButton.addEventListener('click', function () {
    var copy = navigator.clipboard && navigator.clipboard.writeText
      ? navigator.clipboard.writeText(command)
      : Promise.reject(new Error('Clipboard API unavailable'));

    copy.then(function () {
      copyButton.textContent = 'Copied';
      window.setTimeout(function () {
        copyButton.textContent = 'Copy install command';
      }, 1600);
    }).catch(function () {
      copyButton.textContent = command;
    });
  });
})();
