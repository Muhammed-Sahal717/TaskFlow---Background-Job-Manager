from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Job, ScheduledRun
from .tasks import process_job, scheduled_heartbeat


class JobAPITests(APITestCase):
    def test_create_job(self):
        with patch("jobs.views.process_job.delay") as mock_task:
            mock_task.return_value.id = "test-task-id"

            response = self.client.post(
                "/api/jobs/",
                {
                    "job_type": "report",
                    "input_data": {"name": "Test Report"},
                },
                format="json",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_202_ACCEPTED,
        )
        self.assertEqual(response.data["status"], Job.Status.PENDING)
        self.assertEqual(response.data["task_id"], "test-task-id")
        self.assertTrue(Job.objects.filter(id=response.data["id"]).exists())
        mock_task.assert_called_once()


class ScheduledRunTests(TestCase):
    def test_scheduled_heartbeat_records_execution(self):
        result = scheduled_heartbeat.apply().get()

        self.assertEqual(ScheduledRun.objects.count(), 1)
        self.assertEqual(
            result["message"],
            "TaskFlow scheduled task executed successfully",
        )


class ProcessJobTests(TestCase):
    @patch("jobs.tasks.time.sleep")
    def test_process_job_succeeds(self, mock_sleep):
        job = Job.objects.create(
            job_type="report",
            input_data={"name": "Test Report"},
        )

        result = process_job.apply(args=[str(job.id)]).get()

        job.refresh_from_db()

        self.assertEqual(job.status, Job.Status.SUCCESS)
        self.assertEqual(result["job_id"], str(job.id))
        self.assertEqual(
            result["message"],
            "Job processed successfully",
        )
        mock_sleep.assert_called_once_with(5)
