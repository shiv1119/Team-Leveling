from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils.text import slugify

User = get_user_model()


class ServiceType(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class SocialMediaLink(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    service = models.ForeignKey("Service", on_delete=models.CASCADE, related_name="social_media_links")
    platform = models.CharField(max_length=50)  # Example: "Facebook", "Instagram"
    url = models.URLField()

    def __str__(self):
        return f"{self.platform} - {self.service.title}"


class WorkingHour(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    service = models.ForeignKey("Service", on_delete=models.CASCADE, related_name="working_hours")
    day = models.CharField(max_length=15, choices=[
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ])
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return f"{self.day}: {self.open_time} - {self.close_time}"


class Service(models.Model):
    PRICE_TYPES = [
        ("fixed", "Fixed Price"),
        ("hourly", "Hourly Rate"),
        ("negotiable", "Negotiable"),
    ]

    CANCELLATION_POLICIES = [
        ("flexible", "Flexible - Full Refund"),
        ("moderate", "Moderate - Partial Refund"),
        ("strict", "Strict - No Refund"),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="services")
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, help_text="SEO-friendly URL")
    description = models.TextField()
    service_types = models.ManyToManyField(ServiceType, related_name="services")
    tags = models.CharField(max_length=255, blank=True, null=True)

    price_type = models.CharField(max_length=20, choices=PRICE_TYPES, default="fixed")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Discount in %")

    cancellation_policy = models.CharField(max_length=20, choices=CANCELLATION_POLICIES, default="moderate")

    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    views_count = models.BigIntegerField(default=0)
    response_time = models.CharField(max_length=50, blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to="service_verifications/", blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def discounted_price(self):
        if self.discount:
            return round(self.price - (self.price * (self.discount / 100)), 2)
        return self.price

    def average_rating(self):
        feedbacks = self.feedbacks.all()
        if feedbacks.exists():
            return round(sum(feedback.rating for feedback in feedbacks) / feedbacks.count(), 1)
        return 0.0
    
class Feedback(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    service = models.ForeignKey("services.Service", on_delete=models.CASCADE, related_name="feedbacks")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    title = models.CharField(max_length=255)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service.title} - {self.user.username} ({self.rating}⭐)"
    
class ServiceLocation(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    service = models.OneToOneField(Service, on_delete=models.CASCADE, related_name="location")
    street_address = models.CharField(max_length=255, blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    google_maps_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Location for {self.service.title}"


class ServiceImage(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="service_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.service.title}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    service = models.ForeignKey("Service", on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    payment_method = models.CharField(max_length=50, blank=True, null=True)
    is_refunded = models.BooleanField(default=False)

    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)

    address = models.TextField(blank=True, null=True, help_text="Required if service is home-based.")
    city = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    cancellation_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, help_text="Special instructions for the service provider")
    selected_service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, related_name="bookings", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(check=models.Q(start_time__lt=models.F("end_time")), name="valid_booking_time")
        ]

    def __str__(self):
        return f"Booking {self.id} - {self.service.title} by {self.user.username}"