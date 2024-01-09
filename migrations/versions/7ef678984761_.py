"""empty message

Revision ID: 7ef678984761
Revises: 5d8434f27ae3
Create Date: 2024-01-08 18:51:08.282413

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ef678984761'
down_revision = '5d8434f27ae3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gastos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('essential', sa.Boolean(), nullable=False))

    with op.batch_alter_table('historical_money', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('historical_money', schema=None) as batch_op:
        batch_op.drop_column('description')

    with op.batch_alter_table('gastos', schema=None) as batch_op:
        batch_op.drop_column('essential')

    # ### end Alembic commands ###