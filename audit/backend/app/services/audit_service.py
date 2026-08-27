"""
AuditService — Repository analysis using Mneme core.

This service orchestrates:
1. Safe repository ingestion (git clone, ZIP extract, local path)
2. Evidence extraction (ADRs, CLAUDE.md, AGENTS.md, configs)
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
            # Load Mneme decisions from repository (ADRs, memory file)
            mneme_report = mneme_adapter.load_repository(self.repo_path)
            
            # Also check for .mneme/project_memory.json
            memory_path = self.repo_path / ".mneme" / "project_memory.json"
            if memory_path.exists():
                mneme_adapter.load_memory_file(memory_path)
            
            # Find all source files containing architectural intent
            sources = self._find_source_files()
            
            # Extract decisions from sources
            decisions = self._extract_decisions(sources)
            
            # Assess governability via MnemeAdapter (Mneme is sole authority)
            for decision in decisions:
                self._assess_via_mneme(decision)
            
            # Generate summary
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

    def _extract_decisions(self, sources: List[Path]) -> List[ArchitecturalDecision]:
        """Extract architectural decisions from source files."""
        decisions = []
        
        for source in sources:
            try:
                content = source.read_text(encoding="utf-8", errors="ignore")
                relative_path = source.relative_to(self.repo_path)
                
                # Parse based on file type
                if source.suffix in [".md", ".txt"]:
                    decisions.extend(self._parse_markdown(content, relative_path))
                elif source.suffix in [".yaml", ".yml"]:
                    decisions.extend(self._parse_yaml(content, relative_path))
                elif source.suffix == ".toml":
                    decisions.extend(self._parse_toml(content, relative_path))
            except Exception:
                # Never log source contents - hostile input safety
                pass
        
        # Deduplicate by title similarity
        return self._deduplicate_decisions(decisions)

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

    def _parse_markdown(self, content: str, file_path: Path) -> List[ArchitecturalDecision]:
        """Parse markdown files for architectural decisions."""
        decisions = []
        lines = content.split("\n")
        
        # Look for ADR patterns - these are the primary decisions
        in_adr = False
        adr_title = ""
        adr_start = 0
        
        for i, line in enumerate(lines):
            if line.startswith("# ") and ("ADR" in line.upper() or "ARCHITECTURAL DECISION" in line.upper()):
                if in_adr and adr_title:
                    decisions.append(self._create_decision_from_context(
                        adr_title, 
                        "\n".join(lines[adr_start:i]), 
                        file_path, 
                        f"{adr_start+1}-{i}"
                    ))
                in_adr = True
                adr_title = line[2:].strip()
                adr_start = i
        
        # Handle last ADR
        if in_adr and adr_title:
            decisions.append(self._create_decision_from_context(
                adr_title, 
                "\n".join(lines[adr_start:]), 
                file_path, 
                f"{adr_start+1}-{len(lines)}"
            ))
        
        # For non-ADR markdown (CLAUDE.md, AGENTS.md), only extract if they have
        # explicit constraint language, and only create ONE decision per file
        if not in_adr and ("CLAUDE.md" in str(file_path) or "AGENTS.md" in str(file_path)):
            constraints = self._extract_constraints(content)
            if constraints:
                decisions.append(self._create_decision_from_context(
                    f"Agent Instructions: {file_path.name}",
                    "\n".join(constraints[:5]),
                    file_path,
                    "1-50",
                    pattern_type="agent_instructions"
                ))
        
        return decisions

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

    def _parse_yaml(self, content: str, file_path: Path) -> List[ArchitecturalDecision]:
        """Parse YAML files for architectural decisions."""
        decisions = []
        try:
            data = yaml.safe_load(content)
            if data:
                decisions.append(self._create_decision_from_context(
                    f"Configuration: {file_path.name}",
                    yaml.dump(data, default_flow_style=False)[:1000],
                    file_path,
                    "1-100",
                    pattern_type="configuration"
                ))
        except Exception:
            pass
        return decisions

    def _parse_toml(self, content: str, file_path: Path) -> List[ArchitecturalDecision]:
        """Parse TOML files for architectural decisions."""
        decisions = []
        if "[tool." in content or "[project" in content:
            decisions.append(self._create_decision_from_context(
                f"Project Config: {file_path.name}",
                content[:1000],
                file_path,
                "1-100",
                pattern_type="configuration"
            ))
        return decisions

    def _create_decision_from_context(
        self,
        title: str,
        content: str,
        file_path: Path,
        lines: str,
        pattern_type: str = "general"
    ) -> ArchitecturalDecision:
        """Create an architectural decision from extracted context."""
        return ArchitecturalDecision(
            title=title[:120],
            summary=content[:300].replace("\n", " ").strip(),
            requirement=content[:1000],
            source=Source(file=str(file_path), lines=lines),
            governability="partial",  # Will be assessed by Mneme
            appliesTo=[],
            proposedRule=ProposedRule(
                type="REQUIRE_PATTERN",
                pattern="",
                description=f"Extracted from {pattern_type}"
            ),
            confidence=0.8,
        )

    def _assess_via_mneme(self, decision: ArchitecturalDecision) -> None:
        """
        Assess governability using MnemeAdapter.
        
        This is where Mneme becomes the sole authority on governability.
        """
        from mneme.schemas import Decision as MnemeDecision, Rule as MnemeRule
        
        # Extract potential rules from the requirement text
        rules = self._extract_mneme_rules(decision.requirement)
        
        mneme_decision = MnemeDecision(
            id=f"audit_{decision.id}",
            decision=decision.title,
            rationale=decision.summary,
            scope=self._infer_scope(decision.requirement),
            constraints=self._extract_constraints(decision.requirement),
            anti_patterns=self._extract_anti_patterns(decision.requirement),
            rules=rules,
            source_path=decision.source.file,
        )
        
        # Get Mneme's authoritative assessment
        assessment = mneme_adapter.assess_governability(mneme_decision)
        
        # Update the audit decision with Mneme's verdict
        if assessment.tier == "enforceable":
            decision.governability = "enforceable"
        elif assessment.tier == "partial":
            decision.governability = "partial"
        else:
            decision.governability = "guidance"
        
        decision.appliesTo = list(assessment.applicable_paths) or ["src/**"]
        decision.confidence = assessment.confidence
        
        # Use Mneme's proposed rules
        proposed = mneme_adapter.get_proposed_rules(mneme_decision)
        if proposed:
            decision.proposedRule = ProposedRule(
                type=proposed[0].type,
                pattern=proposed[0].pattern,
                description=proposed[0].description,
            )

    def _extract_mneme_rules(self, text: str) -> list:
        """Extract FORBID_LITERAL rules from text."""
        from mneme.schemas import Rule
        rules = []
        
        for db in ["postgresql", "postgres", "mysql", "sqlite"]:
            if db in text.lower():
                rules.append(Rule(type="FORBID_LITERAL", value=db))
        
        for pm in ["uv", "pip", "poetry", "pipenv"]:
            if f"must use {pm}" in text.lower() or f"use {pm} for" in text.lower():
                rules.append(Rule(type="FORBID_LITERAL", value=pm))
        
        return rules

    def _infer_scope(self, text: str) -> list:
        """Infer scope from text."""
        scope = []
        if any(db in text.lower() for db in ["database", "postgres", "mysql", "sqlite"]):
            scope.append("storage")
        if any(pm in text.lower() for pm in ["package", "uv", "pip", "poetry"]):
            scope.append("dependencies")
        if "service" in text.lower() and "boundary" in text.lower():
            scope.append("architecture")
        return scope or ["general"]

    def _extract_constraints(self, text: str) -> list:
        """Extract 'no X' style constraints from text (handles markdown lists)."""
        constraints = []
        for line in text.split("\n"):
            line = line.strip().lower()
            # Handle markdown list items: "- no X", "* no X", "1. no X"
            clean_line = line.lstrip("- *0123456789.").strip()
            if clean_line.startswith("no ") or "must not" in clean_line or "forbidden" in clean_line:
                constraints.append(clean_line)
        return constraints[:5]

    def _extract_anti_patterns(self, text: str) -> list:
        """Extract anti-patterns from text."""
        patterns = []
        text_lower = text.lower()
        if "orm" in text_lower and ("avoid" in text_lower or "not" in text_lower):
            patterns.append("introduce ORM")
        if "migration" in text_lower and ("avoid" in text_lower or "not" in text_lower):
            patterns.append("add migration layer")
        return patterns

    def _generate_summary(self, decisions: List[ArchitecturalDecision], sources: List[Path]) -> AuditSummary:
        """Generate audit summary."""
        enforceable = sum(1 for d in decisions if d.governability == "enforceable")
        partial = sum(1 for d in decisions if d.governability == "partial")
        guidance = sum(1 for d in decisions if d.governability == "guidance")
        total = len(decisions)
        
        coverage = 0
        if total > 0:
            coverage = int(((enforceable + partial * 0.5) / total) * 100)
        
        source_names = [str(s.relative_to(self.repo_path)) for s in sources]
        
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