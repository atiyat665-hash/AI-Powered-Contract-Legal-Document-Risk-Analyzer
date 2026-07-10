# Authentication System Guide

## Overview

The Contract Risk Analyzer uses a simple, secure session-based authentication system built with:
- **bcrypt** for password hashing
- **Streamlit session_state** for session management
- **SQLAlchemy ORM** for database operations
- **SQLite** for data storage

## Architecture

### Files
```
auth/
├── __init__.py
└── auth_utils.py          # Core authentication functions

database/
├── models.py              # User model definition
└── db.py                  # Database configuration

app.py                     # Main app with login/register UI
```

## Core Functions

### Password Management

#### `hash_password(password: str) -> str`
Hashes a plain text password using bcrypt with automatic salt generation.

```python
from auth.auth_utils import hash_password

hashed = hash_password("mypassword")
# Returns: "$2b$12$..."
```

#### `verify_password(plain_password: str, hashed_password: str) -> bool`
Verifies a plain text password against a hashed password.

```python
from auth.auth_utils import verify_password

is_valid = verify_password("mypassword", hashed_password)
# Returns: True or False
```

### User Registration

#### `register_user(username: str, email: str, password: str, role: str = "user") -> tuple[bool, str]`
Registers a new user with validation checks.

**Validations:**
- Email format validation
- Password minimum length (6 characters)
- Duplicate username check
- Duplicate email check
- Role validation (user/admin)

**Returns:** `(success: bool, message: str)`

```python
from auth.auth_utils import register_user

success, message = register_user(
    username="john_doe",
    email="john@example.com",
    password="secure123",
    role="user"
)

if success:
    print(message)  # "User 'john_doe' registered successfully!"
else:
    print(message)  # Error message
```

### User Login

#### `login_user(username: str, password: str) -> tuple[bool, dict, str]`
Authenticates a user and returns their data.

**Returns:** `(success: bool, user_data: dict, message: str)`

```python
from auth.auth_utils import login_user

success, user_data, message = login_user("john_doe", "secure123")

if success:
    print(f"Logged in as: {user_data['username']}")
    print(f"Role: {user_data['role']}")
    print(f"User ID: {user_data['id']}")
else:
    print(message)  # "Invalid username or password"
```

### Helper Functions

#### `validate_email(email: str) -> bool`
Validates email format using regex.

```python
from auth.auth_utils import validate_email

is_valid = validate_email("user@example.com")  # True
is_valid = validate_email("invalid.email")      # False
```

#### `validate_password(password: str) -> tuple[bool, str]`
Validates password strength.

```python
from auth.auth_utils import validate_password

is_valid, error_msg = validate_password("12345")
# Returns: (False, "Password must be at least 6 characters long")
```

#### `get_user_by_id(user_id: int) -> dict`
Retrieves user information by ID.

```python
from auth.auth_utils import get_user_by_id

user = get_user_by_id(1)
if user:
    print(user['username'])
```

#### `seed_admin_user() -> bool`
Creates default admin user if no users exist.

## Session Management

### Session State Variables

The app tracks authentication state using `st.session_state`:

```python
st.session_state.logged_in = True          # Authentication status
st.session_state.user_id = 1               # Database user ID
st.session_state.username = "john_doe"     # Username
st.session_state.email = "john@example.com" # Email
st.session_state.role = "user"             # Role (user/admin)
st.session_state.created_at = datetime(...)  # Account creation
```

### Login Flow

1. User submits username and password
2. `login_user()` authenticates credentials
3. On success: populate `session_state` and call `st.rerun()`
4. On failure: display error message

```python
success, user_data, message = login_user(username, password)

if success:
    st.session_state.logged_in = True
    st.session_state.user_id = user_data['id']
    st.session_state.username = user_data['username']
    st.session_state.email = user_data['email']
    st.session_state.role = user_data['role']
    st.session_state.created_at = user_data['created_at']
    st.rerun()
else:
    st.error(message)
```

### Registration Flow

