"""
Authentication utilities for user registration and login
Uses bcrypt for secure password hashing
"""
import bcrypt
import re
from datetime import datetime
from database.db import get_db, close_db
from database.models import User


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: Plain text password string
        
    Returns:
        Hashed password as string
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False


def validate_email(email: str) -> bool:
    """
    Validate email format using regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    # Add more validation rules as needed
    # if not any(char.isdigit() for char in password):
    #     return False, "Password must contain at least one number"
    
    return True, ""


def register_user(username: str, email: str, password: str, role: str = "user") -> tuple[bool, str]:
    """
    Register a new user in the database.
    
    Args:
        username: Unique username
        email: User email address
        password: Plain text password (will be hashed)
        role: User role ('user' or 'admin'), defaults to 'user'
        
    Returns:
        Tuple of (success, message)
    """
    db = get_db()
    
    try:
        # Validate email format
        if not validate_email(email):
            return False, "Invalid email format"
        
        # Validate password strength
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return False, error_msg
        
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return False, "Username already exists"
        
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            return False, "Email already registered"
        
        # Validate role
        if role not in ['user', 'admin']:
            role = 'user'
        
        # Hash password
        hashed_pwd = hash_password(password)
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_pwd,
            role=role,
            created_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return True, f"User '{username}' registered successfully!"
        
    except Exception as e:
        db.rollback()
        print(f"Error registering user: {e}")
        return False, f"Registration failed: {str(e)}"
        
    finally:
        close_db(db)


def login_user(username: str, password: str) -> tuple[bool, dict, str]:
    """
    Authenticate a user by username and password.
    
    Args:
        username: Username to authenticate
        password: Plain text password
        
    Returns:
        Tuple of (success, user_data_dict, message)
        user_data_dict contains: id, username, email, role, created_at
    """
    db = get_db()
    
    try:
        # Find user by username
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            return False, {}, "Invalid username or password"
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            return False, {}, "Invalid username or password"
        
        # Return user data (excluding password)
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at
        }
        
        return True, user_data, "Login successful!"
        
    except Exception as e:
        print(f"Error during login: {e}")
        return False, {}, f"Login failed: {str(e)}"
        
    finally:
        close_db(db)


def get_user_by_id(user_id: int) -> dict:
    """
    Retrieve user information by user ID.
    
    Args:
        user_id: User ID to look up
        
    Returns:
        Dictionary containing user data, or None if not found
    """
    db = get_db()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at
        }
        
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None
        
    finally:
        close_db(db)


def seed_admin_user() -> bool:
    """
    Seed an admin user if no users exist in the database.
    Creates: username='admin', password='admin123', role='admin'
    
    Returns:
        True if admin was created, False otherwise
    """
    db = get_db()
    
    try:
        # Check if any users exist
        user_count = db.query(User).count()
        
        if user_count == 0:
            # Create admin user
            hashed_pwd = hash_password('admin123')
            admin_user = User(
                username='admin',
                email='admin@example.com',
                hashed_password=hashed_pwd,
                role='admin',
                created_at=datetime.utcnow()
            )
            
            db.add(admin_user)
            db.commit()
            
            print("=" * 60)
            print("🔑 DEFAULT ADMIN USER CREATED")
            print("=" * 60)
            print("Username: admin")
            print("Password: admin123")
            print("⚠️  IMPORTANT: Change this password after first login!")
            print("=" * 60)
            
            return True
        
        return False
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding admin user: {e}")
        return False
        
    finally:
        close_db(db)
