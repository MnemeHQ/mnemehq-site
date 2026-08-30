import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.audit_service import audit_service

import pytest

@pytest.mark.asyncio
async def test_adr_gadr():
    fixture_path = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures" / "adr-gadr"
    result = await audit_service.analyze_repository(local_path=str(fixture_path))
    print(f"Total: {result.summary.totalDecisions}")
    print(f"Enforceable: {result.summary.enforceable}")
    print(f"Partial: {result.summary.partial}")
    print(f"Guidance: {result.summary.guidance}")
    for d in result.decisions:
        print(f"  [{d.governability}] {d.title}")
        if d.proposedRule:
            print(f"  Proposed rule: {d.proposedRule.type} \"{d.proposedRule.pattern}\"")
        else:
            print(f"  Proposed rule: None (no deterministic rule)")
        print(f"    Confidence: {d.confidence}")
    print("Sources:", result.summary.sources)
    print("Gaps:", len(result.gaps))
    assert result.summary.enforceable == 0
    assert result.summary.partial == 0
    assert result.summary.guidance == 2
    print("All assertions passed!")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])