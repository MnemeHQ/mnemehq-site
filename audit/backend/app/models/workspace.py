"""HTTP request contracts for the canonical workspace; no scoring logic."""
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.api.audit import validate_github_url


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    source_locator: str = Field(max_length=500)
    source_type: str = "github"
    default_ref: str | None = None


class BaselineSave(BaseModel):
    model_config = ConfigDict(extra="forbid")
    audit_id: UUID


class ProjectAuditRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    repository_url: str | None = None
    source_ref: str | None = Field(default=None, max_length=255)
    trigger_type: str = "re_audit"

    @field_validator("repository_url")
    @classmethod
    def public_repository(cls, value):
        if value is not None and not validate_github_url(value):
            raise ValueError("Use a public GitHub repository URL")
        return value


class SetupCompleteRequest(BaseModel):
    """Payload the Mneme CLI sends when setup completes with an audit ref.

    ``repository`` is the local clone's origin remote, used only for a
    mismatch check against the audit's repository; ``None`` skips the check.
    """
    model_config = ConfigDict(extra="forbid")
    repository: str | None = Field(default=None, max_length=500)
    mneme_version: str = Field(min_length=1, max_length=50)