1. User submits registration form with validation
2. Check all fields are filled
3. Validate email format
4. Check password length
5. Verify passwords match
6. Call `register_user()`
7. Display success/error message

```python
if reg_password != reg_confirm_password:
    st.error("Passwords do not match")
else:
    success, message = register_user(username, email, password)
    if success:
        st.success(message)
    else:
        st.error(message)
```

### Logout Flow

```python
def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.email = None
    st.session_state.role = None
    st.session_state.created_at = None
    st.rerun()
```

## Access Control

### Role-Based Access

```python
# Check if user is logged in
if not st.session_state.logged_in:
    display_login_register()
    return

# Check if user is admin
if st.session_state.role != "admin":
    st.error("⛔ Access Denied: Admin privileges required")
    return

# Admin-only features...
```

### Protected Routes

The sidebar menu dynamically adjusts based on role:

```python
menu_options = [
    "🏠 Home",
    "📤 Upload Document",
    "📊 Dashboard",
    "📜 History",
    "📈 Reports",
    "👤 Profile"
]

# Add Admin Panel only for admins
if st.session_state.role == "admin":
    menu_options.append("⚙️ Admin Panel")
```

## Database Schema

### User Table

```python
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default='user', nullable=False)  # 'admin' or 'user'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

## Security Best Practices

### Implemented ✅
- [x] Password hashing with bcrypt (never store plain text)
- [x] Salt generation per password (automatic with bcrypt)
- [x] Email validation
- [x] Password minimum length requirement
- [x] Duplicate prevention (username/email)
- [x] Role-based access control
- [x] Session-based authentication
- [x] Secure password comparison (timing-safe)

### Recommended Additions 🔄
- [ ] Password complexity requirements (uppercase, numbers, special chars)
- [ ] Rate limiting on login attempts
- [ ] Account lockout after failed attempts
- [ ] Password reset functionality
- [ ] Email verification
- [ ] Two-factor authentication (2FA)
- [ ] Session timeout
- [ ] Activity logging
- [ ] Password change on first login (for admin)

## Testing

### Manual Testing

1. Start the app: `streamlit run app.py`
2. Register a new user
3. Login with the new credentials
4. Test invalid credentials
5. Test admin login (admin/admin123)
6. Verify role-based menu access

### Automated Testing

Run the test script:

```bash
py test_auth.py
```

Tests include:
- Password hashing and verification
- Email validation
- User registration (success and failure cases)
- User login (success and failure cases)
- Duplicate detection

## Common Issues & Solutions

### Issue: Admin user not created
**Solution:** Delete `database/app.db` and restart the app to trigger reinitialization.

### Issue: Password verification fails
**Solution:** Ensure you're comparing the plain password against the hashed password, not the other way around.

### Issue: Session state not persisting
**Solution:** Check that you're calling `st.rerun()` after setting session state variables.

### Issue: Can't login after registration
**Solution:** Verify the password was hashed before saving to the database.

## Future Enhancements

1. **Password Reset**: Email-based password reset flow
2. **Email Verification**: Confirm email ownership during registration
3. **OAuth Integration**: Google/Microsoft login
4. **Activity Logs**: Track user actions for security auditing
5. **Session Management**: View and revoke active sessions
6. **Password Policy**: Configurable password requirements
7. **Account Settings**: Allow users to update their profile
8. **User Management UI**: Admin panel to manage users

## API Reference

### Quick Reference Table

| Function | Purpose | Returns |
|----------|---------|---------|
| `hash_password(password)` | Hash a password | `str` |
| `verify_password(plain, hashed)` | Verify password | `bool` |
| `validate_email(email)` | Validate email format | `bool` |
| `validate_password(password)` | Check password strength | `(bool, str)` |
| `register_user(username, email, password, role)` | Register new user | `(bool, str)` |
| `login_user(username, password)` | Authenticate user | `(bool, dict, str)` |
| `get_user_by_id(user_id)` | Get user info | `dict` or `None` |
| `seed_admin_user()` | Create default admin | `bool` |

---

**Last Updated:** January 2025
**Version:** 1.0
