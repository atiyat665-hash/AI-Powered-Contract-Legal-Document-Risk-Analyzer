# 🚀 Quick Start Guide

## Contract Risk Analyzer - Authentication System

### ⚡ Get Started in 3 Minutes

#### 1️⃣ Install Dependencies

```bash
# Create virtual environment
py -m venv venv

# Activate it
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

#### 2️⃣ Run the Application

```bash
streamlit run app.py
```

The app will automatically:
- ✅ Initialize the SQLite database
- ✅ Create the admin user
- ✅ Open in your browser at http://localhost:8501

#### 3️⃣ Login

Use the default admin credentials:

```
Username: admin
Password: admin123
```

Or register a new user account!

---

## 📋 What's Implemented

### ✅ Authentication Features
- **User Registration**: Create new accounts with email validation
- **User Login**: Secure authentication with bcrypt password hashing
- **Session Management**: Persistent login state using Streamlit session
- **Role-Based Access**: Admin and User roles with different permissions
- **User Profile**: View account information and statistics
- **Admin Panel**: Exclusive access for administrators

### 🔒 Security Features
- bcrypt password hashing (no plain text storage)
- Email format validation
- Password minimum length (6 characters)
- Duplicate username/email prevention
- Secure password verification
- Session-based authentication (no JWT needed)

---

## 🎮 User Interface

### Login/Register Page
When not logged in, you'll see:
- **Login Tab**: Enter username and password
- **Register Tab**: Create new account with username, email, and password

### Main Application (After Login)
**Sidebar shows:**
- Your username and role
- Logout button
- Navigation menu:
  - 🏠 Home
  - 📤 Upload Document *(coming soon)*
  - 📊 Dashboard *(coming soon)*
  - 📜 History *(coming soon)*
  - 📈 Reports *(coming soon)*
  - 👤 Profile
  - ⚙️ Admin Panel *(admin only)*

---

## 🧪 Testing

### Run Authentication Tests

```bash
py test_auth.py
```

This tests:
- ✓ Password hashing and verification
- ✓ Email validation
- ✓ User registration (with duplicate detection)
- ✓ User login (correct/incorrect credentials)
- ✓ Admin user creation

### Manual Testing Checklist

- [ ] Register a new user
- [ ] Login with the new user
- [ ] Try logging in with wrong password (should fail)
- [ ] Try registering with duplicate username (should fail)
- [ ] Try registering with duplicate email (should fail)
- [ ] Login as admin (admin/admin123)
- [ ] Verify Admin Panel is visible for admin
- [ ] Logout and verify you're back at login screen
- [ ] Check Profile page shows correct information

---

## 📁 Project Structure

```
contract-risk-analyzer/
├── app.py                          # Main Streamlit app ⭐
├── test_auth.py                    # Authentication tests
├── requirements.txt                # Dependencies
├── README.md                       # Full documentation
├── AUTHENTICATION_GUIDE.md         # Auth system details
├── QUICK_START.md                  # This file
│
├── auth/                           # Authentication ⭐
│   ├── __init__.py
│   └── auth_utils.py              # Core auth functions
│
├── database/                       # Database ⭐
│   ├── __init__.py
│   ├── db.py                      # SQLAlchemy setup
│   ├── models.py                  # ORM models
│   └── app.db                     # SQLite database (auto-created)
│
├── services/                       # Business logic (empty for now)
├── utils/                         # Utilities (empty for now)
├── reports/                       # Report generation (empty for now)
├── uploads/                       # Document storage
├── vector_db/                     # FAISS vectors
└── sample_docs/                   # Sample files
```

---

## 🎯 Current Features by Page

### 🏠 Home
- Welcome page with feature overview
- Quick introduction to the system

### 🔐 Login/Register
- Full authentication system
- Email validation
- Password security
- Duplicate prevention

### 👤 Profile
- Username, email, role display
- Account creation date
- Activity statistics (placeholder)
- Account actions (placeholder)

### ⚙️ Admin Panel *(Admin Only)*
- User management (placeholder)
- System statistics (placeholder)
- Application settings (placeholder)

### 📤 Upload, 📊 Dashboard, 📜 History, 📈 Reports
- Placeholder pages (next implementation phase)

---

## 🔑 User Roles

### 👤 User (Default)
- Can access all features
- Cannot access Admin Panel
- Can upload and analyze documents
- Can view own profile and history

### 🛡️ Admin
- Full system access
- Can access Admin Panel
- Can manage users (coming soon)
- Can view system statistics
- All user permissions

---

## 🚧 Next Steps (Coming Soon)

1. **Document Upload** 📤
   - PDF, DOCX, image file support
   - Text extraction (pdfplumber, python-docx, OCR)
   - File storage and management

2. **AI Analysis** 🤖
   - Google Gemini integration
   - Contract clause extraction
   - Key information identification

3. **Risk Detection** ⚠️
   - AI-powered risk identification
   - Confidence scoring
   - Risk categorization

4. **Vector Search** 🔍
   - FAISS vector database
   - Semantic similarity search
   - Similar clause finding

5. **Report Generation** 📊
   - PDF report export
   - Interactive dashboards
   - Visual analytics

---

## 💡 Tips & Tricks

### Reset Database
If you need to start fresh:

```bash
# Delete the database file
del database\app.db

# Restart the app (will recreate database and admin user)
streamlit run app.py
```

### View Session State
Add this to any page in app.py for debugging:

```python
with st.expander("🔍 Debug: Session State"):
    st.write(st.session_state)
```

### Change Admin Password
After first login, you should change the admin password:
1. Login as admin
2. Go to Profile (feature coming soon)
3. Use "Change Password" option

*(Currently disabled - will be implemented in next phase)*

---

## 📚 Documentation

- **README.md**: Complete project documentation
- **AUTHENTICATION_GUIDE.md**: Detailed auth system guide
- **QUICK_START.md**: This file - quick reference

---

## ❓ Common Issues

### Issue: App won't start
**Solution:** Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Can't login as admin
**Solution:** Check console output for admin credentials. They should be printed on first run.

### Issue: Database locked error
**Solution:** Close other instances of the app. SQLite allows only one writer at a time.

### Issue: Module not found error
**Solution:** Make sure you're in the project root directory and virtual environment is activated.

---

## 🎉 You're All Set!

The authentication system is fully functional. You can now:
- ✅ Register new users
- ✅ Login securely
- ✅ Manage sessions
- ✅ View user profiles
- ✅ Access admin panel (if admin)

**Next up:** Document upload and AI analysis features!

---

**Need Help?** Check the full documentation in README.md or AUTHENTICATION_GUIDE.md
