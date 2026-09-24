with open("db_service.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Fix get_ayur_approvals
target_appr = "def get_ayur_approvals():\n    conn = get_app_conn()\n    c = conn.cursor()\n    c.execute(\"SELECT * FROM ayur_approvals ORDER BY submission_date DESC\")\n    approvals = [dict(r) for r in c.fetchall()]\n    conn.close()\n    return {\"success\": True, \"approvals\": approvals}"

replacement_appr = """def get_ayur_approvals(site=None, approval_type=None, status=None):
    conn = get_app_conn()
    c = conn.cursor()
    query = "SELECT * FROM ayur_approvals WHERE 1=1"
    params = []
    if site and site != 'All':
        query += " AND site = ?"
        params.append(site)
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

if target_appr in code:
    code = code.replace(target_appr, replacement_appr)
    print("Replaced get_ayur_approvals successfully")

# 2. Fix audit trail keys
if '"audit_trail": audit_logs' not in code:
    code = code.replace('"audit_logs": audit_logs', '"audit_logs": audit_logs, "audit_trail": audit_logs')
    print("Added audit_trail key to get_ayur_audit_trail")

# 3. Fix interop keys
if '"fhir_preview":' not in code:
    code = code.replace('"fhir_patient": fhir_patient,', '"fhir_preview": fhir_patient, "fhir_patient": fhir_patient,')
    code = code.replace('"cdisc_sdtm": cdisc_sdtm,', '"cdisc_preview": cdisc_sdtm, "cdisc_sdtm": cdisc_sdtm,')
    print("Added fhir_preview and cdisc_preview keys to get_ayur_interop_demo")

# 4. Fix get_ayur_report_data return
target_rep = '''    return {
        "title": title,
        "date": datetime.date.today().isoformat(),
        "columns": columns,
        "records": records
    }'''

replacement_rep = '''    return {
        "success": True,
        "title": title,
        "report_title": title,
        "date": datetime.date.today().isoformat(),
        "generated_at": datetime.date.today().isoformat(),
        "institution": "All India Institute of Ayurveda (AIIA)",
        "columns": columns,
        "rows": records,
        "records": records
    }'''

if target_rep in code:
    code = code.replace(target_rep, replacement_rep)
    print("Replaced get_ayur_report_data return successfully")

with open("db_service.py", "w", encoding="utf-8") as f:
    f.write(code)

print("db_service.py updated successfully.")
