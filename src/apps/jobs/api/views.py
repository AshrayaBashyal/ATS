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
        # Show jobs only from companies user belongs to
        return Job.objects.filter(company__membership__user=self.request.user).select_related("company", "created_by")
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = create_job(
            company=serializer.validated_data["company"],
            title=serializer.validated_data["title"],
            description=serializer.validated_data["description"],
            department=serializer.validated_data.get("department", ""),
            location=serializer.validated_data.get("location", ""),
            created_by=request.user,
        )

        return Response(self.get_serializer(job).data, status=status.HTTP_201_CREATED)


    def update(self, request, *args, **kwargs):
        job = self.get_object()
        serializer = self.get_serializer(job, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        job = update_job(job=job, data=serializer.validated_data, updated_by=request.user)

        return Response(self.get_serializer(job).data)
