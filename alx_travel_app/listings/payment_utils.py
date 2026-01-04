"""
Utility functions for Chapa payment API integration.
"""
import logging
import requests
from django.conf import settings
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def initiate_chapa_payment(
    amount: float,
    email: str,
    first_name: str,
    last_name: str,
    tx_ref: str,
    callback_url: str,
    currency: str = "ETB",
) -> Dict:
    """
    Initiate a payment with Chapa API.
    
    Args:
        amount: Payment amount
        email: Customer email
        first_name: Customer first name
        last_name: Customer last name
        tx_ref: Unique transaction reference
        callback_url: Callback URL for payment verification
        currency: Currency code (default: ETB)
    
    Returns:
        Dictionary containing payment response from Chapa API
    """
    url = f"{settings.CHAPA_API_URL}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "amount": str(amount),
        "currency": currency,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "tx_ref": tx_ref,
        "callback_url": callback_url,
        "return_url": callback_url,
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            logger.info(f"Payment initiated successfully for tx_ref: {tx_ref}")
            return {
                "success": True,
                "data": data.get("data", {}),
                "checkout_url": data.get("data", {}).get("checkout_url"),
            }
        else:
            error_msg = data.get("message", "Payment initiation failed")
            logger.error(f"Payment initiation failed for tx_ref {tx_ref}: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
            }
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(f"Payment initiation error for tx_ref {tx_ref}: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
        }
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Payment initiation error for tx_ref {tx_ref}: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
        }


def verify_chapa_payment(tx_ref: str) -> Dict:
    """
    Verify a payment status with Chapa API.
    
    Args:
        tx_ref: Transaction reference from Chapa
    
    Returns:
        Dictionary containing payment verification response from Chapa API
    """
    url = f"{settings.CHAPA_API_URL}/transaction/verify/{tx_ref}"
    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            payment_data = data.get("data", {})
            payment_status = payment_data.get("status", "").lower()
            
            logger.info(f"Payment verification successful for tx_ref: {tx_ref}, status: {payment_status}")
            return {
                "success": True,
                "data": payment_data,
                "status": payment_status,
            }
        else:
            error_msg = data.get("message", "Payment verification failed")
            logger.error(f"Payment verification failed for tx_ref {tx_ref}: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
            }
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(f"Payment verification error for tx_ref {tx_ref}: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
        }
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Payment verification error for tx_ref {tx_ref}: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
        }
