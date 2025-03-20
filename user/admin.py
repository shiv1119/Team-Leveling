from django.contrib import admin
from .models import *

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'date_of_birth', 'gender', 'created_at')
    search_fields = ('full_name', 'phone', 'user__username')
    list_filter = ('gender', 'created_at')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at') 
    search_fields = ('title', 'message')
    list_filter = ('created_at',)


class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'feedback')

admin.site.register(Testimonial, TestimonialAdmin)

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-created_at',)

admin.site.register(Notification)
admin.site.register(NotificationPreferences)