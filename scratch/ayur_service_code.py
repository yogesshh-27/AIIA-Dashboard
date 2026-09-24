"""
AYURCTMS Database Service Functions.
To be merged into db_service.py.
"""

import sqlite3
import json
import datetime
import uuid

APP_DB_PATH = "aiia_app.db"

def get_app_conn():
    conn = sqlite3.connect(APP_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------------------------------------------
# 1. PATIENT TRIAL-LOCATION MATCHING ENGINE (Section 2 & 3)
# -------------------------------------------------------------
def match_patient_trials(condition, accessible_locations, distance_pref="", age=None, gender=None):
    """
    Finds potentially relevant Ayurvedic trials based on patient's condition and accessible locations.
    Clearly returns recommendations without claiming clinical diagnosis.
    """
    conn = get_app_conn()
    c = conn.cursor()

    # Normalize inputs
    cond_search = f"%{condition.strip().lower()}%" if condition else "%"
    
    # Query trials
    c.execute("""
        SELECT * FROM ayur_trials 
        WHERE LOWER(condition) LIKE ? OR LOWER(trial_name) LIKE ? OR LOWER(description) LIKE ?
    """, (cond_search, cond_search, cond_search))
    rows = [dict(r) for r in c.fetchall()]

    # Filter/rank based on accessible locations
    matched = []
    other_trials = []
    
    # Normalize list of accessible locations
    if isinstance(accessible_locations, str):
        loc_list = [l.strip().lower() for l in accessible_locations.split(",") if l.strip()]
    elif isinstance(accessible_locations, list):
        loc_list = [str(l).strip().lower() for l in accessible_locations]
    else:
        loc_list = []

    for trial in rows:
        t_city = trial["city"].strip().lower()
        t_state = trial["state"].strip().lower()
        
        is_accessible = False
        if not loc_list or any(loc in t_city or loc in t_state for loc in loc_list):
            is_accessible = True

        available_slots = max(0, trial["target_participants"] - trial["enrolled_participants"])
        distance_str = "Directly in your preferred / selected location" if is_accessible else "Participating multi-center location"

        card = {
            "trial_id": trial["trial_id"],
            "trial_name": trial["trial_name"],
            "condition": trial["condition"],
            "intervention": trial["intervention"],
            "location": trial["city"],
            "state": trial["state"],
            "hospital": trial["hospital_name"],
            "pi_name": trial["pi_name"],
            "duration": f"{trial['duration_weeks']} Weeks",
            "status": trial["recruitment_status"],
            "trial_status": trial["trial_status"],
            "available_slots": available_slots,
            "distance_context": distance_str,
            "eligibility": trial["eligibility_criteria"],
            "exclusion": trial["exclusion_criteria"],
            "description": trial["description"],
            "is_directly_accessible": is_accessible
        }
        if is_accessible:
            matched.append(card)
        else:
            other_trials.append(card)

    conn.close()
    
    # If no direct matches, return all matching condition
    final_list = matched if matched else other_trials
    
    return {
        "success": True,
        "query": {
            "condition": condition,
            "accessible_locations": loc_list,
            "distance_pref": distance_pref
        },
        "disclaimer": "Potentially Relevant Trial. Final eligibility will be determined by the authorized clinical research team.",
        "total_matches": len(final_list),
        "results": final_list
    }

# -------------------------------------------------------------
# 2. DASHBOARD KPI STATS (Section 7 & 8)
# -------------------------------------------------------------
def get_ayur_dashboard_stats():
    """
    Returns data for the 3 top large cards:
    CARD 1: DOCTOR INFORMATION (Total doctors, Active investigators, Number of trial sites)
    CARD 2: PATIENT INFORMATION (Total patients, Active participants, Completed participants)
    CARD 3: PHARMACOVIGILANCE (Total adverse events, Serious adverse events, Cases under review)
    Plus Active Trials distribution (Ongoing, Completed, Upcoming) and progress bars.
    """
    conn = get_app_conn()
    c = conn.cursor()

    # Card 1: Doctors
    c.execute("SELECT COUNT(*) FROM ayur_doctors")
    total_doctors = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ayur_doctors WHERE status = 'Active'")
    active_investigators = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT city) FROM ayur_sites")
    total_sites = c.fetchone()[0]

    # Card 2: Patients
    c.execute("SELECT COUNT(*) FROM ayur_patients")
    total_patients = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ayur_patients WHERE status = 'Active'")
    active_patients = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ayur_patients WHERE status = 'Completed'")
    completed_patients = c.fetchone()[0]

    # Card 3: Pharmacovigilance
    c.execute("SELECT COUNT(*) FROM ayur_adverse_events")
    total_aes = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ayur_adverse_events WHERE serious = 'Yes'")
    serious_aes = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ayur_adverse_events WHERE status IN ('Under Investigation', 'Reported', 'Under Review')")
    under_review_aes = c.fetchone()[0]

    # Section A: Active Trials breakdown
    c.execute("SELECT COUNT(*) FROM ayur_trials WHERE trial_status = 'Ongoing'")
    ongoing_trials = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ayur_trials WHERE trial_status = 'Completed'")
    completed_trials = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ayur_trials WHERE trial_status IN ('Upcoming', 'Pending Approval')")
    upcoming_trials = c.fetchone()[0]

    # Trial progress bars
    c.execute("""
        SELECT trial_id, trial_name, condition, city, enrolled_participants, target_participants, progress_pct, trial_status 
        FROM ayur_trials ORDER BY trial_id
    """)
    trials_progress = [dict(r) for r in c.fetchall()]

    # GCP Compliance status
    c.execute("SELECT COUNT(*) FROM ayur_gcp_checklist")
    total_gcp = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ayur_gcp_checklist WHERE is_completed = 1")
    completed_gcp = c.fetchone()[0]
    gcp_pct = round((completed_gcp / total_gcp) * 100) if total_gcp > 0 else 0

    # Safety signals count
    c.execute("SELECT COUNT(*) FROM ayur_safety_signals")
    active_signals_count = c.fetchone()[0]

    conn.close()

    return {
        "success": True,
        "kpi_cards": {
            "doctors": {
                "title": "DOCTOR INFORMATION",
                "total_doctors": total_doctors,
                "active_investigators": active_investigators,
                "trial_sites": total_sites,
                "button_text": "VIEW DOCTORS"
            },
            "patients": {
                "title": "PATIENT INFORMATION",
                "total_patients": total_patients,
                "active_participants": active_patients,
                "completed_participants": completed_patients,
                "button_text": "VIEW PATIENTS"
            },
            "pharmacovigilance": {
                "title": "PHARMACOVIGILANCE",
                "total_adverse_events": total_aes,
                "serious_adverse_events": serious_aes,
                "cases_under_review": under_review_aes,
                "active_signals": active_signals_count,
                "button_text": "VIEW SAFETY"
            }
        },
        "active_trials_summary": {
            "ongoing": ongoing_trials,
            "completed": completed_trials,
            "upcoming": upcoming_trials,
            "trials_progress": trials_progress
        },
        "gcp_compliance": {
            "total_items": total_gcp,
            "completed_items": completed_gcp,
            "percentage": gcp_pct
        }
    }

