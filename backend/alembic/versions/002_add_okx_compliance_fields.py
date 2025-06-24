"""Add OKX API compliance fields

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to exchange_accounts table
    op.add_column('exchange_accounts', sa.Column('permissions', sa.Text(), nullable=True))
    op.add_column('exchange_accounts', sa.Column('ip_whitelist', sa.Text(), nullable=True))
    op.add_column('exchange_accounts', sa.Column('last_validation', sa.DateTime(), nullable=True))
    op.add_column('exchange_accounts', sa.Column('validation_status', sa.String(20), nullable=True, default='pending'))
    op.add_column('exchange_accounts', sa.Column('validation_error', sa.Text(), nullable=True))
    op.add_column('exchange_accounts', sa.Column('rate_limit_remaining', sa.Integer(), nullable=True))
    op.add_column('exchange_accounts', sa.Column('rate_limit_reset', sa.DateTime(), nullable=True))
    op.add_column('exchange_accounts', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade():
    # Remove new columns from exchange_accounts table
    op.drop_column('exchange_accounts', 'updated_at')
    op.drop_column('exchange_accounts', 'rate_limit_reset')
    op.drop_column('exchange_accounts', 'rate_limit_remaining')
    op.drop_column('exchange_accounts', 'validation_error')
    op.drop_column('exchange_accounts', 'validation_status')
    op.drop_column('exchange_accounts', 'last_validation')
    op.add_column('exchange_accounts', 'ip_whitelist')
    op.drop_column('exchange_accounts', 'permissions')
