from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SleepGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="sleep_goal")
    target_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8)
    target_bedtime = models.TimeField(null=True, blank=True)
    target_waketime = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Goal for {self.user.username}: {self.target_hours}h"

class SleepSession(models.Model):
    STAGE_CHOICES = [
        ("awake", "Awake"),
        ("light", "Light"),
        ("deep", "Deep"),
        ("rem", "REM"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sleep_sessions")
    start = models.DateTimeField()
    end = models.DateTimeField()
    quality = models.PositiveSmallIntegerField(default=3, help_text="1 (poor) to 5 (excellent)")
    latency_minutes = models.PositiveIntegerField(default=0, help_text="Time to fall asleep")
    awakenings = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags like 'caffeine, workout'")
    stages_json = models.JSONField(blank=True, null=True, help_text="Optional list of dicts with 't' and 'stage'")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start"]

    @property
    def duration_hours(self):
        delta = self.end - self.start
        return round(delta.total_seconds() / 3600, 2)

    @property
    def meets_goal(self):
        try:
            goal = self.user.sleep_goal
            return self.duration_hours >= float(goal.target_hours)
        except SleepGoal.DoesNotExist:
            return None

    def __str__(self):
        return f"SleepSession({self.user.username} {self.start} -> {self.end})"
