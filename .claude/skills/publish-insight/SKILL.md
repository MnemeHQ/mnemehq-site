---
name: publish-insight
description: End-to-end procedure for turning ChatGPT "Post-" scope chats into published mnemehq.com insight articles. Use when asked to "draft insights", gather scope briefs, build an insight from a brief, or check which scope chats are unprocessed.
---

# Publish an insight

One procedure, five stages. Rules live in `PUBLISHING.md` (Insights articles, OG images,
Conceptual authority) and `docs/site/insight-publishing-contract.md`; this skill is the order of
operations and points back to them. If this file and those disagree, those win; fix this file.

Insights only. Concept pages, landing pages, pricing, roadmap and other page edits follow
`docs/site/concept-publication.md` or their own contracts and go in separate PRs.

## Stage 1: Intake (read-only)

1. Read `docs/site/insights-scope-ledger.md` and `docs/site/scope-briefs/README.md`.
2. Open ChatGPT in the user's real Chrome (`mcp__claude-in-chrome__*`), project
   **Mneme Growth and GTM**. Use the project page's list,
   not search.
3. Match the `Post-` prefix case-insensitively (`post-reverse engineer decisions` counts). A
   `Post-` chat whose title contains `*` is processed (shipped, merged into a shipped article, or dropped). Unmarked chats are candidates, but the
   test of "shipped" is the repo: `git log origin/main` and `ls site/insights/`. Renaming re-sorts
   chats, so list position means nothing.
4. Skip `Post-tv-` chats: they belong to theovalmis.com and never enter `site/`.
5. Read every candidate chat **in full**: expand "Show more", read every turn. The last turns often
   reverse earlier ones; the final agreed scope is what counts.
6. Never rename, delete or message a chat in this stage (marking happens only at close-out, Stage 5).
7. Confirm the list of chats and titles with the user before writing anything.

Tip: `get_page_text` reads a whole chat. Inline citations render only as labels ("Reuters +2");
pull their real URLs from the `<a href>` elements in `main`, and strip `?utm_source=chatgpt.com`.

**This repository is public.** Briefs and every other file here are world-readable. Never copy
into them: investor or fundraising details, sales-pipeline or customer-conversation facts, names
of prospects, design partners or private contacts, internal competitive threat or valuation
assessments, or go-to-market targeting. Summarise what the site needs and note that other
follow-ups are tracked privately.

## Stage 2: Brief

Write one brief per chat at `docs/site/scope-briefs/<yyyy-mm-dd>-<kebab-title>.md` from
`docs/site/scope-briefs/TEMPLATE.md`, and add it to the README index. Date = chat creation date
(UTC). The **Build card** must be complete before Stage 3:

- slug, title, report-anchored or not (ADR-015), topic hub, OG headline (4-7 words), eyebrow
- editorial-gate verdict (below)
- cannibalisation check (below)
- every source with a verified / unverified flag
- every Mneme claim with its maturity class

### Editorial gate

Publish only if the piece does at least one of: targets a distinct query; adds new evidence to a
Mneme thesis; creates an entry point from a named report, vendor or paper; supports a cornerstone
through internal linking. Not because an announcement can be reframed as "this also needs
governance". It must answer: what changed, why it matters, what breaks, what teams should do, how
governance helps. Fail the gate → record "drop" or "re-angle" in the brief and stop.

### Cannibalisation check

Run for every proposed page, with its title and target keywords:

```bash
python scripts/find_overlap.py "<proposed title>" --keywords "<kw1>,<kw2>"
```

It ranks existing pages (insights, concepts, compare, docs, use-cases) by rarity-weighted overlap
of title, H1, description, lede, OG image alt text and slug. It does not read article bodies, so
also search them for the proposal's key figures, entities and source names, e.g.
`git grep -n -i -E "240%|national bureau|nber" -- site/insights` (the 2026-10-12 miss: a
scoped "new" NBER article already existed as `ai-throughput-is-not-engineering-throughput`). It is a screen, not a verdict: read every page scoring 40 or
more and judge whether a searcher for the target query would be served by it. Record the top hits
and scores in the brief, then one verdict:

- **clear**: distinct query or named-source entry point; link to the top hits.
- **re-angle**: same topic, different intent; state the narrower angle that separates them.
- **update instead**: same entity or query as an existing page (e.g. a new version of a spec
  already covered); extend that page, do not publish a new one.
- **merge or drop**: same thesis as an existing page.

Also compare the candidates in the batch with each other (the script only sees published pages):
two briefs scoping the same thesis become one article. New category terms proposed in the same
batch compete too; settle them together under the terminology lock before building any of them.

## Stage 3: Build

1. **Verify every citation against the live source** before writing a sentence that depends on it.
   Never ship a fabricated ID, report title or statistic. Record the check in the brief.
2. Write the body following PUBLISHING.md: News → Problem → Governance; for engineering leaders;
   concrete and declarative; never "bottleneck"; no em dashes as connective tissue; domain is
   `mnemehq.com`; terminology lock ("decision corpus", "enforcement", "drift"...); "decision
   layer" thesis framing only per the 2026-09-11 amendment.
