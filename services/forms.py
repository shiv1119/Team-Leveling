from django import forms
from .models import *


class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control dark-input"})


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            "title", "description", "service_types", "tags",
            "price_type", "price", "discount", "cancellation_policy",
            "contact_email", "contact_phone", "whatsapp_number",
            "website_url", "is_available"
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control dark-input"}),
            "description": forms.Textarea(attrs={"class": "form-control dark-input", "rows": 4}),
            "service_types": forms.SelectMultiple(attrs={"class": "form-control dark-input"}),
            "tags": forms.TextInput(attrs={"class": "form-control dark-input"}),
            "price_type": forms.Select(attrs={"class": "form-control dark-input"}),
            "price": forms.NumberInput(attrs={"class": "form-control dark-input"}),
            "discount": forms.NumberInput(attrs={"class": "form-control dark-input"}),
            "cancellation_policy": forms.Select(attrs={"class": "form-control dark-input"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-control dark-input"}),
            "contact_phone": forms.TextInput(attrs={"class": "form-control dark-input"}),
            "whatsapp_number": forms.TextInput(attrs={"class": "form-control dark-input"}),
            "website_url": forms.URLInput(attrs={"class": "form-control dark-input"}),
            "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),  # Bootstrap checkbox class
        }


class ServiceLocationForm(BaseForm):
    class Meta:
        model = ServiceLocation
        fields = [
            "street_address", "landmark", "city", "state",
            "country", "postal_code", "latitude", "longitude",
            "google_maps_url"
        ]


class WorkingHourForm(forms.ModelForm):
    class Meta:
        model = WorkingHour
        fields = ["day", "open_time", "close_time"]
        widgets = {
            "day": forms.Select(attrs={"class": "form-control"}),
            "open_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "close_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
        }



class SocialMediaLinkForm(BaseForm):
    class Meta:
        model = SocialMediaLink
        fields = ["platform", "url"]


class ServiceImageForm(BaseForm):
    class Meta:
        model = ServiceImage
        fields = ["image"]


class BookingForm(forms.ModelForm):
    selected_service_type = forms.ModelChoiceField(
        queryset=ServiceType.objects.none(),
        empty_label="Select a Service Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        label="Start Time"
    )
    
    end_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        label="End Time"
    )

    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your address'}),
        label="Address"
    )
    
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}),
        label="City"
    )
    
    pincode = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter pincode'}),
        label="Pincode"
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Special instructions (optional)'}),
        label="Notes"
    )
    booking_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Booking Date"
    )
    class Meta:
        model = Booking
        fields = ["selected_service_type", "start_time","booking_date", "end_time", "notes", "address", "city", "pincode"]

    def __init__(self, *args, **kwargs):
        service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)
        if service:
            self.fields['selected_service_type'].queryset = service.service_types.all()

        for field in self.fields:
            self.fields[field].widget.attrs['class'] += ' mb-3'

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["rating", "title", "comment"]
        widgets = {
            "rating": forms.Select(
                attrs={
                    "class": "form-select form-control dark-input",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control dark-input",
                    "placeholder": "Enter feedback title",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control dark-input",
                    "rows": 4,
                    "placeholder": "Write your feedback here...",
                }
            ),
        }