"""fix: add server_default to criado_em columns

Revision ID: eb2b6a72343f
Revises: 8cc949aea0d4
Create Date: 2026-02-18 09:19:44.523548

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'eb2b6a72343f'
down_revision: Union[str, Sequence[str], None] = '8cc949aea0d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'arquivos_blob',
        'criado_em',
        existing_type=sa.DateTime(),
        server_default=sa.text('CURRENT_TIMESTAMP'),
        existing_nullable=False,
    )
    op.alter_column(
        'usuarios',
        'criado_em',
        existing_type=sa.DateTime(),
        server_default=sa.text('CURRENT_TIMESTAMP'),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'usuarios',
        'criado_em',
        existing_type=sa.DateTime(),
        server_default=None,
        existing_nullable=False,
    )
    op.alter_column(
        'arquivos_blob',
        'criado_em',
        existing_type=sa.DateTime(),
        server_default=None,
        existing_nullable=False,
    )
