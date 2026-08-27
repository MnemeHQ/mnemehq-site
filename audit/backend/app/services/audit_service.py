import os
import tempfile
import zipfile
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
from git import Repo
import yaml

from app.models.audit import (
    ArchitecturalDecision, 
    GovernanceGap, 
    AuditSummary, 
    AuditResult,
    Source,
    ProposedRule,
    Governability
)

class AuditService:
    """Service for analyzing repositories and extracting architectural decisions."""
    
    DECISION_PATTERNS = {
        'database': {
            'keywords': ['postgresql', 'postgres', 'mysql', 'sqlite', 'database', 'db'],
            'rule_type': 'FORBID_LITERAL',
            'enforceable': True,
        },
        'package_manager': {
            'keywords': ['uv', 'pip', 'poetry', 'pipenv', 'package manager'],
            'rule_type': 'REQUIRE_PATTERN',
            'enforceable': True,
        },
        'service_boundary': {
            'keywords': ['service boundary', 'must not import', 'forbidden import', 'cross-service'],
            'rule_type': 'FORBID_IMPORT',
            'enforceable': False,
        },
        'testing': {
            'keywords': ['test', 'pytest', 'unit test', 'integration test', 'coverage'],
            'rule_type': 'REQUIRE_PATTERN',
            'enforceable': True,
        },
        'linting': {
            'keywords': ['ruff', 'flake8', 'pylint', 'mypy', 'type check', 'lint'],
            'rule_type': 'REQUIRE_COMMAND',
            'enforceable': True,
        },
        'architecture': {
            'keywords': ['architecture', 'adr', 'decision record', 'architectural decision'],
            'rule_type': 'REQUIRE_PATTERN',
            'enforceable': False,
        },
        'dependency': {
            'keywords': ['dependency', 'import', 'require', 'vendor'],
            'rule_type': 'FORBID_IMPORT',
            'enforceable': True,
        },
        'security': {
            'keywords': ['secret', 'password', 'token', 'key', 'credential', 'auth'],
            'rule_type': 'FORBID_LITERAL',
            'enforceable': True,
        },
    }

    SOURCE_FILES = [
        'CLAUDE.md',
        'AGENTS.md',
        'architecture.md',
        'ARCHITECTURE.md',
        'docs/architecture.md',
        'docs/adr/',
        'pyproject.toml',
        'requirements.txt',
        'setup.py',
        'setup.cfg',
        '.github/workflows/',
        '.gitlab-ci.yml',
        'Makefile',
        'justfile',
        'Taskfile.yml',
    ]

    def __init__(self):
        self.repo_path: Optional[Path] = None

    async def analyze_repository(self, repo_url: Optional[str] = None, zip_path: Optional[str] = None, local_path: Optional[str] = None) -> AuditResult:
        """Analyze a repository and return audit results."""
        
        # Prepare repository
        if repo_url:
            self.repo_path = await self._clone_repo(repo_url)
            repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
            repo_identifier = repo_url
        elif zip_path:
            self.repo_path = await self._extract_zip(zip_path)
            repo_name = Path(zip_path).stem
            repo_identifier = f"upload:{repo_name}"
        elif local_path:
            self.repo_path = Path(local_path).resolve()
            repo_name = self.repo_path.name
            repo_identifier = f"local:{local_path}"
        else:
            raise ValueError("No repository source provided")

        try:
            # Find source files
            sources = self._find_source_files()
            
            # Extract decisions from sources
            decisions = self._extract_decisions(sources)
            
            # Classify governability
            for decision in decisions:
                self._classify_governability(decision)
            
            # Generate summary
            summary = self._generate_summary(decisions, sources)
            
            # Identify gaps
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
            if repo_url or zip_path:
                self._cleanup()

    async def _clone_repo(self, url: str) -> Path:
        """Clone a git repository to a temporary directory."""
        temp_dir = Path(tempfile.mkdtemp(prefix='mneme-audit-'))
        Repo.clone_from(url, temp_dir, depth=1)
        return temp_dir

    async def _extract_zip(self, zip_path: str) -> Path:
        """Extract a ZIP file to a temporary directory."""
        temp_dir = Path(tempfile.mkdtemp(prefix='mneme-audit-'))
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        return temp_dir

    def _cleanup(self):
        """Clean up temporary directory."""
        if self.repo_path and self.repo_path.exists():
            shutil.rmtree(self.repo_path, ignore_errors=True)

    def _find_source_files(self) -> List[Path]:
        """Find relevant source files in the repository."""
        sources = []
        
        for pattern in self.SOURCE_FILES:
            if pattern.endswith('/'):
                # Directory pattern
                dir_path = self.repo_path / pattern.rstrip('/')
                if dir_path.exists() and dir_path.is_dir():
                    for file in dir_path.rglob('*'):
                        if file.is_file() and file.suffix in ['.md', '.txt', '.yaml', '.yml', '.toml']:
                            sources.append(file)
            else:
                # File pattern (supports glob)
                for file in self.repo_path.rglob(pattern):
                    if file.is_file():
                        sources.append(file)
        
        # Deduplicate
        return list(set(sources))

    def _extract_decisions(self, sources: List[Path]) -> List[ArchitecturalDecision]:
        """Extract architectural decisions from source files."""
        decisions = []
        
        for source in sources:
            try:
                content = source.read_text(encoding='utf-8', errors='ignore')
                relative_path = source.relative_to(self.repo_path)
                
                # Parse based on file type
                if source.suffix in ['.md', '.txt']:
                    decisions.extend(self._parse_markdown(content, relative_path))
                elif source.suffix in ['.yaml', '.yml']:
                    decisions.extend(self._parse_yaml(content, relative_path))
                elif source.suffix == '.toml':
                    decisions.extend(self._parse_toml(content, relative_path))
            except Exception as e:
                print(f"Error parsing {source}: {e}")
        
        return decisions

    def _parse_markdown(self, content: str, file_path: Path) -> List[ArchitecturalDecision]:
        """Parse markdown files for architectural decisions."""
        decisions = []
        lines = content.split('\n')
        
        # Look for ADR patterns
        in_adr = False
        adr_title = ""
        adr_start = 0
        
        for i, line in enumerate(lines):
            # Detect ADR headers
            if line.startswith('# ') and ('ADR' in line.upper() or 'ARCHITECTURAL DECISION' in line.upper()):
                if in_adr and adr_title:
                    decisions.append(self._create_decision(
                        adr_title, 
                        '\n'.join(lines[adr_start:i]), 
                        file_path, 
                        f"{adr_start+1}-{i}"
                    ))
                in_adr = True
                adr_title = line[2:].strip()
                adr_start = i
            elif in_adr and line.startswith('## ') and i > adr_start:
                # Subsection within ADR
                pass
        
        # Handle last ADR
        if in_adr and adr_title:
            decisions.append(self._create_decision(
                adr_title, 
                '\n'.join(lines[adr_start:]), 
                file_path, 
                f"{adr_start+1}-{len(lines)}"
            ))
        
        # Also look for key architectural statements in any markdown
        for pattern_name, pattern_info in self.DECISION_PATTERNS.items():
            for keyword in pattern_info['keywords']:
                for i, line in enumerate(lines):
                    if keyword.lower() in line.lower() and len(line.strip()) > 20:
                        # Found a relevant line, extract context
                        context_start = max(0, i - 2)
                        context_end = min(len(lines), i + 3)
                        context = '\n'.join(lines[context_start:context_end])
                        
                        decisions.append(self._create_decision(
                            f"{pattern_name.replace('_', ' ').title()}: {line.strip()[:60]}",
                            context,
                            file_path,
                            f"{context_start+1}-{context_end}",
                            pattern_name
                        ))
        
        return decisions

    def _parse_yaml(self, content: str, file_path: Path) -> List[ArchitecturalDecision]:
        """Parse YAML files for architectural decisions."""
        decisions = []
        try:
            data = yaml.safe_load(content)
            if data:
                decisions.append(self._create_decision(
                    f"Configuration: {file_path.name}",
                    yaml.dump(data, default_flow_style=False)[:500],
                    file_path,
                    "1-50",
                    "configuration"
                ))
        except Exception:
            pass
        return decisions

    def _parse_toml(self, content: str, file_path: Path) -> List[ArchitecturalDecision]:
        """Parse TOML files for architectural decisions."""
        decisions = []
        # Simple extraction of key sections
        if '[tool.' in content or '[project' in content:
            decisions.append(self._create_decision(
                f"Project Config: {file_path.name}",
                content[:500],
                file_path,
                "1-50",
                "configuration"
            ))
        return decisions

    def _create_decision(
        self, 
        title: str, 
        content: str, 
        file_path: Path, 
        lines: str,
        pattern_type: str = "general"
    ) -> ArchitecturalDecision:
        """Create an architectural decision from extracted content."""
        
        # Determine pattern info
        pattern_info = self.DECISION_PATTERNS.get(pattern_type, {
            'rule_type': 'REQUIRE_PATTERN',
            'enforceable': False,
        })
        
        # Generate a proposed rule based on pattern
        proposed_rule = self._generate_rule(pattern_type, content)
        
        return ArchitecturalDecision(
            title=title[:100],
            summary=content[:200].replace('\n', ' ').strip(),
            requirement=content[:500],
            source=Source(file=str(file_path), lines=lines),
            governability="partial",  # Will be classified later
            appliesTo=self._infer_applies_to(pattern_type),
            proposedRule=proposed_rule,
            confidence=0.85,
        )

    def _generate_rule(self, pattern_type: str, content: str) -> ProposedRule:
        """Generate a proposed Mneme rule based on pattern type."""
        pattern_info = self.DECISION_PATTERNS.get(pattern_type, {})
        rule_type = pattern_info.get('rule_type', 'REQUIRE_PATTERN')
        
        # Extract key terms from content for pattern
        if pattern_type == 'database':
            for db in ['postgresql', 'postgres', 'mysql', 'sqlite']:
                if db in content.lower():
                    return ProposedRule(
                        type=rule_type,
                        pattern=db,
                        description=f"Enforce {db} as the required database"
                    )
        elif pattern_type == 'package_manager':
            if 'uv' in content.lower():
                return ProposedRule(
                    type=rule_type,
                    pattern='uv',
                    description="Require uv for package management"
                )
        elif pattern_type == 'dependency':
            return ProposedRule(
                type='FORBID_IMPORT',
                pattern='*',
                description="Restrict cross-service dependencies"
            )
        elif pattern_type == 'security':
            return ProposedRule(
                type='FORBID_LITERAL',
                pattern='password|secret|token|key',
                description="Forbid hardcoded secrets"
            )
        
        return ProposedRule(
            type=rule_type,
            pattern='',
            description=f"Enforce {pattern_type.replace('_', ' ')}"
        )

    def _infer_applies_to(self, pattern_type: str) -> List[str]:
        """Infer which paths the decision applies to."""
        mapping = {
            'database': ['src/**', 'migrations/**', 'alembic/**'],
            'package_manager': ['pyproject.toml', 'requirements*.txt', 'setup.py'],
            'service_boundary': ['src/**/services/**', 'src/**/api/**'],
            'testing': ['tests/**', 'test_*.py', '*_test.py'],
            'linting': ['**/*.py', 'pyproject.toml'],
            'architecture': ['docs/adr/**', 'architecture.md', 'CLAUDE.md', 'AGENTS.md'],
            'dependency': ['src/**'],
            'security': ['**/*'],
            'configuration': ['pyproject.toml', 'setup.py', 'requirements.txt'],
        }
        return mapping.get(pattern_type, ['src/**'])

    def _classify_governability(self, decision: ArchitecturalDecision):
        """Classify the governability of a decision."""
        rule_type = decision.proposedRule.type
        
        # Deterministic rules are enforceable
        enforceable_types = ['FORBID_LITERAL', 'REQUIRE_PATTERN', 'REQUIRE_COMMAND', 'FORBID_IMPORT']
        
        if rule_type in enforceable_types and decision.proposedRule.pattern:
            decision.governability = "enforceable"
        elif rule_type in enforceable_types:
            decision.governability = "partial"
        else:
            decision.governability = "guidance"

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
        import uuid
        return str(uuid.uuid4())[:8]


audit_service = AuditService()