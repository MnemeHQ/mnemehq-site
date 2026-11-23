/* Setup chooser for /setup/. Data: setup-chooser-data-v2.js (source of truth:
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
    '/setup/claude-code/': 'Claude Code + CI guide',
    '/setup/codex-cli/': 'Codex CLI + CI guide',
    '/setup/opencode/': 'OpenCode + CI guide',
    '/setup/ci/': 'CI-only guide',
    '/setup/mcp/': 'MCP lookup server guide',
    '/setup/software-factory/': 'software factory guide'
  };
  /* The first command each guide runs, copied from the guide's own first
   * install step. A result that links to an integration page shows none:
   * those pages carry their own install steps. */
  var FIRST = {
    '/setup/claude-code/': ['pipx install "mneme-hq==0.11.0"'],
    '/setup/codex-cli/': ['python -m venv ~/.mneme-venv', '~/.mneme-venv/bin/python -m pip install "mneme-hq==0.11.0"'],
    '/setup/opencode/': ['pipx install "mneme-hq==0.11.0"'],
    '/setup/ci/': ['pipx install "mneme-hq==0.11.0"'],
    '/setup/mcp/': ['pipx install "mneme-hq[mcp]==0.11.0"'],
    '/setup/software-factory/': ['pipx install "mneme-hq==0.11.0"']
  };
  /* Guides whose first step is the CI check, after activating a rule locally. */
  var LOCAL_FIRST = ['/setup/ci/', '/setup/opencode/', '/setup/software-factory/'];
  var GOALS = {
    full: 'Goal: agent hook + CI check',
    ci: 'Goal: CI check only',
    mcp: 'Goal: lookup only (MCP)'
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
  allSummary.textContent = 'Show all ' + DATA.options.length + ' tools: more agents, editors, orchestrators and factories';

  /* ---- Result ---- */
  function hooked(o) { return o.hook === 'shipped' || o.hook === 'validated' || o.hook === 'via'; }
  function hookPart(o, goal) {
    if (goal === 'ci') return { state: 'off', label: 'Not included', text: 'Nothing runs inside the agent. A bad edit is written, then caught by the CI check.' };
    if (goal === 'mcp') return { state: 'off', label: 'Not included', text: 'Nothing is blocked. Add a hook and the CI check when you want bad changes stopped.' };
    if (hooked(o)) return { state: 'required', label: 'Included', text: o.hook_text };
    if (o.hook === 'experimental') return { state: 'experimental', label: 'Experimental', text: o.hook_text };
    return { state: 'gap', label: 'None for this tool', text: o.hook_text };
  }
  function ciPart(o, goal) {
    if (goal === 'mcp') return { state: 'off', label: 'Not included', text: 'Pull requests are not checked.' };
    return { state: 'required', label: 'Included', text: 'Runs mneme check on each file a pull request adds or modifies, whoever wrote it. Make it a required check, or a failure is only a red mark.' };
  }
  function mcpPart(o, goal) {
    if (goal === 'ci') return { state: 'off', label: 'Not included', text: 'Add it later if agents should look decisions up before they write.' };
    if (goal === 'mcp') {
      return { state: 'required', label: 'Included', text: o.id === 'claude-code'
        ? 'The plugin’s /mneme:context already looks up the decisions for a task. The server adds lookup by file path, which decision replaced which, and proposals.'
        : 'Works in a tool that can start a local MCP server over stdio. Check that yours can; we have not tested every tool.' };
    }
    return { state: 'optional', label: 'Optional', text: o.mcp_note || 'Add it if your tool can start a local MCP server. It shows the agent the decisions and blocks nothing.' };
  }
  function headline(o, goal) {
    var who = o.id === 'other' ? 'your tool' : o.name;
    if (goal === 'mcp') {
      if (o.group === 'ci') return 'The MCP lookup server runs inside a coding agent, not in CI. Pick your agent instead, or choose the CI check.';
      return 'Lets ' + who + ' look up which decisions apply before it writes. Nothing is blocked.';
    }
    if (goal === 'ci' || o.group === 'ci') {
      var ci = o.group === 'ci' ? 'A required ' + o.name + ' check' : 'A required CI check';
      var by = o.group === 'ci' || o.id === 'other' ? 'whoever wrote it' : 'whether ' + o.name + ' or a person wrote it';
      return ci + ' fails any pull request that breaks an active rule, ' + by + '.';
    }
    if (hooked(o)) return 'The agent hook refuses a bad edit while the agent works. The required CI check fails a bad pull request that gets past it.';
    if (o.hook === 'experimental') return o.name + '’s hook is experimental. Rely on the required CI check to fail a bad pull request.';
    if (o.id === 'other') return 'Assume your tool has no Mneme hook. A required CI check fails a bad pull request instead.';
    return o.name + ' has no Mneme hook, so nothing stops a bad edit while you work. A required CI check fails the pull request instead.';
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
    if (GUIDES[href]) return (isPrimary ? 'Open the ' : 'Then follow the ') + GUIDES[href];
    if (href.indexOf('/insights/') === 0) return 'Read our ' + o.name + ' analysis';
    return (isPrimary ? 'Open the ' : 'Read the ') + o.name + ' integration page';
  }
  function intentFor(href) { return href.indexOf('/setup/') === 0 ? 'setup' : 'integration'; }
  function missing(o, goal) {
    if (goal === 'mcp') return 'The server can search and explain decisions and take proposals for people to review. It cannot block an edit, or accept, activate or enforce a decision.';
    if (goal === 'ci' || o.group === 'ci') return 'CI runs after the file is written, on the files a pull request adds or modifies. It blocks a merge only where the check is required.';
    return o.limit;
  }
  function startNote(goal) {
    if (goal === 'mcp') return 'Then register mneme decision-mcp with your agent. An imported decision is enough; it needs no active rule.';
    if (goal === 'ci') return 'Run it on your machine to import a decision and activate its rule, then commit the ADR and the memory file. The CI job installs its own copy. Nothing is blocked until a rule is active.';
    return 'The guide then imports one decision and activates its rule. Nothing is blocked until a rule is active.';
  }

  var result = app.querySelector('[data-result]');

  function render(envId, goal) {
    var o = byId[envId];
    if (!o) return;
    var b = badge(o.status);
    result.textContent = '';
    var head = el('div', { 'class': 'result-head' });
    var titleRow = el('div', { 'class': 'result-title-row' });
    titleRow.appendChild(el('h3', { 'class': 'result-title', id: 'result-title-anchor', tabindex: '-1' }, o.name));
    var st = el('span', { 'class': 'result-status' });
    st.appendChild(el('span', { 'class': 'result-status-label' }, 'Integration status'));
    st.appendChild(el('span', { 'class': 'status-badge status-badge--' + b.key }, b.text));
    titleRow.appendChild(st);
    head.appendChild(titleRow);
    head.appendChild(el('p', { 'class': 'result-goal' }, GOALS[goal]));
    head.appendChild(el('p', { 'class': 'result-headline' }, headline(o, goal)));
    result.appendChild(head);

    result.appendChild(el('p', { 'class': 'result-section-label' }, 'What you set up'));
    var stack = el('ol', { 'class': 'layer-stack', 'aria-label': 'What you set up' });
    [
      ['Agent hook', 'blocks an edit while the agent works', hookPart(o, goal)],
      ['CI check', 'fails a bad pull request', ciPart(o, goal)],
      ['MCP lookup server', 'shows decisions, blocks nothing', mcpPart(o, goal)]
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
    limit.appendChild(el('p', { 'class': 'result-limit-label' }, 'What it misses'));
    limit.appendChild(el('p', null, missing(o, goal)));
    result.appendChild(limit);

    var l = links(o, goal);
    var first = FIRST[l.primary];
    if (first) {
      var start = el('div', { 'class': 'result-start' });
      start.appendChild(el('p', { 'class': 'result-section-label' }, 'Start here'));
      start.appendChild(el('pre', { 'class': 'result-cmd' }, first.join('\n')));
      start.appendChild(el('p', { 'class': 'result-start-note' }, startNote(goal === 'mcp' ? 'mcp' : (LOCAL_FIRST.indexOf(l.primary) !== -1 ? 'ci' : 'full'))));
      result.appendChild(start);
    }

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
    track(c.env, c.goal);
  }

  /* One setup_choice per distinct user selection; cta-analytics.js sends it. */
  var lastTracked = '';
  function track(env, goal) {
    var key = env + '/' + goal;
    if (!userChose || key === lastTracked) return;
    lastTracked = key;
    var o = byId[env] || {};
    try {
      document.dispatchEvent(new CustomEvent('mneme:track', { detail: { event: 'setup_choice',
        params: { setup_goal: goal, setup_env: env, setup_env_status: o.status || 'unknown' } } }));
    } catch (err) { /* old browser without CustomEvent constructor */ }
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
