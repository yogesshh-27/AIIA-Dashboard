"""
Unit & Integration Tests for AYURCTMS v3.0 REST Endpoints
Using FastAPI TestClient for in-process, non-blocking execution.
"""

import unittest
from fastapi.testclient import TestClient
from app_fastapi import app


class TestV3API(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # 1. ALCOA+ Endpoints
    def test_alcoa_metrics_endpoint(self):
        res = self.client.get("/api/compliance/alcoa/metrics?scope=aiia")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("overall_alcoa_score", data)
        self.assertIn("principles", data)
        self.assertEqual(len(data["principles"]), 9)

    def test_alcoa_certificate_endpoint(self):
        res = self.client.get("/api/compliance/alcoa/certificate/CTRI-2017-12-010899")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("certificate_id", data)
        self.assertIn("digital_fingerprint_sha256", data)

    # 2. ABDM & EDC Endpoints
    def test_abdm_verify_abha(self):
        res = self.client.post("/api/interop/abdm/verify-abha", json={"abha_id": "91-1234-5678-9012"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["status"], "ACTIVE")

    def test_abdm_status(self):
        res = self.client.get("/api/interop/abdm/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("milestones", data)

    def test_fhir_bundle(self):
        res = self.client.get("/api/interop/fhir/bundle")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["resourceType"], "Bundle")
        self.assertGreaterEqual(len(data["entry"]), 4)

    def test_edc_ingest(self):
        payload = {
            "source_system": "REDCap",
            "trial_id": "CTRI/2017/12/010899",
            "subject_id": "SUBJ-555",
            "event_type": "FOLLOWUP_M1",
            "records": [{"metric": "VAS", "score": 22}]
        }
        res = self.client.post("/api/interop/edc/ingest", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["status"], "STAGED_AND_AUDITED")

    # 3. MedDRA & Regulatory Timelines
    def test_meddra_search(self):
        res = self.client.get("/api/pv/meddra/search?query=Dyspepsia")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]["pt"], "Dyspepsia")

    def test_regulatory_timelines(self):
        res = self.client.get("/api/pv/regulatory/timelines")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)

    def test_e2b_export(self):
        res = self.client.get("/api/pv/export/e2b/EVT-0042")
        self.assertEqual(res.status_code, 200)
        self.assertIn("application/xml", res.headers.get("content-type", ""))
        self.assertIn("<ichicsr", res.text)

    # 4. DPDP Privacy & Consent
    def test_dpdp_notice(self):
        res = self.client.get("/api/privacy/notice?language=en")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["language"], "en")
        self.assertIn("specified_purposes", data)

    def test_dpdp_consent_lifecycle(self):
        record_res = self.client.post("/api/privacy/consent/record", json={
            "trial_id": "CTRI/2017/12/010899",
            "subject_id": "SUBJ-API-01",
            "language": "en"
        })
        self.assertEqual(record_res.status_code, 200)
        c_id = record_res.json()["consent"]["consent_id"]

        withdraw_res = self.client.post("/api/privacy/consent/withdraw", json={
            "consent_id": c_id,
            "reason": "Test revocation"
        })
        self.assertEqual(withdraw_res.status_code, 200)
        self.assertEqual(withdraw_res.json()["status"], "WITHDRAWN")

    def test_dpdp_dpo_audit_log(self):
        res = self.client.get("/api/privacy/dpo/audit-log")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["dpo_compliance_status"], "FULLY_COMPLIANT")

    # 5. CDISC Submission Datasets
    def test_cdisc_sdtm_domain(self):
        res = self.client.get("/api/interop/cdisc/sdtm/DM")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["domain"], "DM")
        self.assertGreaterEqual(data["record_count"], 1)

    def test_cdisc_adam_dataset(self):
        res = self.client.get("/api/interop/cdisc/adam/ADSL")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["dataset_name"], "ADSL")

    def test_cdisc_define_xml_2(self):
        res = self.client.get("/api/interop/cdisc/define-xml-2")
        self.assertEqual(res.status_code, 200)
        self.assertIn("application/xml", res.headers.get("content-type", ""))
        self.assertIn("<ODM", res.text)
        self.assertIn("define2-0-0.xsl", res.text)


if __name__ == "__main__":
    unittest.main()
