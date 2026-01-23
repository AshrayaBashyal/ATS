from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/users/", include(("apps.users.urls", "users"), namespace="users")),
    path("api/companies/", include("apps.companies.api.urls")),



    # Schema (raw OpenAPI JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ReDoc (alternative UI)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]
