# Scope brief: Post-OKF architecture article scope

Status: **gathered, not built.** Do not treat as published; no `***` mark.

| Field | Value |
|---|---|
| ChatGPT chat | `Post-OKF architecture article scope` |
| Created / last updated (UTC) | 2026-09-01 / 2026-09-01 (local timestamp in chat: Tue Sep 1, 6:00 AM) |
| Shape | User prompt "Scope sn article with the latter title" (it refers to a title offered in a previous assistant turn that is in the same chat), then a scoped assistant reply. |
| Repo check | **Partial overlap, read before building.** `site/insights/open-knowledge-format-vs-governance/` ("Open Knowledge Format vs Governance: Why Structured Memory Is Not Enough for AI Agents") shipped 2026-06-17 in `b7a9c656c`. It does **not** mention OKF v0.2, Attested Computation or `stale_after`. The scoped article is therefore not shipped, but it must be differentiated from, and should link to, that page. The chat claims neither repo mentions OKF; that is **wrong as of today**. |

## Build card

| Field | Value |
|---|---|
| Kind | **update `open-knowledge-format-vs-governance` instead** (cannibalisation verdict below); the rows that follow apply only if the user overrides and wants a separate article |
| Cannibalisation | `find_overlap.py`: `open-knowledge-format-vs-governance` 129.8 (same entity, same query), next hit 30.7. Verdict: **update instead**: add a v0.2 section (trust vs authority, applicability, Attested Computation precedent) to the June page and refresh its `dateModified` |
| Title | Open Knowledge Format v0.2: From Trusted Knowledge to Enforceable Architecture (proposed; ADR-015 puts the entity first, unlike the chat's title) |
| Slug | `open-knowledge-format-v0-2-enforceable-architecture` |
| Report-anchored (ADR-015) | yes: entity = "Open Knowledge Format" (confirm exact version naming in the live spec) |
| Topic hub | agent-infrastructure (same hub as the June OKF piece) |
| Content type (`--type`) | Analysis (unchanged: this is an update of the existing page) |
| OG headline | OKF v0.2 Meets Architectural Authority (5 words) |
| Editorial gate | pass: new evidence (v0.2 trust, lifecycle and Attested Computation) plus a named-source entry point |
| Five questions | changed: OKF v0.2 adds provenance, lifecycle, freshness, attestation; matters: agents get trusted knowledge; breaks: trusted is not authoritative, and authority is not applicability; do: classify authority and scope separately from trust; governance: compile the authoritative subset into scoped rules |
| Cross-links | `open-knowledge-format-vs-governance` (and add a reciprocal link from it) |

## Draft quality gate (filled at build time)

| Check | Result |
|---|---|
| stop-slop score (/50, pass >= 35) | |
| `lint_prose.py` | |
| Cold read: thesis as restated | |
| Cold read: unclear terms, and how resolved | |

## Agreed scope

- **Target title (the chat's chosen one):** From Open Knowledge to Enforceable Architecture: Where OKF Meets AI Coding Agents.
- **Alternate, rejected as too provocative:** Open Knowledge Is Not Architectural Authority.
- **Slug suggestion:** `open-knowledge-to-enforceable-architecture`
- **Audience:** engineers and architects following agent-knowledge standards; standards-literate readers. Also suited to an external pitch (the chat names O'Reilly Radar). Length target **1,600-2,000 words**.
- **Thesis:** trusted knowledge is not architectural authority. Chain: knowledge → trusted knowledge → authoritative decision → applicable constraint → runtime enforcement. OKF handles the first two; Mneme's territory starts at the transition from knowledge to authority.

### Structure agreed

1. Agents do not merely need more context (available vs governing context; six questions: current? provenance? who approved? guidance only? applies to this change? may the agent violate it?).
2. What OKF changes (brief, not a tutorial): directory of Markdown with YAML frontmatter; only `type` universally required; producers can define types. Illustrative frontmatter: `type: Architecture Decision`, `status: stable`, `verified.by: human:principal-architect`, `stale_after: <date>`.
3. **Trust is not authority** (the central, strongest original idea). `verified` signals confirmation, not obligation; OKF itself calls trust tiers advisory, not access control.
4. Applicability: even an authoritative ADR does not govern every operation (e.g. "payments services must use PostgreSQL" governs `services/payments/**`, not `docs/**`). So authority + scope + operation + lifecycle.
5. From decision to agent constraint (pipeline: OKF concept → trusted knowledge → authority classification → scope resolution → guidance or enforceable rule → agent action → allow/warn/block).
6. **Attested Computation precedent** (the section that elevates the piece): v0.2 lets a sanctioned computation, executor contract and deterministic attester be declared so a consumer can check a value was produced by the approved computation. OKF records the computation and the means to check it; it executes nothing. Use it as a bridge: what would the analogous move look like for architecture decisions? Do not manufacture a gap.
7. Illustrative OKF + Mneme architecture diagram, **explicitly labelled illustrative, not shipped**.
8. Close bigger than Mneme: open formats describe portable knowledge; governance systems interpret the subset that carries organisational authority; agent runtimes consume the resulting context and constraints.

### Follow-up piece (not this build)

"Turning Open Knowledge into Architectural Guardrails: An OKF Compatibility Experiment". Depends on a small OKF importer → Architecture Audit experiment, which is **not built**. Concept article first, evidence article later.

## Key facts, figures, sources

**None verified yet.** All sourced to one document (query string stripped; the chat's `%2F` encoding decoded to `/`):

- https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

Facts the chat attributes to it (verify each in the live spec, including the version):
- OKF is a vendor-neutral interchange format for agent-readable knowledge: Markdown + YAML frontmatter, Git-friendly.
- v0.2 adds provenance, verification/trust, lifecycle (draft, stable, deprecated), freshness (`stale_after`), and Attested Computation.
- `type` is extensible; consumers must tolerate unknown types; types are not centrally registered.
- Trust tiers are advisory signals, not access control.
- Attested Computation separates the definition, runtime, executor receipt and deterministic attester.

## Mneme positioning constraints

- Not "OKF vs Mneme". They are complementary layers.
- Do **not** say OKF provides deterministic architecture enforcement, and do not say "OKF stops at trusted knowledge" (v0.2 goes further).
- Do not imply every stable or human-reviewed concept becomes enforceable.
- Do not present `type: Architecture Decision` as an official OKF type; say it is possible because the type system is extensible.
- The Mneme-consumes-OKF pipeline is **PLANNED/CONCEPTUAL**. No OKF importer exists. Phrase as "an architectural possibility" and "Mneme HQ is exploring this second layer". The audit must not let it read as shipped.
- Mneme's existing decision/authority/applicability machinery (retrieval vs enforcement distinction, scoped rules) is the grounded part; verify against the current release's documented behaviour (mneme-hq 0.10.0 release notes and docs).

## Non-insight site edits requested

None beyond the article work itself, which is an update to the June `open-knowledge-format-vs-governance` page (see the build card).

## Open questions

- Resolved: **update the June `open-knowledge-format-vs-governance` page** with a v0.2 section (cannibalisation verdict in the build card); no new article.
- Which of the earlier title options was "the latter title"? The chat resolved it to the "From Open Knowledge to Enforceable Architecture" title.
- External pitch (O'Reilly Radar) intended or Mneme site only?
- The chat mentions an Aug 6 screenshot about an "Agent Knowledge Compiler & Control Plane". Not available here.

## Unverified / needs checking

- **The repo-coverage claim in the chat is stale/incorrect** (see Repo check).
- OKF version number, field names (`verified`, `stale_after`, attested computation terms) and the statement about advisory trust tiers must be re-read in the live SPEC.md. The chat's citations are inline "GitHub" labels pointing at one file; it is not clear which section backs each point.
- "OKF v0.2 is a September 2026 development" is implied but undated in the chat. Find the release or commit date.
