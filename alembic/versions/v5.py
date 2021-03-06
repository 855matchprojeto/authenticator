"""empty message

Revision ID: ecc6a395aa14
Revises: 94b1e123165a
Create Date: 2021-09-25 14:48:09.331960

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecc6a395aa14'
down_revision = '94b1e123165a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tb_usuario', 'nome',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tb_usuario', 'nome',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
