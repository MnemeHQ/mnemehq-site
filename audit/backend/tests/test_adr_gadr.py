import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.audit_service import audit_service

import pytest


@pytest.mark.asyncio
async def test_adr_gadr():
    """Test GADR fixture - should produce 3 guidance findings with correct provenance (0000, 0001, 0002)."""
    fixture_path = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures" / "adr-gadr"
    result = await audit_service.analyze_repository(local_path=str(fixture_path))
    
    print(f"Total: {result.summary.totalDecisions}")
    print(f"Enforceable: {result.summary.enforceable}")
    print(f"Partial: {result.summary.partial}")
    print(f"Guidance: {result.summary.guidance}")
    for d in result.decisions:
        print(f"  [{d.governability}] {d.title}")
        print(f"    Source: {d.source.file} (Lines {d.source.lines})")
        if d.proposedRule:
            print(f"  Proposed rule: {d.proposedRule.type} \"{d.proposedRule.pattern}\"")
        else:
            print(f"  Proposed rule: None (no deterministic rule)")
        print(f"    Confidence: {d.confidence}")
    print("Sources:", result.summary.sources)
    print("Gaps:", len(result.gaps))
    
    # Count assertions - 3 guidance (0000, 0001, 0002)
    assert result.summary.enforceable == 0, f"Expected 0 enforceable, got {result.summary.enforceable}"
    assert result.summary.partial == 0, f"Expected 0 partial, got {result.summary.partial}"
    assert result.summary.guidance == 3, f"Expected 3 guidance, got {result.summary.guidance}"
    
    # Exactly 3 decisions from GADR fixture (0000, 0001, 0002)
    assert len(result.decisions) == 3, f"Expected 3 decisions, got {len(result.decisions)}"
    
    # Find decisions by title
    decision_by_title = {d.title: d for d in result.decisions}
    
    # GADR 0000 - Use Markdown Architectural Decision Records
    d0000 = decision_by_title.get("Use Markdown Architectural Decision Records")
    assert d0000 is not None, "GADR 0000 decision not found"
    assert d0000.governability == "guidance"
    assert d0000.proposedRule is None
    assert d0000.confidence == 0.5
    # Should extract from ## Decision section (lines 14-18 in fixture)
    assert d0000.source.lines != "unknown", f"GADR 0000 should have exact provenance, got {d0000.source.lines}"
    start, end = map(int, d0000.source.lines.split("-"))
    assert start <= end, f"GADR 0000 source range invalid: {d0000.source.lines}"
    assert "Markdown files" in d0000.requirement or "ADR" in d0000.requirement
    
    # GADR 0001 - Use GADR as Name for Generalized ADRs
    d0001 = decision_by_title.get("Use GADR As Name For Generalized Adrs") or \
            decision_by_title.get("Use GADR as Name for Generalized ADRs")
    assert d0001 is not None, "GADR 0001 decision not found"
    assert d0001.governability == "guidance"
    assert d0001.proposedRule is None
    assert d0001.confidence == 0.5
    assert d0001.source.lines != "unknown", f"GADR 0001 should have exact provenance, got {d0001.source.lines}"
    start, end = map(int, d0001.source.lines.split("-"))
    assert start <= end, f"GADR 0001 source range invalid: {d0001.source.lines}"
    assert "GADR" in d0001.requirement
    
    # GADR 0002 - Decision Drivers Structure
    d0002 = decision_by_title.get("Use Decision Drivers Structure")
    assert d0002 is not None, "GADR 0002 decision not found"
    assert d0002.governability == "guidance"
    assert d0002.proposedRule is None
    assert d0002.confidence == 0.5
    assert d0002.source.lines != "unknown", f"GADR 0002 should have exact provenance, got {d0002.source.lines}"
    start, end = map(int, d0002.source.lines.split("-"))
    assert start <= end, f"GADR 0002 source range invalid: {d0002.source.lines}"
    # Should extract from ## Decision Outcome, NOT ## Decision Drivers
    assert "Decision Outcome" in d0002.requirement or "dedicated" in d0002.requirement or "separate" in d0002.requirement
    # The text mentions "Decision Drivers" as a phrase but it's from Decision Outcome section
    # Verify it's the Decision Outcome text, not the Decision Drivers bullet points
    assert "We will use a dedicated" in d0002.requirement
    assert "forces" in d0002.requirement and "influencing" in d0002.requirement
    # Should NOT contain the bullet points from Decision Drivers section
    assert "Driver 1" not in d0002.requirement
    assert "Driver 2" not in d0002.requirement
    
    # Sources should include the ADR files (index and template are skipped)
    sources = result.summary.sources
    assert any("0000-use-markdown" in s for s in sources)
    assert any("0001-use-gadr" in s for s in sources)
    assert any("0002-decision-drivers" in s for s in sources)
    # index.md and template.md should NOT be in sources as decisions
    # (they may appear in sources list from Mneme scan but not as loose ADR decisions)
    
    print("All GADR assertions passed!")


