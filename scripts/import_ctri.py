import os
import sys
import sqlite3
import argparse
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, SessionLocal, Base
import models

# Set up logging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "import_ctri.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("import_ctri")

# Normalization helpers
def parse_date(date_str: Optional[str]) -> Optional[datetime.date]:
    if not date_str:
        return None
    cleaned = date_str.strip()
    if not cleaned or cleaned in ("NA", "character(0)", "N/A"):
        return None
    # Common format in CTRI: DD/MM/YYYY
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", cleaned)
    if m:
        try:
            day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
            return datetime(year, month, day).date()
        except ValueError:
            return None
    # Format: YYYY-MM-DD
    m2 = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", cleaned)
    if m2:
        try:
            year, month, day = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
            return datetime(year, month, day).date()
        except ValueError:
            return None
    # Format: DD-MM-YYYY
    m3 = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})$", cleaned)
    if m3:
        try:
            day, month, year = int(m3.group(1)), int(m3.group(2)), int(m3.group(3))
            return datetime(year, month, day).date()
        except ValueError:
            return None
    return None

def parse_sample_size(raw: Optional[str]) -> Optional[int]:
    if not raw:
        return None
    # Pattern: Total Sample Size="400"
    m = re.search(r'Total Sample Size\s*=\s*"(\d+)"', raw, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    # Pure integer
    digits = re.search(r'(\d+)', raw)
    if digits:
        try:
            return int(digits.group(1))
        except ValueError:
            pass
    return None

def normalize_status(raw: Optional[str]) -> str:
    if not raw:
        return "Unspecified"
    s = raw.strip()
    if not s or s in ("NA", "character(0)"):
        return "Unspecified"
    if s == "Other (Terminated)":
        return "Terminated"
    if s == "Closed to Recruitment of Participants":
        return "Closed to Recruitment"
    return s

def check_aiia(texts: List[Optional[str]]) -> bool:
    for t in texts:
        if t:
            tl = t.lower()
            if "all india institute of ayurveda" in tl or "aiia" in tl:
                return True
    return False

def check_ayush(texts: List[Optional[str]]) -> bool:
    for t in texts:
        if t:
            tl = t.lower()
            if any(term in tl for term in ("ayurved", "ayush", "unani", "siddha", "homeopath", "yoga")):
                return True
    return False

def ingest_cdisc(db_session):
    import xlrd
    logger.info("Importing CDISC Controlled Terminology standards...")
    cdisc_files = [
        ("CDISC Glossary.xls", 1, "CDISC Glossary", "Glossary"),
        ("Protocol Terminology.xls", 1, "CDISC Protocol Standard", "Protocol"),
        ("ADaM Terminology.xls", 1, "CDISC ADaM Standard", "Analysis Data Model"),
        ("SDTM Terminology.xls", 1, "CDISC SDTM Standard", "Study Data Tabulation")
    ]
    total_cdisc = 0
    for fname, sheet_idx, standard_label, mapped_domain in cdisc_files:
        if not os.path.exists(fname):
            continue
        try:
            wb = xlrd.open_workbook(fname)
            if len(wb.sheet_names()) > sheet_idx:
                sheet = wb.sheet_by_index(sheet_idx)
                for r in range(1, min(sheet.nrows, 1500)):
                    vals = sheet.row_values(r)
                    code = str(vals[0]).strip() if len(vals) > 0 else ""
                    codelist = str(vals[1]).strip() if len(vals) > 1 else ""
                    term = str(vals[4]).strip() if len(vals) > 4 else (str(vals[3]).strip() if len(vals) > 3 else "")
                    definition = str(vals[7]).strip() if len(vals) > 7 else (str(vals[6]).strip() if len(vals) > 6 else "")
                    if code and term:
                        mapping = models.CDISCMapping(
                            concept_code=code,
                            codelist_code=codelist,
                            term=term,
                            standard_name=standard_label,
                            definition=definition,
                            ctri_field_mapped=mapped_domain
                        )
                        db_session.add(mapping)
                        total_cdisc += 1
            logger.info(f"Loaded {total_cdisc} terms from {fname}")
        except Exception as e:
            logger.warning(f"Error loading CDISC file {fname}: {e}")
    db_session.commit()
    logger.info(f"Total CDISC standards ingested: {total_cdisc}")

def run_import(source_db_path: str, batch_size: int = 500, limit: Optional[int] = None, scope: str = "all"):
    logger.info(f"Starting CTRI Data Ingestion from {source_db_path}")
    logger.info(f"Target Application Database: {engine.url}")
    logger.info(f"Scope: {scope.upper()}, Batch Size: {batch_size}, Limit: {limit or 'ALL'}")

    # Ensure tables are created
    Base.metadata.create_all(bind=engine)

    # Connect to read-only source SQLite DB
    src_conn = sqlite3.connect(f"file:{os.path.abspath(source_db_path)}?mode=ro", uri=True)
    src_conn.row_factory = sqlite3.Row
    c = src_conn.cursor()

    # Pre-populate default Roles and System User
    db = SessionLocal()
    if db.query(models.Role).count() == 0:
        admin_role = models.Role(name="ADMIN", description="Institutional Research Administrator", permissions_json='["ALL"]')
        auditor_role = models.Role(name="AUDITOR", description="Ethics & Compliance Auditor", permissions_json='["READ", "AUDIT"]')
        pi_role = models.Role(name="INVESTIGATOR", description="Principal Investigator", permissions_json='["READ", "SUBMIT"]')
        db.add_all([admin_role, auditor_role, pi_role])
        db.commit()

        sys_user = models.User(
            username="system_auditor",
            email="research.governance@aiia.gov.in",
            password_hash="argon2_institutional_hash_placeholder",
            full_name="AIIA System Research Auditor",
            role_id=auditor_role.id,
            institution="All India Institute of Ayurveda"
        )
        db.add(sys_user)
        db.commit()

    # Load CDISC Controlled Terminology
    if db.query(models.CDISCMapping).count() == 0:
        ingest_cdisc(db)

    # Ingestion stats
    records_processed = 0
    records_imported = 0
    duplicates_count = 0
    warnings_count = 0
    errors_count = 0

    seen_ctri_numbers: Dict[str, int] = {}
    existing_trial_ids = {r[0] for r in db.query(models.Trial.id).all()}

    # Scope where clause
    scope_where = ""
    if scope == "aiia":
        c.execute("""
            SELECT DISTINCT Trial_ID FROM (
                SELECT Trial_ID FROM Primary_sponsor WHERE primary_sponsor_name LIKE '%All India Institute of Ayurveda%' OR primary_sponsor_name LIKE '%AIIA%'
                UNION
                SELECT Trial_ID FROM Sites_of_study WHERE Site_Name LIKE '%All India Institute of Ayurveda%' OR Site_Name LIKE '%AIIA%'
                UNION
                SELECT Trial_ID FROM Principal_investigator WHERE Affiliation LIKE '%All India Institute of Ayurveda%' OR Affiliation LIKE '%AIIA%'
                UNION
                SELECT Trial_ID FROM Study_titles WHERE Public_Title LIKE '%All India Institute of Ayurveda%' OR Scientific_Title LIKE '%All India Institute of Ayurveda%'
            )
        """)
        aiia_ids = [str(r[0]) for r in c.fetchall()]
        scope_where = f"WHERE t.Trial_ID IN ({','.join(aiia_ids)})"
    elif scope == "ayush":
        c.execute("""
            SELECT DISTINCT Trial_ID FROM (
                SELECT Trial_ID FROM Intervention_table WHERE Intervention_Name LIKE '%Ayurved%' OR Intervention_Name LIKE '%Ayush%' OR Intervention_Name LIKE '%Yoga%' OR Intervention_Name LIKE '%Unani%' OR Intervention_Name LIKE '%Siddha%' OR Intervention_Name LIKE '%Homeopath%'
                UNION
                SELECT Trial_ID FROM Primary_sponsor WHERE primary_sponsor_name LIKE '%Ayush%' OR primary_sponsor_name LIKE '%AYUSH%' OR primary_sponsor_name LIKE '%Ayurved%'
                UNION
                SELECT Trial_ID FROM Study_titles WHERE Public_Title LIKE '%Ayurved%' OR Scientific_Title LIKE '%Ayurved%' OR Public_Title LIKE '%Ayush%' OR Scientific_Title LIKE '%Ayush%'
            )
        """)
        ayush_ids = [str(r[0]) for r in c.fetchall()]
        scope_where = f"WHERE t.Trial_ID IN ({','.join(ayush_ids)})"

    # Query source trials in streaming cursor
    count_query = f"SELECT COUNT(*) FROM Study_titles t {scope_where}"
    c.execute(count_query)
    total_in_scope = c.fetchone()[0]
    total_to_process = min(total_in_scope, limit) if limit else total_in_scope

    logger.info(f"Total source records in scope ({scope}): {total_in_scope} (Processing: {total_to_process})")

    offset = 0
    while True:
        current_limit = batch_size
        if limit and (offset + current_limit > limit):
            current_limit = limit - offset
        if current_limit <= 0:
            break

        c.execute(f"""
            SELECT 
                t.Trial_ID, t.CTRI_Number, t.Public_Title, t.Scientific_Title,
                d.Type_of_Trial, d.Type_of_Study, d.Study_design, d.Phase, d.Trial_Acronym, d.Post_graduation_thesis,
                r.Recruitment_Status_India, r.Recruitment_Status_Global,
                reg.Registered_on, reg.Registration_type,
                dt.Last_modified_on, dt.Date_first_enrollment_India, dt.Date_of_study_completion_India,
                sp.primary_sponsor_name, sp.primary_sponsor_address, sp.Type_of_Sponsor,
                pi.Name as PI_Name, pi.Designation as PI_Designation, pi.Affiliation as PI_Affiliation,
                pi.Address as PI_Address, pi.Phone as PI_Phone, pi.Email as PI_Email,
                sz.sample_size,
                sm.Brief_Summary,
                dc."DCGI status" as dcgi_status
            FROM Study_titles t
            LEFT JOIN Study_details d ON t.Trial_ID = d.Trial_ID
            LEFT JOIN Recruitment_details r ON t.Trial_ID = r.Trial_ID
            LEFT JOIN Registration_details reg ON t.Trial_ID = reg.Trial_ID
            LEFT JOIN "Dates table" dt ON t.Trial_ID = dt.Trial_ID
            LEFT JOIN Primary_sponsor sp ON t.Trial_ID = sp.Trial_ID
            LEFT JOIN Principal_investigator pi ON t.Trial_ID = pi.Trial_ID
            LEFT JOIN Target_sample_size sz ON t.Trial_ID = sz.Trial_ID
            LEFT JOIN Study_summary sm ON t.Trial_ID = sm.Trial_ID
            LEFT JOIN "DCGI status" dc ON t.Trial_ID = dc."Trial ID"
            {scope_where}
            ORDER BY t.Trial_ID ASC
            LIMIT ? OFFSET ?
        """, (current_limit, offset))

        batch_rows = c.fetchall()
        if not batch_rows:
            break

        batch_trial_ids = [row["Trial_ID"] for row in batch_rows]
        id_placeholders = ",".join("?" for _ in batch_trial_ids)

        # Batch-fetch interventions
        c.execute(f'SELECT * FROM Intervention_table WHERE Trial_ID IN ({id_placeholders})', batch_trial_ids)
        interventions_by_trial = {}
        for row in c.fetchall():
            tid = row["Trial_ID"]
            interventions_by_trial.setdefault(tid, []).append(row)

        # Batch-fetch eligibility
        c.execute(f'SELECT * FROM Inclusion_criteria WHERE Trial_ID IN ({id_placeholders})', batch_trial_ids)
        inclusion_by_trial = {row["Trial_ID"]: row for row in c.fetchall()}

        c.execute(f'SELECT * FROM Exclusion_criteria WHERE Trial_ID IN ({id_placeholders})', batch_trial_ids)
        exclusion_by_trial = {row["Trial_ID"]: row for row in c.fetchall()}

        # Batch-fetch outcomes
        c.execute(f'SELECT * FROM Primary_outcomes WHERE Trial_ID IN ({id_placeholders})', batch_trial_ids)
        primary_outcomes_by_trial = {}
        for row in c.fetchall():
            primary_outcomes_by_trial.setdefault(row["Trial_ID"], []).append(row)

        c.execute(f'SELECT * FROM Secondary_outcomes WHERE Trial_ID IN ({id_placeholders})', batch_trial_ids)
        secondary_outcomes_by_trial = {}
        for row in c.fetchall():
            secondary_outcomes_by_trial.setdefault(row["Trial_ID"], []).append(row)

        # Batch-fetch sites
        c.execute(f'SELECT * FROM Sites_of_study WHERE Trial_ID IN ({id_placeholders})', batch_trial_ids)
        sites_by_trial = {}
        for row in c.fetchall():
            sites_by_trial.setdefault(row["Trial_ID"], []).append(row)

        # Batch-fetch ethics
        c.execute(f'SELECT * FROM Ethics_committee WHERE Trial_ID IN ({id_placeholders})', batch_trial_ids)
        ethics_by_trial = {}
        for row in c.fetchall():
            ethics_by_trial.setdefault(row["Trial_ID"], []).append(row)

        # Ingest batch
        try:
            for r in batch_rows:
                records_processed += 1
                trial_id = r["Trial_ID"]
                if trial_id in existing_trial_ids:
                    continue
                existing_trial_ids.add(trial_id)

                raw_ctri = (r["CTRI_Number"] or "").strip()

                # Handle duplicate CTRI numbers
                ctri_to_save = raw_ctri
                if raw_ctri in seen_ctri_numbers:
                    duplicates_count += 1
                    seen_ctri_numbers[raw_ctri] += 1
                    ctri_to_save = f"{raw_ctri}-REV{seen_ctri_numbers[raw_ctri]}"
                    warnings_count += 1
                    logger.warning(f"Duplicate CTRI Number '{raw_ctri}' detected on Trial_ID {trial_id}. Stored as '{ctri_to_save}'.")
                else:
                    seen_ctri_numbers[raw_ctri] = 1

                # Normalize dates
                reg_date = parse_date(r["Registered_on"])
                mod_date = parse_date(r["Last_modified_on"])
                first_enroll_date = parse_date(r["Date_first_enrollment_India"])
                completion_date = parse_date(r["Date_of_study_completion_India"])

                # Normalization of status & sample size
                status = normalize_status(r["Recruitment_Status_India"])
                sample_sz = parse_sample_size(r["sample_size"])

                # Tag AIIA / AYUSH
                site_names = [s["Site_Name"] for s in sites_by_trial.get(trial_id, [])]
                inv_names = [iv["Intervention_Name"] for iv in interventions_by_trial.get(trial_id, [])]
                all_texts = [
                    r["primary_sponsor_name"], r["PI_Affiliation"], r["Public_Title"],
                    r["Scientific_Title"]
                ] + site_names + inv_names

                is_aiia_trial = check_aiia(all_texts)
                is_ayush_trial = check_ayush(all_texts)

                # Create Trial model
                trial_obj = models.Trial(
                    id=trial_id,
                    ctri_number=ctri_to_save,
                    public_title=r["Public_Title"] or "Untitled Protocol",
                    scientific_title=r["Scientific_Title"],
                    trial_acronym=r["Trial_Acronym"],
                    type_of_trial=r["Type_of_Trial"],
                    type_of_study=r["Type_of_Study"],
                    study_design=r["Study_design"],
                    phase=r["Phase"],
                    post_graduation_thesis=r["Post_graduation_thesis"],
                    recruitment_status=status,
                    registration_type=r["Registration_type"],
                    registered_on=reg_date,
                    last_modified_on=mod_date,
                    date_first_enrollment=first_enroll_date,
                    date_completion=completion_date,
                    target_sample_size=sample_sz,
                    brief_summary=r["Brief_Summary"],
                    dcgi_status=r["dcgi_status"],
                    is_aiia=is_aiia_trial,
                    is_ayush=is_ayush_trial
                )
                db.add(trial_obj)

                # 4. Investigators
                if r["PI_Name"] and r["PI_Name"].strip() and r["PI_Name"].strip() != "character(0)":
                    pi_name = r["PI_Name"].strip()
                    investigator = models.Investigator(
                        name=pi_name,
                        designation=r["PI_Designation"],
                        affiliation=r["PI_Affiliation"],
                        address=r["PI_Address"],
                        phone=r["PI_Phone"],
                        email=r["PI_Email"],
                        is_aiia=is_aiia_trial
                    )
                    db.add(investigator)
                    db.flush()
                    t_inv = models.TrialInvestigator(
                        trial_id=trial_id,
                        investigator_id=investigator.id,
                        role="Principal Investigator"
                    )
                    db.add(t_inv)

                # 5. Sponsors
                if r["primary_sponsor_name"] and r["primary_sponsor_name"].strip():
                    sponsor = models.Sponsor(
                        trial_id=trial_id,
                        name=r["primary_sponsor_name"].strip(),
                        address=r["primary_sponsor_address"],
                        sponsor_type=r["Type_of_Sponsor"],
                        is_primary=True
                    )
                    db.add(sponsor)

                # 6. Study Sites
                for site in sites_by_trial.get(trial_id, []):
                    s_name = site["Site_Name"]
                    if s_name and s_name.strip():
                        ss = models.StudySite(
                            trial_id=trial_id,
                            site_name=s_name.strip(),
                            site_address=site["Site_Address"],
                            pi_name=site["Name_of_Prinicpal_Investigator"],
                            num_sites=str(site["No_of_Sites"])
                        )
                        db.add(ss)

                # 7. Interventions
                for inv in interventions_by_trial.get(trial_id, []):
                    i_obj = models.Intervention(
                        trial_id=trial_id,
                        intervention_name=inv["Intervention_Name"],
                        intervention_details=inv["Intervention_details"],
                        comparator_name=inv["Comparator_Name"],
                        comparator_details=inv["Comparator_details"]
                    )
                    db.add(i_obj)

                # 8. Outcomes (Primary & Secondary)
                for po in primary_outcomes_by_trial.get(trial_id, []):
                    if po["Primary_Outcome"] and po["Primary_Outcome"].strip():
                        o_obj = models.Outcome(
                            trial_id=trial_id,
                            outcome_type="PRIMARY",
                            outcome_name=po["Primary_Outcome"].strip(),
                            timepoints=po["primary_Outcome_timepoints"]
                        )
                        db.add(o_obj)

                for so in secondary_outcomes_by_trial.get(trial_id, []):
                    if so["Secondary_Outcome"] and so["Secondary_Outcome"].strip():
                        so_obj = models.Outcome(
                            trial_id=trial_id,
                            outcome_type="SECONDARY",
                            outcome_name=so["Secondary_Outcome"].strip(),
                            timepoints=so["Secondary_Outcome_timepoints"]
                        )
                        db.add(so_obj)

                # 9. Eligibility
                inc = inclusion_by_trial.get(trial_id)
                exc = exclusion_by_trial.get(trial_id)
                if inc or exc:
                    elig = models.Eligibility(
                        trial_id=trial_id,
                        age_from=inc["Age_From"] if inc else None,
                        age_to=inc["Age_To"] if inc else None,
                        gender=inc["Gender"] if inc else None,
                        inclusion_details=inc["Details"] if inc else None,
                        exclusion_details=exc["Exclusion_details"] if exc else None
                    )
                    db.add(elig)

                # 17. Compliance Checks (Prospective Registration & Ethics)
                is_prospective = "prospective" in (r["Registration_type"] or "").lower()
                comp_check = models.ComplianceCheck(
                    trial_id=trial_id,
                    check_type="PROSPECTIVE_REGISTRATION",
                    status="COMPLIANT" if is_prospective else "ATTENTION_REQUIRED",
                    score=100.0 if is_prospective else 50.0,
                    findings="Registered prospectively before patient enrollment" if is_prospective else "Retrospective registration detected; governance audit required."
                )
                db.add(comp_check)

                if not is_prospective:
                    # 18. Alerts
                    alert = models.Alert(
                        trial_id=trial_id,
                        alert_type="RETROSPECTIVE_REGISTRATION",
                        severity="MEDIUM",
                        message=f"Trial {ctri_to_save} was registered retrospectively."
                    )
                    db.add(alert)

                for ec in ethics_by_trial.get(trial_id, []):
                    ec_name = ec["Name_of_Committee"] or "Institutional Ethics Committee"
                    ec_status = ec["Approval_Status"] or "Approved"
                    ec_check = models.ComplianceCheck(
                        trial_id=trial_id,
                        check_type="IEC_CLEARANCE",
                        status="COMPLIANT" if "approve" in ec_status.lower() else "ATTENTION_REQUIRED",
                        score=100.0 if "approve" in ec_status.lower() else 0.0,
                        findings=f"Ethics Committee '{ec_name}': Status={ec_status}"
                    )
                    db.add(ec_check)

                # 10. Trial Milestones
                if reg_date:
                    ms_reg = models.TrialMilestone(
                        trial_id=trial_id,
                        milestone_name="CTRI Registration",
                        achieved_date=reg_date,
                        status="ACHIEVED"
                    )
                    db.add(ms_reg)

                if first_enroll_date:
                    ms_fp = models.TrialMilestone(
                        trial_id=trial_id,
                        milestone_name="First Subject Enrolled",
                        achieved_date=first_enroll_date,
                        status="ACHIEVED"
                    )
                    db.add(ms_fp)

                if completion_date:
                    ms_comp = models.TrialMilestone(
                        trial_id=trial_id,
                        milestone_name="Study Completion",
                        achieved_date=completion_date,
                        status="ACHIEVED" if status == "Completed" else "PLANNED"
                    )
                    db.add(ms_comp)

                # 11. Enrollment summary
                if sample_sz:
                    enr = models.Enrollment(
                        trial_id=trial_id,
                        target_enrollment=sample_sz,
                        actual_enrolled=sample_sz if status == "Completed" else None,
                        last_updated=mod_date or reg_date
                    )
                    db.add(enr)

                records_imported += 1

            db.commit()
            logger.info(f"Progress: Processed {records_processed}/{total_to_process} records...")
        except Exception as e:
            db.rollback()
            errors_count += len(batch_rows)
            logger.error(f"Error importing batch at offset {offset}: {e}")

        offset += current_limit

    # Record Audit Log for the Ingestion Job
    audit = models.AuditLog(
        entity_name="TRIALS_IMPORT_JOB",
        entity_id=0,
        action="IMPORT",
        changed_by="SYSTEM_INGESTION_PIPELINE",
        changes_json=f'{{"processed": {records_processed}, "imported": {records_imported}, "duplicates": {duplicates_count}, "errors": {errors_count}}}'
    )
    db.add(audit)
    db.commit()

    db.close()
    src_conn.close()

    # Formatted standard summary output
    print("\n" + "=" * 40)
    print("CTRI Import Completed\n")
    print(f"Records processed: {records_processed}")
    print(f"Records imported: {records_imported}")
    print(f"Duplicates: {duplicates_count}")
    print(f"Warnings: {warnings_count}")
    print(f"Errors: {errors_count}")
    print("=" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CTRI Streaming Batch Ingestion Pipeline")
    parser.add_argument("--source-db", default="JM_CTRIdb.sqlite", help="Path to source JM_CTRIdb.sqlite")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch size for chunked streaming")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit for test/partial ingestion")
    parser.add_argument("--scope", default="all", choices=["all", "aiia", "ayush"], help="Scope of trials to import")
    args = parser.parse_args()

    run_import(source_db_path=args.source_db, batch_size=args.batch_size, limit=args.limit, scope=args.scope)
