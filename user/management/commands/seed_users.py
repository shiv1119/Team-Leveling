from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Update all users to is_active=True if not already active, in batches"

    def handle(self, *args, **kwargs):
        batch_size = 50
        inactive_users = User.objects.filter(is_active=False)

        total_updated = 0
        while inactive_users.exists():
            batch = inactive_users[:batch_size]
            updated_count = batch.update(is_active=True)
            total_updated += updated_count
            inactive_users = User.objects.filter(is_active=False)  # Refresh query
            
        self.stdout.write(self.style.SUCCESS(f"✅ Updated {total_updated} inactive users to active!"))
