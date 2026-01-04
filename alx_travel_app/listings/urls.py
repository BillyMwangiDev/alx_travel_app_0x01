from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, verify_payment, initiate_payment

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    # Payment endpoints
    path('payments/verify/', verify_payment, name='verify-payment'),
    path('bookings/<int:booking_id>/initiate-payment/', initiate_payment, name='initiate-payment'),
]

