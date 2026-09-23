import unittest
import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000"

def get_json(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "AIIA-TestRunner/1.0"})
    with urllib.request.urlopen(req, timeout=5) as response:
        assert response.status == 200, f"Expected 200 OK, got {response.status}"
        return json.loads(response.read().decode('utf-8'))

class TestPharmacovigilanceModule(unittest.TestCase):
    """Integration tests for the AIIA Pharmacovigilance Module."""

    def test_pv_overview_kpis_and_disclaimers(self):
        """Verify PV Overview dashboard KPIs, disclaimers and distributions."""
        data = get_json("/api/pv/overview")
        
        # Verify mandatory synthetic data disclaimer
        self.assertIn("disclaimer", data)
        self.assertIn("Demonstration / Synthetic Safety Data", data["disclaimer"])
        self.assertTrue(data.get("is_synthetic"))

        # Verify decision support notice
        self.assertIn("signal_disclaimer", data)
        self.assertIn("decision-support outputs", data["signal_disclaimer"])

        # Verify 6 required KPI metrics
        kpis = data.get("kpis", {})
        self.assertIn("total_ae", kpis)
        self.assertGreater(kpis["total_ae"], 0)
        self.assertIn("total_sae", kpis)
        self.assertGreater(kpis["total_sae"], 0)
        self.assertIn("open_reports", kpis)
        self.assertIn("under_review", kpis)
        self.assertIn("closed_reports", kpis)
        self.assertIn("potential_signals", kpis)
        self.assertGreater(kpis["potential_signals"], 0)

        # Verify distribution breakdowns
        self.assertIn("severity_distribution", data)
        self.assertGreater(len(data["severity_distribution"]), 0)
        self.assertIn("causality_distribution", data)
        self.assertGreater(len(data["causality_distribution"]), 0)
        self.assertIn("outcome_distribution", data)
        self.assertGreater(len(data["outcome_distribution"]), 0)

    def test_pv_adverse_events_table_and_filtering(self):
        """Verify AE/SAE table columns, status field, and filters."""
        data = get_json("/api/pv/adverse-events?page=1&limit=10")
        self.assertIn("data", data)
        self.assertGreater(len(data["data"]), 0)
        
        # Verify required columns for each AE record
        record = data["data"][0]
        self.assertIn("report_id", record)
        self.assertIn("ctri_number", record)
        self.assertIn("event_term", record)
        self.assertIn("severity", record)
        self.assertIn("is_serious", record)
        self.assertIn("onset_date", record)
        self.assertIn("status", record)
        self.assertIn(record["status"], ["Open", "Under Review", "Closed"])

        # Verify serious_only filter
        sae_data = get_json("/api/pv/adverse-events?serious_only=true&limit=10")
        for r in sae_data["data"]:
            self.assertEqual(r["is_serious"], 1)

        # Verify severity filter
        mild_data = get_json("/api/pv/adverse-events?severity=Mild&limit=10")
        for r in mild_data["data"]:
            self.assertEqual(r["severity"], "Mild")

        # Verify status filter
        closed_data = get_json("/api/pv/adverse-events?status=Closed&limit=10")
        for r in closed_data["data"]:
            self.assertEqual(r["status"], "Closed")

    def test_pv_safety_signals_detection(self):
        """Verify aggregated signal detection, frequency comparison, and review status."""
        data = get_json("/api/pv/signals?page=1&limit=10")
        self.assertIn("data", data)
        self.assertGreater(len(data["data"]), 0)
        
        # Check disclaimer
        self.assertIn("signal_disclaimer", data)
        self.assertIn("decision-support outputs", data["signal_disclaimer"])

        # Check signal fields
        sig = data["data"][0]
        self.assertIn("signal_code", sig)
        self.assertIn("event_term", sig)
        self.assertIn("ctri_number", sig)
        self.assertIn("current_frequency", sig)
        self.assertIn("previous_frequency", sig)
        self.assertIn("change_pct", sig)
        self.assertIn("severity", sig)
        self.assertIn("review_status", sig)
        self.assertIn(sig["severity"], ["High", "Medium", "Low"])

    def test_pv_reporting_deadlines_and_overdue_flag(self):
        """Verify safety reporting deadlines across IEC, DCGI/CDSCO, Annual Safety Reports."""
        data = get_json("/api/pv/reporting?page=1&limit=25")
        self.assertIn("data", data)
        self.assertGreater(len(data["data"]), 0)

        # Verify deadline fields
        item = data["data"][0]
        self.assertIn("ctri_number", item)
        self.assertIn("report_type", item)
        self.assertIn("deadline_date", item)
        self.assertIn("status", item)
        self.assertIn("responsible_role", item)

        # Verify presence of Overdue status flagging
        statuses = [d["status"] for d in data["data"]]
        self.assertTrue(any(s == "Overdue" for s in statuses) or any(s == "Due Soon" for s in statuses))

if __name__ == "__main__":
    unittest.main()
