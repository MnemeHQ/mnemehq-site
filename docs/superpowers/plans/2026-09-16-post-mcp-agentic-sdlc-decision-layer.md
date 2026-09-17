# Post-MCP Agentic SDLC: Decision Layer Positioning — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Position Mneme's Decision Index against CodeRabbit's newly-launched "Agentic Change Management" (Triage) category by patching three site pages, shipping a reusable cross-integration MCP CTA, publishing one pillar insight article, and drafting (not publishing) one founder LinkedIn post — all without touching the homepage or claiming a CodeRabbit integration that does not exist.

**Architecture:** This is a static HTML site (no build step, no framework). Pages are plain HTML files under `site/`; "shared components" are either (a) classes in a shared stylesheet referenced by every page in a family, or (b) idempotent Python sweep scripts that insert a marker-gated HTML block across many pages (the existing pattern in `scripts/sweep_integration_cta.py`). There is no live database of claims — publication safety comes from `scripts/check_insights.py` (CI-enforced registration contract) plus a mandatory pre-merge adversarial audit that classifies every claim's maturity.

**Tech Stack:** Static HTML/CSS/JS, Python 3 (stdlib only) for site-maintenance scripts, GitHub Actions CI (`check-insights.yml`, others), cPanel/Cloudflare deploy via `scripts/deploy_site.py` (not run by this plan).

**Spec:** The source scope is a ChatGPT conversation ("Post-MCP Agentic SDLC Scope", Mneme Growth and GTM project, 2026-09-16), reproduced here as the authoritative requirements this plan implements. No separate spec file exists; this plan document carries the spec inline per task.

## Global Constraints

