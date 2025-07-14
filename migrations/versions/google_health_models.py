"""Add Google Health models

Revision ID: google_health_models
Revises: 
Create Date: 2025-07-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'google_health_models'
down_revision = None  # Update this to the previous migration
branch_labels = None
depends_on = None


def upgrade():
    # Create google_health_tokens table
    op.create_table(
        'google_health_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=False),
        sa.Column('token_type', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('scope', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_google_health_tokens_id'), 'google_health_tokens', ['id'], unique=False)

    # Create google_health_data table
    op.create_table(
        'google_health_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('data_type', sa.String(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_google_health_data_id'), 'google_health_data', ['id'], unique=False)
    
    # Create unique constraint to prevent duplicate data
    op.create_index(
        'ix_google_health_data_unique',
        'google_health_data',
        ['user_id', 'data_type', 'start_time', 'end_time'],
        unique=True
    )


def downgrade():
    # Drop tables
    op.drop_index('ix_google_health_data_unique', table_name='google_health_data')
    op.drop_index(op.f('ix_google_health_data_id'), table_name='google_health_data')
    op.drop_table('google_health_data')
    op.drop_index(op.f('ix_google_health_tokens_id'), table_name='google_health_tokens')
    op.drop_table('google_health_tokens')