"""Canonical M1.2 workspace lifecycle. Legacy /api/audit remains compatible."""
import os
import tempfile
import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.api.audit import MAX_UPLOAD_SIZE, validate_github_url
from app.api.v1 import get_persistence_service, get_project
from app.db.models import AuditStatus, ProjectLifecycle
from app.models.protection_audit import ProtectionAuditResponse
from app.models.workspace import BaselineSave
from app.services.audit_persistence import AuditPersistenceService

router = APIRouter(prefix="/api/v1", tags=["workspace"])


@router.post("/audit", response_model=ProtectionAuditResponse, status_code=201)
async def create_audit(
    repository_url: str | None = Form(None),
    zip_file: UploadFile | None = File(None),
    service: AuditPersistenceService = Depends(get_persistence_service),
):
    if bool(repository_url) == bool(zip_file):
        raise HTTPException(400, "Provide exactly one public GitHub URL or ZIP file")
    if repository_url and not validate_github_url(repository_url):
        raise HTTPException(400, "Use a public GitHub repository URL")
    zip_path = None
    try:
        if zip_file:
            if not (zip_file.filename or "").lower().endswith(".zip"):
                raise HTTPException(400, "File must be a .zip archive")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as target:
                zip_path = target.name
                total = 0
                while chunk := await zip_file.read(8192):
                    total += len(chunk)
                    if total > MAX_UPLOAD_SIZE:
                        raise HTTPException(413, "ZIP exceeds the upload size limit")
                    target.write(chunk)
        project = await service.projects.create(
            name=repository_url or "Uploaded repository",
            slug=f"audit-{uuid4()}",
            source_type="github" if repository_url else "zip",
            source_locator=repository_url or "upload:repository.zip",
        )
        try:
            audit = await service.run_and_save_audit(
                project.id, repository_url=repository_url, zip_path=zip_path,
                save_as_baseline=False,
            )
        except Exception:
            logging.getLogger(__name__).exception("Canonical repository audit failed")
            await service.session.commit()
            raise HTTPException(502, "Repository audit failed. Check the repository or ZIP and retry.")
        await service.session.commit()
        return audit.result_payload
    finally:
        if zip_path:
            os.unlink(zip_path)


@router.post("/baselines")
async def save_baseline(
    request: BaselineSave,
    service: AuditPersistenceService = Depends(get_persistence_service),
):
    audit = await service.audits.get_by_id(request.audit_id)
    if not audit or audit.status != AuditStatus.COMPLETED:
        raise HTTPException(404, "Completed audit not found")
    # Lock the project: concurrent save clicks cannot assign different baselines.
    from sqlalchemy import select
    from app.db.models import Project
    project = (await service.session.execute(
        select(Project).where(Project.id == audit.project_id).with_for_update()
    )).scalar_one()
    if project.baseline_audit_id not in (None, audit.id):
        raise HTTPException(409, "This project already has a baseline")
    if project.lifecycle == ProjectLifecycle.EPHEMERAL:
        await service.projects.update_lifecycle(project.id, ProjectLifecycle.SAVED)
    await service.projects.set_baseline(project.id, audit.id)
    await service.session.commit()
    return await get_project(project.id, service)


@router.get("/audits/{audit_id}/export")
async def export_audit(
    audit_id: UUID, format: str = "json",
    service: AuditPersistenceService = Depends(get_persistence_service),
):
    audit = await service.audits.get_by_id(audit_id)
    if not audit or audit.status != AuditStatus.COMPLETED:
        raise HTTPException(404, "Completed audit not found")
    result = ProtectionAuditResponse.model_validate(audit.result_payload)
    if format == "json":
        content, media_type = result.model_dump_json(indent=2), "application/json"
    elif format == "markdown":
        summary = result.summary
        lines = ["# Architecture Protection Audit", result.repository,
                 f"Audit: {result.audit_id}", f"Commit: {result.commit_sha}",
                 f"Mneme: {result.mneme_version}", f"Date: {result.timestamp.isoformat()}",
                 f"Current Protection: {summary.current_protection:.0%}"]
        for decision in result.decisions:
            lines += [f"## {decision.title}", decision.protection_classification.value,
                      decision.requirement, f"Source: {decision.source.file}"]
        content, media_type = "\n\n".join(lines), "text/markdown"
    else:
        raise HTTPException(400, "Format must be json or markdown")
    return Response(content, media_type=media_type,
                    headers={"Content-Disposition": f'attachment; filename="audit-{audit_id}.{ "json" if format == "json" else "md"}"'})
