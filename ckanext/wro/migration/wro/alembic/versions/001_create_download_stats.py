"""Create download stats table

Revision ID: 001_download_stats
Revises:
Create Date: 2025-12-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_download_stats'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create the download statistics tracking table."""
    op.create_table(
        'wro_download_stats',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('resource_id', sa.String(36), sa.ForeignKey('resource.id', ondelete='CASCADE'), nullable=False),
        sa.Column('package_id', sa.String(36), sa.ForeignKey('package.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('user.id', ondelete='SET NULL'), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('downloaded_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
    )

    # Create indexes for better query performance
    op.create_index('idx_download_stats_resource', 'wro_download_stats', ['resource_id'])
    op.create_index('idx_download_stats_package', 'wro_download_stats', ['package_id'])
    op.create_index('idx_download_stats_downloaded_at', 'wro_download_stats', ['downloaded_at'])
    op.create_index('idx_download_stats_user', 'wro_download_stats', ['user_id'])


def downgrade():
    """Drop the download statistics tracking table."""
    op.drop_index('idx_download_stats_user', 'wro_download_stats')
    op.drop_index('idx_download_stats_downloaded_at', 'wro_download_stats')
    op.drop_index('idx_download_stats_package', 'wro_download_stats')
    op.drop_index('idx_download_stats_resource', 'wro_download_stats')
    op.drop_table('wro_download_stats')
