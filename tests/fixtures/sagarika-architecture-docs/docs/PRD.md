# AI System Architect — Product Requirements Document

**Version:** 0.1 (MVP)
**Owner:** Saga
**Product type:** Internal accelerator (personal + team use). Not a commercial product in v0.1.
**Build budget:** One evening (~4 focused hours)
**Date:** 6 Aug 2026

---

## 0. Framing note (read first)

The obvious version of this product is "describe a use case → get a production-ready architecture." That framing is wrong, and building to it will produce something that looks impressive in a demo and is useless on Monday.

An LLM cannot produce a *production-ready* architecture from a paragraph, because production-readiness is a function of constraints the user hasn't stated: latency budget, data residency, existing platform, team skill, budget, compliance regime, failure tolerance. Any system that skips those and emits a confident diagram is generating plausible-looking debt.

**The actual job to be done:** compress the 2–4 hours you currently spend turning a vague stakeholder request into a defensible first-draft architecture, down to ~10 minutes — *and* surface the questions you would have forgotten to ask.

So the product has two outputs of roughly equal value:

1. A structured architecture draft.
2. An explicit list of assumptions made and decisions deferred.

Output #2 is the differentiator. Everything else is a wrapper around a good prompt.

---

## 1. Vision

**One line:** Turn a half-formed AI use case into a defensible architecture draft and a list of the right questions, in ten minutes.

**Three-year version:** A system that encodes *your* architectural judgement — patterns you trust, vendors you've validated, failure modes you've seen — so that the quality of an architecture proposal is no longer bounded by who happens to be in the room.

**Explicit non-goal:** Replacing the architect. The product produces a draft that a competent architect edits. It is a leverage tool, not an autonomy tool.

---

## 2. Users

| Segment | Who | Core pain | Priority |
|---|---|---|---|
| **P0 — You** | AI Lead scoping 3–10 use cases per quarter | Repeated cold-start cost; inconsistent quality across drafts; forgetting to ask about compliance/latency until week three | Must serve perfectly |
| **P1 — Your engineers** | Mid-level AI/DS engineers proposing designs | Don't know the pattern space; over-reach on complexity; can't defend choices to leadership | Serve in v0.2 |
| **P2 — Business stakeholders** | Product owners, transformation leads | Ask for "an AI agent" without knowing what that implies in cost or effort | Read-only consumer of output |

**Not a user in v0.1:** external clients, anyone who needs the output to be authoritative without review.

---

## 3. User Stories

**P0 (MVP)**

- As an AI Lead, I paste a 3-sentence use case description and get back a structured architecture so I don't start from a blank page.
- As an AI Lead, I see which assumptions the system made on my behalf, so I know exactly what to verify with the business.
- As an AI Lead, I get a list of open questions ranked by how much they'd change the design, so I walk into the stakeholder meeting with an agenda.
- As an AI Lead, I get a *rejected alternatives* section, so I can defend the choice when a stakeholder asks "why not fine-tuning?"
- As an AI Lead, I can save the output as markdown into my working folder, so it becomes the seed of a real design doc.

**P1 (post-MVP)**

- As an engineer, I answer 5 clarifying questions before generation, so the output reflects real constraints.
- As an AI Lead, I constrain generation to our approved stack, so outputs are actionable inside our platform.
- As an AI Lead, I regenerate a single section without redoing the whole document.

**Explicitly deferred:** collaboration, versioning, cost modelling, IaC generation.

---

## 4. MVP Scope

**In (one evening):**

- Single text input: freeform use case description.
- Three optional dropdowns: deployment target (cloud / on-prem / hybrid), data sensitivity (public / internal / regulated), scale (prototype / team / enterprise). These three are chosen because they change the architecture more than any other variable.
- One LLM call with a heavily structured system prompt and a fixed output contract.
- Markdown output, rendered in-app.
- A Mermaid component diagram embedded in the markdown.
- "Copy" and "Save to folder" buttons.

**Out (v0.1):**

- Accounts, auth, persistence, history
- Multi-turn refinement
- RAG over your own past designs
- Cost estimation
- Diagram editing
- Export to PDF/Confluence/Notion
- Any evaluation harness

**Recommended surface:** Streamlit, single `app.py`, one Anthropic API call. ~150 lines. If it takes more than 150 lines you have over-engineered it — the value is 90% in the prompt, 10% in the code.

**Definition of done for the evening:** you run it on one real use case from your current backlog and the output is good enough that you'd edit it rather than discard it.

---

## 5. Inputs

| Input | Type | Required | Why it exists |
|---|---|---|---|
| Use case description | Freeform text, 2–10 sentences | Yes | Primary signal |
| Deployment target | Enum: Cloud / On-prem / Hybrid / Unsure | No | Gates the vendor and pattern space |
| Data sensitivity | Enum: Public / Internal / Regulated / Unsure | No | Determines whether external model APIs are viable at all |
| Scale | Enum: Prototype / Team / Enterprise | No | Separates "a script and a vector store" from "a platform" |

"Unsure" is a first-class value, not a fallback. When selected, the system must raise the corresponding question in the Open Questions section rather than silently picking.

**Deliberately excluded from MVP:** budget, timeline, team size, existing stack. All materially useful — all add form friction on the first run, which is where adoption dies.

---

## 6. Outputs

A single markdown document with a fixed section contract:

