from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator


class Listing(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    max_guests = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f\"{self.title} - {self.location}\"


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = \"PENDING\", \"Pending\"
        CONFIRMED = \"CONFIRMED\", \"Confirmed\"
        CANCELLED = \"CANCELLED\", \"Cancelled\"

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name=\"bookings\")
    guest_name = models.CharField(max_length=150)
    guest_email = models.EmailField(validators=[EmailValidator()])
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [\"-created_at\"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F(\"start_date\")),
                name=\"booking_end_after_start\",
            )
        ]

    def __str__(self) -> str:
        return f\"Booking #{self.id} for {self.listing} ({self.start_date} → {self.end_date})\"


class Review(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name=\"reviews\")
    reviewer_name = models.CharField(max_length=150)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [\"-created_at\"]

    def __str__(self) -> str:
        return f\"Review {self.rating}/5 by {self.reviewer_name} on {self.listing}\"

