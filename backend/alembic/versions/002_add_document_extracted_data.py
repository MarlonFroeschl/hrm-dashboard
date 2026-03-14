"""Add extracted_data and matching_score to documents

Revision ID: 002
Revises: 001
Create Date: 2026-03-14

Columns added:
  - extracted_data  JSONB    nullable – structured key/value pairs parsed from document text
  - matching_score  FLOAT    nullable – relevance score produced by the AI matching pipeline
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("extracted_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("matching_score", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documents", "matching_score")
    op.drop_column("documents", "extracted_data")
