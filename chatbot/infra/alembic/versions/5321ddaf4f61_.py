"""replace pix_id with provider fields in pix_charge

Revision ID: 5321ddaf4f61
Revises: 14bac00ed167
Create Date: 2026-04-06 09:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5321ddaf4f61"
down_revision = "14bac00ed167"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pix_charge",
        sa.Column("provider", sa.String(), nullable=True),
    )
    op.add_column(
        "pix_charge",
        sa.Column("provider_id", sa.String(), nullable=True),
    )
    op.execute("UPDATE pix_charge SET provider = 'unknown', provider_id = pix_id")
    op.alter_column("pix_charge", "provider", nullable=False)
    op.alter_column("pix_charge", "provider_id", nullable=False)
    op.create_unique_constraint(
        "uq_pix_charge_provider_id", "pix_charge", ["provider_id"]
    )
    op.drop_constraint("pix_charge_pix_id_key", "pix_charge", type_="unique")
    op.drop_column("pix_charge", "pix_id")


def downgrade() -> None:
    op.add_column(
        "pix_charge",
        sa.Column("pix_id", sa.String(), nullable=True),
    )
    op.execute("UPDATE pix_charge SET pix_id = provider_id")
    op.alter_column("pix_charge", "pix_id", nullable=False)
    op.create_unique_constraint("pix_charge_pix_id_key", "pix_charge", ["pix_id"])
    op.drop_constraint("uq_pix_charge_provider_id", "pix_charge", type_="unique")
    op.drop_column("pix_charge", "provider_id")
    op.drop_column("pix_charge", "provider")
