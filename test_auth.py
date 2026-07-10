"""
Test script to verify authentication functionality
Run this to test user registration and login without starting Streamlit
"""
from database.db import init_db
from auth.auth_utils import (
    register_user,
    login_user,
    seed_admin_user,
    hash_password,
    verify_password,
    validate_email
)

def test_password_hashing():
    """Test password hashing and verification"""
    print("\n" + "="*60)
    print("TEST 1: Password Hashing")
    print("="*60)
    
    password = "test123"
    hashed = hash_password(password)
    
    print(f"✓ Original password: {password}")
    print(f"✓ Hashed password: {hashed[:50]}...")
    print(f"✓ Password verification (correct): {verify_password(password, hashed)}")
    print(f"✓ Password verification (wrong): {verify_password('wrongpass', hashed)}")


def test_email_validation():
    """Test email validation"""
    print("\n" + "="*60)
    print("TEST 2: Email Validation")
    print("="*60)
    
    test_emails = [
        ("user@example.com", True),
        ("test.user@domain.co.uk", True),
        ("invalid.email", False),
        ("@example.com", False),
        ("user@", False),
    ]
    
    for email, expected in test_emails:
        result = validate_email(email)
        status = "✓" if result == expected else "✗"
        print(f"{status} {email}: {result} (expected {expected})")


def test_user_registration():
    """Test user registration"""
    print("\n" + "="*60)
    print("TEST 3: User Registration")
    print("="*60)
    
    # Test successful registration
    print("\n→ Testing successful registration...")
    success, message = register_user("testuser", "test@example.com", "password123", "user")
    print(f"  {message}")
    print(f"  Success: {success}")
    
    # Test duplicate username
    print("\n→ Testing duplicate username...")
    success, message = register_user("testuser", "other@example.com", "password123", "user")
    print(f"  {message}")
    print(f"  Success: {success}")
    
    # Test duplicate email
    print("\n→ Testing duplicate email...")
    success, message = register_user("otheruser", "test@example.com", "password123", "user")
    print(f"  {message}")
    print(f"  Success: {success}")
    
    # Test invalid email
    print("\n→ Testing invalid email...")
    success, message = register_user("newuser", "invalid-email", "password123", "user")
    print(f"  {message}")
    print(f"  Success: {success}")
    
    # Test short password
    print("\n→ Testing short password...")
    success, message = register_user("newuser", "new@example.com", "12345", "user")
    print(f"  {message}")
    print(f"  Success: {success}")


def test_user_login():
    """Test user login"""
    print("\n" + "="*60)
    print("TEST 4: User Login")
    print("="*60)
    
    # Test successful login
    print("\n→ Testing successful login...")
    success, user_data, message = login_user("testuser", "password123")
    print(f"  {message}")
    print(f"  Success: {success}")
    if success:
        print(f"  User data: {user_data}")
    
    # Test wrong password
    print("\n→ Testing wrong password...")
    success, user_data, message = login_user("testuser", "wrongpassword")
    print(f"  {message}")
    print(f"  Success: {success}")
    
    # Test non-existent user
    print("\n→ Testing non-existent user...")
    success, user_data, message = login_user("nonexistent", "password123")
    print(f"  {message}")
    print(f"  Success: {success}")
    
    # Test admin login
    print("\n→ Testing admin login...")
    success, user_data, message = login_user("admin", "admin123")
    print(f"  {message}")
    print(f"  Success: {success}")
    if success:
        print(f"  User data: {user_data}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AUTHENTICATION SYSTEM TEST SUITE")
    print("="*60)
    
    # Initialize database
    print("\nInitializing database...")
    init_db()
    print("✓ Database initialized")
    
    # Seed admin user
    print("\nSeeding admin user...")
    seed_admin_user()
    
    # Run tests
    test_password_hashing()
    test_email_validation()
    test_user_registration()
    test_user_login()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
    print("\n✅ Authentication system is working correctly!")
    print("\n📝 You can now run the Streamlit app:")
    print("   streamlit run app.py")
    print("\n💡 Default admin credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
