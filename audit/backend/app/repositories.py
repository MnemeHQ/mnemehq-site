"""
Repository layer for Mneme Audit M1.

Provides data access abstraction over the four core entities.
All methods are async and use SQLAlchemy async session.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Project,
    Audit,
    Contact,
    ProjectContact,
    ProjectLifecycle,
    AuditStatus,
    AuditTriggerType,
    ContactRelationship,
)
from app.core.lifecycle import transition, TransitionResult, LifecycleTransitionError


class ProjectRepository:
    """Repository for Project operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        name: str,
        slug: str,
        source_type: str,
        source_locator: str,
        default_ref: Optional[str] = None,
        lifecycle: ProjectLifecycle = ProjectLifecycle.EPHEMERAL,
    ) -> Project:
        """Create a new project."""
        project = Project(
            name=name,
            slug=slug,
            source_type=source_type,
            source_locator=source_locator,
            default_ref=default_ref,
            lifecycle=lifecycle,
        )
        self.session.add(project)
        await self.session.flush()
        return project

    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID with relationships loaded."""
        stmt = (
            select(Project)
            .where(Project.id == project_id)
            .options(selectinload(Project.audits), selectinload(Project.contacts).selectinload(ProjectContact.contact))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Project]:
        """Get project by slug."""
        stmt = select(Project).where(Project.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_source_locator(self, source_locator: str) -> Optional[Project]:
        """Get project by source locator (GitHub owner/repo)."""
        stmt = select(Project).where(Project.source_locator == source_locator)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        lifecycle: Optional[ProjectLifecycle] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Project]:
        """List projects with optional lifecycle filter."""
        stmt = select(Project).order_by(Project.created_at.desc()).limit(limit).offset(offset)
        if lifecycle:
            stmt = stmt.where(Project.lifecycle == lifecycle)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_lifecycle(
        self,
        project_id: UUID,
        target_lifecycle: ProjectLifecycle,
    ) -> TransitionResult:
        """Transition project lifecycle (monotonic: ephemeral → saved → pilot)."""
        project = await self.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        result = transition(project.lifecycle, target_lifecycle)
        if not result.success:
            raise LifecycleTransitionError(result.error)

        project.lifecycle = target_lifecycle
        project.updated_at = datetime.utcnow()
        await self.session.flush()
        return result

    async def set_baseline(self, project_id: UUID, audit_id: UUID) -> Project:
        """Set the baseline audit for a project."""
        project = await self.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Verify audit belongs to project
        audit = await self.session.get(Audit, audit_id)
        if not audit or audit.project_id != project_id:
            raise ValueError(f"Audit {audit_id} not found or does not belong to project {project_id}")

        # Only completed audits can be baselines
        if audit.status != AuditStatus.COMPLETED:
            raise ValueError(f"Only completed audits can be set as baseline (audit status: {audit.status.value})")

        project.baseline_audit_id = audit_id
        project.updated_at = datetime.utcnow()
        await self.session.flush()
        return project

    async def update_name(self, project_id: UUID, name: str) -> Project:
        """Update project name."""
        project = await self.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        project.name = name
        project.updated_at = datetime.utcnow()
        await self.session.flush()
        return project


class AuditRepository:
    """Repository for Audit operations.

    Key invariant: Completed audits are immutable.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        project_id: UUID,
        trigger_type: AuditTriggerType,
        source_ref: Optional[str],
        commit_sha: str,
        mneme_version: str,
        schema_version: int,
        result_payload: dict,
        summary_payload: dict,
        status: AuditStatus = AuditStatus.RUNNING,
        audit_schema: str = "mneme.audit/v1",
    ) -> Audit:
        """Create a new audit record."""
        audit = Audit(
            project_id=project_id,
            trigger_type=trigger_type,
            source_ref=source_ref,
            commit_sha=commit_sha,
            mneme_version=mneme_version,
            schema_version=schema_version,
            audit_schema=audit_schema,
            result_payload=result_payload,
            summary_payload=summary_payload,
            status=status,
            started_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(audit)
        await self.session.flush()
        return audit

    async def get_by_id(self, audit_id: UUID) -> Optional[Audit]:
        """Get audit by ID with project loaded."""
        stmt = select(Audit).where(Audit.id == audit_id).options(selectinload(Audit.project))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_project(self, audit_id: UUID) -> Optional[Audit]:
        """Get audit by ID with project relationship loaded."""
        return await self.get_by_id(audit_id)

    async def mark_completed(
        self,
        audit_id: UUID,
        result_payload: dict,
        summary_payload: dict,
    ) -> Audit:
        """Mark a running audit as completed with immutable results."""
        audit = await self.get_by_id(audit_id)
        if not audit:
            raise ValueError(f"Audit {audit_id} not found")

        if audit.status != AuditStatus.RUNNING:
            raise ValueError(f"Audit {audit_id} is not in RUNNING state (current: {audit.status.value})")

        # Immutable once completed - these fields are final
        audit.status = AuditStatus.COMPLETED
        audit.result_payload = result_payload
        audit.summary_payload = summary_payload
        audit.completed_at = datetime.now(timezone.utc)
        await self.session.flush()
        return audit

    async def mark_failed(self, audit_id: UUID) -> Audit:
        """Mark a running audit as failed."""
        audit = await self.get_by_id(audit_id)
        if not audit:
            raise ValueError(f"Audit {audit_id} not found")

        if audit.status != AuditStatus.RUNNING:
            raise ValueError(f"Audit {audit_id} is not in RUNNING state")

        audit.status = AuditStatus.FAILED
        audit.completed_at = datetime.utcnow()
        await self.session.flush()
        return audit

    async def get_project_audits(
        self,
        project_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Audit]:
        """Get all audits for a project, newest first."""
        stmt = (
            select(Audit)
            .where(Audit.project_id == project_id)
            .order_by(Audit.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_completed(self, project_id: UUID) -> Optional[Audit]:
        """Get the most recent completed audit for a project."""
        stmt = (
            select(Audit)
            .where(Audit.project_id == project_id, Audit.status == AuditStatus.COMPLETED)
            .order_by(Audit.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_baseline_audit(self, project_id: UUID) -> Optional[Audit]:
        """Get the baseline audit for a project."""
        stmt = (
            select(Audit)
            .join(Project, Project.baseline_audit_id == Audit.id)
            .where(Project.id == project_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class ContactRepository:
    """Repository for Contact operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
        company: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Contact:
        """Create a new contact."""
        contact = Contact(email=email, name=name, company=company, role=role)
        self.session.add(contact)
        await self.session.flush()
        return contact

    async def get_by_id(self, contact_id: UUID) -> Optional[Contact]:
        """Get contact by ID."""
        return await self.session.get(Contact, contact_id)

    async def get_by_email(self, email: str) -> Optional[Contact]:
        """Get contact by email."""
        stmt = select(Contact).where(Contact.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(
        self,
        email: str,
        name: Optional[str] = None,
        company: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Contact:
        """Create or update contact by email."""
        contact = await self.get_by_email(email)
        if contact:
            if name is not None:
                contact.name = name
            if company is not None:
                contact.company = company
            if role is not None:
                contact.role = role
            contact.updated_at = datetime.utcnow()
        else:
            contact = await self.create(email=email, name=name, company=company, role=role)
        await self.session.flush()
        return contact


class ProjectContactRepository:
    """Repository for ProjectContact operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(
        self,
        project_id: UUID,
        contact_id: UUID,
        relationship: ContactRelationship = ContactRelationship.TECHNICAL,
    ) -> ProjectContact:
        """Add a contact to a project."""
        # Check if already exists
        existing = await self.get(project_id, contact_id)
        if existing:
            return existing

        pc = ProjectContact(
            project_id=project_id,
            contact_id=contact_id,
            role=relationship,
        )
        self.session.add(pc)
        await self.session.flush()
        return pc

    async def get(self, project_id: UUID, contact_id: UUID) -> Optional[ProjectContact]:
        """Get project-contact relationship."""
        stmt = select(ProjectContact).where(
            ProjectContact.project_id == project_id,
            ProjectContact.contact_id == contact_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_project(self, project_id: UUID) -> list[ProjectContact]:
        """List all contacts for a project."""
        stmt = (
            select(ProjectContact)
            .where(ProjectContact.project_id == project_id)
            .options(selectinload(ProjectContact.contact))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def remove(self, project_id: UUID, contact_id: UUID) -> bool:
        """Remove a contact from a project."""
        pc = await self.get(project_id, contact_id)
        if pc:
            await self.session.delete(pc)
            await self.session.flush()
            return True
        return False
