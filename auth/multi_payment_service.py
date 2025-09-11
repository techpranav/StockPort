"""
Multi-Gateway Payment Service

This module automatically selects the appropriate payment gateway based on user location and availability.
Supports Razorpay (India), Stripe (Global), and PayPal (Global).
"""

import logging
import streamlit as st
from typing import Optional, Dict, Any, Tuple
import requests
from datetime import datetime

from auth.razorpay_service import RazorpayService
from auth.payment_service import PaymentService
from auth.paypal_service import PayPalService
from config import LICENSE_PLANS, get_base_url

logger = logging.getLogger(__name__)

class MultiPaymentService:
    """Service for handling payments through multiple gateways."""
    
    def __init__(self):
        self.razorpay_service = RazorpayService()
        self.stripe_service = PaymentService()
        self.paypal_service = PayPalService()
        self.preferred_gateway = None
        self._detect_preferred_gateway()
    
    def _detect_preferred_gateway(self):
        """Detect the preferred payment gateway based on configuration."""
        import os
        
        # Check if specific gateway is configured
        gateway = os.getenv("PAYMENT_GATEWAY", "auto")
        
        if gateway == "razorpay":
            self.preferred_gateway = "razorpay"
        elif gateway == "stripe":
            self.preferred_gateway = "stripe"
        elif gateway == "paypal":
            self.preferred_gateway = "paypal"
        else:
            # Auto-detect based on availability
            if self.razorpay_service.is_configured():
                self.preferred_gateway = "razorpay"
            elif self.stripe_service.is_configured():
                self.preferred_gateway = "stripe"
            elif self.paypal_service.is_configured():
                self.preferred_gateway = "paypal"
            else:
                self.preferred_gateway = None
    
    def _detect_user_location(self) -> str:
        """Detect user location based on IP address."""
        try:
            # Use a free IP geolocation service
            response = requests.get("https://ipapi.co/json/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                country_code = data.get('country_code', 'US')
                return country_code
        except Exception as e:
            logger.warning(f"Could not detect user location: {e}")
        
        return "US"  # Default to US
    
    def get_available_gateways(self) -> Dict[str, bool]:
        """Get list of available payment gateways."""
        return {
            "razorpay": self.razorpay_service.is_configured(),
            "stripe": self.stripe_service.is_configured(),
            "paypal": self.paypal_service.is_configured()
        }
    
    def get_recommended_gateway(self, user_location: str = None) -> str:
        """Get recommended payment gateway based on user location."""
        if not user_location:
            user_location = self._detect_user_location()
        
        available_gateways = self.get_available_gateways()
        
        # India-specific logic
        if user_location == "IN":
            if available_gateways["razorpay"]:
                return "razorpay"
            elif available_gateways["paypal"]:
                return "paypal"
            elif available_gateways["stripe"]:
                return "stripe"
        
        # Global logic
        if available_gateways["stripe"]:
            return "stripe"
        elif available_gateways["paypal"]:
            return "paypal"
        elif available_gateways["razorpay"]:
            return "razorpay"
        
        return None
    
    def create_payment_session(self, user_id: int, plan_type: str, gateway: str = None) -> Optional[Dict[str, Any]]:
        """Create a payment session with the specified or recommended gateway."""
        try:
            if not gateway:
                user_location = self._detect_user_location()
                gateway = self.get_recommended_gateway(user_location)
            
            if not gateway:
                logger.error("No payment gateway available")
                return None
            
            plan = LICENSE_PLANS.get(plan_type)
            if not plan:
                logger.error(f"Invalid plan type: {plan_type}")
                return None
            
            if gateway == "razorpay":
                return self._create_razorpay_session(user_id, plan_type, plan)
            elif gateway == "stripe":
                return self._create_stripe_session(user_id, plan_type, plan)
            elif gateway == "paypal":
                return self._create_paypal_session(user_id, plan_type, plan)
            else:
                logger.error(f"Unsupported payment gateway: {gateway}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating payment session: {e}")
            return None
    
    def _create_razorpay_session(self, user_id: int, plan_type: str, plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create Razorpay payment session."""
        try:
            # Convert USD price to INR (approximate)
            usd_price = float(plan.get('price', 0) or 0)
            inr_price = int(round(usd_price * 83))  # Approximate USD to INR conversion
            if inr_price < 1:
                inr_price = 1  # Razorpay requires positive amount
            
            import os
            import streamlit as streamlit_module
            
            # Get dynamic base URL for redirect URLs
            base_url = get_base_url()
            success_url = f"{base_url}/?purchase=success&plan_type={plan_type}"
            failure_url = f"{base_url}/?purchase=failed&plan_type={plan_type}"
            cancel_url = f"{base_url}/?purchase=cancelled&plan_type={plan_type}"
            
            # Note: Razorpay Payment Links don't support separate success/failure URLs
            # They use webhooks for failure handling, but we'll use success URL as fallback
            link = self.razorpay_service.create_payment_link(user_id, plan_type, inr_price, "INR", success_url)
            if link:
                result = {
                    'gateway': 'razorpay',
                    'payment_url': link['short_url'],
                    'amount': inr_price,
                    'currency': 'INR',
                    'gateway_data': link
                }
                return result
            return None
            
        except Exception as e:
            logger.error(f"Error creating Razorpay session: {e}")
            return None
    
    def _create_stripe_session(self, user_id: int, plan_type: str, plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create Stripe payment session."""
        try:
            import os
            base_url = get_base_url()
            success_url = f"{base_url}/?purchase=success"
            cancel_url = f"{base_url}/?purchase=cancelled"
            
            checkout_url = self.stripe_service.create_checkout_session(
                user_id=user_id,
                plan_type=plan_type,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            if checkout_url:
                return {
                    'gateway': 'stripe',
                    'checkout_url': checkout_url,
                    'amount': plan.get('price', 0),
                    'currency': 'USD',
                    'gateway_data': {'checkout_url': checkout_url}
                }
            return None
            
        except Exception as e:
            logger.error(f"Error creating Stripe session: {e}")
            return None
    
    def _create_paypal_session(self, user_id: int, plan_type: str, plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create PayPal payment session."""
        try:
            order = self.paypal_service.create_order(
                user_id=user_id,
                plan_type=plan_type,
                amount=plan.get('price', 0),
                currency="USD"
            )
            
            if order and order.get('approval_url'):
                return {
                    'gateway': 'paypal',
                    'order_id': order['order_id'],
                    'approval_url': order['approval_url'],
                    'amount': plan.get('price', 0),
                    'currency': 'USD',
                    'gateway_data': order
                }
            return None
            
        except Exception as e:
            logger.error(f"Error creating PayPal session: {e}")
            return None
    
    def process_webhook(self, gateway: str, webhook_data: Dict[str, Any], signature: str = None) -> bool:
        """Process webhook from the specified gateway."""
        try:
            if gateway == "razorpay":
                return self.razorpay_service.process_webhook(webhook_data, signature or "")
            elif gateway == "stripe":
                return self.stripe_service.process_webhook_event(webhook_data)
            elif gateway == "paypal":
                return self.paypal_service.process_webhook(webhook_data)
            else:
                logger.error(f"Unsupported gateway for webhook: {gateway}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing webhook for {gateway}: {e}")
            return False
    
    def get_available_plans(self) -> Dict[str, Any]:
        """Get available license plans with pricing information."""
        return LICENSE_PLANS
    
    def get_plan_details(self, plan_type: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific plan."""
        return LICENSE_PLANS.get(plan_type)
    
    def get_gateway_info(self, gateway: str) -> Dict[str, Any]:
        """Get information about a specific payment gateway."""
        info = {
            'name': gateway.title(),
            'configured': False,
            'supported_countries': [],
            'supported_currencies': [],
            'payment_methods': []
        }
        
        if gateway == "razorpay":
            info['configured'] = self.razorpay_service.is_configured()
            info['supported_countries'] = ["India"]
            info['supported_currencies'] = ["INR"]
            info['payment_methods'] = self.razorpay_service.get_supported_payment_methods()
            
        elif gateway == "stripe":
            info['configured'] = self.stripe_service.is_configured()
            info['supported_countries'] = ["Global (excluding India)"]
            info['supported_currencies'] = ["USD", "EUR", "GBP", "CAD", "AUD"]
            info['payment_methods'] = ["cards", "bank_transfers", "wallets"]
            
        elif gateway == "paypal":
            info['configured'] = self.paypal_service.is_configured()
            info['supported_countries'] = ["Global"]
            info['supported_currencies'] = self.paypal_service.get_supported_currencies()
            info['payment_methods'] = ["paypal", "cards", "bank_transfers"]
        
        return info
    
    def get_pricing_by_location(self, user_location: str = None) -> Dict[str, Any]:
        """Get pricing information based on user location."""
        if not user_location:
            user_location = self._detect_user_location()
        
        plans = self.get_available_plans()
        pricing = {}
        
        for plan_key, plan in plans.items():
            usd_price = plan.get('price', 0)
            
            if user_location == "IN":
                # Convert to INR for Indian users
                inr_price = usd_price * 83  # Approximate conversion
                pricing[plan_key] = {
                    'currency': 'INR',
                    'price': inr_price,
                    'formatted_price': f"₹{inr_price:,.0f}",
                    'gateway': 'razorpay'
                }
            else:
                # Use USD for international users
                pricing[plan_key] = {
                    'currency': 'USD',
                    'price': usd_price,
                    'formatted_price': f"${usd_price:.2f}",
                    'gateway': 'stripe' if self.stripe_service.is_configured() else 'paypal'
                }
        
        return pricing
    
    def is_configured(self) -> bool:
        """Check if any payment gateway is configured."""
        available_gateways = self.get_available_gateways()
        return any(available_gateways.values())
    
    def get_supported_countries(self) -> Dict[str, list]:
        """Get supported countries for each gateway."""
        return {
            "razorpay": ["India"],
            "stripe": ["United States", "Canada", "United Kingdom", "Australia", "European Union"],
            "paypal": ["Global"]
        }