3. Report-anchored pieces: verbatim entity first in all six title fields; meta description leads
   with source + figure verified against the body.
4. **Comprehension and slop filter (gate before the final write-up).** The draft does not become a
   page until it passes all three:
   1. **Slop pass:** apply the `stop-slop` skill to the draft and score it on its 50-point rubric.
      Below 35, revise and rescore. Record the final score in the brief. (`stop-slop` is a
      user-level skill; if it is not installed, score the same five dimensions by hand:
      directness, rhythm, trust, authenticity, density, each out of 10.)
   2. **Lint:** `python scripts/lint_prose.py <body.html>`. Zero errors (house voice: no
      "bottleneck", no em dash). A block that quotes an external source verbatim (a report title
      or a quotation) may carry `<!-- voice-ok: reason -->` before it; that exempts only that
      block, never house prose. Fix every warning or justify it in the brief: slop phrases, sentences averaging
      over 22 words, more than 15% over 30 words, Flesch under 30, paragraphs over 120 words,
      acronyms not expanded on first use.
   3. **Cold read:** a reviewer with no context (a fresh subagent given only the draft, never the
      brief or the chat) answers: what is the thesis in one sentence; who should act and what
      should they do; which terms were unclear. Pass only if the thesis matches the brief's, the
      action is concrete, and every unclear term gets defined at first use. Internal names (ADR
      numbers, O1, DG1, codenames) must be defined or removed. "Decision Index" is a product term with its own docs page; define it at first use.
5. Create the page:
   ```bash
   python scripts/new_article.py --slug <slug> --title "<title>" \
     --description "<150-160 chars>" --date <YYYY-MM-DD> --lede "<standfirst>" \
     --body-file <body.html> --type "<canonical type>" [--read-time ...] [--faq faq.json]
   ```
   It writes the page only. There is no `--register` flag; registration is the next step.

## Stage 4: Register and validate

Registration (all manual, per `docs/site/insight-publishing-contract.md`):

1. OG record under `insights/<slug>/` in `site/og/cards.yaml` (editorial: headline only), then
   `python scripts/render_og.py --strict --out site --only insights/<slug>/`.
2. `<url>` block in `site/sitemap.xml`.
3. Card in `site/insights/all/index.html` **and** its `CollectionPage.hasPart` entry; card on the
   topic hub `site/insights/topics/<hub>/index.html`.
4. `python scripts/sync_insights_catalog.py`
5. Reciprocal links from 2-3 related insights.

Validate, in order (all must pass):

```bash
python scripts/render_og.py --strict --dry-run
python scripts/check_og_coverage.py
python scripts/lint_og_voice.py
python scripts/check_og_render_unique.py
python scripts/sync_insights_catalog.py --check
python scripts/check_insight_types.py
python scripts/check_insights.py
python scripts/check_encoding.py site scripts
python scripts/lint_prose.py site/insights/<slug>/index.html   # re-run on the built page
```

`lint_prose.py` is not a CI gate: 133 of 179 published articles (as of 2026-10-12) predate it and still use em dashes, and 25 use "bottleneck"
in body prose. Apply it to new and substantially edited articles only.

## Stage 5: Audit, PR, ship, close out

1. **Opus audit before merge** (required). Classify every sentence about Mneme as SHIPPED /
   VALIDATED EXPERIMENT / PLANNED / CONCEPTUAL, calibrated to ADR-001 claim levels: category and
   vision claims may lead; concrete claims (integrations, enforcement paths, enterprise features)
   stay literal. Fix everything flagged.
2. **Citation verification is mandatory before publication.** Scope briefs may carry unverified
   citations; an article may not. Every source row in the brief must read "verified" (checked
   against the live source, with the page or section) before the PR is opened. Unverifiable
   claims are cut, not softened.
3. Category or tagline changes need ADR-001/013/014 amendments in `MnemeHQ/mneme` first.
4. Batch all insights from one run into one PR on a `site/` branch. Fill the Execution provenance
   block (`AGENTS.md`). Confirm titles and count with the user. Squash merge.
5. Deployed means: a successful "Deploy site to mnemehq.com" run for the exact `main` SHA, and
   `site-deployed` resolving to it. Merge alone is not deployment.
6. Close out, in this order, once deployment is verified:
   1. Add the chat to the ledger's Published table (PR, merge date) and set the brief's status to
      "built" (or "dropped" / "merged", with the reason).
   2. **Mark the chat in ChatGPT (required):** rename it to `***<original title>` in the user's
      real Chrome, in the Mneme Growth and GTM project. Mark every chat whose scoped items are all
      shipped, merged into another shipped article, or explicitly dropped by the user; a chat with
      any open item stays unmarked (e.g. `Post-Writing ROI Content` while its backlog is open).
      Marking is a required step, but this file is not a standing authorisation: list the exact
      chats you will rename and get the user's confirmation in chat first. It is the only write
      to ChatGPT in this procedure. Never rename a chat for any other reason, never edit or delete
      messages, never mark a `Post-tv-` chat.
   3. Verify each mark: re-list the project's conversations and confirm the new titles start with
      `***`. Report the marked chats, and any that stayed unmarked with why, in the close-out
      message.
