# Site scope: decision and control layer reposition

**Date:** 2026-09-25
**Source strategy:** `mneme-growth-ops/docs/plans/2026-09-25-decision-control-positioning-reposition.md` (growth-ops PR #29, merged)
**Status:** Approved 2026-09-25. Phase 1 is implemented in `site/decision-control-reposition`.

## Approved decisions (2026-09-25)

1. **Homepage hierarchy.** The H1 stays "Architecture that holds." The eyebrow above it becomes "The decision and control layer for agentic software development."
2. **`<title>`.** It keeps "Architectural Drift Prevention" for Phase 1. Description, OG, and structured data change now. Whether to migrate the title is a separate decision, informed by the GSC evidence below.
3. **OG versioning.** Cards opt in per record with `card: og-v3.png`. Unchanged pages stay on `og-v2.png`.
4. **Current-capability wording.** Used wherever product capability is described:
   - "across AI coding agents, repositories, and CI workflows" (not "delivery systems")
   - "decision-linked" or "inspectable enforcement results" (not "verifiable evidence")
   - "Architecture is the first decision domain; the model is designed to extend to broader engineering policy"
   - MCP: "Give compatible agents access to the same Mneme decisions and decision context" (not "authoritative")
   - Diagram: current surfaces solid (agent integrations, CLI, GitHub/CI); planned surfaces dashed (deployment platforms, OPA/policy engines, broader evidence return paths)
5. **Terminology.** *Decision and control layer* is what Mneme is. *Architecture protection* is what it does first. *Governance* is an outcome or capability, never the category name, and Phase 1 must not introduce "governance layer" as a synonym.
6. **Scope limit.** No sweep of the 332-file architecture-led content estate.

## GSC evidence for the title decision (last 90 days to 2026-09-25)

Source: BigQuery `mneme-hq-prod.searchconsole.searchdata_url_impression`, homepage URL only.

- The homepage has 1,570 impressions and 49 clicks. 1,141 impressions (73%) are anonymized queries.
- Every named query with more than one impression is branded: `mneme` (157), `mneme ai` (82), `mneme hq` (47, 26 clicks, pos 1.0), `mnemiq`, `mneme ai company`, and similar.
- Exactly one non-branded category query reaches the homepage: "how do i prevent ai agents from introducing architectural drift?" (1 impression, position 8).
- Site-wide, drift and guardrail queries land on content pages, not the homepage: `/insights/ai-coding-agent-guardrails/` (193 impressions), `/demo/architectural-drift/` (98), and `/concepts/architectural-drift-prevention/` (66).

**Reading:** the homepage title carries almost no measurable non-branded drift demand, so migrating it to the category line is low risk. The 73% anonymized share is the one unknown. The recommended follow-up is to change the title to `Mneme HQ — Decision and Control Layer for Agentic Software Development`, then watch branded clicks and anonymized impressions for 28 days.

## Companion PR: `MnemeHQ/mneme` README

Ship this in the same release window as Phase 1, because the site, the README, and `llms.txt` are the three canonical descriptions of Mneme.

- **Line 5** (currently "**Architectural drift prevention for the agentic AI SDLC.**") becomes: **Mneme is an open decision and control layer for AI-assisted software development.**
- **Line 7** becomes: *It turns durable engineering decisions into agent context, deterministic enforcement, and inspectable enforcement results across AI coding agents, repositories, and CI workflows. Architecture is the first supported decision domain: Mneme prevents architectural drift by enforcing approved ADRs and engineering standards.*
- **Line 17** ("Mneme is the architectural governance layer behind…"): drop "governance layer", per decision 5.
- **Keep** the Architecture Audit callout and every drift-prevention example beneath it.
- **Check** that `server.json` / `glama.json` / PyPI short descriptions match. They are also public descriptions.

## What the strategy asks of the site

The category moves above the use case:

| Level | Line |
|---|---|
| Category | The decision and control layer for agentic software development |
| Value | Make engineering decisions portable, enforceable, and provable across agents and tools |
| Current proof | Mneme starts with architecture: ADR-based decisions, applicability, deterministic rules, agent context, enforcement evidence |
| Use case | Prevent architectural drift before AI-generated code ships |

Hard constraints from the strategy, which also act as the audit checklist:

- Keep *architecture, architectural drift, ADR, guardrails, architecture protection* on the public surface.
- Never present security, compliance, platform, or operational-policy domains as current capability.
- Every use of the category line must sit next to a concrete primitive (decision identity, applicability, lifecycle, deterministic enforcement, MCP access, evidence).
- Don't treat "control plane" as a slogan, and don't describe interoperability as the moat.

## Current state (surveyed 2026-09-25)

The drift and governance framing is everywhere: 1,831 matches across 332 files. **This scope doesn't sweep the long tail.** The ~200 insights, the concept pages, and the compare pages keep architecture-first framing, which the strategy explicitly allows. The scope covers the surfaces that define *what Mneme is*:

| Surface | Current category statement |
|---|---|
| `site/index.html` `<title>` | "Architectural Drift Prevention for the Agentic AI SDLC" |
| Homepage kicker / H1 / deck | "Architectural drift prevention for the agentic AI SDLC" / "Architecture that holds." / "AI writes the code. Your architecture still decides what ships." |
| Homepage `What Mneme does` aside | "Mneme turns approved decisions into deterministic guardrails." |
| Homepage JSON-LD (`SoftwareApplication`, `Organization`) | Drift prevention; `about` Things list drift, AI SDLC, intent enforcement, ADRs |
| `site/about/` H1 + OG card | "Architectural drift prevention for the agentic AI SDLC." |
| `site/llms.txt`, `site/llms-full.txt` | "the architectural governance layer" plus "a governance and control plane for AI coding agents". The strategy's anti-pattern appears verbatim. |
| `site/docs/how-enforcement-works/` (linked as "Product" from the homepage) | "Human-readable decisions, deterministic enforcement." No decision-layer diagram. |
| `site/integrations/mcp/` | "Decision Interoperability". Already the most on-strategy page, with careful maturity wording. |
| `site/audit/` | "See how much architectural intent is protected from AI-generated drift." |
| `site/founder/`, `site/works-with/` meta | Drift origin story; "the governance layer across heterogeneous AI coding systems" |

## Claim-maturity blockers (resolve before writing copy)

These come from comparing the strategy's lines with what currently ships. Each needs a decision or a softened wording.

1. **"across agents, repositories, and delivery systems."** Delivery-system coverage today is the GitHub Actions gate (tested workflow); GitLab CI is only "designed to support." **Recommendation:** use the README variant, "across agents and repositories," for Phase 1. Add "delivery systems" only after a second CI surface ships.
2. **"verifiable evidence."** What ships is PASS/WARN/FAIL verdicts that reference the decision, plus the provenance concepts. There's no evidence store and no cross-tool evidence return path. **Recommendation:** use "enforcement evidence" or "a verdict tied to the decision that produced it." Don't use the strategy doc's `Evidence` box, fed from Agents/CI/Platforms, as a shipped flow.
3. **"Extend the same decision model to security, platform standards, compliance…"** This has to read as direction. **Recommendation:** "Architecture is the first domain. The decision model is built to extend beyond it; see the roadmap." Link `/roadmap/` and avoid present-tense domain lists. Also re-audit `site/use-cases/security-compliance-guardrails/` against this rule.
4. **MCP "the same authoritative engineering decisions."** `site/docs/decision-proposals/` says the MCP canonical-read path is *not yet automatically unified*. **Recommendation:** "Give any MCP-compatible agent read access to the same decision corpus." Keep the "without enforcement authority" boundary.
5. **Decision-layer diagram targets "OPA/etc." and "Platforms."** No OPA integration exists. **Recommendation:** the diagram shows shipped surfaces solid (Claude Code hook, Agent SDK, CLI, MCP, GitHub Actions) and planned surfaces dashed and labelled *planned*.

## Page changes

### Phase 1: narrative alignment (one PR, `site/decision-control-reposition`)

**1. Homepage** (`site/index.html`)
- Kicker: "Architectural drift prevention…" becomes **"The decision and control layer for agentic software development."**
- H1: **keep "Architecture that holds."** It's the concrete-domain promise and it satisfies the "don't remove architecture" rule. *(Decision: the strategy's "preferred direction" makes the category the headline. Recommend keeping the H1 and moving the category into the kicker plus the definition aside. That's lower risk, and the success test is still met by the aside.)*
- Hero deck: keep. It already matches the strategy's "engineering intent decides what ships" outcome.
- `What Mneme does` aside: rewrite to the Level 2/3 pair: decisions become agent context, deterministic rules, and a verdict tied to the decision. Architecture is first. This aside is where success-test Q1 and Q2 get answered.
- New short problem band (strategy §2) before the flagship scenario: *Your decisions already exist → Agents don't consistently carry them → Mneme makes them operational.* Three lines, existing `hm-` styles, no new CSS.
- Product-boundary sentence (strategy §4) in the "Explore" or compatibility section, to answer success-test Q3.
- `<title>`: **decision needed, SEO risk.** Recommend `Mneme HQ — Decision and Control Layer for Agentic Software Development | Architectural Drift Prevention`, or check GSC homepage queries first. If "architectural drift prevention" drives homepage impressions, keep it in the title tail.
- `meta description`, `og:*`, `twitter:*`: category first, drift as the use case.
- JSON-LD: `SoftwareApplication.description` and `Organization.description` get the category line. `about` Things add "Engineering decisions" and keep all four existing items.

**2. About** (`site/about/`): H1 becomes the category. Move the drift-prevention sentence into the first paragraph as "first domain."

**3. `site/llms.txt` + `site/llms-full.txt`**: replace "architectural governance layer" and **remove "governance and control plane"**. Add the messaging ladder, the "What Mneme is not" list from the strategy's product boundary, and the architecture-first statement. These are the highest-leverage AI-citation surfaces, and today they state the old category outright.

**4. Meta-only touch-ups** (no body rewrite): `site/works-with/`, `site/founder/` description, `site/pricing/` title ("Deterministic AI Coding Governance"), `site/docs/` description.

**5. Footer** (`site/_snippets/footer.html`): keep the "Architectural drift prevention" link. Optionally add a one-line category tagline. The footer is a shared snippet, so check the propagation script.

### Phase 2: conceptual proof (separate PRs)

**6. Product page diagram** (`site/docs/how-enforcement-works/`): add the canonical *Engineering intent → Mneme decision layer → Agents | CI | (planned) → verdict/evidence* diagram as inline SVG using `site/assets/css/diagrams.css` tokens, per blocker 5. Add the product-boundary paragraph. Retitling the page to "How Mneme works" is optional.

**7. MCP page** (`site/integrations/mcp/`): new lead line per blocker 4, and frame MCP as *proof that decisions are addressable independent of the harness*. Keep the local-stdio, non-authoritative framing.

**8. Audit** (`site/audit/`): keep the name and the H1. Add one line framing it as "the first application of the decision model," plus the Decision → Relevance → Representation → Current control → Gap flow. Check first whether the audit report actually emits each stage. Don't add stages it doesn't produce.

**9. Decision Model docs hub** (strategy §7): a new `site/docs/decision-model/` hub. It should link the concept pages that already exist (`precedence-semantics`, `decision-continuity`, `enforcement-provenance`, `governance-provenance`, `deterministic-enforcement`) rather than write new ones. New pages for **applicability**, **authority**, and **lifecycle** only where `mneme` core has a documented behaviour to cite. Reorder `site/docs/index.html` into Concepts / Architecture / Interfaces.

**10. "Context alone is not control" article**: `site/insights/why-context-alone-doesnt-prevent-architectural-drift/` already exists. Refresh its framing and cross-link it from the homepage problem band instead of writing a new piece.

### Out of scope

- Insights, concept, and compare long tail. Leave them as they are and let new content use the broader framing.
- Phase 3 domain pages. They're gated on product evidence.
- `mneme` repo README. It's a separate repo, but it should ship the same week as Phase 1 so the GitHub and site categories match. Social, deck, and application boilerplate belong to growth-ops.

## Asset changes

**Prerequisite: OG versioning.** `scripts/render_og.py:29` hardcodes `CARD_NAME = "og-v2.png"`. Re-rendering a changed card therefore overwrites `og-v2.png` in place, which violates `PUBLISHING.md:105`: cPanel won't reliably replace the file, and LinkedIn/X cache by URL. **Options:** (a) add a per-record `file:` override in `cards.yaml` so changed cards emit `og-v3.png` and only their HTML refs change (recommended, small); (b) bump `CARD_NAME` globally and update every page's `og:image`/`twitter:image` (~330 files).

| Asset | Change |
|---|---|
| `site/og/cards.yaml` `''` (homepage) | "Keep AI code aligned with your architecture" becomes the category headline, e.g. **"The decision layer for agentic software"** (6 words; the full category line is 7 and also fits). Brand family, no secondary copy. |
| `about/` card | headline becomes the category; `sup` drops "governance layer" |
| `integrations/mcp/` card | headline/alt to match the new lead; keep the `SHIPPED IN 0.9.0` badge |
| `docs/how-enforcement-works/` card | only if the page is retitled in Phase 2 |
| `audit/` card | no change: the architecture-specific wedge stays |
| New decision-layer diagram | inline SVG on the product page (theme-aware via `diagrams.css`) plus an exported PNG in `site/assets/images/` for README, decks, and social reuse |
| Hero photo (`photo-decision-wall.webp`), logo, favicon | no change: "people deciding" already fits the decision framing |

Every changed card runs the AGENTS.md gate in order: `render_og.py --strict --dry-run` → `check_og_coverage.py` → `lint_og_voice.py` → `check_og_render_unique.py`.

## Gates for every PR

1. Adversarial Opus audit before merge, with the SHIPPED / VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL test applied to every sentence about Mneme, and blockers 1–5 above as explicit checks. Verdict vocabulary is PASS/WARN/FAIL.
2. Existing site validators and the OG gate.
3. Success test from the strategy, read cold against the new homepage: can a technical buyer answer what Mneme is, what it controls today, how it differs from an agent or generator, and why it matters?

## Decisions needed from Theo

Resolved 2026-09-25. See "Approved decisions" at the top.
