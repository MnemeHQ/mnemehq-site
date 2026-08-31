## Summary

Adds loose ADR normalization to the Architecture Audit Workspace (M0.1). This enables the Audit to extract architectural intent from common non-Mneme ADR formats (MADR, custom Markdown ADRs) while preserving canonical Mneme ADR parsing as the authoritative source.

## Key Changes

### Loose ADR Parser (`audit/backend/app/services/loose_adr_parser.py`)
- **Exact heading matching**: Uses normalized heading text comparison instead of prefix matching. `Decision Drivers`, `Decision Context`, etc. no longer incorrectly match as Decision sections.
- **Provenance tracking**: Both `decision_start_line` and `decision_end_line` reset when a new valid Decision heading begins. Removes all `1-100` whole-file fallbacks — returns `"unknown"` if exact range cannot be established. Invariant: `end >= start`.
- **Supported decision headings**: `Decision`, `Decision Outcome`, `Outcome`, `Chosen Option`, `Accepted Decision` (exact match, case-insensitive).
- **Termination handling**: Decision sections correctly end at rationale headings, status headings, other headings, or EOF.

### Regression Tests (`audit/backend/tests/test_adr_gadr.py` — 8 tests)
- GADR fixture (3 guidance: 0000, 0001, 0002) with exact provenance assertions
- `Decision Drivers` heading correctly excluded from Decision extraction
- Context → Decision → Consequences ordering
- Decision at EOF (no trailing heading)
- Decision → Status termination
- Empty decision body rejected (no finding)
- Canonical Mneme ADRs (valid YAML frontmatter) excluded from loose parsing
- `index.md`, `template.md`, `README.md` skipped

### New Fixture
- `tests/fixtures/adr-gadr/docs/adr/0002-decision-drivers-structure.md` — Real GADR structure with `Decision Drivers`, `Considered Options`, `Decision Outcome`

### Cleanup
- Removed stray test files: `test_gadr.py`, `test_gadr_live.py`, `test_adr_live.py`

### Docker (`audit/backend/Dockerfile`, `.dockerignore`)
- Production image no longer copies `tests/`
- `CMD` honors `$PORT` via shell (`exec python -m uvicorn ... --port ${PORT}`)
- Repo-root `.dockerignore` effective for `docker build -f audit/backend/Dockerfile .`

## Verification

| Fixture | Result |
|---------|--------|
| `audit-repo` (canonical Mneme ADRs) | 1 Enforceable / 1 Partial / 3 Guidance |
| `adr-gadr` fixture (loose ADRs) | 0 Enforceable / 0 Partial / 3 Guidance |
| Live `adr/gadr` | 2 Guidance, provenance `17-27` / `43-49` (no `42-29` corruption) |
| Live `MnemeHQ/mneme` | Canonical ADRs processed via Mneme core |

## Boundary

**External ADR normalization → guidance-only findings** (confidence 0.5, no proposed rules).
**Canonical Mneme ADRs remain authoritative** for governability assessment and enforcement (Mneme core pipeline).