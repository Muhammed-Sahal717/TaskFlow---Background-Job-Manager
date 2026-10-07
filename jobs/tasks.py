from celery import shared_task

from .models import Job


@shared_task(bind=True, max_retries=3)
def process_job(self, job_id):
    job = Job.objects.get(id=job_id)

    try:
        job.status = Job.Status.PROCESSING
        job.save(update_fields=["status", "updated_at"])

        # Simulate background work
        import time

        time.sleep(5)

        result = {
            "message": "Job processed successfully",
            "job_id": str(job.id),
        }

        job.status = Job.Status.SUCCESS
        job.result_data = result
        job.error_message = ""
        job.save(
            update_fields=[
                "status",
                "result_data",
                "error_message",
                "updated_at",
            ]
        )

        return result

    except Exception as exc:
        job.status = Job.Status.RETRYING
        job.error_message = str(exc)
        job.save(
            update_fields=[
                "status",
                "error_message",
                "updated_at",
            ]
        )

        raise self.retry(exc=exc, countdown=5)
