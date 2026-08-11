(function () {
  'use strict';

  var PAGE_SIZE = 24;
  var TYPE_ORDER = [
    'Analysis',
    'Research & reports',
    'Guides',
    'Concepts & reference',
    'Perspective',
    'Product & comparison'
  ];
  var COLLECTION_LABELS = {
    'ai-native': 'Architectural intent',
    'governance-problem': 'Governance',
    'market-context': 'Industry & market',
    'mneme-in-practice': 'Mneme in practice',
    'reference': 'Reference',
    'latest-analysis': 'Latest analysis'
  };
  var TYPE_LABELS = {
    'analysis': 'Analysis',
    'market context': 'Analysis',
    'industry analysis': 'Analysis',
    'engineering': 'Analysis',
    'infrastructure': 'Analysis',
    'architecture': 'Analysis',
    'technical deep dive': 'Analysis',
    'economics': 'Analysis',
    'agentic development': 'Analysis',
    'launch response': 'Analysis',
    'tooling analysis': 'Analysis',
    'research': 'Research & reports',
    'report response': 'Research & reports',
    'productivity': 'Research & reports',
    'guide': 'Guides',
    'operations': 'Guides',
    'reference': 'Concepts & reference',
    'category education': 'Concepts & reference',
    'category distinction': 'Concepts & reference',
    'category map': 'Concepts & reference',
    'concept': 'Concepts & reference',
    'thought leadership': 'Perspective',
    'worldview': 'Perspective',
    'perspective': 'Perspective',
    'integration': 'Product & comparison',
    'comparison': 'Product & comparison',
    'comparative': 'Product & comparison'
  };

  function normalizeText(value) {
    return (value || '').toLocaleLowerCase().replace(/\s+/g, ' ').trim();
  }

  function makeMetaItem(className, text) {
    var item = document.createElement('span');
    item.className = className;
    item.textContent = text;
    return item;
  }

  function makeMetaDot() {
    var dot = document.createElement('span');
    dot.className = 'card-dot';
    dot.setAttribute('aria-hidden', 'true');
    return dot;
  }

  function formattedDate(value) {
    if (!value) return '';
    var parsed = new Date(value + 'T00:00:00Z');
    if (Number.isNaN(parsed.getTime())) return '';
    return new Intl.DateTimeFormat('en', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      timeZone: 'UTC'
    }).format(parsed);
  }

  function normalizedType(rawType) {
    return TYPE_LABELS[normalizeText(rawType)] || 'Analysis';
  }

  function readState(validCollections, validTypes) {
    var params = new URLSearchParams(window.location.search);
    var collection = params.get('collection') || 'all';
    var type = params.get('type') || 'all';
    var sort = params.get('sort') || 'newest';
    var page = parseInt(params.get('page') || '1', 10);

    if (!validCollections.has(collection)) collection = 'all';
    if (!validTypes.has(type)) type = 'all';
    if (['newest', 'oldest', 'title'].indexOf(sort) === -1) sort = 'newest';
    if (!Number.isFinite(page) || page < 1) page = 1;

    return {
      q: (params.get('q') || '').trim(),
      collection: collection,
      type: type,
      sort: sort,
      page: page
    };
  }

  function start() {
    var controls = document.getElementById('catalog-controls');
    var results = document.getElementById('catalog-results');
    var paginationTop = document.getElementById('catalog-pagination-top');
    var pagination = document.getElementById('catalog-pagination');
    var status = document.getElementById('catalog-status');
    var empty = document.getElementById('catalog-empty');
    var search = document.getElementById('catalog-search');
    var collectionSelect = document.getElementById('catalog-collection');
    var typeSelect = document.getElementById('catalog-type');
    var sortSelect = document.getElementById('catalog-sort');
    var clearButton = document.getElementById('catalog-clear');
    var sourceLinks = Array.prototype.slice.call(
      document.querySelectorAll('.cards-section .insight-card-link')
    ).filter(function (link) {
      return /^\/insights\/[^/]+\/$/.test(link.getAttribute('href') || '');
    });

    if (!controls || !results || !pagination || !status || !empty || !sourceLinks.length) return;

    var items = sourceLinks.map(function (link, index) {
      var section = link.closest('.cards-section');
      var card = link.querySelector('.insight-card');
      var meta = link.querySelector('.card-meta');
      var tag = link.querySelector('.card-tag');
      var readTime = link.querySelector('.card-read-time');
      var title = link.querySelector('h3');
      var summary = link.querySelector('p');
      var collection = section && COLLECTION_LABELS[section.id] ? section.id : 'latest-analysis';
      var collectionLabel = COLLECTION_LABELS[collection];
      var rawType = tag ? tag.textContent.trim() : 'Analysis';
      var type = normalizedType(rawType);
      var published = link.getAttribute('data-published') || '';
      var dateLabel = formattedDate(published);
      var readingLabel = readTime ? readTime.textContent.trim() : '';

      if (meta) {
        meta.textContent = '';
        meta.appendChild(makeMetaItem('card-topic', collectionLabel));
        meta.appendChild(makeMetaDot());
        meta.appendChild(makeMetaItem('card-tag', type));
        if (dateLabel) {
          meta.appendChild(makeMetaDot());
          var time = document.createElement('time');
          time.className = 'card-date';
          time.dateTime = published;
          time.textContent = dateLabel;
          meta.appendChild(time);
        }
        if (readingLabel) {
          meta.appendChild(makeMetaDot());
          meta.appendChild(makeMetaItem('card-read-time', readingLabel));
        }
      }

      if (card) card.classList.add('catalog-row');

      return {
        link: link,
        index: index,
        collection: collection,
        type: type,
        published: published,
        title: title ? title.textContent.trim() : '',
        searchText: normalizeText([
          title ? title.textContent : '',
          summary ? summary.textContent : '',
          rawType,
          type,
          collectionLabel
        ].join(' '))
      };
    });

    var validCollections = new Set(['all'].concat(Object.keys(COLLECTION_LABELS)));
    var availableTypes = new Set(items.map(function (item) { return item.type; }));
    var validTypes = new Set(['all'].concat(Array.from(availableTypes)));

    TYPE_ORDER.forEach(function (type) {
      if (!availableTypes.has(type)) return;
      var option = document.createElement('option');
      option.value = type;
      option.textContent = type;
      typeSelect.appendChild(option);
    });

    var state = readState(validCollections, validTypes);
    var searchTimer = null;

    function syncControls() {
      search.value = state.q;
      collectionSelect.value = state.collection;
      typeSelect.value = state.type;
      sortSelect.value = state.sort;
    }

    function updateUrl(mode) {
      var params = new URLSearchParams();
      if (state.q) params.set('q', state.q);
      if (state.collection !== 'all') params.set('collection', state.collection);
      if (state.type !== 'all') params.set('type', state.type);
      if (state.sort !== 'newest') params.set('sort', state.sort);
      if (state.page > 1) params.set('page', String(state.page));

      var url = window.location.pathname;
      var query = params.toString();
      if (query) url += '?' + query;
      if (mode === 'push') window.history.pushState(null, '', url);
      else window.history.replaceState(null, '', url);
    }

    function paginationButton(label, page, options) {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = options.className || 'catalog-page-number';
      button.disabled = options.disabled || false;
      button.setAttribute('aria-label', options.ariaLabel || label);
      if (options.current) button.setAttribute('aria-current', 'page');
      button.innerHTML = options.html || label;
      button.addEventListener('click', function () {
        if (button.disabled || page === state.page) return;
        state.page = page;
        updateUrl('push');
        render(true);
      });
      return button;
    }

    function visiblePages(pageCount) {
      var pages = [];
      for (var page = 1; page <= pageCount; page += 1) {
        if (page === 1 || page === pageCount || Math.abs(page - state.page) <= 1) pages.push(page);
      }
      return pages;
    }

    function renderPagination(pageCount) {
      pagination.textContent = '';
      pagination.hidden = pageCount <= 1;
      if (pageCount <= 1) return;

      pagination.appendChild(paginationButton('Previous', state.page - 1, {
        className: 'catalog-page-step',
        disabled: state.page === 1,
        ariaLabel: 'Previous page',
        html: '<span aria-hidden="true">&larr;</span><span class="pagination-label"> Previous</span>'
      }));

      var numbers = document.createElement('div');
      numbers.className = 'catalog-page-numbers';
      var pages = visiblePages(pageCount);
      var previousPage = 0;
      pages.forEach(function (page) {
        if (previousPage && page - previousPage > 1) {
          var ellipsis = document.createElement('span');
          ellipsis.className = 'catalog-page-ellipsis';
          ellipsis.setAttribute('aria-hidden', 'true');
          ellipsis.textContent = '…';
          numbers.appendChild(ellipsis);
        }
        numbers.appendChild(paginationButton(String(page), page, {
          current: page === state.page,
          ariaLabel: page === state.page ? 'Page ' + page + ', current page' : 'Go to page ' + page
        }));
        previousPage = page;
      });
      pagination.appendChild(numbers);

      pagination.appendChild(paginationButton('Next', state.page + 1, {
        className: 'catalog-page-step',
        disabled: state.page === pageCount,
        ariaLabel: 'Next page',
        html: '<span class="pagination-label">Next </span><span aria-hidden="true">&rarr;</span>'
      }));
    }

    function renderTopPagination(pageCount) {
      if (!paginationTop) return;
      paginationTop.textContent = '';
      paginationTop.hidden = pageCount <= 1;
      if (pageCount <= 1) return;

      paginationTop.appendChild(paginationButton('Previous', state.page - 1, {
        className: 'catalog-page-step',
        disabled: state.page === 1,
        ariaLabel: 'Previous page',
        html: '<span aria-hidden="true">&larr;</span>'
      }));

      var summary = document.createElement('span');
      summary.className = 'catalog-page-summary';
      summary.textContent = 'Page ' + state.page + ' of ' + pageCount;
      paginationTop.appendChild(summary);

      paginationTop.appendChild(paginationButton('Next', state.page + 1, {
        className: 'catalog-page-step',
        disabled: state.page === pageCount,
        ariaLabel: 'Next page',
        html: '<span aria-hidden="true">&rarr;</span>'
      }));
    }

    function render(shouldScroll) {
      var query = normalizeText(state.q);
      var filtered = items.filter(function (item) {
        return (!query || item.searchText.indexOf(query) !== -1) &&
          (state.collection === 'all' || item.collection === state.collection) &&
          (state.type === 'all' || item.type === state.type);
      });

      filtered.sort(function (a, b) {
        if (state.sort === 'oldest') {
          return a.published.localeCompare(b.published) || a.index - b.index;
        }
        if (state.sort === 'title') {
          return a.title.localeCompare(b.title) || a.index - b.index;
        }
        return b.published.localeCompare(a.published) || a.index - b.index;
      });

      var pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
      state.page = Math.min(Math.max(state.page, 1), pageCount);
      var startIndex = (state.page - 1) * PAGE_SIZE;
      var pageItems = filtered.slice(startIndex, startIndex + PAGE_SIZE);
      var fragment = document.createDocumentFragment();

      pageItems.forEach(function (item) {
        item.link.hidden = false;
        fragment.appendChild(item.link);
      });
      results.textContent = '';
      results.appendChild(fragment);

      empty.hidden = filtered.length !== 0;
      results.hidden = filtered.length === 0;
      clearButton.hidden = !(
        state.q || state.collection !== 'all' || state.type !== 'all' || state.sort !== 'newest'
      );

      if (!filtered.length) {
        status.textContent = 'No articles match the selected filters.';
      } else {
        var endIndex = Math.min(startIndex + PAGE_SIZE, filtered.length);
        status.textContent = 'Showing ' + (startIndex + 1) + '–' + endIndex + ' of ' +
          filtered.length + (filtered.length === 1 ? ' article' : ' articles');
      }

      renderTopPagination(pageCount);
      renderPagination(pageCount);
      updateUrl('replace');

      if (shouldScroll) {
        controls.scrollIntoView({
          behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
          block: 'start'
        });
        status.focus({ preventScroll: true });
      }
    }

    search.addEventListener('input', function () {
      window.clearTimeout(searchTimer);
      searchTimer = window.setTimeout(function () {
        state.q = search.value.trim();
        state.page = 1;
        render(false);
      }, 180);
    });

    [collectionSelect, typeSelect, sortSelect].forEach(function (select) {
      select.addEventListener('change', function () {
        state.collection = collectionSelect.value;
        state.type = typeSelect.value;
        state.sort = sortSelect.value;
        state.page = 1;
        updateUrl('push');
        render(false);
      });
    });

    clearButton.addEventListener('click', function () {
      state = { q: '', collection: 'all', type: 'all', sort: 'newest', page: 1 };
      syncControls();
      updateUrl('push');
      render(false);
      search.focus();
    });

    controls.addEventListener('submit', function (event) {
      event.preventDefault();
      window.clearTimeout(searchTimer);
      state.q = search.value.trim();
      state.page = 1;
      updateUrl('push');
      render(false);
    });

    window.addEventListener('popstate', function () {
      state = readState(validCollections, validTypes);
      syncControls();
      render(false);
    });

    syncControls();
    render(false);
    document.body.classList.add('catalog-ready');
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
