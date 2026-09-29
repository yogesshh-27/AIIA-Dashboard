import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.alcoa_engine import evaluate_alcoa_principles, generate_alcoa_certificate


class TestALCOAEngine(unittest.TestCase):
    def test_evaluate_alcoa_principles_aiia(self):
        result = evaluate_alcoa_principles(scope="aiia")
        self.assertTrue(result.get("success"))
        self.assertIn("overall_alcoa_score", result)
        self.assertGreaterEqual(result["overall_alcoa_score"], 0.0)
        self.assertLessEqual(result["overall_alcoa_score"], 100.0)
        self.assertIn(result["compliance_status"], ["COMPLIANT", "SUBSTANTIAL", "REMEDIATION_REQUIRED"])

        principles = result.get("principles", [])
        self.assertEqual(len(principles), 9)

        expected_codes = {"ATTR", "LEGB", "CONT", "ORIG", "ACCU", "COMP", "CONS", "ENDU", "AVAL"}
        found_codes = {p["code"] for p in principles}
        self.assertEqual(expected_codes, found_codes)

        for p in principles:
            self.assertIn("score", p)
            self.assertIn("status", p)
            self.assertIn("description", p)

    def test_generate_alcoa_certificate(self):
        cert = generate_alcoa_certificate("CTRI/2017/12/010899")
        self.assertIn("certificate_id", cert)
        self.assertTrue(cert["certificate_id"].startswith("ALCOA-CERT-"))
        self.assertIn("digital_fingerprint_sha256", cert)
        self.assertEqual(len(cert["digital_fingerprint_sha256"]), 64)
        self.assertEqual(cert["trial_id"], "CTRI/2017/12/010899")
        self.assertIn("alcoa_score", cert)


if __name__ == "__main__":
    unittest.main()
