import logging
import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
from .payment_utils import initiate_chapa_payment, verify_chapa_payment
from .tasks import send_booking_confirmation_email

logger = logging.getLogger(__name__)


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

    def create(self, request, *args, **kwargs):
        """
        Create a booking and initiate payment.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create booking
        booking = serializer.save()
        
        # Generate booking reference
        booking_reference = f"BK-{booking.id}-{uuid.uuid4().hex[:8].upper()}"
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            booking_reference=booking_reference,
            amount=booking.total_price,
            status=Payment.Status.PENDING,
        )
        
        # Prepare customer name for Chapa
        guest_name_parts = booking.guest_name.split(maxsplit=1)
        first_name = guest_name_parts[0] if guest_name_parts else booking.guest_name
        last_name = guest_name_parts[1] if len(guest_name_parts) > 1 else ""
        
        # Build callback URL
        callback_url = request.build_absolute_uri(f"/api/payments/verify/")
        
        # Initiate payment with Chapa
        payment_result = initiate_chapa_payment(
            amount=float(booking.total_price),
            email=booking.guest_email,
            first_name=first_name,
            last_name=last_name,
            tx_ref=booking_reference,
            callback_url=callback_url,
        )
        
        if payment_result.get("success"):
            # Update payment with transaction ID if available
            checkout_url = payment_result.get("checkout_url")
            transaction_data = payment_result.get("data", {})
            
            # Store checkout URL or transaction ID if available
            if checkout_url:
                logger.info(f"Payment initiated for booking {booking.id}, checkout URL: {checkout_url}")
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    "booking": serializer.data,
                    "payment": {
                        "status": payment.status,
                        "booking_reference": payment.booking_reference,
                        "amount": str(payment.amount),
                        "checkout_url": checkout_url,
                    },
                },
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            # Payment initiation failed
            error_msg = payment_result.get("error", "Failed to initiate payment")
            logger.error(f"Payment initiation failed for booking {booking.id}: {error_msg}")
            
            # Update payment status to failed
            payment.status = Payment.Status.FAILED
            payment.save()
            
            return Response(
                {
                    "booking": serializer.data,
                    "payment": {
                        "status": payment.status,
                        "error": error_msg,
                    },
                },
                status=status.HTTP_201_CREATED,
            )


@api_view(['GET', 'POST'])
def verify_payment(request):
    """
    Verify payment status with Chapa API.
    
    GET /api/payments/verify/?tx_ref=<transaction_reference>
    POST /api/payments/verify/ (for webhook callbacks)
    """
    tx_ref = request.GET.get('tx_ref') or request.data.get('tx_ref')
    
    if not tx_ref:
        return Response(
            {"error": "tx_ref parameter is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    try:
        # Find payment by booking_reference (tx_ref)
        payment = Payment.objects.get(booking_reference=tx_ref)
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for tx_ref: {tx_ref}")
        return Response(
            {"error": "Payment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    
    # Verify payment with Chapa
    verification_result = verify_chapa_payment(tx_ref)
    
    if verification_result.get("success"):
        payment_status = verification_result.get("status", "").lower()
        
        # Update payment status based on Chapa response
        if payment_status == "success":
            payment.status = Payment.Status.COMPLETED
            payment.transaction_id = verification_result.get("data", {}).get("id", tx_ref)
            payment.save()
            
            # Update booking status to confirmed
            booking = payment.booking
            booking.status = Booking.Status.CONFIRMED
            booking.save()
            
            # Send confirmation email asynchronously
            try:
                send_booking_confirmation_email.delay(booking.id)
                logger.info(f"Booking confirmation email queued for booking {booking.id}")
            except Exception as e:
                logger.error(f"Failed to queue confirmation email: {e}")
            
            return Response(
                {
                    "status": "success",
                    "payment_status": payment.status,
                    "booking_id": booking.id,
                    "message": "Payment verified successfully",
                },
                status=status.HTTP_200_OK,
            )
        else:
            payment.status = Payment.Status.FAILED
            payment.save()
            
            return Response(
                {
                    "status": "failed",
                    "payment_status": payment.status,
                    "message": "Payment verification failed",
                },
                status=status.HTTP_200_OK,
            )
    else:
        error_msg = verification_result.get("error", "Payment verification failed")
        logger.error(f"Payment verification error for tx_ref {tx_ref}: {error_msg}")
        
        return Response(
            {
                "status": "error",
                "error": error_msg,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(['POST'])
def initiate_payment(request, booking_id):
    """
    Initiate payment for an existing booking.
    
    POST /api/bookings/{booking_id}/initiate-payment/
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if payment already exists
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            "booking_reference": f"BK-{booking.id}-{uuid.uuid4().hex[:8].upper()}",
            "amount": booking.total_price,
            "status": Payment.Status.PENDING,
        },
    )
    
    if not created and payment.status == Payment.Status.COMPLETED:
        return Response(
            {"error": "Payment already completed for this booking"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    # Prepare customer name for Chapa
    guest_name_parts = booking.guest_name.split(maxsplit=1)
    first_name = guest_name_parts[0] if guest_name_parts else booking.guest_name
    last_name = guest_name_parts[1] if len(guest_name_parts) > 1 else ""
    
    # Build callback URL
    callback_url = request.build_absolute_uri(f"/api/payments/verify/")
    
    # Initiate payment with Chapa
    payment_result = initiate_chapa_payment(
        amount=float(booking.total_price),
        email=booking.guest_email,
        first_name=first_name,
        last_name=last_name,
        tx_ref=payment.booking_reference,
        callback_url=callback_url,
    )
    
    if payment_result.get("success"):
        checkout_url = payment_result.get("checkout_url")
        logger.info(f"Payment initiated for booking {booking.id}, checkout URL: {checkout_url}")
        
        return Response(
            {
                "status": "success",
                "payment": {
                    "booking_reference": payment.booking_reference,
                    "amount": str(payment.amount),
                    "checkout_url": checkout_url,
                },
            },
            status=status.HTTP_200_OK,
        )
    else:
        error_msg = payment_result.get("error", "Failed to initiate payment")
        logger.error(f"Payment initiation failed for booking {booking.id}: {error_msg}")
        
        payment.status = Payment.Status.FAILED
        payment.save()
        
        return Response(
            {
                "status": "error",
                "error": error_msg,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