# -------------------------------------------------------------
# 3. SITES / LOCATIONS (Section 9)
# -------------------------------------------------------------
def get_ayur_sites(city=None):
    conn = get_app_conn()
    c = conn.cursor()
    if city:
        c.execute("SELECT * FROM ayur_sites WHERE LOWER(city) = LOWER(?)", (city.strip(),))
        site = c.fetchone()
        conn.close()
        if site:
            res = dict(site)
            res["outcome_trend"] = json.loads(res.get("outcome_trend_json") or "[]")
            return {"success": True, "site": res}
        return {"success": False, "error": "Site not found"}
    else:
        c.execute("SELECT * FROM ayur_sites ORDER BY city")
        sites = []
        for r in c.fetchall():
            d = dict(r)
            d["outcome_trend"] = json.loads(d.get("outcome_trend_json") or "[]")
            sites.append(d)
        conn.close()
        return {"success": True, "sites": sites}

# -------------------------------------------------------------
# 4. TRIALS & NEW TRIAL PLANNING (Section 10 & 11)
# -------------------------------------------------------------
def get_ayur_trials(status=None, condition=None, location=None, search=None):
    conn = get_app_conn()
    c = conn.cursor()
    query = "SELECT * FROM ayur_trials WHERE 1=1"
    params = []
    if status and status != 'All':
        query += " AND (trial_status = ? OR recruitment_status = ?)"
        params.extend([status, status])
    if condition and condition != 'All':
        query += " AND condition = ?"
        params.append(condition)
    if location and location != 'All':
        query += " AND city = ?"
        params.append(location)
    if search:
        s = f"%{search.strip().lower()}%"
        query += " AND (LOWER(trial_id) LIKE ? OR LOWER(trial_name) LIKE ? OR LOWER(condition) LIKE ? OR LOWER(pi_name) LIKE ? OR LOWER(hospital_name) LIKE ?)"
        params.extend([s, s, s, s, s])
    
    query += " ORDER BY trial_id"
    c.execute(query, params)
    trials = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"success": True, "total": len(trials), "trials": trials}

