import uuid
import random
from faker import Faker
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.apps import apps  # ✅ Fix: Avoids circular import
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Generate fake bookings for testing"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Dynamically get models to prevent circular import
        Booking = apps.get_model('services', 'Booking')
        Service = apps.get_model('services', 'Service')
        ServiceType = apps.get_model('services', 'ServiceType')

        # Get the user with username 'shiv_1119'
        try:
            owner_user = User.objects.get(username="shiv_1119")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ User 'shiv_1119' does not exist. Create this user first!"))
            return

        # Get all services owned by 'shiv_1119'
        services = list(Service.objects.filter(user=owner_user))
        if not services:
            self.stdout.write(self.style.ERROR("❌ No services found for user 'shiv_1119'. Create services first!"))
            return

        # Get all service types (if available)
        service_types = list(ServiceType.objects.all())

        # Get all users except 'shiv_1119'
        other_users = list(User.objects.exclude(username="shiv_1119"))
        if not other_users:
            self.stdout.write(self.style.ERROR("❌ No other users found. Create test users first!"))
            return

        # Create fake bookings
        bookings = []
        for _ in range(10):  # Change this number to generate more bookings
            service = random.choice(services)
            booking_date = fake.date_between(start_date="-30d", end_date="+30d")
            
            # Generate a valid start_time and end_time
            start_time = fake.time_object()
            end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=random.randint(1, 3))).time()

            booking = Booking(
                id=uuid.uuid4(),
                service=service,
                user=random.choice(other_users),  # Ensure booking user is NOT 'shiv_1119'
                status=random.choice(["pending", "confirmed", "completed", "canceled"]),
                payment_status=random.choice(["pending", "paid", "failed", "refunded"]),
                total_amount=round(random.uniform(100, 1000), 2),
                razorpay_order_id=str(uuid.uuid4()),
                razorpay_payment_id=str(uuid.uuid4()),
                razorpay_signature=str(uuid.uuid4()),
                payment_method=random.choice(["Credit Card", "Debit Card", "UPI", "Net Banking"]),
                is_refunded=random.choice([True, False]),
                booking_date=booking_date,
                start_time=start_time,
                end_time=end_time,
                address=fake.address() if random.choice([True, False]) else "",
                city=fake.city(),
                pincode=fake.zipcode(),
                cancellation_reason=fake.sentence() if random.choice([True, False]) else "",
                notes=fake.sentence(),
                selected_service_type=random.choice(service_types) if service_types else None,
            )
            bookings.append(booking)

        Booking.objects.bulk_create(bookings)

        self.stdout.write(self.style.SUCCESS(f"✅ {len(bookings)} fake bookings created for services owned by 'shiv_1119', booked by other users."))
