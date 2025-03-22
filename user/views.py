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
from django.contrib.auth.views import LoginView
from .forms import *
from .models import *
from django.urls import reverse_lazy
from .helpers import create_notification
from django.views.generic import ListView, View
from services.models import Service
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.generic import FormView, View
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views import View
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.conf import settings


class Home(TemplateView):
    template_name = "user/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['announcements'] = Announcement.objects.order_by('-created_at')[:5]
        context['testimonials'] = Testimonial.objects.all().order_by('-created_at')[:5]
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
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data["username"],
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password1"]
                )
                user.is_active = False  
                current_site = get_current_site(request)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                activation_link = f"{settings.SITE_URL}/activate/{uid}/{token}/"

                subject = "Activate Your Account"
                html_message = render_to_string("user/activation_email.html", {
                    "user": user,
                    "activation_link": activation_link
                })
                plain_message = strip_tags(html_message)  
                email = EmailMultiAlternatives(subject, plain_message, "your-email@gmail.com", [user.email])
                email.attach_alternative(html_message, "text/html")
                email.send()

                messages.success(request, "A verification email has been sent to your email. Please check your inbox.")
                return redirect("login")
            except IntegrityError:
                messages.error(request, "Username or email already exists.")
            except Exception:
                messages.error(request, "An error occurred. Please try again.")

        return render(request, "user/register.html", {"form": form})

class ActivateAccountView(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))  # Decode user ID
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):  # Validate token
                user.is_active = True
                user.save()
                messages.success(request, "Your account has been activated successfully! You can now log in.")
                return redirect("login")
            else:
                messages.error(request, "The activation link is invalid or has expired.")
                return redirect("register")
        except (User.DoesNotExist, ValueError, TypeError):
            messages.error(request, "The activation link is invalid.")
            return redirect("register")

from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from user.models import UserProfile

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
                messages.error(request, "All fields are required.")
                return redirect("login")

            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    messages.error(request, "Your account is not activated. Please check your email for the activation link.")
                    return redirect("login")

                login(request, user)
                messages.success(request, "Successfully logged in.")
                
                if not UserProfile.objects.filter(user=user).exists():
                    return redirect("create_profile")

                return redirect(next_url) if next_url else redirect("home")

            messages.error(request, "Invalid credentials. Please try again.")
            return redirect("login")
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
            return redirect("login")

        
class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            logout(request)
            messages.success(request, "Logged out successfully")
        except Exception:
            messages.error(request, "An error occurred while logging out. Please try again.")
        return redirect("home")

class ProfileCreateView(LoginRequiredMixin, CreateView):
    template_name = "user/create_profile.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            messages.success(self.request, "Profile created successfully")
            return super().form_valid(form)
        except Exception:
            messages.error(self.request, "An error occurred while creating the profile. Please try again.")
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, "Unable to create profile. Check fields and try again.")
        return self.render_to_response(self.get_context_data(form=form))

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "user/profile.html"

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["user"] = self.request.user
            context["profile"] = UserProfile.objects.filter(user=self.request.user).first()
            return context
        except Exception:
            messages.error(self.request, "An error occurred while loading the profile.")
            return {}

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "user/edit_profile.html"
    form_class = UserProfileUpdateForm
    success_url = reverse_lazy("profile")

    def get_object(self):
        try:
            return self.request.user.user_profile
        except UserProfile.DoesNotExist:
            messages.error(self.request, "Profile does not exist.")
            return None
        except Exception:
            messages.error(self.request, "An error occurred while retrieving the profile.")
            return None

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            print(self.request.POST)
            if "profile_photo" in self.request.FILES:
                form.instance.profile_photo = self.request.FILES["profile_photo"]
            form.save()
            messages.success(self.request, "Profile updated successfully")
            return super().form_valid(form)
        except Exception:
            messages.error(self.request, "An error occurred while updating the profile.")
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, "Unable to update profile. Check fields and try again.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["user"] = self.request.user
            return context
        except Exception:
            messages.error(self.request, "An error occurred while loading profile data.")
            return {}
    
from django.db.models import Count,Avg
from django.db.models.functions import Round

class UserProfileDetailView(DetailView):
    model = UserProfile
    template_name = "user/user_profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        services_with_reviews = Service.objects.filter(user=profile.user).annotate(
            review_count=Count("feedbacks"),
            average_rating=Round(Avg("feedbacks__rating"), 1)
        )

        context["services"] = services_with_reviews
        return context

    
    
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
    template_name = "user/login_history.html"
    context_object_name = "login_records"

    def get_queryset(self):
        try:
            return LoginHistory.objects.filter(user=self.request.user).order_by("-timestamp")
        except Exception:
            messages.error(self.request, "An error occurred while retrieving login history.")
            return LoginHistory.objects.none()

    def get_active_sessions(self):
        try:
            active_sessions = []
            sessions = Session.objects.filter(expire_date__gte=now())

            for session in sessions:
                try:
                    session_data = session.get_decoded()
                    user_id = session_data.get("_auth_user_id")

                    if str(self.request.user.id) == str(user_id):
                        last_activity = session_data.get("last_activity")
                        if last_activity:
                            last_activity = parse_datetime(last_activity)
                            if last_activity:
                                last_activity = localtime(last_activity)

                        is_active = bool(last_activity and (now() - last_activity) < timedelta(minutes=30))

                        active_sessions.append({
                            "session_key": session.session_key,
                            "last_activity": last_activity.strftime('%Y-%m-%d %H:%M:%S') if last_activity else "Unknown",
                            "device": session_data.get("device", "Unknown Device"),
                            "operating_system": session_data.get("operating_system", "Unknown OS"),
                            "is_active": is_active,
                        })
                except Exception:
                    continue

            return active_sessions
        except Exception:
            messages.error(self.request, "An error occurred while retrieving active sessions.")
            return []

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["active_sessions"] = self.get_active_sessions()
            return context
        except Exception:
            messages.error(self.request, "An error occurred while loading login history.")
            return {}
    
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

from django.db.models import Q
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from services.models import Service, ServiceLocation

User = get_user_model()

class GlobalSearchView(TemplateView):
    template_name = "services/search_result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        
        if query:
            services = Service.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query) | Q(user__username__icontains=query)
            )
            
            users = User.objects.filter(
                Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )
        else:
            services = []
            users = []

        context["services"] = services
        context["users"] = users
        context["query"] = query
        return context


class ImageUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if "image" in request.FILES:
            user_profile = request.user.user_profile
            user_profile.profile_photo = request.FILES["image"]
            user_profile.save()
            messages.success(request, "Profile image updated successfully!")
        else:
            messages.error(request, "No image selected. Please choose an image.")

        return redirect("profile")