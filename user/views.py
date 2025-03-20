from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth.views import LoginView
from .forms import *
from .models import *
from django.urls import reverse_lazy
from django.urls import reverse
from .helpers import create_notification
from django.views.generic import ListView, View


class Home(TemplateView):
    template_name = "user/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['announcements'] = Announcement.objects.order_by('-created_at')[:5]
        context['testimonials'] = Testimonial.objects.all().order_by('-created_at')
        return context
    


class SignupView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        form = SignupForm()
        return render(request, "user/register.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.POST)
        
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"]
            )
            user.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect("login")
        messages.error(request, "Unable to create account. Try again")
        return render(request, "user/register.html", {"form": form})
        
class SigninView(LoginView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, "user/login.html")

    def post(self, request, *args, **kwargs):
        try:
            username = request.POST.get("username")
            password = request.POST.get("password")
            
            next_url = request.POST.get("next") or request.GET.get("next") or "home"

            if not username or not password:
                messages.error(request, "All fields required")
                return redirect("login")

            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Successfully logged in.")
                if not UserProfile.objects.filter(user=user).exists():
                    return redirect("create_profile")
                return redirect(next_url) if next_url else redirect("home")
            else:
                messages.error(request, "Invalid Credentials. Try again")
                return redirect("login")

        except Exception as e:
            messages.error(request, f"Unable to login. {str(e)}")
            return redirect("login")
        
class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Logged out successfully")
        return redirect("home")
    
class ProfileCreateView(LoginRequiredMixin, CreateView):
    template_name = "user/create_profile.html"
    form_class = UserProfileForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        print(self.request.FILES)
        form.instance.user = self.request.user
        messages.success(self.request, "Profile created successfully")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Unable to create profile. Check fields and try again")
        return self.render_to_response(self.get_context_data(form=form)) 


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "user/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["profile"] = UserProfile.objects.filter(user=self.request.user).first()
        return context
    
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "user/edit_profile.html"
    form_class = UserProfileForm
    success_url = reverse_lazy('profile')


    def get_object(self):
        return self.request.user.user_profile

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Profile updated successfully")
        create_notification(self.request.user, "user_update", "Your profile has been updated!", related_object=form.instance)
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Unable to update profile. Check fields and try again")
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user 
        return context
        
class UserProfileDetailView(DetailView):
    model = UserProfile
    template_name = "user/user_profile.html"
    context_object_name = "profile"
    
from django.views.generic.edit import FormView
class ContactUsView(FormView):
    template_name = "user/contact_us.html"
    form_class = ContactUsForm
    success_url = reverse_lazy('contact-us')

    def form_valid(self, form):
        form.save() 
        messages.success(self.request, "Your message has been sent successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error. Please check the form fields.")
        return super().form_invalid(form)

class PrivacyPolicy(TemplateView):
    template_name = 'user/privacy_policy.html'

class TermsAndConditionView(TemplateView):
    template_name = 'user/terms_and_conditions.html'


