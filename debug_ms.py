import asyncio
from pathlib import Path
import sys
sys.path.insert(0, 'C:/dev/mnemehq-site/audit/backend')
from app.services.audit_service import audit_service
from app.services.loose_adr_parser import find_loose_adrs

async def test():
    # Clone the Microsoft repo locally first, then test
    repo_path = Path('C:/temp/microsoft-agent-governance-toolkit')
    if not repo_path.exists():
        print("Repo not found locally")
        return
    
    loose_adrs = find_loose_adrs(repo_path)
    for adr in loose_adrs[:5]:
        constraints = audit_service._extract_constraints(adr.decision_text)
        anti_patterns = [c for c in constraints if c.lower().startswith(("no ", "avoid ", "never ", "prohibit", "forbid"))]
        print(f"\n{adr.title}:")
        print(f"  Decision text (first 200): {adr.decision_text[:200]}")
        print(f"  Constraints ({len(constraints)}): {constraints}")
        print(f"  Anti-patterns ({len(anti_patterns)}): {anti_patterns}")

asyncio.run(test())