@pytest.mark.asyncio
async def test_decision_drivers_not_matched():
    """Test that 'Decision Drivers' heading is NOT treated as a Decision section."""
    # Create a temporary fixture with Decision Drivers structure
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        adr_dir = repo_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        
        # Write ADR with Decision Drivers, Considered Options, Decision Outcome
        adr_content = """# Test ADR with Decision Drivers

## Status

Accepted

## Decision Drivers

- Driver 1: We need performance
- Driver 2: We need scalability

## Considered Options

- Option A: Do nothing
- Option B: Implement caching

## Decision Outcome

We will implement a Redis caching layer to improve response times.

## Consequences

- Added dependency on Redis
- Improved latency
"""
        (adr_dir / "0003-test-decision-drivers.md").write_text(adr_content)
        
        result = await audit_service.analyze_repository(local_path=str(repo_path))
        
        print(f"Total: {result.summary.totalDecisions}")
        print(f"Enforceable: {result.summary.enforceable}")
        print(f"Partial: {result.summary.partial}")
        print(f"Guidance: {result.summary.guidance}")
        for d in result.decisions:
            print(f"  [{d.governability}] {d.title}")
            print(f"    Source: {d.source.file} (Lines {d.source.lines})")
            print(f"    Requirement: {d.requirement[:200]}")
        
        # Should find exactly 1 decision from the Decision Outcome section
        assert result.summary.totalDecisions == 1, f"Expected 1 decision, got {result.summary.totalDecisions}"
        assert result.summary.guidance == 1
        
        decision = result.decisions[0]
        # The requirement text should come from "Decision Outcome" NOT "Decision Drivers"
        assert "Redis" in decision.requirement, f"Expected Decision Outcome text, got: {decision.requirement}"
        assert "Driver" not in decision.requirement, f"Should not contain Decision Drivers text: {decision.requirement}"
        assert "caching" in decision.requirement.lower()
        
        # Provenance should point to Decision Outcome section
        assert decision.source.lines != "unknown"
        start, end = map(int, decision.source.lines.split("-"))
        assert start <= end, f"Invalid source range: {decision.source.lines}"
        
        print("Decision Drivers test passed!")


@pytest.mark.asyncio
async def test_context_decision_ordering():
    """Test Context -> Decision -> Consequences ordering is handled correctly."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        adr_dir = repo_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        
        # Context first, then Decision, then Consequences
        adr_content = """# Test Context First

## Context

This is the context section explaining the problem.

## Decision

We will use PostgreSQL as our primary database.

## Consequences

- ACID compliance
- Mature ecosystem
"""
        (adr_dir / "0004-context-first.md").write_text(adr_content)
        
        result = await audit_service.analyze_repository(local_path=str(repo_path))
        
        assert result.summary.totalDecisions == 1
        decision = result.decisions[0]
        assert "PostgreSQL" in decision.requirement
        # The requirement includes rationale (Context section) by design
        # The key is that the Decision section content is present
        assert "primary database" in decision.requirement
        print("Context -> Decision ordering test passed!")


@pytest.mark.asyncio
async def test_decision_at_eof():
    """Test decision section that goes to EOF (no terminating heading)."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        adr_dir = repo_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        
        # Decision at end of file, no trailing heading
        adr_content = """# Test EOF Decision

## Context

Problem statement here.

## Decision

We will use Kafka for event streaming.
This decision continues to the end of file.
"""
        (adr_dir / "0005-eof-decision.md").write_text(adr_content)
        
        result = await audit_service.analyze_repository(local_path=str(repo_path))
        
        assert result.summary.totalDecisions == 1
        decision = result.decisions[0]
        assert "Kafka" in decision.requirement
        assert "event streaming" in decision.requirement
        # Should have valid provenance
        assert decision.source.lines != "unknown"
        start, end = map(int, decision.source.lines.split("-"))
        assert start <= end
        print("Decision at EOF test passed!")


