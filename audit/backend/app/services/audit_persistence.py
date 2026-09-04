"""
Audit persistence service for Mneme Audit M1 with P1.2 Architecture Protection.

Orchestrates the P1.2 audit adapter with M1 persistence:
- Run P1.2 audit (ephemeral or saved)
- Save audit to persistent storage
- Manage project lifecycle
- Re-audit against new commit
- Baseline assignment

Key principle: The P1.2 evaluator (mneme.audit/v1) is the canonical source.
M1 adds identity, history, provenance, and comparison around it.
"""
from __future__ import annotations

from datetime import datetime
from importlib.metadata import version
from git import Repo, InvalidGitRepositoryError, NoSuchPathError
from starlette.concurrency import run_in_threadpool
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Project,
    Audit,
    ProjectLifecycle,
    AuditStatus,
    AuditTriggerType,
)
from app.repositories import (
    ProjectRepository,
    AuditRepository,
    ContactRepository,
    ProjectContactRepository,
)
from app.services.p12_adapter import (
    build_protection_audit_response,
    collect_p12_inputs,
    ProtectionAuditResponse,
)
from app.services.audit_service import audit_service
from app.services.mneme_adapter import MnemeAdapter
from app.services.loose_adr_parser import find_loose_adrs
from app.services.safe_extract import (
    safe_clone_repo,
    safe_extract_zip,
    safe_local_path,
    cleanup_temp_dir,
    SafeExtractionError,
)
from app.core.config import settings


