from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import JobViewSet, ScheduledRunListView


router = DefaultRouter()
router.register("jobs", JobViewSet, basename="job")

urlpatterns = [
    path("scheduled-runs/", ScheduledRunListView.as_view(), name="scheduled-runs"),
    *router.urls,
]
