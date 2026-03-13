"""Add yoga_asanas, video_references, and plan_yoga_asanas tables.

Revision ID: 0005
Revises: 0004
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "yoga_asanas",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_sanskrit", sa.String(200)),
        sa.Column("category", sa.String(80)),
        sa.Column("level", sa.String(30)),
        sa.Column("description", sa.Text),
        sa.Column("instructions", sa.JSON),
        sa.Column("benefits", sa.Text),
        sa.Column("dosha_effect", sa.String(200)),
        sa.Column("therapeutic_focus", sa.JSON),
        sa.Column("modifications", sa.JSON),
        sa.Column("contraindications", sa.JSON),
        sa.Column("hold_duration", sa.String(100)),
        sa.Column("repetitions", sa.String(100)),
        sa.Column("image_url", sa.String(500)),
        sa.Column("is_community", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "video_references",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("platform", sa.String(20)),
        sa.Column("embed_url", sa.String(500)),
        sa.Column("thumbnail_url", sa.String(500)),
        sa.Column("duration_display", sa.String(20)),
        sa.Column("language", sa.String(50), default="English"),
        sa.Column("source_name", sa.String(200)),
        sa.Column("is_primary", sa.Boolean, default=False),
        sa.Column("entity_type", sa.String(50), nullable=False, index=True),
        sa.Column("entity_id", sa.Integer, nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "plan_yoga_asanas",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("plan_id", sa.Integer, sa.ForeignKey("consultation_plans.id"), nullable=False, index=True),
        sa.Column("asana_id", sa.Integer, sa.ForeignKey("yoga_asanas.id"), nullable=False),
        sa.Column("frequency", sa.String(100)),
        sa.Column("notes", sa.Text),
    )


def downgrade() -> None:
    op.drop_table("plan_yoga_asanas")
    op.drop_table("video_references")
    op.drop_table("yoga_asanas")
