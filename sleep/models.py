from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SleepGoal(models.Model):
    """
    Model representing a user's sleep goal.

    - One-to-one relationship with User.
    - Tracks target sleep duration, bedtime, and waketime.
    - Automatically records creation and update timestamps.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="sleep_goal")
    target_hours = models.DecimalField(
        max_digits=4, decimal_places=2, default=8.00,
        help_text="Target sleep duration in hours (e.g., 8.00)"
    )
    target_bedtime = models.TimeField(
        null=True, blank=True,
        help_text="Desired bedtime (optional)"
    )
    target_waketime = models.TimeField(
        null=True, blank=True,
        help_text="Desired waketime (optional)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='sleep_goal_user_idx'),
        ]

    def __str__(self):
        return f"Goal for {self.user.username}: {self.target_hours}h"

    def clean(self):
        """Validate that target_hours is positive."""
        if self.target_hours <= 0:
            raise ValidationError({"target_hours": "Target hours must be a positive number."})
        if self.target_bedtime and self.target_waketime and self.target_bedtime >= self.target_waketime:
            raise ValidationError({"target_waketime": "Wake time must be after bed time."})

class SleepSession(models.Model):
    """
    Model representing a user's sleep session.

    - Foreign key relationship with User for multiple sessions.
    - Tracks start/end times, quality, latency, awakenings, notes, tags, and sleep stages.
    - Includes calculated duration_hours and meets_goal properties.
    - Automatically records creation and update timestamps.
    """
    STAGE_CHOICES = [
        ("awake", "Awake"),
        ("light", "Light"),
        ("deep", "Deep"),
        ("rem", "REM"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sleep_sessions")
    start = models.DateTimeField(
        help_text="Start time of the sleep session"
    )
    end = models.DateTimeField(
        help_text="End time of the sleep session"
    )
    quality = models.PositiveSmallIntegerField(
        default=3, help_text="1 (poor) to 5 (excellent)"
    )
    latency_minutes = models.PositiveIntegerField(
        default=0, help_text="Time to fall asleep in minutes"
    )
    awakenings = models.PositiveIntegerField(
        default=0, help_text="Number of awakenings"
    )
    notes = models.TextField(blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags like 'caffeine, workout'")
    stages_json = models.JSONField(
        blank=True, null=True,
        help_text="Optional list of dicts with 't' (timestamp) and 'stage' (e.g., [{'t': '09:00', 'stage': 'light'}])"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start"]
        indexes = [
            models.Index(fields=['user', 'start'], name='sleep_session_user_start_idx'),
        ]

    @property
    def duration_hours(self):
        """Calculate the duration of the sleep session in hours."""
        if self.start and self.end:
            delta = self.end - self.start
            return round(delta.total_seconds() / 3600, 2)
        return 0.0

    @property
    def meets_goal(self):
        """Check if the session duration meets the user's sleep goal."""
        try:
            goal = self.user.sleep_goal
            return self.duration_hours >= float(goal.target_hours)
        except SleepGoal.DoesNotExist:
            return None

    def clean(self):
        """Validate that start is before end."""
        if self.start and self.end and self.start >= self.end:
            raise ValidationError({"end": "End time must be after start time."})

    def __str__(self):
        return f"SleepSession({self.user.username} {self.start} -> {self.end})"

        