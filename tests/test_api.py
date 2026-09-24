import unittest
import urllib.request
import urllib.error
import json
import threading
import time
import socketserver
import os
import sys

# Ensure workspace is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import server
import db_service

TEST_PORT = 8008

class TestAIIADashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db_service.init_indexes()
        socketserver.TCPServer.allow_reuse_address = True
        cls.httpd = socketserver.ThreadingTCPServer(("127.0.0.1", TEST_PORT), server.AIIADashboardHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def get_url(self, path):
        req = urllib.request.Request(f"http://127.0.0.1:{TEST_PORT}{path}")
        with urllib.request.urlopen(req) as response:
            return response.status, response.headers.get("Content-Type"), response.read()

    def test_01_static_index(self):
        status, ctype, content = self.get_url("/")
        self.assertEqual(status, 200)
        self.assertIn(b"All India Institute of Ayurveda", content)
        self.assertIn(b"AYURCTMS", content)

    def test_02_static_css(self):
        status, ctype, content = self.get_url("/app.css")
        self.assertEqual(status, 200)
        self.assertIn(b"--ayur-primary", content)
        self.assertIn(b"gate-card", content)

    def test_03_static_js(self):
        status, ctype, content = self.get_url("/app.js")
        self.assertEqual(status, 200)
        self.assertIn(b"handlePatientMatchingSubmit", content)

    def test_04_api_stats(self):
        status, ctype, content = self.get_url("/api/stats")
        self.assertEqual(status, 200)
        data = json.loads(content.decode("utf-8"))
        self.assertIn("aiia", data)
        self.assertEqual(data["aiia"]["total_trials"], 263)
        self.assertGreater(data["aiia"]["pg_thesis"], 200)
        self.assertGreater(data["ayush_total"], 3000)
        self.assertEqual(data["national_total"], 39821)

    def test_05_api_trials_default(self):
        status, ctype, content = self.get_url("/api/trials?scope=aiia&page=1&limit=10")
        self.assertEqual(status, 200)
        data = json.loads(content.decode("utf-8"))
        self.assertEqual(data["total"], 263)
        self.assertEqual(len(data["data"]), 10)
        first = data["data"][0]
        self.assertIn("CTRI_Number", first)
        self.assertIn("Public_Title", first)
        self.assertIn("Phase", first)

    def test_06_api_trials_search(self):
        status, ctype, content = self.get_url("/api/trials?scope=aiia&search=Galib")
        self.assertEqual(status, 200)
        data = json.loads(content.decode("utf-8"))
        self.assertGreater(data["total"], 0)
        for r in data["data"]:
            self.assertTrue("Galib" in (r["PI_Name"] or "") or "Galib" in (r["PI_Affiliation"] or ""))

    def test_07_api_trial_dossier(self):
        status, ctype, content = self.get_url("/api/trials?scope=aiia&page=1&limit=1")
        data = json.loads(content.decode("utf-8"))
        trial_id = data["data"][0]["Trial_ID"]

        dossier_status, _, dossier_content = self.get_url(f"/api/trials/{trial_id}")
        self.assertEqual(dossier_status, 200)
        dossier = json.loads(dossier_content.decode("utf-8"))
        self.assertIn("titles", dossier)
        self.assertIn("details", dossier)
        self.assertIn("recruitment", dossier)
        self.assertIn("sponsor", dossier)
        self.assertIn("pi", dossier)
        self.assertIn("ethics", dossier)

    def test_08_api_governance(self):
        status, ctype, content = self.get_url("/api/governance")
        self.assertEqual(status, 200)
        data = json.loads(content.decode("utf-8"))
        self.assertIn("ethics_committees", data)
        self.assertIn("registration_timeliness", data)
        self.assertIn("top_investigators", data)

    def test_09_api_analytics(self):
        status, ctype, content = self.get_url("/api/analytics")
        self.assertEqual(status, 200)
        data = json.loads(content.decode("utf-8"))
        self.assertIn("phases", data)
        self.assertIn("trial_types", data)
        self.assertIn("yearly_registration", data)
        self.assertIn("top_conditions", data)

    def test_10_api_cdisc(self):
        status, ctype, content = self.get_url("/api/cdisc?search=Protocol&limit=5")
        self.assertEqual(status, 200)
        data = json.loads(content.decode("utf-8"))
        self.assertGreater(len(data), 0)
        self.assertIn("term", data[0])
        self.assertIn("definition", data[0])

    def test_12_api_app_stats(self):
        status, ctype, content = self.get_url("/api/app/stats")
        self.assertEqual(status, 200)
        data = json.loads(content.decode("utf-8"))
        self.assertIn("trials_total", data)
        self.assertGreater(data["trials_total"], 0)
        self.assertIn("cdisc_mappings", data)
        self.assertIn("compliance_checks", data)

    def test_13_api_app_trials(self):
        status, ctype, content = self.get_url("/api/app/trials?scope=aiia&limit=5")
        self.assertEqual(status, 200)
        data = json.loads(content.decode("utf-8"))
        self.assertIn("data", data)
        self.assertGreater(len(data["data"]), 0)
        first = data["data"][0]
        self.assertIn("ctri_number", first)
        self.assertIn("public_title", first)

    def test_14_api_dashboard_portfolio(self):
        status, ctype, content = self.get_url("/api/dashboard/portfolio")
        self.assertEqual(status, 200)
        data = json.loads(content.decode("utf-8"))
        self.assertIn("kpis", data)
        self.assertEqual(data["kpis"]["total_trials"], 263)
        self.assertEqual(data["kpis"]["active_trials"], 242)
        self.assertEqual(data["kpis"]["recruiting_trials"], 11)
        self.assertEqual(data["kpis"]["completed_trials"], 21)
        self.assertIn("status_distribution", data)
        self.assertIn("type_distribution", data)
        self.assertIn("recruitment_overview", data)
        self.assertIn("milestones", data)
        self.assertIn("compliance_alerts", data)
        self.assertIn("safety_overview", data)
        self.assertIn("recent_activity", data)

    def test_15_api_trials_sorting(self):
        status, ctype, content = self.get_url("/api/trials?scope=aiia&sort_by=sample_size&sort_dir=desc&limit=5")
        self.assertEqual(status, 200)
        data = json.loads(content.decode("utf-8"))
        self.assertEqual(len(data["data"]), 5)
        sizes = [d["Sample_Size_Num"] for d in data["data"] if d["Sample_Size_Num"] is not None]
        self.assertEqual(sizes, sorted(sizes, reverse=True))

    def test_16_api_export_formats(self):
        # CSV Export
        status, ctype, content = self.get_url("/api/export?scope=aiia&format=csv")
        self.assertEqual(status, 200)
        self.assertIn("text/csv", ctype)
        self.assertIn(b"CTRI Number", content)

        # JSON Export
        status_j, ctype_j, content_j = self.get_url("/api/export?scope=aiia&format=json")
        self.assertEqual(status_j, 200)
        self.assertIn("application/json", ctype_j)
        j_data = json.loads(content_j.decode("utf-8"))
        self.assertEqual(len(j_data), 263)

    def test_17_api_trial_dossier_enrichment(self):
        # Pick first AIIA trial
        status, _, content = self.get_url("/api/trials?scope=aiia&page=1&limit=1")
        data = json.loads(content.decode("utf-8"))
        trial_id = data["data"][0]["Trial_ID"]
        
        status_d, _, content_d = self.get_url(f"/api/trials/{trial_id}")
        self.assertEqual(status_d, 200)
        dossier = json.loads(content_d.decode("utf-8"))
        self.assertIn("app_records", dossier)
        self.assertIn("milestones", dossier["app_records"])
        self.assertIn("compliance_checks", dossier["app_records"])
        self.assertIn("alerts", dossier["app_records"])

if __name__ == "__main__":
    unittest.main()

