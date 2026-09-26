"""
SQLAlchemy ORM Models & Dual-Mode Database Engine (SQLite / PostgreSQL)
Supports seamless migration from embedded SQLite to production PostgreSQL via Alembic.
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./aiia_app.db")

# SQLite requires check_same_thread=False for async FastAPI concurrency
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Trial(Base):
    __tablename__ = "ayur_trials_orm"

    id = Column(Integer, primary_key=True, index=True)
    trial_id = Column(String(50), unique=True, index=True, nullable=False)
    trial_name = Column(String(255), nullable=False)
    condition = Column(String(100), index=True)
    phase = Column(String(50))
    status = Column(String(50), default="Recruiting")
    lead_institution = Column(String(255), default="All India Institute of Ayurveda (AIIA)")
    target_participants = Column(Integer, default=50)
    enrolled_participants = Column(Integer, default=0)
    start_date = Column(String(50))
    completion_date = Column(String(50))
    ctri_number = Column(String(100), unique=True)


class AdverseEvent(Base):
    __tablename__ = "ayur_adverse_events_orm"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), unique=True, index=True)
    patient_id = Column(String(50), index=True)
    patient_name = Column(String(100))
    trial_id = Column(String(50), index=True)
    condition = Column(String(100))
    location = Column(String(100))
    adverse_event = Column(String(200), nullable=False)
    severity = Column(String(50), default="Mild")
    serious = Column(String(10), default="No")
    suspected_treatment = Column(String(255))
    date_reported = Column(String(50))
    action_taken = Column(Text)
    outcome = Column(String(100))
    reported_by = Column(String(100))
    status = Column(String(50), default="Under Investigation")


class Approval(Base):
    __tablename__ = "ayur_approvals_orm"

    id = Column(Integer, primary_key=True, index=True)
    approval_id = Column(String(50), unique=True, index=True)
    trial_id = Column(String(50), index=True)
    city = Column(String(100))
    hospital_name = Column(String(255))
    approval_type = Column(String(100))
    status = Column(String(50), default="PENDING")
    submission_date = Column(String(50))
    decision_date = Column(String(50))
    reviewer_notes = Column(Text)
    action_required = Column(String(255))
    signature_id = Column(String(100))
    signature_hash = Column(String(100))
    signed_by = Column(String(100))
    signed_at = Column(String(50))
    signing_intent = Column(Text)


class ESignature(Base):
    __tablename__ = "esignatures_orm"

    id = Column(Integer, primary_key=True, index=True)
    signature_id = Column(String(100), unique=True, index=True)
    record_type = Column(String(50), index=True)
    record_id = Column(String(100), index=True)
    signer_name = Column(String(100))
    signer_role = Column(String(100))
    intent = Column(Text)
    signed_at = Column(String(50))
    signature_hash = Column(String(64))
    previous_signature_hash = Column(String(64))
    verification_status = Column(String(50), default="VALID")


def init_orm_tables():
    """Initializes tables via SQLAlchemy metadata."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for obtaining an ORM database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
