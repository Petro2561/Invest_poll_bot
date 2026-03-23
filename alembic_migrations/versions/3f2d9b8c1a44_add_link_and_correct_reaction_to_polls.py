"""add link and correct reaction to polls

Revision ID: 3f2d9b8c1a44
Revises: b581d5957776
Create Date: 2026-03-23 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3f2d9b8c1a44"
down_revision: Union[str, None] = "b581d5957776"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("polls", sa.Column("link", sa.Text(), nullable=True))
    op.add_column(
        "polls",
        sa.Column("correct_answer_reaction", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("polls", "correct_answer_reaction")
    op.drop_column("polls", "link")
