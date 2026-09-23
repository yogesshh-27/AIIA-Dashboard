import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime,
    ForeignKey, Float, Index
)
from sqlalchemy.orm import relationship
from database import Base

# 1. ROLES
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    permissions_json = Column(Text, nullable=True)

    users = relationship("User", back_populates="role")

# 2. USERS
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    institution = Column(String(255), nullable=True, default="All India Institute of Ayurveda")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    role = relationship("Role", back_populates="users")

# 3. TRIALS
class Trial(Base):
    __tablename__ = "trials"

    id = Column(Integer, primary_key=True)  # Maps to CTRI Trial_ID
    ctri_number = Column(String(50), nullable=False, index=True)
    public_title = Column(Text, nullable=False)
    scientific_title = Column(Text, nullable=True)
    trial_acronym = Column(String(100), nullable=True)
    type_of_trial = Column(String(100), nullable=True, index=True)
    type_of_study = Column(String(150), nullable=True)
    study_design = Column(String(255), nullable=True)
    phase = Column(String(50), nullable=True, index=True)
    post_graduation_thesis = Column(String(10), nullable=True, index=True)
    recruitment_status = Column(String(100), nullable=True, index=True)
    registration_type = Column(String(100), nullable=True, index=True)
    registered_on = Column(Date, nullable=True, index=True)
    last_modified_on = Column(Date, nullable=True)
    date_first_enrollment = Column(Date, nullable=True)
    date_completion = Column(Date, nullable=True)
    target_sample_size = Column(Integer, nullable=True)
    brief_summary = Column(Text, nullable=True)
    dcgi_status = Column(String(100), nullable=True)
    is_aiia = Column(Boolean, default=False, index=True)
    is_ayush = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    sponsors = relationship("Sponsor", back_populates="trial", cascade="all, delete-orphan")
    study_sites = relationship("StudySite", back_populates="trial", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="trial", cascade="all, delete-orphan")
    outcomes = relationship("Outcome", back_populates="trial", cascade="all, delete-orphan")
    eligibility = relationship("Eligibility", back_populates="trial", uselist=False, cascade="all, delete-orphan")
    milestones = relationship("TrialMilestone", back_populates="trial", cascade="all, delete-orphan")
    enrollment_records = relationship("Enrollment", back_populates="trial", cascade="all, delete-orphan")
    visits = relationship("Visit", back_populates="trial", cascade="all, delete-orphan")
    protocol_deviations = relationship("ProtocolDeviation", back_populates="trial", cascade="all, delete-orphan")
    adverse_events = relationship("AdverseEvent", back_populates="trial", cascade="all, delete-orphan")
    safety_reports = relationship("SafetyReport", back_populates="trial", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="trial", cascade="all, delete-orphan")
    compliance_checks = relationship("ComplianceCheck", back_populates="trial", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="trial", cascade="all, delete-orphan")
    investigator_links = relationship("TrialInvestigator", back_populates="trial", cascade="all, delete-orphan")

# 4. INVESTIGATORS
class Investigator(Base):
    __tablename__ = "investigators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    designation = Column(String(255), nullable=True)
    affiliation = Column(Text, nullable=True, index=True)
    address = Column(Text, nullable=True)
    phone = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    is_aiia = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    trial_links = relationship("TrialInvestigator", back_populates="investigator")

class TrialInvestigator(Base):
    __tablename__ = "trial_investigators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    investigator_id = Column(Integer, ForeignKey("investigators.id"), nullable=False, index=True)
    role = Column(String(100), default="Principal Investigator")  # PI, Scientific Contact, Public Contact

    trial = relationship("Trial", back_populates="investigator_links")
    investigator = relationship("Investigator", back_populates="trial_links")

# 5. SPONSORS
class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    address = Column(Text, nullable=True)
    sponsor_type = Column(String(150), nullable=True)
    is_primary = Column(Boolean, default=True)

    trial = relationship("Trial", back_populates="sponsors")

# 6. STUDY SITES
class StudySite(Base):
    __tablename__ = "study_sites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    site_name = Column(Text, nullable=False, index=True)
    site_address = Column(Text, nullable=True)
    pi_name = Column(String(255), nullable=True)
    num_sites = Column(String(50), nullable=True)
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)

    trial = relationship("Trial", back_populates="study_sites")
    enrollment = relationship("Enrollment", back_populates="site")

