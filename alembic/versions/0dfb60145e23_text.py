"""text

Revision ID: 0dfb60145e23
Revises: aeff25f89db0
Create Date: 2024-11-07 20:53:44.806395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0dfb60145e23'
down_revision: Union[str, None] = 'aeff25f89db0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('strategies', sa.Column('indicators', sa.Text(), nullable=True))


def downgrade() -> None:
    pass
