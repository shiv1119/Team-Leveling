from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import NotificationPreferences
import requests
import re
import user_agents
from django.utils.timezone import now
from django.contrib.sessions.models import Session
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from .models import LoginHistory

@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    if created:
        NotificationPreferences.objects.create(user=instance, in_app_notification=True)

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def get_location(ip):
    try:
        response = requests.get(f"https://ipwho.is/{ip}", timeout=5)
        data = response.json()
        if data.get("success"):
            return {
                "city": data.get("city", "Unknown"),
                "region": data.get("region", "Unknown"),
                "country": data.get("country", "Unknown"),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
            }
    except requests.RequestException:
        pass 
    return None

def extract_device_name(user_agent, user_agent_string):
    if user_agent.is_mobile:
        return detect_mobile_model(user_agent, user_agent_string)
    elif user_agent.is_tablet:
        return detect_tablet_model(user_agent, user_agent_string)
    elif user_agent.is_pc:
        return detect_pc_brand(user_agent_string)
    return "Unknown Device"

def detect_mobile_model(user_agent, user_agent_string):
    model = user_agent.device.family
    if not model or model == "Generic Smartphone":
        model = extract_model_from_ua(user_agent_string)
    return f"{model} (Mobile)" if model else "Unknown Mobile"

def detect_tablet_model(user_agent, user_agent_string):
    model = user_agent.device.family
    if not model or model == "Generic Tablet":
        model = extract_model_from_ua(user_agent_string)
    return f"{model} (Tablet)" if model else "Unknown Tablet"

def detect_pc_brand(user_agent_string):
    """Detect PC brand based on user-agent string."""
    device_patterns = [
        (r"MSI", "MSI"), (r"Dell", "Dell"), (r"HP", "HP"),
        (r"Asus", "Asus"), (r"Lenovo", "Lenovo"), (r"Acer", "Acer"),
        (r"Macintosh", "Apple Mac"), (r"Mac OS X", "Apple Mac"),
    ]
    for pattern, brand in device_patterns:
        if re.search(pattern, user_agent_string, re.IGNORECASE):
            return brand
    return "PC"

def extract_model_from_ua(user_agent_string):
    """Extract mobile/tablet model from user-agent string."""
    device_patterns = [
        (r"iPhone\s([\d\w]+)", "iPhone {}"),
        (r"iPad; CPU OS ([\d_]+)", "iPad (iOS {})"),
        (r"SM-(\w+)", "Samsung Galaxy {}"),
        (r"GT-(\w+)", "Samsung Galaxy {}"),
        (r"Pixel\s([\d\w]+)", "Google Pixel {}"),
        (r"Redmi\s([\d\w]+)", "Xiaomi Redmi {}"),
        (r"Mi\s([\d\w]+)", "Xiaomi Mi {}"),
        (r"OnePlus\s([\d\w]+)", "OnePlus {}"),
        (r"Huawei\s([\d\w]+)", "Huawei {}"),
        (r"Fire\s([\d\w]+)", "Amazon Fire {}"),
    ]
    for pattern, format_str in device_patterns:
        match = re.search(pattern, user_agent_string, re.IGNORECASE)
        if match:
            return format_str.format(match.group(1))
    return None

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    user_agent_str = request.META.get("HTTP_USER_AGENT", "")
    user_agent = user_agents.parse(user_agent_str)
    os = f"{user_agent.os.family} {user_agent.os.version_string}" or "Unknown OS"
    device = extract_device_name(user_agent, user_agent_str)
    location = get_location(ip)  # Fetch location

    session_key = request.session.session_key
    request.session["device"] = device
    request.session["operating_system"] = os
    request.session["last_activity"] = now().isoformat()
    request.session.modified = True

    existing_record = LoginHistory.objects.filter(user=user, ip_address=ip, device=device).first()

    if existing_record:
        existing_record.timestamp = now()
        existing_record.session_key = session_key
        existing_record.city = location["city"] if location else "Unknown"
        existing_record.region = location["region"] if location else "Unknown"
        existing_record.country = location["country"] if location else "Unknown"
        existing_record.latitude = location["latitude"] if location else None
        existing_record.longitude = location["longitude"] if location else None
        existing_record.save()
    else:
        LoginHistory.objects.create(
            user=user, ip_address=ip, user_agent=user_agent_str,
            device=device, operating_system=os, session_key=session_key,
            city=location["city"] if location else "Unknown",
            region=location["region"] if location else "Unknown",
            country=location["country"] if location else "Unknown",
            latitude=location["latitude"] if location else None,
            longitude=location["longitude"] if location else None,
        )