@pytest.mark.asyncio
async def test_decision_status_termination():
    """Test Decision -> Status termination."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        adr_dir = repo_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        
        adr_content = """# Test Decision Status

## Decision

We will use Docker for containerization.

## Status

Accepted
"""
        (adr_dir / "0006-decision-status.md").write_text(adr_content)
        
        result = await audit_service.analyze_repository(local_path=str(repo_path))
        
        assert result.summary.totalDecisions == 1
        decision = result.decisions[0]
        assert "Docker" in decision.requirement
        assert decision.source.lines != "unknown"
        start, end = map(int, decision.source.lines.split("-"))
        assert start <= end
        print("Decision -> Status termination test passed!")


@pytest.mark.asyncio
async def test_empty_decision_rejected():
    """Test that empty decision body produces no finding."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        adr_dir = repo_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        
        # Decision heading but no content
        adr_content = """# Test Empty Decision

## Context

Some context.

## Decision

## Status

Accepted
"""
        (adr_dir / "0007-empty-decision.md").write_text(adr_content)
        
        result = await audit_service.analyze_repository(local_path=str(repo_path))
        
        # Should NOT produce a decision for empty decision body
        assert result.summary.totalDecisions == 0, f"Expected 0 decisions for empty decision, got {result.summary.totalDecisions}"
        print("Empty decision rejected test passed!")


@pytest.mark.asyncio
async def test_canonical_mneme_excluded():
    """Test that canonical Mneme ADRs (with id/status frontmatter) are excluded from loose parsing.
    
    Note: This tests that the loose parser correctly identifies and skips canonical Mneme ADRs.
    The Mneme core import handles valid canonical ADRs; the loose parser should not double-count them.
    """
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        adr_dir = repo_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        
        # Valid canonical Mneme ADR with all required frontmatter fields
        adr_content = """---
id: ADR-001
status: accepted
priority: normal
date: 2024-01-15
scope: architecture
title: Canonical Mneme ADR
---

# Canonical Mneme ADR

## Decision

This is a valid canonical ADR handled by Mneme core.
"""
        (adr_dir / "ADR-001-canonical.md").write_text(adr_content)
        
        # Also add a loose ADR to ensure we can still parse those
        loose_adr = """# Loose ADR

## Decision

This is a loose ADR that should be found.
"""
        (adr_dir / "0002-loose.md").write_text(loose_adr)
        
        result = await audit_service.analyze_repository(local_path=str(repo_path))
        
        # The canonical ADR should appear via Mneme import (enforceable/partial/guidance with proposedRule)
        # The loose ADR should appear via loose parsing (guidance, no proposedRule, confidence=0.5)
        # Deduplication by file path should prevent double-counting
        
        # Find loose decisions (confidence=0.5, no proposedRule)
        loose_decisions = [d for d in result.decisions if d.confidence == 0.5 and d.proposedRule is None]
        loose_titles = [d.title for d in loose_decisions]
        assert "Loose ADR" in loose_titles, f"Expected loose ADR in results: {loose_titles}"
        
        # Canonical ADR should NOT appear as a loose decision
        canonical_loose = [d for d in loose_decisions if "Canonical" in d.title]
        assert len(canonical_loose) == 0, f"Canonical ADR should not appear as loose: {canonical_loose}"
        
        print("Canonical Mneme ADR excluded from loose parsing test passed!")


@pytest.mark.asyncio
async def test_index_template_readme_skipped():
    """Test that index.md, template.md, README.md are skipped."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        adr_dir = repo_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        
        # Create index.md, template.md, README.md with decision headings
        (adr_dir / "index.md").write_text("""# Index

## Decision

This should be skipped.
""")
        (adr_dir / "template.md").write_text("""# Template

## Decision

This should be skipped.
""")
        (adr_dir / "README.md").write_text("""# README

## Decision

This should be skipped.
""")
        # Valid ADR
        (adr_dir / "0008-valid.md").write_text("""# Valid ADR

## Decision

This should be found.
""")
        
        result = await audit_service.analyze_repository(local_path=str(repo_path))
        
        assert result.summary.totalDecisions == 1, f"Expected 1 decision, got {result.summary.totalDecisions}"
        assert result.decisions[0].title == "Valid ADR"
        print("Index/template/README skipped test passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])