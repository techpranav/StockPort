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
from auth.payment_service import PaymentService
from auth.security_service import SecurityService
from config import ENABLE_STRIPE_PAYMENTS, ENABLE_SOCIAL_LOGIN, STRIPE_PUBLISHABLE_KEY, AppConfig
from datetime import datetime, timedelta
try:
    import extra_streamlit_components as stx
except Exception:
    stx = None

logger = logging.getLogger(__name__)

def handle_oauth_callback() -> bool:
    """Handle OAuth callback and return True if callback was processed."""
    try:
        query_params = st.query_params
        if not query_params or 'code' not in query_params or 'state' not in query_params:
            logger.info("No OAuth parameters found, skipping OAuth callback")
            return False
        
        # Check if we've already processed this specific OAuth callback
        current_code = query_params.get('code', '')
        if st.session_state.get('last_processed_code') == current_code:
            logger.info("OAuth callback already processed for this code, skipping")
            return False
        
        # Check if the code is too old (authorization codes expire in 10 minutes)
        import time
        current_time = time.time()
        if st.session_state.get('oauth_callback_time', 0) > 0:
            if current_time - st.session_state.get('oauth_callback_time', 0) > 600:  # 10 minutes
                logger.info("OAuth callback too old, clearing session state")
                for key in ['oauth_callback_processed', 'last_processed_code', 'oauth_callback_time']:
                    if key in st.session_state:
                        del st.session_state[key]
        
        # Additional check: if we're already authenticated, don't process OAuth
        if st.session_state.get('current_user'):
            logger.info("User already authenticated, skipping OAuth callback")
            return False
        
        if 'code' in query_params and 'state' in query_params:
            provider = query_params.get('state', '')
            code = query_params.get('code', '')
            
            # Debug logging
            logger.info(f"OAuth callback received: provider='{provider}', code_length={len(code)}")
            st.info(f"🔍 Debug: OAuth callback received for '{provider}'")
            st.info(f"🔍 Debug: Raw state parameter: {query_params.get('state', '')}")
            st.info(f"🔍 Debug: Raw code parameter: {query_params.get('code', '')}")
            st.info(f"🔍 Debug: Provider length: {len(provider)}")
            
            # Handle OAuth callback based on provider
            if provider in ['google', 'microsoft']:
                # Valid provider, proceed with OAuth
                pass
            elif provider == 'g' or (provider.startswith('g') and len(provider) < 10):
                # Google OAuth state parameter is truncated to 'g'
                provider = 'google'
                st.info(f"🔍 Debug: Corrected provider to 'google' from truncated state")
            elif provider.startswith('m') and len(provider) < 10:
                # Only treat as Microsoft if it's clearly truncated (short and starts with 'm')
                provider = 'microsoft'
                st.info(f"🔍 Debug: Corrected provider to 'microsoft' from truncated state")
            else:
                # Unknown provider, skip
                logger.warning(f"Unknown OAuth provider: {provider}")
                # Clear flags and query params to avoid loops
                st.query_params.clear()
                st.session_state.pop('oauth_initiated', None)
                st.session_state.pop('oauth_expected_provider', None)
                return False
            
            # Mark this specific code as processed immediately to prevent loops
            st.session_state['last_processed_code'] = code
            st.session_state['oauth_callback_processed'] = True
            st.session_state['oauth_callback_time'] = current_time
            
            with st.spinner(f"Completing {provider.title()} login..."):
                oauth_service = OAuthService()
                logger.info(f"Attempting OAuth callback for {provider} with code length: {len(code)}")
                user_info = oauth_service.handle_oauth_callback(provider, code)
                
                if user_info:
                    logger.info(f"OAuth user info received: {user_info.get('email', 'no email')}")
                    st.info(f"🔍 Debug: User info received: {user_info.get('email', 'no email')}")
                    
                    user_service = UserService()
                    success, message, session_info = user_service.social_login(provider, user_info)
                    
                    if success:
                        logger.info(f"Social login successful: {message}")
                        
                        # Set session state
                        st.session_state['session_token'] = session_info['session_token']
                        st.session_state['current_user'] = session_info
                        st.session_state['auth_redirect'] = False
                        # Persist session in cookie (7 days) to survive reruns/browser refreshes
                        if stx:
                            try:
                                mgr = stx.CookieManager(key="social_login_cookie_manager")
                                from datetime import datetime, timedelta
                                mgr.set("session_token", session_info['session_token'], expires_at=(datetime.utcnow() + timedelta(days=7)))
                            except Exception:
                                pass

                        # Clear the query parameters to avoid reprocessing
                        st.query_params.clear()
                        # Clear OAuth initiation flags
                        st.session_state.pop('oauth_initiated', None)
                        st.session_state.pop('oauth_expected_provider', None)
                        
                        # Show success message
                        st.success(f"✅ {provider.title()} login successful! Welcome, {user_info.get('name', user_info.get('email', 'User'))}!")
                        
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
                        st.warning("🔧 **Microsoft OAuth Troubleshooting:**")
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
                st.session_state.pop('oauth_initiated', None)
                st.session_state.pop('oauth_expected_provider', None)
                # Do not rerun here unconditionally; guard variables already prevent loops
            return True
    except Exception as e:
        logger.error(f"Error handling OAuth callback: {e}")
        st.error(f"❌ OAuth callback error: {e}")
    return False

