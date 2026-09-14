"""Markdown architecture-document discovery (M0 minimum source).

Ordinary docs/ Markdown is the new candidate decision source. The semantic
gate lives in Mneme core (ADR-026 intent markers); these tests pin the
deterministic extraction behaviour and the false-positive controls:

- descriptive prose does not become a decision;
- headings alone do not become decisions;
- code fences are never decisions;
- advisory prose remains Guidance;
- deterministic architectural requirements become candidates;
- filename shape only orders candidates, never creates one;
- sample/example artefacts and user-story prose are skipped;
- statements carry source evidence (file, lines) and stable IDs.
"""
import shutil
from pathlib import Path

from app.services.markdown_discovery import (
    MAX_STATEMENTS_PER_FILE,
    MAX_STATEMENTS_TOTAL,
    discover_architecture_statements,
    assess_statement,
)


def write_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    root = tmp_path / "repo"
    for rel, text in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


def statements(root: Path):
    return discover_architecture_statements(root)


def tier_of(statement):
    return assess_statement(statement).protection_tier


def test_descriptive_prose_does_not_become_a_decision(tmp_path):
    root = write_repo(tmp_path, {"docs/notes.md": (
        "# Notes\n\n"
        "The application needs a primary relational database for persistent "
        "data storage. The service loads the system prompt and calls the "
        "model. The model returns the architecture draft as markdown.\n"
    )})
    assert statements(root) == []


def test_headings_alone_do_not_become_decisions(tmp_path):
    root = write_repo(tmp_path, {"docs/shape.md": (
        "# Architecture Boundaries\n"
        "## Deterministic requirements\n"
        "### Fail closed validation boundaries\n"
    )})
    assert statements(root) == []


def test_code_fences_are_never_decisions(tmp_path):
    root = write_repo(tmp_path, {"docs/flow.md": (
        "# Flow\n\n"
        "```bash\n"
        "deploy.sh must fail closed on missing env vars\n"
        "```\n"
    )})
    assert statements(root) == []


def test_prescriptive_requirement_becomes_candidate(tmp_path):
    root = write_repo(tmp_path, {"docs/boundaries.md": (
        "# Boundaries\n\n"
        "- Validate required fields before calling the model.\n"
        "- Fail closed if the output is missing required sections.\n"
    )})
    found = statements(root)
    assert len(found) == 2
    for statement in found:
        assert tier_of(statement) == "requires_modelling"
    assert found[0].line_start == 3
    assert found[1].line_start == 4


def test_advisory_prose_remains_guidance(tmp_path):
    root = write_repo(tmp_path, {"docs/boundaries.md": (
        "# Boundaries\n\n"
        "If a decision can be unit tested, it should be deterministic.\n"
        "Where practical, services must reject invalid input.\n"
    )})
    found = statements(root)
    assert len(found) == 2
    assert all(tier_of(s) == "guidance" for s in found)
    assert all(s.origin == "sentence" for s in found)


def test_quoted_term_ban_is_mneme_ready(tmp_path):
    root = write_repo(tmp_path, {"docs/voice.md": (
        "# Voice\n\n"
        "Generated recommendations must not use the term `seamless`.\n"
    )})
    found = statements(root)
    assert len(found) == 1
    report = assess_statement(found[0])
    assert report.protection_tier == "mneme_ready"
    assert report.mneme_guardrail == "FORBID_LITERAL: seamless"


def test_deterministic_section_labels_noun_bullets(tmp_path):
    root = write_repo(tmp_path, {"docs/boundaries.md": (
        "# Boundaries\n\n"
        "## Deterministic\n\n"
        "These should be explicit code, not model judgment.\n\n"
        "- Empty input rejection\n"
        "- Required field checks\n"
        "- Logging\n"
        "\n"
        "## Probabilistic\n\n"
        "- Architecture pattern selection\n"
        "- Memory strategy\n"
    )})
    found = statements(root)
    by_text = {s.text: s for s in found}
    assert tier_of(by_text["Deterministic: Empty input rejection"]) == "requires_modelling"
    assert tier_of(by_text["Deterministic: Required field checks"]) == "requires_modelling"
    assert tier_of(by_text["Probabilistic: Architecture pattern selection"]) == "guidance"
    assert tier_of(by_text["Probabilistic: Memory strategy"]) == "guidance"
    # "Logging" is too short to be a statement.
    assert "Deterministic: Logging" not in by_text
    # Evidence carries the section heading and the bullet's own line.
    statement = by_text["Deterministic: Empty input rejection"]
    assert statement.heading == "Deterministic"
    assert statement.lines == "7-7"
    assert statement.file == "docs/boundaries.md"


def test_table_header_rows_are_not_decisions(tmp_path):
    root = write_repo(tmp_path, {"docs/mapping.md": (
        "# Mapping\n\n"
        "| Area | Current state | Required boundary |\n"
        "|---|---|---|\n"
        "| CLI input | Deterministic | Keep deterministic |\n"
    )})
    assert statements(root) == []


