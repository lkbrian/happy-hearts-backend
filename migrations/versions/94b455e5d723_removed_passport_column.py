"""removed passport column

Revision ID: 94b455e5d723
Revises: f6e09f003f80
Create Date: 2024-10-14 21:15:36.327350

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94b455e5d723'
down_revision = 'f6e09f003f80'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('children', schema=None) as batch_op:
        batch_op.drop_column('passport')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('children', schema=None) as batch_op:
        batch_op.add_column(sa.Column('passport', sa.VARCHAR(), nullable=False))

    # ### end Alembic commands ###
