from django.urls import path
from .views import *


urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("sign-up/", SignupView.as_view(), name="register"),
    path("sign-in", SigninView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("user/create-profile/", ProfileCreateView.as_view(), name="create_profile"),
    path("user/profile/", ProfileView.as_view(), name="profile"),
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path("user/profile/update/", ProfileUpdateView.as_view(), name="update_profile"),
    path('contact-us/', ContactUsView.as_view(), name='contact-us'),
    path('privacy-policy/', PrivacyPolicy.as_view(), name='privacy-policy'),
    path('user/notifications/',NotificationView.as_view(), name="notification"),
    path('terms-and-conditions/', TermsAndConditionView.as_view(), name='terms-and-conditions'),
    path('login-history/', LoginHistoryView.as_view(), name='login_history'),
    path('logout-session/<str:session_key>/', LogoutSessionView.as_view(), name='logout_session'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('notifications-settings/', NotificationPreferencesView.as_view(), name='notification_settings'),
    path('settings/account/', AccountManagementView.as_view(), name='account_settings'),
    path('settings/account/delete/', DeleteAccountView.as_view(), name='delete_account'),
    path("faq/", FAQView.as_view(), name="faq"),
    path("search/", GlobalSearchView.as_view(), name="global_search"),
    path("activate/<uidb64>/<token>/", ActivateAccountView.as_view(), name="activate"),
    path("update-profile-image/", ImageUpdateView.as_view(), name="update_profile_image"),
]

