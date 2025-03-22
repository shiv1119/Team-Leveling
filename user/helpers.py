from django.utils.timezone import now
import re
from .models import Notification, NotificationPreferences

def create_notification(user, notification_type, message, related_object=None):
    
    notification_preferences = NotificationPreferences.objects.get(user=user)

    if notification_preferences.in_app_notification:
        existing_notification = Notification.objects.filter(
            user=user,
            is_read=False
        ).filter(message__startswith=message.split(" (")[0]).first() 

        if existing_notification:
            match = re.search(r"\((\d+) updates\)", existing_notification.message)
            count = int(match.group(1)) + 1 if match else 2  

            existing_notification.message = f"{message.split(' (')[0]} ({count} updates)"
            existing_notification.created_at = now()  
            existing_notification.notification_type = notification_type
            if related_object:
                existing_notification.related_object_id = str(related_object.id)
                existing_notification.related_model = related_object.__class__.__name__
                existing_notification.link = get_notification_link(notification_type, related_object)

            existing_notification.save()

        else:
            notification = Notification(
                user=user,
                notification_type=notification_type,
                message=message
            )

            if related_object:
                notification.related_object_id = str(related_object.id)
                notification.related_model = related_object.__class__.__name__
                notification.link = get_notification_link(notification_type, related_object)

            notification.save()
    else:
        pass

def get_notification_link(notification_type, related_object):
    if notification_type == "user_update":
        return "/user/profile/"
    elif notification_type == "account_security":
        return "/settings/security/"
    elif notification_type == "new_login":
        return "/login-history/"
    elif notification_type == "new_message":
        return "/messages/"
    elif notification_type == "contact" and related_object.__class__.__name__ == "ContactUs":
        return f"/admin/user/contactus/{related_object.id}/change/"
    elif notification_type == "review_received" and related_object.__class__.__name__ == "Feedback":
        return f"/feedback/{related_object.id}/"
    elif notification_type == "service_created" or notification_type == "service_updated":
        return f"/service/{related_object.id}/"
    elif notification_type == "service_updated":
        return f"/service/{related_object.id}/"
    elif notification_type == "service_deleted":
        return "/services/"
    elif notification_type == "working_hours":
        return f"/{related_object.id}/working-hours/create/"
    elif notification_type == "service_image":
        return f"/{related_object.id}/images/upload/"
    elif notification_type == "address_added" or notification_type == "address_updated" or notification_type == "service_image_added" or notification_type == "service_image_deleted":
        return f"/service/{related_object.id}/"
    elif notification_type == "social_link":
        return f"/{related_object.id}/social-links/create/"
    elif notification_type == "verification_pending" or notification_type == "verification_completed":
        return "/verification-status/"
    elif notification_type.startswith("booking_"):
        return f"/booking/{related_object.id}/"
    elif notification_type == "payment_success" or notification_type == "booking_payment_success":
        return "/payment/success/"
    elif notification_type == "payment_failed" or notification_type == "booking_payment_failed":
        return "/payment/failed/"
    return "/notifications/" 
