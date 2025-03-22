from django.shortcuts import render
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views.generic import View
from .forms import *
from .models import *
from user.helpers import create_notification

from django.urls import reverse

class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'services/forms/service_form.html'


    def form_valid(self, form):
        form.instance.user = self.request.user
        service = form.save()  
        address_details = ServiceLocation.objects.filter(service=service).exists()
        if address_details:
            return redirect(reverse("address_details_update", kwargs={"service_id": service.id, "address_id": address_details.id}))
        return redirect(reverse("address_details_create", kwargs={"service_id": service.id}))
    
    def form_invalid(self, form):
        messages.error(self.request, "Error, Check input details and try again")
        return self.render_to_response(self.get_context_data(form=form)) 

class WorkingHoursCreateView(LoginRequiredMixin, CreateView):
    model = WorkingHour
    form_class = WorkingHourForm
    template_name = 'services/forms/working_hours_form.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.service = get_object_or_404(Service, id=kwargs['service_id'])
            return super().dispatch(request, *args, **kwargs)
        except Exception:
            messages.error(request, "An error occurred while processing the request.")
            return redirect("some_error_page_or_fallback_url")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service"] = self.service
        context["service_id"] = self.service.id
        context["working_hours"] = WorkingHour.objects.filter(service=self.service)
        context["working_hour_form"] = self.get_form()
        context["address"] = ServiceLocation.objects.filter(service=self.service).exists()
        return context

    def form_valid(self, form):
        try:
            form.instance.service = self.service
            form.save()
            return redirect(reverse("working_hours_create", kwargs={"service_id": self.service.id}))
        except Exception:
            messages.error(self.request, "An error occurred while saving the working hours.")
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, "Error: Check input details and try again.")
        return self.render_to_response(self.get_context_data(form=form))


class AddressDetailsCreateView(LoginRequiredMixin, CreateView):
    model = ServiceLocation
    form_class = ServiceLocationForm
    template_name = 'services/forms/location_form.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.service = get_object_or_404(Service, id=kwargs['service_id'])
            return super().dispatch(request, *args, **kwargs)
        except Exception:
            messages.error(request, "An error occurred while processing the request.")
            return redirect("some_error_page_or_fallback_url")

    def form_valid(self, form):
        try:
            form.instance.service = self.service
            form.save()
            social_links = SocialMediaLink.objects.filter(service_id=self.service.id).first()
            if social_links:
                return redirect(reverse("links_update", kwargs={"service_id": self.service.id}))
            return redirect(reverse("social_link_create", kwargs={"service_id": self.service.id}))
        except Exception:
            messages.error(self.request, "An error occurred while saving the address details.")
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, "Error, Check input details and try again")
        return self.render_to_response(self.get_context_data(form=form))


class SocialLinksCreateView(LoginRequiredMixin, CreateView):
    model = SocialMediaLink
    form_class = SocialMediaLinkForm
    template_name = 'services/forms/links_form.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.service = get_object_or_404(Service, id=kwargs['service_id'])
            return super().dispatch(request, *args, **kwargs)
        except Exception:
            messages.error(request, "An error occurred while processing the request.")
            return redirect("some_error_page_or_fallback_url")

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context["service"] = self.service
            context["service_id"] = self.service.id
            context["social_media_form"] = self.get_form()
            context["social_links"] = SocialMediaLink.objects.filter(service=self.service)
            return context
        except Exception:
            messages.error(self.request, "An error occurred while fetching social links.")
            return {}

    def form_valid(self, form):
        try:
            form.instance.service = self.service
            social_link=form.save()
            messages.success(self.request, "Social media link added successfully!")
            create_notification(
                user=self.service.user,
                notification_type="social_link",
                message=f"A new social media link ({social_link.platform}) has been added for {self.service.title}.",
                related_object=self.service
            )
            return self.render_to_response(self.get_context_data(form=self.form_class()))
        except Exception:
            messages.error(self.request, "An error occurred while saving the social media link.")
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, "Error: Check input details and try again.")
        return self.render_to_response(self.get_context_data(form=form))


