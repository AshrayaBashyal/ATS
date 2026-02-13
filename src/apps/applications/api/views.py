from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError


from apps.applications.models import Application
from apps.applications.services.application_service import (
    apply_to_job,
    change_application_status,
    get_applications_for_user,
)
from apps.applications.api.serializers import (
    ApplicationSerializer,
    ChangeStatusSerializer,
)
from apps.jobs.models import Job


class ApplicationViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationSerializer


    def get_queryset(self):
        return get_applications_for_user(user=self.request.user)

    
    @action(detail=False, methods=["post"])
    def apply(self, request):
        job_id = request.data.get("job")
        job = get_object_or_404(Job, id=job_id)

        try:
            application = apply_to_job(
                job=job,
                candidate=request.user,
                resume=request.FILES.get("resume"),
                cover_letter=request.data.get("cover_letter"),
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)

        serializer = self.get_serializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        application = self.get_object()
        serializer = ChangeStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            application = change_application_status(
                application=application,
                status=serializer.validated_data["status"],
                changed_by=request.user,
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)

        return Response(
            self.get_serializer(application).data,
            status=status.HTTP_200_OK,
        )


    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