def get_ayur_trial_detail(trial_id):
    conn = get_app_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM ayur_trials WHERE trial_id = ?", (trial_id,))
    t = c.fetchone()
    if not t:
        conn.close()
        return {"success": False, "error": "Trial not found"}
    trial_data = dict(t)

    # Get associated site
    c.execute("SELECT * FROM ayur_sites WHERE trial_id = ?", (trial_id,))
    site = c.fetchone()
    trial_data["site_info"] = dict(site) if site else None

    # Get assigned doctor
    c.execute("SELECT * FROM ayur_doctors WHERE trial_id = ?", (trial_id,))
    doc = c.fetchone()
    trial_data["doctor_info"] = dict(doc) if doc else None

    # Get enrolled patients count & list
    c.execute("SELECT patient_id, full_name, age, gender, treatment_status, registration_date FROM ayur_patients WHERE assigned_trial_id = ?", (trial_id,))
    trial_data["patients"] = [dict(r) for r in c.fetchall()]

    # Get adverse events
    c.execute("SELECT * FROM ayur_adverse_events WHERE trial_id = ?", (trial_id,))
    trial_data["adverse_events"] = [dict(r) for r in c.fetchall()]

    conn.close()
    return {"success": True, "trial": trial_data}

def create_ayur_trial(data):
    """
    Creates a new trial with intelligent overlap warning if another active trial
    at the same location is already studying the same condition.
    """
    conn = get_app_conn()
    c = conn.cursor()

    trial_id = data.get("trial_id") or f"AYU-TRIAL-{str(uuid.uuid4())[:4].upper()}"
    city = data.get("city", "").strip()
    condition = data.get("condition", "").strip()

    # Intelligent overlap check
    c.execute("""
        SELECT trial_id, trial_name, hospital_name, condition, city 
        FROM ayur_trials 
        WHERE LOWER(city) = LOWER(?) AND LOWER(condition) = LOWER(?) AND trial_status = 'Ongoing'
    """, (city, condition))
    overlapping = [dict(r) for r in c.fetchall()]

    overlap_warning = None
    if overlapping:
        exist = overlapping[0]
        overlap_warning = f"Potential overlap detected: An active {exist['condition']} trial ({exist['trial_id']}) already exists at {exist['city']} ({exist['hospital_name']})."

    # Insert trial
    c.execute("""
    INSERT INTO ayur_trials (
        trial_id, trial_name, condition, intervention, description, hospital_name,
        city, state, pi_name, start_date, end_date, duration_weeks, target_participants,
        enrolled_participants, recruitment_status, trial_status, eligibility_criteria,
        exclusion_criteria, ethics_approval_status, ctri_registration_status, regulatory_status,
        progress_pct, outcome_metric_name, outcome_metric_value
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trial_id,
        data.get("trial_name", "Ayurvedic Clinical Protocol"),
        condition,
        data.get("intervention", "Classical Ayurvedic Formulation"),
        data.get("description", "Prospective clinical evaluation."),
        data.get("hospital_name", f"AIIA Clinical Facility - {city}"),
        city,
        data.get("state", "India"),
        data.get("pi_name", "Authorized AIIA Investigator"),
        data.get("start_date", datetime.date.today().isoformat()),
        data.get("end_date", (datetime.date.today() + datetime.timedelta(days=90)).isoformat()),
        int(data.get("duration_weeks", 12)),
        int(data.get("target_participants", 100)),
        0,
        "Recruiting",
        data.get("trial_status", "Ongoing"),
        data.get("eligibility_criteria", "Adults meeting diagnostic criteria."),
        data.get("exclusion_criteria", "Severe systemic illness, pregnant or lactating women."),
        data.get("ethics_approval_status", "Approved"),
        data.get("ctri_registration_status", "Registered"),
        data.get("regulatory_status", "Approved"),
        0,
        data.get("outcome_metric_name", "Clinical Outcome Score"),
        "Intake Active"
    ))

    # Log audit
    c.execute("""
    INSERT INTO ayur_audit_trail (audit_id, user_name, action, module, previous_value, new_value, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        f"AUD-{str(uuid.uuid4())[:6].upper()}",
        data.get("created_by", "Dr. Research Admin"),
        f"Created new clinical trial {trial_id}",
        "Trial Management",
        "None",
        f"{trial_id}: {data.get('trial_name')}",
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "trial_id": trial_id,
        "overlap_warning": overlap_warning,
        "message": "Trial created successfully."
    }

# -------------------------------------------------------------
# 5. DOCTOR INFORMATION (Section 14)
# -------------------------------------------------------------
def get_ayur_doctors(site=None, specialization=None, status=None, search=None):
    conn = get_app_conn()
    c = conn.cursor()
    query = "SELECT * FROM ayur_doctors WHERE 1=1"
    params = []
    if site and site != 'All':
        query += " AND current_site = ?"
        params.append(site)
    if specialization and specialization != 'All':
        query += " AND specialization = ?"
        params.append(specialization)
    if status and status != 'All':
        query += " AND status = ?"
        params.append(status)
    if search:
        s = f"%{search.strip().lower()}%"
        query += " AND (LOWER(name) LIKE ? OR LOWER(qualification) LIKE ? OR LOWER(specialization) LIKE ? OR LOWER(current_site) LIKE ?)"
        params.extend([s, s, s, s])
    
    query += " ORDER BY doctor_id"
    c.execute(query, params)
    docs = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"success": True, "total": len(docs), "doctors": docs}

