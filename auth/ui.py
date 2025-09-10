"""
Authentication UI Components

This module contains Streamlit UI components for authentication and licensing.
"""

import streamlit as st
import logging
from typing import Optional, Dict, Any
import webbrowser
from urllib.parse import parse_qs, urlparse

from auth.database import AuthDatabase
from auth.user_service import UserService
from auth.license_service import LicenseService
from auth.oauth_service import OAuthService
from auth.multi_payment_service import MultiPaymentService
from auth.security_service import SecurityService
from auth.constants import (
    PROVIDER_GOOGLE, PROVIDER_MICROSOFT,
    SSK_SESSION_TOKEN, SSK_CURRENT_USER, SSK_AUTH_REDIRECT,
    SSK_OAUTH_PROCESSED, SSK_OAUTH_TIME, SSK_OAUTH_LAST_CODE,
    SSK_OAUTH_INITIATED, SSK_OAUTH_EXPECTED_PROVIDER, SSK_COOKIE_SYNC_DONE,
    SSK_SELECTED_PLAN, SSK_PAYMENT_GATEWAY, SSK_PAYMENT_SESSION, SSK_PAYMENT_REDIRECT_URL,
)
from config import ENABLE_STRIPE_PAYMENTS, ENABLE_SOCIAL_LOGIN, STRIPE_PUBLISHABLE_KEY, AppConfig
from datetime import datetime, timedelta
try:
    import extra_streamlit_components as stx
except Exception:
    stx = None
from auth.constants import (
    TITLE_LOGIN,
    TITLE_REGISTER,
    TITLE_PURCHASE,
    TITLE_PROFILE,
    TITLE_ADMIN,
    SUBHEADER_OR_LOGIN_WITH,
    SUBHEADER_ACCOUNT_INFO,
    SUBHEADER_ACCOUNT_ACTIONS,
    SUBHEADER_CHANGE_PASSWORD,
    LABEL_EMAIL,
    PLACEHOLDER_EMAIL,
    LABEL_PASSWORD,
    PLACEHOLDER_PASSWORD,
    LABEL_REMEMBER_ME,
    LABEL_SELECT_PLAN,
    LABEL_REDIRECT_FALLBACK,
    BUTTON_LOGIN,
    BUTTON_REGISTER,
    BUTTON_BACK_TO_LOGIN,
    BUTTON_LOGIN_GOOGLE,
    BUTTON_LOGIN_MICROSOFT,
    BUTTON_CHANGE_PASSWORD,
    BUTTON_LOGOUT,
    SUCCESS_LOGIN,
    SUCCESS_LOGGED_OUT,
    INFO_REDIRECT_GOOGLE,
    INFO_REDIRECT_MICROSOFT,
    INFO_CONTACT_SUPPORT,
    ERROR_ENTER_EMAIL_PASSWORD,
    ERROR_TOO_MANY_ATTEMPTS,
    ERROR_INVALID_EMAIL,
    ERROR_FILL_ALL_FIELDS,
    ERROR_PASSWORDS_DONT_MATCH,
    ERROR_LOGOUT_FAILED,
    CAPTION_GOOGLE_NOT_CONFIGURED,
    CAPTION_MS_NOT_CONFIGURED
)

logger = logging.getLogger(__name__)

def _get_cookie_manager():
    if not stx:
        return None
    # Use a single, consistent CookieManager instance
    return stx.CookieManager(key="cookie_mgr")

