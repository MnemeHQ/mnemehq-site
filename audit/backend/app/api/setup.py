"""
M1.3b setup pairing routes.

Reference issuance (used by the Audit UI), resolution and completion (used
by the Mneme CLI). All endpoints are unauthenticated by design: references
are opaque, scoped, expiring tokens tied to one audit/project — not account
credentials — per the frozen M1.3 contract.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1 import get_persistence_service
from app.services.audit_persistence import AuditPersistenceService
from app.services.setup_pairing import (
    SetupPairingError,
    SetupPairingService,
    iso_utc,
)
from app.models.workspace import SetupCompleteRequest

router = APIRouter(prefix="/api/v1", tags=["setup"])


def get_setup_pairing_service(
    service: AuditPersistenceService = Depends(get_persistence_service),
) -> SetupPairingService:
    return SetupPairingService(service.session)


@router.post("/audits/{audit_id}/setup-reference", status_code=201)
async def create_setup_reference(
    audit_id: UUID,
    service: SetupPairingService = Depends(get_setup_pairing_service),
):
    """Create an opaque setup reference for a saved baseline audit."""
    try:
        row = await service.create_reference(audit_id)
    except SetupPairingError as exc:
        raise HTTPException(exc.status_code, exc.detail)
    await service.session.commit()
    return {
        "reference": row.reference,
        "audit_id": str(row.audit_id),
        "project_id": str(row.project_id),
        # Canonical install (ADR-005: the package is mneme-hq, never bare "mneme").
        "install_command": 'pipx install "mneme-hq>=0.6.0"',
        "setup_command": f"mneme setup --audit-ref {row.reference}",
        "expires_at": iso_utc(row.expires_at),
    }


@router.get("/setup-references/{reference}")
async def resolve_setup_reference(
    reference: str,
    service: SetupPairingService = Depends(get_setup_pairing_service),
):
    """Resolve a setup reference to its baseline provenance (no consumption)."""
    try:
        return await service.resolve(reference)
    except SetupPairingError as exc:
        raise HTTPException(exc.status_code, exc.detail)


@router.post("/setup-references/{reference}/complete")
async def complete_setup(
    reference: str,
    request: SetupCompleteRequest,
    service: SetupPairingService = Depends(get_setup_pairing_service),
):
    """Record a Mneme setup completion against a reference (idempotent)."""
    try:
        payload = await service.complete(
            reference,
            repository=request.repository,
            mneme_version=request.mneme_version,
        )
    except SetupPairingError as exc:
        raise HTTPException(exc.status_code, exc.detail)
    await service.session.commit()
    return payload
