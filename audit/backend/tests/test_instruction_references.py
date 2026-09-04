"""Reference wrappers are source pointers, never P1.2 architectural decisions."""
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.models.protection_audit import ProtectionAuditResponse
from app.services.audit_service import AuditService
from app.services.p12_adapter import collect_p12_inputs, build_protection_audit_response


INTENT = "Never make external database calls from handlers."


def audit_sources(root):
    service = AuditService()
    service.repo_path = root
    instructions = [
        dict(name=p.name, path=p.relative_to(root).as_posix(),
             content=p.read_text(encoding="utf-8"), lines="1-50")
        for p in service._find_source_files() if p.name in {"CLAUDE.md", "AGENTS.md"}
    ]
    inputs = collect_p12_inputs(SimpleNamespace(decisions=[]), [], instructions, [], root)
    return build_protection_audit_response(
        "reference fixture", None, "not-applicable:directory", "test", inputs,
        [i['path'] for i in instructions],
    )


@pytest.mark.parametrize("wrapper", [
    "@AGENTS.md\n",
    "# Agent instructions\n\n@AGENTS.md\n",
    "See [instructions](AGENTS.md).",
    "Use the instructions in `AGENTS.md`.",
    "Follow AGENTS.md for all instructions.",
    "Include ./AGENTS.md",
])
def test_reference_wrapper_preserves_target_once(tmp_path, wrapper):
    (tmp_path / "AGENTS.md").write_text(INTENT, encoding="utf-8")
    before = audit_sources(tmp_path)
    (tmp_path / "CLAUDE.md").write_text(wrapper, encoding="utf-8")
    after = audit_sources(tmp_path)
    assert len(after.decisions) == 1
    assert after.decisions == before.decisions
    assert after.decisions[0].source.file == "AGENTS.md"
    assert after.decisions[0].title == INTENT
    assert all(d.source.file != "CLAUDE.md" for d in after.decisions)
    assert ProtectionAuditResponse.model_validate_json(after.model_dump_json()) == after


@pytest.mark.parametrize("wrapper", [
    "@missing/AGENTS.md", "Use the instructions in missing.md.",
    "@../outside.md", "@https://example.invalid/AGENTS.md", "@CLAUDE.md",
    "", "# Instructions\n", "Welcome to this example repository.",
])
def test_unresolved_or_non_substantive_wrapper_emits_no_decision(tmp_path, wrapper):
    (tmp_path / "CLAUDE.md").write_text(wrapper, encoding="utf-8")
    result = audit_sources(tmp_path)
    assert result.decisions == []
    assert result.summary.decisions_discovered == 0
    assert ProtectionAuditResponse.model_validate_json(result.model_dump_json()) == result


def test_ordinary_substantive_claude_keeps_intent_and_provenance(tmp_path):
    (tmp_path / "CLAUDE.md").write_text(INTENT, encoding="utf-8")
    result = audit_sources(tmp_path)
    assert len(result.decisions) == 1
    decision = result.decisions[0]
    assert decision.title == INTENT
    assert decision.requirement == INTENT + "\n\nRationale: Agent instructions from CLAUDE.md"
    assert decision.source.file == "CLAUDE.md"
    assert decision.source.lines == "1-50"
    assert decision.protection_classification == "Requires modelling"
    assert decision.proposed_rule is None


@pytest.mark.parametrize("field", ["title", "requirement"])
@pytest.mark.parametrize("empty", ["", " \n\t"])
def test_response_boundary_rejects_blank_decision_text(tmp_path, field, empty):
    (tmp_path / "CLAUDE.md").write_text(INTENT, encoding="utf-8")
    payload = audit_sources(tmp_path).model_dump(mode="json")
    payload['decisions'][0][field] = empty
    with pytest.raises(ValidationError, match="non-empty title and requirement"):
        ProtectionAuditResponse.model_validate(payload)
