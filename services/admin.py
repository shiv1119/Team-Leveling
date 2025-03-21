from django.contrib import admin
from .models import *

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "price", "is_active", "is_available", "average_rating_display")
    list_filter = ("is_active", "is_available", "price_type", "cancellation_policy")
    search_fields = ("title", "user__username", "description", "tags")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")

    def average_rating_display(self, obj):
        return f"{obj.average_rating()} ⭐"
    average_rating_display.short_description = "Avg. Rating"

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("service", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("service__title", "user__username", "comment")
    readonly_fields = ("created_at",)
    
@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(SocialMediaLink)
class SocialMediaLinkAdmin(admin.ModelAdmin):
    list_display = ("service", "platform", "url")
    search_fields = ("service__title", "platform")


@admin.register(WorkingHour)
class WorkingHourAdmin(admin.ModelAdmin):
    list_display = ("service", "day", "open_time", "close_time")
    list_filter = ("day",)
    search_fields = ("service__title",)

from django.contrib import admin
from .models import ServiceLocation, ServiceImage

@admin.register(ServiceLocation)
class ServiceLocationAdmin(admin.ModelAdmin):
    list_display = ("service", "city", "state", "country", "postal_code")
    search_fields = ("service__title", "city", "state", "country")
    list_filter = ("country", "state", "city")


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ("service", "image", "uploaded_at")
    search_fields = ("service__title",)
    list_filter = ("uploaded_at",)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "service", "user", "status", "payment_status", "booking_date", "start_time", "end_time", "total_amount")
    list_filter = ("status", "payment_status", "booking_date", "service")
    search_fields = ("user__username", "service__title", "razorpay_order_id", "razorpay_payment_id")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "id")  # Add id to readonly_fields to prevent editing

    fieldsets = (
        ("Basic Info", {
            "fields": ("service", "user", "status", "payment_status", "total_amount")
        }),
        ("Payment Details", {
            "fields": ("razorpay_order_id", "razorpay_payment_id", "razorpay_signature", "payment_method", "is_refunded")
        }),
        ("Booking Time & Address", {
            "fields": ("booking_date", "start_time", "end_time", "address", "city", "pincode")
        }),
        ("Additional Info", {
            "fields": ("cancellation_reason", "notes", "selected_service_type")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def has_add_permission(self, request):
        return True 

    def has_change_permission(self, request, obj=None):
        return True 

    def has_delete_permission(self, request, obj=None):
        return True
