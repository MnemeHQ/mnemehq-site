"""
Setup pairing service for M1.3b.

Creates opaque, scoped, expiring setup references for saved Audit baselines
and resolves/records setup completions against them, per the frozen M1.3
contract (docs/plans/m1-3-audit-to-setup-activation.md, section 4 M1.3b):

- A reference resolves exactly one audit + project + baseline provenance.
- It is not a general-purpose credential: no account, org, or billing
  semantics; it grants nothing beyond this audit/project pairing.
- Invalid, expired, or mismatched references fail safely (404/410/409).
- A successful setup is attributable back to its audit/project (G7).
- Completion never mutates audit payloads, lifecycle, or baseline, and never
  moves a project past `setup` (activation to `active` is out of M1.3 scope).
"""
from __future__ import annotations

import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import (
    ActivationState,
    Audit,
    AuditStatus,
    Project,
    SetupReference,
)
from app.repositories import AuditRepository, ProjectRepository

_GITHUB_REPO_PATTERN = re.compile(
    r"github\.com[:/](?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)


class SetupPairingError(Exception):
    """Domain-level pairing failure carrying the HTTP status to raise."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def normalize_github_repo(value: str | None) -> Optional[str]:
    """Extract case-insensitive ``owner/repo`` from a GitHub URL or remote.

    Returns None when the value is not recognizable as a GitHub repository
    (ZIP audits, non-GitHub remotes): the mismatch check is skipped for
    those rather than guessing.
    """
    if not value:
        return None
    match = _GITHUB_REPO_PATTERN.search(value.strip())
    if not match:
        return None
    repo = match.group("repo")
    if repo.endswith(".git"):
        repo = repo[:-4]
    return f"{match.group('owner')}/{repo}".lower()


def iso_utc(value: datetime | None) -> Optional[str]:
    """ISO 8601 UTC string. SQLite drops tzinfo; persisted timestamps are UTC."""
    if value is None:
        return None
    return (value if value.tzinfo else value.replace(tzinfo=timezone.utc)).isoformat()


def reference_expiry(now: datetime | None = None) -> datetime:
    now = now or datetime.now(timezone.utc)
    return now + timedelta(hours=settings.SETUP_REFERENCE_TTL_HOURS)


class SetupPairingService:
    """Reference issuance, resolution, and setup-completion recording."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.projects = ProjectRepository(session)
        self.audits = AuditRepository(session)

    # ── Issuance ────────────────────────────────────────────────────────────

    async def create_reference(self, audit_id: UUID) -> SetupReference:
        """Create a setup reference for a saved baseline audit.

        The audit must be completed and must be the project's current
        baseline: pairing is a saved-baseline concept, not an ephemeral-run
        concept.
        """
        audit = await self.audits.get_by_id(audit_id)
        if not audit or audit.status != AuditStatus.COMPLETED:
            raise SetupPairingError(404, "Completed audit not found")
        project = await self.projects.get_by_id(audit.project_id)
        if not project or project.baseline_audit_id != audit.id:
            raise SetupPairingError(
                409, "Setup references can only be created for a saved baseline audit"
            )
        reference = SetupReference(
            reference=secrets.token_urlsafe(24),
            audit_id=audit.id,
            project_id=project.id,
            expires_at=reference_expiry(),
        )
        self.session.add(reference)
        await self.session.flush()
        return reference

    # ── Resolution ──────────────────────────────────────────────────────────

    async def resolve(self, reference: str) -> dict:
        """Resolve a reference to its baseline provenance without consuming it."""
        row, audit, project = await self._load_valid(reference)
        return {
            "reference": row.reference,
            "audit_id": str(audit.id),
            "project_id": str(project.id),
            "project_name": project.name,
            "repository": audit.result_payload.get("repository"),
            "repository_url": audit.result_payload.get("repository_url"),
            "commit_sha": audit.commit_sha,
            "mneme_version": audit.mneme_version,
            "schema_version": audit.schema_version,
            "audit_schema": audit.audit_schema,
            "summary": audit.summary_payload,
            "project_activation_state": project.activation_state.value,
            "expires_at": iso_utc(row.expires_at),
            "redeemed": row.redeemed_at is not None,
        }

    # ── Completion ──────────────────────────────────────────────────────────

    async def complete(
        self,
        reference: str,
        repository: str | None,
        mneme_version: str,
    ) -> dict:
        """Record a setup completion against a reference (idempotent).

        Fails safely on unknown (404), expired (410), or mismatched (409)
        references. Records attribution on the project (setup_audit_id,
        setup_completed_at, activation_state=setup) without touching audit
        payloads, lifecycle, or baseline.
        """
        row, audit, project = await self._load_valid(reference)
        if row.redeemed_at is not None:
            return await self._completion_payload(
                row, audit, project, already_redeemed=True
            )
        self._verify_repository_match(audit, repository)

        now = datetime.now(timezone.utc)
        row.redeemed_at = now
        row.redeemed_mneme_version = mneme_version
        project.setup_audit_id = audit.id
        if project.setup_completed_at is None:
            project.setup_completed_at = now
        # Never downgrade an explicitly activated project; setup only ever
        # moves not_installed → setup.
        if project.activation_state != ActivationState.ACTIVE:
            project.activation_state = ActivationState.SETUP
        await self.session.flush()
        return await self._completion_payload(row, audit, project)

    # ── Internals ───────────────────────────────────────────────────────────

    async def _load_valid(
        self, reference: str
    ) -> tuple[SetupReference, Audit, Project]:
        row = (
            await self.session.execute(
                select(SetupReference).where(SetupReference.reference == reference)
            )
        ).scalar_one_or_none()
        if not row:
            raise SetupPairingError(404, "Unknown setup reference")
        if row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise SetupPairingError(
                410, "Setup reference has expired. Save the baseline again to get a new reference."
            )
        audit = await self.audits.get_by_id(row.audit_id)
        project = await self.projects.get_by_id(row.project_id)
        if not audit or not project or audit.project_id != project.id:
            raise SetupPairingError(409, "Setup reference does not match its audit or project")
        return row, audit, project

    @staticmethod
    def _verify_repository_match(audit: Audit, repository: str | None) -> None:
        expected = normalize_github_repo(audit.result_payload.get("repository"))
        expected = expected or normalize_github_repo(audit.result_payload.get("repository_url"))
        provided = normalize_github_repo(repository)
        if expected and provided and expected != provided:
            raise SetupPairingError(
                409,
                f"Setup reference belongs to repository '{expected}', "
                f"but setup was run against '{provided}'",
            )

    async def _completion_payload(
        self,
        row: SetupReference,
        audit: Audit,
        project: Project,
        already_redeemed: bool = False,
    ) -> dict:
        return {
            "reference": row.reference,
            "already_redeemed": already_redeemed,
            "audit_id": str(audit.id),
            "project_id": str(project.id),
            "project_name": project.name,
            "activation_state": project.activation_state.value,
            "setup_completed_at": iso_utc(project.setup_completed_at),
            "commit_sha": audit.commit_sha,
            "mneme_version": audit.mneme_version,
            "schema_version": audit.schema_version,
            "summary": audit.summary_payload,
        }
