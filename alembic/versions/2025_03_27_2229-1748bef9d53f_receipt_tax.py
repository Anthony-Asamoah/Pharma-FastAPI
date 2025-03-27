"""receipt tax

Revision ID: 1748bef9d53f
Revises: 4f926a8669af
Create Date: 2025-03-27 22:29:30.920199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1748bef9d53f'
down_revision: Union[str, None] = '4f926a8669af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('receipts', sa.Column('tax', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('receipts', 'tax')
    # ### end Alembic commands ###
