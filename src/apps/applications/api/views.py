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

from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


class ApplicationViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Application.objects.all() # MUST add this to fix the 'id' warning
    serializer_class = ApplicationSerializer
    parser_classes = [MultiPartParser, FormParser]


    def get_queryset(self):
        return get_applications_for_user(user=self.request.user)


    @extend_schema(
        operation_id="apply_to_job",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'job': {'type': 'integer'},
                    'resume': {'type': 'string', 'format': 'binary'}, # This triggers the upload button
                    'cover_letter': {'type': 'string', 'format': 'binary'},
                },
                'required': ['job', 'resume'], # Tells Swagger 'resume' is a mandatory file
            },
        },
        responses={201: ApplicationSerializer}
    )


    @action(detail=False, methods=["post"], parser_classes = [MultiPartParser, FormParser])
    def apply(self, request):
        job_id = request.data.get("job")
        job = get_object_or_404(Job, id=job_id)

        try:
            application = apply_to_job(
                job=job,
                candidate=request.user,
                resume=request.FILES.get("resume"),
                cover_letter=request.FILES.get("cover_letter"),
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)

        serializer = self.get_serializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @extend_schema(request=ChangeStatusSerializer)
    @action(detail=True, methods=["post"], parser_classes=[JSONParser])
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
