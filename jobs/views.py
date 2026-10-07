from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Job
from .serializers import JobSerializer
from .tasks import process_job


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by("-created_at")
    serializer_class = JobSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = serializer.save(
            status=Job.Status.PENDING,
            job_type=serializer.validated_data["job_type"],
            input_data=serializer.validated_data.get("input_data", {}),
        )

        task = process_job.delay(str(job.id))

        job.task_id = task.id
        job.save(update_fields=["task_id", "updated_at"])

        return Response(
            JobSerializer(job).data,
            status=status.HTTP_202_ACCEPTED,
        )
