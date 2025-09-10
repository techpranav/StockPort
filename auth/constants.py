"""
Authentication module constants

All auth-related user-facing strings live here to keep the auth module self-contained
and reusable across projects without depending on project-wide constants.
"""

# Titles and Headers
TITLE_LOGIN = "🔐 Login to Stockport"
TITLE_REGISTER = "📝 Register for Stockport"
TITLE_PURCHASE = "💳 Purchase License"
TITLE_PROFILE = "👤 User Profile"
TITLE_ADMIN = "👨‍💼 Admin Panel"
SUBHEADER_OR_LOGIN_WITH = "Or login with:"
SUBHEADER_ACCOUNT_INFO = "Account Information"
SUBHEADER_ACCOUNT_ACTIONS = "Account Actions"
SUBHEADER_CHANGE_PASSWORD = "Change Password"

# Labels and Placeholders
LABEL_EMAIL = "Email"
PLACEHOLDER_EMAIL = "Enter your email"
LABEL_PASSWORD = "Password"
PLACEHOLDER_PASSWORD = "Enter your password"
LABEL_REMEMBER_ME = "Remember me"
LABEL_SELECT_PLAN = "Select {plan_name}"
LABEL_REDIRECT_FALLBACK = "Click here if not redirected"

# Buttons
BUTTON_LOGIN = "Login"
BUTTON_REGISTER = "Register"
BUTTON_BACK_TO_LOGIN = "Back to Login"
BUTTON_LOGIN_GOOGLE = "🔍 Login with Google"
BUTTON_LOGIN_MICROSOFT = "📧 Login with Microsoft"
BUTTON_CHANGE_PASSWORD = "🔑 Change Password"
BUTTON_LOGOUT = "🚪 Logout"

# Info / Status
SUCCESS_LOGIN = "Login successful!"
SUCCESS_LOGGED_OUT = "Logged out successfully"
INFO_REDIRECT_GOOGLE = "Redirecting to Google sign-in..."
INFO_REDIRECT_MICROSOFT = "Redirecting to Microsoft sign-in..."
INFO_CONTACT_SUPPORT = "Please contact support to purchase a license"

# Errors / Warnings
ERROR_ENTER_EMAIL_PASSWORD = "Please enter both email and password"
ERROR_TOO_MANY_ATTEMPTS = "Too many login attempts. Please try again later."
ERROR_INVALID_EMAIL = "Please enter a valid email address"
ERROR_FILL_ALL_FIELDS = "Please fill in all fields"
ERROR_PASSWORDS_DONT_MATCH = "Passwords do not match"
ERROR_LOGOUT_FAILED = "Logout failed"
CAPTION_GOOGLE_NOT_CONFIGURED = "Google OAuth not configured"
CAPTION_MS_NOT_CONFIGURED = "Microsoft OAuth not configured"

# Providers and Scopes
PROVIDER_GOOGLE = "google"
PROVIDER_MICROSOFT = "microsoft"
GOOGLE_SCOPE = "openid email profile"
MS_SCOPE = "openid profile email offline_access User.Read"

# Session state keys
SSK_SESSION_TOKEN = "session_token"
SSK_CURRENT_USER = "current_user"
SSK_AUTH_REDIRECT = "auth_redirect"
SSK_OAUTH_PROCESSED = "oauth_callback_processed"
SSK_OAUTH_TIME = "oauth_callback_time"
SSK_OAUTH_LAST_CODE = "last_processed_code"
SSK_OAUTH_INITIATED = "oauth_initiated"
SSK_OAUTH_EXPECTED_PROVIDER = "oauth_expected_provider"
SSK_COOKIE_SYNC_DONE = "cookie_sync_done"

# Payment-related session keys
SSK_SELECTED_PLAN = "auth_selected_plan"
SSK_PAYMENT_SESSION = "auth_payment_session"
SSK_PAYMENT_GATEWAY = "auth_payment_gateway"
SSK_PAYMENT_REDIRECT_URL = "auth_payment_redirect_url"