class NotificationView(LoginRequiredMixin, TemplateView ):
    template_name = "user/notifications.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unread_notifications = Notification.objects.filter(user=self.request.user, is_read=False).select_related("user").order_by("-created_at")
        read_notifications = Notification.objects.filter(user=self.request.user, is_read=True).select_related("user").order_by("-created_at")
        
        context["unread_notifications"] = unread_notifications
        context["read_notifications"] = read_notifications
        context["unread_count"] = unread_notifications.count()
        
        return context
    
    def post(self, request, *args, **kwargs):
        edit_type = request.POST.get("edit_type")

        if edit_type == 'mark_read':
            return self.markRead(request)
        elif edit_type == 'delete_notification':
            return self.deleteNotification(request)
        elif edit_type == "clear_notification":
            return self.clearNotification(request)
        elif edit_type == "mark_unread_all_read":
            return self.markAllUnreadNotification(request)
        else:
            messages.error(request, "Invalid type request")
            return redirect("notification")
        
        
    def markRead(self, request):
        try:
            notification_id = request.POST.get("notification_id")
            notification_view = request.POST.get("notification_view", '')

            if not notification_id:
                messages.error(request, "Invalid notification ID")
                return redirect('notification')
            notification = get_object_or_404(Notification, id=notification_id)
            notification.mark_as_read()
            if notification_view == 'redirect_true' and notification.link:
                return redirect(notification.link) 
            messages.success(request, "Notification marked as read")
            return redirect('notification')
        except Exception as e:
            messages.error(request, f"Error occurred while marking notification as read {str(e)}")
            return redirect("notification")
        
    def deleteNotification(self, request):
        try:
            notification_id = request.POST.get("notification_id")
            if not notification_id:
                messages.error(request, "Invalid notification ID")
                return redirect("notification")
            notification = get_object_or_404(Notification, id=notification_id)
            notification.delete()
            messages.success(request, "Notification deleted successfully")
            return redirect("notification")
        except Exception as e:
            messages.error(request, f"Error occurred while deleting notification {str(e)}")
            return redirect("notification")
        
    def clearNotification(self, request):
        try:
            notification_type = request.POST.get("notification_type")

            if notification_type == "read_notification":
                Notification.objects.filter(is_read=True).delete()
                messages.success(request, "All read notifications cleared successfully.")

            elif notification_type == "unread_notification":
                Notification.objects.filter(is_read=False).delete()
                messages.success(request, "All unread notifications cleared successfully.")

            else:
                messages.error(request, "Invalid notification type.")

            return redirect("notification")

        except Exception as e:
            messages.error(request, f"Error occurred while clearing notifications: {str(e)}")
            return redirect("notification")
        
    def markAllUnreadNotification(self, request):
        try:
            Notification.objects.filter(is_read=False).update(is_read=True)
            
            messages.success(request, "All unread notifications marked as read successfully.")
            return redirect("notification")

        except Exception as e:
            messages.error(request, f"Error occurred while marking unread notifications as read: {str(e)}")
            return redirect("notification")

from django.utils.timezone import now
from django.utils.timezone import localtime
from django.utils.timezone import localtime
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime

class LoginHistoryView(LoginRequiredMixin, ListView):
    model = LoginHistory
    template_name = 'user/login_history.html'
    context_object_name = 'login_records'

    def get_queryset(self):
        return LoginHistory.objects.filter(user=self.request.user).order_by('-timestamp')

    def get_active_sessions(self):
        active_sessions = []
        sessions = Session.objects.filter(expire_date__gte=now())

        for session in sessions:
            session_data = session.get_decoded()
            user_id = session_data.get('_auth_user_id')

            if str(self.request.user.id) == str(user_id):
                last_activity = session_data.get('last_activity')

                if last_activity:
                    last_activity = parse_datetime(last_activity)
                    if last_activity:
                        last_activity = localtime(last_activity)
                is_active = bool(last_activity and (now() - last_activity) < timedelta(minutes=30))

                active_sessions.append({
                    "session_key": session.session_key,
                    "last_activity": last_activity.strftime('%Y-%m-%d %H:%M:%S') if last_activity else "Unknown",
                    "device": session_data.get('device', 'Unknown Device'),
                    "operating_system": session_data.get('operating_system', 'Unknown OS'),
                    "is_active": is_active,
                })

        return active_sessions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_sessions'] = self.get_active_sessions()
        return context
    
class LogoutSessionView(LoginRequiredMixin, View):
    def post(self, request, session_key, *args, **kwargs):
        if not session_key:
            messages.error(request, "Invalid session key.")
            return redirect('login_history')

        try:
            session = Session.objects.get(session_key=session_key)
            session.delete()

            messages.success(request, "Session successfully logged out.")
        except Session.DoesNotExist:
            messages.error(request, "Session not found or already expired.")

        return redirect('login_history')

class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "user/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user 
        return context

from django.urls import reverse_lazy

class NotificationPreferencesView(LoginRequiredMixin, UpdateView):
    model = NotificationPreferences
    form_class = NotificationPreferencesForm
    template_name = "user/notification_settings.html"
    success_url = reverse_lazy('settings')

    def get_object(self, queryset=None):
        obj, created = NotificationPreferences.objects.get_or_create(user=self.request.user)
        return obj
    def form_valid(self, form):
        messages.success(self.request, "Notification preferences updated successfully!")
        return super().form_valid(form)

class AccountManagementView(LoginRequiredMixin, TemplateView):
    template_name = "user/account_management.html"

class DeleteAccountView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        messages.warning(request, "Your account has been deleted.")
        user.delete()
        logout(request)
        return redirect('home')
    
class FAQView(TemplateView):
    template_name = "user/faq.html"