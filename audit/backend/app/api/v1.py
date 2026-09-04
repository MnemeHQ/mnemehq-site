"""
M1 API routes for Mneme Audit.

Endpoints for:
- Project CRUD
- Audit persistence and history
- Baseline assignment
- Re-audit
- Comparison
- Lifecycle transitions
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID
from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import (
    ProjectLifecycle,
    AuditTriggerType,
    ContactRelationship,
)
from app.repositories import (
    ProjectRepository,
    AuditRepository,
    ContactRepository,
    ProjectContactRepository,
)
from app.services.audit_persistence import AuditPersistenceService
from app.services.comparison import comparison_engine, AuditComparison
from app.core.lifecycle import LifecycleTransitionError
from app.core.config import settings
from app.models.workspace import ProjectCreate, ProjectAuditRequest
from app.api.audit import validate_github_url


def iso_utc(value):
    # SQLite drops timezone information; persisted timestamps are UTC.
    if value is None:
        return None
    return (value if value.tzinfo else value.replace(tzinfo=timezone.utc)).isoformat()


router = APIRouter(prefix="/api/v1", tags=["audit-m1"])


# --- Dependency injection ---

def get_project_repo(session: AsyncSession = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(session)


def get_audit_repo(session: AsyncSession = Depends(get_db)) -> AuditRepository:
    return AuditRepository(session)


def get_persistence_service(session: AsyncSession = Depends(get_db)) -> AuditPersistenceService:
    return AuditPersistenceService(session)


# --- Projects ---

@router.post("/projects", status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreate,
    service: AuditPersistenceService = Depends(get_persistence_service),
):
    """Create a new project (starts as ephemeral)."""
    # Check slug uniqueness
    existing = await service.projects.get_by_slug(request.slug)
    if existing:
        raise HTTPException(status_code=409, detail="Project slug already exists")

    project = await service.projects.create(
        name=request.name,
        slug=request.slug,
        source_type=request.source_type,
        source_locator=request.source_locator,
        default_ref=request.default_ref,
        lifecycle=ProjectLifecycle.EPHEMERAL,
    )
    await service.session.commit()
    return {"id": str(project.id), "slug": project.slug, "lifecycle": project.lifecycle.value}


@router.get("/projects/{project_id}")
async def get_project(
    project_id: UUID,
    service: AuditPersistenceService = Depends(get_persistence_service),
):
    """Get project with audit history and baseline."""
    project = await service.projects.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get audit history
    audits = await service.get_project_history(project_id)

    # Get baseline
    baseline = await service.get_baseline(project_id)

    return {
        "id": str(project.id),
        "name": project.name,
        "slug": project.slug,
        "source_type": project.source_type,
        "source_locator": project.source_locator,
        "default_ref": project.default_ref,
        "lifecycle": project.lifecycle.value,
        "baseline_audit_id": str(baseline.id) if baseline else None,
        "audits": [
            {
                "id": str(a.id),
                "status": a.status.value,
                "trigger_type": a.trigger_type.value,
                "commit_sha": a.commit_sha,
                "mneme_version": a.mneme_version,
                "schema_version": a.schema_version,
                "created_at": iso_utc(a.created_at),
                "completed_at": iso_utc(a.completed_at) if a.completed_at else None,
            }
            for a in audits
        ],
        "created_at": iso_utc(project.created_at),
        "updated_at": iso_utc(project.updated_at),
    }


@router.get("/projects")
async def list_projects(
    lifecycle: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    service: AuditPersistenceService = Depends(get_persistence_service),
):
    """List projects with optional lifecycle filter."""
    lifecycle_enum = ProjectLifecycle(lifecycle) if lifecycle else None
    projects = await service.projects.list_all(lifecycle=lifecycle_enum, limit=limit, offset=offset)

    return [
        {
            "id": str(p.id),
            "name": p.name,
            "slug": p.slug,
            "source_locator": p.source_locator,
            "lifecycle": p.lifecycle.value,
            "created_at": iso_utc(p.created_at),
        }
        for p in projects
    ]


@router.patch("/projects/{project_id}")
async def update_project(
    project_id: UUID,
    name: Optional[str] = None,
    lifecycle: Optional[str] = None,
    baseline_audit_id: Optional[UUID] = None,
    service: AuditPersistenceService = Depends(get_persistence_service),
):
    """Update project (name, lifecycle, baseline)."""
    project = await service.projects.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if name is not None:
        await service.projects.update_name(project_id, name)

    if lifecycle is not None:
        try:
            target = ProjectLifecycle(lifecycle)
            await service.projects.update_lifecycle(project_id, target)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid lifecycle: {lifecycle}")
        except LifecycleTransitionError as e:
            raise HTTPException(status_code=400, detail=str(e))

    if baseline_audit_id is not None:
        try:
            await service.set_baseline(project_id, baseline_audit_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    await service.session.commit()
    return await get_project(project_id, service)


# --- Audits ---

@router.post("/projects/{project_id}/audits", status_code=status.HTTP_201_CREATED)
async def run_audit(
    project_id: UUID,
    request: ProjectAuditRequest,
    service: AuditPersistenceService = Depends(get_persistence_service),
):
    """
    Run and persist an audit for a project.

    For ephemeral projects: transitions to saved, sets first audit as baseline.
    For saved/pilot projects: creates new audit record (re-audit if not first).
    """
    project = await service.projects.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    repository_url = request.repository_url or project.source_locator
    if project.source_type != "github" or not validate_github_url(repository_url):
        raise HTTPException(status_code=400, detail="Re-audit requires a public GitHub repository. Start a new audit for ZIP uploads.")
    if repository_url != project.source_locator:
        raise HTTPException(status_code=400, detail="Repository does not match this project")
    source_ref = request.source_ref or project.default_ref
    try:
        trigger = AuditTriggerType(request.trigger_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid trigger_type")

    try:
        if trigger == AuditTriggerType.INITIAL:
            audit = await service.run_and_save_audit(
                project_id=project_id,
                repository_url=repository_url,
                trigger_type=trigger,
                source_ref=source_ref,
            )
        else:
            audit = await service.re_audit(
                project_id=project_id,
                repository_url=repository_url,
                source_ref=source_ref,
            )
    except ValueError as e:
        await service.session.commit()  # retain failed execution, never overwrite baseline
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        await service.session.commit()
        raise HTTPException(status_code=502, detail="Repository audit failed. Please retry or check the repository.")

    await service.session.commit()
    return {
        "id": str(audit.id),
        "status": audit.status.value,
        "commit_sha": audit.commit_sha,
        "mneme_version": audit.mneme_version,
        "schema_version": audit.schema_version,
    }


@router.get("/audits/{audit_id}")
async def get_audit(
    audit_id: UUID,
    service: AuditPersistenceService = Depends(get_persistence_service),
):
    """Get full audit result (immutable evidence record)."""
    audit = await service.audits.get_by_id_with_project(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    return {
        "id": str(audit.id),
        "project_id": str(audit.project_id),
        "status": audit.status.value,
        "trigger_type": audit.trigger_type.value,
        "source_ref": audit.source_ref,
        "commit_sha": audit.commit_sha,
        "mneme_version": audit.mneme_version,
        "schema_version": audit.schema_version,
        "result": audit.result_payload,
        "summary": audit.summary_payload,
        "summary_payload": audit.summary_payload,
        "started_at": iso_utc(audit.started_at),
        "completed_at": iso_utc(audit.completed_at) if audit.completed_at else None,
        "created_at": iso_utc(audit.created_at),
    }


@router.get("/projects/{project_id}/audits")
async def list_project_audits(
    project_id: UUID,
    limit: int = 50,
    offset: int = 0,
    service: AuditPersistenceService = Depends(get_persistence_service),
):
    """List all audits for a project."""
    audits = await service.audits.get_project_audits(project_id, limit=limit, offset=offset)

    return [
        {
            "id": str(a.id),
            "status": a.status.value,
            "trigger_type": a.trigger_type.value,
            "commit_sha": a.commit_sha,
            "mneme_version": a.mneme_version,
            "schema_version": a.schema_version,
            "created_at": iso_utc(a.created_at),
            "completed_at": iso_utc(a.completed_at) if a.completed_at else None,
        }
        for a in audits
    ]


# --- Comparison ---

@router.get("/projects/{project_id}/compare", response_model=AuditComparison)
async def compare_audits(
    project_id: UUID,
    current_audit_id: Optional[UUID] = None,
    service: AuditPersistenceService = Depends(get_persistence_service),
):
    """
    Compare baseline audit vs current (or specified) audit.

    Returns deterministic diff: improved, regressed, unchanged, added, removed.
    """
    project = await service.projects.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get baseline
    baseline = await service.get_baseline(project_id)
    if not baseline:
        raise HTTPException(status_code=400, detail="No baseline set for this project")

    # Get current audit (latest completed if not specified)
    if current_audit_id:
        current = await service.audits.get_by_id(current_audit_id)
        if not current or current.project_id != project_id:
            raise HTTPException(status_code=404, detail="Current audit not found")
    else:
        current = await service.audits.get_latest_completed(project_id)
        if not current:
            raise HTTPException(status_code=400, detail="No completed audits to compare")

    if baseline.id == current.id:
        raise HTTPException(status_code=400, detail="Cannot compare audit to itself")

    # Compare
    comparison = comparison_engine.compare(
        baseline_result=baseline.result_payload,
        current_result=current.result_payload,
        baseline_audit_id=baseline.id,
        current_audit_id=current.id,
        baseline_commit_sha=baseline.commit_sha,
        current_commit_sha=current.commit_sha,
        baseline_mneme_version=baseline.mneme_version,
        current_mneme_version=current.mneme_version,
        baseline_schema_version=baseline.schema_version,
        current_schema_version=current.schema_version,
    )

    return comparison


# --- Contacts (CRM-lite) ---

@router.post("/contacts", status_code=status.HTTP_201_CREATED)
async def create_contact(
    email: Optional[str] = None,
    name: Optional[str] = None,
    company: Optional[str] = None,
    role: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
):
    """Create a contact."""
    repo = ContactRepository(session)
    contact = await repo.create(email=email, name=name, company=company, role=role)
    await session.commit()
    return {"id": str(contact.id), "email": contact.email, "name": contact.name}


@router.post("/projects/{project_id}/contacts", status_code=status.HTTP_201_CREATED)
async def add_contact_to_project(
    project_id: UUID,
    contact_id: UUID,
    relationship: str = "technical",
    service: AuditPersistenceService = Depends(get_persistence_service),
):
    """Associate a contact with a project."""
    try:
        rel = ContactRelationship(relationship)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid relationship: {relationship}")

    project = await service.projects.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    contact = await service.contacts.get_by_id(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    pc = await service.project_contacts.add(project_id, contact_id, rel)
    await service.session.commit()
    return {"project_id": str(pc.project_id), "contact_id": str(pc.contact_id), "relationship": pc.relationship.value}


@router.get("/projects/{project_id}/contacts")
async def list_project_contacts(
    project_id: UUID,
    service: AuditPersistenceService = Depends(get_persistence_service),
):
    """List contacts for a project."""
    project = await service.projects.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    pcs = await service.project_contacts.list_for_project(project_id)
    return [
        {
            "contact_id": str(pc.contact_id),
            "email": pc.contact.email,
            "name": pc.contact.name,
            "company": pc.contact.company,
            "role": pc.contact.role,
            "relationship": pc.relationship.value,
        }
        for pc in pcs
    ]
