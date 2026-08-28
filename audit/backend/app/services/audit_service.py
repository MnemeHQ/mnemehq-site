"""
AuditService — Repository analysis using Mneme core.

This service orchestrates:
1. Safe repository ingestion (git clone, ZIP extract, local path)
2. Evidence extraction (ADRs via Mneme import, CLAUDE.md, AGENTS.md, configs)
3. Governability assessment via MnemeAdapter (Mneme is sole authority)
4. Audit result assembly
"""
from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import List, Optional

import yaml

from app.models.audit import (
    ArchitecturalDecision,
    GovernanceGap,
    AuditSummary,
    AuditResult,
    Source,
    ProposedRule,
)
from typing import Optional as TypingOptional
from app.services.mneme_adapter import mneme_adapter, ProposedRuleInfo
from app.services.safe_extract import (
    safe_clone_repo,
    safe_extract_zip,
    safe_local_path,
    cleanup_temp_dir,
    SafeExtractionError,
)


class AuditService:
    """Service for analyzing repositories and extracting architectural decisions."""
    
    # Files that commonly contain architectural decisions
    SOURCE_FILE_PATTERNS = [
        "CLAUDE.md",
        "AGENTS.md",
        "architecture.md",
        "ARCHITECTURE.md",
        "docs/architecture.md",
        "docs/adr/",
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        "setup.py",
        "setup.cfg",
        ".github/workflows/",
        ".gitlab-ci.yml",
        "Makefile",
        "justfile",
        "Taskfile.yml",
    ]
    
    # Binary file extensions to skip
    BINARY_EXTENSIONS = {
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
        ".pdf", ".zip", ".tar", ".gz", ".tgz", ".rar",
        ".exe", ".dll", ".so", ".dylib",
        ".pyc", ".pyo", ".pyd",
        ".woff", ".woff2", ".ttf", ".eot",
        ".mp4", ".webm", ".mov",
    }

    def __init__(self):
        self.repo_path: Optional[Path] = None
        self._temp_dir: Optional[Path] = None

    async def analyze_repository(
        self,
        repo_url: Optional[str] = None,
        zip_path: Optional[str] = None,
        local_path: Optional[str] = None,
    ) -> AuditResult:
        """Analyze a repository and return audit results using Mneme core."""
        
        # Prepare repository with safe extraction
        if repo_url:
            self.repo_path = safe_clone_repo(repo_url)
            self._temp_dir = self.repo_path
            repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
            repo_identifier = repo_url
        elif zip_path:
            self.repo_path = safe_extract_zip(zip_path)
            self._temp_dir = self.repo_path
            repo_name = Path(zip_path).stem
            repo_identifier = f"upload:{repo_name}"
        elif local_path:
            self.repo_path = safe_local_path(local_path)
            repo_name = self.repo_path.name
            repo_identifier = f"local:{local_path}"
        else:
            raise ValueError("No repository source provided")

        try:
            # Load Mneme decisions from repository (ADRs via Mneme's import pipeline)
            mneme_report = mneme_adapter.load_repository(self.repo_path)
            
            # Also check for .mneme/project_memory.json
            memory_path = self.repo_path / ".mneme" / "project_memory.json"
            if memory_path.exists():
                mneme_adapter.load_memory_file(memory_path)
            
            # Build audit decisions from two sources:
            # 1. Mneme's authoritative ADR import (decisions with typed rules)
            # 2. Other architectural intent sources (CLAUDE.md, AGENTS.md, configs)
            decisions = []
            
            # Source 1: Mneme's own ADR import — these have typed rules and are authoritative
            for mneme_decision in mneme_report.decisions:
                assessment = mneme_adapter.assess_governability(mneme_decision)
                proposed = mneme_adapter.get_proposed_rules(mneme_decision)
                
                # Use actual ADR source path from Mneme
                source_file = mneme_decision.source_path if mneme_decision.source_path else f"docs/adr/{mneme_decision.id}.md"
                
                decisions.append(ArchitecturalDecision(
                    id=mneme_decision.id,
                    title=mneme_decision.decision,
                    summary=mneme_decision.rationale[:300] if mneme_decision.rationale else mneme_decision.decision[:300],
                    requirement=mneme_decision.decision + ("\n\nRationale: " + mneme_decision.rationale if mneme_decision.rationale else ""),
                    source=Source(file=source_file, lines="ADR import"),
                    governability=assessment.tier,
                    appliesTo=list(assessment.applicable_paths),  # Don't fallback to src/** — leave empty if no paths
                    proposedRule=ProposedRule(
                        type=proposed[0].type,
                        pattern=proposed[0].pattern,
                        description=proposed[0].description
                    ) if proposed else None,
                    confidence=assessment.confidence,
                ))
            
            # Source 2: Other architectural intent sources (non-ADR)
            # These are preserved as architectural intent findings but don't get manufactured rules
            sources = self._find_source_files()
            for source in sources:
                if source.suffix in [".md", ".txt"] and ("CLAUDE.md" in str(source) or "AGENTS.md" in str(source)):
                    content = source.read_text(encoding="utf-8", errors="ignore")
                    relative_path = source.relative_to(self.repo_path)
                    constraints = self._extract_constraints(content)
                    if constraints:
                        decisions.append(ArchitecturalDecision(
                            title=f"Agent Instructions: {source.name}",
                            summary="\n".join(constraints[:3]),
                            requirement="\n".join(constraints),
                            source=Source(file=str(source.relative_to(self.repo_path)), lines="1-50"),
                            governability="guidance",
                            appliesTo=[],
                            proposedRule=None,  # No deterministic rule for guidance-only findings
                            confidence=0.5,
                        ))
            
            # Source 3: Config files as architectural context (guidance only)
            for source in sources:
                if source.suffix in [".toml", ".yaml", ".yml"] or source.name in ["requirements.txt", "requirements-dev.txt", "setup.py", "setup.cfg", "Makefile", "justfile", "Taskfile.yml"]:
                    content = source.read_text(encoding="utf-8", errors="ignore")
                    decisions.append(ArchitecturalDecision(
                        title=f"Project Config: {source.name}",
                        summary=content[:300].replace("\n", " ").strip(),
                        requirement=content[:1000],
                        source=Source(file=str(source.relative_to(self.repo_path)), lines="1-100"),
                        governability="guidance",
                        appliesTo=[],
                        proposedRule=None,  # No deterministic rule for config files
                        confidence=0.4,
                    ))
            
            # Deduplicate by title
            decisions = self._deduplicate_decisions(decisions)
            
            # Generate summary (pass sources for accurate source list)
            summary = self._generate_summary(decisions, sources)
            
            # Identify governance gaps
            gaps = self._identify_gaps(decisions)
            
            return AuditResult(
                id=self._generate_audit_id(),
                repository=repo_identifier,
                repositoryUrl=repo_url,
                summary=summary,
                decisions=decisions,
                gaps=gaps,
            )
        finally:
            # Cleanup temp directory if we created one
            if self._temp_dir and (repo_url or zip_path):
                cleanup_temp_dir(self._temp_dir)

    def _find_source_files(self) -> List[Path]:
        """Find relevant source files in the repository."""
        sources = []
        
        for pattern in self.SOURCE_FILE_PATTERNS:
            if pattern.endswith("/"):
                # Directory pattern
                dir_path = self.repo_path / pattern.rstrip("/")
                if dir_path.exists() and dir_path.is_dir():
                    for file in dir_path.rglob("*"):
                        if file.is_file() and not self._is_binary_file(file):
                            sources.append(file)
            else:
                # File pattern (supports glob)
                for file in self.repo_path.rglob(pattern):
                    if file.is_file() and not self._is_binary_file(file):
                        sources.append(file)
        
        # Deduplicate
        return list(set(sources))
    
    def _is_binary_file(self, path: Path) -> bool:
        """Quick binary check by extension and content sample."""
        if path.suffix.lower() in self.BINARY_EXTENSIONS:
            return True
        try:
            sample = path.read_bytes()[:8192]
            if b"\x00" in sample:
                return True
            non_ascii = sum(1 for b in sample if b > 127)
            if sample and (non_ascii / len(sample)) > 0.3:
                return True
        except Exception:
            pass
        return False

    def _deduplicate_decisions(self, decisions: List[ArchitecturalDecision]) -> List[ArchitecturalDecision]:
        """Remove duplicate decisions based on title similarity."""
        seen = set()
        unique = []
        for d in decisions:
            key = d.title.lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(d)
        return unique

    def _extract_constraints(self, text: str) -> list:
        """Extract lines that look like constraints."""
        constraints = []
        for line in text.split("\n"):
            line = line.strip()
            if len(line) < 20:
                continue
            line_lower = line.lower()
            if any(p in line_lower for p in ["must", "must not", "shall", "shall not", 
                                              "required", "forbidden", "prohibited",
                                              "use ", "avoid ", "prefer ", "do not ",
                                              "only ", "never ", "always ",
                                              "enforce", "require", "constrain",
                                              "no "]):
                constraints.append(line)
        return constraints

    def _generate_summary(self, decisions: List[ArchitecturalDecision], sources: List[Path] = None) -> AuditSummary:
        """Generate audit summary."""
        enforceable = sum(1 for d in decisions if d.governability == "enforceable")
        partial = sum(1 for d in decisions if d.governability == "partial")
        guidance = sum(1 for d in decisions if d.governability == "guidance")
        total = len(decisions)
        
        coverage = 0
        if total > 0:
            coverage = int(((enforceable + partial * 0.5) / total) * 100)
        
        source_names = [str(s.relative_to(self.repo_path)) for s in sources] if sources else []
        
        return AuditSummary(
            totalDecisions=total,
            enforceable=enforceable,
            partial=partial,
            guidance=guidance,
            coverage=coverage,
            sources=list(set(source_names)),
        )

    def _identify_gaps(self, decisions: List[ArchitecturalDecision]) -> List[GovernanceGap]:
        """Identify governance gaps."""
        gaps = []
        
        for decision in decisions:
            if decision.governability == "guidance":
                gaps.append(GovernanceGap(
                    decision=decision.title,
                    reason="The decision describes intent but does not specify a machine-testable constraint.",
                    suggestedNextStep="Define specific prohibited patterns, required commands, or allowed/forbidden dependencies that can be checked automatically."
                ))
            elif decision.governability == "partial":
                gaps.append(GovernanceGap(
                    decision=decision.title,
                    reason="The decision has some testable aspects but lacks complete specification for deterministic enforcement.",
                    suggestedNextStep="Add specific patterns, file paths, or commands that Mneme can verify programmatically."
                ))
        
        return gaps

    def _generate_audit_id(self) -> str:
        """Generate a short audit ID."""
        return str(uuid.uuid4())[:8]


audit_service = AuditService()