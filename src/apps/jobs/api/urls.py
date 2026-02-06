from rest_framework.routers import DefaultRouter
from apps.jobs.api.views import JobViewset, PublicJobViewset


router = DefaultRouter()

router.register(r"jobs", PublicJobViewset, basename="public-jobs")
router.register(r"manage/jobs", JobViewset, basename="recruiter-jobs")

urlpatterns = router.urls
