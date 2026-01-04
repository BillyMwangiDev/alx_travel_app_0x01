from django.contrib import admin
from .models import Listing, Booking, Review, Payment


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'location', 'price_per_night', 'max_guests', 'created_at']
    list_filter = ['created_at', 'location']
    search_fields = ['title', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'guest_name', 'guest_email', 'start_date', 'end_date', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'start_date']
    search_fields = ['guest_name', 'guest_email', 'listing__title']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'reviewer_name', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reviewer_name', 'listing__title', 'comment']
    readonly_fields = ['created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'booking_reference', 'transaction_id', 'amount', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['booking_reference', 'transaction_id', 'booking__guest_email', 'booking__guest_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


