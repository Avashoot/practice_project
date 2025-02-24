"""empty message

Revision ID: aa195979b41f
Revises: a287cc7fe74d
Create Date: 2025-02-24 12:16:37.782555

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa195979b41f'
down_revision = 'a287cc7fe74d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('item_description', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.drop_column('item_description')

    # ### end Alembic commands ###
