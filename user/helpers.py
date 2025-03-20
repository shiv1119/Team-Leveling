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
                existing_notification.related_object_id = related_object.id
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
                notification.related_object_id = related_object.id
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
    elif notification_type == "new_message":
        return "/messages/"
    elif notification_type == "delivery_status":
        return f"/orders/{related_object.id}/tracking/"

    elif notification_type == "new_application":
        return f"/applicant/{related_object.id}/details/"
    elif notification_type == "renewal_application":
        return f"/applications/{related_object.id}/"
    elif notification_type == "reissue_application":
        return f"/applications/{related_object.id}/"
    elif notification_type == "lost_application":
        return f"/applications/{related_object.id}/"
    elif notification_type == "tatkal_application":
        return f"/applications/{related_object.id}/"
    elif notification_type == "application_under_review":
        return f"/applications/{related_object.id}/status/"
    elif notification_type == "application_approved":
        return f"/applications/{related_object.id}/status/"
    elif notification_type == "application_rejected":
        return f"/applications/{related_object.id}/status/"
    elif notification_type == "application_issued":
        return f"/applications/{related_object.id}/issued/"

    elif notification_type == "police_verification":
        return f"/verifications/{related_object.id}/police/"
    elif notification_type == "document_verification":
        return f"/verifications/{related_object.id}/documents/"
    elif notification_type == "background_check":
        return f"/verifications/{related_object.id}/background/"
    elif notification_type == "final_review":
        return f"/verifications/{related_object.id}/final/"
    elif notification_type == "criminal_record_check":
        return f"/verifications/{related_object.id}/criminal/"
    elif notification_type == "address_verification":
        return f"/verifications/{related_object.id}/address/"
    elif notification_type == "identity_verification":
        return f"/verifications/{related_object.id}/identity/"
    elif notification_type == "aadhaar_verification":
        return f"/verifications/{related_object.id}/aadhaar/"
    elif notification_type == "financial_status_verification":
        return f"/verifications/{related_object.id}/financial/"
    elif notification_type == "visa_clearance":
        return f"/verifications/{related_object.id}/visa/"
    elif notification_type == "blacklist_check":
        return f"/verifications/{related_object.id}/blacklist/"
    elif notification_type == "immigration_check":
        return f"/verifications/{related_object.id}/immigration/"

    return None
