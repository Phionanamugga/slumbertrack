from rest_framework import viewsets, permissions
from .models import SleepSession, SleepGoal
from .serializers import SleepSessionSerializer, SleepGoalSerializer

class SleepSessionViewSet(viewsets.ModelViewSet):
    serializer_class = SleepSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SleepSession.objects.filter(user=self.request.user).order_by("-start")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SleepGoalViewSet(viewsets.ModelViewSet):
    serializer_class = SleepGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SleepGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
