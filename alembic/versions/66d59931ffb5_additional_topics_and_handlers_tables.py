"""additional topics and handlers tables

Revision ID: 66d59931ffb5
Revises: 97abdde2da83
Create Date: 2026-02-23 08:33:19.091518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '66d59931ffb5'
down_revision: Union[str, Sequence[str], None] = '97abdde2da83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
