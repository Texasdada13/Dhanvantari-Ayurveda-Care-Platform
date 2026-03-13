"""
Dosha Assessment model — structured Prakriti / Vikriti / Agni / Ama / Ashtavidha scoring.
"""
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class DoshaAssessment(Base):
    __tablename__ = "dosha_assessments"

    id:              Mapped[int] = mapped_column(primary_key=True)
    patient_id:      Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False, index=True)
    practitioner_id: Mapped[int] = mapped_column(ForeignKey("practitioners.id"), nullable=False)

    # Prakriti (constitutional) scores out of 20
    prakriti_vata:      Mapped[int | None] = mapped_column(Integer)
    prakriti_pitta:     Mapped[int | None] = mapped_column(Integer)
    prakriti_kapha:     Mapped[int | None] = mapped_column(Integer)
    prakriti_responses: Mapped[dict | None] = mapped_column(JSON)     # {q1: "vata", q2: "pitta", ...}

    # Vikriti (current imbalance) scores
    vikriti_vata:      Mapped[int | None] = mapped_column(Integer)
    vikriti_pitta:     Mapped[int | None] = mapped_column(Integer)
    vikriti_kapha:     Mapped[int | None] = mapped_column(Integer)
    vikriti_responses: Mapped[dict | None] = mapped_column(JSON)     # {symptom: severity, ...}

    # Agni & Ama
    agni_type:     Mapped[str | None] = mapped_column(String(30))    # Samagni / Vishama / Tikshna / Manda
    ama_level:     Mapped[str | None] = mapped_column(String(30))    # None / Mild / Moderate / Severe
    agni_responses: Mapped[dict | None] = mapped_column(JSON)
    ama_responses:  Mapped[dict | None] = mapped_column(JSON)

    # Ashtavidha Pareeksha (8-fold exam)
    ashtavidha_responses: Mapped[dict | None] = mapped_column(JSON)  # {nadi: {...}, jihwa: {...}, ...}

    # Computed results
    result_prakriti: Mapped[str | None] = mapped_column(String(30))  # e.g. "Vata-Pitta"
    result_vikriti:  Mapped[str | None] = mapped_column(String(30))

    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    patient:      Mapped["Patient"]      = relationship()  # noqa: F821
    practitioner: Mapped["Practitioner"] = relationship()  # noqa: F821
