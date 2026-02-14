from rest_framework import serializers
from apps.applications.models import Application

# 1. Main Serializer for displaying data
class ApplicationSerializer(serializers.ModelSerializer):
    candidate_email = serializers.EmailField(source="candidate.email", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)
    company_name = serializers.CharField(source="job.company.name", read_only=True)
    resume = serializers.FileField(required=True)
    cover_letter = serializers.FileField(required=False)

    class Meta:
        model = Application
        fields = [
            "id", "job", "job_title", "company_name",
            "candidate_email", "status", "resume",
            "cover_letter", "created_at",
        ]
        read_only_fields = ["id", "status", "job", "created_at"]

class ChangeStatusSerializer(serializers.Serializer):   #This Method Provides Validation Against incorrect statuses
    status = serializers.ChoiceField(choices=Application.Status.choices)