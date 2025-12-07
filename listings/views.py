from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing listings.
    
    Provides CRUD operations:
    - GET /api/listings/ - List all listings
    - POST /api/listings/ - Create a new listing
    - GET /api/listings/{id}/ - Retrieve a specific listing
    - PUT /api/listings/{id}/ - Update a listing (full update)
    - PATCH /api/listings/{id}/ - Partially update a listing
    - DELETE /api/listings/{id}/ - Delete a listing
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """
        Get all bookings for a specific listing.
        GET /api/listings/{id}/bookings/
        """
        listing = self.get_object()
        bookings = listing.bookings.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    
    Provides CRUD operations:
    - GET /api/bookings/ - List all bookings
    - POST /api/bookings/ - Create a new booking
    - GET /api/bookings/{id}/ - Retrieve a specific booking
    - PUT /api/bookings/{id}/ - Update a booking (full update)
    - PATCH /api/bookings/{id}/ - Partially update a booking
    - DELETE /api/bookings/{id}/ - Delete a booking
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_queryset(self):
        """
        Optionally filter bookings by listing_id via query parameter.
        Example: /api/bookings/?listing_id=1
        """
        queryset = Booking.objects.all()
        listing_id = self.request.query_params.get('listing_id', None)
        if listing_id is not None:
            queryset = queryset.filter(listing_id=listing_id)
        return queryset

