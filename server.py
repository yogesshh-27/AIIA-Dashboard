import http.server
import socketserver
import urllib.parse
import json
import os
import io
import csv
import sys
from typing import Dict, Any

import db_service

PORT = 8000
HOST = "127.0.0.1"

class AIIADashboardHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS and caching control
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Session-Token, X-Active-Role")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def get_auth_context(self) -> Dict[str, Any]:
        """Extract active user, role, and permissions from headers or token."""
        auth_header = self.headers.get("Authorization", "")
        token = ""
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        if not token:
            token = self.headers.get("X-Session-Token", "")
        if not token:
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            token = params.get("token", [""])[0]

        session = db_service.get_session(token) if token else None

        # Demonstration role switcher header (allows instant role switching during demo)
        demo_role = self.headers.get("X-Active-Role", "").strip()

        if session:
            active_role = demo_role if demo_role else session.get("role_name", "Administrator")
            user_name = session.get("full_name", session.get("username", "Authenticated User"))
            user_id = session.get("user_id", 1)
            perms = session.get("permissions", ["*"])
        elif demo_role:
            active_role = demo_role
            user_name = f"Demo User ({demo_role})"
            user_id = 1
            # Retrieve role permissions
            roles = db_service.get_roles()
            role_dict = next((r for r in roles if r["name"] == active_role), None)
            perms = role_dict["permissions"] if role_dict else ["*"]
        else:
            # Default institutional role
            active_role = "Administrator"
            user_name = "Prof. (Dr.) Tanuja Nesari"
            user_id = 1
            perms = ["*"]

        return {
            "token": token or "demo-session-token",
            "user_id": user_id,
            "user_name": user_name,
            "role": active_role,
            "permissions": perms,
            "is_authenticated": True
        }

    def require_permission(self, permission_code: str) -> bool:
        """Enforce server-side authorization check. Return False and send 403 if unauthorized."""
        auth = self.get_auth_context()
        role = auth["role"]

        # Regulator role is strictly read-only: deny all modifying requests
        if role == "Regulator / Read-only" and self.command in ("POST", "PUT", "DELETE", "PATCH"):
            self.send_json_response({
                "error": "Forbidden: Read-Only Access",
                "message": f"Role '{role}' is restricted to authorized read-only audit access. All modifying actions are prohibited.",
                "role": role,
                "required_permission": permission_code
            }, status=403)
            return False

        if not db_service.has_permission(role, permission_code):
            self.send_json_response({
                "error": "Forbidden",
                "message": f"Role '{role}' is not authorized to perform action '{permission_code}'. Server-side RBAC restriction enforced.",
                "role": role,
                "required_permission": permission_code
            }, status=403)
            return False
        return True

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query_params = urllib.parse.parse_qs(parsed.query)

        def get_param(key, default=""):
            return query_params.get(key, [default])[0]

        if path == "/api/dashboard/portfolio":
            self.send_json_response(db_service.get_dashboard_portfolio())
        elif path == "/api/stats":
            self.send_json_response(db_service.get_kpis())
        elif path == "/api/trials":
            scope = get_param("scope", "aiia")
            search = get_param("search", "")
            status = get_param("status", "")
            phase = get_param("phase", "")
            trial_type = get_param("trial_type", "")
            sponsor = get_param("sponsor", "")
            thesis = get_param("thesis", "")
            year = get_param("year", "")
            date_from = get_param("date_from", "")
            date_to = get_param("date_to", "")
            sort_by = get_param("sort_by", "registered_on")
            sort_dir = get_param("sort_dir", "desc")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "15"))

            self.send_json_response(db_service.get_trials(
                scope=scope, search=search, status=status,
                phase=phase, trial_type=trial_type, sponsor=sponsor,
                thesis=thesis, year=year, date_from=date_from, date_to=date_to,
                sort_by=sort_by, sort_dir=sort_dir, page=page, limit=limit
            ))
        elif path.startswith("/api/trials/"):
            trial_id_str = path.split("/")[-1]
            try:
                trial_id = int(trial_id_str)
                trial_data = db_service.get_trial_detail(trial_id)
            except (ValueError, TypeError):
                trial_data = None
            if trial_data:
                self.send_json_response(trial_data)
            else:
                self.send_error_response(404, "Trial not found")
        elif path == "/api/governance":
            scope = get_param("scope", "aiia")
            self.send_json_response(db_service.get_governance_insights(scope=scope))
        elif path == "/api/analytics":
            scope = get_param("scope", "aiia")
            self.send_json_response(db_service.get_analytics_deep_dive(scope=scope))
        elif path == "/api/cdisc":
            search = get_param("search", "")
            limit = int(get_param("limit", "50"))
            self.send_json_response(db_service.search_cdisc_concepts(search=search, limit=limit))
        elif path == "/api/app/stats":
            self.send_json_response(db_service.get_app_db_stats())
        elif path == "/api/app/trials":
            scope = get_param("scope", "aiia")
            search = get_param("search", "")
            status = get_param("status", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "15"))
            self.send_json_response(db_service.get_app_trials(
                scope=scope, search=search, status=status, page=page, limit=limit
            ))
        elif path == "/api/ctri-extractor/trials" or path == "/api/ctri/dataset":
            json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ctri-extractor", "output", "ctri_trials.json")
            if os.path.exists(json_file):
                with open(json_file, "r", encoding="utf-8") as f:
                    trials = json.load(f)
                for t in trials:
                    c_num = t.get("ctri_number", "")
                    s_url = t.get("source_url", "")
                    if s_url and "showallp.php" in s_url and c_num:
                        if "userName=" in s_url:
                            base = s_url.split("userName=")[0]
                            t["source_url"] = f"{base}userName={urllib.parse.quote(c_num)}"
                        else:
                            sep = "&" if "?" in s_url else "?"
                            t["source_url"] = f"{s_url}{sep}userName={urllib.parse.quote(c_num)}"
            else:
                trials = []
            search_term = get_param("search", "").lower()
            if search_term:
                trials = [
                    t for t in trials if search_term in (t.get("public_title", "") or "").lower()
                    or search_term in (t.get("ctri_number", "") or "").lower()
                    or search_term in (t.get("condition", "") or "").lower()
                    or search_term in (t.get("intervention_name", "") or "").lower()
                    or search_term in (t.get("principal_investigator", "") or "").lower()
                ]
            limit_val = int(get_param("limit", "100"))
            self.send_json_response({"total": len(trials), "trials": trials[:limit_val]})
        elif path == "/api/ctri-extractor/quality-report":
            report_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ctri-extractor", "output", "quality_report.txt")
            if os.path.exists(report_file):
                with open(report_file, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                content = "Quality report not found."
            self.send_json_response({"report": content})
        elif path == "/api/ctms/overview":
            self.send_json_response(db_service.get_ctms_overview())
        elif path == "/api/ctms/timelines":
            search = get_param("search", "")
            status = get_param("status", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "15"))
            self.send_json_response(db_service.get_ctms_timelines(search=search, status=status, page=page, limit=limit))
        elif path == "/api/ctms/recruitment":
            search = get_param("search", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "15"))
            self.send_json_response(db_service.get_ctms_recruitment(search=search, page=page, limit=limit))
        elif path == "/api/ctms/monitoring":
            search = get_param("search", "")
            status = get_param("status", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "15"))
            self.send_json_response(db_service.get_ctms_monitoring(search=search, status=status, page=page, limit=limit))
        elif path == "/api/ctms/deviations":
            search = get_param("search", "")
            severity = get_param("severity", "")
            status = get_param("status", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "15"))
            self.send_json_response(db_service.get_ctms_deviations(search=search, severity=severity, status=status, page=page, limit=limit))
        elif path == "/api/ctms/milestones":
            search = get_param("search", "")
            status = get_param("status", "")
            overdue_only = get_param("overdue_only", "false").lower() in ("true", "1")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "15"))
            self.send_json_response(db_service.get_ctms_milestones(search=search, status=status, overdue_only=overdue_only, page=page, limit=limit))
        elif path == "/api/compliance/overview":
            self.send_json_response(db_service.get_compliance_overview())
        elif path == "/api/compliance/data-quality":
            scope = get_param("scope", "aiia")
            self.send_json_response(db_service.calculate_data_quality_audit(scope=scope))
        elif path == "/api/alerts":
            category = get_param("category", "")
            severity = get_param("severity", "")
            status = get_param("status", "")
            search = get_param("search", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "15"))
            self.send_json_response(db_service.get_alerts(category=category, severity=severity, status=status, search=search, page=page, limit=limit))
        elif path == "/api/pv/overview":
            self.send_json_response(db_service.get_pv_overview())
        elif path == "/api/pv/adverse-events":
            search = get_param("search", "")
            severity = get_param("severity", "")
            status = get_param("status", "")
            serious = get_param("serious_only", "false").lower() in ("true", "1")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "20"))
            self.send_json_response(db_service.get_pv_adverse_events(
                search=search, severity=severity, serious_only=serious, status=status, page=page, limit=limit))
        elif path == "/api/pv/signals":
            search = get_param("search", "")
            severity = get_param("severity", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "20"))
            self.send_json_response(db_service.get_pv_safety_signals(
                search=search, severity=severity, page=page, limit=limit))
        elif path == "/api/pv/reporting":
            search = get_param("search", "")
            status = get_param("status", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "20"))
            self.send_json_response(db_service.get_pv_reporting_deadlines(
                search=search, status=status, page=page, limit=limit))
        
        # --- SECURITY & RBAC GET ROUTES ---
        elif path == "/api/auth/roles":
            self.send_json_response(db_service.get_roles())
        elif path == "/api/auth/users":
            self.send_json_response(db_service.get_users())
        elif path == "/api/auth/me":
            auth = self.get_auth_context()
            self.send_json_response(auth)

        # --- HASH-LINKED AUDIT TRAIL GET ROUTES ---
        elif path == "/api/audit/chain":
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "20"))
            search = get_param("search", "")
            role_filter = get_param("role", "")
            self.send_json_response(db_service.get_audit_chain(page=page, limit=limit, search=search, role_filter=role_filter))
        elif path == "/api/audit/verify":
            self.send_json_response(db_service.verify_audit_chain())

        # --- INTEROPERABILITY (CDISC & FHIR R4) GET ROUTES ---
        elif path == "/api/interop/cdisc/overview":
            self.send_json_response(db_service.get_cdisc_overview())
        elif path == "/api/interop/cdisc/mapping":
            self.send_json_response(db_service.get_cdisc_mappings())
        elif path == "/api/interop/cdisc/export":
            fmt = get_param("format", "sdtm").lower()
            trial_id = get_param("trial_id", None)
            if fmt == "sdtm":
                self.send_json_response(db_service.export_cdisc_sdtm(trial_id=trial_id))
            elif fmt == "adam":
                self.send_json_response(db_service.export_cdisc_adam(trial_id=trial_id))
            elif fmt == "define_xml":
                xml_data = db_service.export_cdisc_define_xml(trial_id=trial_id).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/xml; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="define_xml_demonstration.xml"')
                self.send_header("Content-Length", str(len(xml_data)))
                self.end_headers()
                self.wfile.write(xml_data)
            else:
                self.send_json_response({"error": f"Unsupported export format '{fmt}'"}, status=400)
        elif path == "/api/interop/fhir/study":
            trial_id = get_param("trial_id", None)
            self.send_json_response(db_service.get_fhir_research_study(trial_id=trial_id))

        # --- DOCUMENTS GET ROUTES ---
        elif path == "/api/documents/summary":
            self.send_json_response(db_service.get_documents_summary())
        elif path == "/api/documents":
            category = get_param("category", "")
            search = get_param("search", "")
            trial_ctri = get_param("trial_ctri", "")
            status = get_param("status", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "20"))
            self.send_json_response(db_service.get_documents(
                category=category, search=search, trial_ctri=trial_ctri, status=status, page=page, limit=limit
            ))
        elif path.startswith("/api/documents/") and path.endswith("/download"):
            if not self.require_permission("documents:read"):
                return
            parts = path.split("/")
            doc_id_str = parts[3]
            version = get_param("version", "")
            doc_file = db_service.get_document_file_path(doc_id_str, version=version if version else None)
            if not doc_file or not os.path.exists(doc_file["file_path"]):
                self.send_error_response(404, "Document file not found in secure repository.")
                return

            auth = self.get_auth_context()
            db_service.log_audit_event(
                user_name=auth["user_name"],
                role=auth["role"],
                action="DOWNLOAD_DOCUMENT",
                entity="DocumentRepository",
                entity_id=doc_file["doc_id"],
                previous_value="Stored Securely",
                new_value=f"Downloaded {doc_file['file_name']} (v{doc_file['version']}) - SHA256: {doc_file['checksum_sha256'][:12]}...",
                ip_address=self.client_address[0] if self.client_address else "127.0.0.1"
            )

            with open(doc_file["file_path"], "rb") as f:
                file_bytes = f.read()

            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{doc_file["file_name"]}"')
            self.send_header("Content-Length", str(len(file_bytes)))
            self.send_header("X-Document-ID", doc_file["doc_id"])
            self.send_header("X-Document-Checksum", doc_file["checksum_sha256"])
            self.end_headers()
            self.wfile.write(file_bytes)
            return

        elif path.startswith("/api/documents/"):
            doc_id_str = path.split("/")[-1]
            doc_detail = db_service.get_document_detail(doc_id_str)
            if doc_detail:
                self.send_json_response(doc_detail)
            else:
                self.send_error_response(404, "Document not found")

        # --- REPORTS GET & EXPORT ROUTES ---
        elif path == "/api/reports/data" or (path.startswith("/api/reports/") and path != "/api/reports/export"):
            if path == "/api/reports/data":
                rep_type = get_param("type", "portfolio").lower()
            else:
                rep_type = path.replace("/api/reports/", "").strip().lower()

            if rep_type == "portfolio":
                self.send_json_response(db_service.get_report_portfolio())
            elif rep_type == "recruitment":
                self.send_json_response(db_service.get_report_recruitment())
            elif rep_type == "compliance":
                self.send_json_response(db_service.get_report_compliance())
            elif rep_type == "safety":
                self.send_json_response(db_service.get_report_safety())
            elif rep_type in ("data_quality", "data-quality"):
                self.send_json_response(db_service.get_report_data_quality())
            elif rep_type == "audit":
                self.send_json_response(db_service.get_report_audit())
            else:
                self.send_error_response(400, f"Unknown report type '{rep_type}'")

        elif path == "/api/reports/export":
            rep_type = get_param("type", "portfolio").lower()
            export_fmt = get_param("format", "csv").lower()
            auth = self.get_auth_context()

            if export_fmt in ("pdf", "html"):
                html_content = db_service.generate_report_printable_html(
                    rep_type,
                    generated_by=auth.get("user_name", "Prof. (Dr.) Tanuja Nesari"),
                    role=auth.get("role", "Administrator")
                )
                html_bytes = html_content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html_bytes)))
                self.end_headers()
                self.wfile.write(html_bytes)
                return
            else:
                csv_content = db_service.generate_report_csv(rep_type)
                csv_bytes = csv_content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", f'attachment; filename="AIIA_{rep_type.upper()}_REPORT.csv"')
                self.send_header("Content-Length", str(len(csv_bytes)))
                self.end_headers()
                self.wfile.write(csv_bytes)
                return

        # --- EXPORT ROUTE ---
        elif path == "/api/export":
            scope = get_param("scope", "aiia")
            search = get_param("search", "")
            status = get_param("status", "")
            phase = get_param("phase", "")
            trial_type = get_param("trial_type", "")
            sponsor = get_param("sponsor", "")
            thesis = get_param("thesis", "")
            year = get_param("year", "")
            date_from = get_param("date_from", "")
            date_to = get_param("date_to", "")
            sort_by = get_param("sort_by", "registered_on")
            sort_dir = get_param("sort_dir", "desc")
            export_fmt = get_param("format", "csv").lower()

            res = db_service.get_trials(
                scope=scope, search=search, status=status,
                phase=phase, trial_type=trial_type, sponsor=sponsor,
                thesis=thesis, year=year, date_from=date_from, date_to=date_to,
                sort_by=sort_by, sort_dir=sort_dir, page=1, limit=2000
            )

            if export_fmt == "json":
                json_bytes = json.dumps(res["data"], indent=2, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="aiia_trials_export.json"')
                self.send_header("Content-Length", str(len(json_bytes)))
                self.send_header("X-Export-Disclaimer", "Prototype mapping/export - AIIA Clinical Trial Intelligence")
                self.end_headers()
                self.wfile.write(json_bytes)
            else:
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow([
                    "CTRI Number", "Public Title", "Scientific Title", "Recruitment Status",
                    "Phase", "Type of Trial", "Target Sample Size", "Registration Date",
                    "Primary Sponsor", "Principal Investigator", "Affiliation"
                ])
                for r in res["data"]:
                    writer.writerow([
                        r.get("CTRI_Number", ""),
                        r.get("Public_Title", ""),
                        r.get("Scientific_Title", ""),
                        r.get("Recruitment_Status_India", ""),
                        r.get("Phase", ""),
                        r.get("Type_of_Trial", ""),
                        r.get("Target_Sample_Size", ""),
                        r.get("Registration_Date", ""),
                        r.get("Primary_Sponsor", ""),
                        r.get("PI_Name", ""),
                        r.get("PI_Affiliation", "")
                    ])
                csv_bytes = output.getvalue().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="aiia_trials_export.csv"')
                self.send_header("Content-Length", str(len(csv_bytes)))
                self.end_headers()
                self.wfile.write(csv_bytes)

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

        else:
            dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
            dist_index = os.path.join(dist_dir, "index.html")
            
            if path == "/" or path == "/index.html":
                if os.path.exists(dist_index):
                    self.path = "/dist/index.html"
                else:
                    self.path = "/index.html"
            elif path.startswith("/assets/"):
                asset_path = os.path.join(dist_dir, path.lstrip("/"))
                if os.path.exists(asset_path):
                    self.path = "/dist" + path
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"
        try:
            body = json.loads(post_body.decode("utf-8")) if post_body else {}
        except Exception:
            body = {}

        # 1. AUTH LOGIN
        if path == "/api/auth/login":
            username = body.get("username", "")
            password = body.get("password", "")
            ip = self.client_address[0] if self.client_address else "127.0.0.1"
            agent = self.headers.get("User-Agent", "WebBrowser")
            auth_res = db_service.authenticate_user(username, password, ip_address=ip, user_agent=agent)
            if auth_res:
                self.send_json_response(auth_res)
            else:
                self.send_json_response({"error": "Invalid institutional credentials or inactive account."}, status=401)
            return

        # 2. ROLE SWITCHER (PROTOTYPE DEMONSTRATION)
        elif path == "/api/auth/switch-role":
            target_role = body.get("role", "Administrator")
            token = self.headers.get("X-Session-Token", "")
            res = db_service.switch_role_session(token, target_role)
            if not res:
                # Fallback for sessionless demo switch
                roles = db_service.get_roles()
                role_dict = next((r for r in roles if r["name"] == target_role), None)
                res = {
                    "role_name": target_role,
                    "full_name": f"AIIA User ({target_role})",
                    "permissions": role_dict["permissions"] if role_dict else ["*"],
                    "is_authenticated": True
                }
            self.send_json_response(res)
            return

        # 3. AUDIT LOGGING
        elif path == "/api/audit/log":
            if not self.require_permission("audit:write"):
                return
            auth = self.get_auth_context()
            res = db_service.log_audit_event(
                user_name=body.get("user", auth["user_name"]),
                role=body.get("role", auth["role"]),
                action=body.get("action", "USER_ACTION"),
                entity=body.get("entity", "GeneralEntity"),
                entity_id=body.get("entity_id", "N/A"),
                previous_value=body.get("previous_value", ""),
                new_value=body.get("new_value", ""),
                ip_address=self.client_address[0] if self.client_address else "127.0.0.1",
                device_metadata=self.headers.get("User-Agent", "WebBrowser")[:120]
            )
            self.send_json_response(res)
            return

        # 4. AUDIT TAMPER DEMONSTRATION (TESTING HASH VERIFICATION FAILURE)
        elif path == "/api/audit/tamper-demo":
            if not self.require_permission("audit:admin"):
                return
            event_id = body.get("event_id", "EVT-0003")
            malicious_val = body.get("malicious_value", "Tampered enrollment count (UNAUTHORIZED_MUTATION)")
            res = db_service.tamper_audit_event_demo(event_id, malicious_val)
            self.send_json_response(res)
            return

        # 5. AUDIT RESTORE DEMONSTRATION
        elif path == "/api/audit/restore-demo":
            if not self.require_permission("audit:admin"):
                return
            res = db_service.restore_audit_chain_demo()
            self.send_json_response(res)
            return

        # 6. FHIR R4 STRUCTURE VALIDATION
        elif path == "/api/interop/fhir/validate":
            validation_res = db_service.validate_fhir_research_study(body)
            self.send_json_response(validation_res)
            return

        # 7. AIIA TRIAL ASSISTANT QUERY
        elif path == "/api/assistant/query":
            user_query = body.get("query", "").strip()
            if not user_query:
                self.send_json_response({"error": "Empty query"}, status=400)
                return
            ans = db_service.query_trial_assistant(user_query)
            # Log query to audit trail
            auth = self.get_auth_context()
            db_service.log_audit_event(
                user_name=auth["user_name"],
                role=auth["role"],
                action="ASSISTANT_QUERY",
                entity="TrialAssistant",
                entity_id=ans.get("intent", "QUERY"),
                previous_value="",
                new_value=user_query[:100],
                ip_address=self.client_address[0] if self.client_address else "127.0.0.1"
            )
            self.send_json_response(ans)
            return

        # 8. ALERTS STATUS UPDATE
        elif path.startswith("/api/alerts/") and path.endswith("/status"):
            # Enforce server-side authorization: Regulators and read-only roles cannot modify alert status
            if not self.require_permission("alerts:write"):
                return
            try:
                parts = path.strip("/").split("/")
                alert_id = int(parts[2])
                new_status = body.get("status", "Acknowledged")
                auth = self.get_auth_context()
                user_name = body.get("user", auth["user_name"])

                res = db_service.update_alert_status(alert_id, new_status, user_name)
                # Log audit event
                db_service.log_audit_event(
                    user_name=user_name,
                    role=auth["role"],
                    action="UPDATE_ALERT_STATUS",
                    entity="Alert",
                    entity_id=str(alert_id),
                    previous_value="Active",
                    new_value=new_status,
                    ip_address=self.client_address[0] if self.client_address else "127.0.0.1"
                )
                self.send_json_response(res)
            except Exception as e:
                self.send_json_response({"error": str(e)}, status=400)
            return
        # 9. DOCUMENT UPLOAD & VERSIONING
        elif path == "/api/documents/upload":
            if not self.require_permission("documents:write"):
                return
            auth = self.get_auth_context()
            doc_name = body.get("document_name", "New Institutional Document")
            category = body.get("category", "Protocol")
            trial_ctri = body.get("trial_ctri", "")
            version = body.get("version", "v1.0")
            uploaded_by = auth.get("user_name", "Prof. (Dr.) Tanuja Nesari")
            status = body.get("status", "Under Review")
            description = body.get("description", "")
            file_name = body.get("file_name", f"{doc_name.replace(' ', '_')}.pdf")
            file_content_raw = body.get("file_content", f"Institutional Record: {doc_name}\nCategory: {category}\nVersion: {version}\n")
            if isinstance(file_content_raw, str):
                file_bytes = file_content_raw.encode("utf-8")
            else:
                file_bytes = bytes(file_content_raw)

            res = db_service.create_document(
                document_name=doc_name, category=category, trial_ctri=trial_ctri,
                version=version, uploaded_by=uploaded_by, status=status,
                description=description, file_name=file_name, file_content_bytes=file_bytes
            )
            self.send_json_response(res)
            return

        elif path.startswith("/api/documents/") and path.endswith("/version"):
            if not self.require_permission("documents:write"):
                return
            parts = path.strip("/").split("/")
            doc_id_str = parts[2]
            auth = self.get_auth_context()
            version = body.get("version", "v1.1")
            change_summary = body.get("change_summary", "Routine periodic version update.")
            uploaded_by = auth.get("user_name", "Principal Investigator")
            status = body.get("status", "Approved")
            file_name = body.get("file_name", f"Document_Update_{version}.pdf")
            file_content_raw = body.get("file_content", f"Updated Document Version: {version}\nSummary: {change_summary}\n")
            if isinstance(file_content_raw, str):
                file_bytes = file_content_raw.encode("utf-8")
            else:
                file_bytes = bytes(file_content_raw)

            res = db_service.add_document_version(
                document_id=doc_id_str, version=version, change_summary=change_summary,
                uploaded_by=uploaded_by, status=status, file_name=file_name, file_content_bytes=file_bytes
            )
            self.send_json_response(res)
            return


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

        self.send_json_response({"error": "Endpoint not found"}, status=404)

    def send_json_response(self, data: Any, status: int = 200):
        json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(json_bytes)))
        self.end_headers()
        self.wfile.write(json_bytes)

    def send_error_response(self, code: int, message: str):
        err = {"error": message, "code": code}
        json_bytes = json.dumps(err).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(json_bytes)))
        self.end_headers()
        self.wfile.write(json_bytes)

def run():
    db_service.init_indexes()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((HOST, PORT), AIIADashboardHandler) as httpd:
        print(f"AIIA Dashboard Server running at http://{HOST}:{PORT}")
        sys.stdout.flush()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.server_close()

if __name__ == "__main__":
    run()