def get_ayur_doctor_detail(doctor_id):
    conn = get_app_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM ayur_doctors WHERE doctor_id = ?", (doctor_id,))
    doc = c.fetchone()
    if not doc:
        conn.close()
        return {"success": False, "error": "Doctor not found"}
    d_data = dict(doc)

    # Get active trial info
    c.execute("SELECT * FROM ayur_trials WHERE trial_id = ?", (d_data["trial_id"],))
    trial = c.fetchone()
    d_data["trial_info"] = dict(trial) if trial else None

    # Get patients treated by doctor
    c.execute("SELECT patient_id, full_name, condition, treatment_status, registration_date FROM ayur_patients WHERE assigned_doctor_name = ?", (d_data["name"],))
    d_data["assigned_patients"] = [dict(r) for r in c.fetchall()]

    conn.close()
    return {"success": True, "doctor": d_data}

# -------------------------------------------------------------
# 6. PATIENT MANAGEMENT & TREATMENT TIMELINE (Section 15 & 16)
# -------------------------------------------------------------
def get_ayur_patients(condition=None, site=None, status=None, search=None):
    conn = get_app_conn()
    c = conn.cursor()
    query = "SELECT * FROM ayur_patients WHERE 1=1"
    params = []
    if condition and condition != 'All':
        query += " AND condition = ?"
        params.append(condition)
    if site and site != 'All':
        query += " AND (treatment_site LIKE ? OR area_city = ?)"
        params.extend([f"%{site}%", site])
    if status and status != 'All':
        query += " AND status = ?"
        params.append(status)
    if search:
        s = f"%{search.strip().lower()}%"
        query += " AND (LOWER(patient_id) LIKE ? OR LOWER(full_name) LIKE ? OR LOWER(condition) LIKE ? OR LOWER(area_city) LIKE ? OR LOWER(assigned_doctor_name) LIKE ?)"
        params.extend([s, s, s, s, s])

    query += " ORDER BY patient_id"
    c.execute(query, params)
    patients = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"success": True, "total": len(patients), "patients": patients}

def get_ayur_patient_detail(patient_id):
    conn = get_app_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM ayur_patients WHERE patient_id = ?", (patient_id,))
    p = c.fetchone()
    if not p:
        conn.close()
        return {"success": False, "error": "Patient not found"}
    p_data = dict(p)

    # Get 8-stage treatment timeline
    c.execute("""
        SELECT * FROM ayur_patient_treatments 
        WHERE patient_id = ? 
        ORDER BY stage_order ASC
    """, (patient_id,))
    p_data["treatment_timeline"] = [dict(r) for r in c.fetchall()]

    # If empty timeline, generate standard default stages
    if not p_data["treatment_timeline"]:
        p_data["treatment_timeline"] = [
            {"stage_key": "REG", "stage_title": "Registration & Consent", "stage_order": 1, "date_recorded": p_data["registration_date"], "status": "Completed", "assigned_doctor_name": p_data["assigned_doctor_name"], "dosage_frequency": "N/A", "notes": "Informed Consent Form executed."},
            {"stage_key": "SCR", "stage_title": "Clinical Screening", "stage_order": 2, "date_recorded": p_data["registration_date"], "status": "Completed", "assigned_doctor_name": p_data["assigned_doctor_name"], "dosage_frequency": "N/A", "notes": "Diagnostic inclusion criteria verified."},
            {"stage_key": "BASE", "stage_title": "Baseline Assessment", "stage_order": 3, "date_recorded": p_data["registration_date"], "status": "Completed", "assigned_doctor_name": p_data["assigned_doctor_name"], "dosage_frequency": "N/A", "notes": "Baseline laboratory & Prakriti workup completed."},
            {"stage_key": "TREAT", "stage_title": "Treatment Started", "stage_order": 4, "date_recorded": p_data["registration_date"], "status": "In Progress", "assigned_doctor_name": p_data["assigned_doctor_name"], "dosage_frequency": "Standard Regimen BD", "notes": "Therapy initiated under study protocol."}
        ]

    # Get adverse events for this patient
    c.execute("SELECT * FROM ayur_adverse_events WHERE patient_id = ?", (patient_id,))
    p_data["adverse_events"] = [dict(r) for r in c.fetchall()]

    conn.close()
    return {"success": True, "patient": p_data}

