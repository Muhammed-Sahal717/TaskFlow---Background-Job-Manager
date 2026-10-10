from rest_framework import status, viewsets, generics
from rest_framework.response import Response

from .models import Job, ScheduledRun
from .serializers import JobSerializer, ScheduledRunSerializer
from .tasks import process_job


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by("-created_at")
    serializer_class = JobSerializer

    filterset_fields = ["status", "job_type"]
    search_fields = ["job_type", "error_message"]
    ordering_fields = ["created_at", "updated_at", "status"]
    ordering = ["-created_at"]

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

class ScheduledRunListView(generics.ListAPIView):
    queryset = ScheduledRun.objects.all().order_by("-executed_at")
    serializer_class = ScheduledRunSerializer
