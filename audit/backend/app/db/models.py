"""
SQLAlchemy models for Mneme Audit M1 persistence layer.

Four core entities:
- projects: Durable identity of something being audited
- audits: Immutable snapshots of audit executions
- contacts: Pilot/customer context (CRM-lite, not identity system)
- project_contacts: Many-to-many relationship with role
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ProjectLifecycle(PyEnum):
    """Project lifecycle states - monotonic in M1."""
    EPHEMERAL = "ephemeral"
    SAVED = "saved"
    PILOT = "pilot"


class AuditStatus(PyEnum):
    """Audit execution status."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AuditTriggerType(PyEnum):
    """What triggered this audit execution."""
    INITIAL = "initial"
    MANUAL = "manual"
    RE_AUDIT = "re_audit"


class ContactRelationship(PyEnum):
    """Relationship between a contact and a project."""
    OWNER = "owner"
    SPONSOR = "sponsor"
    TECHNICAL = "technical"


class ActivationState(PyEnum):
    """
    Mneme activation state for a project (M1.3, frozen contract section 3).

    Distinct from the Audit lifecycle (ephemeral → saved → pilot):
    - not_installed: no connected Mneme installation exists
    - setup: initialized; context/integrations/non-blocking checks only
    - active: at least one preventive protection explicitly enabled

    Setup never sets this to active; activation is always an explicit,
    separate user action. It is kept as a representable value so the Audit
    product can distinguish all three states, but no M1.3 code path
    transitions a project to active.
    """
    NOT_INSTALLED = "not_installed"
    SETUP = "setup"
    ACTIVE = "active"


class Project(Base):
    """
    Durable identity of something being audited.

    source_locator is identity (e.g., "MnemeHQ/mneme").
    commit_sha belongs to the audit, not the project, because every run
    can target a different repository state.
    """
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="github")
    source_locator: Mapped[str] = mapped_column(String(500), nullable=False)
    default_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    lifecycle: Mapped[ProjectLifecycle] = mapped_column(
        Enum(ProjectLifecycle, native_enum=False),
        nullable=False,
        default=ProjectLifecycle.EPHEMERAL,
    )
    baseline_audit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audits.id", ondelete="SET NULL"),
        nullable=True,
    )
    # M1.3 activation state (distinct from lifecycle; see ActivationState).
    activation_state: Mapped[ActivationState] = mapped_column(
        Enum(
            ActivationState,
            native_enum=False,
            # Migration 002 backfills existing rows with the frozen contract
            # value ("not_installed"), not the Python member name
            # ("NOT_INSTALLED").  Persist enum values so migrated and newly
            # created rows use the same representation.
            values_callable=lambda enum_type: [state.value for state in enum_type],
        ),
        nullable=False,
        default=ActivationState.NOT_INSTALLED,
    )
    setup_completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # Attribution: the baseline audit this setup was linked to (G7).
    setup_audit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audits.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    audits: Mapped[list["Audit"]] = relationship(
        "Audit",
        back_populates="project",
        lazy="selectin",
        order_by="Audit.created_at.desc()",
        foreign_keys="Audit.project_id",
    )
    contacts: Mapped[list["ProjectContact"]] = relationship(
        "ProjectContact",
        back_populates="project",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_projects_source_locator", "source_locator"),
        Index("ix_projects_lifecycle", "lifecycle"),
    )


class Audit(Base):
    """
    Immutable snapshots of an audit execution.

    Completed audits are immutable evidence records. If the parser, scoring
    logic, UI, or schema changes later, an old audit must remain reproducible
    as "what Mneme reported at that point in time."
    """
    __tablename__ = "audits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[AuditStatus] = mapped_column(
        Enum(AuditStatus, native_enum=False),
        nullable=False,
        default=AuditStatus.RUNNING,
    )
    trigger_type: Mapped[AuditTriggerType] = mapped_column(
        Enum(AuditTriggerType, native_enum=False),
        nullable=False,
        default=AuditTriggerType.INITIAL,
    )

    source_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)

    mneme_version: Mapped[str] = mapped_column(String(50), nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    audit_schema: Mapped[str] = mapped_column(String(50), nullable=False, default="mneme.audit/v1")

    # Canonical normalized audit result from P1.2 evaluator (source of truth)
    result_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Derived totals for fast UI rendering - never the source of truth
    summary_payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="audits", foreign_keys="Audit.project_id")

    __table_args__ = (
        Index("ix_audits_project_created", "project_id", "created_at"),
        Index("ix_audits_status", "status"),
        Index("ix_audits_commit_sha", "commit_sha"),
    )


class Contact(Base):
    """
    Pilot/customer context without introducing an identity system.

    A contact is CRM-lite metadata, NOT a login principal.
    """
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    project_contacts: Mapped[list["ProjectContact"]] = relationship(
        "ProjectContact",
        back_populates="contact",
        lazy="selectin",
    )


class ProjectContact(Base):
    """
    Many-to-many relationship between projects and contacts.

    Avoids one-project/one-person assumption. Costs almost nothing now.
    """
    __tablename__ = "project_contacts"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[ContactRelationship] = mapped_column(
        Enum(ContactRelationship, native_enum=False),
        nullable=False,
        default=ContactRelationship.TECHNICAL,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    project = relationship("Project", back_populates="contacts")
    contact = relationship("Contact", back_populates="project_contacts")

    __table_args__ = (
        Index("ix_project_contacts_contact", "contact_id"),
    )


class SetupReference(Base):
    """
    Opaque, scoped setup reference linking a saved Audit baseline to a
    Mneme setup (M1.3b, frozen contract section 4).

    The token is random, single-purpose, and scoped to exactly one audit and
    one project. It is not a user/account credential: it grants nothing
    beyond resolving the baseline provenance of this audit/project and
    recording one setup completion. It expires, and completion is idempotent
    per reference.
    """
    __tablename__ = "setup_references"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    reference: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    redeemed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # Mneme version reported by the CLI at completion (provenance).
    redeemed_mneme_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_setup_references_project", "project_id"),
    )
