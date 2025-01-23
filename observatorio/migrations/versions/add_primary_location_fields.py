"""Add primary location fields

Revision ID: add_primary_location_fields
Revises: 
Create Date: 2025-01-23 16:31:30.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_primary_location_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Agregar las nuevas columnas a la tabla news
    op.add_column('news', sa.Column('primary_location', sa.String(length=255), nullable=True))
    op.add_column('news', sa.Column('primary_country', sa.String(length=2), nullable=True))

def downgrade():
    # Eliminar las columnas
    op.drop_column('news', 'primary_location')
    op.drop_column('news', 'primary_country')