# -------------------------------------------------------------
# 7. PHARMACOVIGILANCE & SAFETY SIGNALS (Section 17 & 18)
# -------------------------------------------------------------
def get_ayur_pv_summary():
    conn = get_app_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM ayur_adverse_events")
    total_ae = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ayur_adverse_events WHERE serious = 'Yes'")
    sae = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ayur_adverse_events WHERE status IN ('Under Investigation', 'Reported', 'Under Review')")
    under_inv = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ayur_adverse_events WHERE status = 'Resolved'")
    resolved = c.fetchone()[0]

    c.execute("SELECT * FROM ayur_safety_signals ORDER BY date_detected DESC")
    signals = [dict(r) for r in c.fetchall()]

    conn.close()
    return {
        "success": True,
        "summary": {
            "total_adverse_events": total_ae,
            "serious_adverse_events": sae,
            "under_investigation": under_inv,
            "resolved_cases": resolved
        },
        "safety_signals": signals
    }

def get_ayur_adverse_events(trial_id=None, severity=None, status=None, search=None):
    conn = get_app_conn()
    c = conn.cursor()
    query = "SELECT * FROM ayur_adverse_events WHERE 1=1"
    params = []
    if trial_id and trial_id != 'All':
        query += " AND trial_id = ?"
        params.append(trial_id)
    if severity and severity != 'All':
        query += " AND severity = ?"
        params.append(severity)
    if status and status != 'All':
        query += " AND status = ?"
        params.append(status)
    if search:
        s = f"%{search.strip().lower()}%"
        query += " AND (LOWER(patient_name) LIKE ? OR LOWER(adverse_event) LIKE ? OR LOWER(location) LIKE ? OR LOWER(suspected_treatment) LIKE ?)"
        params.extend([s, s, s, s])

    query += " ORDER BY date_reported DESC"
    c.execute(query, params)
    events = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"success": True, "total": len(events), "events": events}