# 7. INTERVENTIONS
class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    arm_type = Column(String(100), default="Intervention Arm")
    intervention_name = Column(Text, nullable=True, index=True)
    intervention_details = Column(Text, nullable=True)
    comparator_name = Column(Text, nullable=True)
    comparator_details = Column(Text, nullable=True)
    dosage_form = Column(String(100), nullable=True)

    trial = relationship("Trial", back_populates="interventions")

# 8. OUTCOMES
class Outcome(Base):
    __tablename__ = "outcomes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    outcome_type = Column(String(50), nullable=False, index=True)  # PRIMARY / SECONDARY
    outcome_name = Column(Text, nullable=False)
    timepoints = Column(Text, nullable=True)

    trial = relationship("Trial", back_populates="outcomes")

# 9. ELIGIBILITY
class Eligibility(Base):
    __tablename__ = "eligibility"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), unique=True, nullable=False, index=True)
    age_from = Column(String(50), nullable=True)
    age_to = Column(String(50), nullable=True)
    gender = Column(String(50), nullable=True)
    inclusion_details = Column(Text, nullable=True)
    exclusion_details = Column(Text, nullable=True)

    trial = relationship("Trial", back_populates="eligibility")

# 10. TRIAL MILESTONES
class TrialMilestone(Base):
    __tablename__ = "trial_milestones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    milestone_name = Column(String(150), nullable=False)  # Protocol Approval, First Patient In, LPI, LPO
    target_date = Column(Date, nullable=True)
    achieved_date = Column(Date, nullable=True)
    status = Column(String(50), default="PLANNED")  # PLANNED, ACHIEVED, DELAYED
    remarks = Column(Text, nullable=True)

    trial = relationship("Trial", back_populates="milestones")

# 11. ENROLLMENT
class Enrollment(Base):
    __tablename__ = "enrollment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("study_sites.id"), nullable=True)
    target_enrollment = Column(Integer, nullable=True)
    actual_enrolled = Column(Integer, nullable=True, default=0)
    screened = Column(Integer, nullable=True, default=0)
    withdrawn = Column(Integer, nullable=True, default=0)
    last_updated = Column(Date, nullable=True)

    trial = relationship("Trial", back_populates="enrollment_records")
    site = relationship("StudySite", back_populates="enrollment")

# 12. VISITS
class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    visit_name = Column(String(100), nullable=False)  # Baseline, Day 14, Month 1, Month 3, End of Study
    visit_number = Column(Integer, nullable=False)
    window_days = Column(Integer, nullable=True, default=0)
    required_assessments = Column(Text, nullable=True)

    trial = relationship("Trial", back_populates="visits")

# 13. PROTOCOL DEVIATIONS
class ProtocolDeviation(Base):
    __tablename__ = "protocol_deviations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    deviation_code = Column(String(50), nullable=True)
    category = Column(String(100), nullable=False)  # Inclusion/Exclusion, Visit Schedule, Dosage, Consent
    severity = Column(String(50), default="MINOR")  # MINOR, MAJOR, CRITICAL
    description = Column(Text, nullable=False)
    date_identified = Column(Date, nullable=True)
    reported_by = Column(String(150), nullable=True)
    resolution_status = Column(String(50), default="OPEN")  # OPEN, RESOLVED, WAIVED

    trial = relationship("Trial", back_populates="protocol_deviations")

# 14. ADVERSE EVENTS
class AdverseEvent(Base):
    __tablename__ = "adverse_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    subject_id = Column(String(100), nullable=True)
    event_term = Column(String(255), nullable=False, index=True)
    onset_date = Column(Date, nullable=True)
    resolution_date = Column(Date, nullable=True)
    severity = Column(String(50), nullable=True)  # MILD, MODERATE, SEVERE
    causality = Column(String(50), nullable=True)  # UNRELATED, POSSIBLE, PROBABLE, DEFINITE
    is_serious = Column(Boolean, default=False, index=True)
    outcome = Column(String(100), nullable=True)  # RECOVERED, ONGOING, FATAL

    trial = relationship("Trial", back_populates="adverse_events")

