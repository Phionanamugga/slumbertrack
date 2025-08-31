from rest_framework import serializers
from .models import SleepSession, SleepGoal
from datetime import datetime, time, timedelta

class SleepSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for SleepSession model.

    - Includes read-only duration_hours calculated from start and end times.
    - Validates that start is before end.
    - Ensures quality, latency_minutes, and awakenings are non-negative.
    """
    duration_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = SleepSession
        fields = ["id", "start", "end", "quality", "latency_minutes", "awakenings", "notes", "tags", "stages_json", "duration_hours"]

    def validate(self, data):
        """Validate the entire data set for consistency."""
        if data.get('start') and data.get('end') and data['start'] >= data['end']:
            raise serializers.ValidationError({"end": "End time must be after start time."})
        if data.get('quality') is not None and data['quality'] < 0:
            raise serializers.ValidationError({"quality": "Quality must be non-negative."})
        if data.get('latency_minutes') is not None and data['latency_minutes'] < 0:
            raise serializers.ValidationError({"latency_minutes": "Latency minutes must be non-negative."})
        if data.get('awakenings') is not None and data['awakenings'] < 0:
            raise serializers.ValidationError({"awakenings": "Awakenings must be non-negative."})
        return data

    def to_representation(self, instance):
        """Customize output representation to ensure datetime fields are ISO formatted."""
        ret = super().to_representation(instance)
        if 'start' in ret:
            ret['start'] = instance.start.isoformat() if instance.start else None
        if 'end' in ret:
            ret['end'] = instance.end.isoformat() if instance.end else None
        return ret

class SleepGoalSerializer(serializers.ModelSerializer):
    """
    Serializer for SleepGoal model.

    - Validates that target_hours is positive.
    - Ensures target_bedtime is before target_waketime, considering next day.
    """
    class Meta:
        model = SleepGoal
        fields = ["target_hours", "target_bedtime", "target_waketime"]

    def validate(self, data):
        """Validate the entire data set for consistency."""
        if data.get('target_hours') is not None and data['target_hours'] <= 0:
            raise serializers.ValidationError({"target_hours": "Target hours must be a positive number."})
        if data.get('target_bedtime') and data.get('target_waketime'):
            # Ensure inputs are strings and convert to time objects
            bedtime_str = data['target_bedtime']
            waketime_str = data['target_waketime']
            if not isinstance(bedtime_str, str) or not isinstance(waketime_str, str):
                raise serializers.ValidationError({"target_bedtime": "Time fields must be strings in HH:MM:SS format."})
            bedtime = datetime.strptime(bedtime_str, '%H:%M:%S').time()
            waketime = datetime.strptime(waketime_str, '%H:%M:%S').time()
            # Compare with next day consideration
            if bedtime > waketime:
                # Assume waketime is the next day
                waketime_dt = datetime.combine(datetime.now().date(), waketime) + timedelta(days=1)
                bedtime_dt = datetime.combine(datetime.now().date(), bedtime)
                if bedtime_dt >= waketime_dt:
                    raise serializers.ValidationError({"target_waketime": "Wake time must be after bed time, considering next day."})
            elif bedtime >= waketime:
                raise serializers.ValidationError({"target_waketime": "Wake time must be after bed time."})
        return data

    def to_representation(self, instance):
        """Customize output representation to ensure time fields are ISO formatted."""
        ret = super().to_representation(instance)
        if 'target_bedtime' in ret:
            ret['target_bedtime'] = instance.target_bedtime.strftime('%H:%M:%S') if instance.target_bedtime else None
        if 'target_waketime' in ret:
            ret['target_waketime'] = instance.target_waketime.strftime('%H:%M:%S') if instance.target_waketime else None
        return ret