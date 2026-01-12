"""
Authentication and Licensing Package

This package provides user authentication, session management, and license validation.
"""

from .database import AuthDatabase
from .user_service import UserService
from .license_service import LicenseService
from .oauth_service import OAuthService
from .payment_service import PaymentService
from .razorpay_service import RazorpayService
from .paypal_service import PayPalService
from .multi_payment_service import MultiPaymentService
from .security_service import SecurityService
from .ui import (
    render_auth_gate,
    render_login_page,
    render_register_page,
    render_license_purchase,
    render_admin_panel,
    render_user_profile
)

__all__ = [
    'AuthDatabase',
    'UserService', 
    'LicenseService',
    'OAuthService',
    'PaymentService',
    'RazorpayService',
    'PayPalService',
    'MultiPaymentService',
    'SecurityService',
    'render_auth_gate',
    'render_login_page',
    'render_register_page',
    'render_license_purchase',
    'render_admin_panel',
    'render_user_profile'
]
