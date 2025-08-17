from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import SleepSessionViewSet, SleepGoalViewSet

router = DefaultRouter()
router.register(r"sessions", SleepSessionViewSet, basename="session")
router.register(r"goals", SleepGoalViewSet, basename="goal")

urlpatterns = [
    path("", include(router.urls)),
]
