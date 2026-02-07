from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from django.db.models import Q
from django.shortcuts import get_object_or_404

from apps.jobs.models import Job
from apps.jobs.api.serializers import JobSerializer
from apps.jobs.services.job_service import (
    create_job,
    update_job,
    delete_job,
    change_job_status,
)
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

class JobViewset(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='mine', description='Filter: Only my jobs', type=bool),
            OpenApiParameter(name='status', description='Filter: Job status', type=str),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


    def get_queryset(self):
        user = self.request.user
        queryset = Job.objects.select_related("company", "created_by")
        # Logic: 
        # 1. Show all jobs I created (including Drafts)
        # 2. Show Open/Closed jobs from my companies (exclude Drafts)
        queryset =  queryset.filter(
            Q(created_by=user) | 
            (Q(company__memberships__user=user) & ~Q(status__iexact="draft"))
        ).distinct()
    
        # Optional Toggle: /api/manage/jobs/?mine=true
        show_only_mine = self.request.query_params.get('mine') == 'true'
        if show_only_mine:
            queryset = queryset.filter(created_by=user)

        # Optional Filter: Show specific status (?status=OPEN)
        status_param = self.request.query_params.get('status')
        if status_param:
            # 'open' or 'OPEN' both work
            queryset = queryset.filter(status__iexact=status_param)        

        return queryset
    

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
    

    def destroy(self, request, *args, **kwargs):
        job = self.get_object()
        delete_job(job=job, deleted_by=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        job = self.get_object()
        status_value = request.data.get("status")

        job = change_job_status(job=job, status=status_value, changed_by=request.user)
        return Response(self.get_serializer(job).data)
    

class PublicJobViewset(viewsets.ReadOnlyModelViewSet):
    """
    Public Viewset for Candidates (and anyone else) to see all OPEN jobs.
    """
    serializer_class = JobSerializer
    # IsAuthenticatedOrReadOnly so unauthenticated users can browse
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Job.objects.filter(status__iexact="open").select_related("company", "created_by")