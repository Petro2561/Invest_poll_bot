"""initial

Revision ID: b581d5957776
Revises:
Create Date: 2026-02-20 15:32:06.357025

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "b581d5957776"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    user_columns = {
        column["name"] for column in inspector.get_columns("users")
    }
    if "questions_completed" not in user_columns:
        op.add_column(
            "users",
            sa.Column(
                "questions_completed",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
        )
        op.alter_column(
            "users", "questions_completed", server_default=None
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    user_columns = {
        column["name"] for column in inspector.get_columns("users")
    }
    if "questions_completed" in user_columns:
        op.drop_column("users", "questions_completed")
