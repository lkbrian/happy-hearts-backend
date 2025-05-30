"""not null @weight

Revision ID: 78cf60a65a65
Revises: c77f8a391b0c
Create Date: 2024-10-19 14:42:45.097410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78cf60a65a65'
down_revision = 'c77f8a391b0c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('deliveries', schema=None) as batch_op:
        batch_op.alter_column('weight_at_birth',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('deliveries', schema=None) as batch_op:
        batch_op.alter_column('weight_at_birth',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###
