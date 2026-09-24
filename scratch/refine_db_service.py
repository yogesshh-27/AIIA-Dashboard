with open("db_service.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update get_ayur_approvals
old_appr = """def get_ayur_approvals():
    conn = get_app_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM ayur_approvals ORDER BY submission_date DESC")
    approvals = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"success": True, "approvals": approvals}"""

new_appr = """def get_ayur_approvals(site=None, approval_type=None, status=None):
    conn = get_app_connection()
    c = conn.cursor()
    query = "SELECT * FROM ayur_approvals WHERE 1=1"
    params = []
    if site and site != 'All':
        query += " AND (site = ? OR city = ?)"
        params.extend([site, site])
    if approval_type and approval_type != 'All':
        query += " AND approval_type = ?"
        params.append(approval_type)
    if status and status != 'All':
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY submission_date DESC"
    c.execute(query, params)
    approvals = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"success": True, "approvals": approvals}"""

if old_appr in code:
    code = code.replace(old_appr, new_appr)
    print("Replaced get_ayur_approvals successfully")

# 2. Update get_ayur_audit_trail
old_audit = 'return {"success": True, "total": len(audits), "audit_logs": audits}'
new_audit = 'return {"success": True, "total": len(audits), "audit_logs": audits, "audit_trail": audits}'
if old_audit in code:
    code = code.replace(old_audit, new_audit)
    print("Updated get_ayur_audit_trail successfully")

# 3. Update get_ayur_report_data helper
old_rep_func = """def get_ayur_report_data(report_type):
    conn = get_app_connection()
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
        }"""

new_rep_func = """def get_ayur_report_data(report_type):
    conn = get_app_connection()
    c = conn.cursor()
    now_str = datetime.date.today().isoformat()

    if report_type in ("trial_progress", "trial-progress"):
        c.execute("SELECT trial_id, trial_name, condition, city, pi_name, enrolled_participants, target_participants, progress_pct, trial_status FROM ayur_trials")
        records = [dict(r) for r in c.fetchall()]
        title = "Trial Progress Report"
        columns = ["Trial ID", "Trial Name", "Condition", "Location", "Principal Investigator", "Enrolled", "Target", "Progress", "Status"]
    elif report_type in ("patient_enrollment", "patient-enrollment"):
        c.execute("SELECT patient_id, full_name, age, gender, condition, area_city, assigned_trial_id, treatment_status, registration_date FROM ayur_patients")
        records = [dict(r) for r in c.fetchall()]
        title = "Patient Enrollment Report"
        columns = ["Patient ID", "Full Name", "Age", "Gender", "Condition", "Location", "Assigned Trial", "Treatment Status", "Registration Date"]
    elif report_type in ("site_performance", "site-performance"):
        c.execute("SELECT site_id, city, hospital_name, condition, pi_name, participants_enrolled, participants_target, progress_pct, status FROM ayur_sites")
        records = [dict(r) for r in c.fetchall()]
        title = "Site Performance Report"
        columns = ["Site ID", "City", "Hospital Name", "Condition", "Lead PI", "Enrolled", "Target", "Progress %", "Status"]
    elif report_type in ("doctor_participation", "doctor-participation"):
        c.execute("SELECT doctor_id, name, qualification, specialization, experience_years, current_site, trial_id, role, status FROM ayur_doctors")
        records = [dict(r) for r in c.fetchall()]
        title = "Doctor Participation Report"
        columns = ["Doctor ID", "Name", "Qualification", "Specialization", "Experience (Yrs)", "Current Site", "Assigned Trial", "Role", "Status"]
    elif report_type in ("adverse_events", "adverse-events", "adverse_event"):
        c.execute("SELECT event_id, patient_id, patient_name, trial_id, condition, location, adverse_event, severity, serious, status, date_reported FROM ayur_adverse_events")
        records = [dict(r) for r in c.fetchall()]
        title = "Adverse Events & Safety Report"
        columns = ["Event ID", "Patient ID", "Patient Name", "Trial ID", "Condition", "Location", "Adverse Event", "Severity", "Serious", "Status", "Reported Date"]
    elif report_type in ("pending_approvals", "pending-approvals", "pending_approval"):
        c.execute("SELECT approval_id, trial_id, city, hospital_name, approval_type, status, submission_date, action_required FROM ayur_approvals")
        records = [dict(r) for r in c.fetchall()]
        title = "Pending Regulatory & Ethics Approvals Report"
        columns = ["Approval ID", "Trial ID", "City", "Hospital", "Type", "Status", "Submitted", "Action Required"]
    elif report_type in ("gcp_compliance", "gcp-compliance"):
        c.execute("SELECT item_id, title, category, is_completed, last_reviewed, reviewed_by FROM ayur_gcp_checklist")
        records = [dict(r) for r in c.fetchall()]
        title = "GCP Compliance Audit Report"
        columns = ["Item ID", "GCP Requirement", "Category", "Status", "Last Reviewed", "Reviewed By"]
    else:
        c.execute("SELECT trial_id, trial_name, condition, city, trial_status FROM ayur_trials")
        records = [dict(r) for r in c.fetchall()]
        title = "General Clinical Trial Summary Report"
        columns = ["Trial ID", "Trial Name", "Condition", "City", "Status"]

    conn.close()
    return {
        "success": True,
        "title": title,
        "report_title": title,
        "date": now_str,
        "generated_at": now_str,
        "institution": "All India Institute of Ayurveda (AIIA)",
        "columns": columns,
        "rows": records,
        "records": records
    }"""

if old_rep_func in code:
    code = code.replace(old_rep_func, new_rep_func)
    print("Replaced get_ayur_report_data successfully")

with open("db_service.py", "w", encoding="utf-8") as f:
    f.write(code)

print("db_service.py update completed.")
