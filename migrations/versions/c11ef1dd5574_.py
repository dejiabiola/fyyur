"""empty message

Revision ID: c11ef1dd5574
Revises: 19756d7b35c8
Create Date: 2022-08-03 22:18:03.242622

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c11ef1dd5574'
down_revision = '19756d7b35c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artist', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable='False')
    op.alter_column('artist', 'seeking_description',
               existing_type=sa.VARCHAR(length=500),
               nullable='True')
    op.alter_column('show', 'start_time',
               existing_type=postgresql.TIMESTAMP(),
               nullable='False')
    op.alter_column('venue', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable='False')
    op.alter_column('venue', 'seeking_description',
               existing_type=sa.VARCHAR(length=500),
               nullable='True')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venue', 'seeking_description',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
    op.alter_column('venue', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('show', 'start_time',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('artist', 'seeking_description',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
    op.alter_column('artist', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###