def render_login_page():
    """Render the login page."""
    st.title("🔐 Login to Stockport")
    st.markdown("---")
    
    user_service = UserService()
    oauth_service = OAuthService()
    security_service = SecurityService()
    
    # Login form
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        remember = st.checkbox("Remember me", value=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_button = st.form_submit_button("Login", type="primary")
        with col2:
            st.form_submit_button("Register", on_click=lambda: st.session_state.update({'auth_mode': 'register'}))
    
    # Social login
    if ENABLE_SOCIAL_LOGIN:
        st.markdown("---")
        st.subheader("Or login with:")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if oauth_service.is_configured('google'):
                if st.button("🔍 Login with Google", use_container_width=True):
                    try:
                        # Mark OAuth as user-initiated and expected provider
                        st.session_state['oauth_initiated'] = True
                        st.session_state['oauth_expected_provider'] = 'google'
                        auth_url = oauth_service.get_google_auth_url()
                        webbrowser.open(auth_url)
                        st.info("Please complete the Google login in your browser")
                    except Exception as e:
                        st.error(f"Google OAuth not configured: {e}")
            else:
                st.button("🔍 Login with Google", use_container_width=True, disabled=True)
                st.caption("Google OAuth not configured")
        
        with col2:
            if oauth_service.is_configured('microsoft'):
                if st.button("📧 Login with Microsoft", use_container_width=True):
                    try:
                        st.session_state['oauth_initiated'] = True
                        st.session_state['oauth_expected_provider'] = 'microsoft'
                        auth_url = oauth_service.get_microsoft_auth_url()
                        webbrowser.open(auth_url)
                        st.info("Please complete the Microsoft login in your browser")
                    except Exception as e:
                        st.error(f"Microsoft OAuth not configured: {e}")
            else:
                st.button("📧 Login with Microsoft", use_container_width=True, disabled=True)
                st.caption("Microsoft OAuth not configured")
    
    # Handle login
    if login_button:
        if not email or not password:
            st.error("Please enter both email and password")
            return
        
        # Rate limiting
        client_ip = "127.0.0.1"  # In production, get from request
        allowed, remaining, reset_time = security_service.check_rate_limit(f"login:{client_ip}")
        if not allowed:
            st.error(f"Too many login attempts. Please try again later.")
            return
        
        security_service.record_request(f"login:{client_ip}")
        
        # Input validation
        if not security_service.validate_email(email):
            st.error("Please enter a valid email address")
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
            st.success("Login successful!")
            st.rerun()
        else:
            st.error(message)

def render_register_page():
    """Render the registration page."""
    st.title("📝 Register for Stockport")
    st.markdown("---")
    
    user_service = UserService()
    security_service = SecurityService()
    
    # Registration form
    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a username")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Choose a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            register_button = st.form_submit_button("Register", type="primary")
        with col2:
            st.form_submit_button("Back to Login", on_click=lambda: st.session_state.update({'auth_mode': 'login'}))
    
    # Handle registration
    if register_button:
        if not username or not email or not password:
            st.error("Please fill in all fields")
            return
        
        if password != confirm_password:
            st.error("Passwords do not match")
            return
        
        # Input validation
        username_valid, username_error = security_service.validate_username(username)
        if not username_valid:
            st.error(username_error)
            return
        
        if not security_service.validate_email(email):
            st.error("Please enter a valid email address")
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
    st.title("💳 Purchase License")
    st.markdown("---")
    
    payment_service = PaymentService()
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
            
            if st.button(f"Select {plan['name']}", key=f"plan_{plan_key}"):
                selected_plan = plan_key
    
    if selected_plan:
        st.markdown("---")
        st.subheader(f"Purchase {plans[selected_plan]['name']}")
        
        # Get current user
        current_user = st.session_state.get('current_user')
        if not current_user:
            st.error("Please login first")
            return
        
        user_id = current_user['id']
        
        # Create checkout session
        if ENABLE_STRIPE_PAYMENTS and STRIPE_PUBLISHABLE_KEY:
            success_url = f"{st.get_option('server.baseUrlPath')}?purchase=success"
            cancel_url = f"{st.get_option('server.baseUrlPath')}?purchase=cancelled"
            
            checkout_url = payment_service.create_checkout_session(
                user_id=user_id,
                plan_type=selected_plan,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            if checkout_url:
                st.markdown(f"**Plan:** {plans[selected_plan]['name']}")
                st.markdown(f"**Price:** ${plans[selected_plan]['price']}")
                st.markdown(f"**Features:** {', '.join(plans[selected_plan].get('features', []))}")
                
                if st.button("💳 Proceed to Payment", type="primary"):
                    webbrowser.open(checkout_url)
                    st.success("Redirecting to payment page...")
                else:
                    st.error("Failed to create payment session")
            else:
                st.error("Payment processing is not configured")
                st.info("Please contact support to purchase a license")

def render_user_profile():
    """Render the user profile page."""
    st.title("👤 User Profile")
    st.markdown("---")
    
    current_user = st.session_state.get('current_user')
    if not current_user:
        st.error("Please login first")
        return
    
    user_service = UserService()
    license_service = LicenseService()
    
    # User info
    st.subheader("Account Information")
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
        st.subheader("Purchase License")
        render_license_purchase()
    
    # Profile actions
    st.markdown("---")
    st.subheader("Account Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔑 Change Password"):
            st.session_state['profile_action'] = 'change_password'
    
    with col2:
        if st.button("🚪 Logout"):
            if user_service.logout_user(current_user['session_token']):
                st.session_state.clear()
                st.success("Logged out successfully")
                st.rerun()
            else:
                st.error("Logout failed")
    
    # Change password form
    if st.session_state.get('profile_action') == 'change_password':
        st.markdown("---")
        st.subheader("Change Password")
        
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Change Password"):
                if new_password != confirm_new_password:
                    st.error("New passwords do not match")
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
            plan_type = st.selectbox("Plan Type", options=list(LICENSE_PLANS.keys()))
            
            if st.button("Create License"):
                if selected_user and plan_type:
                    user_id = user_options[selected_user]
                    license_service = LicenseService(storage)
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
    
    # Handle OAuth callback first (before authentication gate)
    # Only process if there are actual OAuth parameters
    query_params = st.query_params
    if query_params and len(query_params) > 0 and 'code' in query_params and 'state' in query_params:
        # Only process OAuth callback if we have valid parameters
        logger.info(f"Processing OAuth callback with parameters: {list(query_params.keys())}")
        if handle_oauth_callback():
            st.rerun()  # Refresh the page after OAuth callback
    else:
        logger.info("No OAuth parameters found, skipping OAuth callback processing")
    
    # Check if user is already authenticated
    current_user = st.session_state.get('current_user')
    if current_user:
        # Show user info and logout option
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"✅ Welcome back, {current_user.get('name', current_user.get('email', 'User'))}!")
        with col2:
            if st.button("🚪 Logout", key="logout_btn"):
                # Clear session state
                for key in ['current_user', 'session_token', 'auth_redirect', 'oauth_callback_processed', 'last_processed_code', 'oauth_callback_time', 'oauth_initiated', 'oauth_expected_provider']:
                    if key in st.session_state:
                        del st.session_state[key]
                # Clear cookies
                if stx:
                    try:
                        mgr = stx.CookieManager(key="auth_gate_cookie_manager")
                        mgr.delete("session_token")
                    except Exception as e:
                        logger.warning(f"Error clearing session cookie: {e}")
                # Clear query parameters
                st.query_params.clear()
                st.rerun()
        return True  # User is authenticated
    
    # Check for session token in cookies
    if stx:
        try:
            mgr = stx.CookieManager(key="auth_gate_cookie_manager")
            session_token = mgr.get("session_token")
            if session_token:
                # Validate session token
                # Ensure session_state is populated from cookie before validation
                st.session_state['session_token'] = session_token
                user_service = UserService()
                user = user_service.get_current_user()
                if user:
                    st.session_state['current_user'] = user
                    st.rerun()  # Refresh to show authenticated state
                    return True
        except Exception as e:
            logger.warning(f"Error reading session cookie: {e}")
    
    # User is not authenticated, show auth interface
    st.session_state['auth_redirect'] = True
    
    # Check for auth mode
    auth_mode = st.session_state.get('auth_mode', 'login')
    
    if auth_mode == 'login':
        render_login_page()
    elif auth_mode == 'register':
        render_register_page()
    else:
        render_login_page()
    
    return False  # Authentication required
