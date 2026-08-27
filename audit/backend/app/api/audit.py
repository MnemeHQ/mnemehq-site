from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Optional
import tempfile
import os
import io
import re

from app.models.audit import AuditResult
from app.services.audit_service import audit_service

router = APIRouter(prefix="/audit", tags=["audit"])

# In-memory storage for demo (replace with database in production)
audit_storage: dict[str, AuditResult] = {}

# Max upload size: 50 MB (matches extraction limit)
MAX_UPLOAD_SIZE = 50 * 1024 * 1024

# GitHub URL validation regex
GITHUB_URL_PATTERN = re.compile(
    r'^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?$'
)

def validate_github_url(url: str) -> bool:
    """Validate that a URL is a public GitHub repository URL."""
    return bool(GITHUB_URL_PATTERN.match(url))


@router.post("", response_model=AuditResult)
async def create_audit(
    background_tasks: BackgroundTasks,
    repository_url: Optional[str] = Form(None),
    zip_file: Optional[UploadFile] = File(None),
):
    """Create a new architecture audit.
    
    Accepts either a public GitHub repository URL or a ZIP file upload.
    local_path is intentionally not exposed via public API for security.
    """
    
    # Validate input
    if not repository_url and not zip_file:
        raise HTTPException(status_code=400, detail="Provide repository_url or zip_file")
    
    # Validate GitHub URL if provided
    if repository_url and not validate_github_url(repository_url):
        raise HTTPException(
            status_code=400, 
            detail="repository_url must be a public GitHub repository URL (https://github.com/owner/repo)"
        )
    
    # Handle ZIP upload with streaming to disk and size limit
    zip_path = None
    if zip_file:
        if not zip_file.filename or not zip_file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="File must be a .zip archive")
        
        # Stream to temp file with size limit
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
            zip_path = tmp.name
            written = 0
            while True:
                chunk = await zip_file.read(8192)
                if not chunk:
                    break
                written += len(chunk)
                if written > MAX_UPLOAD_SIZE:
                    os.unlink(zip_path)
                    raise HTTPException(status_code=413, detail=f"Upload exceeds {MAX_UPLOAD_SIZE // (1024*1024)} MB limit")
                tmp.write(chunk)
    
    try:
        # Run audit
        result = await audit_service.analyze_repository(
            repo_url=repository_url,
            zip_path=zip_path,
            # local_path intentionally not accepted from public API
        )
        
        # Store result
        audit_storage[result.id] = result
        
        return result
    finally:
        # Cleanup temp zip file
        if zip_path and os.path.exists(zip_path):
            os.unlink(zip_path)


@router.get("/{audit_id}", response_model=AuditResult)
async def get_audit(audit_id: str):
    """Get audit results by ID."""
    if audit_id not in audit_storage:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit_storage[audit_id]


@router.get("/{audit_id}/export")
async def export_audit(audit_id: str, format: str = "markdown"):
    """Export audit results as Markdown or JSON."""
    if audit_id not in audit_storage:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    audit = audit_storage[audit_id]
    
    if format == "json":
        content = audit.model_dump_json(indent=2)
        media_type = "application/json"
        filename = f"architecture-audit-{audit_id}.json"
    else:
        content = _generate_markdown(audit)
        media_type = "text/markdown"
        filename = f"architecture-audit-{audit_id}.md"
    
    return StreamingResponse(
        io.BytesIO(content.encode('utf-8')),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def _generate_markdown(audit: AuditResult) -> str:
    """Generate Markdown export of audit results."""
    lines = [
        f"# Architecture Governability Audit",
        f"",
        f"**Repository:** {audit.repository}",
        f"**Audit ID:** {audit.id}",
        f"**Date:** {audit.createdAt.strftime('%Y-%m-%d %H:%M UTC')}",
        f"",
        f"---",
        f"",
        f"## Executive Summary",
        f"",
        f"- **Total Decisions Identified:** {audit.summary.totalDecisions}",
        f"- **Enforceable Now:** {audit.summary.enforceable}",
        f"- **Partially Enforceable:** {audit.summary.partial}",
        f"- **Guidance Only:** {audit.summary.guidance}",
        f"- **Coverage:** {audit.summary.coverage}%",
        f"",
        f"## Sources Found",
        f"",
    ]
    
    for source in audit.summary.sources:
        lines.append(f"- {source}")
    
    lines.extend([
        f"",
        f"---",
        f"",
        f"## Architectural Decisions",
        f"",
    ])
    
    for decision in audit.decisions:
        badge = {
            "enforceable": "✅ ENFORCEABLE",
            "partial": "⚠️ PARTIALLY ENFORCEABLE",
            "guidance": "ℹ️ GUIDANCE ONLY",
        }[decision.governability]
        
        lines.extend([
            f"### {decision.title} {badge}",
            f"",
            f"**Requirement:** {decision.requirement}",
            f"",
            f"**Source:** {decision.source.file} (Lines {decision.source.lines})",
            f"",
            f"**Governability:** {decision.governability.title()}",
            f"",
            f"**Applies To:** {', '.join(decision.appliesTo) if decision.appliesTo else 'N/A'}",
            f"",
            f"**Proposed Mneme Rule:**",
            f"```",
            f'{decision.proposedRule.type} "{decision.proposedRule.pattern}"',
            f"```",
            f"",
            f"*{decision.proposedRule.description}*",
            f"",
            f"---",
            f"",
        ])
    
    if audit.gaps:
        lines.extend([
            f"## Governance Gaps",
            f"",
            f"The following decisions cannot be fully enforced and require clarification:",
            f"",
        ])
        
        for gap in audit.gaps:
            lines.extend([
                f"### {gap.decision}",
                f"",
                f"**Reason:** {gap.reason}",
                f"",
                f"**Suggested Next Step:** {gap.suggestedNextStep}",
                f"",
                f"---",
                f"",
            ])
    
    lines.extend([
        f"---",
        f"",
        f"*Generated by Mneme HQ Architecture Audit Workspace*",
        f"*https://mnemehq.com/audit/*",
    ])
    
    return "\n".join(lines)