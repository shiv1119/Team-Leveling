from .models import Notification, Subscriber

def global_context(request):
    context = {
        "notification_count": 0,
        "subscribed": False
    }

    if request.user.is_authenticated:
        context["notification_count"] = Notification.objects.filter(user=request.user, is_read=False).count()
        context["subscribed"] = Subscriber.objects.filter(email=request.user.email, is_subscribed=True).exists()

    return context