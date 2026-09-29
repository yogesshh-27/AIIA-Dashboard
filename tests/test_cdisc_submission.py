import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.cdisc_submission_exporter import (
    get_sdtm_domain_dataset,
    get_adam_dataset,
    generate_define_xml_2_0,
)


class TestCdiscSubmission(unittest.TestCase):
    def test_sdtm_domains(self):
        for domain in ["TS", "DM", "AE", "EX", "DS", "LB"]:
            res = get_sdtm_domain_dataset(domain)
            self.assertEqual(res["domain"], domain)
            self.assertGreaterEqual(res["record_count"], 1)
            self.assertIn("variables", res)
            self.assertIn("STUDYID", res["variables"])

    def test_sdtm_invalid_domain(self):
        res = get_sdtm_domain_dataset("INVALID")
        self.assertIn("error", res)

    def test_adam_datasets(self):
        adsl = get_adam_dataset("ADSL")
        self.assertEqual(adsl["dataset_name"], "ADSL")
        self.assertIn("SAFFL", adsl["variables"])
        self.assertIn("PRAKRITI", adsl["variables"])

        adae = get_adam_dataset("ADAE")
        self.assertEqual(adae["dataset_name"], "ADAE")
        self.assertIn("TRTEMFL", adae["variables"])

    def test_define_xml_2_0(self):
        xml_content = generate_define_xml_2_0("CTRI/2017/12/010899")
        self.assertIn("<?xml", xml_content)
        self.assertIn("<?xml-stylesheet", xml_content)
        self.assertIn("<ODM", xml_content)
        self.assertIn("<ItemGroupDef", xml_content)
        self.assertIn('OID="IG.TS"', xml_content)
        self.assertIn('OID="IG.DM"', xml_content)


if __name__ == "__main__":
    unittest.main()
