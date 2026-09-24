import pathlib

script_content = '''
import re

server_path = "c:/Users/yoges/Documents/AIIA Dashboard/server.py"
with open(server_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Insert GET routes for documents and reports right after /api/interop/fhir/study
get_routes = """        elif path == "/api/interop/fhir/study":
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
        elif path == "/api/reports/data":
            rep_type = get_param("type", "portfolio").lower()
            if rep_type == "portfolio":
                self.send_json_response(db_service.get_report_portfolio())
            elif rep_type == "recruitment":
                self.send_json_response(db_service.get_report_recruitment())
            elif rep_type == "compliance":
                self.send_json_response(db_service.get_report_compliance())
            elif rep_type == "safety":
                self.send_json_response(db_service.get_report_safety())
            elif rep_type == "data_quality":
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
                return"""

content = content.replace('''        elif path == "/api/interop/fhir/study":
            trial_id = get_param("trial_id", None)
            self.send_json_response(db_service.get_fhir_research_study(trial_id=trial_id))''', get_routes)

# 2. Add POST routes for Document Upload and Document Versioning
post_routes = """        # 7. DOCUMENT UPLOAD & VERSIONING
        elif path == "/api/documents/upload":
            if not self.require_permission("documents:upload"):
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
            file_content_raw = body.get("file_content", f"Institutional Record: {doc_name}\\nCategory: {category}\\nVersion: {version}\\n")
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
            if not self.require_permission("documents:upload"):
                return
            parts = path.split("/")
            doc_id_str = parts[3]
            auth = self.get_auth_context()
            version = body.get("version", "v1.1")
            change_summary = body.get("change_summary", "Routine periodic version update.")
            uploaded_by = auth.get("user_name", "Principal Investigator")
            status = body.get("status", "Approved")
            file_name = body.get("file_name", f"Document_Update_{version}.pdf")
            file_content_raw = body.get("file_content", f"Updated Document Version: {version}\\nSummary: {change_summary}\\n")
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
"""

content = content.replace('''        # 6. FHIR R4 STRUCTURE VALIDATION
        elif path == "/api/interop/fhir/validate":
            resource = body.get("resource", {})
            self.send_json_response(db_service.validate_fhir_research_study(resource))
            return''', '''        # 6. FHIR R4 STRUCTURE VALIDATION
        elif path == "/api/interop/fhir/validate":
            resource = body.get("resource", {})
            self.send_json_response(db_service.validate_fhir_research_study(resource))
            return

''' + post_routes)

with open(server_path, "w", encoding="utf-8") as f:
    f.write(content)

print("server.py updated with Documents and Reports endpoints successfully!")
'''

with open("c:/Users/yoges/Documents/AIIA Dashboard/scratch/update_server_docs_reports.py", "w", encoding="utf-8") as f:
    f.write(script_content)
print("update_server_docs_reports.py written.")