def handle_oauth_callback() -> bool:
    """Handle OAuth callback and return True if callback was processed."""
    try:
        query_params = st.query_params
        if not query_params or 'code' not in query_params or 'state' not in query_params:
            logger.info("No OAuth parameters found, skipping OAuth callback")
            return False
        
        # Check if we've already processed this specific OAuth callback
        current_code = query_params.get('code', '')
        if st.session_state.get(SSK_OAUTH_LAST_CODE) == current_code:
            logger.info("OAuth callback already processed for this code, skipping")
            return False
        
        # Check if the code is too old (authorization codes expire in 10 minutes)
        import time
        current_time = time.time()
        if st.session_state.get(SSK_OAUTH_TIME, 0) > 0:
            if current_time - st.session_state.get(SSK_OAUTH_TIME, 0) > 600:  # 10 minutes
                logger.info("OAuth callback too old, clearing session state")
                for key in [SSK_OAUTH_PROCESSED, SSK_OAUTH_LAST_CODE, SSK_OAUTH_TIME]:
                    if key in st.session_state:
                        del st.session_state[key]
        
        # Additional check: if we're already authenticated, don't process OAuth
        if st.session_state.get(SSK_CURRENT_USER):
            logger.info("User already authenticated, skipping OAuth callback")
            return False
        
        if 'code' in query_params and 'state' in query_params:
            provider = query_params.get('state', '')
            code = query_params.get('code', '')
            
            # Debug logging
            logger.info(f"OAuth callback received: provider='{provider}', code_length={len(code)}")
            # Handle OAuth callback based on provider
            if provider in [PROVIDER_GOOGLE, PROVIDER_MICROSOFT]:
                # Valid provider, proceed with OAuth
                pass
            elif provider == 'g' or (provider.startswith('g') and len(provider) < 10):
                # Google OAuth state parameter is truncated to 'g'
                provider = PROVIDER_GOOGLE
            elif provider.startswith('m') and len(provider) < 10:
                # Only treat as Microsoft if it's clearly truncated (short and starts with 'm')
                provider = PROVIDER_MICROSOFT
            else:
                # Unknown provider, skip
                logger.warning(f"Unknown OAuth provider: {provider}")
                # Clear flags and query params to avoid loops
                st.query_params.clear()
                st.session_state.pop(SSK_OAUTH_INITIATED, None)
                st.session_state.pop(SSK_OAUTH_EXPECTED_PROVIDER, None)
                return False
            
            # Mark this specific code as processed immediately to prevent loops
            st.session_state[SSK_OAUTH_LAST_CODE] = code
            st.session_state[SSK_OAUTH_PROCESSED] = True
            st.session_state[SSK_OAUTH_TIME] = current_time
            
            with st.spinner(f"Completing {provider.title()} login..."):
                oauth_service = OAuthService()
                logger.info(f"Attempting OAuth callback for {provider} with code length: {len(code)}")
                user_info = oauth_service.handle_oauth_callback(provider, code)
                
                if user_info:
                    logger.info(f"OAuth user info received: {user_info.get('email', 'no email')}")
                    
                    user_service = UserService()
                    success, message, session_info = user_service.social_login(provider, user_info)
                    
                    if success:
                        logger.info(f"Social login successful: {message}")
                        
                        # Set session state
                        st.session_state[SSK_SESSION_TOKEN] = session_info['session_token']
                        st.session_state[SSK_CURRENT_USER] = session_info
                        st.session_state[SSK_AUTH_REDIRECT] = False
                        # Persist session in cookie (7 days) to survive reruns/browser refreshes
                        try:
                            mgr = _get_cookie_manager()
                            if mgr:
                                from datetime import datetime, timedelta
                                mgr.set("session_token", session_info['session_token'], expires_at=(datetime.utcnow() + timedelta(days=7)))
                                # Ensure cookie persists before rerun
                                import time as _t
                                _t.sleep(0.4)
                        except Exception:
                            pass

                        # Clear OAuth initiation flags
                        st.session_state.pop(SSK_OAUTH_INITIATED, None)
                        st.session_state.pop(SSK_OAUTH_EXPECTED_PROVIDER, None)
                        
                        # Show success message
                        st.success(f"✅ {provider.title()} login successful! Welcome, {user_info.get('name', user_info.get('email', 'User'))}!")
                        
                        # Clear the query parameters after setting success state
                        st.query_params.clear()
                        
                        # Force a rerun to refresh the page
                        st.rerun()
                        return True
                    else:
                        logger.error(f"Social login failed: {message}")
                        st.error(f"❌ Social login failed: {message}")
                else:
                    logger.error(f"OAuth callback failed for {provider}")
                    if provider == 'microsoft':
                        st.error(f"❌ Microsoft OAuth failed. This is likely due to Azure AD app configuration issues.")
                        st.markdown("""
                        The Microsoft OAuth is failing with `AADSTS70000` error. This indicates an Azure AD app configuration issue.
                        
                        **To fix this:**
                        1. Go to [Azure Portal](https://portal.azure.com/)
                        2. Navigate to Azure Active Directory → App registrations
                        3. Find your app: `8cacdb29-3348-40c9-8f35-56db16cf1286`
                        4. Check these settings:
                           - **Supported account types**: Personal Microsoft accounts only
                           - **Redirect URIs**: `http://localhost:8501`
                           - **API permissions**: `openid`, `email`, `profile`
                           - **Implicit grant**: Disabled
                        
                        **Alternative:** Create a new Azure AD app with the correct settings.
                        """)
                    else:
                        st.error(f"❌ Failed to complete {provider.title()} login")
                # Clear the query parameters on any outcome to prevent reprocessing
                try:
                    st.query_params.clear()
                except Exception:
                    pass
                # Clear OAuth initiation flags regardless of outcome
                st.session_state.pop(SSK_OAUTH_INITIATED, None)
                st.session_state.pop(SSK_OAUTH_EXPECTED_PROVIDER, None)
                # Do not rerun here unconditionally; guard variables already prevent loops
            return True
    except Exception as e:
        logger.error(f"Error handling OAuth callback: {e}")
        st.error(f"❌ OAuth callback error: {e}")
    return False

