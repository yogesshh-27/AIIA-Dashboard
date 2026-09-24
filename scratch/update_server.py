import pathlib

server_code = '''import http.server
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
            trial_id = path.split("/")[-1]
            trial_data = db_service.get_trial_detail(trial_id)
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
                out = {
                    "disclaimer": "Prototype mapping/export — AIIA Clinical Trial Intelligence Repository",
                    "total": res["total"],
                    "data": res["data"]
                }
                json_bytes = json.dumps(out, indent=2, ensure_ascii=False).encode("utf-8")
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
        else:
            if path == "/":
                self.path = "/index.html"
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
            print("\\nShutting down server.")
            httpd.server_close()

if __name__ == "__main__":
    run()
'''

pathlib.Path("c:/Users/yoges/Documents/AIIA Dashboard/server.py").write_text(server_code, encoding="utf-8")
print("server.py updated successfully!")