def report_ayur_adverse_event(data):
    conn = get_app_conn()
    c = conn.cursor()
    event_id = f"AE-{str(uuid.uuid4())[:4].upper()}"

    c.execute("""
    INSERT INTO ayur_adverse_events (
        event_id, patient_id, patient_name, trial_id, condition, location,
        adverse_event, severity, serious, suspected_treatment, date_reported,
        action_taken, outcome, reported_by, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id,
        data.get("patient_id", "AYU-PAT-UNKNOWN"),
        data.get("patient_name", "Trial Participant"),
        data.get("trial_id", "AYU-TRIAL-001"),
        data.get("condition", "General"),
        data.get("location", "Delhi"),
        data.get("adverse_event", "Unspecified event"),
        data.get("severity", "Mild"),
        data.get("serious", "No"),
        data.get("suspected_treatment", "Ayurvedic formulation"),
        data.get("date_reported", datetime.date.today().isoformat()),
        data.get("action_taken", "Patient evaluated; supportive measures given."),
        data.get("outcome", "Under observation"),
        data.get("reported_by", "Dr. Research Admin"),
        data.get("status", "Reported")
    ))

    # Audit log
    c.execute("""
    INSERT INTO ayur_audit_trail (audit_id, user_name, action, module, previous_value, new_value, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        f"AUD-{str(uuid.uuid4())[:6].upper()}",
        data.get("reported_by", "Dr. Research Admin"),
        f"Reported adverse event {event_id} for {data.get('patient_name')}",
        "Pharmacovigilance",
        "None",
        f"{data.get('adverse_event')} ({data.get('severity')})",
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()
    return {"success": True, "event_id": event_id, "message": "Adverse event reported successfully."}

# -------------------------------------------------------------
# 8. PENDING APPROVALS (Section 12)
# -------------------------------------------------------------
def get_ayur_approvals():
    conn = get_app_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM ayur_approvals ORDER BY submission_date DESC")
    approvals = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"success": True, "approvals": approvals}

def update_ayur_approval(approval_id, status, notes=None, reviewer="Dr. Research Admin"):
    conn = get_app_conn()
    c = conn.cursor()
    decision_date = datetime.date.today().isoformat() if status in ('APPROVED', 'REJECTED') else None
    c.execute("""
        UPDATE ayur_approvals 
        SET status = ?, decision_date = ?, reviewer_notes = COALESCE(?, reviewer_notes) 
        WHERE approval_id = ?
    """, (status, decision_date, notes, approval_id))

    c.execute("""
    INSERT INTO ayur_audit_trail (audit_id, user_name, action, module, previous_value, new_value, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        f"AUD-{str(uuid.uuid4())[:6].upper()}",
        reviewer,
        f"Updated approval decision for {approval_id}",
        "Approvals",
        "PENDING",
        status,
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()
    return {"success": True, "message": f"Approval {approval_id} updated to {status}."}

# -------------------------------------------------------------
# 9. GCP GUIDELINES CHECKLIST (Section 13)
# -------------------------------------------------------------
def get_ayur_gcp_checklist():
    conn = get_app_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM ayur_gcp_checklist ORDER BY item_id")
    items = [dict(r) for r in c.fetchall()]
    total = len(items)
    completed = sum(1 for i in items if i["is_completed"] == 1)
    pct = round((completed / total) * 100) if total > 0 else 0
    conn.close()
    return {
        "success": True,
        "total_items": total,
        "completed_items": completed,
        "percentage": pct,
        "overall_status": f"{pct}% Checklist Completed",
        "items": items
    }

def toggle_ayur_gcp_item(item_id, is_completed, reviewer="Dr. Research Admin"):
    conn = get_app_conn()
    c = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("""
        UPDATE ayur_gcp_checklist 
        SET is_completed = ?, last_reviewed = ?, reviewed_by = ? 
        WHERE item_id = ?
    """, (1 if is_completed else 0, now_str, reviewer, item_id))

    c.execute("""
    INSERT INTO ayur_audit_trail (audit_id, user_name, action, module, previous_value, new_value, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        f"AUD-{str(uuid.uuid4())[:6].upper()}",
        reviewer,
        f"Toggled GCP Checklist item {item_id}",
        "GCP Guidelines",
        "Uncompleted" if is_completed else "Completed",
        "Completed" if is_completed else "Uncompleted",
        now_str
    ))

    conn.commit()
    conn.close()
    return {"success": True, "message": f"GCP item {item_id} updated."}

# -------------------------------------------------------------
# 10. NOTIFICATIONS & GLOBAL SEARCH (Section 20 & 21)
# -------------------------------------------------------------
def get_ayur_notifications():
    conn = get_app_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM ayur_notifications ORDER BY created_at DESC")
    notifs = [dict(r) for r in c.fetchall()]
    unread_count = sum(1 for n in notifs if n["is_read"] == 0)
    conn.close()
    return {"success": True, "unread_count": unread_count, "notifications": notifs}

def global_ayur_search(query):
    if not query or len(query.strip()) < 2:
        return {"success": True, "query": query, "results": {"patients": [], "doctors": [], "trials": [], "sites": []}}

    q = f"%{query.strip().lower()}%"
    conn = get_app_conn()
    c = conn.cursor()

    # Patients
    c.execute("SELECT patient_id, full_name, condition, area_city, assigned_trial_id FROM ayur_patients WHERE LOWER(full_name) LIKE ? OR LOWER(patient_id) LIKE ? OR LOWER(condition) LIKE ? LIMIT 5", (q, q, q))
    pts = [dict(r) for r in c.fetchall()]

    # Doctors
    c.execute("SELECT doctor_id, name, specialization, current_site, trial_id FROM ayur_doctors WHERE LOWER(name) LIKE ? OR LOWER(specialization) LIKE ? OR LOWER(current_site) LIKE ? LIMIT 5", (q, q, q))
    docs = [dict(r) for r in c.fetchall()]

    # Trials
    c.execute("SELECT trial_id, trial_name, condition, city, trial_status FROM ayur_trials WHERE LOWER(trial_id) LIKE ? OR LOWER(trial_name) LIKE ? OR LOWER(condition) LIKE ? LIMIT 5", (q, q, q))
    trials = [dict(r) for r in c.fetchall()]

    # Sites
    c.execute("SELECT site_id, city, hospital_name, condition, status FROM ayur_sites WHERE LOWER(city) LIKE ? OR LOWER(hospital_name) LIKE ? LIMIT 5", (q, q))
    sites = [dict(r) for r in c.fetchall()]

    conn.close()
    return {
        "success": True,
        "query": query,
        "results": {
            "patients": pts,
            "doctors": docs,
            "trials": trials,
            "sites": sites
        }
    }

# -------------------------------------------------------------
# 11. DATA INTEROPERABILITY (FHIR & CDISC DEMO) (Section 24)
# -------------------------------------------------------------
def get_ayur_interop_demo():
    """
    Returns visual pipeline and concrete sample mapping from Hospital EHR (FHIR R4)
    through mapping layer to CDISC SDTM / ADaM dataset.
    """
    fhir_patient_sample = {
        "resourceType": "Patient",
        "id": "AYU-PAT-001",
        "identifier": [{"system": "https://aiia.gov.in/mrn", "value": "AIIA-DEL-2026-092"}],
        "name": [{"use": "official", "family": "Sharma", "given": ["Ramlal"]}],
        "gender": "male",
        "birthDate": "1972-04-12",
        "address": [{"city": "New Delhi", "state": "Delhi", "country": "IND"}],
        "extension": [{
            "url": "http://hl7.org/fhir/StructureDefinition/patient-clinicalTrial",
            "valueString": "AYU-TRIAL-002"
        }]
    }

    fhir_observation_sample = {
        "resourceType": "Observation",
        "id": "OBS-HBA1C-01",
        "status": "final",
        "code": {
            "coding": [{"system": "http://loinc.org", "code": "4548-4", "display": "HbA1c in Blood"}]
        },
        "subject": {"reference": "Patient/AYU-PAT-001"},
        "valueQuantity": {"value": 7.8, "unit": "%", "system": "http://unitsofmeasure.org", "code": "%"}
    }

    mapping_rules = [
        {"fhir_element": "Patient.id", "cdisc_domain": "DM", "cdisc_variable": "USUBJID", "transformation": "AIIA-AYU-002-001"},
        {"fhir_element": "Patient.gender", "cdisc_domain": "DM", "cdisc_variable": "SEX", "transformation": "M (CDISC CT: M/F)"},
        {"fhir_element": "Patient.birthDate", "cdisc_domain": "DM", "cdisc_variable": "AGE", "transformation": "54 (Calculated to Study Day 1)"},
        {"fhir_element": "Observation.code.loinc", "cdisc_domain": "LB", "cdisc_variable": "LBTESTCD", "transformation": "HBA1C (CDISC Lab Test)"},
        {"fhir_element": "Observation.valueQuantity.value", "cdisc_domain": "LB", "cdisc_variable": "LBSTRESN", "transformation": "7.8"},
        {"fhir_element": "MedicationRequest.medication", "cdisc_domain": "EX", "cdisc_variable": "EXTRT", "transformation": "NISHAMALAKI & GUDMAR (500mg BD)"}
    ]

    cdisc_sdtm_sample = [
        {"STUDYID": "AYU-002", "DOMAIN": "DM", "USUBJID": "AIIA-AYU-002-001", "SUBJID": "001", "RFSTDTC": "2026-05-25", "AGE": 54, "SEX": "M", "RACE": "ASIAN", "ARMCD": "AYUR_TREAT", "ARM": "Nishamalaki Active Arm", "COUNTRY": "IND"},
        {"STUDYID": "AYU-002", "DOMAIN": "LB", "USUBJID": "AIIA-AYU-002-001", "LBSEQ": 1, "LBTESTCD": "HBA1C", "LBTEST": "Hemoglobin A1c", "LBORRES": "7.8", "LBORRESU": "%", "LBSTRESC": "7.8", "LBSTRESN": 7.8, "LBDTC": "2026-07-25"}
    ]

    return {
        "success": True,
        "pipeline": [
            {"step": 1, "name": "Hospital EHR Source", "format": "Hospital Clinical Systems & OPD Registries"},
            {"step": 2, "name": "FHIR R4 Ingestion Layer", "format": "HL7 FHIR Patient / Observation / MedicationRequest"},
            {"step": 3, "name": "Semantic Transformation Engine", "format": "AIIA Ayurveda CTMS Mapping Engine"},
            {"step": 4, "name": "CDISC Standard Repository", "format": "CDISC SDTM v1.7 / ADaM v1.1 Submission-Ready"}
        ],
        "fhir_patient": fhir_patient_sample,
        "fhir_observation": fhir_observation_sample,
        "mapping_rules": mapping_rules,
        "cdisc_sdtm": cdisc_sdtm_sample,
        "disclaimer": "Prototype interoperability demonstration. Designed for CDISC/FHIR harmonization in Ayurvedic research."
    }

# -------------------------------------------------------------
# 12. AUDIT TRAIL (Section 25)
# -------------------------------------------------------------
def get_ayur_audit_trail(limit=50):
    conn = get_app_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM ayur_audit_trail ORDER BY created_at DESC LIMIT ?", (limit,))
    audits = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"success": True, "total": len(audits), "audit_logs": audits}

