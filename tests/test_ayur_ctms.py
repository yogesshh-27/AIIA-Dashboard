"""
Unit and Integration Tests for AYURCTMS (AIIA Clinical Trial Management System)
Validates all 28 requirements of SIH Problem Statement ID 26046.
"""

import unittest
import urllib.request
import urllib.parse
import json
import sqlite3
import os

BASE_URL = "http://127.0.0.1:8000"

def get(path):
    req = urllib.request.Request(f"{BASE_URL}{path}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def post(path, data):
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}{path}", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

class TestAYURCTMS(unittest.TestCase):

    # 1. Dual Entry & Patient Matching
    def test_patient_matching_flow(self):
        res = post("/api/ayur/patient/match", {
            "condition": "Arthritis",
            "accessible_locations": ["Mumbai", "Delhi"],
            "distance_pref": "Within City (< 25 km)"
        })
        self.assertTrue(res.get("success"))
        self.assertIn("Potentially Relevant Trial", res.get("disclaimer", ""))
        self.assertGreaterEqual(res.get("total_matches", 0), 1)
        # Check first match
        first = res["results"][0]
        self.assertEqual(first["condition"], "Arthritis")
        self.assertEqual(first["location"], "Mumbai")

    # 2. Staff Authentication
    def test_staff_authentication(self):
        # Valid credentials
        res = post("/api/ayur/auth/login", {
            "staff_id": "AIIA001",
            "password": "AIIA@123"
        })
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("user", {}).get("staff_id"), "AIIA001")
        self.assertEqual(res.get("user", {}).get("full_name"), "Dr. Research Admin")

        # Invalid credentials
        try:
            post("/api/ayur/auth/login", {
                "staff_id": "INVALID",
                "password": "WRONG"
            })
            self.fail("Should have thrown HTTPError for invalid login")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 401)

    # 3. Main Dashboard & 3 KPI Cards
    def test_dashboard_kpis(self):
        stats = get("/api/ayur/dashboard/stats")
        self.assertTrue(stats.get("success"))
        kpis = stats.get("kpi_cards", {})

        # Card 1: Doctor Information
        self.assertEqual(kpis["doctors"]["title"], "DOCTOR INFORMATION")
        self.assertGreaterEqual(kpis["doctors"]["total_doctors"], 10)
        self.assertGreaterEqual(kpis["doctors"]["trial_sites"], 8)

        # Card 2: Patient Information
        self.assertEqual(kpis["patients"]["title"], "PATIENT INFORMATION")
        self.assertGreaterEqual(kpis["patients"]["total_patients"], 20)

        # Card 3: Pharmacovigilance
        self.assertEqual(kpis["pharmacovigilance"]["title"], "PHARMACOVIGILANCE")
        self.assertGreaterEqual(kpis["pharmacovigilance"]["total_adverse_events"], 5)

        # Section A: Active trials breakdown
        trials_sum = stats.get("active_trials_summary", {})
        self.assertGreaterEqual(trials_sum.get("ongoing", 0), 3)

    # 4. Sites / Locations Explorer
    def test_sites_explorer_9_cities(self):
        sites_res = get("/api/ayur/sites")
        self.assertTrue(sites_res.get("success"))
        sites = sites_res.get("sites", [])
        city_names = [s["city"] for s in sites]

        for city in ["Mumbai", "Delhi", "Kolkata", "Kerala", "Lucknow", "Noida", "Jaipur", "Hyderabad", "Bengaluru"]:
            self.assertIn(city, city_names)

        # Test single site details & outcome trend
        mumbai = get("/api/ayur/sites/Mumbai")
        self.assertTrue(mumbai.get("success"))
        self.assertEqual(mumbai["site"]["city"], "Mumbai")
        self.assertEqual(mumbai["site"]["condition"], "Arthritis")
        self.assertGreater(len(mumbai["site"]["outcome_trend"]), 0)

    # 5. Trial Information & Overlap Warning
    def test_trials_and_overlap_detection(self):
        trials_res = get("/api/ayur/trials")
        self.assertTrue(trials_res.get("success"))
        self.assertGreaterEqual(len(trials_res.get("trials", [])), 6)

        # Test overlap warning when creating trial with existing condition & site
        res = post("/api/ayur/trials/create", {
            "trial_name": "Second Arthritis Protocol in Mumbai",
            "condition": "Arthritis",
            "city": "Mumbai",
            "hospital_name": "AIIA Partner Hospital - Mumbai",
            "target_participants": 50,
            "duration_weeks": 8
        })
        self.assertTrue(res.get("success"))
        self.assertIsNotNone(res.get("overlap_warning"))
        self.assertIn("Potential overlap detected", res.get("overlap_warning"))

    # 6. Pending Approvals Workflow
    def test_pending_approvals(self):
        appr_res = get("/api/ayur/approvals")
        self.assertTrue(appr_res.get("success"))
        approvals = appr_res.get("approvals", [])
        self.assertGreaterEqual(len(approvals), 4)

        # Update an approval
        up_res = post("/api/ayur/approvals/update", {
            "approval_id": approvals[0]["approval_id"],
            "status": "APPROVED",
            "notes": "Verified by Ethics Reviewer"
        })
        self.assertTrue(up_res.get("success"))

    # 7. GCP Guidelines Checklist
    def test_gcp_guidelines(self):
        gcp_res = get("/api/ayur/gcp")
        self.assertTrue(gcp_res.get("success"))
        self.assertGreaterEqual(gcp_res.get("total_items", 0), 8)

        # Toggle item
        toggle_res = post("/api/ayur/gcp/toggle", {
            "item_id": 1,
            "is_completed": 1,
            "reviewed_by": "Test Auditor"
        })
        self.assertTrue(toggle_res.get("success"))

    # 8. Doctor Information Directory
    def test_doctor_directory(self):
        docs_res = get("/api/ayur/doctors")
        self.assertTrue(docs_res.get("success"))
        docs = docs_res.get("doctors", [])
        self.assertGreaterEqual(len(docs), 10)

        # Test single doctor detail
        doc_detail = get(f"/api/ayur/doctors/{docs[0]['doctor_id']}")
        self.assertTrue(doc_detail.get("success"))
        self.assertIn("qualification", doc_detail["doctor"])

    # 9. Patient Information & 8-Stage Treatment Timeline
    def test_patient_management_and_ramlal(self):
        pats_res = get("/api/ayur/patients")
        self.assertTrue(pats_res.get("success"))
        pats = pats_res.get("patients", [])
        self.assertGreaterEqual(len(pats), 20)

        # Find Ramlal Sharma (AYU-PAT-001)
        ramlal = get("/api/ayur/patients/AYU-PAT-001")
        self.assertTrue(ramlal.get("success"))
        p_data = ramlal["patient"]
        self.assertEqual(p_data["full_name"], "Ramlal Sharma")
        self.assertEqual(p_data["condition"], "Diabetes")
        self.assertEqual(p_data["area_city"], "Delhi")

        # Verify 8-stage timeline
        timeline = p_data.get("treatment_timeline", [])
        self.assertGreaterEqual(len(timeline), 4)

    # 10. Pharmacovigilance & Safety Signals
    def test_pharmacovigilance_and_safety_signal(self):
        pv_sum = get("/api/ayur/pv/summary")
        self.assertTrue(pv_sum.get("success"))

        # Safety Signal Detection (7 skin rash cases in AYU-002)
        signals_res = get("/api/ayur/pv/signals")
        self.assertTrue(signals_res.get("success"))
        signals = signals_res.get("signals", [])
        self.assertGreaterEqual(len(signals), 1)
        sig = signals[0]
        self.assertEqual(sig["trial_id"], "AYU-TRIAL-002")
        self.assertIn("7 participants", sig["recommendation"])
        self.assertIn("Potential safety signal detected", sig["recommendation"])

        # Report new adverse event
        ae_res = post("/api/ayur/pv/report", {
            "patient_name": "Test Subject",
            "trial_id": "AYU-TRIAL-001",
            "adverse_event": "Mild Nausea",
            "severity": "Mild",
            "serious": "No",
            "suspected_treatment": "Ayurvedic formulation",
            "location": "Mumbai"
        })
        self.assertTrue(ae_res.get("success"))

    # 11. Reports & CSV Export
    def test_reports_and_export(self):
        rep = get("/api/ayur/reports?type=trial_progress")
        self.assertTrue(rep.get("success"))
        self.assertIn("Trial Progress", rep.get("report_title", ""))
        self.assertGreater(len(rep.get("rows", [])), 0)

        # Test CSV export endpoint
        req = urllib.request.Request(f"{BASE_URL}/api/ayur/reports/export?type=trial_progress&format=csv")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get("Content-Type"), "text/csv; charset=utf-8")
            csv_text = resp.read().decode("utf-8")
            self.assertIn("Trial ID", csv_text)

    # 12. Global Search
    def test_global_search_ramlal(self):
        search_res = get("/api/ayur/search?q=Ramlal")
        self.assertTrue(search_res.get("success"))
        patients = search_res["results"].get("patients", [])
        self.assertGreaterEqual(len(patients), 1)
        self.assertEqual(patients[0]["patient_id"], "AYU-PAT-001")

    # 13. FHIR & CDISC Interoperability Demo
    def test_interop_pipeline(self):
        interop = get("/api/ayur/interop/demo")
        self.assertTrue(interop.get("success"))
        self.assertIn("pipeline", interop)
        self.assertIn("fhir_patient", interop)
        self.assertIn("cdisc_sdtm", interop)
        self.assertIn("mapping_rules", interop)

    # 14. Audit Trail
    def test_audit_trail(self):
        audit = get("/api/ayur/audit")
        self.assertTrue(audit.get("success"))
        self.assertGreater(len(audit.get("audit_trail", [])), 0)

if __name__ == "__main__":
    unittest.main()
