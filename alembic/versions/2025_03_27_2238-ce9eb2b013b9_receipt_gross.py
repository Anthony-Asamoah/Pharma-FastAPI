"""receipt gross

Revision ID: ce9eb2b013b9
Revises: 1748bef9d53f
Create Date: 2025-03-27 22:38:30.694024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce9eb2b013b9'
down_revision: Union[str, None] = '1748bef9d53f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('receipts', sa.Column('gross_amount', sa.Float(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('receipts', 'gross_amount')
    # ### end Alembic commands ###
