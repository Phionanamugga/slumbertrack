from django.contrib import admin
from .models import SleepSession, SleepGoal

@admin.register(SleepSession)
class SleepSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "start", "end", "duration_hours", "quality", "awakenings", "meets_goal")
    list_filter = ("user", "quality", "start")
    search_fields = ("user__username", "notes", "tags")

@admin.register(SleepGoal)
class SleepGoalAdmin(admin.ModelAdmin):
    list_display = ("user", "target_hours", "target_bedtime", "target_waketime", "updated_at")
