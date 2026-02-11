"""make import_tasks.import_start_time timezone-aware

Revision ID: 3c4d7b8e9f10
Revises: b241453a2ae7
Create Date: 2026-02-11 22:35:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3c4d7b8e9f10"
down_revision: Union[str, Sequence[str], None] = "b241453a2ae7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "import_tasks",
        "import_start_time",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using="import_start_time AT TIME ZONE 'UTC'",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "import_tasks",
        "import_start_time",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="import_start_time AT TIME ZONE 'UTC'",
    )
