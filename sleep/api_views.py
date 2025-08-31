# sleep/api_views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta 
from .models import SleepSession, SleepGoal
from .serializers import SleepSessionSerializer, SleepGoalSerializer

class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination class to control the number of items per page."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class SleepSessionViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing SleepSession instances for the authenticated user.

    - Supports CRUD operations.
    - Filters data by the authenticated user.
    - Validates that start time is before end time.
    - Paginates results for better performance.
    """
    serializer_class = SleepSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return SleepSession objects for the authenticated user, ordered by start date (descending),
        with optional date range filtering."""
        queryset = SleepSession.objects.filter(user=self.request.user).order_by("-start")
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            start_datetime = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            queryset = queryset.filter(start__gte=start_datetime)
        if end_date:
            end_datetime = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
            queryset = queryset.filter(start__lt=end_datetime)
        return queryset

    def perform_create(self, serializer):
        """Associate the new SleepSession with the authenticated user and validate dates."""
        data = serializer.validated_data
        if data.get('start') >= data.get('end'):
            raise ValidationError({"end": "End time must be after start time."})
        serializer.save(user=self.request.user)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        if 'start' in validated_data and 'end' in validated_data and validated_data.get('start') >= validated_data.get('end'):
            raise ValidationError({"end": "End time must be after start time."})
        self.perform_update(serializer)
        return Response(serializer.data)

class SleepGoalViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing SleepGoal instances for the authenticated user.

    - Supports CRUD operations.
    - Filters data by the authenticated user.
    - Validates that target_hours is positive.
    """
    serializer_class = SleepGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return SleepGoal objects for the authenticated user."""
        return SleepGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Associate the new SleepGoal with the authenticated user and validate target_hours."""
        data = serializer.validated_data
        if data.get('target_hours') <= 0:
            raise ValidationError({"target_hours": "Target hours must be a positive number."})
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """Override update to validate target_hours on partial updates."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('target_hours') <= 0:
            raise ValidationError({"target_hours": "Target hours must be a positive number."})
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Override destroy to prevent deletion if a related SleepSession exists."""
        instance = self.get_object()
        if SleepSession.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "Cannot delete goal while sleep sessions exist."},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)        