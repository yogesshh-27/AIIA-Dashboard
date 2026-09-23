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
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query_params = urllib.parse.parse_qs(parsed.query)

        # Helper to get single param value
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
            limit = int(get_param("limit", "25"))
            res = db_service.get_trials(
                scope=scope, search=search, status=status,
                phase=phase, trial_type=trial_type, sponsor=sponsor,
                thesis=thesis, year=year, date_from=date_from, date_to=date_to,
                sort_by=sort_by, sort_dir=sort_dir, page=page, limit=limit
            )
            self.send_json_response(res)
        elif path.startswith("/api/trials/"):
            trial_id_str = path.split("/api/trials/")[1]
            try:
                trial_id = int(trial_id_str)
                dossier = db_service.get_trial_dossier(trial_id)
                if dossier:
                    self.send_json_response(dossier)
                else:
                    self.send_error_response(404, "Trial record not found")
            except ValueError:
                self.send_error_response(400, "Invalid Trial ID")
        elif path == "/api/governance":
            self.send_json_response(db_service.get_governance_data())
        elif path == "/api/analytics":
            self.send_json_response(db_service.get_analytics_data())
        elif path == "/api/app/stats":
            # API for Normalized Application Database
            from database import SessionLocal
            import models
            db = SessionLocal()
            try:
                stats = {
                    "trials_total": db.query(models.Trial).count(),
                    "trials_aiia": db.query(models.Trial).filter(models.Trial.is_aiia == True).count(),
                    "trials_ayush": db.query(models.Trial).filter(models.Trial.is_ayush == True).count(),
                    "investigators": db.query(models.Investigator).count(),
                    "sponsors": db.query(models.Sponsor).count(),
                    "study_sites": db.query(models.StudySite).count(),
                    "interventions": db.query(models.Intervention).count(),
                    "outcomes": db.query(models.Outcome).count(),
                    "eligibility": db.query(models.Eligibility).count(),
                    "compliance_checks": db.query(models.ComplianceCheck).count(),
                    "alerts": db.query(models.Alert).count(),
                    "cdisc_mappings": db.query(models.CDISCMapping).count(),
                    "users": db.query(models.User).count(),
                    "roles": db.query(models.Role).count(),
                    "audit_logs": db.query(models.AuditLog).count()
                }
                self.send_json_response(stats)
            finally:
                db.close()
        elif path == "/api/app/trials":
            from database import SessionLocal
            import models
            db = SessionLocal()
            try:
                page = int(get_param("page", "1"))
                limit = int(get_param("limit", "25"))
                scope = get_param("scope", "")
                status = get_param("status", "")
                search = get_param("search", "")

                q = db.query(models.Trial)
                if scope == "aiia":
                    q = q.filter(models.Trial.is_aiia == True)
                elif scope == "ayush":
                    q = q.filter(models.Trial.is_ayush == True)
                if status:
                    q = q.filter(models.Trial.recruitment_status == status)
                if search:
                    st = f"%{search.strip()}%"
                    q = q.filter((models.Trial.ctri_number.like(st)) | (models.Trial.public_title.like(st)))

                total = q.count()
                items = q.order_by(models.Trial.id.desc()).offset((page - 1) * limit).limit(limit).all()

                data = [{
                    "id": t.id,
                    "ctri_number": t.ctri_number,
                    "public_title": t.public_title,
                    "phase": t.phase,
                    "recruitment_status": t.recruitment_status,
                    "registered_on": str(t.registered_on) if t.registered_on else None,
                    "is_aiia": t.is_aiia,
                    "is_ayush": t.is_ayush
                } for t in items]

                self.send_json_response({
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "data": data
                })
            finally:
                db.close()
        elif path == "/api/cdisc":
            search = get_param("search", "")
            limit = int(get_param("limit", "50"))
            self.send_json_response(db_service.get_cdisc_terms(search=search, limit=limit))
        elif path == "/api/ctms/overview":
            self.send_json_response(db_service.get_ctms_overview())
        elif path == "/api/ctms/timelines":
            search = get_param("search", "")
            status = get_param("status", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "20"))
            self.send_json_response(db_service.get_ctms_timelines(search=search, status=status, page=page, limit=limit))
        elif path == "/api/ctms/recruitment":
            search = get_param("search", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "20"))
            self.send_json_response(db_service.get_ctms_recruitment(search=search, page=page, limit=limit))
        elif path == "/api/ctms/monitoring":
            status = get_param("status", "")
            search = get_param("search", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "20"))
            self.send_json_response(db_service.get_ctms_monitoring_visits(status=status, search=search, page=page, limit=limit))
        elif path == "/api/ctms/deviations":
            severity = get_param("severity", "")
            status = get_param("status", "")
            category = get_param("category", "")
            search = get_param("search", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "20"))
            self.send_json_response(db_service.get_ctms_protocol_deviations(severity=severity, status=status, category=category, search=search, page=page, limit=limit))
        elif path == "/api/ctms/milestones":
            status = get_param("status", "")
            role = get_param("role", "")
            overdue_only = get_param("overdue_only", "false").lower() in ("true", "1")
            search = get_param("search", "")
            page = int(get_param("page", "1"))
            limit = int(get_param("limit", "25"))
            self.send_json_response(db_service.get_ctms_milestones(status=status, role=role, overdue_only=overdue_only, search=search, page=page, limit=limit))
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
            
            # Fetch up to 2000 records for export
            res = db_service.get_trials(
                scope=scope, search=search, status=status,
                phase=phase, trial_type=trial_type, sponsor=sponsor,
                thesis=thesis, year=year, date_from=date_from, date_to=date_to,
                sort_by=sort_by, sort_dir=sort_dir, page=1, limit=2000
            )
            
            if export_fmt == "json":
                json_bytes = json.dumps(res["data"], ensure_ascii=False, indent=2).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="aiia_trials_export.json"')
                self.send_header("Content-Length", str(len(json_bytes)))
                self.end_headers()
                self.wfile.write(json_bytes)
            else:
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow([
                    "Trial ID", "CTRI Number", "Public Title", "Scientific Title",
                    "Study Type", "Phase", "Recruitment Status", "Sponsor",
                    "Sample Size", "Registration Date", "Last Updated",
                    "Principal Investigator", "Affiliation"
                ])
                for r in res["data"]:
                    writer.writerow([
                        r.get("Trial_ID", ""),
                        r.get("CTRI_Number", ""),
                        r.get("Public_Title", ""),
                        r.get("Scientific_Title", ""),
                        r.get("Type_of_Trial", ""),
                        r.get("Phase", ""),
                        r.get("Recruitment_Status_India", ""),
                        r.get("Sponsor_Name", ""),
                        r.get("Sample_Size_Num") or r.get("Sample_Size_Raw", ""),
                        r.get("Registration_Date_ISO", ""),
                        r.get("Last_Updated_ISO", ""),
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
        else:
            # Fall back to static files
            if path == "/":
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # Check /api/alerts/<id>/status
        if path.startswith("/api/alerts/") and path.endswith("/status"):
            try:
                content_len = int(self.headers.get('Content-Length', 0))
                post_body = self.rfile.read(content_len) if content_len > 0 else b'{}'
                body = json.loads(post_body.decode('utf-8'))
                
                parts = path.strip("/").split("/")
                alert_id = int(parts[2])
                new_status = body.get("status", "Acknowledged")
                user_name = body.get("user", "Dr. Galib (Auditor)")
                
                res = db_service.update_alert_status(alert_id, new_status, user_name)
                self.send_json_response(res)
            except Exception as e:
                self.send_json_response({"error": str(e)}, status=400)
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
    # Allow address reuse
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
