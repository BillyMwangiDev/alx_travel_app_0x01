from django.core.management.base import BaseCommand
from django.db import transaction
from listings.models import Listing, Booking, Review
from datetime import date, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = "Seed the database with sample listings, bookings, and reviews."

    def add_arguments(self, parser):
        parser.add_argument(
            "--listings",
            type=int,
            default=5,
            help="Number of listings to create (default: 5)",
        )
        parser.add_argument(
            "--bookings-per-listing",
            type=int,
            default=2,
            help="Number of bookings per listing (default: 2)",
        )
        parser.add_argument(
            "--reviews-per-listing",
            type=int,
            default=2,
            help="Number of reviews per listing (default: 2)",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing seeded data before seeding again.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        num_listings = options["listings"]
        bookings_per_listing = options["bookings_per_listing"]
        reviews_per_listing = options["reviews_per_listing"]
        do_flush = options["flush"]

        if do_flush:
            Review.objects.all().delete()
            Booking.objects.all().delete()
            Listing.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing data removed."))

        created_count = 0
        today = date.today()

        for i in range(1, num_listings + 1):
            listing = Listing.objects.create(
                title=f"Cozy Stay #{i}",
                description=(
                    "A comfortable property perfect for short vacations. "
                    "Includes amenities and is close to local attractions."
                ),
                location=f"City {i}",
                price_per_night=Decimal("50.00") + Decimal(i * 10),
                max_guests=2 + (i % 4),
            )
            created_count += 1

            # Create bookings
            for b in range(1, bookings_per_listing + 1):
                start = today + timedelta(days=i + (b - 1) * 3)
                end = start + timedelta(days=2)
                nights = (end - start).days
                total = listing.price_per_night * nights
                Booking.objects.create(
                    listing=listing,
                    guest_name=f"Guest {i}-{b}",
                    guest_email=f"guest{i}{b}@example.com",
                    start_date=start,
                    end_date=end,
                    total_price=total,
                    status=Booking.Status.CONFIRMED if b % 2 else Booking.Status.PENDING,
                )

            # Create reviews
            for r in range(1, reviews_per_listing + 1):
                Review.objects.create(
                    listing=listing,
                    reviewer_name=f"Reviewer {i}-{r}",
                    rating=3 + (r % 3),
                    comment="Great place. Would stay again!",
                )

        self.stdout.write(self.style.SUCCESS(f"Seed complete. Listings created: {created_count}"))


