"""Cria validadorTeste

Revision ID: daa1f747d3e3
Revises: 84905412ecb2
Create Date: 2024-01-15 18:44:51.857861

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'daa1f747d3e3'
down_revision = '84905412ecb2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('validador_testes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('codigo', sa.String(length=64), nullable=False),
    sa.Column('entrada', sa.String(length=250000), nullable=False),
    sa.Column('validador_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['validador_id'], ['validadores.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('validador_id')
    )
    op.create_index(op.f('ix_validador_testes_id'), 'validador_testes', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_validador_testes_id'), table_name='validador_testes')
    op.drop_table('validador_testes')
    # ### end Alembic commands ###