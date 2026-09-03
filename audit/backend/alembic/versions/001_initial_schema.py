"""
M1.0 Initial Schema Migration

Creates the four core tables for Mneme Audit M1:
- audits
- projects
- contacts
- project_contacts

Revision ID: 001
Revises: 
Create Date: 2026-09-02
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy import inspect

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing tables if they exist (for idempotent migrations)
    # This ensures a clean slate for each migration run
    op.execute('DROP TABLE IF EXISTS project_contacts CASCADE')
    op.execute('DROP TABLE IF EXISTS contacts CASCADE')
    op.execute('DROP TABLE IF EXISTS projects CASCADE')
    op.execute('DROP TABLE IF EXISTS audits CASCADE')
    
    # Create audits table first (no foreign key dependencies initially)
    op.create_table(
        'audits',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('status', sa.String(20), nullable=False, default='running'),
        sa.Column('trigger_type', sa.String(20), nullable=False, default='initial'),
        sa.Column('source_ref', sa.String(255), nullable=True),
        sa.Column('commit_sha', sa.String(64), nullable=False),
        sa.Column('mneme_version', sa.String(50), nullable=False),
        sa.Column('schema_version', sa.Integer, nullable=False),
        sa.Column('audit_schema', sa.String(50), nullable=False, default='mneme.audit/v1'),
        sa.Column('result_payload', sa.JSON, nullable=False),
        sa.Column('summary_payload', sa.JSON, nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    op.create_index('ix_audits_project_created', 'audits', ['project_id', 'created_at'])
    op.create_index('ix_audits_status', 'audits', ['status'])
    op.create_index('ix_audits_commit_sha', 'audits', ['commit_sha'])
    
    # Create projects table (references audits via baseline_audit_id)
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True),
        sa.Column('source_type', sa.String(50), nullable=False, default='github'),
        sa.Column('source_locator', sa.String(500), nullable=False),
        sa.Column('default_ref', sa.String(255), nullable=True),
        sa.Column('lifecycle', sa.String(20), nullable=False, default='ephemeral'),
        sa.Column('baseline_audit_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    op.create_index('ix_projects_source_locator', 'projects', ['source_locator'])
    op.create_index('ix_projects_lifecycle', 'projects', ['lifecycle'])
    
    # Add foreign key constraints after both tables exist
    op.create_foreign_key('fk_audits_project_id', 'audits', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_projects_baseline_audit_id', 'projects', 'audits', ['baseline_audit_id'], ['id'], ondelete='SET NULL')
    
    op.create_index('ix_audits_project_created', 'audits', ['project_id', 'created_at'])
    op.create_index('ix_audits_status', 'audits', ['status'])
    op.create_index('ix_audits_commit_sha', 'audits', ['commit_sha'])
    
    op.create_index('ix_projects_source_locator', 'projects', ['source_locator'])
    op.create_index('ix_projects_lifecycle', 'projects', ['lifecycle'])
    
    # Create contacts table
    op.create_table(
        'contacts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=True, unique=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('company', sa.String(255), nullable=True),
        sa.Column('role', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create project_contacts table
    op.create_table(
        'project_contacts',
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('contact_id', UUID(as_uuid=True), sa.ForeignKey('contacts.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role', sa.String(20), nullable=False, default='technical'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    op.create_index('ix_project_contacts_contact', 'project_contacts', ['contact_id'])


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS ix_project_contacts_contact')
    op.execute('DROP TABLE IF EXISTS project_contacts CASCADE')
    op.execute('DROP TABLE IF EXISTS contacts CASCADE')
    op.execute('DROP INDEX IF EXISTS ix_audits_commit_sha')
    op.execute('DROP INDEX IF EXISTS ix_audits_status')
    op.execute('DROP INDEX IF EXISTS ix_audits_project_created')
    op.execute('DROP TABLE IF EXISTS audits CASCADE')
    op.execute('DROP INDEX IF EXISTS ix_projects_lifecycle')
    op.execute('DROP INDEX IF EXISTS ix_projects_source_locator')
    op.execute('DROP TABLE IF EXISTS projects CASCADE')
    op.execute('DROP TABLE IF EXISTS contacts CASCADE')
    op.execute('DROP TABLE IF EXISTS project_contacts CASCADE')