class AuditPersistenceService:
    """
    Service for running and persisting P1.2 Architecture Protection audits.

    Key principle: The P1.2 evaluator produces mneme.audit/v1 responses.
    M1 adds identity, history, provenance, and comparison around it.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.projects = ProjectRepository(session)
        self.audits = AuditRepository(session)
        self.contacts = ContactRepository(session)
        self.project_contacts = ProjectContactRepository(session)

    async def run_ephemeral_audit(
        self,
        repository_url: Optional[str] = None,
        zip_path: Optional[str] = None,
        local_path: Optional[str] = None,
    ) -> ProtectionAuditResponse:
        """
        Run a P1.2 audit without persisting.

        Returns the complete mneme.audit/v1 response.
        """
        return await self._run_p12_audit(
            repository_url=repository_url,
            zip_path=zip_path,
            local_path=local_path,
        )

    async def run_ephemeral_legacy_audit(
        self,
        repository_url: Optional[str] = None,
        zip_path: Optional[str] = None,
        local_path: Optional[str] = None,
    ):
        """
        Run a legacy M0.1 audit without persisting (backward compatibility).

        This preserves the existing anonymous/ephemeral Audit experience.
        """
        return await audit_service.analyze_repository(
            repo_url=repository_url,
            zip_path=zip_path,
            local_path=local_path,
        )

    async def run_and_save_audit(
        self,
        project_id: UUID,
        repository_url: Optional[str] = None,
        zip_path: Optional[str] = None,
        local_path: Optional[str] = None,
        trigger_type: AuditTriggerType = AuditTriggerType.INITIAL,
        source_ref: Optional[str] = None,
        commit_sha: Optional[str] = None,
        save_as_baseline: bool = True,
    ) -> Audit:
        """
        Run a P1.2 audit and persist it as a durable record.

        If project is ephemeral, transitions to saved.
        Creates immutable audit record with full P1.2 provenance.
        """
        # Get or create project
        project = await self.projects.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Create running audit record
        audit = await self.audits.create(
            project_id=project_id,
            trigger_type=trigger_type,
            source_ref=source_ref,
            commit_sha=commit_sha or "unknown",
            mneme_version=version("mneme-hq"),
            schema_version=1,  # mneme.audit/v1
            audit_schema="mneme.audit/v1",
            result_payload={},  # Will be updated on completion
            summary_payload={},  # Will be updated on completion
            status=AuditStatus.RUNNING,
        )

        try:
            # Run the P1.2 evaluation
            p12_response = await self._run_p12_audit(
                repository_url=repository_url,
                zip_path=zip_path,
                local_path=local_path,
                source_ref=source_ref,
            )

            # Provenance comes from the evaluated checkout, never the caller.
            if commit_sha and commit_sha != p12_response.commit_sha:
                raise ValueError("Requested commit does not match the evaluated checkout")
            p12_response.audit_id = str(audit.id)
            p12_response.project_id = str(project_id)
            audit.commit_sha = p12_response.commit_sha
            audit.mneme_version = p12_response.mneme_version

            # Build result payload (canonical mneme.audit/v1 response)
            result_payload = p12_response.model_dump(mode="json")

            # Build summary payload (derived for fast UI - P1.2 metrics)
            summary_payload = {
                "decisions_discovered": p12_response.summary.decisions_discovered,
                "protection_relevant": p12_response.summary.protection_relevant,
                "protected_count": p12_response.summary.protected_count,
                "mneme_ready_count": p12_response.summary.mneme_ready_count,
                "requires_modelling_count": p12_response.summary.requires_modelling_count,
                "guidance_count": p12_response.summary.guidance_count,
                "current_protection": p12_response.summary.current_protection,
                "identified_mneme_potential": p12_response.summary.identified_mneme_potential,
                "sources": p12_response.summary.sources,
                "by_category": p12_response.summary.by_category,
            }

            # Mark as completed (immutable from this point)
            completed_audit = await self.audits.mark_completed(
                audit_id=audit.id,
                result_payload=result_payload,
                summary_payload=summary_payload,
            )

            # If project was ephemeral, transition to saved
            if save_as_baseline and project.lifecycle == ProjectLifecycle.EPHEMERAL:
                await self.projects.update_lifecycle(project_id, ProjectLifecycle.SAVED)
                # First saved audit becomes baseline by default
                await self.projects.set_baseline(project_id, completed_audit.id)

            return completed_audit

        except Exception as e:
            # Mark audit as failed
            await self.audits.mark_failed(audit.id)
            raise

    async def _run_p12_audit(
        self,
        repository_url: Optional[str] = None,
        zip_path: Optional[str] = None,
        local_path: Optional[str] = None,
        source_ref: Optional[str] = None,
    ) -> ProtectionAuditResponse:
        # Cloning/parsing are blocking; do not block unrelated API requests.
        return await run_in_threadpool(
            self._evaluate_p12, repository_url, zip_path, local_path, source_ref
        )

    def _evaluate_p12(
        self,
        repository_url: Optional[str] = None,
        zip_path: Optional[str] = None,
        local_path: Optional[str] = None,
        source_ref: Optional[str] = None,
    ) -> ProtectionAuditResponse:
        """
        Run the complete P1.2 audit pipeline.
        
        Returns a complete mneme.audit/v1 response.
        """
        # Prepare repository with safe extraction
        temp_dir: Optional[Path] = None
        if repository_url:
            repo_path = safe_clone_repo(repository_url, source_ref=source_ref)
            temp_dir = repo_path
            repo_name = repository_url.rstrip("/").split("/")[-1].replace(".git", "")
            repo_identifier = repository_url
        elif zip_path:
            repo_path = safe_extract_zip(zip_path)
            temp_dir = repo_path
            repo_name = Path(zip_path).stem
            repo_identifier = f"upload:{repo_name}"
        elif local_path:
            repo_path = safe_local_path(local_path)
            repo_name = repo_path.name
            repo_identifier = f"local:{repo_name}"
        else:
            raise ValueError("No repository source provided")

        try:
            # ZIPs have no trustworthy Git provenance; never trust uploaded .git.
            resolved_commit = "not-applicable:archive"
            if not zip_path:
                try:
                    resolved_commit = Repo(repo_path, search_parent_directories=False).head.commit.hexsha
                except (InvalidGitRepositoryError, NoSuchPathError, ValueError):
                    if repository_url:
                        raise ValueError("Could not resolve the audited Git commit")
                    resolved_commit = "not-applicable:directory"
            mneme_adapter = MnemeAdapter()
            # Load Mneme decisions from repository (ADRs via Mneme's import pipeline)
            mneme_report = mneme_adapter.load_repository(repo_path)
            
            # Also check for .mneme/project_memory.json
            memory_path = repo_path / ".mneme" / "project_memory.json"
            if memory_path.exists():
                mneme_adapter.load_memory_file(memory_path)
            
            # Find loose ADRs
            loose_adrs = find_loose_adrs(repo_path)
            
            # Find agent instructions and config files
            agent_instructions = []
            config_files = []
            sources = self._find_source_files(repo_path)
            
            for source in sources:
                if source.suffix in [".md", ".txt"] and ("CLAUDE.md" in str(source) or "AGENTS.md" in str(source)):
                    content = source.read_text(encoding="utf-8", errors="ignore")
                    relative_path = str(source.relative_to(repo_path))
                    agent_instructions.append({
                        "name": source.name,
                        "content": content,
                        "path": relative_path,
                        "lines": "1-50",
                    })
                elif source.suffix in [".toml", ".yaml", ".yml"] or source.name in ["requirements.txt", "requirements-dev.txt", "setup.py", "setup.cfg", "Makefile", "justfile", "Taskfile.yml"]:
                    content = source.read_text(encoding="utf-8", errors="ignore")
                    relative_path = str(source.relative_to(repo_path))
                    config_files.append({
                        "name": source.name,
                        "content": content,
                        "path": relative_path,
                        "lines": "1-100",
                    })
            
            # Collect all P1.2 decision inputs
            p12_inputs = collect_p12_inputs(
                mneme_report=mneme_report,
                loose_adrs=loose_adrs,
                agent_instructions=agent_instructions,
                config_files=config_files,
                repo_path=repo_path,
            )
            for item in p12_inputs:
                source_path = Path(item.source_path)
                if source_path.is_absolute():
                    try:
                        item.source_path = source_path.relative_to(repo_path).as_posix()
                    except ValueError:
                        item.source_path = source_path.name
                else:
                    item.source_path = item.source_path.replace("\\", "/")
            
            # Collect source file paths for summary
            source_file_paths = [str(s.relative_to(repo_path)) for s in sources]
            
            # Build complete P1.2 response
            return build_protection_audit_response(
                project_name=repo_identifier,
                repository_url=repository_url,
                commit_sha=resolved_commit,
                mneme_version=version("mneme-hq"),
                decisions_inputs=p12_inputs,
                source_files=source_file_paths,
            )
        finally:
            # Cleanup temp directory if we created one
            if temp_dir and (repository_url or zip_path):
                cleanup_temp_dir(temp_dir)

    def _find_source_files(self, repo_path: Path) -> List[Path]:
        """Find relevant source files in the repository."""
        from app.services.audit_service import AuditService
        service = AuditService()
        service.repo_path = repo_path
        return service._find_source_files()

    async def re_audit(
        self,
        project_id: UUID,
        repository_url: Optional[str] = None,
        zip_path: Optional[str] = None,
        local_path: Optional[str] = None,
        source_ref: Optional[str] = None,
        commit_sha: Optional[str] = None,
    ) -> Audit:
        """
        Run a re-audit against a new repository state.

        Creates a new immutable audit record linked to the same project.
        Does not modify the baseline or any previous audits.
        """
        project = await self.projects.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        if project.lifecycle == ProjectLifecycle.EPHEMERAL:
            raise ValueError("Cannot re-audit an ephemeral project. Save it first.")

        return await self.run_and_save_audit(
            project_id=project_id,
            repository_url=repository_url,
            zip_path=zip_path,
            local_path=local_path,
            trigger_type=AuditTriggerType.RE_AUDIT,
            source_ref=source_ref,
            commit_sha=commit_sha,
        )

    async def get_project_history(self, project_id: UUID) -> list[Audit]:
        """Get all audits for a project (history)."""
        return await self.audits.get_project_audits(project_id)

    async def get_baseline(self, project_id: UUID) -> Optional[Audit]:
        """Get the baseline audit for a project."""
        return await self.audits.get_baseline_audit(project_id)

    async def set_baseline(self, project_id: UUID, audit_id: UUID) -> Project:
        """Set a specific audit as the project baseline."""
        return await self.projects.set_baseline(project_id, audit_id)


# Import Path for _find_source_files
from pathlib import Path
from typing import List