| # | Section | Content | Constraint |
|---|---|---|---|
| 1 | **Problem restatement** | The use case in one paragraph, in system terms | Forces the model to show it understood; makes misreads obvious immediately |
| 2 | **Assumptions made** | Bulleted, explicit | Non-negotiable. This is the trust mechanism. |
| 3 | **Recommended pattern** | Named pattern (e.g. retrieval-augmented Q&A, tool-using agent, batch classification pipeline) + why | One recommendation, not three. Opinions are the product. |
| 4 | **Component architecture** | Table of components: name, responsibility, suggested technology, alternative | Technology suggestions must include an alternative to avoid vendor anchoring |
| 5 | **Data flow** | Mermaid diagram + numbered walkthrough | Diagram must be syntactically valid Mermaid |
| 6 | **Rejected alternatives** | 2–3 approaches considered and why not | The section that makes the output defensible in a review |
| 7 | **Key risks** | Table: risk, likelihood, mitigation | Must include at least one failure mode specific to the use case, not generic "hallucination" |
| 8 | **Open questions** | Ranked by design impact | Ranked, not listed. The top question should be the one that would most change the answer. |
| 9 | **First three steps** | Concrete next actions | Bounded at three. Prevents roadmap-shaped output. |

**Hard length ceiling:** ~1,200 words. An architecture document nobody reads has zero value. Verbosity is the primary failure mode of LLM-generated design docs and must be constrained in the prompt.

---

## 7. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-1 | Accept freeform text input up to 2,000 characters | P0 |
| FR-2 | Accept three optional constraint selectors, each supporting "Unsure" | P0 |
| FR-3 | Generate output conforming to the 9-section contract in §6 | P0 |
| FR-4 | Emit exactly one recommended pattern, never a menu | P0 |
| FR-5 | Emit a syntactically valid Mermaid diagram; render it in-app | P0 |
| FR-6 | Every "Unsure" input must produce a corresponding entry in Open Questions | P0 |
| FR-7 | Copy full output to clipboard | P0 |
| FR-8 | Save output as `.md` to a configured folder with a slugged filename | P0 |
| FR-9 | Show a clear error state on API failure; never render partial output as complete | P0 |
| FR-10 | Refuse gracefully when input is too vague to architect against (< ~15 meaningful words) and ask for more | P1 |
| FR-11 | Regenerate a single section on demand | P2 |
| FR-12 | Constrain suggestions to a user-supplied approved-technology list | P2 |

---

## 8. Non-Functional Requirements

| ID | Requirement | Target | Rationale |
|---|---|---|---|
| NFR-1 | Time to first output | < 60s | Above this, the user context-switches and abandons |
| NFR-2 | Cost per generation | < $0.15 | Must be ignorable so usage is unmetered by the user's own hesitation |
| NFR-3 | Codebase size | < 200 LOC, single file | An evening build that grows a module structure will not ship |
| NFR-4 | No data persistence in v0.1 | Zero storage | Removes the entire security/privacy surface. Use cases may contain confidential business context. |
| NFR-5 | API key via environment variable only | Never in source or UI | Baseline hygiene |
| NFR-6 | Output determinism | Temperature ≤ 0.4 | Architecture drafts should be stable, not creative |
| NFR-7 | Graceful degradation | If Mermaid fails to parse, show the code block rather than breaking the page | Diagram is supporting, not load-bearing |
| NFR-8 | Zero-install for a second user | Single command to run | Prerequisite for the P1 audience later |

**Not a requirement in v0.1:** uptime, concurrency, observability, rate limiting. Single-user local tool.

---

## 9. Future Roadmap

| Phase | Focus | Key additions | Unlock |
|---|---|---|---|
| **v0.1** — one evening | Prove the prompt | Core generation loop, 9-section contract, markdown out | Does the output beat a blank page? |
| **v0.2** — week 2 | Constraint fidelity | 5-question clarifying pre-pass; approved-stack constraint list; section-level regeneration | Output becomes actionable inside your real platform |
| **v0.3** — month 2 | Institutional memory | RAG over your past design docs and post-mortems; house patterns; "we tried this before" retrieval | Output starts reflecting *your* judgement, not the internet's average |
| **v0.4** — month 3 | Economics | Cost/latency estimation per component; build-vs-buy comparison; effort sizing | Makes the output usable in a funding conversation, not just a design review |
| **v0.5** — month 4+ | Distribution | Multi-user, Confluence/Notion export, review workflow, versioned decisions (ADR format) | Becomes team infrastructure rather than a personal tool |

**The compounding asset is v0.3.** Versions 0.1 and 0.2 are commodity — anyone can build them, and a frontier model will absorb them. The defensible layer is the corpus of your organisation's own architecture decisions and their outcomes. Start capturing that from day one, even manually, even before you have the retrieval built.

---

## 10. Success Metrics

Single metric for v0.1: **edit-not-discard rate.** Across your next 10 real use cases, in what fraction did you keep the generated draft as the starting point rather than throwing it away?

- < 40% → the prompt is wrong. Fix the prompt, not the product.
- 40–70% → working. Proceed to v0.2.
- \> 70% → be suspicious. You may be accepting mediocre output because it's convenient.

Secondary: **surprise rate** — how often does the Open Questions section raise something you hadn't considered? This is the leading indicator for whether the tool adds judgement or just formats yours.

---

## 11. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Output is confidently wrong and gets copied into a real proposal | High | Assumptions section is mandatory and appears second, before any recommendation |
| Verbosity makes output unreadable | Medium | Hard word ceiling in the prompt; enforce section contract |
| Scope creep turns an evening into a fortnight | High | 200 LOC ceiling; feature list in §4 is a contract with yourself |
| Frontier models make the wrapper obsolete | Medium | Accepted. Value migrates to v0.3's proprietary corpus. Build v0.1 cheaply on that assumption. |
| Tool substitutes for thinking | Medium | Positioned as draft generator; success metric measures editing, not acceptance |

---

## Appendix: The prompt is the product

Budget your evening as: 45 minutes on scaffolding, 2.5 hours iterating the system prompt against 3 real use cases, 45 minutes on polish. If you invert that ratio you will ship something that runs and doesn't work.
