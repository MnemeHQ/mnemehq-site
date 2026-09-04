"""Frozen P1.2: readiness is backed by supported, serializable evidence."""
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from mneme.enforcer import assess_governability
from mneme.schemas import Decision, Rule

from app.models.protection_audit import MnemeRule, ProtectionDecision
from app.services.p12_adapter import P12DecisionInput, build_protection_decision, collect_p12_inputs
from app.services.p12_classifier import classify_protection


def decision(anti_patterns):
    return Decision(id="explicit-intent", decision="Repository dependency constraint",
                    rationale="Explicit test intent", scope=[], constraints=[],
                    anti_patterns=anti_patterns, rules=[], source_path="docs/adr/intent.md")


def render(value):
    return build_protection_decision(P12DecisionInput(
        value, assess_governability(value), value.source_path, "1-5"))


def test_supported_explicit_guardrail_is_serializable_mneme_ready():
    result = render(decision(["sqlite3"]))
    assert result.protection_classification == "Mneme-ready"
    assert result.proposed_rule.type == "FORBID_LITERAL"
    assert result.proposed_rule.pattern == "sqlite3"
    assert result.proposed_rule.description.strip()
    assert ProtectionDecision.model_validate_json(result.model_dump_json()) == result


@pytest.mark.parametrize("rule", [None, {},
    {"type": "FORBID_LITERAL", "pattern": "", "description": "Empty"},
    {"type": "FORBID_LITERAL", "pattern": "   ", "description": "Empty"},
    {"type": "FORBID_LITERAL", "pattern": "sqlite3", "description": " "},
    {"type": "UNSUPPORTED_GUESS", "pattern": "sqlite3", "description": "Not supported"},
])
def test_mneme_ready_empty_or_unsupported_guardrail_is_rejected(rule):
    payload = render(decision(["sqlite3"])).model_dump(mode="json")
    payload["proposed_rule"] = rule
    with pytest.raises(ValidationError):
        ProtectionDecision.model_validate(payload)


def test_ambiguous_deterministic_intent_requires_modelling():
    result = render(decision(["external database calls from handlers"]))
    assert result.protection_classification == "Requires modelling"
    assert result.proposed_rule is None


def test_assessment_alone_is_not_serializable_guardrail_evidence():
    assessment = assess_governability(decision(["sqlite3"]))
    assert classify_protection(assessment) == "Requires modelling"
    rule = MnemeRule(type="FORBID_LITERAL", pattern="sqlite3", description="Reject sqlite3")
    assert classify_protection(assessment, guardrail=rule) == "Mneme-ready"
    with pytest.raises(ValidationError):
        classify_protection(assessment, guardrail=True)


def test_agent_source_type_does_not_assert_guardrail_safety(tmp_path):
    inputs = collect_p12_inputs(SimpleNamespace(decisions=[]), [], [{
        "name": "AGENTS.md", "path": "AGENTS.md", "lines": "1-1",
        "content": "Never make external database calls from handlers.",
    }], [], tmp_path)
    result = build_protection_decision(inputs[0])
    assert result.protection_classification == "Requires modelling"
    assert result.proposed_rule is None


def test_single_term_strategy_uses_core_literal_not_prose():
    result = render(decision(["no postgres"]))
    assert result.protection_classification == "Mneme-ready"
    assert result.proposed_rule.pattern == "postgres"


def test_existing_explicit_typed_rule_remains_protected():
    value = decision([])
    value.rules = [Rule(type="FORBID_LITERAL", value="sqlite3")]
    result = render(value)
    assert result.protection_classification == "Protected"
    assert result.proposed_rule.pattern == "sqlite3"