class ServiceImageUploadView(LoginRequiredMixin, View):
    template_name = "services/forms/image_form.html"

    def get(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        form = ServiceImageForm()
        images = service.images.all()

        return render(request, self.template_name, {
            "form": form,
            "service": service,
            "service_id": service_id,
            "images": images
        })

    def post(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        form = ServiceImageForm(request.POST, request.FILES)

        files = request.FILES.getlist("image")

        if not files:
            messages.error(request, "Please select at least one image to upload.")
            return self.get(request, service_id)

        for file in files:
            ServiceImage.objects.create(service=service, image=file)

        messages.success(request, "Images uploaded successfully!")
        return redirect(reverse("service_image_upload", kwargs={"service_id": service.id}))

class ServiceImageDeleteView(LoginRequiredMixin, View):
    def post(self, request, service_id, image_id):
        service = get_object_or_404(Service, id=service_id)
        image = get_object_or_404(ServiceImage, id=image_id, service=service)
        
        image.delete()
        messages.success(request, "Image deleted successfully!")

        return redirect(reverse("service_image_upload", kwargs={"service_id": service.id}))

class ServiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'services/forms/service_form.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Service, id=self.kwargs["service_id"], user=self.request.user)

    def form_valid(self, form):
        service = form.save()
        messages.success(self.request, "Service details updated successfully.")
        address_details = ServiceLocation.objects.filter(service=service).first()
        if address_details:
            return redirect(reverse("address_details_update", kwargs={"service_id": service.id, "address_id": address_details.id}))
        return redirect(reverse("address_details_create", kwargs={"service_id": service.id}))

    def form_invalid(self, form):
        messages.error(self.request, "Error: Check input details and try again.")
        return self.render_to_response(self.get_context_data(form=form))
    
class AddressDetailsUpdateView(LoginRequiredMixin, UpdateView):
    model = ServiceLocation
    form_class = ServiceLocationForm
    template_name = "services/forms/location_form.html"

    def get_object(self, queryset=None):
        service = get_object_or_404(Service, id=self.kwargs["service_id"])
        return get_object_or_404(ServiceLocation, id=self.kwargs["address_id"], service=service)

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Address details updated successfully.")
        service_id = self.object.service.id
        return redirect(reverse("social_link_create", kwargs={"service_id": service_id}))

    def form_invalid(self, form):
        messages.error(self.request, "Error: Check input details and try again.")
        return self.render_to_response(self.get_context_data(form=form))

    
class ServiceDetailView(LoginRequiredMixin, View):
    template_name = "services/service_details.html"

    def get(self, request, service_id):
        service = get_object_or_404(Service, id=service_id, user=request.user)
        working_hours = WorkingHour.objects.filter(service=service)
        address_details = ServiceLocation.objects.filter(service=service).first()
        social_links = SocialMediaLink.objects.filter(service=service)
        service_images = ServiceImage.objects.filter(service=service)

        return render(request, self.template_name, {
            "service": service,
            "working_hours": working_hours,
            "address_details": address_details,
            "social_links": social_links,
            "service_images": service_images,
        })


class WorkingHoursDeleteView(View):
    def post(self, request, working_hour_id, *args, **kwargs):
        working_hour = get_object_or_404(WorkingHour, id=working_hour_id)
        service_id = working_hour.service.id  # Get service ID before deleting
        working_hour.delete()
        messages.success(request, "Working hour deleted successfully.")
        return redirect(reverse("working_hours_create", kwargs={"service_id": service_id}))
    
class SocialLinkDeleteView(LoginRequiredMixin, View):
    def post(self, request, link_id, *args, **kwargs):
        social_link = get_object_or_404(SocialMediaLink, id=link_id)
        service = social_link.service  
        create_notification(
            user=service.user,
            notification_type="social_link",
            message=f"A social media link ({social_link.platform}) has been removed from {service.title}.",
            related_object=service
        )
        social_link.delete()
        messages.success(request, "Social media link deleted successfully!")
        return redirect("social_link_create", service_id=service.id)

from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class MyServicesView(LoginRequiredMixin, ListView):
    model = Service
    template_name = "services/my_services.html"
    context_object_name = "services"

    def get_queryset(self):
        return Service.objects.filter(user=self.request.user)


class ServiceDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        service = Service.objects.get(pk=kwargs["pk"])
        service_title = service.title
        service.delete()
        messages.success(request, f"Service '{service_title}' has been deleted successfully.")
        return redirect(reverse_lazy("my-services"))

    def get(self, request, *args, **kwargs):
        return redirect(reverse_lazy("my-services"))

class ToggleAvailabilityView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        service = Service.objects.get(id=kwargs["pk"], user=request.user)
        service.is_available = not service.is_available
        service.save()
        messages.success(request, "Service marked available")

        return redirect("my-services")
    
class ServiceView(View):
    template_name = "services/service.html"

    def get(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        working_hours = WorkingHour.objects.filter(service=service)
        address_details = ServiceLocation.objects.filter(service=service).first()
        social_links = SocialMediaLink.objects.filter(service=service)
        service_images = ServiceImage.objects.filter(service=service)
        feedbacks = Feedback.objects.filter(service=service).order_by("-created_at")
        form = FeedbackForm()
        return render(request, self.template_name, {
            "service": service,
            "working_hours": working_hours,
            "address_details": address_details,
            "social_links": social_links,
            "service_images": service_images,
            "feedbacks": feedbacks,
            "form": form
        })

    def post(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.service = service
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('service_view', service_id=service.id)
        else:
            messages.error(request, "There was an error with your feedback. Please try again.")
            return redirect('service_view', service_id=service.id)

    
from django.utils.timezone import now
from django.views.generic import ListView
from .models import Service, ServiceType, ServiceLocation, WorkingHour

from django.db.models import Avg, Min, Max, Count


class AllServicesView(ListView):
    model = Service
    template_name = "services/all_services.html"
    context_object_name = "all_services"

    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True, is_available=True)

        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        if min_price and max_price:
            queryset = queryset.filter(price__gte=min_price, price__lte=max_price)

        availability = self.request.GET.get("availability")
        if availability == "available":
            queryset = queryset.filter(is_available=True)
        elif availability == "unavailable":
            queryset = queryset.filter(is_available=False)

        user_id = self.request.GET.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        city = self.request.GET.get("city")
        state = self.request.GET.get("state")
        country = self.request.GET.get("country")
        if city:
            queryset = queryset.filter(location__city__iexact=city)
        if state:
            queryset = queryset.filter(location__state__iexact=state)
        if country:
            queryset = queryset.filter(location__country__iexact=country)

        working_day = self.request.GET.get("working_day")
        start_time = self.request.GET.get("start_time")
        end_time = self.request.GET.get("end_time")
        if working_day and start_time and end_time:
            queryset = queryset.filter(
                working_hours__day=working_day,
                working_hours__open_time__lte=start_time,
                working_hours__close_time__gte=end_time,
            ).distinct()

        min_rating = self.request.GET.get("ratings")
        if min_rating:
            queryset = queryset.annotate(avg_rating=Avg("feedbacks__rating")).filter(avg_rating__gte=min_rating)

        return queryset.annotate(
            avg_rating=Avg("feedbacks__rating"),
            feedback_count=Count("feedbacks")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        service_types = ServiceType.objects.all()
        categorized_services = {}

        for service_type in service_types:
            services = self.get_queryset().filter(service_types=service_type)[:20]  # Limit to 20 services
            
            for service in services:
                service.discounted_price = round(service.price - (service.price * (service.discount / 100)), 2) if service.discount else service.price

            categorized_services[service_type] = services

        price_range = Service.objects.aggregate(min_price=Min("price"), max_price=Max("price"))

        context.update({
            "categorized_services": categorized_services,
            "service_types": service_types,
            "price_range": price_range,
        })
        return context


from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from .models import Service, ServiceType

class FilteredServicesView(ListView):
    model = Service
    template_name = "services/filtered_services.html"
    context_object_name = "services"
    paginate_by = 20

    def get_queryset(self):
        service_type = get_object_or_404(ServiceType, id=self.kwargs["service_type_id"])
        queryset = Service.objects.filter(service_types=service_type).order_by("-created_at")

        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        availability = self.request.GET.get("availability")
        city = self.request.GET.get("city")
        working_day = self.request.GET.get("working_day")
        start_time = self.request.GET.get("start_time")
        end_time = self.request.GET.get("end_time")
        ratings = self.request.GET.get("ratings")

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        if availability == "available":
            queryset = queryset.filter(is_available=True)
        elif availability == "unavailable":
            queryset = queryset.filter(is_available=False)

        if city:
            queryset = queryset.filter(location__icontains=city)

        if working_day:
            queryset = queryset.filter(working_hours__day=working_day)  # ✅ Corrected

        if start_time:
            queryset = queryset.filter(working_hours__open_time__gte=start_time)

        if end_time:
            queryset = queryset.filter(working_hours__close_time__lte=end_time)

        if ratings:
            queryset = queryset.annotate(avg_rating=Avg("feedbacks__rating")).filter(avg_rating__gte=ratings)

        queryset = queryset.annotate(
            avg_rating=Avg("feedbacks__rating"),
            total_ratings=Count("feedbacks"),
        )

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_type"] = get_object_or_404(ServiceType, id=self.kwargs["service_type_id"])
        return context


import razorpay
from django.conf import settings

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class BookingCreateView(View):
    def get(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        form = BookingForm(service=service)
        return render(request, "services/booking_form.html", {"form": form, "service": service})

    def post(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        form = BookingForm(request.POST, service=service)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.service = service
            booking.total_amount = service.discounted_price()
            booking.save()

            razorpay_order = client.order.create(
                {
                    "amount": int(booking.total_amount * 100),
                    "currency": "INR",
                    "payment_capture": "1",
                }
            )
            booking.razorpay_order_id = razorpay_order["id"]
            booking.save()

            return render(
                request,
                "services/payment.html",
                {
                    "booking": booking,
                    "razorpay_key": settings.RAZORPAY_KEY_ID,
                    "amount": booking.total_amount * 100,
                },
            )

        return render(request, "book_service.html", {"form": form, "service": service})

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = "services/booking_detail.html"
    context_object_name = "booking"

from django.conf import settings
from django.http import JsonResponse

class CreateRazorpayOrderView(View):
    def post(self, request, *args, **kwargs):
        service_id = self.kwargs["service_id"]
        service = get_object_or_404(Service, id=service_id)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        total_amount = int(service.discounted_price() * 100)  # Convert to paisa

        order_data = {
            "amount": total_amount,
            "currency": "INR",
            "payment_capture": "1",
        }

        order = client.order.create(data=order_data)

        return JsonResponse({"order_id": order["id"], "amount": total_amount, "currency": "INR"})
    
class PaymentSuccessView(View):
    def post(self, request):
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        booking = get_object_or_404(Booking, razorpay_order_id=razorpay_order_id)
        booking.razorpay_payment_id = razorpay_payment_id
        booking.razorpay_signature = razorpay_signature
        booking.payment_status = "paid"
        booking.save()

        return JsonResponse({"status": "success"})
    

from django.db.models.functions import Round

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "services/recieved_bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return (
            Booking.objects.filter(service__user=self.request.user)
            .select_related("service")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services_with_reviews = Service.objects.filter(user=self.request.user).annotate(
            review_count=Count("feedbacks"),
            average_rating=Round(Avg("feedbacks__rating"), 1)
        )

        context["services"] = services_with_reviews
        return context
    
class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = "services/booking_detail.html"
    context_object_name = "booking"

    def get_queryset(self):
        return Booking.objects.filter(id=self.kwargs["pk"])
    
class CancelBookingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, id=pk)

        if booking.user != request.user and booking.service.user != request.user:
            messages.error(request, "You are not allowed to cancel this booking.")
            return redirect("booking_list")
        if booking.status == "canceled":
            messages.warning(request, "This booking is already canceled.")
        else:
            booking.status = "canceled"
            booking.save()
            messages.success(request, "Your booking has been canceled successfully.")

        return redirect(reverse_lazy("booking_list"))
     
class MyBookedServicesView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "services/my_booked_services.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related("service").order_by("-created_at")

from django.db.models import Sum, Count, Avg

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "services/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_bookings = Booking.objects.count()
        booking_status_counts = Booking.objects.values("status").annotate(count=Count("status"))
        payment_status_counts = Booking.objects.values("payment_status").annotate(count=Count("payment_status"))
        average_ratings = Feedback.objects.values("service__title").annotate(avg_rating=Avg("rating"))
        total_earnings = round(Booking.objects.filter(payment_status="paid").aggregate(total=Sum("total_amount"))["total"] or 0)
        total_refunded = Booking.objects.filter(payment_status="refunded").aggregate(total=Sum("total_amount"))["total"] or 0
        total_completed_bookings = Booking.objects.filter(status="completed").count()
        total_canceled_bookings = Booking.objects.filter(status="canceled").count()
        total_pending_bookings = Booking.objects.filter(status="pending").count()
        total_ongoing_bookings = Booking.objects.filter(status="ongoing").count()
        total_users = User.objects.filter(bookings__isnull=False).distinct().count()

        total_services = Service.objects.count()

        recent_bookings = Booking.objects.select_related("user", "service").order_by("-created_at")[:5]

        context.update({
            "total_bookings": total_bookings,
            "booking_status_counts": booking_status_counts,
            "payment_status_counts": payment_status_counts,
            "average_ratings": average_ratings,
            "total_earnings": total_earnings,
            "total_refunded": total_refunded,
            "total_completed_bookings": total_completed_bookings,
            "total_canceled_bookings": total_canceled_bookings,
            "total_pending_bookings": total_pending_bookings,
            "total_ongoing_bookings": total_ongoing_bookings,
            "total_users": total_users,
            "total_services": total_services,
            "recent_bookings": recent_bookings,
        })

        return context


class FeedbackCreateView(CreateView):
    model = Feedback
    form_class = FeedbackForm
    
    def dispatch(self, request, *args, **kwargs):
        self.service = get_object_or_404(Service, id=kwargs["service_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.service = self.service
        form.instance.user = self.request.user
        form.save()
        messages.success(self.request, "Your feedback has been submitted successfully!")
        return redirect(reverse("service_detail", kwargs={"pk": self.service.id}))

    def form_invalid(self, form):
        messages.error(self.request, "Error: Please check your input and try again.")
        return self.render_to_response(self.get_context_data(form=form))
    

class FeedbackDetailView(DetailView):
    model = Feedback
    template_name = "services/feedback.html"
    context_object_name = "feedback"

    def get_object(self):
        feedback_id = self.kwargs.get("id") 
        return get_object_or_404(Feedback, id=feedback_id)