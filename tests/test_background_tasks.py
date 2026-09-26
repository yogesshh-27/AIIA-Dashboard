import unittest
import asyncio
from services.background_tasks import (
    async_generate_clinical_report,
    async_sync_ctri_registry,
    get_job_status
)

class TestBackgroundTasks(unittest.TestCase):
    def test_async_report_processing(self):
        job_id = "test-job-001"
        asyncio.run(async_generate_clinical_report(job_id, "trial_progress", {}))
        status = get_job_status(job_id)
        self.assertEqual(status["status"], "COMPLETED")
        self.assertEqual(status["progress"], 100)
        self.assertIn("download_url", status)

    def test_async_ctri_sync(self):
        job_id = "test-ctri-001"
        asyncio.run(async_sync_ctri_registry(job_id))
        status = get_job_status(job_id)
        self.assertEqual(status["status"], "COMPLETED")
        self.assertEqual(status["records_fetched"], 75)
