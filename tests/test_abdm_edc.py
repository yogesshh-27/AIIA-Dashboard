import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.abdm_edc_service import (
    verify_abha_id,
    generate_fhir_r4_bundle,
    ingest_edc_payload,
    get_abdm_gateway_status,
)


class TestAbdmEdcService(unittest.TestCase):
    def test_verify_abha_id_valid_14_digit(self):
        res = verify_abha_id("91-1234-5678-9012")
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "ACTIVE")
        self.assertTrue(res["kyc_verified"])
        self.assertEqual(res["abdm_milestone_compliance"]["M1_Identity"], "VERIFIED")

    def test_verify_abha_id_valid_phr(self):
        res = verify_abha_id("vaidya.ayush@abdm")
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "ACTIVE")

    def test_verify_abha_id_invalid(self):
        res = verify_abha_id("invalid-abha")
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "INVALID_FORMAT")

    def test_generate_fhir_r4_bundle(self):
        bundle = generate_fhir_r4_bundle()
        self.assertEqual(bundle["resourceType"], "Bundle")
        self.assertEqual(bundle["type"], "collection")
        entries = bundle.get("entry", [])
        self.assertGreaterEqual(len(entries), 4)

        resource_types = [e["resource"]["resourceType"] for e in entries]
        self.assertIn("ResearchStudy", resource_types)
        self.assertIn("Patient", resource_types)
        self.assertIn("ResearchSubject", resource_types)
        self.assertIn("Condition", resource_types)
        self.assertIn("MedicationStatement", resource_types)

    def test_ingest_edc_payload(self):
        payload = {
            "source_system": "OpenClinica",
            "study_id": "CTRI/2017/12/010899",
            "subject_id": "SUBJ-101",
            "event_type": "VISIT_BASELINE",
            "data": [{"param": "VAS_SCORE", "value": 65}]
        }
        res = ingest_edc_payload("OpenClinica", payload)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "STAGED_AND_AUDITED")
        self.assertTrue(res["alcoa_compliant_entry"])
        self.assertIn("ingest_id", res)

    def test_abdm_gateway_status(self):
        status = get_abdm_gateway_status()
        self.assertIn("milestones", status)
        self.assertEqual(status["milestones"]["M1_Identity"]["status"], "Operational")
        self.assertIn("supported_edc_systems", status)


if __name__ == "__main__":
    unittest.main()
