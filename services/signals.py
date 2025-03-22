from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from user.models import UserProfile
from user.helpers import create_notification

@receiver(post_save, sender=Service)
def set_service_provider_role(sender, instance, created, **kwargs):

    if created:
        user_profile, created = UserProfile.objects.get_or_create(user=instance.user)
        if user_profile.role == 'customer': 
            user_profile.role = 'service_provider'
            user_profile.save()

def send_email_notification(user, subject, template_name, context):
    context["site_url"] = settings.SITE_URL
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
    )

@receiver(post_save, sender=Service)
def service_created_or_updated(sender, instance, created, **kwargs):
    if created:
        message = f"Your service '{instance.title}' has been created successfully."
        subject = "Service Created Successfully"
        template = "services/emails/service_created.html"
        notification_type = "service_created"
    else:
        message = f"Your service '{instance.title}' has been updated."
        subject = "Service Updated Successfully"
        template = "services/emails/service_updated.html"
        notification_type = "service_updated"
    
    create_notification(instance.user, notification_type, message, instance)
    send_email_notification(instance.user, subject, template, {"service": instance, "site_url": settings.SITE_URL})


@receiver(post_delete, sender=Service)
def service_deleted(sender, instance, **kwargs):
    message = f"Your service '{instance.title}' has been deleted."
    create_notification(instance.user, "service_deleted", message, instance)
    send_email_notification(instance.user, "Service Deleted", "services/emails/service_deleted.html", {"service": instance})

@receiver(post_save, sender=Feedback)
def feedback_notification(sender, instance, created, **kwargs):
    if created:
        service_owner = instance.service.user 
        feedback_user = instance.user

        create_notification(
            user=feedback_user,
            notification_type="review_received",
            message=f"Your feedback on {instance.service.title} has been submitted.",
            related_object=instance
        )

        if service_owner != feedback_user: 
            create_notification(
                user=service_owner,
                notification_type="review_received",
                message=f"You received a new feedback on your service {instance.service.title}.",
                related_object=instance
            )

@receiver(post_save, sender=ServiceLocation)
def service_location_notification(sender, instance, created, **kwargs):
    service_owner = instance.service.user 
    
    if created:
        message = f"A location has been added for your service: {instance.service.title}."
        notification_type = "address_added"
    else:
        message = f"The location for your service {instance.service.title} has been updated."
        notification_type = "address_updated"

    create_notification(
        user=service_owner,
        notification_type=notification_type,
        message=message,
        related_object=instance.service 
    )
@receiver(post_save, sender=ServiceImage)
def service_image_added_notification(sender, instance, created, **kwargs):
    service_owner = instance.service.user 
    
    if created:
        message = f"A new image has been added to your service: {instance.service.title}."
        notification_type = "service_image"

        create_notification(
            user=service_owner,
            notification_type=notification_type,
            message=message,
            related_object=instance.service 
        )

@receiver(post_delete, sender=ServiceImage)
def service_image_deleted_notification(sender, instance, **kwargs):
    service_owner = instance.service.user  

    message = f"An image has been removed from your service: {instance.service.title}."
    notification_type = "service_image"

    create_notification(
        user=service_owner,
        notification_type=notification_type,
        message=message,
        related_object=instance.service 
    )

@receiver(post_save, sender=WorkingHour)
def working_hour_added_notification(sender, instance, created, **kwargs):
    if created:
        service_owner = instance.service.user  
        message = f"Working hours have been added for {instance.service.title} on {instance.day}."
        
        create_notification(
            user=service_owner,
            notification_type="working_hours",
            message=message,
            related_object=instance.service
        )

@receiver(post_delete, sender=WorkingHour)
def working_hour_deleted_notification(sender, instance, **kwargs):
    service_owner = instance.service.user  
    message = f"Working hours for {instance.service.title} on {instance.day} have been removed."

    create_notification(
        user=service_owner,
        notification_type="working_hours",
        message=message,
        related_object=instance.service
    )

def send_booking_email(user, subject, template_name, context):
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
from django.urls import reverse
@receiver(post_save, sender=Booking)
def send_booking_emails_and_notifications(sender, instance, created, **kwargs):
    service_booker = instance.user
    service_owner = instance.service.user

    context = {
        "booking": instance,
        "user": service_booker,
        "service": instance.service,
        "booking_url": f"{settings.SITE_URL}/booking/{instance.id}/",
        "support_url" : f"{settings.SITE_URL}{reverse('contact-us')}/"
    }

    if created:
        send_booking_email(service_booker, "Booking Confirmation", "services/emails/booking_confirmation.html", context)
        send_booking_email(service_owner, "New Booking Received", "services/emails/booking_confirmation.html", context)

        create_notification(service_booker, "booking_created", "Your booking has been confirmed.", instance)
        create_notification(service_owner, "booking_received", f"New booking for {instance.service.title}.", instance)

    else:
        if instance.status == "confirmed":
            send_booking_email(service_booker, "Booking Confirmed", "services/emails/booking_status_update.html", context)
            create_notification(service_booker, "booking_confirmed", "Your booking has been confirmed!", instance)
        elif instance.status == "completed":
            send_booking_email(service_booker, "Booking Completed", "services/emails/booking_status_update.html", context)
            create_notification(service_booker, "booking_completed", "Your booking has been completed!", instance)
        elif instance.status == "canceled":
            send_booking_email(service_booker, "Booking Canceled", "services/emails/booking_cancellation.html", context)
            create_notification(service_booker, "booking_canceled", "Your booking has been canceled!", instance)

        if instance.payment_status == "paid":
            send_booking_email(service_booker, "Payment Received", "services/emails/booking_payment_update.html", context)
            create_notification(service_booker, "booking_payment_success", "Your payment has been received!", instance)
        elif instance.payment_status == "failed":
            send_booking_email(service_booker, "Payment Failed", "services/emails/booking_payment_update.html", context)
            create_notification(service_booker, "booking_payment_failed", "Your payment failed!", instance)
        elif instance.payment_status == "refunded":
            send_booking_email(service_booker, "Refund Issued", "services/emails/booking_payment_update.html", context)
            create_notification(service_booker, "booking_refunded", "Your refund has been processed!", instance)