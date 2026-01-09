# AuthX: Plug-and-Play Authentication & Licensing

AuthX is a small, reusable layer for authentication and licensing that you can drop into any Python/Streamlit project.

## What you get
- Core service interfaces independent of UI and storage
- SQLite storage adapter (can be swapped with your own)
- Minimal Streamlit UI wrapper (optional)
- Works with existing `config.AppConfig` settings

## Install dependencies
Make sure `bcrypt` and `stripe` are installed if you need them.

```bash
pip install bcrypt stripe
```

## Quick start (Streamlit)

```python
from authx import AuthX

ax = AuthX()

# Gate your app
if not ax.gate():
    st.title("Login")
    ax.login_form()
    st.stop()

# App content
st.write("Hello, authenticated user!")
```

## Use core services directly

```python
from authx import AuthService, LicenseService, SQLiteAuthStorage
from config import AppConfig

storage = SQLiteAuthStorage()
auth = AuthService(storage, session_timeout_hours=AppConfig.get_auth_settings()['session_timeout_hours'])
lic  = LicenseService(storage, plans=AppConfig.get_auth_settings()['license_plans'])

ok, msg = auth.register_user("alice", "alice@example.com", "secret")
ok, msg, user = auth.login("alice@example.com", "secret")
valid, _, lic_info = lic.validate(user['id'])
```

## Swap storage backend
Implement `AuthStorage` protocol and pass it to `AuthService`/`LicenseService`.

```python
from authx.core.storage import AuthStorage

class MyStorage(AuthStorage):
    ... # implement methods using your DB

storage = MyStorage()
```

## Notes
- AuthX reads plans and session config from `config.AppConfig` where available.
- Stripe webhook integration remains in `auth/stripe_webhook.py` (optional).
- You can continue using your existing `auth/` UI or switch to `authx/integrations/streamlit_ui.py` for minimal UI.
