"""
Dosha Assessment routes — create, list, and retrieve structured assessments.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_practitioner
from app.models.practitioner import Practitioner
from app.models.patient import Patient, HealthProfile
from app.models.dosha_assessment import DoshaAssessment

router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────────────────

class PrakritiData(BaseModel):
    vata: int
    pitta: int
    kapha: int
    responses: dict

class VikritiData(BaseModel):
    vata: int
    pitta: int
    kapha: int
    responses: dict

class AgniAmaData(BaseModel):
    agni_type: str
    ama_level: str
    agni_responses: dict | None = None
    ama_responses: dict | None = None

class AssessmentCreate(BaseModel):
    patient_id: int
    prakriti: PrakritiData | None = None
    vikriti: VikritiData | None = None
    agni_ama: AgniAmaData | None = None
    ashtavidha: dict | None = None
    notes: str | None = None


# ── Helpers ────────────────────────────────────────────────────────────────

def _compute_dosha_label(v: int, p: int, k: int) -> str:
    """Determine dosha type from scores."""
    total = v + p + k
    if total == 0:
        return "Unknown"
    pcts = {"Vata": v / total, "Pitta": p / total, "Kapha": k / total}
    sorted_doshas = sorted(pcts.items(), key=lambda x: -x[1])

    # If top dosha is >50%, it's dominant
    if sorted_doshas[0][1] >= 0.50:
        # If second dosha is >30%, it's dual
        if sorted_doshas[1][1] >= 0.30:
            return f"{sorted_doshas[0][0]}-{sorted_doshas[1][0]}"
        return sorted_doshas[0][0]
    # If top two are close (within 10%), dual
    if abs(sorted_doshas[0][1] - sorted_doshas[1][1]) <= 0.10:
        # If all three are close, tridoshic
        if abs(sorted_doshas[1][1] - sorted_doshas[2][1]) <= 0.10:
            return "Tridoshic"
        return f"{sorted_doshas[0][0]}-{sorted_doshas[1][0]}"
    return sorted_doshas[0][0]


def _assessment_dict(a: DoshaAssessment) -> dict:
    return {
        "id": a.id,
        "patient_id": a.patient_id,
        "practitioner_id": a.practitioner_id,
        "prakriti": {
            "vata": a.prakriti_vata,
            "pitta": a.prakriti_pitta,
            "kapha": a.prakriti_kapha,
            "responses": a.prakriti_responses,
        } if a.prakriti_vata is not None else None,
        "vikriti": {
            "vata": a.vikriti_vata,
            "pitta": a.vikriti_pitta,
            "kapha": a.vikriti_kapha,
            "responses": a.vikriti_responses,
        } if a.vikriti_vata is not None else None,
        "agni_type": a.agni_type,
        "ama_level": a.ama_level,
        "agni_responses": a.agni_responses,
        "ama_responses": a.ama_responses,
        "ashtavidha": a.ashtavidha_responses,
        "result_prakriti": a.result_prakriti,
        "result_vikriti": a.result_vikriti,
        "notes": a.notes,
        "created_at": a.created_at.isoformat(),
        "updated_at": a.updated_at.isoformat() if a.updated_at else None,
    }


# ── Routes ─────────────────────────────────────────────────────────────────

@router.get("/{patient_id}/assessments")
async def list_assessments(
    patient_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    """List all dosha assessments for a patient, newest first."""
    # Verify patient belongs to practitioner
    pat = await db.execute(
        select(Patient).where(Patient.id == patient_id, Patient.practitioner_id == practitioner.id)
    )
    if not pat.scalars().first():
        raise HTTPException(status_code=404, detail="Patient not found")

    result = await db.execute(
        select(DoshaAssessment)
        .where(DoshaAssessment.patient_id == patient_id)
        .order_by(DoshaAssessment.created_at.desc())
    )
    return [_assessment_dict(a) for a in result.scalars().all()]


@router.get("/{patient_id}/assessments/{assessment_id}")
async def get_assessment(
    patient_id: int,
    assessment_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DoshaAssessment).where(
            DoshaAssessment.id == assessment_id,
            DoshaAssessment.patient_id == patient_id,
            DoshaAssessment.practitioner_id == practitioner.id,
        )
    )
    a = result.scalars().first()
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return _assessment_dict(a)


@router.post("/{patient_id}/assessments", status_code=201)
async def create_assessment(
    patient_id: int,
    body: AssessmentCreate,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    """Create a new dosha assessment and auto-update the patient's health profile."""
    # Verify patient
    pat_result = await db.execute(
        select(Patient).where(Patient.id == patient_id, Patient.practitioner_id == practitioner.id)
    )
    if not pat_result.scalars().first():
        raise HTTPException(status_code=404, detail="Patient not found")

    assessment = DoshaAssessment(
        patient_id=patient_id,
        practitioner_id=practitioner.id,
        notes=body.notes,
    )

    # Prakriti
    if body.prakriti:
        assessment.prakriti_vata = body.prakriti.vata
        assessment.prakriti_pitta = body.prakriti.pitta
        assessment.prakriti_kapha = body.prakriti.kapha
        assessment.prakriti_responses = body.prakriti.responses
        assessment.result_prakriti = _compute_dosha_label(
            body.prakriti.vata, body.prakriti.pitta, body.prakriti.kapha
        )

    # Vikriti
    if body.vikriti:
        assessment.vikriti_vata = body.vikriti.vata
        assessment.vikriti_pitta = body.vikriti.pitta
        assessment.vikriti_kapha = body.vikriti.kapha
        assessment.vikriti_responses = body.vikriti.responses
        assessment.result_vikriti = _compute_dosha_label(
            body.vikriti.vata, body.vikriti.pitta, body.vikriti.kapha
        )

    # Agni & Ama
    if body.agni_ama:
        assessment.agni_type = body.agni_ama.agni_type
        assessment.ama_level = body.agni_ama.ama_level
        assessment.agni_responses = body.agni_ama.agni_responses
        assessment.ama_responses = body.agni_ama.ama_responses

    # Ashtavidha
    if body.ashtavidha:
        assessment.ashtavidha_responses = body.ashtavidha

    db.add(assessment)
    await db.flush()

    # ── Auto-update HealthProfile with latest assessment results ──────────
    hp_result = await db.execute(
        select(HealthProfile).where(HealthProfile.patient_id == patient_id)
    )
    hp = hp_result.scalars().first()
    if hp:
        if assessment.result_prakriti:
            hp.dosha_primary = assessment.result_prakriti
        if assessment.result_vikriti:
            hp.dosha_imbalances = f"Vikriti: {assessment.result_vikriti} (V:{assessment.vikriti_vata} P:{assessment.vikriti_pitta} K:{assessment.vikriti_kapha})"
        if assessment.agni_type:
            hp.agni_assessment = assessment.agni_type
        if assessment.ama_level:
            hp.ama_assessment = assessment.ama_level

        # Update ashtavidha notes
        if body.ashtavidha:
            for key in ["nadi", "jihwa", "mutra", "mala", "shabda", "sparsha", "drika", "akriti"]:
                val = body.ashtavidha.get(key)
                if val and isinstance(val, dict):
                    note_text = val.get("notes", "")
                    finding = val.get("finding", "")
                    combined = f"{finding}. {note_text}".strip(". ") if finding or note_text else None
                    if combined:
                        setattr(hp, f"{key}_notes", combined)

    return _assessment_dict(assessment)


@router.delete("/{patient_id}/assessments/{assessment_id}", status_code=204)
async def delete_assessment(
    patient_id: int,
    assessment_id: int,
    practitioner: Practitioner = Depends(get_current_practitioner),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DoshaAssessment).where(
            DoshaAssessment.id == assessment_id,
            DoshaAssessment.patient_id == patient_id,
            DoshaAssessment.practitioner_id == practitioner.id,
        )
    )
    a = result.scalars().first()
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")
    await db.delete(a)
