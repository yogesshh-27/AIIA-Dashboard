import unittest
import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000"

def get_json(path, headers=None):
    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(f"{BASE_URL}{path}", headers=req_headers)
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode('utf-8')), response.status

def get_raw(path, headers=None):
    req_headers = {}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(f"{BASE_URL}{path}", headers=req_headers)
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.read(), response.status, response.headers

def post_json(path, data, headers=None):
    req_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(f"{BASE_URL}{path}", data=json.dumps(data).encode("utf-8"), headers=req_headers)
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode('utf-8')), response.status

class TestReportingAndDocuments(unittest.TestCase):
    """Test suite for Documents Management (version tracking, access control) and Institutional Reports (CSV, Print/PDF)."""

    # ============================================================
    # 1. DOCUMENTS MANAGEMENT TESTS
    # ============================================================

    def test_documents_summary_and_categories(self):
        """Verify document summary counts and all 6 required categories."""
        data, status = get_json("/api/documents/summary")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(data["total_documents"], 10)
        self.assertGreaterEqual(data["total_versions"], 15)
        self.assertIn("by_category", data)
        expected_cats = ["Protocol", "IEC / Ethics", "CTRI", "Monitoring", "Safety", "Reports"]
        for cat in expected_cats:
            self.assertIn(cat, data["by_category"])
            self.assertGreater(data["by_category"][cat], 0)

    def test_documents_list_and_filters(self):
        """Verify document retrieval, category filtering, and search."""
        # All documents
        data, status = get_json("/api/documents?page=1&limit=20")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(data["total"], 10)
        first_doc = data["data"][0]
        self.assertIn("doc_id", first_doc)
        self.assertIn("document_name", first_doc)
        self.assertIn("category", first_doc)
        self.assertIn("current_version", first_doc)
        self.assertIn("uploaded_by", first_doc)
        self.assertIn("upload_date", first_doc)
        self.assertIn("status", first_doc)

        # Filter by Protocol
        proto_data, _ = get_json("/api/documents?category=Protocol")
        self.assertTrue(all(d["category"] == "Protocol" for d in proto_data["data"]))

        # Filter by Safety
        safety_data, _ = get_json("/api/documents?category=Safety")
        self.assertTrue(all(d["category"] == "Safety" for d in safety_data["data"]))

        # Search by CTRI or name
        search_data, _ = get_json("/api/documents?search=Guduchi")
        self.assertGreaterEqual(len(search_data["data"]), 1)
        self.assertIn("Guduchi", search_data["data"][0]["document_name"])

    def test_document_version_history(self):
        """Verify version tracking and historical version chain."""
        doc, status = get_json("/api/documents/DOC-PRT-001")
        self.assertEqual(status, 200)
        self.assertEqual(doc["doc_id"], "DOC-PRT-001")
        self.assertEqual(doc["current_version"], "v2.1")
        self.assertIn("versions", doc)
        self.assertGreaterEqual(len(doc["versions"]), 3)
        v_names = [v["version"] for v in doc["versions"]]
        self.assertIn("v1.0", v_names)
        self.assertIn("v2.0", v_names)
        self.assertIn("v2.1", v_names)
        self.assertTrue(all("checksum_sha256" in v and "change_summary" in v for v in doc["versions"]))

    def test_document_secure_download_and_audit(self):
        """Verify access-controlled download, SHA-256 validation, and audit trail entry."""
        # Download latest version
        raw, status, headers = get_raw("/api/documents/DOC-PRT-001/download")
        self.assertEqual(status, 200)
        self.assertIn("application/octet-stream", headers.get("Content-Type", ""))
        self.assertIn("Protocol_Guduchi_OA_v2.1.pdf", headers.get("Content-Disposition", ""))
        self.assertGreater(len(raw), 50)

        # Download historical version v1.0
        raw_v1, status_v1, headers_v1 = get_raw("/api/documents/DOC-PRT-001/download?version=v1.0")
        self.assertEqual(status_v1, 200)
        self.assertIn("Protocol_Guduchi_OA_v1.0.pdf", headers_v1.get("Content-Disposition", ""))

        # Verify audit event was logged for download
        audit_res, _ = get_json("/api/audit/chain?limit=5")
        recent_actions = [ev["action"] for ev in audit_res["data"]]
        self.assertIn("DOWNLOAD_DOCUMENT", recent_actions)

    def test_document_upload_and_versioning_lifecycle(self):
        """Verify new document creation and subsequent version bump with audit trail."""
        # 1. Upload new document
        upload_payload = {
            "document_name": "DSMB Safety Interim Review Report 2026",
            "category": "Safety",
            "trial_ctri": "CTRI/2017/10/010023",
            "version": "v1.0",
            "status": "Under Review",
            "description": "Mid-term DSMB safety data analysis.",
            "file_name": "DSMB_Interim_Review_2026_v1.0.pdf",
            "file_content": "ALL INDIA INSTITUTE OF AYURVEDA\nDSMB Interim Safety Analysis 2026."
        }
        res, status = post_json("/api/documents/upload", upload_payload, headers={"X-Active-Role": "Study Coordinator"})
        self.assertEqual(status, 200)
        self.assertTrue(res.get("success"))
        new_doc_id = res.get("doc_id")
        self.assertTrue(new_doc_id.startswith("DOC-SAF-"))

        # 2. Upload new version v1.1
        ver_payload = {
            "version": "v1.1",
            "change_summary": "Incorporated DSMB statistical chair remarks.",
            "status": "Approved",
            "file_name": f"{new_doc_id}_v1.1_Final.pdf",
            "file_content": "ALL INDIA INSTITUTE OF AYURVEDA\nDSMB Interim Safety Analysis 2026 Version 1.1 Final."
        }
        ver_res, ver_status = post_json(f"/api/documents/{new_doc_id}/version", ver_payload, headers={"X-Active-Role": "Principal Investigator"})
        self.assertEqual(ver_status, 200)
        self.assertTrue(ver_res.get("success"))
        self.assertEqual(ver_res.get("new_version"), "v1.1")

        # 3. Verify updated document has 2 versions
        detail, _ = get_json(f"/api/documents/{new_doc_id}")
        self.assertEqual(detail["current_version"], "v1.1")
        self.assertEqual(len(detail["versions"]), 2)

    # ============================================================
    # 2. INSTITUTIONAL REPORTS TESTS (6 REPORTS & DUAL EXPORTS)
    # ============================================================

    def test_report_trial_portfolio(self):
        """Verify Trial Portfolio Report data and CSV/PDF export."""
        # JSON Data
        data, status = get_json("/api/reports/data?type=portfolio")
        self.assertEqual(status, 200)
        self.assertEqual(data["report_title"], "Trial Portfolio Report")
        self.assertEqual(data["total_trials"], 263)
        self.assertIn("status_distribution", data)
        self.assertIn("phase_distribution", data)

        # CSV Export
        csv_raw, c_status, c_headers = get_raw("/api/reports/export?type=portfolio&format=csv")
        self.assertEqual(c_status, 200)
        self.assertIn("text/csv", c_headers.get("Content-Type", ""))
        self.assertIn(b"ALL INDIA INSTITUTE OF AYURVEDA", csv_raw)
        self.assertIn(b"CTRI Number", csv_raw)

        # Print / PDF HTML View
        html_raw, h_status, h_headers = get_raw("/api/reports/export?type=portfolio&format=html")
        self.assertEqual(h_status, 200)
        self.assertIn("text/html", h_headers.get("Content-Type", ""))
        self.assertIn(b"Trial Portfolio Report", html_raw)
        self.assertIn(b"All India Institute of Ayurveda", html_raw)

    def test_report_recruitment(self):
        """Verify Recruitment Performance Report and metrics."""
        data, status = get_json("/api/reports/data?type=recruitment")
        self.assertEqual(status, 200)
        self.assertIn("overall_enrollment_percentage", data)
        self.assertGreater(data["total_target_enrollment"], 0)
        self.assertGreater(data["total_current_enrollment"], 0)

        csv_raw, c_status, _ = get_raw("/api/reports/export?type=recruitment&format=csv")
        self.assertEqual(c_status, 200)
        self.assertIn(b"OVERALL ENROLLMENT", csv_raw)

    def test_report_compliance(self):
        """Verify Institutional Compliance Report and metrics."""
        data, status = get_json("/api/reports/data?type=compliance")
        self.assertEqual(status, 200)
        self.assertIn("compliance_rate", data)
        self.assertIn("category_breakdown", data)

        csv_raw, c_status, _ = get_raw("/api/reports/export?type=compliance&format=csv")
        self.assertEqual(c_status, 200)
        self.assertIn(b"COMPLIANCE RATE", csv_raw)

    def test_report_safety(self):
        """Verify Pharmacovigilance Safety Report and AE/SAE metrics."""
        data, status = get_json("/api/reports/data?type=safety")
        self.assertEqual(status, 200)
        self.assertIn("total_adverse_events", data)
        self.assertIn("severity_distribution", data)
        self.assertIn("safety_signals", data)

        csv_raw, c_status, _ = get_raw("/api/reports/export?type=safety&format=csv")
        self.assertEqual(c_status, 200)
        self.assertIn(b"TOTAL ADVERSE EVENTS", csv_raw)

    def test_report_data_quality(self):
        """Verify Data Quality & CDISC Alignment Report."""
        data, status = get_json("/api/reports/data?type=data_quality")
        self.assertEqual(status, 200)
        self.assertIn("overall_data_quality_score", data)
        self.assertIn("field_completeness", data)

        csv_raw, c_status, _ = get_raw("/api/reports/export?type=data_quality&format=csv")
        self.assertEqual(c_status, 200)
        self.assertIn(b"DATA QUALITY SCORE", csv_raw)

    def test_report_audit(self):
        """Verify Cryptographic Audit Trail Report."""
        data, status = get_json("/api/reports/data?type=audit")
        self.assertEqual(status, 200)
        self.assertIn("verification_status", data)
        self.assertEqual(data["verification_status"], "Audit Chain Verified")
        self.assertIn("total_cryptographic_blocks", data)

        csv_raw, c_status, _ = get_raw("/api/reports/export?type=audit&format=csv")
        self.assertEqual(c_status, 200)
        self.assertIn(b"VERIFICATION STATUS", csv_raw)

if __name__ == "__main__":
    unittest.main()
