from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "id",
            "task_id",
            "job_type",
            "status",
            "input_data",
            "result_data",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "task_id",
            "status",
            "result_data",
            "error_message",
            "created_at",
            "updated_at",
        ]
