"""Frozen discovery regression: the first Design Partner server capture.

Production finding (sagarika29/ai-system-architect @ 0797e27, server
mneme-hq 0.6.0, POST /api/v1/audit): the autonomous Audit returned exactly
one decision — a low-confidence "Project Config: pyproject.toml" pseudo-
decision — while the human-reviewed corpus contains meaningful documented
architectural boundaries in ordinary docs/ Markdown:

- docs/architecture-boundaries-base.md
- docs/architecture-guide.md
- docs/PRD.md

The fixture (tests/fixtures/sagarika-architecture-docs) is a read-only
transcription of that exact commit; see its PROVENANCE.md. This regression
does NOT require reproducing the nine human-authored project-memory records
exactly (that corpus was hand-authored by the partner using the documented
add-decision workflow). It asserts the narrow M0 acceptance criteria:

- meaningful documented boundaries are discovered autonomously;
- obvious Guidance is distinguished from deterministic requirements;
- source attribution (file + lines) is preserved;
- no Sagarika-specific vocabulary or filenames are special-cased;
- the output is substantially better than the one-pseudo-decision result;
- generic config echoes are labelled config evidence, not architecture
  decisions, and never dominate the result.
"""
from importlib.metadata import version
from pathlib import Path

from app.models.protection_audit import ProtectionClassification
from app.services.audit_persistence import AuditPersistenceService

FIXTURE = Path(__file__).parents[3] / "tests" / "fixtures" / "sagarika-architecture-docs"


def evaluate():
    service = AuditPersistenceService(session=None)
    return service._evaluate_p12(local_path=str(FIXTURE))


def by_text(result, needle: str):
    """Find the first decision whose requirement text contains needle."""
    matches = [d for d in result.decisions if needle.lower() in d.requirement.lower()]
    assert matches, f"no discovered decision contains {needle!r}"
    return matches[0]


def test_meaningful_boundaries_are_discovered_not_one_pseudo_decision():
    result = evaluate()
    # The production capture discovered exactly one config-echo row.
    # Discovery must now surface the documented boundary corpus.
    assert result.summary.decisions_discovered > 10
    # And the discovered set must include real architecture decisions,
    # not only a config echo.
    assert result.summary.by_category.get("architecture_decision", 0) > 10


def test_user_listed_examples_are_discoverable_with_expected_tiers():
    result = evaluate()
    deterministic = ProtectionClassification.REQUIRES_MODELLING
    guidance = ProtectionClassification.GUIDANCE

    # reject empty input before invoking the model
    assert by_text(result, "Empty input rejection").protection_classification == deterministic
    # required fields are enforced before the model call
    assert by_text(result, "Enforce required fields").protection_classification == deterministic
    assert by_text(
        result, "Validate required fields before calling the model"
    ).protection_classification == deterministic
    # validate output contract
    assert by_text(result, "Validate the output contract").protection_classification == deterministic
    assert by_text(
        result, "Validate the response against a markdown contract"
    ).protection_classification == deterministic
    # fail closed when required sections are absent
    assert by_text(
        result, "Fail closed if the output is missing required sections"
    ).protection_classification == deterministic
    assert "fails closed" in by_text(
        result, "If the contract is broken, the app fails closed"
    ).requirement.lower()
    # architecture-pattern selection may remain probabilistic -> Guidance
    assert by_text(
        result, "architecture pattern selection"
    ).protection_classification == guidance
    # "If a decision can be unit tested, it should be deterministic." -> Guidance
    assert by_text(
        result, "can be unit tested, it should be deterministic"
    ).protection_classification == guidance


def test_source_attribution_is_preserved():
    result = evaluate()
    docs_decisions = [
        d for d in result.decisions if d.source.file.startswith("docs/")
    ]
    assert len(docs_decisions) > 10
    for decision in docs_decisions:
        assert decision.source.file.startswith("docs/"), decision.source.file
        assert decision.source.lines, decision.source
        start, _, end = decision.source.lines.partition("-")
        if start.isdigit() and end:
            assert int(end) >= int(start) > 0
        # The requirement carries the verbatim statement material plus a
        # provenance rationale pointing back at the source file.
        assert decision.source.file in decision.requirement
        assert decision.protection_classification in (
            ProtectionClassification.REQUIRES_MODELLING,
            ProtectionClassification.GUIDANCE,
            ProtectionClassification.MNEME_READY,
            ProtectionClassification.PROTECTED,
        )
    covered_files = {d.source.file for d in docs_decisions}
    assert "docs/architecture-boundaries-base.md" in covered_files
    assert "docs/architecture-guide.md" in covered_files
    assert "docs/PRD.md" in covered_files


def test_no_partner_specific_hard_coding():
    result = evaluate()
    for decision in result.decisions:
        blob = f"{decision.id} {decision.title} {decision.requirement}".lower()
        assert "sagarika" not in blob
        assert "ai-system-architect" not in blob


def test_config_echo_is_labelled_evidence_and_does_not_dominate():
    result = evaluate()
    echoes = [d for d in result.decisions if d.title.startswith("Project Config:")]
    assert echoes, "config context row expected"
    for echo in echoes:
        assert echo.protection_classification == ProtectionClassification.GUIDANCE
        assert echo.evidence_confidence == "low"
        # Evidence-driven labelling: a config file's existence is config
        # evidence, never an architecture decision.
        assert echo.category == "config_evidence"
    # Real candidates dominate: the pseudo-decision must never again be
    # the only (or dominant) architecture row.
    architecture = result.summary.by_category.get("architecture_decision", 0)
    config = result.summary.by_category.get("config_evidence", 0)
    assert architecture > config * 5


def test_summary_counts_reconstruct_and_version_is_reported():
    result = evaluate()
    summary = result.summary
    assert summary.protection_relevant == (
        summary.protected_count + summary.mneme_ready_count
        + summary.requires_modelling_count
    )
    assert summary.guidance_count > 0
    assert result.mneme_version == version("mneme-hq")
    assert result.commit_sha == "not-applicable:directory"
    assert "pyproject.toml" in summary.sources
    assert "docs/architecture-boundaries-base.md" in summary.sources