def log_ayur_audit(user_name, action, module, prev_val="", new_val=""):
    conn = get_app_conn()
    c = conn.cursor()
    c.execute("""
    INSERT INTO ayur_audit_trail (audit_id, user_name, action, module, previous_value, new_value, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        f"AUD-{str(uuid.uuid4())[:6].upper()}",
        user_name or "AIIA User",
        action,
        module,
        str(prev_val),
        str(new_val),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

# -------------------------------------------------------------
# 13. REPORTS MODULE (Section 19)
# -------------------------------------------------------------
def get_ayur_report_data(report_type):
    conn = get_app_conn()
    c = conn.cursor()
    now_str = datetime.date.today().isoformat()

    if report_type == "trial_progress":
        c.execute("SELECT trial_id, trial_name, condition, city, pi_name, enrolled_participants, target_participants, progress_pct, trial_status FROM ayur_trials")
        records = [dict(r) for r in c.fetchall()]
        return {
            "title": "Trial Progress Report",
            "date": now_str,
            "columns": ["Trial ID", "Trial Name", "Condition", "Location", "Principal Investigator", "Enrolled", "Target", "Progress", "Status"],
            "records": records
        }
    elif report_type == "patient_enrollment":
        c.execute("SELECT patient_id, full_name, age, gender, condition, area_city, assigned_trial_id, treatment_status, registration_date FROM ayur_patients")
        records = [dict(r) for r in c.fetchall()]
        return {
            "title": "Patient Enrollment Report",
            "date": now_str,
            "columns": ["Patient ID", "Full Name", "Age", "Gender", "Condition", "Location", "Assigned Trial", "Treatment Status", "Registration Date"],
            "records": records
        }
    elif report_type == "site_performance":
        c.execute("SELECT site_id, city, hospital_name, condition, pi_name, participants_enrolled, participants_target, progress_pct, status FROM ayur_sites")
        records = [dict(r) for r in c.fetchall()]
        return {
            "title": "Site Performance Report",
            "date": now_str,
            "columns": ["Site ID", "City", "Hospital Name", "Condition", "Lead PI", "Enrolled", "Target", "Progress %", "Status"],
            "records": records
        }
    elif report_type == "doctor_participation":
        c.execute("SELECT doctor_id, name, qualification, specialization, experience_years, current_site, trial_id, role, status FROM ayur_doctors")
        records = [dict(r) for r in c.fetchall()]
        return {
            "title": "Doctor Participation Report",
            "date": now_str,
            "columns": ["Doctor ID", "Name", "Qualification", "Specialization", "Experience (Yrs)", "Current Site", "Assigned Trial", "Role", "Status"],
            "records": records
        }
    elif report_type == "adverse_events":
        c.execute("SELECT event_id, patient_id, patient_name, trial_id, condition, location, adverse_event, severity, serious, status, date_reported FROM ayur_adverse_events")
        records = [dict(r) for r in c.fetchall()]
        return {
            "title": "Adverse Events & Safety Report",
            "date": now_str,
            "columns": ["Event ID", "Patient ID", "Patient Name", "Trial ID", "Condition", "Location", "Adverse Event", "Severity", "Serious", "Status", "Reported Date"],
            "records": records
        }
    elif report_type == "pending_approvals":
        c.execute("SELECT approval_id, trial_id, city, hospital_name, approval_type, status, submission_date, action_required FROM ayur_approvals")
        records = [dict(r) for r in c.fetchall()]
        return {
            "title": "Pending Regulatory & Ethics Approvals Report",
            "date": now_str,
            "columns": ["Approval ID", "Trial ID", "City", "Hospital", "Type", "Status", "Submitted", "Action Required"],
            "records": records
        }
    elif report_type == "gcp_compliance":
        c.execute("SELECT item_id, title, category, is_completed, last_reviewed, reviewed_by FROM ayur_gcp_checklist")
        records = [dict(r) for r in c.fetchall()]
        return {
            "title": "GCP Compliance Audit Report",
            "date": now_str,
            "columns": ["Item ID", "GCP Requirement", "Category", "Status", "Last Reviewed", "Reviewed By"],
            "records": records
        }
    else:
        c.execute("SELECT trial_id, trial_name, condition, city, trial_status FROM ayur_trials")
        records = [dict(r) for r in c.fetchall()]
        return {
            "title": "General Clinical Trial Summary Report",
            "date": now_str,
            "columns": ["Trial ID", "Trial Name", "Condition", "City", "Status"],
            "records": records
        }
