"""
Therapy services, service packages, and plan assignments.
"""
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, DateTime, Date, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Therapy(Base):
    """Master therapy/service library. Shared or practitioner-owned."""
    __tablename__ = "therapies"

    id:               Mapped[int]        = mapped_column(primary_key=True)
    practitioner_id:  Mapped[int | None] = mapped_column(ForeignKey("practitioners.id"), nullable=True)
    name:             Mapped[str]        = mapped_column(String(200), nullable=False)
    name_sanskrit:    Mapped[str | None] = mapped_column(String(200))
    description:      Mapped[str | None] = mapped_column(Text)
    category:         Mapped[str | None] = mapped_column(String(80))     # Massage, Head Therapy, Steam, Facial, Prenatal, Detox, Exfoliating
    default_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    default_price_cents:      Mapped[int | None] = mapped_column(Integer)
    benefits:         Mapped[list | None] = mapped_column(JSON)
    contraindications: Mapped[list | None] = mapped_column(JSON)
    dosha_effect:     Mapped[str | None] = mapped_column(String(200))
    image_url:        Mapped[str | None] = mapped_column(String(500))
    is_community:     Mapped[bool]       = mapped_column(Boolean, default=True)
    is_active:        Mapped[bool]       = mapped_column(Boolean, default=True)
    created_at:       Mapped[datetime]   = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    practitioner: Mapped["Practitioner | None"] = relationship()  # noqa: F821


class ServicePackage(Base):
    """A bundle of therapies offered as a package."""
    __tablename__ = "service_packages"

    id:               Mapped[int]        = mapped_column(primary_key=True)
    practitioner_id:  Mapped[int | None] = mapped_column(ForeignKey("practitioners.id"), nullable=True)
    name:             Mapped[str]        = mapped_column(String(200), nullable=False)
    description:      Mapped[str | None] = mapped_column(Text)
    category:         Mapped[str | None] = mapped_column(String(80))     # Combination, Pampering, Panchakarma
    total_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    total_price_cents:      Mapped[int | None] = mapped_column(Integer)
    includes_extras:  Mapped[list | None] = mapped_column(JSON)          # ["consultation", "lunch", "tea"]
    panchakarma_days: Mapped[int | None] = mapped_column(Integer)
    image_url:        Mapped[str | None] = mapped_column(String(500))
    is_community:     Mapped[bool]       = mapped_column(Boolean, default=True)
    is_active:        Mapped[bool]       = mapped_column(Boolean, default=True)
    created_at:       Mapped[datetime]   = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    practitioner: Mapped["Practitioner | None"] = relationship()  # noqa: F821
    package_therapies: Mapped[list["PackageTherapy"]] = relationship(back_populates="package", cascade="all, delete-orphan")


class PackageTherapy(Base):
    """Junction: which therapies belong to a package."""
    __tablename__ = "package_therapies"

    id:          Mapped[int]        = mapped_column(primary_key=True)
    package_id:  Mapped[int]        = mapped_column(ForeignKey("service_packages.id"), nullable=False)
    therapy_id:  Mapped[int]        = mapped_column(ForeignKey("therapies.id"), nullable=False)
    sort_order:  Mapped[int]        = mapped_column(Integer, default=0)
    override_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    notes:       Mapped[str | None] = mapped_column(String(500))

    package: Mapped["ServicePackage"] = relationship(back_populates="package_therapies")
    therapy: Mapped["Therapy"]        = relationship()


class PlanTherapy(Base):
    """Individual therapy assigned to a patient's consultation plan."""
    __tablename__ = "plan_therapies"

    id:             Mapped[int]         = mapped_column(primary_key=True)
    plan_id:        Mapped[int]         = mapped_column(ForeignKey("consultation_plans.id"), nullable=False, index=True)
    therapy_id:     Mapped[int]         = mapped_column(ForeignKey("therapies.id"), nullable=False)
    frequency:      Mapped[str | None]  = mapped_column(String(100))
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    price_cents:    Mapped[int | None]  = mapped_column(Integer)
    notes:          Mapped[str | None]  = mapped_column(Text)
    sort_order:     Mapped[int]         = mapped_column(Integer, default=0)
    scheduled_date: Mapped[date | None] = mapped_column(Date)

    plan:    Mapped["ConsultationPlan"] = relationship()  # noqa: F821
    therapy: Mapped["Therapy"]          = relationship()


class PlanServicePackage(Base):
    """Package assigned to a patient's consultation plan."""
    __tablename__ = "plan_service_packages"

    id:          Mapped[int]         = mapped_column(primary_key=True)
    plan_id:     Mapped[int]         = mapped_column(ForeignKey("consultation_plans.id"), nullable=False, index=True)
    package_id:  Mapped[int]         = mapped_column(ForeignKey("service_packages.id"), nullable=False)
    price_cents: Mapped[int | None]  = mapped_column(Integer)
    start_date:  Mapped[date | None] = mapped_column(Date)
    notes:       Mapped[str | None]  = mapped_column(Text)
    sort_order:  Mapped[int]         = mapped_column(Integer, default=0)

    plan:    Mapped["ConsultationPlan"] = relationship()  # noqa: F821
    package: Mapped["ServicePackage"]   = relationship()