def test_sample_and_example_artefacts_are_skipped(tmp_path):
    root = write_repo(tmp_path, {
        "docs/sample_output/generated.md": "Output must contain all required sections.\n",
        "docs/examples/walkthrough.md": "Never render partial output as complete.\n",
        "docs/manual-test-examples.md": "Validate required fields before calling the model.\n",
        "docs/boundaries.md": "Validate required fields before calling the model.\n",
    })
    found = statements(root)
    assert [s.file for s in found] == ["docs/boundaries.md"]


def test_user_story_voice_is_not_a_requirement(tmp_path):
    root = write_repo(tmp_path, {"docs/stories.md": (
        "# Stories\n\n"
        "As an AI Lead, I paste a use case description and get a structured "
        "architecture so I don't start from a blank page.\n"
    )})
    assert statements(root) == []


def test_filename_priority_is_order_only(tmp_path):
    root = write_repo(tmp_path, {
        "docs/zzz-late.md": "# Late\n\nWord limits must be enforced.\n",
        "docs/architecture-boundaries.md": "# Early\n\nOutput must fail closed when sections are missing.\n",
    })
    found = statements(root)
    assert [s.file for s in found] == [
        "docs/architecture-boundaries.md", "docs/zzz-late.md",
    ]
    # A priority-named file with no prescriptive content yields nothing.
    empty = write_repo(tmp_path / "2", {
        "docs/architecture-boundaries.md": "# Boundaries\n\nPlain descriptive text only.\n",
    })
    assert statements(empty) == []


def test_cross_file_duplicates_collapse_to_first_source(tmp_path):
    root = write_repo(tmp_path, {
        "docs/architecture-a.md": (
            "# A\n\n## Deterministic\n\n- Empty input rejection\n"
        ),
        "docs/architecture-b.md": (
            "# B\n\n### What is deterministic\n\n- Empty input rejection\n"
        ),
    })
    found = statements(root)
    assert len(found) == 1
    assert found[0].file == "docs/architecture-a.md"


def test_statement_ids_are_stable_and_evidenced(tmp_path):
    root = write_repo(tmp_path, {"docs/boundaries.md": (
        "# B\n\n- Validate required fields before calling the model.\n"
    )})
    first = statements(root)
    again = discover_architecture_statements(root)
    assert [s.text for s in first] == [s.text for s in again]
    assert first[0].lines == "3-3"
    assert first[0].file == "docs/boundaries.md"


def test_caps_bound_pathological_documentation(tmp_path):
    many = "\n".join(
        f"- Requirement {index} must be validated before the model call."
        for index in range(60)
    )
    root = write_repo(tmp_path, {
        "docs/one.md": f"# One\n\n{many}\n",
        "docs/two.md": f"# Two\n\n{many}\n",
        "docs/three.md": f"# Three\n\n{many}\n",
    })
    found = statements(root)
    per_file: dict[str, int] = {}
    for statement in found:
        per_file[statement.file] = per_file.get(statement.file, 0) + 1
    assert max(per_file.values()) <= MAX_STATEMENTS_PER_FILE
    assert len(found) <= MAX_STATEMENTS_TOTAL


def test_no_docs_dir_yields_nothing(tmp_path):
    root = tmp_path / "bare"
    root.mkdir()
    (root / "CLAUDE.md").write_text("Never use sqlite.\n", encoding="utf-8")
    assert statements(root) == []


class TestNoPrivateCoreSemantics:
    """ADR-028 boundary: intent interpretation goes through the public
    Mneme Core API. Importing private lexical helpers is the failure mode
    this regression pins — it caused the published-package incompatibility
    (private helpers existed only on unreleased Core)."""

    def test_discovery_layer_does_not_import_private_intent_helpers(self):
        source = (
            Path(__file__).parents[1] / "app" / "services" / "markdown_discovery.py"
        ).read_text(encoding="utf-8")
        assert "_is_prescriptive_text" not in source
        assert "_is_advisory_text" not in source
        assert "assess_decision_intent" in source

    def test_discovery_classification_goes_through_the_public_api(self, tmp_path):
        """Runtime proof: ADR-026 advisory precedence is applied by Core,
        not reproduced here — mixed wording stays advisory via the public
        verdict, and a neutral bullet under a deterministic heading still
        becomes Requires modelling through the document-structure channel."""
        root = write_repo(tmp_path, {"docs/boundaries.md": (
            "# B\n\n"
            "We should never use SQLite.\n"
            "## Deterministic\n\n"
            "- Empty input rejection\n"
        )})
        found = statements(root)
        by_text = {s.text: s for s in found}
        assert assess_statement(by_text["We should never use SQLite."]).protection_tier == "guidance"
        assert assess_statement(
            by_text["Deterministic: Empty input rejection"]
        ).protection_tier == "requires_modelling"
