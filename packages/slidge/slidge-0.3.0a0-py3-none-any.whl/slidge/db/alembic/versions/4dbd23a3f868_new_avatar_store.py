"""New avatar store

Revision ID: 4dbd23a3f868
Revises: 04cf35e3cf85
Create Date: 2025-04-14 21:57:49.030430

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4dbd23a3f868"
down_revision: Union[str, None] = "04cf35e3cf85"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("avatar", schema=None) as batch_op:
        batch_op.add_column(sa.Column("legacy_id", sa.String(), nullable=True))
        batch_op.create_unique_constraint("avatar_unique_legacy_id", ["legacy_id"])

    batch_op.execute("""
        UPDATE avatar
        SET legacy_id = contact.avatar_legacy_id
        FROM contact
        WHERE avatar.id = contact.avatar_id
    """)

    batch_op.execute("""
        UPDATE avatar
        SET legacy_id = room.avatar_legacy_id
        FROM room
        WHERE avatar.id = room.avatar_id
    """)

    with op.batch_alter_table("contact", schema=None) as batch_op:
        batch_op.drop_column("avatar_legacy_id")

    with op.batch_alter_table("room", schema=None) as batch_op:
        batch_op.drop_column("avatar_legacy_id")


def downgrade() -> None:
    with op.batch_alter_table("room", schema=None) as batch_op:
        batch_op.add_column(sa.Column("avatar_legacy_id", sa.VARCHAR(), nullable=True))

    with op.batch_alter_table("contact", schema=None) as batch_op:
        batch_op.add_column(sa.Column("avatar_legacy_id", sa.VARCHAR(), nullable=True))

    with op.batch_alter_table("avatar", schema=None) as batch_op:
        batch_op.drop_constraint("avatar_unique_legacy_id", type_="unique")
        batch_op.drop_column("legacy_id")
