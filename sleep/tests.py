from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from sleep.models import SleepSession, SleepGoal
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone

class SleepAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', 
            password='otherpassword123'
        )
        # Ensure no existing goal to avoid unique constraint issues
        SleepGoal.objects.filter(user=self.user).delete()
        self.sleep_data = {
            'start': '2024-01-01T22:00:00Z',
            'end': '2024-01-02T06:00:00Z',
            'quality': 4,
            'latency_minutes': 15,
            'awakenings': 2,
            'notes': 'Test sleep entry'
        }

    # --- Basic CRUD Tests ---
    
    def test_create_sleep_entry(self):
        """Test creating a new sleep entry"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('session-list'),
            self.sleep_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SleepSession.objects.count(), 1)
        self.assertEqual(SleepSession.objects.get().user, self.user)

    def test_retrieve_sleep_entries(self):
        """Test retrieving sleep entries"""
        session = SleepSession.objects.create(
            user=self.user,
            start='2024-01-01T22:00:00Z',
            end='2024-01-02T06:00:00Z',
            quality=4
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('session-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], session.id)

    def test_update_sleep_entry(self):
        """Test updating a sleep entry"""
        session = SleepSession.objects.create(
            user=self.user,
            start='2024-01-01T22:00:00Z',
            end='2024-01-02T06:00:00Z',
            quality=4
        )
        
        self.client.force_authenticate(user=self.user)
        update_data = {'quality': 5, 'notes': 'Updated notes'}
        response = self.client.patch(
            reverse('session-detail', kwargs={'pk': session.id}),
            update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        session.refresh_from_db()
        self.assertEqual(session.quality, 5)
        self.assertEqual(session.notes, 'Updated notes')

    def test_delete_sleep_entry(self):
        """Test deleting a sleep entry"""
        session = SleepSession.objects.create(
            user=self.user,
            start='2024-01-01T22:00:00Z',
            end='2024-01-02T06:00:00Z',
            quality=4
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse('session-detail', kwargs={'pk': session.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SleepSession.objects.count(), 0)

    # --- Authentication & Authorization Tests ---

    def test_unauthenticated_access(self):
        response = self.client.get(reverse('session-list'))
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_user_cannot_access_other_users_data(self):
        """Test that users can only access their own data"""
        session = SleepSession.objects.create(
            user=self.other_user,
            start='2024-01-01T22:00:00Z',
            end='2024-01-02T06:00:00Z',
            quality=4
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse('session-detail', kwargs={'pk': session.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Validation Tests ---
    
    def test_invalid_sleep_session_start_after_end(self):
        """Test validation for start time after end time"""
        self.client.force_authenticate(user=self.user)
        invalid_data = self.sleep_data.copy()
        invalid_data['start'] = '2024-01-02T07:00:00Z'
        invalid_data['end'] = '2024-01-02T06:00:00Z'
        
        response = self.client.post(
            reverse('session-list'),
            invalid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end', response.data)

    def test_negative_quality_rating(self):
        """Test validation for quality rating"""
        self.client.force_authenticate(user=self.user)
        invalid_data = self.sleep_data.copy()
        invalid_data['quality'] = -1
        
        response = self.client.post(
            reverse('session-list'),
            invalid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Sleep Goal Tests ---
    

    def test_negative_target_hours(self):
        """Test validation for negative target hours"""
        self.client.force_authenticate(user=self.user)
        invalid_data = {
            'target_hours': -5.0,
            'target_bedtime': '22:30:00',
            'target_waketime': '07:00:00'
        }
        
        response = self.client.post(
            reverse('goal-list'),
            invalid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('target_hours', response.data)

    # --- Pagination Tests ---
    
    def test_pagination(self):
        """Test that pagination works correctly"""
        for i in range(15):
            SleepSession.objects.create(
                user=self.user,
                start=f'2024-01-{i+1:02d}T22:00:00Z',
                end=f'2024-01-{i+1:02d}T06:00:00Z',
                quality=4
            )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('session-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 10)
        
        response = self.client.get(reverse('session-list') + '?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

    # --- Filtering Tests ---
    
    def test_filter_by_date_range(self):
        """Test filtering sleep sessions by date range"""
        dates = [
            ('2024-01-01T22:00:00Z', '2024-01-02T06:00:00Z'),
            ('2024-01-05T22:00:00Z', '2024-01-06T06:00:00Z'),
            ('2024-01-10T22:00:00Z', '2024-01-11T06:00:00Z'),
        ]
        
        for start, end in dates:
            SleepSession.objects.create(
                user=self.user,
                start=start,
                end=end,
                quality=4
            )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse('session-list') + '?start_date=2024-01-04&end_date=2024-01-07'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    # --- Edge Case Tests ---
    
    def test_empty_notes(self):
        """Test creating session with empty notes"""
        self.client.force_authenticate(user=self.user)
        data = self.sleep_data.copy()
        data['notes'] = ''
        
        response = self.client.post(
            reverse('session-list'),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_missing_optional_fields(self):
        """Test creating session with missing optional fields"""
        self.client.force_authenticate(user=self.user)
        minimal_data = {
            'start': '2024-01-01T22:00:00Z',
            'end': '2024-01-02T06:00:00Z',
            'quality': 4
        }
        
        response = self.client.post(
            reverse('session-list'),
            minimal_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