# 15. SAFETY REPORTS
class SafetyReport(Base):
    __tablename__ = "safety_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    report_type = Column(String(100), nullable=False)  # DSMB Report, SUSAR, Annual Safety Summary
    reporting_period_start = Column(Date, nullable=True)
    reporting_period_end = Column(Date, nullable=True)
    submission_date = Column(Date, nullable=True)
    reviewed_by = Column(String(255), nullable=True)
    review_status = Column(String(50), default="SUBMITTED")  # SUBMITTED, REVIEWED, ACTION_REQUIRED

    trial = relationship("Trial", back_populates="safety_reports")

# 16. DOCUMENTS
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    document_type = Column(String(100), nullable=False)  # Protocol, IEC Approval, ICF, Clinical Study Report
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    version = Column(String(50), default="1.0")
    uploaded_by = Column(String(150), nullable=True)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)

    trial = relationship("Trial", back_populates="documents")

# 17. COMPLIANCE CHECKS
class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    check_type = Column(String(100), nullable=False)  # IEC_CLEARANCE, PROSPECTIVE_REGISTRATION, DCGI_AUDIT, etc.
    check_name = Column(String(150), nullable=True)  # e.g., 'CTRI Registration', 'IEC / Ethics Approval'
    status = Column(String(50), nullable=False)  # Compliant, Pending, Due Soon, Overdue, Non-Compliant
    score = Column(Float, nullable=True)
    findings = Column(Text, nullable=True)
    reason_rule = Column(Text, nullable=True)  # Human-readable transparent rule rationale
    last_checked = Column(DateTime, default=datetime.datetime.utcnow)
    due_date = Column(Date, nullable=True)
    responsible_role = Column(String(150), nullable=True)
    action_label = Column(String(200), nullable=True)
    checked_at = Column(DateTime, default=datetime.datetime.utcnow)
    checked_by = Column(String(150), nullable=True, default="SYSTEM_AUDITOR")

    trial = relationship("Trial", back_populates="compliance_checks")

# 18. ALERTS
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    alert_type = Column(String(100), nullable=False)  # Category/Type identifier
    category = Column(String(100), nullable=True, index=True)  # Regulatory, CTRI, Ethics, Recruitment, Safety, Data Quality, Monitoring, System
    severity = Column(String(50), default="Medium", index=True)  # Critical, High, Medium, Low
    message = Column(Text, nullable=False)
    description = Column(Text, nullable=True)  # Detailed rationale / condition triggered
    created_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    responsible_role = Column(String(150), nullable=True)
    status = Column(String(50), default="Active", index=True)  # Active, Acknowledged, Resolved
    action_label = Column(String(200), nullable=True)  # e.g., 'Review Submission', 'Acknowledge'
    is_resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(150), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    trial = relationship("Trial", back_populates="alerts")

