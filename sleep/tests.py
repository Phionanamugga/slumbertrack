from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from .models import SleepSession

class SleepBasics(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", password="pass12345")

    def test_duration(self):
        from datetime import timedelta
        start = timezone.now()
        end = start + timedelta(hours=7.5)
        s = SleepSession.objects.create(user=self.user, start=start, end=end, quality=4)
        self.assertAlmostEqual(s.duration_hours, 7.5, places=2)
