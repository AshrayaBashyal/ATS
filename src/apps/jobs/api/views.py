from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.jobs.models import Job
from apps.jobs.api.serializers import JobSerializer
from apps.jobs.services.job_service import (
    create_job,
    update_job,
    delete_job,
    change_job_status,
)


class JobViewset(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(company__membership__user=self.request.user).select_related("company", "created_by")