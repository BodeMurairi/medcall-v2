"""create consultation decision table

Revision ID: b3f892ac1d40
Revises: 2af571154ca6
Create Date: 2026-03-25

"""
from alembic import op
import sqlalchemy as sa

revision = 'b3f892ac1d40'
down_revision = '2af571154ca6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'consultation_decisions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('consultation_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('urgency', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('referral_type', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['consultation_id'], ['consultations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('consultation_id'),
    )


def downgrade() -> None:
    op.drop_table('consultation_decisions')