# 19. AUDIT LOGS
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_name = Column(String(100), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, IMPORT
    changed_by = Column(String(150), nullable=True)
    changes_json = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

# 20. CDISC MAPPINGS
class CDISCMapping(Base):
    __tablename__ = "cdisc_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    concept_code = Column(String(50), nullable=False, index=True)  # NCI C-Code e.g. C142649
    codelist_code = Column(String(50), nullable=True, index=True)
    term = Column(String(255), nullable=False, index=True)
    standard_name = Column(String(100), nullable=False, index=True)  # CDISC Glossary, Protocol, ADaM, SDTM, SEND
    definition = Column(Text, nullable=True)
    ctri_field_mapped = Column(String(100), nullable=True)


# ============================================================
# INTERNAL CTMS OPERATIONAL DATA LAYER (SYNTHETIC / DEMONSTRATION)
# ============================================================

# 21. CTMS TIMELINES (9-Stage Progression Pipeline)
class CTMSTimeline(Base):
    __tablename__ = "ctms_timelines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    ctri_number = Column(String(50), nullable=False, index=True)
    trial_title = Column(Text, nullable=False)
    
    # 9 Distinct CTMS Progression Stages
    stage_protocol_status = Column(String(50), default="Completed")  # Completed, In Progress, Upcoming, Due Soon, Overdue
    stage_protocol_date = Column(String(20), nullable=True)
    
    stage_iec_status = Column(String(50), default="Completed")
    stage_iec_date = Column(String(20), nullable=True)
    
    stage_ctri_status = Column(String(50), default="Completed")
    stage_ctri_date = Column(String(20), nullable=True)
    
    stage_activation_status = Column(String(50), default="Completed")
    stage_activation_date = Column(String(20), nullable=True)
    
    stage_recruitment_status = Column(String(50), default="In Progress")
    stage_recruitment_date = Column(String(20), nullable=True)
    
    stage_monitoring_status = Column(String(50), default="In Progress")
    stage_monitoring_date = Column(String(20), nullable=True)
    
    stage_followup_status = Column(String(50), default="Upcoming")
    stage_followup_date = Column(String(20), nullable=True)
    
    stage_dblock_status = Column(String(50), default="Upcoming")
    stage_dblock_date = Column(String(20), nullable=True)
    
    stage_closeout_status = Column(String(50), default="Upcoming")
    stage_closeout_date = Column(String(20), nullable=True)
    
    overall_status = Column(String(50), default="In Progress")
    is_synthetic = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# 22. CTMS RECRUITMENT VELOCITY & TARGETS
class CTMSRecruitment(Base):
    __tablename__ = "ctms_recruitment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    ctri_number = Column(String(50), nullable=False, index=True)
    trial_title = Column(Text, nullable=False)
    
    target_enrollment = Column(Integer, nullable=False)
    current_enrollment = Column(Integer, nullable=False, default=0)
    enrollment_pct = Column(Float, nullable=False, default=0.0)
    expected_enrollment = Column(Integer, nullable=False)
    enrollment_gap = Column(Integer, nullable=False, default=0)
    
    monthly_trend_json = Column(Text, nullable=True)  # JSON array of {month, actual, projected}
    is_synthetic = Column(Boolean, default=True, index=True)
    last_updated = Column(String(20), nullable=True)


# 23. CTMS CLINICAL MONITORING VISITS
class CTMSMonitoringVisit(Base):
    __tablename__ = "ctms_monitoring_visits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    visit_code = Column(String(50), nullable=False, index=True)  # e.g. IMV-01, SIV-01
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    ctri_number = Column(String(50), nullable=False, index=True)
    trial_title = Column(Text, nullable=False)
    
    site_name = Column(String(255), nullable=False)
    monitor_name = Column(String(150), nullable=False)
    visit_type = Column(String(100), default="Interim Monitoring Visit (IMV)")
    planned_date = Column(String(20), nullable=False)
    actual_date = Column(String(20), nullable=True)
    status = Column(String(50), nullable=False)  # Scheduled, Completed, Overdue
    findings = Column(Text, nullable=True)
    is_synthetic = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# 24. CTMS PROTOCOL DEVIATIONS
class CTMSProtocolDeviation(Base):
    __tablename__ = "ctms_protocol_deviations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deviation_code = Column(String(50), nullable=False, index=True)  # e.g. DEV-2022-001
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    ctri_number = Column(String(50), nullable=False, index=True)
    trial_title = Column(Text, nullable=False)
    
    site_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # Informed Consent, Eligibility, IP, Visit Window, Safety, Procedure
    description = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False)  # Minor, Major, Critical
    date_identified = Column(String(20), nullable=False)
    status = Column(String(50), default="Open")  # Open, Under Investigation, Resolved, Closed
    resolution = Column(Text, nullable=True)
    is_synthetic = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# 25. CTMS MILESTONES (Automated Overdue Detection)
class CTMSMilestone(Base):
    __tablename__ = "ctms_milestones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    milestone_code = Column(String(50), nullable=False, index=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False, index=True)
    ctri_number = Column(String(50), nullable=False, index=True)
    trial_title = Column(Text, nullable=False)
    
    milestone_name = Column(String(200), nullable=False)
    due_date = Column(String(20), nullable=False)
    status = Column(String(50), nullable=False)  # Completed, Pending, Due Soon, Overdue
    responsible_role = Column(String(100), nullable=False)  # PI, CRC, Ethics Secretary, Lead CRA, Data Manager
    is_overdue = Column(Boolean, default=False, index=True)
    is_synthetic = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

