from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user
from user.models import UserProfile
from time import sleep

def test_update_activity(self):
    old_timestamp = self.login_history.last_activity
    sleep(0.01) 
    self.login_history.update_activity()
    updated_login_history = LoginHistory.objects.get(id=self.login_history.id)
    
    self.assertNotEqual(updated_login_history.last_activity, old_timestamp)

class AuthViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")

    def test_register_view(self):
        response = self.client.post(reverse("register"), {
            "username": "newuser",
            "password1": "Test@1234",
            "password2": "Test@1234",
            "email": "newuser@example.com"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_view(self):
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 302)
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 302)
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_logout_view(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from django.contrib.sessions.models import Session
from user.models import UserProfile, Notification, NotificationPreferences, LoginHistory

class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.profile = UserProfile.objects.create(
            user=self.user,
            full_name="Test User",
            phone="1234567890",
            date_of_birth="2000-01-01",
            gender="Male",
            address="Test Address",
            city="Test City",
            state="Test State",
            zip_code="123456",
            country="Test Country",
            role="customer"
        )

    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, "testuser")
        self.assertEqual(self.profile.full_name, "Test User")

    def test_role_display(self):
        self.assertEqual(self.profile.get_role_display(), "Customer")

class NotificationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="notifyuser", password="password123")
        self.notification = Notification.objects.create(
            user=self.user,
            notification_type="user_update",
            message="Your profile has been updated.",
            is_read=False
        )

    def test_notification_creation(self):
        self.assertEqual(self.notification.user.username, "notifyuser")
        self.assertEqual(self.notification.get_notification_type_display(), "User Update")

    def test_mark_as_read(self):
        self.notification.mark_as_read()
        self.assertTrue(self.notification.is_read)

    def test_get_unread_count(self):
        unread_count = Notification.get_unread_count(self.user)
        self.assertEqual(unread_count, 1)


class NotificationPreferencesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.preferences, created = NotificationPreferences.objects.get_or_create(user=self.user)

    def test_default_preferences(self):
        self.assertTrue(self.preferences.email_notifications)
        self.assertTrue(self.preferences.sms_notifications)
        self.assertTrue(self.preferences.push_notifications)
        self.assertTrue(self.preferences.in_app_notification)

    def test_preference_update(self):
        self.preferences.email_notifications = False
        self.preferences.save()
        updated_preferences = NotificationPreferences.objects.get(user=self.user)
        self.assertFalse(updated_preferences.email_notifications)


class LoginHistoryTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="historyuser", password="password123")
        self.login_history = LoginHistory.objects.create(
            user=self.user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            device="Laptop",
            operating_system="Windows",
            session_key="abc123"
        )

    def test_login_history_creation(self):
        self.assertEqual(self.login_history.user.username, "historyuser")
        self.assertEqual(self.login_history.ip_address, "192.168.1.1")

    def test_check_activity(self):
        self.login_history.last_activity = now() - timedelta(minutes=31)
        self.login_history.check_activity()
        self.assertFalse(self.login_history.is_active_session)

    def test_is_active(self):
        session = Session.objects.create(session_key="abc123", expire_date=now() + timedelta(days=1))
        self.assertTrue(self.login_history.is_active)

