from django.urls import path
from .views import *

urlpatterns = [
    path("create/", ServiceCreateView.as_view(), name="service_create"),
    path("<uuid:service_id>/working-hours/create/", WorkingHoursCreateView.as_view(), name="working_hours_create"),
    path("<uuid:service_id>/address/create/", AddressDetailsCreateView.as_view(), name="address_details_create"),
    path("<uuid:service_id>/address/<uuid:address_id>/update/", AddressDetailsUpdateView.as_view(), name="address_details_update"),
    path("<uuid:service_id>/social-links/create/", SocialLinksCreateView.as_view(), name="social_link_create"),
    path("social-links/<uuid:link_id>/delete/", SocialLinkDeleteView.as_view(), name="social_link_delete"),

    path("<uuid:service_id>/images/upload/", ServiceImageUploadView.as_view(), name="service_image_upload"),
    path("<uuid:service_id>/images/<uuid:image_id>/delete/", ServiceImageDeleteView.as_view(), name="service_image_delete"),

    path("<uuid:service_id>/update/", ServiceUpdateView.as_view(), name="service_update"),

    path("<uuid:service_id>/", ServiceDetailView.as_view(), name="service_detail"),
    path("working-hours/<uuid:working_hour_id>/delete/", WorkingHoursDeleteView.as_view(), name="working_hours_delete"),
    path("my-offered-services/", MyServicesView.as_view(), name="my-services"),
    path("service/<uuid:pk>/delete/", ServiceDeleteView.as_view(), name="service-delete"),
    path("service/<uuid:pk>/toggle-availability/", ToggleAvailabilityView.as_view(), name="toggle-availability"),
    path("service/<uuid:service_id>/", ServiceView.as_view(), name="service_view"),

    path("services/", AllServicesView.as_view(), name="all_services"),
    path("services/type/<uuid:service_type_id>/", FilteredServicesView.as_view(), name="filtered_services"),
    path("book/<uuid:service_id>/", BookingCreateView.as_view(), name="book_service"),
    path("received-bookings/", BookingListView.as_view(), name="booking_list"),
    path("book/<uuid:service_id>/", BookingCreateView.as_view(), name="book_service"),
    path("payment/success/", PaymentSuccessView.as_view(), name="payment_success"),
    path("booking/<uuid:pk>/", BookingDetailView.as_view(), name="booking_detail"),
    path("booking/<uuid:pk>/cancel/", CancelBookingView.as_view(), name="cancel_booking"),
    path("my-bookings/", MyBookedServicesView.as_view(), name="my_booked_services"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("feedback/<uuid:id>/", FeedbackDetailView.as_view(), name="feedback_detail"),
]
