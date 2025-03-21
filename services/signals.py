from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Service
from user.models import UserProfile

@receiver(post_save, sender=Service)
def set_service_provider_role(sender, instance, created, **kwargs):

    if created:
        user_profile, created = UserProfile.objects.get_or_create(user=instance.user)
        if user_profile.role == 'customer': 
            user_profile.role = 'service_provider'
            user_profile.save()
