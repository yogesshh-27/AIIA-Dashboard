import unittest
from services.pharmacovigilance_engine import (
    calculate_disproportionality_metrics,
    analyze_dataset_signals
)

class TestPharmacovigilanceEngine(unittest.TestCase):
    def test_evans_signal_detection(self):
        """Test WHO/Evans et al. criteria: a >= 3, PRR >= 2.0, chi2 >= 4.0."""
        # Significant cluster: 10 target events out of 20 reports on target drug vs 5 target events out of 100 on other drugs
        # a=10, b=10, c=5, d=95
        res = calculate_disproportionality_metrics(a=10, b=10, c=5, d=95)
        self.assertTrue(res["is_signal"])
        self.assertTrue(res["evans_criteria_met"])
        self.assertGreaterEqual(res["prr"], 2.0)
        self.assertGreaterEqual(res["chi2_yates"], 4.0)
        self.assertGreater(res["ror"], 1.0)
        self.assertIn("High", res["confidence"])

    def test_no_signal_when_expected_rate(self):
        """Test no signal when event rate is proportional across drugs."""
        # a=2, b=48, c=10, d=240 -> PRR ~ 1.0
        res = calculate_disproportionality_metrics(a=2, b=48, c=10, d=240)
        self.assertFalse(res["is_signal"])
        self.assertFalse(res["evans_criteria_met"])
        self.assertLess(res["prr"], 1.5)

    def test_analyze_dataset_signals(self):
        """Test dataset scanning and signal identification."""
        events = [
            {"suspected_treatment": "Ashwagandha", "adverse_event": "Rash"},
            {"suspected_treatment": "Ashwagandha", "adverse_event": "Rash"},
            {"suspected_treatment": "Ashwagandha", "adverse_event": "Rash"},
            {"suspected_treatment": "Ashwagandha", "adverse_event": "Headache"},
            {"suspected_treatment": "Brahmi", "adverse_event": "Nausea"},
            {"suspected_treatment": "Brahmi", "adverse_event": "Fatigue"},
            {"suspected_treatment": "Curcumin", "adverse_event": "Headache"},
            {"suspected_treatment": "Curcumin", "adverse_event": "Mild Gastritis"},
        ]
        signals = analyze_dataset_signals(events)
        self.assertIsInstance(signals, list)
        self.assertTrue(len(signals) > 0)
        top = signals[0]
        self.assertEqual(top["suspected_treatment"], "Ashwagandha")
        self.assertEqual(top["adverse_event"], "Rash")
        self.assertEqual(top["case_count"], 3)
