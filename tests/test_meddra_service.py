import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.meddra_service import (
    search_meddra,
    calculate_regulatory_timelines,
    generate_e2b_r3_xml,
)


class TestMeddraService(unittest.TestCase):
    def test_search_meddra_all(self):
        results = search_meddra()
        self.assertGreaterEqual(len(results), 5)
        for r in results:
            self.assertIn("meddra_code", r)
            self.assertIn("pt", r)
            self.assertIn("soc", r)
            self.assertIn("ayurvedic_correlate", r)

    def test_search_meddra_query(self):
        results = search_meddra("rash")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["pt"], "Rash")

        results_ayur = search_meddra("Amlapitta")
        self.assertGreaterEqual(len(results_ayur), 1)
        self.assertEqual(results_ayur[0]["pt"], "Dyspepsia")

    def test_calculate_regulatory_timelines(self):
        timelines = calculate_regulatory_timelines()
        self.assertIsInstance(timelines, list)
        if len(timelines) > 0:
            first = timelines[0]
            self.assertIn("event_id", first)
            self.assertIn("report_type", first)
            self.assertIn("hours_remaining", first)
            self.assertIn("urgency", first)
            self.assertIn(first["urgency"], ["CRITICAL_URGENT", "EXPIRING_SOON", "ON_TRACK", "OVERDUE"])
            self.assertIn("required_recipients", first)

    def test_generate_e2b_r3_xml(self):
        xml_content = generate_e2b_r3_xml("EVT-9099")
        self.assertIn("<?xml", xml_content)
        self.assertIn("<ichicsr", xml_content)
        self.assertIn("<messagesenderidentifier>AIIA-NPVCC-NEWDELHI</messagesenderidentifier>", xml_content)
        self.assertIn("<safetyreportid>IND-AIIA-EVT-9099</safetyreportid>", xml_content)
        self.assertIn("<primarysourcereaction>Skin Rash with Pruritus</primarysourcereaction>", xml_content)


if __name__ == "__main__":
    unittest.main()
