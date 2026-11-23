/* Setup chooser for /setup/. Data: setup-chooser-data-v1.js (source of truth:
 * site/integrations/index.html). Without JavaScript the page shows the same
 * options as a grouped list of links, rendered at build time.
 *
 * Analytics: result links carry the site's existing cta_click attributes
 * (docs/site/gtm-tagging-requirements.md); cta-analytics.js sends them. The
 * selections themselves send no event: the contract has no event for them.
 */
(function () {
  'use strict';
  var DATA = window.MNEME_SETUP_CHOOSER;
  var app = document.querySelector('[data-chooser]');
  if (!DATA || !app) return;

  var GUIDES = {
    '/setup/claude-code/': 'Claude Code + CI setup',
    '/setup/codex-cli/': 'Codex CLI + CI setup',
    '/setup/opencode/': 'OpenCode + CI setup',
    '/setup/ci/': 'CI-only setup',
    '/setup/mcp/': 'decision MCP setup',
    '/setup/software-factory/': 'software factory setup'
  };
  var GOALS = {
    full: 'Complete governance setup',
    ci: 'CI enforcement only',
    mcp: 'Decision MCP only'
  };
  var byId = {};
  DATA.options.forEach(function (o) { byId[o.id] = o; });

  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text != null) n.textContent = text;
    return n;
  }

  function badge(status) {
    var s = (status || '').toLowerCase();
    if (!s) return { key: 'unlisted', text: 'Not in the catalogue' };
    var key = s.indexOf('no adapter') === 0 ? 'none' : s.split(/[\s·]/)[0];
    return { key: key, text: status };
  }

  /* ---- Step 2: a Popular row, then every tool grouped as the catalogue
   * groups them, behind a disclosure. A popular tool appears in its group as
   * a second label for the same radio, so each tool has exactly one input. */
  var POPULAR = DATA.popular || [];
  var popularHost = app.querySelector('[data-env-popular]');
  var groupsHost = app.querySelector('[data-env-groups]');
  var allBox = app.querySelector('[data-env-all]');

  /* Popular radios and catalogue radios are two radio groups (one Tab stop
   * each); choosing in one clears the other, so exactly one tool is selected. */
  function chip(o, withInput, groupName) {
    var b = badge(o.status);
    var id = 'env-' + o.id;
    var label = el('label', { 'class': 'env-option' + (withInput ? '' : ' env-option--alias'), 'for': id, 'data-env': o.id });
    if (withInput) label.appendChild(el('input', { type: 'radio', name: groupName, value: o.id, id: id }));
    label.appendChild(el('span', { 'class': 'env-dot env-dot--' + b.key, 'aria-hidden': 'true' }));
    label.appendChild(el('span', { 'class': 'env-name' }, o.name));
    label.appendChild(el('span', { 'class': 'sr-only' }, ', ' + b.text));
    return label;
  }

  POPULAR.forEach(function (id) { if (byId[id]) popularHost.appendChild(chip(byId[id], true, 'env')); });
  DATA.groups.forEach(function (g) {
    var opts = DATA.options.filter(function (o) { return o.group === g.id; });
    if (!opts.length) return;
    var wrap = el('div', { 'class': 'env-group' });
    var gid = 'env-group-' + g.id;
    wrap.appendChild(el('p', { 'class': 'env-group-label', id: gid }, g.label));
    var row = el('div', { 'class': 'env-options', role: 'group', 'aria-labelledby': gid });
    opts.forEach(function (o) { row.appendChild(chip(o, POPULAR.indexOf(o.id) === -1, 'env-all')); });
    wrap.appendChild(row);
    groupsHost.appendChild(wrap);
  });
  var allSummary = allBox.querySelector('summary');
  allSummary.textContent = 'Show all ' + DATA.options.length + ' tools, grouped as in the catalogue';

  /* ---- Result ---- */
  function hookLayer(o, goal) {
    if (goal === 'ci') return { state: 'off', label: 'CLI in CI only', text: 'The CI job installs the Mneme CLI and runs mneme check. No agent hook.' };
    if (goal === 'mcp') return { state: 'off', label: 'Not in this setup', text: 'MCP blocks nothing. Add a hook and CI when you want enforcement.' };
    if (o.hook === 'shipped' || o.hook === 'validated' || o.hook === 'via') return { state: 'required', label: 'Required', text: o.hook_text };
    if (o.hook === 'experimental') return { state: 'experimental', label: 'Experimental', text: o.hook_text };
    return { state: 'gap', label: 'No Mneme hook', text: o.hook_text };
  }
  function mcpLayer(o, goal) {
    if (goal === 'ci') return { state: 'off', label: 'Not in this setup', text: 'Add it later if agents should look decisions up before they write.' };
    if (goal === 'mcp') {
      return { state: 'required', label: 'Required', text: o.id === 'claude-code'
        ? 'The plugin’s /mneme:context covers basic lookup. The MCP server adds search by path, tracing and proposals.'
        : 'Runs in any host that can start a local MCP server over stdio. Check that your tool supports that; we have not tested every host.' };
    }
    return { state: 'optional', label: 'Optional', text: o.mcp_note || 'Add it if your tool can start a local MCP server. It helps the agent find decisions and blocks nothing.' };
  }
  function ciLayer(o, goal) {
    if (goal === 'mcp') return { state: 'off', label: 'Not in this setup', text: 'Nothing verifies changes in this setup.' };
    return { state: 'required', label: 'Required', text: 'A required check on every pull request or merge request, whoever wrote the change.' };
  }
  function headline(o, goal) {
    if (goal === 'mcp') return 'Decision lookup for ' + o.name + '. It informs the agent and enforces nothing.';
    if (goal === 'ci') return o.group === 'ci' ? o.name + ' runs the check on every change.' : 'A CI check on every change, whatever ' + o.name + ' wrote.';
    if (o.group === 'ci') return o.name + ' is the enforcement layer. Add an agent hook where you can.';
    if (o.hook === 'shipped' || o.hook === 'validated' || o.hook === 'via') return 'Agent hook plus a required CI check.';
    if (o.hook === 'experimental') return 'Experimental hook. Treat CI as the check you rely on.';
    return 'No Mneme hook here, so CI is your enforcement layer.';
  }
  function links(o, goal) {
    var primary, secondary = null;
    if (goal === 'ci') primary = '/setup/ci/';
    else if (goal === 'mcp') primary = '/setup/mcp/';
    else if (o.guide) primary = o.guide;
    else if (o.page && o.hook !== 'none') primary = o.page;
    else primary = '/setup/ci/';
    if (primary.indexOf('/setup/') !== 0) secondary = '/setup/ci/';
    else if (o.page && o.page !== primary && o.page !== '/integrations/') secondary = o.page;
    return { primary: primary, secondary: secondary };
  }
  function linkLabel(href, o, isPrimary) {
    if (GUIDES[href]) return (isPrimary ? 'Open the ' : 'Then add the ') + GUIDES[href];
    if (href.indexOf('/insights/') === 0) return 'Read our ' + o.name + ' analysis';
    return 'Read the ' + o.name + ' integration page';
  }
  function intentFor(href) { return href.indexOf('/setup/') === 0 ? 'setup' : 'integration'; }

  var result = app.querySelector('[data-result]');

  function render(envId, goal) {
    var o = byId[envId];
    if (!o) return;
    var b = badge(o.status);
    result.textContent = '';
    var head = el('div', { 'class': 'result-head' });
    var titleRow = el('div', { 'class': 'result-title-row' });
    titleRow.appendChild(el('h3', { 'class': 'result-title', id: 'result-title-anchor', tabindex: '-1' }, o.name));
    titleRow.appendChild(el('span', { 'class': 'status-badge status-badge--' + b.key }, b.text));
    head.appendChild(titleRow);
    head.appendChild(el('p', { 'class': 'result-goal' }, GOALS[goal]));
    head.appendChild(el('p', { 'class': 'result-headline' }, headline(o, goal)));
    result.appendChild(head);

    var stack = el('ol', { 'class': 'layer-stack', 'aria-label': 'Recommended layers' });
    [
      ['Discover', 'Decision MCP server', mcpLayer(o, goal)],
      ['Enforce', 'Mneme CLI and agent hook', hookLayer(o, goal)],
      ['Verify', 'CI check before merge', ciLayer(o, goal)]
    ].forEach(function (row) {
      var li = el('li', { 'class': 'layer-row layer-row--' + row[2].state });
      var top = el('div', { 'class': 'layer-row-top' });
      var name = el('span', { 'class': 'layer-row-name' });
      name.appendChild(el('strong', null, row[0]));
      name.appendChild(el('span', null, row[1]));
      top.appendChild(name);
      top.appendChild(el('span', { 'class': 'layer-state' }, row[2].label));
      li.appendChild(top);
      li.appendChild(el('p', { 'class': 'layer-row-text' }, row[2].text));
      stack.appendChild(li);
    });
    result.appendChild(stack);

    var limit = el('div', { 'class': 'result-limit' });
    limit.appendChild(el('p', { 'class': 'result-limit-label' }, goal === 'mcp' ? 'What this does not do' : 'Coverage limit'));
    limit.appendChild(el('p', null, goal === 'mcp'
      ? 'The MCP server can search and explain decisions and take proposals for people to review. It cannot accept, activate or enforce a decision.'
      : (goal === 'ci' ? 'CI checks the files a change adds or modifies, after they are written. It covers only what your pipeline runs on.' : o.limit)));
    result.appendChild(limit);

    var l = links(o, goal);
    var actions = el('div', { 'class': 'result-actions' });
    var p = el('a', { 'class': 'cta-btn-primary', href: l.primary, 'data-cta-intent': intentFor(l.primary), 'data-cta-position': 'mid', 'data-cta-component': 'context' }, linkLabel(l.primary, o, true));
    actions.appendChild(p);
    if (l.secondary) {
      actions.appendChild(el('a', { 'class': 'cta-btn-outline', href: l.secondary, 'data-cta-intent': intentFor(l.secondary), 'data-cta-position': 'mid', 'data-cta-component': 'context' }, linkLabel(l.secondary, o, false)));
    }
    result.appendChild(actions);
  }

  function current() {
    var e = app.querySelector('input[name="env"]:checked, input[name="env-all"]:checked');
    var g = app.querySelector('input[name="goal"]:checked');
    return { env: e ? e.value : 'claude-code', goal: g ? g.value : 'full' };
  }
  function select(envId, goal) {
    var e = document.getElementById('env-' + envId);
    var g = app.querySelector('input[name="goal"][value="' + goal + '"]');
    if (e) { clearOther(e.name); e.checked = true; }
    if (g) g.checked = true;
  }
  function clearOther(name) {
    var other = name === 'env' ? 'env-all' : 'env';
    app.querySelectorAll('input[name="' + other + '"]').forEach(function (r) { r.checked = false; });
  }
  /* A popular tool's second label, inside the catalogue list, mirrors the
   * selection state of its one radio. */
  function syncAliases(envId) {
    app.querySelectorAll('.env-option--alias').forEach(function (a) {
      a.classList.toggle('selected', a.getAttribute('data-env') === envId);
    });
  }
  var goalDesc = app.querySelector('[data-goal-desc]');
  function syncGoal(goal) {
    var src = app.querySelector('input[name="goal"][value="' + goal + '"]');
    if (goalDesc && src) goalDesc.textContent = src.getAttribute('data-desc') || '';
  }

  /* ---- Mobile bar: below 768px the result sits under the whole list, so a
   * selection shows a compact summary pinned to the bottom of the screen. ---- */
  var bar = document.querySelector('[data-chooser-bar]');
  var mobile = window.matchMedia('(max-width: 767px)');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var resultInView = false;
  var userChose = false;

  function fillBar(envId, goal) {
    if (!bar) return;
    var o = byId[envId];
    var b = badge(o.status);
    var l = links(o, goal);
    bar.querySelector('[data-bar-name]').textContent = o.name;
    var bb = bar.querySelector('[data-bar-badge]');
    bb.className = 'status-badge status-badge--' + b.key;
    bb.textContent = b.text || 'Not in the catalogue';
    var go = bar.querySelector('[data-bar-go]');
    go.setAttribute('href', l.primary);
    go.setAttribute('data-cta-intent', intentFor(l.primary));
    go.textContent = linkLabel(l.primary, o, true);
  }
  function showBar() {
    if (!bar) return;
    var on = userChose && mobile.matches && !resultInView;
    bar.hidden = !on;
    document.body.classList.toggle('chooser-bar-on', on);
    var h = on ? bar.offsetHeight : 0;
    document.documentElement.style.scrollPaddingBottom = h ? (h + 16) + 'px' : '';
    document.body.style.paddingBottom = h ? h + 'px' : '';
  }
  if (bar) {
    bar.querySelector('[data-bar-details]').addEventListener('click', function () {
      var target = document.getElementById('result-title-anchor');
      if (target) target.focus({ preventScroll: true });
      var panel = app.querySelector('.result');
      var y = panel.getBoundingClientRect().top + window.pageYOffset - 80; // below the sticky nav
      window.scrollTo({ top: y, behavior: reduced.matches ? 'auto' : 'smooth' });
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        resultInView = entries[0].isIntersecting;
        showBar();
      }, { threshold: 0.15 }).observe(result);
    }
    (mobile.addEventListener ? mobile.addEventListener('change', showBar) : mobile.addListener(showBar));
    /* Never let the bar cover the element that has focus. */
    document.addEventListener('focusin', function (e) {
      if (bar.hidden || bar.contains(e.target)) return;
      var r = e.target.getBoundingClientRect();
      var top = bar.getBoundingClientRect().top;
      if (r.bottom > top - 8) window.scrollBy(0, r.bottom - top + 16);
    });
  }

  function update() {
    var c = current();
    render(c.env, c.goal);
    syncAliases(c.env);
    syncGoal(c.goal);
    fillBar(c.env, c.goal);
    result.classList.remove('is-updating');
    void result.offsetWidth; // restart the row transition
    result.classList.add('is-updating');
    try { history.replaceState(null, '', '#setup=' + c.env + '/' + c.goal); } catch (err) { /* file:// or sandboxed */ }
  }

  var initial = { env: 'claude-code', goal: 'full' };
  var m = /#setup=([a-z0-9-]+)\/(full|ci|mcp)$/.exec(window.location.hash);
  if (m && byId[m[1]]) initial = { env: m[1], goal: m[2] };
  if (POPULAR.indexOf(initial.env) === -1) allBox.open = true;
  select(initial.env, initial.goal);
  render(initial.env, initial.goal);
  syncAliases(initial.env);
  syncGoal(initial.goal);
  fillBar(initial.env, initial.goal);

  app.addEventListener('change', function (e) {
    if (e.target.name === 'env' || e.target.name === 'env-all') clearOther(e.target.name);
    userChose = true; update(); showBar();
  });
  app.addEventListener('submit', function (e) { e.preventDefault(); });

  var fallback = document.querySelector('[data-chooser-fallback]');
  if (fallback) fallback.hidden = true;
  app.hidden = false;
})();
