"""change release_date in table books

Revision ID: 2d7929d0b253
Revises: f321cc85be80
Create Date: 2025-05-19 10:36:05.405795

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2d7929d0b253"
down_revision: Union[str, None] = "f321cc85be80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "books",
        "release_date",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.Integer(),
        nullable=True,
        postgresql_using="extract(epoch from release_date)::integer"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "books",
        "release_date",
        existing_type=sa.Integer(),
        type_=postgresql.TIMESTAMP(),
        nullable=True,
        postgresql_using="to_timestamp(release_date)::timestamp"
    )
