import time
from celery import shared_task

from .models import Job, ScheduledRun


@shared_task(bind=True, max_retries=3)
def process_job(self, job_id):
    job = Job.objects.get(id=job_id)

    try:
        job.status = Job.Status.PROCESSING
        job.save(update_fields=["status", "updated_at"])

        time.sleep(5)

        if job.input_data.get("force_failure"):
            raise Exception("Intentional failure requested for testing")

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
        if self.request.retries >= self.max_retries:
            job.status = Job.Status.FAILURE
            job.error_message = str(exc)
            job.save(
                update_fields=[
                    "status",
                    "error_message",
                    "updated_at",
                ]
            )

            raise

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


@shared_task
def scheduled_heartbeat():
    run = ScheduledRun.objects.create(
        task_name="scheduled_heartbeat",
        message="TaskFlow scheduled task executed successfully",
    )

    print(f"Scheduled run recorded: {run.id}")

    return {
        "run_id": run.id,
        "message": run.message,
    }
