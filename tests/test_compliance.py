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

def post_json(path, payload):
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "User-Agent": "AIIA-TestRunner/1.0"
    })
    with urllib.request.urlopen(req, timeout=5) as response:
        assert response.status == 200, f"Expected 200 OK, got {response.status}"
        return json.loads(response.read().decode('utf-8'))

class TestComplianceAndAlertEngine(unittest.TestCase):
    def test_compliance_overview(self):
        data = get_json("/api/compliance/overview")
        self.assertIn("summary", data)
        self.assertIn("checks", data)
        
        summary = data["summary"]
        self.assertEqual(summary["total_checks"], 7)
        self.assertIn("compliant", summary)
        self.assertIn("due_soon", summary)
        self.assertIn("overdue", summary)
        self.assertIn("compliance_rate", summary)
        
        # Verify all 7 core checks are present
        checks = data["checks"]
        self.assertEqual(len(checks), 7)
        
        expected_checks = [
            "CTRI Registration",
            "IEC / Ethics Approval",
            "Required Documentation",
            "Monitoring",
            "Safety Reporting",
            "Data Quality",
            "Protocol Compliance"
        ]
        
        actual_names = [c["check_name"] for c in checks]
        for ec in expected_checks:
            self.assertIn(ec, actual_names, f"Expected check '{ec}' not found in compliance overview")

        # Verify each check has required fields, transparent rule rationale, and role
        for c in checks:
            self.assertIn("status", c)
            self.assertIn(c["status"], ["Compliant", "Pending", "Due Soon", "Overdue", "Non-Compliant"])
            self.assertIn("last_checked", c)
            self.assertIn("due_date", c)
            self.assertIn("responsible_role", c)
            self.assertIn("action_label", c)
            self.assertIn("reason_rule", c)
            self.assertTrue(len(c["reason_rule"]) > 10, "Rule logic rationale must be explicit and non-empty")

    def test_data_quality_audit(self):
        # 1. Test AIIA scope
        data = get_json("/api/compliance/data-quality?scope=aiia")
        self.assertEqual(data["scope"], "aiia")
        self.assertEqual(data["total_trials"], 263)
        self.assertIn("completeness_rate", data)
        self.assertGreater(data["completeness_rate"], 90.0)
        self.assertIn("total_defects", data)
        self.assertIn("metrics", data)
        
        metrics = data["metrics"]
        self.assertIn("missing_sample_size", metrics)
        self.assertIn("missing_sponsors", metrics)
        self.assertIn("missing_interventions", metrics)
        self.assertIn("missing_outcomes", metrics)
        self.assertIn("duplicate_ctri", metrics)
        self.assertIn("retrospective_registration", metrics)
        self.assertIn("status_completed_no_date", metrics)

        # 2. Test Full Registry scope
        all_data = get_json("/api/compliance/data-quality?scope=all")
        self.assertEqual(all_data["scope"], "all")
        self.assertGreater(all_data["total_trials"], 1000)
        self.assertIn("flagged_trials", all_data)

    def test_alerts_listing_and_filtering(self):
        data = get_json("/api/alerts?limit=20")
        self.assertIn("total", data)
        self.assertGreater(data["total"], 0)
        self.assertIn("counts_by_severity", data)
        self.assertIn("counts_by_category", data)
        self.assertIn("data", data)
        
        first = data["data"][0]
        self.assertIn("ctri_number", first)
        self.assertIn("trial_title", first)
        self.assertIn("category", first)
        self.assertIn("severity", first)
        self.assertIn("description", first)
        self.assertIn("responsible_role", first)
        self.assertIn("status", first)
        self.assertIn("due_date", first)

        # Test category filter
        crit_res = get_json("/api/alerts?severity=Critical")
        for item in crit_res["data"]:
            self.assertEqual(item["severity"], "Critical")

        # Test status filter
        act_res = get_json("/api/alerts?status=Active")
        for item in act_res["data"]:
            self.assertEqual(item["status"], "Active")

    def test_alert_status_mutation(self):
        # Fetch an active alert
        alerts = get_json("/api/alerts?status=Active&limit=1")
        if not alerts["data"]:
            alerts = get_json("/api/alerts?limit=1")
            
        self.assertGreater(len(alerts["data"]), 0)
        target_id = alerts["data"][0]["id"]
        
        # 1. Update to Acknowledged
        res1 = post_json(f"/api/alerts/{target_id}/status", {
            "status": "Acknowledged",
            "user": "Dr. Galib (Auditor)"
        })
        self.assertTrue(res1["success"])
        self.assertEqual(res1["alert"]["status"], "Acknowledged")
        
        # 2. Update to Resolved
        res2 = post_json(f"/api/alerts/{target_id}/status", {
            "status": "Resolved",
            "user": "Dr. Galib (Auditor)"
        })
        self.assertTrue(res2["success"])
        self.assertEqual(res2["alert"]["status"], "Resolved")
        self.assertEqual(res2["alert"]["is_resolved"], 1)
        self.assertIsNotNone(res2["alert"]["resolved_at"])

if __name__ == "__main__":
    unittest.main()
