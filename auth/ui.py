"""
Refactored Authentication UI Module

This module provides a clean, modular approach to authentication UI components.
Each function handles a specific aspect of the authentication flow.
"""

import streamlit as st
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

# Import services and utilities
from .user_service import UserService
from .license_service import LicenseService
from .oauth_service import OAuthService
from .multi_payment_service import MultiPaymentService
from .constants import *
from config.app_config import AppConfig
from config.constants.Messages import *

# Configure logging
logger = logging.getLogger(__name__)

# Helper to get a CookieManager instance compatibly across versions
def _get_cookie_manager():
    try:
        from extra_streamlit_components import CookieManager  # type: ignore
        try:
            return CookieManager(key="app_cookies")
        except TypeError:
            # Older/newer API variants without named params
            return CookieManager("app_cookies")
    except Exception:
        try:
            import extra_streamlit_components as stx  # type: ignore
            try:
                return stx.CookieManager(key="app_cookies")
            except TypeError:
                return stx.CookieManager("app_cookies")
        except Exception:
            return None

class AuthUI:
    """Main authentication UI controller class."""
    
    def __init__(self):
        self.user_service = UserService()
        self.license_service = LicenseService()
        self.oauth_service = OAuthService()
        self.payment_service = MultiPaymentService()
        self.config = AppConfig()
    
    def render_auth_interface(self) -> bool:
        """
        Main authentication interface renderer.
        Returns True if user is authenticated, False otherwise.
        """
        # Handle OAuth callbacks first
        if self._handle_oauth_callback():
            return True
        
        # Handle payment callbacks
        self._handle_payment_callbacks()
        
        # Check if user is already authenticated
        if self._check_existing_authentication():
            return True
        
        # Show authentication interface
        self._render_login_register_interface()
        return False
    
    def _handle_oauth_callback(self) -> bool:
        """Handle OAuth callback from Google/Microsoft."""
        qp = st.query_params
        
        # Check for OAuth callback
        if qp.get('code') and qp.get('state'):
            try:
                state = qp.get('state', '')
                code = qp.get('code', '')
                
                # Check if we've already processed this code to prevent reuse
                if st.session_state.get('last_oauth_code') == code:
                    logger.info("OAuth code already processed, skipping")
                    # Clear OAuth parameters to prevent reprocessing
                    st.query_params.clear()
                    return False
                
                # Determine provider from state
                if state == 'google':
                    provider = 'google'
                elif state == 'microsoft':
                    provider = 'microsoft'
                else:
                    logger.warning(f"Invalid OAuth state: {state}")
                    # Clear OAuth parameters to prevent reprocessing
                    st.query_params.clear()
                    return False
                
                # Store the code to prevent reuse
                st.session_state['last_oauth_code'] = code
                
                # Exchange code for token and get user info
                try:
                    user_info = self.oauth_service.exchange_code_for_token(provider, code, state)
                    
                    if user_info:
                        # Create or update user
                        user = self._create_or_update_oauth_user(user_info, provider)
                        if user:
                            st.session_state[SSK_CURRENT_USER] = user
                            st.session_state[SSK_SESSION_TOKEN] = user['session_token']
                            
                            # Store session token in cookie for persistence
                            self._set_session_cookie(user['session_token'])
                            
                            st.success(f"Successfully logged in with {provider.title()}!")
                            
                            # Clear OAuth callback parameters to prevent reprocessing
                            st.query_params.clear()
                            
                            st.rerun()
                            return True
                    
                    logger.warning(f"Failed to authenticate with {provider.title()}")
                    # Clear OAuth parameters to prevent reprocessing
                    st.query_params.clear()
                    return False
                    
                except Exception as oauth_error:
                    logger.error(f"OAuth exchange error: {oauth_error}")
                    # Clear OAuth parameters to prevent reprocessing
                    st.query_params.clear()
                    return False
                
            except Exception as e:
                logger.error(f"OAuth callback error: {e}")
                st.error(f"Authentication error: {e}")
                return False
        
        return False
    
    def _handle_payment_callbacks(self):
        """Handle payment success/failure callbacks."""
        qp = st.query_params
        
        if qp.get('purchase') == 'success':
            # Prevent duplicate handling across reruns
            if not st.session_state.get('payment_success_processed'):
                st.session_state['payment_success_processed'] = True
                self._handle_payment_success()
        elif qp.get('purchase') in ['failed', 'cancelled']:
            self._handle_payment_failure(qp.get('purchase'))
    
    def _handle_payment_success(self):
        """Handle successful payment callback."""
        st.success("🎉 Payment successful! Activating your license...")
        # Keep user on Admin page if they were there
        if st.session_state.get('current_page') == 'admin':
            st.session_state['stay_on_admin'] = True
        
        # Determine final plan to activate: priority upgrade_plan > qp.plan_type > payment_session.plan_type > selected_plan
        upgrade_plan = st.session_state.get(SSK_UPGRADE_PLAN)
        payment_session = st.session_state.get(SSK_PAYMENT_SESSION)
        qp = st.query_params
        final_plan = None
        if upgrade_plan:
            final_plan = upgrade_plan
        elif qp.get('plan_type'):
            final_plan = qp.get('plan_type')
        elif payment_session and payment_session.get('plan_type'):
            final_plan = payment_session.get('plan_type')
        elif st.session_state.get(SSK_SELECTED_PLAN):
            final_plan = st.session_state.get(SSK_SELECTED_PLAN)
        
        if final_plan:
            try:
                current_user = st.session_state.get(SSK_CURRENT_USER)
                if not current_user:
                    st.error("Unable to identify user for activation. Please login again.")
                    return
                license_key = self.license_service.create_license(current_user['id'], final_plan)
                st.success(f"✅ License activated! Your {final_plan.replace('_', ' ').title()} plan is now active.")
                # Clear any cached license so next view reflects new state
                st.session_state.pop('license_cache', None)
                # Clear upgrade/payment state and query params
                self._clear_upgrade_state()
                st.query_params.clear()
                # Reset processed flag for future payments
                st.session_state.pop('payment_success_processed', None)
                # Keep or restore admin tab
                if st.session_state.pop('stay_on_admin', False):
                    st.session_state['current_page'] = 'admin'
                st.rerun()
            except Exception as e:
                logger.error(f"Activation error after payment: {e}")
                st.error(f"Activation failed: {e}")
        else:
            # Fallback: try selected_plan cookie
            try:
                cm = _get_cookie_manager()
                cookie_plan = cm.get("selected_plan") if cm else None
                if cookie_plan:
                    current_user = st.session_state.get(SSK_CURRENT_USER)
                    if current_user:
                        license_key = self.license_service.create_license(current_user['id'], cookie_plan)
                        st.success(f"✅ License activated! Your {cookie_plan.replace('_', ' ').title()} plan is now active.")
                        if cm:
                            cm.delete("selected_plan")
                        st.session_state.pop('license_cache', None)
                        self._clear_upgrade_state()
                        st.query_params.clear()
                        st.session_state.pop('payment_success_processed', None)
                        if st.session_state.pop('stay_on_admin', False):
                            st.session_state['current_page'] = 'admin'
                        st.rerun()
                        return
            except Exception as _:
                pass
            logger.warning("Payment success received but no plan found for activation")
            st.info("Payment confirmed. Please choose a plan again if it is not activated.")
    
    def _handle_payment_failure(self, status: str):
        """Handle payment failure callback."""
        if status == 'failed':
            st.error("❌ Payment failed. Please try again or contact support.")
        elif status == 'cancelled':
            st.warning("⚠️ Payment was cancelled.")
        
        # Clear payment state
        for key in [SSK_PAYMENT_SESSION, SSK_PAYMENT_REDIRECT_URL, SSK_SELECTED_PLAN, SSK_PAYMENT_GATEWAY]:
            st.session_state.pop(key, None)
    
    def _check_existing_authentication(self) -> bool:
        """Check if user is already authenticated via session or cookies."""
        # Check session state first
        current_user = st.session_state.get(SSK_CURRENT_USER)
        if current_user:
            # Validate session
            if self._validate_user_session(current_user):
                return True
        
        # Always check cookies if no valid session found
        return self._check_session_cookies()
    
    def _validate_user_session(self, user: Dict[str, Any]) -> bool:
        """Validate user session and update if needed."""
        try:
            validated_user = self.user_service.get_current_user()
            if validated_user and validated_user['id'] == user['id']:
                st.session_state[SSK_CURRENT_USER] = validated_user
                return True
            else:
                # Session invalid, clear state
                self._clear_session_state()
                return False
        except Exception as e:
            logger.warning(f"Session validation failed: {e}")
            self._clear_session_state()
            return False
    
    def _check_session_cookies(self) -> bool:
        """Check for valid session cookies."""
        try:
            cookie_manager = _get_cookie_manager()
            if cookie_manager:
                session_token = cookie_manager.get("session_token")
                if session_token:
                    st.session_state[SSK_SESSION_TOKEN] = session_token
                    user = self.user_service.get_current_user()
                    if user:
                        st.session_state[SSK_CURRENT_USER] = user
                        return True
        except Exception as e:
            logger.warning(f"Error reading session cookie: {e}")
        
        return False
    
    def _set_session_cookie(self, session_token: str):
        """Set session token in cookie for persistence."""
        try:
            cookie_manager = _get_cookie_manager()
            if cookie_manager:
                cookie_manager.set(
                    cookie="session_token",
                    val=session_token,
                    expires_at=datetime.now() + timedelta(days=30)
                )
                logger.info("Session token stored in cookie")
        except Exception as e:
            logger.warning(f"Error setting session cookie: {e}")
    
    def _clear_session_cookie(self):
        """Clear session token from cookie."""
        try:
            cookie_manager = _get_cookie_manager()
            if cookie_manager:
                cookie_manager.delete("session_token")
                logger.info("Session token cleared from cookie")
        except Exception as e:
            logger.warning(f"Error clearing session cookie: {e}")
    
    def _clear_session_state(self):
        """Clear all authentication-related session state."""
        for key in list(st.session_state.keys()):
            if key.startswith(('auth_', 'session_', 'oauth_', 'payment_', 'upgrade_')):
                del st.session_state[key]
    
    def _create_or_update_oauth_user(self, user_info: Dict[str, Any], provider: str) -> Optional[Dict[str, Any]]:
        """Create or update user from OAuth info."""
        try:
            # Use the existing social_login method
            success, message, user = self.user_service.social_login(provider, user_info)
            
            if success and user:
                return user
            else:
                st.error(f"OAuth login failed: {message}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating/updating OAuth user: {e}")
            st.error(f"Error creating user account: {e}")
            return None
    
    def _render_login_register_interface(self):
        """Render the main login/register interface."""
        st.title("🔐 Authentication")
        st.markdown("---")
    
        # Create tabs for login and register
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            self._render_login_form()
        
        with tab2:
            self._render_register_form()
    
    def _render_login_form(self):
        """Render the login form."""
        with st.form("login_form"):
            st.subheader("Login")
            
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Login", use_container_width=True):
                    self._handle_login(email, password)
            
            with col2:
                if st.form_submit_button("Forgot Password?", use_container_width=True):
                    st.info("Password reset functionality coming soon!")
        
        # Social login section
        st.markdown("---")
        st.markdown("**Or login with:**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔵 Login with Google", use_container_width=True, key="google_login_btn"):
                self._initiate_google_oauth()
        
        with col2:
            if st.button("🔷 Login with Microsoft", use_container_width=True, key="microsoft_login_btn"):
                self._initiate_microsoft_oauth()
    
    def _render_register_form(self):
        """Render the registration form."""
        with st.form("register_form"):
            st.subheader("Register")
            
            username = st.text_input("Username", key="register_username")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
            
            if st.form_submit_button("Register", use_container_width=True):
                self._handle_registration(username, email, password, confirm_password)
        
        # Social login section
        st.markdown("---")
        st.markdown("**Or register with:**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔵 Register with Google", use_container_width=True, key="google_register_btn"):
                self._initiate_google_oauth()
        
        with col2:
            if st.button("🔷 Register with Microsoft", use_container_width=True, key="microsoft_register_btn"):
                self._initiate_microsoft_oauth()
    
    
    def _handle_login(self, email: str, password: str):
        """Handle user login."""
        if not email or not password:
            st.error("Please enter both email and password")
            return
        
        try:
            success, message, user = self.user_service.login_user(email, password)
            if success and user:
                st.session_state[SSK_CURRENT_USER] = user
                st.session_state[SSK_SESSION_TOKEN] = user['session_token']
                
                # Store session token in cookie for persistence
                self._set_session_cookie(user['session_token'])
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(message or "Invalid email or password")
        except Exception as e:
            logger.error(f"Login error: {e}")
            st.error(f"Login failed: {e}")
    
    def _handle_registration(self, username: str, email: str, password: str, confirm_password: str):
        """Handle user registration."""
        if not all([username, email, password, confirm_password]):
            st.error("Please fill in all fields")
            return
        
        if password != confirm_password:
            st.error("Passwords do not match")
            return
        
        if len(password) < 6:
            st.error("Password must be at least 6 characters long")
            return
        
        try:
            success, message = self.user_service.register_user(username, email, password)
            if success:
                st.success("Registration successful! Please login.")
                st.rerun()
            else:
                st.error(message or "Registration failed. Email may already be in use.")
        except Exception as e:
            logger.error(f"Registration error: {e}")
            st.error(f"Registration failed: {e}")
    
    def _initiate_google_oauth(self):
        """Initiate Google OAuth flow."""
        try:
            auth_url = self.oauth_service.get_google_auth_url()
            if auth_url:
                # Use direct redirect without debug messages
                st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
            else:
                st.error("Google OAuth not configured")
        except Exception as e:
            logger.error(f"Google OAuth error: {e}")
            st.error(f"Google OAuth error: {e}")
    
    def _initiate_microsoft_oauth(self):
        """Initiate Microsoft OAuth flow."""
        try:
            auth_url = self.oauth_service.get_microsoft_auth_url()
            if auth_url:
                # Use direct redirect without debug messages
                st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
            else:
                st.error("Microsoft OAuth not configured")
        except Exception as e:
            logger.error(f"Microsoft OAuth error: {e}")
            st.error(f"Microsoft OAuth error: {e}")


