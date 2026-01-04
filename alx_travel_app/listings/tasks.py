"""
Celery tasks for listings app.
"""
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email(self, booking_id: int):
    """
    Send booking confirmation email to the guest.
    
    Args:
        booking_id: The ID of the booking
    """
    try:
        booking = Booking.objects.get(id=booking_id)
        
        subject = f'Booking Confirmation - {booking.listing.title}'
        message = f'''
Dear {booking.guest_name},

Thank you for your booking!

Booking Details:
- Listing: {booking.listing.title}
- Location: {booking.listing.location}
- Check-in: {booking.start_date}
- Check-out: {booking.end_date}
- Total Amount: ${booking.total_price}
- Booking Reference: #{booking.id}

Your booking has been confirmed. We look forward to hosting you!

Best regards,
ALX Travel App Team
'''
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [booking.guest_email]
        
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        logger.info(f'Booking confirmation email sent to {booking.guest_email} for booking #{booking_id}')
        
    except Booking.DoesNotExist:
        logger.error(f'Booking #{booking_id} not found')
        raise
    except Exception as exc:
        logger.error(f'Failed to send booking confirmation email: {exc}')
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
