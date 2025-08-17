from rest_framework import serializers
from .models import SleepSession, SleepGoal

class SleepSessionSerializer(serializers.ModelSerializer):
    duration_hours = serializers.FloatField(read_only=True)
    class Meta:
        model = SleepSession
        fields = ["id", "start", "end", "quality", "latency_minutes", "awakenings", "notes", "tags", "stages_json", "duration_hours"]

class SleepGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SleepGoal
        fields = ["target_hours", "target_bedtime", "target_waketime"]
