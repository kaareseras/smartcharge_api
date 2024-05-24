"""create cars table

Revision ID: 100adda12d9e
Revises: bad8740f77b7
Create Date: 2024-05-24 21:23:26.063132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '100adda12d9e'
down_revision: Union[str, None] = 'bad8740f77b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cars',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=150), nullable=True),
    sa.Column('registration', sa.String(length=150), nullable=True),
    sa.Column('brand', sa.String(length=150), nullable=True),
    sa.Column('model', sa.String(length=150), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('image_filename', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('battery_capacity', sa.Integer(), nullable=True),
    sa.Column('HA_Entity_ID_Trip', sa.String(length=255), nullable=True),
    sa.Column('HA_Entity_ID_SOC', sa.String(length=255), nullable=True),
    sa.Column('HA_Entity_ID_SOC_Max', sa.String(length=255), nullable=True),
    sa.Column('HA_Entity_ID_Pluged_In', sa.String(length=255), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('cars')
    # ### end Alembic commands ###