- **Branch naming:** this branch is `site/agentic-sdlc-decision-layer` (already created). Never use a `claude/` prefix (user's global CLAUDE.md).
- **Squash merge:** the eventual PR lands on `main` as one squash commit using the PR title (user's global CLAUDE.md). Do not worry about intermediate commit granularity beyond what's useful for review checkpoints in this plan.
- **Homepage is explicitly out of scope.** Do not edit `site/index.html`. The user reviewed and rejected a homepage change in the source conversation.
- **No claimed integration.** Every CodeRabbit reference must be phrased as an interoperability *pattern* or *example*, never as a shipped or planned Mneme–CodeRabbit integration. Do not add CodeRabbit to `/integrations/`, `/compare/`, or any supported-integrations grid.
- **Maturity discipline (mandatory pre-merge gate, see Task 7):** every sentence describing what Mneme does must be classifiable as SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL, and must not imply a higher maturity than the truth. Verified rule vocabulary is PASS/WARN/FAIL, never ALLOW/WARN/BLOCK.
- **House voice (PUBLISHING.md [ED]):** concrete and declarative; never the word "bottleneck"; no em dashes as connective tissue; domain is always `mnemehq.com`; target engineering leaders, not individual developers.
- **CSS class hygiene (PUBLISHING.md [OP/ED]):** every `class="..."` used inside `<body>` must resolve to a rule either in an inline `<style>` on the same page or in a shared stylesheet already linked from that page.
- **Insights registration contract (PUBLISHING.md, CI-enforced via `scripts/check_insights.py`):** sitemap entry, index card + `hasPart` entry, local `og.png`, visible breadcrumb + `BreadcrumbList` JSON-LD, `TechArticle`/`Article` JSON-LD, ≥1 incoming internal link. See Task 5.
- **Citation verification:** the one external citation used in this plan (CodeRabbit's Triage announcement) was fetched and verified on 2026-09-16 against `https://www.coderabbit.ai/blog/coderabbit-triage` (strip the `?utm_source=chatgpt.com` tracking param before citing). Do not introduce any other external citation without the same verification.

---

### Task 1: `/architecture/` — decision plane vs. change plane section

**Files:**
- Modify: `site/architecture/index.html` (inside the existing inline `<style>` block, and inside `<section class="stack-section" aria-labelledby="runtime-stack-heading">`'s sibling position)

**Interfaces:**
- Produces: a new page anchor `#decision-vs-change-plane` that Task 5 (the article) links to.
- Consumes: nothing from other tasks; this is a standalone page edit.

This is a static HTML edit with no unit-test harness. "Test" here means: HTML remains well-formed, every new class resolves to a rule on the same page, and the section renders correctly in a real browser — the same verification standard this repo's own validators (`scripts/seo_check.py` class-hygiene check) apply.

- [ ] **Step 1: Add scoped CSS for the new two-column plane comparison**

Open `site/architecture/index.html` and find its inline `<style>` block (it already defines `.layer-stack`, `.layer-row`, `.layer-num`, `.layer-content` around line 132). Add these new rules immediately after the last `.layer-row.highlighted .layer-content strong { color: var(--accent); }` rule:

```css
    .plane-grid { display:grid; grid-template-columns:1fr 1fr; gap:1px; margin:1.5rem 0 1.25rem; border-radius:10px; overflow:hidden; background:var(--border2); }
    .plane-card { background:var(--surface); padding:1.1rem 1.25rem; }
    .plane-card.decision { border-top:2px solid var(--accent); }
    .plane-card.change { border-top:2px solid var(--border2); }
    .plane-card h3 { font-family:'DM Mono',monospace; font-size:0.7rem; letter-spacing:0.08em; text-transform:uppercase; color:var(--muted); margin:0 0 0.6rem; }
    .plane-card.decision h3 { color:var(--accent); }
    .plane-card ul { margin:0; padding-left:1.1rem; font-size:0.82rem; color:var(--text); line-height:1.75; }
    @media (max-width:640px){ .plane-grid{ grid-template-columns:1fr; } }
```

- [ ] **Step 2: Verify the CSS was inserted and the style block is still valid**

Run:

```bash
python -c "
import re
t = open('site/architecture/index.html', encoding='utf-8').read()
assert '.plane-grid' in t, 'CSS missing'
style = re.search(r'<style>(.*?)</style>', t, re.DOTALL).group(1)
assert style.count('{') == style.count('}'), 'unbalanced braces in <style>'
print('OK: CSS present and balanced')
"
```

Expected: `OK: CSS present and balanced`

- [ ] **Step 3: Insert the new section markup**

Find this exact block (the end of the `stack-section`, right before the `<figure class="doc-figure">`):

```html
    <p class="stack-xrefs">Harnesses coordinate execution; governance defines constraints; verification enforces invariants. None of those layers can do the others' jobs. The argument in full: <a href="/insights/harness-engineering-still-needs-governance/">Harness Engineering Still Needs Governance</a>. The concept page that anchors this stack: <a href="/concepts/governance-infrastructure/">Governance Infrastructure</a>.</p>
  </section>

<figure class="doc-figure">
```

Replace it with (the original paragraph and `</section>` stay byte-for-byte identical; only the new `<section>` block is inserted between them and the `<figure>`):

```html
    <p class="stack-xrefs">Harnesses coordinate execution; governance defines constraints; verification enforces invariants. None of those layers can do the others' jobs. The argument in full: <a href="/insights/harness-engineering-still-needs-governance/">Harness Engineering Still Needs Governance</a>. The concept page that anchors this stack: <a href="/concepts/governance-infrastructure/">Governance Infrastructure</a>.</p>
  </section>

  <section class="stack-section" id="decision-vs-change-plane" aria-labelledby="plane-heading">
    <div class="section-label" id="plane-heading">Decision governance and change governance are different layers</div>
    <p class="stack-lede">Layer 4 above answers what has been decided and whether it applies. A separate class of tooling &mdash; code review, PR prioritization, change-management systems &mdash; answers what changed and whether it is safe to ship. Both are necessary. Neither can do the other's job.</p>
    <div class="plane-grid">
      <div class="plane-card decision">
        <h3>Decision plane &middot; Mneme</h3>
        <ul>
          <li>What architecture has been decided?</li>
          <li>Which decision applies here?</li>
          <li>Is it authoritative?</li>
          <li>What constraint follows?</li>
          <li>Can this action proceed?</li>
        </ul>
      </div>
      <div class="plane-card change">
        <h3>Change plane &middot; review &amp; change management</h3>
        <ul>
          <li>What changed?</li>
          <li>Is the implementation correct?</li>
          <li>What risk does it introduce?</li>
          <li>Which PR deserves attention?</li>
          <li>Is it ready to merge?</li>
        </ul>
      </div>
    </div>
    <p class="stack-xrefs">The two planes compose over MCP rather than merge: a change-management system can ask Mneme's Decision Index which decisions govern a proposed change, while keeping full ownership of review, risk scoring, and merge readiness. See <a href="/integrations/mcp/">the MCP integration overview</a> for how that boundary works.</p>
  </section>

<figure class="doc-figure">
```

- [ ] **Step 4: Verify the section and anchor exist, and the file is still well-formed**

```bash
python -c "
import re
t = open('site/architecture/index.html', encoding='utf-8').read()
assert 'id=\"decision-vs-change-plane\"' in t
assert 'Decision governance and change governance are different layers' in t
assert t.count('<section') == t.count('</section>')
print('OK: section present, tags balanced')
"
```

Expected: `OK: section present, tags balanced`

- [ ] **Step 5: Visual check**

Open the file in the built-in browser preview (or any local static server) and confirm: the two-column card grid renders side by side on desktop and stacks on narrow widths, the accent color highlights the "Decision plane" card only, and no layout overlaps the existing pipeline diagram below it.

- [ ] **Step 6: Commit**

```bash
git add site/architecture/index.html
git commit -m "site(architecture): add decision plane vs change plane section"
```

---

### Task 2: `/integrations/mcp/` — "Decision layer for the wider agentic SDLC" + reverse native-integrations section

**Files:**
- Modify: `site/integrations/mcp/index.html`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: nothing consumed elsewhere (Task 4's reciprocal "Native integrations" pointer is separate markup on the same page, not a shared interface).

- [ ] **Step 1: Insert the new section after the existing "Where MCP fits" section**

Find this exact block near the end of `article-body`:

```html
      <h2>Where MCP fits</h2>
      <p>MCP is an interoperability boundary for Mneme's decision layer. It lets heterogeneous systems exchange decision context without redefining governance in each system. The deterministic enforcement layer still operates at execution boundaries such as agent hooks and CI, where actual changes can be evaluated against applicable rules.</p>
      <p>See <a href="/docs/decision-proposals/">Decision proposals</a> for the full human review workflow and <a href="/docs/how-enforcement-works/">How enforcement works</a> for the prevent, catch, and verify layers that MCP complements.</p>
      <p>Related implementation paths include <a href="/integrations/adr-import/">ADR import</a> for compiling an existing decision corpus and the <a href="/integrations/claude-agent-sdk/">Claude Agent SDK integration</a> for enforcement around agent execution. The released implementation is available in the <a href="https://github.com/MnemeHQ/mneme" target="_blank" rel="noopener">Mneme source repository</a>.</p>
    </div>
```

Replace it with (adds two new `<h2>` sections before the closing `</div>`):

```html
      <h2>Where MCP fits</h2>
      <p>MCP is an interoperability boundary for Mneme's decision layer. It lets heterogeneous systems exchange decision context without redefining governance in each system. The deterministic enforcement layer still operates at execution boundaries such as agent hooks and CI, where actual changes can be evaluated against applicable rules.</p>
      <p>See <a href="/docs/decision-proposals/">Decision proposals</a> for the full human review workflow and <a href="/docs/how-enforcement-works/">How enforcement works</a> for the prevent, catch, and verify layers that MCP complements.</p>
      <p>Related implementation paths include <a href="/integrations/adr-import/">ADR import</a> for compiling an existing decision corpus and the <a href="/integrations/claude-agent-sdk/">Claude Agent SDK integration</a> for enforcement around agent execution. The released implementation is available in the <a href="https://github.com/MnemeHQ/mneme" target="_blank" rel="noopener">Mneme source repository</a>.</p>

      <h2>Decision layer for the wider agentic SDLC</h2>
      <p>Mneme is not a substitute for code review, CI, issue tracking, or change-management tooling. Those systems decide what changed, whether the implementation is correct, what risk it introduces, and which change deserves attention next. Mneme answers a different, earlier question: what has the organization already decided about the architecture this change has to obey?</p>
      <pre tabindex="0"><code>Decision Index
        |
        v
       MCP
        |
        v
agent / review system / change-management system
        |
        v
      change</code></pre>
      <p>A downstream system does not need Mneme's internals to use this. It calls the Decision Index through MCP, retrieves the architectural decisions applicable to a proposed action, and keeps its own responsibility for code quality, risk, prioritization, and workflow.</p>
      <p><strong>Example, not a shipped integration:</strong> CodeRabbit's Triage feature, launched September 15, 2026, assigns every pull request a deterministic priority from P0 to P3 as the "prioritization layer" of what CodeRabbit calls Agentic Change Management &mdash; its system for governing change from both humans and agents (<a href="https://www.coderabbit.ai/blog/coderabbit-triage" target="_blank" rel="noopener">CodeRabbit, September 2026</a>). A change-management system built this way could query Mneme's Decision Index over MCP to retrieve the architectural decisions governing a change, while continuing to own its own review, impact analysis, and prioritization. Mneme has no CodeRabbit integration today; this illustrates the interoperability pattern MCP was built for, not a supported connector.</p>
      <p>Review systems govern changes. Mneme governs the decisions those changes have to obey.</p>

      <h2>Native integrations</h2>
      <p>MCP is one access path to the Decision Index. Several coding agents and IDEs integrate natively instead: <a href="/integrations/claude-code/">Claude Code</a>, <a href="/integrations/codex-cli/">Codex CLI</a>, <a href="/integrations/kiro/">Kiro</a>, and <a href="/integrations/hermes/">Hermes</a>. Native integrations and MCP expose the same decision layer through different transports; pick whichever your tooling already supports.</p>
    </div>
```

- [ ] **Step 2: Verify insertion and link targets exist**

```bash
python -c "
import os
t = open('site/integrations/mcp/index.html', encoding='utf-8').read()
assert 'Decision layer for the wider agentic SDLC' in t
assert 'coderabbit.ai/blog/coderabbit-triage' in t and 'utm_source' not in t
assert 'Mneme has no CodeRabbit integration today' in t
assert t.count('<pre') == t.count('</pre>')
for path in ['claude-code', 'codex-cli', 'kiro', 'hermes']:
    assert os.path.isdir(f'site/integrations/{path}'), f'missing integrations/{path}'
print('OK')
"
```

Expected: `OK`

- [ ] **Step 3: Visual check**

Render the page and confirm the ASCII flow diagram matches the existing `<pre><code>` style already used earlier on the same page (the proposal-lifecycle diagram), and that all four native-integration links resolve (no 404s) when clicked in the browser preview.

- [ ] **Step 4: Commit**

```bash
git add site/integrations/mcp/index.html
git commit -m "site(integrations): position MCP as the agentic SDLC decision layer"
```

---

### Task 3: `/docs/mcp/` — vendor-neutral "Downstream governance consumers" section

**Files:**
- Modify: `site/docs/mcp/index.html`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: nothing consumed elsewhere. This section must stay vendor-neutral — no CodeRabbit mention here (that lives only in Task 2's `/integrations/mcp/` page, which is explicitly allowed to name an example).

- [ ] **Step 1: Insert a new section between "MCP is not the authority surface" and "Known limitations in 0.9.0"**

Find:

```html
      <p>Acceptance materializes a canonical decision into project memory. It still does not install deterministic protection or run the Architecture Audit. Retrieval, authority, Audit, and enforcement remain distinct.</p>
    </section>

    <section class="section" id="limitations">
```

Replace with:

```html
      <p>Acceptance materializes a canonical decision into project memory. It still does not install deterministic protection or run the Architecture Audit. Retrieval, authority, Audit, and enforcement remain distinct.</p>
    </section>

    <section class="section" id="downstream-consumers">
      <h2>Downstream governance consumers</h2>
      <p>A downstream system does not need to adopt Mneme's data model, storage, or workflow to use the Decision Index. It calls <code>decision.applicable_to</code> for a proposed change, receives the governing decisions with provenance, and folds that into whatever review, risk-scoring, or triage logic it already runs. Mneme does not see, and does not need to see, the consumer's priority score, risk model, or merge queue.</p>
      <pre tabindex="0"><code>Change proposed (PR, agent patch, generated diff)
        |
        v
Consumer calls decision.applicable_to(...)
        |
        v
Mneme returns applicable decisions + provenance
        |
        v
Consumer performs its own review, risk scoring,
prioritization, or workflow routing</code></pre>
      <p>This is the boundary the MCP server is built for: a stable protocol surface for exchanging decision context, not a shared implementation. See <a href="/integrations/mcp/">the integration overview</a> for how this composes with review and change-management tooling in practice.</p>
    </section>

    <section class="section" id="limitations">
```

- [ ] **Step 2: Verify insertion, vendor-neutrality, and JSON structure untouched**

```bash
python -c "
t = open('site/docs/mcp/index.html', encoding='utf-8').read()
assert 'id=\"downstream-consumers\"' in t
assert 'Downstream governance consumers' in t
assert 'CodeRabbit' not in t, 'docs/mcp must stay vendor-neutral'
assert t.count('<section') == t.count('</section>')
print('OK: vendor-neutral section present')
"
```

Expected: `OK: vendor-neutral section present`

- [ ] **Step 3: Visual check**

Render the page; confirm the new section sits between "MCP is not the authority surface" and "Known limitations in 0.9.0", and the ASCII diagram is legible at mobile width (this repo requires mobile-readable diagrams per PUBLISHING.md's diagram rule).

- [ ] **Step 4: Commit**

```bash
git add site/docs/mcp/index.html
git commit -m "docs(mcp): add vendor-neutral downstream governance consumer flow"
```

---

### Task 4: Shared "Use Mneme through MCP" CTA across all integration pages

**Files:**
- Modify: `site/assets/css/integration-system-v2.css` (add the `.mcp-cross-cta` component once, shared by all pages that link it)
- Create: `scripts/sweep_mcp_cta.py`
- Modify (via running the script): all 19 `site/integrations/<tool>/index.html` files except `site/integrations/mcp/index.html`

**Interfaces:**
- Consumes: nothing from Tasks 1–3.
- Produces: the `.mcp-cross-cta` CSS class, reused verbatim by the script inserted into every integration page. This is the "shared component" the source scope explicitly asked for (a single place to change future MCP messaging).

- [ ] **Step 1: Add the shared CSS component**

Append to the end of `site/assets/css/integration-system-v2.css`:

```css

/* MCP cross-integration CTA: quiet secondary box below the primary end CTA on every integration page. */
.mcp-cross-cta {
  box-sizing: border-box;
  width: 100%;
  max-width: var(--integration-reading);
  margin: 1.25rem auto 0;
  padding: 1.25rem 1.5rem;
  border: 1px dashed var(--border2);
  border-radius: 12px;
  background: transparent;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
}
.mcp-cross-cta__text { max-width: 620px; }
.mcp-cross-cta__eyebrow { display: block; font-family: 'DM Mono', monospace; font-size: 0.68rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.35rem; }
.mcp-cross-cta__text p { margin: 0; font-size: 0.84rem; color: var(--muted); line-height: 1.65; }
.mcp-cross-cta__link { flex-shrink: 0; font-family: 'DM Mono', monospace; font-size: 0.78rem; color: var(--accent); text-decoration: none; white-space: nowrap; }
.mcp-cross-cta__link:hover, .mcp-cross-cta__link:focus-visible { text-decoration: underline; }
@media (max-width: 640px) { .mcp-cross-cta { flex-direction: column; align-items: flex-start; } }
```

- [ ] **Step 2: Verify the CSS file is still syntactically balanced**

```bash
python -c "
t = open('site/assets/css/integration-system-v2.css', encoding='utf-8').read()
assert '.mcp-cross-cta' in t
assert t.count('{') == t.count('}')
print('OK')
"
```

Expected: `OK`

- [ ] **Step 3: Write the idempotent sweep script**

Create `scripts/sweep_mcp_cta.py`:

```python
"""Insert the shared 'Use Mneme through MCP' cross-integration CTA into
every integration detail page except the MCP page itself.

Idempotent via the 'mcp-cross-cta' marker: re-running after a partial
apply only touches files that don't already have it. Mirrors the pattern
in scripts/sweep_integration_cta.py (regex-locate the existing
integration-end-cta block, insert immediately after it).
"""
import re
from pathlib import Path

SITE = Path(__file__).parent.parent / "site" / "integrations"

# Native integrations get "Prefer MCP?" wording; everyone else gets the
# generic "Use Mneme through MCP" wording.
NATIVE = {"claude-code", "codex-cli", "kiro", "hermes"}

GENERIC_CARD = (
    '\n<div class="mcp-cross-cta">\n'
    '  <div class="mcp-cross-cta__text">\n'
    '    <span class="mcp-cross-cta__eyebrow">Use Mneme through MCP</span>\n'
    "    <p>Connect Mneme's Decision Index to MCP-compatible agents and tools. "
    "Query applicable architectural decisions, retrieve provenance, and expose "
    "decision context without coupling the consumer to Mneme internals.</p>\n"
    "  </div>\n"
    '  <a href="/integrations/mcp/" class="mcp-cross-cta__link" data-cta-intent="mcp" '
    'data-cta-position="end" data-cta-component="mcp_cross_cta">Explore MCP &rarr;</a>\n'
    "</div>"
)

NATIVE_CARD = (
    '\n<div class="mcp-cross-cta">\n'
    '  <div class="mcp-cross-cta__text">\n'
    '    <span class="mcp-cross-cta__eyebrow">Prefer MCP?</span>\n'
    "    <p>Mneme also exposes its Decision Index through a standard MCP server "
    "for interoperable access from compatible tools.</p>\n"
    "  </div>\n"
    '  <a href="/integrations/mcp/" class="mcp-cross-cta__link" data-cta-intent="mcp" '
    'data-cta-position="end" data-cta-component="mcp_cross_cta">Explore MCP &rarr;</a>\n'
    "</div>"
)

# Matches either the "cta-block integration-end-cta" or "cta-band
# integration-end-cta" wrapper, capturing through its two closing </div>s.
END_CTA_BLOCK = re.compile(
    r'(<div class="(?:cta-block|cta-band) integration-end-cta">.*?</div>\s*</div>)',
    re.DOTALL,
)

changed = []
skipped = []
for d in sorted(SITE.iterdir()):
    if not d.is_dir() or d.name == "mcp":
        continue
    f = d / "index.html"
    if not f.exists():
        continue
    text = f.read_text(encoding="utf-8")
    if "mcp-cross-cta" in text:
        skipped.append(d.name)
        continue
    card = NATIVE_CARD if d.name in NATIVE else GENERIC_CARD
    new_text, n = END_CTA_BLOCK.subn(lambda m: m.group(1) + card, text, count=1)
    if n == 0:
        print(f"WARNING: no integration-end-cta block found in {d.name}, skipping")
        continue
    f.write_bytes(new_text.encode("utf-8"))
    changed.append(d.name)

for c in changed:
    print(f"updated: {c}")
for s in skipped:
    print(f"already present, skipped: {s}")
print(f"\n{len(changed)} pages updated, {len(skipped)} already had the card")
```

- [ ] **Step 4: Run it and verify against every integration dir**

```bash
python scripts/sweep_mcp_cta.py
```

Expected: one `updated: <slug>` line per integration directory except `mcp` (19 lines total), then a summary line `19 pages updated, 0 already had the card`. If any `WARNING: no integration-end-cta block found` lines print, stop and inspect that page's footer structure by hand before proceeding — do not force the insertion.

- [ ] **Step 5: Verify wording variants landed correctly**

```bash
python -c "
from pathlib import Path
native = {'claude-code', 'codex-cli', 'kiro', 'hermes'}
site = Path('site/integrations')
for d in sorted(site.iterdir()):
    if not d.is_dir() or d.name == 'mcp':
        continue
    t = (d / 'index.html').read_text(encoding='utf-8')
    assert 'mcp-cross-cta' in t, f'{d.name}: card missing'
    if d.name in native:
        assert 'Prefer MCP?' in t, f'{d.name}: expected native wording'
    else:
        assert 'Use Mneme through MCP' in t, f'{d.name}: expected generic wording'
print('OK: all 19 pages carry the correct card variant')
"
```

Expected: `OK: all 19 pages carry the correct card variant`

- [ ] **Step 6: Run the repo's existing nav/footer and class-hygiene checks**

```bash
python scripts/check_nav_footer.py
python scripts/seo_check.py 2>&1 | grep -i "mcp-cross-cta" || echo "no class-hygiene warnings for mcp-cross-cta"
```

Expected: `check_nav_footer.py` exits 0 (unrelated to this change, but confirms the sweep didn't corrupt nav/footer markup); no `mcp-cross-cta`-related warnings from `seo_check.py`.

- [ ] **Step 7: Visual spot-check**

Open 2 pages of each footer style in the browser preview — one `article-footer` style (e.g. `claude-code`) and one `cta-band` style (e.g. `codex-cli`) — and confirm the new card renders below the primary end CTA, is visually quieter (dashed border, no filled background), and the "Explore MCP →" link navigates to `/integrations/mcp/`.

- [ ] **Step 8: Commit**

```bash
git add site/assets/css/integration-system-v2.css scripts/sweep_mcp_cta.py site/integrations/
git commit -m "site(integrations): add shared 'use Mneme through MCP' cross-integration CTA"
```

---

### Task 5: Publish the pillar article — "Agentic Change Management Needs a Decision Layer"

**Files:**
- Create: `scratch/agentic-change-management-body.html` (working file, gitignored, not deployed — deleted or left in `scratch/` after use)
- Create (via `scripts/new_article.py`): `site/insights/agentic-change-management-needs-a-decision-layer/index.html`
- Modify: `scripts/ensure_og_coverage.py` (`TEMPLATES` + `NEW_MAP_ENTRIES`)
- Create (via `scripts/generate_og_images.py`): `site/insights/agentic-change-management-needs-a-decision-layer/og.png`
- Modify: `site/sitemap.xml`
- Modify: `site/insights/all/index.html` (archive card + `CollectionPage.hasPart` entry)
- Modify: `site/insights/topics/architectural-governance/index.html` (topic-hub card)
- Modify (via `scripts/sync_insights_catalog.py`): `site/insights/index.html` (homepage latest-6 sync, if this article displaces an older one)

**Interfaces:**
- Consumes: the verified CodeRabbit citation and the `/architecture/#decision-vs-change-plane` anchor from Task 1, and `/integrations/mcp/` / `/docs/mcp/` from Tasks 2–3 (all three must be merged into this branch before this task, since the article links to all of them).
- Produces: the article URL `https://mnemehq.com/insights/agentic-change-management-needs-a-decision-layer/`, referenced by Task 6's LinkedIn draft.

- [ ] **Step 1: Write the body fragment**

Create `scratch/agentic-change-management-body.html` (this is the `--body-file` argument to `new_article.py`: everything between `</header>` and the end of the article body) with exactly this content:

```html
<h2>The PR queue is becoming a decision system</h2>
<p>CodeRabbit calls Triage the "prioritization layer" of what it calls Agentic Change Management: its system for governing software change from both people and agents (<a href="https://www.coderabbit.ai/blog/coderabbit-triage" target="_blank" rel="noopener">CodeRabbit, September 2026</a>). Triage replaces FIFO ordering with a deterministic P0-to-P3 score per pull request, and it shows the evidence behind each score. That is not marketing language stretched onto a review feature. It is a genuine move from probabilistic AI review toward deterministic, evidence-backed governance output, and it is the clearest signal yet that agentic development is pushing governance into the delivery pipeline itself.</p>

<h2>A PR is not an architectural decision</h2>
<p>Triage's own framing is honest about its object: it governs the change, not the architecture the change has to fit inside. CodeRabbit says explicitly that architectural judgment, including whether an abstraction makes sense for the application, remains human. That is the right boundary, and it is also the gap. A pull request is a transient artifact: opened, scored, merged, closed. An architectural decision is not. It survives the PR that prompted it, the next thousand PRs, a framework migration, a team rewrite, and every agent that touches the codebase afterward. A system that scores PRs needs a durable, separate answer to what decisions apply to this PR before it can meaningfully judge whether the PR is safe to advance.</p>

<h2>Change evidence and decision authority are different things</h2>
<p>Triage can explain why a PR is P0 instead of P3: it shows the evidence behind the score. That is change evidence. It is a different kind of evidence from decision authority: why an architectural decision governs this action, who approved it, what constraint follows from it, and whether it is still in force. Change evidence answers whether a change is good. Decision authority answers what the change is bound by. Conflating the two produces tools that can explain their own risk model but cannot say whether the code violates an architecture the organization already agreed on.</p>

<h2>The agentic SDLC now has two control planes</h2>
<p>Put together, the emerging stack for governed agentic delivery has two distinct planes, not one:</p>
<pre tabindex="0"><code>Human architectural judgment
        |
        v
   Decision Index
        |
        v
 Decision applicability
        |
        v
  Decision enforcement
        |
        v
     Code change
        |
        v
Review / risk / prioritization
        |
        v
       Merge</code></pre>
<p>The decision plane sits before the change exists: what has been decided, what applies, what is enforced before generation. The change plane sits after: what changed, is it correct, what risk it carries, whether it is ready to merge. Neither plane can do the other's job. A prioritization engine that tries to encode architectural authority ends up re-deriving governance ad hoc, per repository, per rule. A decision layer that tries to score PR risk ends up duplicating review tooling it has no advantage building. See the full breakdown in <a href="/architecture/#decision-vs-change-plane">Mneme's architecture overview</a>.</p>

<h2>MCP is the interoperability boundary between them</h2>
<p>Until recently, connecting the two planes meant one of two bad options: a change-management system re-implements architectural governance itself, or a governance system builds bespoke adapters into every review and CI product it wants to reach. Mneme's Decision MCP server, shipped in 0.9.0, is built for the second boundary: a stable, six-tool protocol surface a reviewer, agent, IDE, or change-management system can call to retrieve the architectural decisions applicable to a proposed action, with provenance attached, without adopting Mneme's storage model or internals.</p>
<p>To be precise about maturity: Mneme has no CodeRabbit integration today, and this is not a roadmap announcement. It is the shape of what MCP enables. A change-management system built the way CodeRabbit describes Triage could call <code>decision.applicable_to</code> to retrieve the decisions governing a change, while continuing to own its own review, impact analysis, and prioritization entirely. See <a href="/integrations/mcp/">how that boundary works today</a> and the <a href="/docs/mcp/">full six-tool reference</a>.</p>

<h2>Where to start</h2>
<p>Before a system can decide which change deserves attention, the organization needs a durable, enforceable answer to what it has already decided about the architecture. Most codebases do not have one: the decisions exist in someone's memory, an old ADR, or a chat thread, not in a form any system, human or agent, can query. The decision-plane-versus-change-plane distinction only pays off once decisions are actually represented in enforceable form. The <a href="/audit/">Architecture Audit</a> is the place to find out how much of your architecture already is, using the same <a href="/insights/four-architecture-protection-states/">four protection states</a> that turn "we decided this once" into a queue you can act on.</p>
```

- [ ] **Step 2: Verify the body word count and internal links before scaffolding**

```bash
python -c "
import re
t = open('scratch/agentic-change-management-body.html', encoding='utf-8').read()
words = len(re.sub(r'<[^>]+>', ' ', t).split())
print(f'{words} words')
assert words >= 500, 'too short for a pillar analysis piece'
for path in ['/architecture/#decision-vs-change-plane', '/integrations/mcp/', '/docs/mcp/', '/audit/', '/insights/four-architecture-protection-states/']:
    assert path in t, f'missing link to {path}'
assert 'coderabbit.ai/blog/coderabbit-triage' in t and 'utm_source' not in t
assert 'bottleneck' not in t.lower()
print('OK')
"
```

Expected: word count printed (should be roughly 650-800), then `OK`.

- [ ] **Step 3: Scaffold the article**

```bash
python scripts/new_article.py \
  --slug agentic-change-management-needs-a-decision-layer \
  --title "Agentic Change Management Needs a Decision Layer" \
  --description "CodeRabbit's Triage scores every pull request P0 to P3. That solves prioritization. It doesn't answer which architectural decisions a change must obey." \
  --date 2026-09-16 \
  --lede "CodeRabbit's Triage, launched September 15, 2026, gives every pull request a deterministic priority from P0 to P3, backed by inspectable evidence. That is a real step toward governed agentic delivery. It also exposes the question no review tool can answer on its own: what is this change supposed to obey in the first place?" \
  --body-file scratch/agentic-change-management-body.html \
  --section Analysis \
  --eyebrow Analysis \
  --about-terms "decision index,architectural governance,agentic change management"
```

Expected output: `wrote site/insights/agentic-change-management-needs-a-decision-layer/index.html (~NNNN bytes, ~NNN words)` followed by the registration checklist. If it fails with `FATAL: --description must be...`-style length concerns, verify length first:

```bash
python -c "print(len(\"CodeRabbit's Triage scores every pull request P0 to P3. That solves prioritization. It doesn't answer which architectural decisions a change must obey.\"))"
```

Expected: a number between 150 and 160 (verified at plan-writing time to be ~151).

- [ ] **Step 4: Register the OG image template**

Open `scripts/ensure_og_coverage.py`. In the `TEMPLATES` list, add (matching the existing tuple shape `(filename, tag, heading, font_size, subtitle, url_path)`):

```python
    (
        "og-insights-agentic-change-management.html",
        "Insights",
        "Two Control Planes, Not One",
        "42px",
        "CodeRabbit scores the PR. Mneme governs the decision it has to obey.",
        "insights/agentic-change-management-needs-a-decision-layer",
    ),
```

In the `NEW_MAP_ENTRIES` dict, add:

```python
    "og-insights-agentic-change-management.html": "insights/agentic-change-management-needs-a-decision-layer/og.png",
```

- [ ] **Step 5: Generate the OG image**

```bash
python scripts/ensure_og_coverage.py
python scripts/generate_og_images.py
```

(Requires `pip install playwright && playwright install chromium` if not already installed in this environment.) Expected: `site/insights/agentic-change-management-needs-a-decision-layer/og.png` exists at 1200x630px.

```bash
python -c "
from PIL import Image
im = Image.open('site/insights/agentic-change-management-needs-a-decision-layer/og.png')
assert im.size == (1200, 630), im.size
print('OK: OG image is 1200x630')
"
```

- [ ] **Step 6: Add the sitemap entry**

Append to `site/sitemap.xml`, in a location near the other recent insights entries:

```xml
<url>
  <loc>https://mnemehq.com/insights/agentic-change-management-needs-a-decision-layer/</loc>
  <changefreq>monthly</changefreq>
  <priority>0.8</priority>
</url>
```

- [ ] **Step 7: Add the archive card and `hasPart` entry**

In `site/insights/all/index.html`, add a card to the most thematically relevant `cards-section` (governance/agentic-SDLC cluster), mirroring a neighboring card's structure exactly (eyebrow tag, read time, `<h3>`, summary `<p>`, `read-pill` footer):

```html
<a href="/insights/agentic-change-management-needs-a-decision-layer/" class="insight-card-link">
  <div class="insight-card">
    <span class="insight-card-eyebrow">Analysis</span>
    <h3>Agentic Change Management Needs a Decision Layer</h3>
    <p>CodeRabbit's Triage turns the PR queue into a scored decision system. A PR still isn't an architectural decision — here's the layer underneath it.</p>
    <span class="read-pill">Analysis &middot; read</span>
  </div>
</a>
```

(Match the exact surrounding card markup in the file rather than this simplified sketch — copy a real neighboring `<a class="insight-card-link">` block and substitute only the href, eyebrow, h3, and summary text, so classes stay identical to what CSS expects.)

Add the matching entry to the archive's `CollectionPage.hasPart` JSON-LD array:

```json
{"@type": "Article", "name": "Agentic Change Management Needs a Decision Layer", "url": "https://mnemehq.com/insights/agentic-change-management-needs-a-decision-layer/"}
```

- [ ] **Step 8: Add the topic-hub card**

Add the same card (copy the exact archive card markup from Step 7) to `site/insights/topics/architectural-governance/index.html`'s curated supporting set.

- [ ] **Step 9: Sync derived catalogue state**

```bash
python scripts/sync_insights_catalog.py
python scripts/sync_insights_catalog.py --check
```

Expected: the first command exits 0 and may rewrite `data-published`/`<time>` values and the homepage's synced latest-6 cards; the second (`--check`) then exits 0 with no diffs.

- [ ] **Step 10: Run the full publishing gate**

```bash
python scripts/check_insights.py
```

Expected: exit code 0, no missing-registration errors for `agentic-change-management-needs-a-decision-layer`.

- [ ] **Step 11: Clean up the scratch file and verify it was never under `site/`**

```bash
git status --porcelain site/ | grep -q "scratch/agentic-change-management-body.html" && echo "FAIL: scratch file leaked into site/" || echo "OK: scratch file stayed out of site/"
```

Expected: `OK: scratch file stayed out of site/`. The scratch file itself does not need to be committed; leave it in `scratch/` (gitignored) or delete it.

- [ ] **Step 12: Commit**

```bash
git add site/insights/agentic-change-management-needs-a-decision-layer/ \
        site/sitemap.xml \
        site/insights/all/index.html \
        site/insights/topics/architectural-governance/index.html \
        site/insights/index.html \
        scripts/ensure_og_coverage.py
git commit -m "site(insights): Agentic Change Management Needs a Decision Layer"
```

---

### Task 6: Draft (do not publish) the founder LinkedIn post

**Files:** none in the repository — this uses the `mneme-linkedin` MCP tool to create a draft only.

**Interfaces:**
- Consumes: the published article URL from Task 5.

Publishing to LinkedIn is "posting on the user's behalf" — per this environment's action-permission rules that requires explicit user confirmation before it happens, every time, regardless of any earlier approval. This task stops at the draft stage.

- [ ] **Step 1: Draft the post**

Call the `mneme-linkedin` draft tool with this exact copy:

```
CodeRabbit's new Triage launch is a good signal for the agentic SDLC: the PR queue is becoming a governed decision system, scored P0 to P3 with evidence attached.

But that also exposes a layer underneath it. A system can only decide which change deserves attention once the organization has a durable way to represent the decisions that change is expected to obey.

Change Index: what is happening to the code.
Decision Index: what the organization has already decided about the code.

That distinction is why we shipped Decision MCP: a way for review, change-management, and agent tooling to query the decisions governing a change, without needing to become a governance system themselves.

Mneme doesn't compete with the CodeRabbit class of tools. It's the layer underneath them.

https://mnemehq.com/insights/agentic-change-management-needs-a-decision-layer/
```

- [ ] **Step 2: Stop and present the draft to the user**

Do not call the publish/approve tool. Report the draft content and its link back to the user and wait for explicit approval before any publish action.

---

### Task 7: Adversarial maturity audit (mandatory pre-merge gate)

**Files:** all files touched in Tasks 1–6.

Per this project's standing publication rule, every content PR gets an adversarial audit before merge, not after, and the audit prompt must explicitly include the maturity-classification test. This is not optional and is not satisfied by the CI validators run in earlier tasks — CI checks registration and structure, never whether a claim is true or correctly scoped.

- [ ] **Step 1: Dispatch the audit**

Run a fresh, high-effort review pass (a subagent or a `/code-review` style pass, whichever this session's tooling provides) with this exact instruction:

> Review every sentence added or changed in this branch that describes what Mneme does, is, or will do — across `site/architecture/index.html`, `site/integrations/mcp/index.html`, `site/docs/mcp/index.html`, every `site/integrations/*/index.html` touched by `scripts/sweep_mcp_cta.py`, and `site/insights/agentic-change-management-needs-a-decision-layer/index.html`. For every such sentence, classify it as SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL. Flag any sentence whose language implies a higher maturity level than the truth — in particular, flag anything that could be read as claiming a real CodeRabbit integration exists or is planned; the only correct framing is "interoperability pattern" / "could" / "would," never "integrates with" or "connects to." Also flag any verdict-vocabulary drift (must be PASS/WARN/FAIL, never ALLOW/WARN/BLOCK) and any claim of whole-system architectural conformance verification (not shipped — Mneme enforces encoded constraints; verification belongs to tests/audit/review).

- [ ] **Step 2: Apply every finding**

Fix each flagged sentence in place. Do not defer findings to a follow-up PR.

- [ ] **Step 3: Re-run all validators touched by this branch**

```bash
python scripts/check_insights.py
python scripts/sync_insights_catalog.py --check
python scripts/check_nav_footer.py
```

Expected: all three exit 0.

- [ ] **Step 4: Commit any audit fixes**

```bash
git add -A
git commit -m "site: apply maturity-audit fixes"
```

(Skip this commit if the audit found nothing to fix.)

---

### Task 8: Final checks and PR

**Files:** none new.

- [ ] **Step 1: Full local validator sweep**

```bash
python scripts/check_insights.py
python scripts/sync_insights_catalog.py --check
python scripts/check_nav_footer.py
python scripts/check_sticky_nav.py
python scripts/seo_check.py
```

Expected: the first four exit 0. `seo_check.py` is warn-only per PUBLISHING.md — read its output for any new class-hygiene warnings introduced by this branch and fix them before opening the PR even though it won't block CI.

- [ ] **Step 2: Diff review**

```bash
git diff main...HEAD --stat
```

Confirm the file list matches exactly: `site/architecture/index.html`, `site/integrations/mcp/index.html`, `site/docs/mcp/index.html`, `site/assets/css/integration-system-v2.css`, `scripts/sweep_mcp_cta.py`, the 19 non-MCP `site/integrations/*/index.html` files, `site/insights/agentic-change-management-needs-a-decision-layer/index.html`, `site/sitemap.xml`, `site/insights/all/index.html`, `site/insights/topics/architectural-governance/index.html`, `site/insights/index.html`, `scripts/ensure_og_coverage.py`, and the new `og.png`. `site/index.html` (homepage) must **not** appear in this list.

- [ ] **Step 3: Push and open the PR — stop for explicit confirmation first**

This is a "publishing/posting content" action under this environment's permission rules. Present the final diff summary and the PR title/description to the user and get explicit go-ahead before running:

```bash
git push -u origin site/agentic-sdlc-decision-layer
gh pr create --title "Position Mneme's Decision Index against post-MCP agentic change management" --body "$(cat <<'EOF'
## Summary
- Add a decision-plane vs. change-plane distinction to /architecture/
- Extend /integrations/mcp/ with an agentic-SDLC positioning section (CodeRabbit Triage cited as an interoperability example, not an integration) and a reverse native-integrations section
- Add a vendor-neutral downstream-governance-consumers flow to /docs/mcp/
- Ship a shared "Use Mneme through MCP" cross-integration CTA across all 19 non-MCP integration pages
- Publish the pillar article "Agentic Change Management Needs a Decision Layer"
- Homepage intentionally untouched (source scope conversation explicitly rejected a homepage change)

## Test plan
- [ ] `python scripts/check_insights.py` exits 0
- [ ] `python scripts/sync_insights_catalog.py --check` exits 0
- [ ] `python scripts/check_nav_footer.py` exits 0
- [ ] `python scripts/check_sticky_nav.py` exits 0
- [ ] Adversarial maturity audit completed and findings applied (Task 7)
- [ ] Manual visual pass on /architecture/, /integrations/mcp/, /docs/mcp/, two integration pages (one per CTA layout), and the new article
EOF
)"
```

Use the user's CLAUDE.md squash-merge convention: the PR title becomes the squash commit title on `main`, so make it accurate and final before opening.
