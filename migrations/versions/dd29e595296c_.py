"""empty message

Revision ID: dd29e595296c
Revises: 1d35b29e002d
Create Date: 2024-01-08 16:40:13.213633

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd29e595296c'
down_revision = '1d35b29e002d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('historical_money', schema=None) as batch_op:
        batch_op.alter_column('fecha',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('historical_money', schema=None) as batch_op:
        batch_op.alter_column('fecha',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=False)

    # ### end Alembic commands ###
