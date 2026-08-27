#!/usr/bin/env python3
"""
Vertical-slice test for the Architecture Audit Workspace.

Tests the full path:
fixture → discovery → extraction → Mneme adapter → audit response → expected evidence + verdicts

Fixture repo is designed to yield:
- 1 enforceable (ADR-001: FORBID_LITERAL sqlite, mysql)
- 1 partial (ADR-002: "no pip install", "no poetry" constraints)
- 1 guidance-only (ADR-003: service boundaries, no mechanical rules)
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from audit.backend.app.services.audit_service import audit_service


async def test_vertical_slice():
    """Run the full audit pipeline on the fixture repo."""
    fixture_path = Path(__file__).parent / "fixtures" / "audit-repo"
    
    print(f"Testing with fixture: {fixture_path}")
    print("=" * 60)
    
    # Run audit
    result = await audit_service.analyze_repository(local_path=str(fixture_path))
    
    # Print results
    print(f"\nAudit ID: {result.id}")
    print(f"Repository: {result.repository}")
    print(f"\nSummary:")
    print(f"  Total Decisions: {result.summary.totalDecisions}")
    print(f"  Enforceable: {result.summary.enforceable}")
    print(f"  Partial: {result.summary.partial}")
    print(f"  Guidance: {result.summary.guidance}")
    print(f"  Coverage: {result.summary.coverage}%")
    print(f"  Sources: {result.summary.sources}")
    
    print(f"\nDecisions:")
    for d in result.decisions:
        print(f"  [{d.governability.upper()}] {d.title}")
        print(f"    Source: {d.source.file} (lines {d.source.lines})")
        print(f"    Applies to: {d.appliesTo}")
        print(f"    Proposed rule: {d.proposedRule.type} \"{d.proposedRule.pattern}\"")
        print(f"    Confidence: {d.confidence}")
        print()
    
    print(f"Governance Gaps:")
    for g in result.gaps:
        print(f"  - {g.decision}")
        print(f"    Reason: {g.reason}")
        print(f"    Next step: {g.suggestedNextStep}")
        print()
    
    # Assertions - the fixture yields:
    # - 1 enforceable (ADR-001: FORBID_LITERAL sqlite, mysql)
    # - 1 partial (ADR-002: "no pip install", "no poetry" constraints)
    # - 2 guidance (ADR-003: service boundaries; pyproject.toml: config)
    assert result.summary.enforceable == 1, f"Expected 1 enforceable, got {result.summary.enforceable}"
    assert result.summary.partial == 1, f"Expected 1 partial, got {result.summary.partial}"
    assert result.summary.guidance == 2, f"Expected 2 guidance, got {result.summary.guidance}"
    
    # Verify specific decisions
    enforceable_dec = next(d for d in result.decisions if d.governability == "enforceable")
    assert "database" in enforceable_dec.title.lower() or "sqlite" in enforceable_dec.requirement.lower()
    assert enforceable_dec.proposedRule.type == "FORBID_LITERAL"
    
    partial_dec = next(d for d in result.decisions if d.governability == "partial")
    assert "package" in partial_dec.title.lower() or "pip" in partial_dec.requirement.lower()
    assert partial_dec.proposedRule.type in ("REQUIRE_PATTERN", "FORBID_LITERAL")
    
    guidance_decisions = [d for d in result.decisions if d.governability == "guidance"]
    assert any("service" in d.title.lower() or "boundar" in d.requirement.lower() for d in guidance_decisions)
    assert any("config" in d.title.lower() or "pyproject" in d.title.lower() for d in guidance_decisions)
    
    print("=" * 60)
    print("✅ ALL ASSERTIONS PASSED")
    print("Vertical slice test successful!")
    
    return result


if __name__ == "__main__":
    asyncio.run(test_vertical_slice())