class UserProfileUI:
    """User profile and license management UI."""
    
    def __init__(self):
        self.user_service = UserService()
        self.license_service = LicenseService()
        self.payment_service = MultiPaymentService()
    
    def render_user_profile(self):
        """Render the user profile page."""
        st.title(TITLE_PROFILE)
        st.markdown("---")
        
        current_user = st.session_state.get('current_user')
        if not current_user:
            st.error("Please login first")
            return
    
        # User info section
        self._render_user_info(current_user)
        
        # License section
        self._render_license_section(current_user)
        
        # Profile actions
        self._render_profile_actions(current_user)
    
    def _render_user_info(self, user: Dict[str, Any]):
        """Render user information section."""
        st.subheader(SUBHEADER_ACCOUNT_INFO)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Username:** {user['username']}")
            st.markdown(f"**Email:** {user['email']}")
            st.markdown(f"**Account Type:** {'Admin' if user['is_admin'] else 'User'}")
        
        with col2:
            # License information
            license_valid, license_message, license_info = self.license_service.validate_license(user['id'])
            if license_valid and license_info:
                st.markdown(f"**License:** {license_info['plan_type']}")
                st.markdown(f"**Expires:** {license_info['expires_at']}")
            else:
                st.markdown("**License:** No active license")
    
    def _render_license_section(self, user: Dict[str, Any]):
        """Render license section with status and management."""
        st.markdown("---")
        st.subheader("License Information")
        
        # Get license information
        license_valid, license_message, license_info = self.license_service.validate_license(user['id'])
        
        if license_valid and license_info:
            self._render_active_license(license_info, user)
        else:
            self._render_no_license(license_message, user)
        
        # Single refresh button for all license states
        self._render_refresh_button(user, license_valid)
        
        # License purchase section
        if not license_valid or st.session_state.get(SSK_UPGRADE_MODE, False):
            st.markdown("---")
            if st.session_state.get(SSK_UPGRADE_MODE, False):
                st.subheader("🚀 Upgrade License")
                # Show upgrade-specific purchase interface
                license_purchase_ui = LicensePurchaseUI()
                license_purchase_ui.render_license_purchase(upgrade_mode=True, upgrade_plan=st.session_state.get(SSK_UPGRADE_PLAN))
            else:
                st.subheader("💳 Purchase License")
                # Show regular purchase interface
                license_purchase_ui = LicensePurchaseUI()
                license_purchase_ui.render_license_purchase()
    
    
    def _render_active_license(self, license_info: Dict[str, Any], user: Dict[str, Any]):
        """Render active license information."""
        st.markdown(f"**License Status:** ✅ Active")
        st.markdown(f"**Plan:** {license_info['plan_type']}")
        st.markdown(f"**Expires:** {license_info['expires_at']}")
        
        # Show upgrade options for basic users
        if license_info['plan_type'] in ['basic_monthly', 'basic_yearly']:
            self._render_upgrade_options(user)
    
    def _render_no_license(self, license_message: str, user: Dict[str, Any]):
        """Render no license state."""
        st.markdown("**License Status:** ❌ No active license")
        st.markdown(f"**Message:** {license_message}")
    
    def _render_upgrade_options(self, user: Dict[str, Any]):
        """Render upgrade options for basic license holders."""
        st.markdown("---")
        st.subheader("🚀 Upgrade to Pro")
        
        # Get available upgrade plans
        upgrade_plans = self._get_upgrade_plans()
        
        if upgrade_plans:
            col1, col2 = st.columns(2)
            for i, (plan_key, plan_name) in enumerate(upgrade_plans):
                with col1 if i % 2 == 0 else col2:
                    if st.button(f"Upgrade to {plan_name}", key=f"upgrade_{plan_key}"):
                        st.session_state[SSK_UPGRADE_PLAN] = plan_key
                        st.session_state[SSK_UPGRADE_MODE] = True
                        st.rerun()
        else:
            st.info("🎉 **You already have the highest plan available!**")
    
    def _get_upgrade_plans(self) -> list:
        """Get available upgrade plans for current user."""
        current_user = st.session_state.get('current_user')
        if not current_user:
            return []
        
        # Get current license
        license_valid, _, license_info = self.license_service.validate_license(current_user['id'])
        
        if not license_valid or not license_info:
            return [('pro_monthly', 'Pro Monthly'), ('pro_yearly', 'Pro Yearly')]
        
        current_plan = license_info['plan_type']
        
        # Define plan hierarchy
        plan_hierarchy = {
            'basic_monthly': ['pro_monthly', 'pro_yearly'],
            'basic_yearly': ['pro_yearly'],
            'pro_monthly': ['pro_yearly'],
            'pro_yearly': []
        }
        
        available_plans = plan_hierarchy.get(current_plan, [])
        
        plan_names = {
            'pro_monthly': 'Pro Monthly',
            'pro_yearly': 'Pro Yearly'
        }
        
        return [(plan, plan_names[plan]) for plan in available_plans]
    
    def _render_refresh_button(self, user: Dict[str, Any], is_active: bool):
        """Render license refresh button with smart functionality."""
        st.markdown("---")
        st.info("💡 **Just completed a payment?** Click the button below to refresh your license status.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            button_key = "refresh_license_active" if is_active else "refresh_license"
            if st.button("🔄 Refresh License Status", key=button_key):
                # Preserve Admin tab if currently on it
                if st.session_state.get('current_page') == 'admin':
                    st.session_state['stay_on_admin'] = True
                self._handle_license_refresh(user)
        
        with col2:
            # Show activation button if in upgrade mode
            upgrade_plan = st.session_state.get(SSK_UPGRADE_PLAN)
            if upgrade_plan and st.session_state.get(SSK_UPGRADE_MODE):
                if st.button(f"🎯 Activate {upgrade_plan.replace('_', ' ').title()}", key="manual_activate"):
                    self._handle_manual_activation(user, upgrade_plan)
    
    def _handle_license_refresh(self, user: Dict[str, Any]):
        """Handle license refresh with smart upgrade detection."""
        try:
            # Check if we should auto-upgrade based on payment context
            upgrade_mode = st.session_state.get(SSK_UPGRADE_MODE, False)
            upgrade_plan = st.session_state.get(SSK_UPGRADE_PLAN)
            payment_session = st.session_state.get(SSK_PAYMENT_SESSION)
            qp = st.query_params
            payment_success = qp.get('purchase') == 'success'
            
            has_payment_context = upgrade_mode or payment_session or payment_success
            
            # Determine final plan to activate: priority upgrade_plan > payment_session.plan_type > selected
            final_plan = None
            if upgrade_plan:
                final_plan = upgrade_plan
            elif qp.get('plan_type'):
                final_plan = qp.get('plan_type')
            elif payment_session and payment_session.get('plan_type'):
                final_plan = payment_session.get('plan_type')
            elif st.session_state.get(SSK_SELECTED_PLAN):
                final_plan = st.session_state.get(SSK_SELECTED_PLAN)

            if has_payment_context and final_plan:
                # Auto-upgrade to Pro license
                st.info(f"🔄 Payment detected - activating {final_plan.replace('_', ' ').title()}...")
                try:
                    license_key = self.license_service.create_license(user['id'], final_plan)
                    st.success(f"✅ License activated! Your {final_plan.replace('_', ' ').title()} plan is now active.")
                    # Clear upgrade mode and payment state
                    self._clear_upgrade_state()
                    # Stay on admin tab if currently there
                    if st.session_state.get('current_page') == 'admin':
                        st.session_state['stay_on_admin'] = True
                        st.query_params.clear()
                        if st.session_state.pop('stay_on_admin', False):
                            st.session_state['current_page'] = 'admin'
                    st.rerun()
                    return
                except Exception as e:
                    st.error(f"❌ Error creating Pro license: {e}")
            
            # Normal refresh if no payment context
            license_valid_new, license_message_new, license_info_new = self.license_service.validate_license(user['id'])
            if license_valid_new:
                st.success(f"✅ License updated! Your {license_info_new['plan_type']} plan is now active.")
                self._clear_payment_state()
                # Stay on admin tab if currently there
                if st.session_state.get('current_page') == 'admin':
                    st.session_state['stay_on_admin'] = True
                    st.query_params.clear()
                    if st.session_state.pop('stay_on_admin', False):
                        st.session_state['current_page'] = 'admin'
                st.rerun()
            else:
                st.warning("⚠️ No license changes found. If you just completed a payment, please wait a few minutes and try again.")
        except Exception as e:
            st.error(f"❌ Error refreshing license: {e}")
            logger.error(f"Error refreshing license: {e}")
    
    def _handle_manual_activation(self, user: Dict[str, Any], upgrade_plan: str):
        """Handle manual license activation."""
        try:
            license_key = self.license_service.create_license(user['id'], upgrade_plan)
            st.success(f"✅ License activated manually: {license_key}")
            self._clear_upgrade_state()
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to activate license: {e}")
    
    def _clear_upgrade_state(self):
        """Clear upgrade-related session state."""
        for key in [SSK_UPGRADE_MODE, SSK_UPGRADE_PLAN, SSK_PAYMENT_SESSION, SSK_PAYMENT_REDIRECT_URL, SSK_SELECTED_PLAN, SSK_PAYMENT_GATEWAY]:
            st.session_state.pop(key, None)
    
    def _clear_payment_state(self):
        """Clear payment-related session state."""
        for key in ['license_cache', SSK_PAYMENT_SESSION, SSK_PAYMENT_REDIRECT_URL, SSK_SELECTED_PLAN, SSK_PAYMENT_GATEWAY]:
            st.session_state.pop(key, None)
    
    def _render_profile_actions(self, user: Dict[str, Any]):
        """Render profile action buttons."""
        st.markdown("---")
        st.subheader("Profile Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Change Password", use_container_width=True):
                st.session_state['profile_action'] = 'change_password'
                st.rerun()
        
        with col2:
            if st.button("Logout", use_container_width=True):
                self._handle_logout()
        
        with col3:
            if user.get('is_admin'):
                if st.button("Admin Panel", use_container_width=True):
                    st.session_state['current_page'] = 'admin'
                    st.rerun()
    
    def _handle_logout(self):
        """Handle user logout."""
        try:
            current_user = st.session_state.get('current_user')
            if current_user and self.user_service.logout_user(current_user['session_token']):
                # Clear session state
                st.session_state.clear()
                
                # Clear cookies
                try:
                    # Use AuthUI helper if available; otherwise local clear
                    if hasattr(AuthUI, '_clear_session_cookie'):
                        # Fallback to invoking on a temporary AuthUI instance
                        AuthUI()._clear_session_cookie()
                    else:
                        from extra_streamlit_components import CookieManager
                        CookieManager().delete("session_token")
                except Exception as ce:
                    logger.warning(f"Cookie clear error on logout: {ce}")
                
                st.success(SUCCESS_LOGGED_OUT)
                st.rerun()
            else:
                st.error(ERROR_LOGOUT_FAILED)
        except Exception as e:
            logger.error(f"Logout error: {e}")
            st.error("Logout failed")


class LicensePurchaseUI:
    """License purchase and payment UI."""
    
    def __init__(self):
        self.license_service = LicenseService()
        self.payment_service = MultiPaymentService()
    
    def render_license_purchase(self, upgrade_mode: bool = False, upgrade_plan: str = None):
        """Render license purchase interface."""
        # Define available plans
        plans = {
            'basic_monthly': {
                'name': 'Basic Monthly',
                'price': 9.99,
                'features': ['Basic analysis', 'Standard reports', 'Email support']
            },
            'basic_yearly': {
                'name': 'Basic Yearly',
                'price': 99.99,
                'features': ['Basic analysis', 'Standard reports', 'Email support', '2 months free']
            },
            'pro_monthly': {
                'name': 'Pro Monthly',
                'price': 29.99,
                'features': ['Advanced analysis', 'Premium reports', 'Priority support', 'API access']
            },
            'pro_yearly': {
                'name': 'Pro Yearly',
                'price': 299.99,
                'features': ['Advanced analysis', 'Premium reports', 'Priority support', 'API access', '2 months free']
            }
        }
        
        # Filter plans based on upgrade mode
        if upgrade_mode and upgrade_plan:
            # Show only the selected upgrade plan
            filtered_plans = {upgrade_plan: plans[upgrade_plan]}
            st.info(f"🚀 **Upgrading to {plans[upgrade_plan]['name']}**")
        else:
            # Show all plans
            filtered_plans = plans
            st.info("💳 **Choose Your Plan**")
        
        st.subheader("Available Plans")
        
        # Display plans
        self._render_plan_selection(filtered_plans, upgrade_mode, upgrade_plan)
    
    def _render_plan_selection(self, plans: Dict[str, Any], upgrade_mode: bool, upgrade_plan: str):
        """Render plan selection interface."""
        # Display plans in columns
        if upgrade_mode and upgrade_plan:
            # Pre-select the upgrade plan
            selected_plan = upgrade_plan
            st.session_state[SSK_SELECTED_PLAN] = selected_plan
        else:
            # Let user select plan
            selected_plan = self._render_plan_buttons(plans)
        
        # Show purchase interface if plan selected
        if selected_plan:
            self._render_purchase_interface(selected_plan, plans[selected_plan], upgrade_mode, upgrade_plan)
    
    def _render_plan_buttons(self, plans: Dict[str, Any]) -> str:
        """Render plan selection buttons."""
        selected_plan = None
        
        # Display plans in a grid
        cols = st.columns(len(plans))
        for i, (plan_key, plan) in enumerate(plans.items()):
            with cols[i]:
                st.markdown(f"**{plan['name']}**")
                st.markdown(f"**${plan['price']}**")
                st.markdown("**Features:**")
                for feature in plan['features']:
                    st.markdown(f"• {feature}")
                
                if st.button(LABEL_SELECT_PLAN.format(plan_name=plan['name']), key=f"plan_{plan_key}"):
                    selected_plan = plan_key
                    st.session_state[SSK_SELECTED_PLAN] = selected_plan
        
        return selected_plan or st.session_state.get(SSK_SELECTED_PLAN)
    
    def _render_purchase_interface(self, selected_plan: str, plan_info: Dict[str, Any], upgrade_mode: bool, upgrade_plan: str):
        """Render purchase interface for selected plan."""
        st.markdown("---")
        st.subheader(f"Purchase {plan_info['name']}")
        
        # Get current user
        current_user = st.session_state.get(SSK_CURRENT_USER)
        if not current_user:
            st.error("Please login first")
            return
    
        # Show plan details
        st.markdown(f"**Plan:** {plan_info['name']}")
        st.markdown(f"**Price:** ${plan_info['price']}")
        st.markdown(f"**Features:** {', '.join(plan_info.get('features', []))}")
        
        # Payment gateway selection
        gateway = self._render_payment_gateway_selection()
        
        if gateway:
            self._handle_payment_creation(current_user, selected_plan, gateway, upgrade_mode, upgrade_plan)
    
    def _render_payment_gateway_selection(self) -> str:
        """Render payment gateway selection without switching tabs."""
        st.markdown("**Payment Method:**")
        
        col1, col2, col3 = st.columns(3)
        
        chosen = st.session_state.get(SSK_PAYMENT_GATEWAY)
        with col1:
            if st.button("💳 Stripe", use_container_width=True):
                chosen = 'stripe'
        
        with col2:
            if st.button("🏦 Razorpay", use_container_width=True):
                chosen = 'razorpay'
        
        with col3:
            if st.button("🅿️ PayPal", use_container_width=True):
                chosen = 'paypal'
        
        if chosen:
            st.session_state[SSK_PAYMENT_GATEWAY] = chosen
        
        return chosen
    
    def _handle_payment_creation(self, user: Dict[str, Any], selected_plan: str, gateway: str, upgrade_mode: bool, upgrade_plan: str):
        """Handle payment session creation and redirect."""
        try:
            # Prevent duplicate session creation within a single run
            last_gateway = st.session_state.get(SSK_PAYMENT_GATEWAY)
            existing_session = st.session_state.get(SSK_PAYMENT_SESSION)
            if existing_session and last_gateway == gateway and existing_session.get('plan_type') == selected_plan:
                # We already have a session for this plan and gateway
                redirect_url = self._get_payment_redirect_url(existing_session, gateway)
                if redirect_url:
                    st.session_state[SSK_PAYMENT_REDIRECT_URL] = redirect_url
                    # Immediate redirect via HTML to avoid extra reruns
                    st.markdown(f'<meta http-equiv="refresh" content="0; url={redirect_url}">', unsafe_allow_html=True)
                    return

            # Create payment session
            session = self.payment_service.create_payment_session(
                user_id=user['id'],
                plan_type=selected_plan,
                gateway=gateway
            )
            
            if session:
                # Store upgrade info in session
                if upgrade_mode:
                    session['upgrade_mode'] = True
                    session['upgrade_plan'] = upgrade_plan
                
                # Persist plan_type inside session to use during activation
                session['plan_type'] = selected_plan
                st.session_state[SSK_PAYMENT_SESSION] = session
                st.session_state['last_selected_plan'] = selected_plan
                
                # Get redirect URL
                redirect_url = self._get_payment_redirect_url(session, gateway)
                
                if redirect_url:
                    st.session_state[SSK_PAYMENT_REDIRECT_URL] = redirect_url
                    # Persist selected plan in cookie as a fallback across redirects
                    try:
                        cm = _get_cookie_manager()
                        if cm:
                            cm.set(
                                cookie="selected_plan",
                                val=selected_plan,
                                expires_at=datetime.now() + timedelta(days=2)
                            )
                    except Exception as ce:
                        logger.warning(f"Could not persist selected_plan cookie: {ce}")
                    # Immediate redirect via HTML to avoid duplicate calls on rerun
                    st.markdown(f'<meta http-equiv="refresh" content="0; url={redirect_url}">', unsafe_allow_html=True)
                    return
                else:
                    st.error("Failed to determine payment redirect URL")
            else:
                st.error("Payment processing is not configured")
                st.info(INFO_CONTACT_SUPPORT)
                
        except Exception as e:
            logger.error(f"Payment creation error: {e}")
            st.error(f"Error creating payment: {e}")
    
    def _get_payment_redirect_url(self, session: Dict[str, Any], gateway: str) -> str:
        """Get payment redirect URL based on gateway."""
        if gateway == 'stripe':
            return session.get('payment_url')
        elif gateway == 'razorpay':
            return session.get('payment_url')
        elif gateway == 'paypal':
            return session.get('approval_url')
        return None


# Legacy function exports for backward compatibility
def render_auth_gate():
    """Main authentication gate - legacy function for backward compatibility."""
    auth_ui = AuthUI()
    return auth_ui.render_auth_interface()

def render_auth_interface():
    """Legacy function for backward compatibility."""
    auth_ui = AuthUI()
    return auth_ui.render_auth_interface()

def render_login_page():
    """Legacy function for backward compatibility."""
    auth_ui = AuthUI()
    auth_ui._render_login_register_interface()

def render_register_page():
    """Legacy function for backward compatibility."""
    auth_ui = AuthUI()
    auth_ui._render_login_register_interface()

def render_user_profile():
    """Legacy function for backward compatibility."""
    profile_ui = UserProfileUI()
    profile_ui.render_user_profile()

def render_license_purchase(upgrade_mode: bool = False, upgrade_plan: str = None):
    """Legacy function for backward compatibility."""
    purchase_ui = LicensePurchaseUI()
    purchase_ui.render_license_purchase(upgrade_mode, upgrade_plan)

def render_admin_panel():
    """Render the admin panel."""
    st.title("👨‍💼 Admin Panel")
    st.markdown("---")
    
    current_user = st.session_state.get('current_user')
    if not current_user or not current_user.get('is_admin'):
        st.error("Admin access required")
        return
    
    user_service = UserService()
    license_service = LicenseService()
    
    # User management
    st.subheader("User Management")
    users = user_service.get_all_users()
    
    if users:
        for user in users:
            with st.expander(f"User: {user['username']} ({user['email']})"):
                st.write(f"**ID:** {user['id']}")
                st.write(f"**Admin:** {user['is_admin']}")
                st.write(f"**Created:** {user['created_at']}")
                
                # License info
                license_valid, license_message, license_info = license_service.validate_license(user['id'])
                if license_valid and license_info:
                    st.write(f"**License:** {license_info['plan_type']} (expires: {license_info['expires_at']})")
                else:
                    st.write(f"**License:** {license_message}")
    
    # License management
    st.subheader("License Management")
    if st.button("Create Test License"):
        test_user_id = 1  # Assuming user ID 1 exists
        try:
            license_key = license_service.create_license(test_user_id, 'pro_monthly')
            st.success(f"Test license created: {license_key}")
        except Exception as e:
            st.error(f"Error creating test license: {e}")
