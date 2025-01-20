"""add news locations table

Revision ID: add_news_locations
Revises: 
Create Date: 2025-01-20 15:35:15.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_news_locations'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('news_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('news_id', sa.Integer(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('location_name', sa.String(length=255), nullable=True),
        sa.Column('country_code', sa.String(length=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['news_id'], ['news.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_news_locations_news_id'), 'news_locations', ['news_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_news_locations_news_id'), table_name='news_locations')
    op.drop_table('news_locations')
