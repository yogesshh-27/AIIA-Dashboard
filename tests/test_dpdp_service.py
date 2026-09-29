import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.dpdp_service import (
    get_dpdp_privacy_notice,
    record_dpdp_consent,
    withdraw_dpdp_consent,
    process_rights_request,
    get_dpo_audit_log,
)


class TestDpdpService(unittest.TestCase):
    def test_get_privacy_notice_en(self):
        notice = get_dpdp_privacy_notice("en")
        self.assertEqual(notice["language"], "en")
        self.assertIn("data_fiduciary", notice)
        self.assertGreaterEqual(len(notice["specified_purposes"]), 3)
        self.assertGreaterEqual(len(notice["data_principal_rights"]), 3)

    def test_get_privacy_notice_hi(self):
        notice = get_dpdp_privacy_notice("hi")
        self.assertEqual(notice["language"], "hi")
        self.assertIn("अखिल भारतीय आयुर्वेद संस्थान", notice["data_fiduciary"])

    def test_consent_lifecycle_record_and_withdraw(self):
        # 1. Record
        rec = record_dpdp_consent({
            "trial_id": "CTRI/2017/12/010899",
            "subject_id": "SUBJ-999",
            "abha_id": "91-1234-5678-9012",
            "language": "en",
            "purposes_granted": ["CLINICAL_EVALUATION"]
        })
        self.assertTrue(rec["success"])
        consent_id = rec["consent"]["consent_id"]
        self.assertEqual(rec["consent"]["status"], "ACTIVE")
        self.assertIn("consent_token", rec["consent"])

        # 2. Withdraw
        withdraw_res = withdraw_dpdp_consent(consent_id, "Patient opted out")
        self.assertTrue(withdraw_res["success"])
        self.assertEqual(withdraw_res["status"], "WITHDRAWN")

    def test_process_rights_request(self):
        res = process_rights_request({
            "subject_id": "SUBJ-999",
            "request_type": "ACCESS",
            "details": "Request personal clinical summary"
        })
        self.assertTrue(res["success"])
        self.assertEqual(res["request"]["request_type"], "ACCESS")
        self.assertEqual(res["request"]["status"], "IN_REVIEW")

    def test_dpo_audit_log(self):
        log = get_dpo_audit_log()
        self.assertIn("total_active_consents", log)
        self.assertIn("total_withdrawn_consents", log)
        self.assertEqual(log["dpo_compliance_status"], "FULLY_COMPLIANT")


if __name__ == "__main__":
    unittest.main()
