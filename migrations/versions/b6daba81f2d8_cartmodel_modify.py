"""cartmodel modify

Revision ID: b6daba81f2d8
Revises: 3c3da291e83e
Create Date: 2024-12-13 11:02:53.513080

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b6daba81f2d8'
down_revision = '3c3da291e83e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('cart', 'product_img',
               existing_type=mysql.VARCHAR(length=200),
               type_=sa.String(length=1000),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('cart', 'product_img',
               existing_type=sa.String(length=1000),
               type_=mysql.VARCHAR(length=200),
               existing_nullable=True)
    # ### end Alembic commands ###