def render_login_page():
    """Render the login page."""
    st.title(TITLE_LOGIN)
    st.markdown("---")
    
    user_service = UserService()
    oauth_service = OAuthService()
    security_service = SecurityService()
    
    # Login form
    with st.form("login_form"):
        email = st.text_input(LABEL_EMAIL, placeholder=PLACEHOLDER_EMAIL)
        password = st.text_input(LABEL_PASSWORD, type="password", placeholder=PLACEHOLDER_PASSWORD)
        remember = st.checkbox(LABEL_REMEMBER_ME, value=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_button = st.form_submit_button(BUTTON_LOGIN, type="primary")
        with col2:
            st.form_submit_button(BUTTON_REGISTER, on_click=lambda: st.session_state.update({'auth_mode': 'register'}))
    
    # Social login
    if ENABLE_SOCIAL_LOGIN:
        st.markdown("---")
        st.subheader(SUBHEADER_OR_LOGIN_WITH)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if oauth_service.is_configured('google'):
                if st.button(BUTTON_LOGIN_GOOGLE, use_container_width=True):
                    try:
                        # Mark OAuth as user-initiated and expected provider
                        st.session_state[SSK_OAUTH_INITIATED] = True
                        st.session_state[SSK_OAUTH_EXPECTED_PROVIDER] = PROVIDER_GOOGLE
                        auth_url = oauth_service.get_google_auth_url()
                        st.markdown(f"<meta http-equiv='refresh' content='0; url={auth_url}'>", unsafe_allow_html=True)
                        st.markdown(f"<a href='{auth_url}' target='_self'>{LABEL_REDIRECT_FALLBACK}</a>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Google OAuth not configured: {e}")
            else:
                st.button(BUTTON_LOGIN_GOOGLE, use_container_width=True, disabled=True)
                st.caption(CAPTION_GOOGLE_NOT_CONFIGURED)
        
        with col2:
            if oauth_service.is_configured('microsoft'):
                if st.button(BUTTON_LOGIN_MICROSOFT, use_container_width=True):
                    try:
                        st.session_state[SSK_OAUTH_INITIATED] = True
                        st.session_state[SSK_OAUTH_EXPECTED_PROVIDER] = PROVIDER_MICROSOFT
                        auth_url = oauth_service.get_microsoft_auth_url()
                        st.markdown(f"<meta http-equiv='refresh' content='0; url={auth_url}'>", unsafe_allow_html=True)
                        st.markdown(f"<a href='{auth_url}' target='_self'>{LABEL_REDIRECT_FALLBACK}</a>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Microsoft OAuth not configured: {e}")
            else:
                st.button(BUTTON_LOGIN_MICROSOFT, use_container_width=True, disabled=True)
                st.caption(CAPTION_MS_NOT_CONFIGURED)
    
    # Handle login
    if login_button:
        if not email or not password:
            st.error(ERROR_ENTER_EMAIL_PASSWORD)
            return
        
        # Rate limiting
        client_ip = "127.0.0.1"  # In production, get from request
        allowed, remaining, reset_time = security_service.check_rate_limit(f"login:{client_ip}")
        if not allowed:
            st.error(ERROR_TOO_MANY_ATTEMPTS)
            return
        
        security_service.record_request(f"login:{client_ip}")
        
        # Input validation
        if not security_service.validate_email(email):
            st.error(ERROR_INVALID_EMAIL)
            return
        
        success, message, user_info = user_service.login_user(email, password)
        if success:
            st.session_state['session_token'] = user_info['session_token']
            st.session_state['current_user'] = user_info
            st.session_state['auth_redirect'] = False
            # set cookie if enabled
            if stx and remember:
                mgr = stx.CookieManager(key="login_cookie_manager")
                days = AppConfig.get_auth_settings().get('remember_me_days', 30)
                mgr.set("session_token", user_info['session_token'], expires_at=(datetime.utcnow() + timedelta(days=days)))
            st.success(SUCCESS_LOGIN)
            st.rerun()
        else:
            st.error(message)

def render_register_page():
    """Render the registration page."""
    st.title(TITLE_REGISTER)
    st.markdown("---")
    
    user_service = UserService()
    security_service = SecurityService()
    
    # Registration form
    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a username")
        email = st.text_input(LABEL_EMAIL, placeholder=PLACEHOLDER_EMAIL)
        password = st.text_input(LABEL_PASSWORD, type="password", placeholder="Choose a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            register_button = st.form_submit_button(BUTTON_REGISTER, type="primary")
        with col2:
            st.form_submit_button(BUTTON_BACK_TO_LOGIN, on_click=lambda: st.session_state.update({'auth_mode': 'login'}))
    
    # Handle registration
    if register_button:
        if not username or not email or not password:
            st.error(ERROR_FILL_ALL_FIELDS)
            return
        
        if password != confirm_password:
            st.error(ERROR_PASSWORDS_DONT_MATCH)
            return
        
        # Input validation
        username_valid, username_error = security_service.validate_username(username)
        if not username_valid:
            st.error(username_error)
            return
        
        if not security_service.validate_email(email):
            st.error(ERROR_INVALID_EMAIL)
            return
        
        password_valid, password_error = security_service.validate_password_strength(password)
        if not password_valid:
            st.error(password_error)
            return
        
        # Sanitize inputs
        username = security_service.sanitize_input(username)
        email = security_service.sanitize_input(email)
        
        success, message = user_service.register_user(username, email, password)
        if success:
            st.success(message)
            st.session_state['auth_mode'] = 'login'
            st.rerun()
        else:
            st.error(message)

def render_license_purchase():
    """Render the license purchase page."""
    st.title(TITLE_PURCHASE)
    st.markdown("---")
    # Handle pending payment redirect from previous click
    pending_redirect = st.session_state.get(SSK_PAYMENT_REDIRECT_URL)
    if pending_redirect:
        st.success("Redirecting to payment page...")
        # Use top-level meta refresh and a direct link fallback; avoid sandboxed iframes
        st.markdown(f"<meta http-equiv='refresh' content='0; url={pending_redirect}'>", unsafe_allow_html=True)
        st.markdown(f"<a href='{pending_redirect}' target='_self'>{LABEL_REDIRECT_FALLBACK}</a>", unsafe_allow_html=True)
        # Do not clear immediately to avoid flicker; let the navigation replace page
        return

    # Handle purchase success callback (fallback when webhooks are not configured)
    try:
        qp = st.query_params
        if qp.get('purchase') == 'success':
            current_user = st.session_state.get(SSK_CURRENT_USER)
            selected_plan = st.session_state.get(SSK_SELECTED_PLAN)
            if current_user and selected_plan:
                license_service = LicenseService()
                try:
                    license_key = license_service.create_license(current_user['id'], selected_plan)
                    st.success(f"License activated successfully: {license_key}")
                except Exception as e:
                    st.error(f"Failed to activate license: {e}")
            # Clean up payment-related state and query params
            for key in [SSK_PAYMENT_SESSION, SSK_PAYMENT_REDIRECT_URL, SSK_SELECTED_PLAN, SSK_PAYMENT_GATEWAY]:
                if key in st.session_state:
                    del st.session_state[key]
            st.query_params.clear()
            st.rerun()
            return
    except Exception:
        pass

    payment_service = MultiPaymentService()
    plans = payment_service.get_available_plans()
    
    if not plans:
        st.error("No license plans available")
        return
    
    st.subheader("Available Plans")
    
    # Display plans in columns
    cols = st.columns(len(plans))
    selected_plan = None
    
    for i, (plan_key, plan) in enumerate(plans.items()):
        with cols[i]:
            st.markdown(f"### {plan['name']}")
            st.markdown(f"**${plan['price']}** / {plan.get('period', 'month')}")
            
            # Features
            for feature in plan.get('features', []):
                st.markdown(f"✅ {feature}")
            
            if st.button(LABEL_SELECT_PLAN.format(plan_name=plan['name']), key=f"plan_{plan_key}"):
                selected_plan = plan_key
                st.session_state[SSK_SELECTED_PLAN] = selected_plan
    
    selected_plan = selected_plan or st.session_state.get(SSK_SELECTED_PLAN)
    if selected_plan:
        st.markdown("---")
        st.subheader(f"Purchase {plans[selected_plan]['name']}")
        
        # Get current user
        current_user = st.session_state.get(SSK_CURRENT_USER)
        if not current_user:
            st.error("Please login first")
            return
        
        user_id = current_user['id']
        
        # Select payment gateway
        gateways = payment_service.get_available_gateways()
        available = [g for g, ok in gateways.items() if ok]
        if not available:
            st.error("Payment processing is not configured")
            st.info(INFO_CONTACT_SUPPORT)
            return
        gateway = st.selectbox("Payment Gateway", options=available, index=available.index(st.session_state.get(SSK_PAYMENT_GATEWAY, available[0])) if st.session_state.get(SSK_PAYMENT_GATEWAY) in available else 0)
        st.session_state[SSK_PAYMENT_GATEWAY] = gateway
        
        # Create payment session via selected/recommended gateway
        import os
        base_url = os.getenv("APP_BASE_URL", "http://localhost:8501")
        success_url = f"{base_url}/?purchase=success"
        cancel_url = f"{base_url}/?purchase=cancelled"
        
        session = st.session_state.get(SSK_PAYMENT_SESSION)
        if not session or session.get('gateway') != gateway or session.get('plan') != selected_plan:
            try:
                session = payment_service.create_payment_session(
                    user_id=user_id,
                    plan_type=selected_plan,
                    gateway=gateway
                )
                if session:
                    session['plan'] = selected_plan
                    st.session_state[SSK_PAYMENT_SESSION] = session
            except Exception as e:
                st.error(f"Error creating checkout session: {e}")
                session = None
        
        if session:
            st.markdown(f"**Plan:** {plans[selected_plan]['name']}")
            st.markdown(f"**Price:** ${plans[selected_plan]['price']}")
            st.markdown(f"**Features:** {', '.join(plans[selected_plan].get('features', []))}")
            
            if st.button("💳 Proceed to Payment", type="primary"):
                # Determine redirect URL from session based on gateway
                redirect_url = None
                if session.get('gateway') == 'stripe':
                    redirect_url = session.get('checkout_url')
                elif session.get('gateway') == 'razorpay':
                    redirect_url = session.get('payment_url')
                elif session.get('gateway') == 'paypal':
                    redirect_url = session.get('approval_url')
                
                if redirect_url:
                    st.session_state[SSK_PAYMENT_REDIRECT_URL] = redirect_url
                    st.rerun()
                else:
                    st.error("Failed to determine payment redirect URL")
        else:
            st.error("Payment processing is not configured")
            st.info(INFO_CONTACT_SUPPORT)

def render_user_profile():
    """Render the user profile page."""
    st.title(TITLE_PROFILE)
    st.markdown("---")
    
    current_user = st.session_state.get('current_user')
    if not current_user:
        st.error("Please login first")
        return
    
    user_service = UserService()
    license_service = LicenseService()
    
    # User info
    st.subheader(SUBHEADER_ACCOUNT_INFO)
    col1, col2 = st.columns(2)
        
    with col1:
        st.markdown(f"**Username:** {current_user['username']}")
        st.markdown(f"**Email:** {current_user['email']}")
        st.markdown(f"**Account Type:** {'Admin' if current_user['is_admin'] else 'User'}")
    
    with col2:
        # License information
        license_valid, license_message, license_info = license_service.validate_license(current_user['id'])
        
        if license_valid and license_info:
            st.markdown(f"**License Status:** ✅ Active")
            st.markdown(f"**Plan:** {license_info['plan_type']}")
            st.markdown(f"**Expires:** {license_info['expires_at']}")
        else:
            st.markdown("**License Status:** ❌ No active license")
            st.markdown(f"**Message:** {license_message}")
    
    # License purchase section
    if not license_valid:
        st.markdown("---")
        st.subheader(TITLE_PURCHASE)
        render_license_purchase()
    
    # Profile actions
    st.markdown("---")
    st.subheader(SUBHEADER_ACCOUNT_ACTIONS)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(BUTTON_CHANGE_PASSWORD):
            st.session_state['profile_action'] = 'change_password'
    
    with col2:
        if st.button(BUTTON_LOGOUT):
            if user_service.logout_user(current_user['session_token']):
                st.session_state.clear()
                st.success(SUCCESS_LOGGED_OUT)
                st.rerun()
            else:
                st.error(ERROR_LOGOUT_FAILED)
    
    # Change password form
    if st.session_state.get('profile_action') == 'change_password':
        st.markdown("---")
        st.subheader(SUBHEADER_CHANGE_PASSWORD)
        
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Change Password"):
                if new_password != confirm_new_password:
                    st.error(ERROR_PASSWORDS_DONT_MATCH)
                else:
                    success, message = user_service.change_password(
                        current_user['id'], current_password, new_password
                    )
                    if success:
                        st.success(message)
                        st.session_state.pop('profile_action', None)
                    else:
                        st.error(message)

def render_admin_panel():
    """Render the admin panel."""
    st.title("👨‍💼 Admin Panel")
    st.markdown("---")
    
    current_user = st.session_state.get('current_user')
    if not current_user or not current_user.get('is_admin'):
        st.error("Admin access required")
        return
    
    user_service = UserService()
    
    # Admin tabs
    tab1, tab2, tab3 = st.tabs(["👥 Users", "🔑 Licenses", "📊 Statistics"])
    
    with tab1:
        st.subheader("User Management")
        
        # Get all users
        users = user_service.get_all_users()
        
        if users:
            # Create a DataFrame for display
            import pandas as pd
            df = pd.DataFrame(users)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['is_active'] = df['is_active'].astype(str)
            df['is_admin'] = df['is_admin'].astype(str)
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users found")
    
    with tab2:
        st.subheader("License Management")
        
        # License management interface
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Create License**")
            
            # Get all users for dropdown
            users = user_service.get_all_users()
            user_options = {f"{u['username']} ({u['email']})": u['id'] for u in users}
            
            selected_user = st.selectbox("Select User", options=list(user_options.keys()))
            plan_type = st.selectbox("Plan Type", options=["basic", "premium", "enterprise"])
            
            if st.button("Create License"):
                if selected_user and plan_type:
                    user_id = user_options[selected_user]
                    license_service = LicenseService()
                    try:
                        license_key = license_service.create_license(user_id, plan_type)
                        st.success(f"License created: {license_key}")
                    except Exception as e:
                        st.error(f"Failed to create license: {e}")
        
        with col2:
            st.markdown("**System Actions**")
            
            if st.button("🧹 Cleanup Expired Sessions"):
                user_service.cleanup_expired_sessions()
                st.success("Expired sessions cleaned up")
    
    with tab3:
        st.subheader("System Statistics")
        
        # Basic statistics
        users = user_service.get_all_users()
        total_users = len(users)
        active_users = len([u for u in users if u['is_active']])
        admin_users = len([u for u in users if u['is_admin']])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", total_users)
        
        with col2:
            st.metric("Active Users", active_users)
    
    with col3:
            st.metric("Admin Users", admin_users)

def render_auth_gate():
    """Render the authentication gate - main entry point for auth."""
    # Check if authentication is enabled from config
    if not AppConfig.get_auth_settings().get('enabled', False):
        return True  # Skip authentication if disabled
    
    # Handle OAuth callback first (before clearing state)
    query_params = st.query_params
    if query_params and len(query_params) > 0 and 'code' in query_params and 'state' in query_params:
        # Only process OAuth callback if we have valid parameters
        logger.info(f"Processing OAuth callback with parameters: {list(query_params.keys())}")
        if handle_oauth_callback():
            st.rerun()  # Refresh the page after OAuth callback
            return True  # Exit early after successful OAuth
    else:
        logger.info("No OAuth parameters found, skipping OAuth callback processing")
    
    # Only clear payment flags if not authenticated and not in a payment flow
    current_user = st.session_state.get(SSK_CURRENT_USER)
    if not current_user:
        try:
            qp = st.query_params
            returning_from_payment = qp.get('purchase') in ('success', 'cancelled') or qp.get('payment') in ('success', 'cancelled') or qp.get('subscription') in ('success', 'cancelled')
            if not returning_from_payment:
                for key in [SSK_PAYMENT_REDIRECT_URL, SSK_PAYMENT_SESSION, SSK_SELECTED_PLAN, SSK_PAYMENT_GATEWAY]:
                    st.session_state.pop(key, None)
        except Exception:
            pass
    
    # Check if user is already authenticated
    current_user = st.session_state.get(SSK_CURRENT_USER)
    if current_user:
        # Show user info and logout option
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"✅ Welcome back, {current_user.get('name', current_user.get('email', 'User'))}!")
        with col2:
            if st.button("🚪 Logout", key="logout_btn"):
                # Clear session state
                for key in [SSK_CURRENT_USER, SSK_SESSION_TOKEN, SSK_AUTH_REDIRECT, SSK_OAUTH_PROCESSED, SSK_OAUTH_LAST_CODE, SSK_OAUTH_TIME, SSK_OAUTH_INITIATED, SSK_OAUTH_EXPECTED_PROVIDER, SSK_COOKIE_SYNC_DONE, SSK_PAYMENT_REDIRECT_URL, SSK_PAYMENT_SESSION, SSK_SELECTED_PLAN, SSK_PAYMENT_GATEWAY]:
                    if key in st.session_state:
                        del st.session_state[key]
                # Clear cookies
                if stx:
                    try:
                        mgr = _get_cookie_manager()
                        if mgr:
                            # Delete if present
                            existing = mgr.get("session_token")
                            if existing:
                                try:
                                    mgr.delete("session_token")
                                except Exception:
                                    pass
                            # Force-expire cookie as fallback
                            from datetime import datetime, timedelta
                            mgr.set("session_token", "", expires_at=(datetime.utcnow() - timedelta(days=1)))
                            # Wait for cookie deletion to persist
                            import time as _t
                            _t.sleep(0.4)
                    except Exception:
                        pass
                    # Clear query parameters
                    st.query_params.clear()
                    st.rerun()
        return True  # User is authenticated
    
    # Check for session token in cookies
    if stx:
        try:
            mgr = _get_cookie_manager()
            session_token = mgr.get("session_token") if mgr else None
            if session_token and not st.session_state.get(SSK_CURRENT_USER):
                # Validate session token
                st.session_state[SSK_SESSION_TOKEN] = session_token
                user_service = UserService()
                user = user_service.get_current_user()
                if user:
                    st.session_state[SSK_CURRENT_USER] = user
                    st.rerun()  # Refresh to show authenticated state
                    return True
        except Exception as e:
            logger.warning(f"Error reading session cookie: {e}")
    
    # User is not authenticated, show auth interface
    st.session_state[SSK_AUTH_REDIRECT] = True
    
    # Check for auth mode
    auth_mode = st.session_state.get('auth_mode', 'login')
    
    if auth_mode == 'login':
        render_login_page()
    elif auth_mode == 'register':
        render_register_page()
    else:
        render_login_page()
    
    return False  # Authentication required
