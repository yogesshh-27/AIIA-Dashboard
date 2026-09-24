import re

with open("server.py", "r", encoding="utf-8") as f:
    content = f.read()

ayur_get_handlers = '''
        # ============================================================
        # AYURCTMS DEDICATED REST API (SIH PS 26046)
        # ============================================================
        elif path == "/api/ayur/dashboard/stats":
            self.send_json_response(db_service.get_ayur_dashboard_stats())
        elif path == "/api/ayur/sites":
            city = get_param("city", "")
            if city:
                self.send_json_response(db_service.get_ayur_sites(city=city))
            else:
                self.send_json_response(db_service.get_ayur_sites())
        elif path.startswith("/api/ayur/sites/"):
            city = urllib.parse.unquote(path.replace("/api/ayur/sites/", "").strip())
            self.send_json_response(db_service.get_ayur_sites(city=city))
        elif path == "/api/ayur/trials":
            status = get_param("status", "")
            condition = get_param("condition", "")
            location = get_param("location", "")
            search = get_param("search", "")
            self.send_json_response(db_service.get_ayur_trials(status=status, condition=condition, location=location, search=search))
        elif path.startswith("/api/ayur/trials/"):
            trial_id = urllib.parse.unquote(path.replace("/api/ayur/trials/", "").strip())
            self.send_json_response(db_service.get_ayur_trial_detail(trial_id))
        elif path == "/api/ayur/doctors":
            site = get_param("site", "")
            specialization = get_param("specialization", "")
            status = get_param("status", "")
            search = get_param("search", "")
            self.send_json_response(db_service.get_ayur_doctors(site=site, specialization=specialization, status=status, search=search))
        elif path.startswith("/api/ayur/doctors/"):
            doctor_id = urllib.parse.unquote(path.replace("/api/ayur/doctors/", "").strip())
            self.send_json_response(db_service.get_ayur_doctor_detail(doctor_id))
        elif path == "/api/ayur/patients":
            condition = get_param("condition", "")
            site = get_param("site", "")
            status = get_param("status", "")
            search = get_param("search", "")
            self.send_json_response(db_service.get_ayur_patients(condition=condition, site=site, status=status, search=search))
        elif path.startswith("/api/ayur/patients/"):
            patient_id = urllib.parse.unquote(path.replace("/api/ayur/patients/", "").strip())
            self.send_json_response(db_service.get_ayur_patient_detail(patient_id))
        elif path == "/api/ayur/pv/summary":
            self.send_json_response(db_service.get_ayur_pv_summary())
        elif path == "/api/ayur/pv/events":
            trial_id = get_param("trial_id", "")
            severity = get_param("severity", "")
            status = get_param("status", "")
            search = get_param("search", "")
            self.send_json_response(db_service.get_ayur_adverse_events(trial_id=trial_id, severity=severity, status=status, search=search))
        elif path == "/api/ayur/pv/signals":
            self.send_json_response(db_service.get_ayur_safety_signals())
        elif path == "/api/ayur/approvals":
            site = get_param("site", "")
            approval_type = get_param("type", "")
            status = get_param("status", "")
            self.send_json_response(db_service.get_ayur_approvals(site=site, approval_type=approval_type, status=status))
        elif path == "/api/ayur/gcp":
            self.send_json_response(db_service.get_ayur_gcp_checklist())
        elif path == "/api/ayur/reports":
            report_type = get_param("type", "trial_progress")
            self.send_json_response(db_service.get_ayur_report_data(report_type=report_type))
        elif path == "/api/ayur/reports/export":
            report_type = get_param("type", "trial_progress")
            fmt = get_param("format", "csv").lower()
            rep_data = db_service.get_ayur_report_data(report_type=report_type)
            if fmt == "csv":
                out = io.StringIO()
                writer = csv.writer(out)
                cols = rep_data.get("columns", [])
                writer.writerow(cols)
                for row in rep_data.get("rows", []):
                    writer.writerow([row.get(c, "") for c in cols])
                csv_bytes = out.getvalue().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", f'attachment; filename="AYURCTMS_{report_type.upper()}_REPORT.csv"')
                self.send_header("Content-Length", str(len(csv_bytes)))
                self.end_headers()
                self.wfile.write(csv_bytes)
                return
            else:
                self.send_json_response(rep_data)
                return
        elif path == "/api/ayur/search":
            q = get_param("q", get_param("search", ""))
            self.send_json_response(db_service.global_ayur_search(q))
        elif path == "/api/ayur/notifications":
            self.send_json_response(db_service.get_ayur_notifications())
        elif path == "/api/ayur/interop/demo":
            self.send_json_response(db_service.get_ayur_interop_demo())
        elif path == "/api/ayur/audit":
            self.send_json_response(db_service.get_ayur_audit_trail())
'''

