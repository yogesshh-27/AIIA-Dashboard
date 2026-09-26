import unittest
from services.esignature_service import sign_record, verify_signature, get_record_signature

class TestESignatures(unittest.TestCase):
    def test_esignature_success_and_verification(self):
        """Test creating a 21 CFR Part 11 signature with re-authentication and verifying hash chain."""
        res = sign_record(
            record_type="approval",
            record_id="APPR-TEST-001",
            signer_name="Dr. Test Signer",
            signer_role="IEC Chairperson",
            intent="Ethical Clearance Granted",
            reauth_password="AdminPassword@2026"
        )
        self.assertTrue(res["success"])
        self.assertIn("SIG-", res["signature_id"])
        self.assertTrue(len(res["signature_hash"]) == 64)

        # Verify signature integrity
        verify = verify_signature(res["signature_id"])
        self.assertTrue(verify["valid"])
        self.assertEqual(verify["chain_integrity"], "INTEGRITY_VERIFIED")

    def test_esignature_invalid_password_rejection(self):
        """Test rejection when password does not match 21 CFR Part 11 requirements."""
        res = sign_record(
            record_type="approval",
            record_id="APPR-TEST-002",
            signer_name="Dr. Test Signer",
            signer_role="Reviewer",
            intent="Approval",
            reauth_password="bad"
        )
        self.assertFalse(res["success"])
        self.assertIn("Re-authentication failed", res["error"])
