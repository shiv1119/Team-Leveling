from django.contrib import messages
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from user.helpers import create_notification
from django.contrib.auth.mixins import AccessMixin
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import logout
class RedirectAuthenticatedUserMixin(AccessMixin):
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request) 
            messages.info(request, "You have been logged out. Please reset your password.")
        return super().dispatch(request, *args, **kwargs)

from django.conf import settings

class CustomPasswordResetView(RedirectAuthenticatedUserMixin, PasswordResetView):
    template_name = "user/password_reset_form.html"
    email_template_name = "user/password_reset_email.html"
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        user_email = form.cleaned_data.get("email")
        users = list(form.get_users(user_email))

        if not users:
            return super().form_valid(form)

        for user in users:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            domain = settings.SITE_URL.rstrip("/")  # Ensuring no trailing slash

            context = {
                "user": user,
                "domain": domain,
                "uid": uid,
                "token": token,
            }

            html_message = render_to_string("user/password_reset_email.html", context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject="Reset Your Password",
                message=plain_message,
                from_email="greenarrow6499@gmail.com",
                recipient_list=[user.email],
                html_message=html_message,
            )

        messages.success(self.request, "If an account exists with this email, you will receive a password reset link shortly.")
        return HttpResponseRedirect(self.get_success_url())


class CustomPasswordResetDoneView(RedirectAuthenticatedUserMixin, PasswordResetDoneView):
    template_name = "user/password_reset_done.html"

class CustomPasswordResetConfirmView(RedirectAuthenticatedUserMixin, PasswordResetConfirmView):
    template_name = "user/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")

    def form_valid(self, form):
        messages.success(self.request, "Your password has been successfully reset!")
        user = user = form.user
        create_notification(user, "user_update", "Your password updated successfully!", related_object=user)
        return super().form_valid(form)

class CustomPasswordResetCompleteView(RedirectAuthenticatedUserMixin, PasswordResetCompleteView):
    template_name = "user/password_reset_complete.html"