ayur_post_handlers = '''
        # ============================================================
        # AYURCTMS POST HANDLERS
        # ============================================================
        elif path == "/api/ayur/patient/match":
            condition = body.get("condition", "")
            accessible_locations = body.get("accessible_locations", [])
            distance_pref = body.get("distance_pref", "")
            age = body.get("age")
            gender = body.get("gender")
            res = db_service.match_patient_trials(
                condition=condition,
                accessible_locations=accessible_locations,
                distance_pref=distance_pref,
                age=age,
                gender=gender
            )
            self.send_json_response(res)
            return

        elif path == "/api/ayur/auth/login":
            staff_id = body.get("staff_id", body.get("username", "")).strip()
            password = body.get("password", "").strip()

            # Prototype credentials check (AIIA001 / AIIA@123 or standard test credentials)
            if (staff_id.upper() == "AIIA001" and password == "AIIA@123") or (staff_id.lower() == "admin" and password == "admin123"):
                self.send_json_response({
                    "success": True,
                    "token": "ayur-demo-token-998811",
                    "user": {
                        "staff_id": "AIIA001",
                        "full_name": "Dr. Research Admin",
                        "role": "AIIA Authorized Staff",
                        "designation": "Clinical Research Coordinator / Admin",
                        "institution": "All India Institute of Ayurveda (AIIA), New Delhi"
                    },
                    "message": "Login successful. Welcome to AYURCTMS."
                })
            else:
                self.send_json_response({
                    "success": False,
                    "error": "Invalid Staff ID or Password. Demo credentials: Staff ID: AIIA001, Password: AIIA@123"
                }, status=401)
            return

        elif path == "/api/ayur/trials/create":
            res = db_service.create_ayur_trial(body)
            self.send_json_response(res)
            return

        elif path == "/api/ayur/pv/report":
            res = db_service.report_ayur_adverse_event(body)
            self.send_json_response(res)
            return

        elif path == "/api/ayur/approvals/update" or path.startswith("/api/ayur/approvals/"):
            approval_id = body.get("approval_id") or path.split("/")[-1]
            status = body.get("status", "Approved")
            notes = body.get("notes", "Reviewed by ethics/regulatory board.")
            reviewed_by = body.get("reviewed_by", "Ethics Committee Officer")
            res = db_service.update_ayur_approval(approval_id, status, notes, reviewed_by)
            self.send_json_response(res)
            return

        elif path == "/api/ayur/gcp/toggle":
            item_id = int(body.get("item_id", 1))
            is_completed = int(body.get("is_completed", 1))
            reviewed_by = body.get("reviewed_by", "Dr. Research Admin")
            res = db_service.toggle_ayur_gcp_item(item_id, is_completed, reviewed_by)
            self.send_json_response(res)
            return

        elif path == "/api/ayur/notifications/read":
            notif_id = int(body.get("notification_id", 1))
            res = db_service.mark_ayur_notification_read(notif_id)
            self.send_json_response(res)
            return
'''

# Insert GET handlers right before "else:\n            if path == "/":"
target_get = '        else:\n            if path == "/":'
if target_get in content and "/api/ayur/dashboard/stats" not in content:
    content = content.replace(target_get, ayur_get_handlers + "\n" + target_get)
    print("Inserted AYUR GET handlers into server.py")

# Insert POST handlers right before "self.send_json_response({"error": "Endpoint not found"}, status=404)"
target_post = '        self.send_json_response({"error": "Endpoint not found"}, status=404)'
if target_post in content and "/api/ayur/patient/match" not in content:
    content = content.replace(target_post, ayur_post_handlers + "\n" + target_post)
    print("Inserted AYUR POST handlers into server.py")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(content)

print("server.py updated successfully.")
