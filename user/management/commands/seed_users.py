from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from user.models import NotificationPreferences

User = get_user_model()

class Command(BaseCommand):
    help = "Create notification preferences for all users if not exists"

    def handle(self, *args, **kwargs):
        users_without_prefs = User.objects.filter(notification_preferences__isnull=True)
        total_created = 0

        for user in users_without_prefs:
            NotificationPreferences.objects.create(user=user)
            total_created += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Created notification preferences for {total_created} users!"))
