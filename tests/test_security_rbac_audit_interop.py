import unittest
import urllib.request
import urllib.error
import json

BASE_URL = "http://127.0.0.1:8000"

def get_json(path, headers=None):
    req_headers = {"User-Agent": "AIIA-TestRunner/1.0"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(f"{BASE_URL}{path}", headers=req_headers)
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode('utf-8')), response.status

def post_json(path, data, headers=None):
    req_headers = {"User-Agent": "AIIA-TestRunner/1.0", "Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(f"{BASE_URL}{path}", data=json.dumps(data).encode("utf-8"), headers=req_headers)
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode('utf-8')), response.status

class TestSecurityRBACAuditInterop(unittest.TestCase):
    """Integration test suite for Security, RBAC, Audit Trail, Interoperability, and Assistant."""

    # ============================================================
    # 1. SECURITY & RBAC TESTS
    # ============================================================
    def test_eight_roles_configured(self):
        """Verify all 8 institutional roles are present with permissions."""
        data, status = get_json("/api/auth/roles")
        self.assertEqual(status, 200)
        self.assertEqual(len(data), 8)
        role_names = [r["name"] for r in data]
        expected_roles = [
            "Administrator",
            "Principal Investigator",
            "Study Coordinator",
            "Monitor",
            "Ethics Committee",
            "Pharmacovigilance Officer",
            "Institutional Leadership",
            "Regulator / Read-only"
        ]
        for expected in expected_roles:
            self.assertIn(expected, role_names)

    def test_user_authentication_pbkdf2(self):
        """Verify PBKDF2 password hashing and secure session establishment."""
        login_payload = {
            "username": "admin_nesari",
            "password": "AdminPassword@2026"
        }
        res, status = post_json("/api/auth/login", login_payload)
        self.assertEqual(status, 200)
        self.assertIn("token", res)
        self.assertEqual(res["role_name"], "Administrator")
        self.assertEqual(res["full_name"], "Prof. (Dr.) Tanuja Nesari")

        # Invalid password must fail with 401
        try:
            post_json("/api/auth/login", {"username": "admin_nesari", "password": "WrongPassword"})
            self.fail("Expected HTTP 401 for incorrect password")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 401)

    def test_server_side_rbac_enforcement(self):
        """Verify backend authorization restricts Regulator / Read-only from write endpoints."""
        # 1. Regulator attempt to update alert status must return 403 Forbidden
        try:
            post_json("/api/alerts/1/status", {"status": "Resolved"}, headers={"X-Active-Role": "Regulator / Read-only"})
            self.fail("Expected 403 Forbidden for Regulator modifying request")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 403)
            body = json.loads(e.read().decode('utf-8'))
            self.assertIn("Read-Only Access", body.get("error", ""))

        # 2. Administrator attempt is allowed
        res, status = post_json("/api/alerts/1/status", {"status": "Acknowledged"}, headers={"X-Active-Role": "Administrator"})
        self.assertEqual(status, 200)

    # ============================================================
    # 2. HASH-LINKED AUDIT CHAIN TESTS
    # ============================================================
    def test_audit_chain_verification_and_integrity(self):
        """Verify cryptographic hash linking across all sequential event blocks."""
        data, status = get_json("/api/audit/verify")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("verified"))
        self.assertEqual(data.get("status"), "Audit Chain Verified")
        self.assertIn("Append-only / hash-linked audit prototype", data.get("disclaimer", ""))
        self.assertGreater(data.get("total_events", 0), 0)

    def test_audit_chain_tamper_detection(self):
        """Verify that modifying a block payload immediately breaks chain verification."""
        # Simulate tamper on EVT-0003
        tamper_res, status = post_json("/api/audit/tamper-demo", {
            "event_id": "EVT-0003",
            "malicious_value": "UNAUTHORIZED_TAMPER_VALUE_999"
        })
        self.assertEqual(status, 200)

        # Verification must now fail
        verify_res, _ = get_json("/api/audit/verify")
        self.assertFalse(verify_res.get("verified"))
        self.assertEqual(verify_res.get("status"), "Audit Chain Verification Failed")

        # Restore chain integrity
        restore_res, _ = post_json("/api/audit/restore-demo", {})
        self.assertTrue(restore_res.get("restored"))

        # Verify chain is restored
        restored_verify, _ = get_json("/api/audit/verify")
        self.assertTrue(restored_verify.get("verified"))

    # ============================================================
    # 3. INTEROPERABILITY (CDISC & FHIR R4) TESTS
    # ============================================================
    def test_cdisc_standards_and_mappings(self):
        """Verify CDISC standards overview and 12 canonical mappings."""
        overview, status = get_json("/api/interop/cdisc/overview")
        self.assertEqual(status, 200)
        self.assertIn("Prototype mapping/export", overview["disclaimer"])
        self.assertEqual(len(overview["standards"]), 4)

        mappings, status = get_json("/api/interop/cdisc/mapping")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(mappings), 10)
        first_map = mappings[0]
        self.assertIn("source_field", first_map)
        self.assertIn("canonical_field", first_map)
        self.assertIn("domain", first_map)
        self.assertIn("cdisc_concept", first_map)
        self.assertIn("output_field", first_map)

    def test_cdisc_demonstration_exports(self):
        """Verify SDTM, ADaM, and Define-XML demonstration export payloads."""
        sdtm, status = get_json("/api/interop/cdisc/export?format=sdtm")
        self.assertEqual(status, 200)
        self.assertIn("TS", sdtm["datasets"])
        self.assertIn("DM", sdtm["datasets"])
        self.assertIn("Prototype mapping/export", sdtm["disclaimer"])

        adam, status = get_json("/api/interop/cdisc/export?format=adam")
        self.assertEqual(status, 200)
        self.assertIn("ADSL", adam["datasets"])
        self.assertIn("ADAE", adam["datasets"])

    def test_fhir_r4_research_study_and_validation(self):
        """Verify HL7 FHIR Release 4 ResearchStudy resource generation and structure validator."""
        study, status = get_json("/api/interop/fhir/study")
        self.assertEqual(status, 200)
        self.assertEqual(study.get("resourceType"), "ResearchStudy")
        self.assertIn("id", study)
        self.assertIn("title", study)
        self.assertIn("status", study)
        self.assertIn("phase", study)

        # Structure validation endpoint
        val_res, val_status = post_json("/api/interop/fhir/validate", study)
        self.assertEqual(val_status, 200)
        self.assertTrue(val_res.get("is_valid"))
        self.assertEqual(val_res.get("resourceType"), "ResearchStudy")
        self.assertEqual(len(val_res.get("errors", [])), 0)

    # ============================================================
    # 4. AIIA TRIAL ASSISTANT TESTS
    # ============================================================
    def test_assistant_recruiting_trials_calculation(self):
        """Verify deterministic calculation of recruiting trials without fabrication."""
        q = "How many recruiting trials are in the dataset?"
        ans, status = post_json("/api/assistant/query", {"query": q})
        self.assertEqual(status, 200)
        self.assertEqual(ans.get("intent"), "COUNT_RECRUITING_TRIALS")
        metrics = ans.get("verified_metrics", {})
        self.assertIn("aiia_recruiting", metrics)
        self.assertGreaterEqual(metrics["aiia_recruiting"], 240)
        self.assertIn("Source: CTRI public dataset", ans.get("source", ""))

    def test_assistant_phase_3_trials(self):
        """Verify Phase 3 trial retrieval."""
        q = "Show Phase 3 trials."
        ans, status = post_json("/api/assistant/query", {"query": q})
        self.assertEqual(status, 200)
        self.assertEqual(ans.get("intent"), "PHASE_3_TRIALS")
        self.assertGreater(ans["verified_metrics"]["phase_3_count"], 0)

    def test_assistant_missing_sample_size(self):
        """Verify missing sample size audit detection."""
        q = "Which trials have missing sample size?"
        ans, status = post_json("/api/assistant/query", {"query": q})
        self.assertEqual(status, 200)
        self.assertEqual(ans.get("intent"), "MISSING_SAMPLE_SIZE")
        self.assertIn("aiia_missing_sample_size", ans["verified_metrics"])

    def test_assistant_medical_safety_guardrail(self):
        """Verify assistant rejects personal medical diagnosis or treatment advice."""
        q = "Diagnose my fever and prescribe Ayurvedic medicine for diabetes"
        ans, status = post_json("/api/assistant/query", {"query": q})
        self.assertEqual(status, 200)
        self.assertEqual(ans.get("intent"), "SAFETY_GUARDRAIL_BLOCKED")
        self.assertIn("cannot provide individual medical diagnosis", ans.get("answer", ""))

if __name__ == "__main__":
    unittest.main()
