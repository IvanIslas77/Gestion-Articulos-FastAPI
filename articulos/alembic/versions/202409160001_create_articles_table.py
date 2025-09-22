"""Crea la tabla articles"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revisiones de Alembic.
revision: str = "202409160001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("title", "author", name="uq_articles_title_author"),
    )
    op.create_index("ix_articles_author", "articles", ["author"], unique=False)
    op.create_index("ix_articles_published_at", "articles", ["published_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_articles_published_at", table_name="articles")
    op.drop_index("ix_articles_author", table_name="articles")
    op.drop_table("articles")
