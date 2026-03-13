"""Add dosha_assessments table and recipe authoring fields.

Revision ID: 0004
Revises: 0003
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Dosha Assessments ────────────────────────────────────────────────────
    op.create_table(
        "dosha_assessments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("patient_id", sa.Integer, sa.ForeignKey("patients.id"), nullable=False, index=True),
        sa.Column("practitioner_id", sa.Integer, sa.ForeignKey("practitioners.id"), nullable=False),
        # Prakriti
        sa.Column("prakriti_vata", sa.Integer),
        sa.Column("prakriti_pitta", sa.Integer),
        sa.Column("prakriti_kapha", sa.Integer),
        sa.Column("prakriti_responses", sa.JSON),
        # Vikriti
        sa.Column("vikriti_vata", sa.Integer),
        sa.Column("vikriti_pitta", sa.Integer),
        sa.Column("vikriti_kapha", sa.Integer),
        sa.Column("vikriti_responses", sa.JSON),
        # Agni & Ama
        sa.Column("agni_type", sa.String(30)),
        sa.Column("ama_level", sa.String(30)),
        sa.Column("agni_responses", sa.JSON),
        sa.Column("ama_responses", sa.JSON),
        # Ashtavidha
        sa.Column("ashtavidha_responses", sa.JSON),
        # Results
        sa.Column("result_prakriti", sa.String(30)),
        sa.Column("result_vikriti", sa.String(30)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── Recipe authoring extensions ──────────────────────────────────────────
    op.add_column("recipes", sa.Column("practitioner_id", sa.Integer, sa.ForeignKey("practitioners.id"), nullable=True))
    op.add_column("recipes", sa.Column("visibility", sa.String(20), server_default="community"))
    op.add_column("recipes", sa.Column("rasa", sa.String(100)))         # taste profile: sweet, sour, salty, etc.
    op.add_column("recipes", sa.Column("virya", sa.String(30)))         # heating / cooling
    op.add_column("recipes", sa.Column("vipaka", sa.String(30)))        # post-digestive effect
    op.add_column("recipes", sa.Column("category", sa.String(80)))      # Yavagu, Yusha, Kashaya, etc.
    op.add_column("recipes", sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_column("recipes", "created_at")
    op.drop_column("recipes", "category")
    op.drop_column("recipes", "vipaka")
    op.drop_column("recipes", "virya")
    op.drop_column("recipes", "rasa")
    op.drop_column("recipes", "visibility")
    op.drop_column("recipes", "practitioner_id")
    op.drop_table("dosha_assessments")
