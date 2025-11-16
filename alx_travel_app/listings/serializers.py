from rest_framework import serializers
from .models import Listing, Booking


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "description",
            "location",
            "price_per_night",
            "max_guests",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "listing",
            "guest_name",
            "guest_email",
            "start_date",
            "end_date",
            "total_price",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        total_price = attrs.get("total_price")
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError("end_date must be on or after start_date")
        if total_price is not None and total_price < 0:
            raise serializers.ValidationError("total_price cannot be negative")
        return attrs


