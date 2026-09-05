"""
M1.3b Setup pairing migration.

Extends the M1.2 model without replacing it:
- projects: activation_state / setup_completed_at / setup_audit_id columns
  (Mneme activation state is distinct from the Audit lifecycle)
- setup_references: opaque, scoped, expiring references that link a saved
  Audit baseline to a Mneme setup completion

Revision ID: 002
Revises: 001
Create Date: 2026-09-05
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'setup_references',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('reference', sa.String(64), nullable=False),
        sa.Column('audit_id', UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('redeemed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('redeemed_mneme_version', sa.String(50), nullable=True),
    )
    op.create_index('ix_setup_references_reference', 'setup_references', ['reference'], unique=True)
    op.create_index('ix_setup_references_audit_id', 'setup_references', ['audit_id'])
    op.create_index('ix_setup_references_project', 'setup_references', ['project_id'])
    op.create_foreign_key('fk_setup_references_audit_id', 'setup_references', 'audits', ['audit_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_setup_references_project_id', 'setup_references', 'projects', ['project_id'], ['id'], ondelete='CASCADE')

    op.add_column(
        'projects',
        sa.Column('activation_state', sa.String(20), nullable=False, server_default='not_installed'),
    )
    op.add_column('projects', sa.Column('setup_completed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        'projects',
        sa.Column('setup_audit_id', UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key('fk_projects_setup_audit_id', 'projects', 'audits', ['setup_audit_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS ix_setup_references_project')
    op.execute('DROP INDEX IF EXISTS ix_setup_references_audit_id')
    op.execute('DROP INDEX IF EXISTS ix_setup_references_reference')
    op.execute('DROP TABLE IF EXISTS setup_references CASCADE')
    op.drop_constraint('fk_projects_setup_audit_id', 'projects', type_='foreignkey')
    op.drop_column('projects', 'setup_audit_id')
    op.drop_column('projects', 'setup_completed_at')
    op.drop_column('projects', 'activation_state')
