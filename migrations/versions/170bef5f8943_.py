"""empty message

Revision ID: 170bef5f8943
Revises: 55f589ad76db
Create Date: 2022-08-10 10:22:37.377451

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '170bef5f8943'
down_revision = '55f589ad76db'
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
               nullable=True)
    op.alter_column('show', 'start_time',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('artist', 'seeking_description',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
    op.alter_column('artist', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###
