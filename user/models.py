from django.db import models
from django.contrib.auth.models import User

INDIAN_STATES_UTS = [
    ("Andhra Pradesh", "Andhra Pradesh"),
    ("Arunachal Pradesh", "Arunachal Pradesh"),
    ("Assam", "Assam"),
    ("Bihar", "Bihar"),
    ("Chhattisgarh", "Chhattisgarh"),
    ("Goa", "Goa"),
    ("Gujarat", "Gujarat"),
    ("Haryana", "Haryana"),
    ("Himachal Pradesh", "Himachal Pradesh"),
    ("Jharkhand", "Jharkhand"),
    ("Karnataka", "Karnataka"),
    ("Kerala", "Kerala"),
    ("Madhya Pradesh", "Madhya Pradesh"),
    ("Maharashtra", "Maharashtra"),
    ("Manipur", "Manipur"),
    ("Meghalaya", "Meghalaya"),
    ("Mizoram", "Mizoram"),
    ("Nagaland", "Nagaland"),
    ("Odisha", "Odisha"),
    ("Punjab", "Punjab"),
    ("Rajasthan", "Rajasthan"),
    ("Sikkim", "Sikkim"),
    ("Tamil Nadu", "Tamil Nadu"),
    ("Telangana", "Telangana"),
    ("Tripura", "Tripura"),
    ("Uttar Pradesh", "Uttar Pradesh"),
    ("Uttarakhand", "Uttarakhand"),
    ("West Bengal", "West Bengal"),

    ("Andaman and Nicobar Islands", "Andaman and Nicobar Islands"),
    ("Chandigarh", "Chandigarh"),
    ("Dadra and Nagar Haveli and Daman and Diu", "Dadra and Nagar Haveli and Daman and Diu"),
    ("Delhi", "Delhi"),
    ("Jammu and Kashmir", "Jammu and Kashmir"),
    ("Ladakh", "Ladakh"),
    ("Lakshadweep", "Lakshadweep"),
    ("Puducherry", "Puducherry"),
]

ROLES_CHOICES = [
    ('customer', 'Customer'),
    ('service_provider', 'Service Provider'),
    ('admin', 'Admin'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    )
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLES_CHOICES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.get_role_display()}"



class Announcement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="testimonials")
    feedback = models.TextField()
    rating = models.IntegerField(default=5) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}⭐"
    
class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("user_update", "User Update"),
        ("system", "System Notification"),
        ("contact", "Contact"),
        ("payment_success", "Payment Successful"),
        ("payment_failed", "Payment Failed"),
        ("service_created", "Service Created"),
        ("service_updated", "Service Updated"),
        ("service_deleted", "Service Deleted"),
        ("working_hours_updated", "Working Hours Updated"),
        ("address_added", "Address Added"),
        ("address_updated", "Address Updated"),
        ("social_link_added", "Social Link Added"),
        ("social_link_updated", "Social Link Updated"),
        ("review_received", "New Review Received"),
        ("review_replied", "Review Replied"),
        ("rating_updated", "Rating Updated"),
        ("verification_pending", "Verification Pending"),
        ("verification_completed", "Verification Completed"),
        ("booking_created", "New Booking Created"),
        ("booking_confirmed", "Booking Confirmed"),
        ("booking_completed", "Booking Completed"),
        ("booking_canceled", "Booking Canceled"),
        ("booking_rescheduled", "Booking Rescheduled"),
        ("booking_payment_pending", "Booking Payment Pending"),
        ("booking_payment_success", "Booking Payment Successful"),
        ("booking_payment_failed", "Booking Payment Failed"),
        ("booking_refunded", "Booking Refunded"),
        ("booking_reminder", "Booking Reminder"),
        ("booking_updated", "Booking Updated"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    related_object_id = models.CharField(max_length=36, null=True, blank=True)
    related_model = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        recipient = self.user.username if self.user else "Unknown"
        return f"{recipient} - {self.get_notification_type_display()} - {self.created_at}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    @staticmethod
    def get_unread_count(user):
        return Notification.objects.filter(user=user, is_read=False).count()

    @staticmethod
    def get_unread_role_notifications(role):
        return Notification.objects.filter(role=role, is_read=False).count()


class NotificationPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    in_app_notification = models.BooleanField(default=True)
    edited_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Preferences"
    
from django.utils.timezone import now, timedelta
from django.contrib.sessions.models import Session

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    device = models.CharField(max_length=255, null=True, blank=True)
    operating_system = models.CharField(max_length=255, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    
    timestamp = models.DateTimeField(default=now) 
    last_activity = models.DateTimeField(default=now)  
    is_active_session = models.BooleanField(default=True) 

    city = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    @property
    def is_active(self):
        return Session.objects.filter(session_key=self.session_key).exists()

    def update_activity(self):
        self.last_activity = now()
        self.save(update_fields=['last_activity'])

    def check_activity(self):
        if now() - self.last_activity > timedelta(minutes=30):
            self.is_active_session = False
            self.save(update_fields=['is_active_session'])

    def __str__(self):
        status = "Active" if self.is_active else "Logged Out"
        return f"{self.user.username} - {self.timestamp} - {self.device} ({self.operating_system}) - {status}"