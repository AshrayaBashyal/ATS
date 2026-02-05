from rest_framework import serializers
from apps.jobs.models import Job

class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.name")
    created_by_email = serializers.ReadOnlyField(source="created_by.email")
    created_by_full_name = serializers.ReadOnlyField(source="created_by.get_full_name")

    class Meta:
        model = Job
        fields = [
            "id",
            "company",
            "company_name",
            "title",
            "description",
            "department",
            "location",
            "status",
            "created_by_email",
            "created_by_full_name", 
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at"]