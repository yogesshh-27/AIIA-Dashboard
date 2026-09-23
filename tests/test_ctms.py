import unittest
import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

def get_json(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "AIIA-TestRunner/1.0"})
    with urllib.request.urlopen(req, timeout=5) as response:
        assert response.status == 200, f"Expected 200 OK, got {response.status}"
        return json.loads(response.read().decode('utf-8'))

class TestCTMSOperationalModule(unittest.TestCase):
    def test_ctms_overview(self):
        data = get_json("/api/ctms/overview")
        self.assertIn("disclaimer", data)
        self.assertIn("Synthetic / Demonstration Data", data["disclaimer"])
        self.assertIn("timelines", data)
        self.assertIn("recruitment", data)
        self.assertIn("monitoring", data)
        self.assertIn("deviations", data)
        self.assertIn("milestones", data)
        
        # Verify recruitment aggregates
        rec = data["recruitment"]
        self.assertGreater(rec["total_target"], 0)
        self.assertGreater(rec["total_current"], 0)
        self.assertIn("overall_pct", rec)
        
        # Verify deviations aggregates
        dev = data["deviations"]
        self.assertIn("total_deviations", dev)
        self.assertIn("open_count", dev)
        self.assertIn("critical", dev)
        
        # Verify milestones aggregates
        ms = data["milestones"]
        self.assertIn("total_milestones", ms)
        self.assertIn("overdue", ms)

    def test_ctms_timelines(self):
        data = get_json("/api/ctms/timelines?limit=10")
        self.assertIn("data", data)
        self.assertGreater(len(data["data"]), 0)
        first = data["data"][0]
        
        # Check all 9 operational timeline stages
        stages = [
            "stage_protocol_status",
            "stage_iec_status",
            "stage_ctri_status",
            "stage_activation_status",
            "stage_recruitment_status",
            "stage_monitoring_status",
            "stage_followup_status",
            "stage_dblock_status",
            "stage_closeout_status",
        ]
        for stage in stages:
            self.assertIn(stage, first, f"Missing stage {stage}")
            self.assertIn(first[stage], ["Completed", "In Progress", "Upcoming", "Due Soon", "Overdue"])

        # Check search filter
        search_res = get_json("/api/ctms/timelines?search=CTRI")
        self.assertIn("data", search_res)

    def test_ctms_recruitment(self):
        data = get_json("/api/ctms/recruitment?limit=10")
        self.assertIn("data", data)
        self.assertIn("portfolio_trend", data)
        self.assertGreater(len(data["data"]), 0)
        
        first = data["data"][0]
        self.assertIn("target_enrollment", first)
        self.assertIn("current_enrollment", first)
        self.assertIn("enrollment_pct", first)
        self.assertIn("expected_enrollment", first)
        self.assertIn("enrollment_gap", first)
        
        # Verify portfolio trend points
        trend = data["portfolio_trend"]
        self.assertEqual(len(trend), 12)
        self.assertIn("month", trend[0])
        self.assertIn("actual", trend[0])
        self.assertIn("projected", trend[0])

    def test_ctms_monitoring(self):
        data = get_json("/api/ctms/monitoring?limit=10")
        self.assertIn("data", data)
        self.assertGreater(len(data["data"]), 0)
        first = data["data"][0]
        self.assertIn("visit_code", first)
        self.assertIn("site_name", first)
        self.assertIn("monitor_name", first)
        self.assertIn("planned_date", first)
        self.assertIn("status", first)
        self.assertIn("findings", first)

        # Test status filter
        completed = get_json("/api/ctms/monitoring?status=Completed")
        self.assertIn("data", completed)
        for item in completed["data"]:
            self.assertEqual(item["status"], "Completed")

    def test_ctms_deviations(self):
        data = get_json("/api/ctms/deviations?limit=10")
        self.assertIn("data", data)
        self.assertGreater(len(data["data"]), 0)
        first = data["data"][0]
        self.assertIn("deviation_code", first)
        self.assertIn("category", first)
        self.assertIn("severity", first)
        self.assertIn("description", first)
        self.assertIn("resolution", first)

        # Test severity filter
        critical = get_json("/api/ctms/deviations?severity=Critical")
        self.assertIn("data", critical)
        for item in critical["data"]:
            self.assertEqual(item["severity"], "Critical")

    def test_ctms_milestones(self):
        data = get_json("/api/ctms/milestones?limit=10")
        self.assertIn("data", data)
        self.assertGreater(len(data["data"]), 0)
        first = data["data"][0]
        self.assertIn("milestone_name", first)
        self.assertIn("due_date", first)
        self.assertIn("responsible_role", first)
        self.assertIn("status", first)
        self.assertIn("is_overdue", first)

        # Test overdue_only filter
        overdue_res = get_json("/api/ctms/milestones?overdue_only=true")
        self.assertIn("data", overdue_res)
        self.assertGreater(len(overdue_res["data"]), 0)
        for item in overdue_res["data"]:
            self.assertTrue(item["is_overdue"] == 1 or item["status"] == "Overdue")

if __name__ == "__main__":
    unittest.main()
