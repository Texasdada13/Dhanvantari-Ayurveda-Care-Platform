"""Initial schema — all tables

Revision ID: 0001
Revises:
Create Date: 2026-03-12
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── practitioners ─────────────────────────────────────────────────────────
    op.create_table(
        "practitioners",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(200), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("practice_name", sa.String(200)),
        sa.Column("practice_logo_url", sa.String(500)),
        sa.Column("tagline", sa.String(300)),
        sa.Column("bio", sa.Text),
        sa.Column("designation", sa.String(50)),
        sa.Column("location", sa.String(200)),
        sa.Column("telehealth_url", sa.String(500)),
        sa.Column("website", sa.String(500)),
        sa.Column("stripe_customer_id", sa.String(100), unique=True),
        sa.Column("stripe_subscription_id", sa.String(100), unique=True),
        sa.Column("subscription_tier", sa.String(20), nullable=False, server_default="free"),
        sa.Column("subscription_active", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True)),
        sa.Column("email_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_admin", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_practitioners_email", "practitioners", ["email"], unique=True)

    # ── patients ──────────────────────────────────────────────────────────────
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("practitioner_id", sa.Integer, sa.ForeignKey("practitioners.id"), nullable=False),
        sa.Column("first_name", sa.String(80), nullable=False),
        sa.Column("last_name", sa.String(80), nullable=False),
        sa.Column("dob", sa.Date),
        sa.Column("sex", sa.String(10)),
        sa.Column("location", sa.String(200)),
        sa.Column("occupation", sa.String(200)),
        sa.Column("phone", sa.String(30)),
        sa.Column("email", sa.String(200)),
        sa.Column("weight_lbs", sa.Float),
        sa.Column("weight_note", sa.String(200)),
        sa.Column("height_in", sa.Float),
        sa.Column("exercise_notes", sa.Text),
        sa.Column("diet_pattern", sa.Text),
        sa.Column("alcohol_notes", sa.String(200)),
        sa.Column("caffeine_notes", sa.String(200)),
        sa.Column("sleep_notes", sa.String(200)),
        sa.Column("stress_level", sa.String(20)),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_patients_practitioner_id", "patients", ["practitioner_id"])

    # ── health_profiles ───────────────────────────────────────────────────────
    op.create_table(
        "health_profiles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("patient_id", sa.Integer, sa.ForeignKey("patients.id"), nullable=False, unique=True),
        # Chief complaint
        sa.Column("chief_complaint", sa.Text),
        sa.Column("current_conditions", sa.Text),
        sa.Column("medications", sa.Text),
        sa.Column("allergies", sa.Text),
        sa.Column("surgical_history", sa.Text),
        sa.Column("family_history", sa.Text),
        # Vitals
        sa.Column("bp_systolic", sa.Integer),
        sa.Column("bp_diastolic", sa.Integer),
        sa.Column("heart_rate", sa.Integer),
        sa.Column("temperature_f", sa.Float),
        sa.Column("spo2_pct", sa.Float),
        # Ayurvedic assessment
        sa.Column("prakriti", sa.String(30)),
        sa.Column("vikriti", sa.String(30)),
        sa.Column("agni", sa.String(50)),
        sa.Column("ama_level", sa.String(50)),
        sa.Column("ojas_level", sa.String(50)),
        # Ashtavidha Pareeksha (8-fold examination)
        sa.Column("nadi_notes", sa.Text),
        sa.Column("jihwa_notes", sa.Text),
        sa.Column("mutra_notes", sa.Text),
        sa.Column("mala_notes", sa.Text),
        sa.Column("shabda_notes", sa.Text),
        sa.Column("sparsha_notes", sa.Text),
        sa.Column("drika_notes", sa.Text),
        sa.Column("akriti_notes", sa.Text),
        # Labs
        sa.Column("hba1c", sa.Float),
        sa.Column("fasting_glucose", sa.Float),
        sa.Column("total_cholesterol", sa.Float),
        sa.Column("hdl", sa.Float),
        sa.Column("ldl", sa.Float),
        sa.Column("triglycerides", sa.Float),
        sa.Column("tsh", sa.Float),
        sa.Column("vitamin_d", sa.Float),
        sa.Column("vitamin_b12", sa.Float),
        sa.Column("creatinine", sa.Float),
        sa.Column("lab_notes", sa.Text),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── supplements ───────────────────────────────────────────────────────────
    op.create_table(
        "supplements",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("name_sanskrit", sa.String(200)),
        sa.Column("brand", sa.String(200)),
        sa.Column("category", sa.String(80)),
        sa.Column("purpose", sa.Text),
        sa.Column("dosha_effect", sa.String(100)),
        sa.Column("typical_dose", sa.String(200)),
        sa.Column("cautions", sa.Text),
        sa.Column("contraindications", sa.Text),
        sa.Column("source_url", sa.String(500)),
        sa.Column("notes", sa.Text),
        sa.Column("is_classical", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_community", sa.Boolean, nullable=False, server_default="true"),
    )

    # ── recipes ───────────────────────────────────────────────────────────────
    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("meal_type", sa.String(50)),
        sa.Column("dosha_good_for", sa.String(100)),
        sa.Column("dosha_avoid", sa.String(100)),
        sa.Column("ingredients", sa.Text),
        sa.Column("instructions", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("is_tea", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_community", sa.Boolean, nullable=False, server_default="true"),
    )

    # ── consultation_plans ────────────────────────────────────────────────────
    op.create_table(
        "consultation_plans",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("patient_id", sa.Integer, sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("title", sa.String(200), server_default="Initial Protocol"),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("duration_weeks", sa.Integer),
        sa.Column("start_date", sa.Date),
        sa.Column("end_date", sa.Date),
        sa.Column("foods_to_avoid", sa.Text),
        sa.Column("foods_to_include", sa.Text),
        sa.Column("lifestyle_notes", sa.Text),
        sa.Column("breathing_notes", sa.Text),
        sa.Column("nasal_care_notes", sa.Text),
        sa.Column("followup_notes", sa.Text),
        sa.Column("ai_rationale", sa.Text),
        sa.Column("ai_generated_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_consultation_plans_patient_id", "consultation_plans", ["patient_id"])

    # ── plan_supplements ──────────────────────────────────────────────────────
    op.create_table(
        "plan_supplements",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("plan_id", sa.Integer, sa.ForeignKey("consultation_plans.id"), nullable=False),
        sa.Column("supplement_id", sa.Integer, sa.ForeignKey("supplements.id"), nullable=False),
        sa.Column("dose", sa.String(100)),
        sa.Column("timing", sa.String(100)),
        sa.Column("frequency", sa.String(100)),
        sa.Column("special_notes", sa.Text),
    )

    # ── plan_recipes ──────────────────────────────────────────────────────────
    op.create_table(
        "plan_recipes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("plan_id", sa.Integer, sa.ForeignKey("consultation_plans.id"), nullable=False),
        sa.Column("recipe_id", sa.Integer, sa.ForeignKey("recipes.id"), nullable=False),
        sa.Column("meal_slot", sa.String(50)),
    )

    # ── checkin_tokens ────────────────────────────────────────────────────────
    op.create_table(
        "checkin_tokens",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("patient_id", sa.Integer, sa.ForeignKey("patients.id"), nullable=False, unique=True),
        sa.Column("token", sa.String(128), nullable=False, unique=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── daily_checkins ────────────────────────────────────────────────────────
    op.create_table(
        "daily_checkins",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("patient_id", sa.Integer, sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        # Morning routine
        sa.Column("warm_water", sa.Boolean, server_default="false"),
        sa.Column("breathing_exercise", sa.Boolean, server_default="false"),
        sa.Column("nasal_oil", sa.Boolean, server_default="false"),
        # Meals
        sa.Column("warm_breakfast", sa.Boolean, server_default="false"),
        sa.Column("avoided_cold_food", sa.Boolean, server_default="false"),
        sa.Column("avoided_yogurt", sa.Boolean, server_default="false"),
        sa.Column("herbal_tea_am", sa.Boolean, server_default="false"),
        sa.Column("warm_lunch", sa.Boolean, server_default="false"),
        sa.Column("included_barley", sa.Boolean, server_default="false"),
        sa.Column("no_cold_drinks", sa.Boolean, server_default="false"),
        sa.Column("warm_dinner", sa.Boolean, server_default="false"),
        sa.Column("dinner_before_8pm", sa.Boolean, server_default="false"),
        # Supplements
        sa.Column("supplements_am", sa.Boolean, server_default="false"),
        sa.Column("supplements_pm", sa.Boolean, server_default="false"),
        # Lifestyle
        sa.Column("cardio_today", sa.Boolean, server_default="false"),
        sa.Column("consistent_sleep", sa.Boolean, server_default="false"),
        # Symptom scores
        sa.Column("digestion_score", sa.Integer),
        sa.Column("urinary_score", sa.Integer),
        sa.Column("sinus_score", sa.Integer),
        sa.Column("energy_score", sa.Integer),
        sa.Column("notes", sa.Text),
    )
    op.create_index("ix_daily_checkins_patient_id", "daily_checkins", ["patient_id"])

    # ── followups ─────────────────────────────────────────────────────────────
    op.create_table(
        "followups",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("patient_id", sa.Integer, sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("practitioner_id", sa.Integer, sa.ForeignKey("practitioners.id"), nullable=False),
        sa.Column("scheduled_date", sa.Date, nullable=False),
        sa.Column("reason", sa.String(300)),
        sa.Column("notes", sa.Text),
        sa.Column("completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_followups_practitioner_id", "followups", ["practitioner_id"])
    op.create_index("ix_followups_patient_id", "followups", ["patient_id"])

    # ── subscriptions ─────────────────────────────────────────────────────────
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("practitioner_id", sa.Integer, sa.ForeignKey("practitioners.id"), nullable=False, unique=True),
        sa.Column("stripe_subscription_id", sa.String(100), unique=True),
        sa.Column("stripe_price_id", sa.String(100)),
        sa.Column("tier", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="trialing"),
        sa.Column("current_period_start", sa.DateTime(timezone=True)),
        sa.Column("current_period_end", sa.DateTime(timezone=True)),
        sa.Column("cancel_at_period_end", sa.Boolean, server_default="false"),
        sa.Column("trial_end", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("subscriptions")
    op.drop_table("followups")
    op.drop_table("daily_checkins")
    op.drop_table("checkin_tokens")
    op.drop_table("plan_recipes")
    op.drop_table("plan_supplements")
    op.drop_table("consultation_plans")
    op.drop_table("recipes")
    op.drop_table("supplements")
    op.drop_table("health_profiles")
    op.drop_table("patients")
    op.drop_table("practitioners")
