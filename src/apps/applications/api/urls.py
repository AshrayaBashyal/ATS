from rest_framework.routers import DefaultRouter
from apps.applications.api.views import ApplicationViewSet

router = DefaultRouter()
router.register("applications", ApplicationViewSet, basename="applications")

urlpatterns = router.urls
