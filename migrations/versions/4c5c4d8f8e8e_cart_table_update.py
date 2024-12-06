"""cart table update

Revision ID: 4c5c4d8f8e8e
Revises: ad351f7b821c
Create Date: 2024-12-06 23:06:29.263000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c5c4d8f8e8e'
down_revision = 'ad351f7b821c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cart', sa.Column('product_url', sa.String(length=255), nullable=True))



def downgrade():
    pass
