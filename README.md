# AI-Powered Contract & Legal Document Risk Analyzer

A comprehensive Streamlit-based application for analyzing contracts and legal documents using AI to identify potential risks, extract key clauses, and provide actionable insights.

## 🎯 Features

- **Smart Document Processing**: Upload and analyze PDF, DOCX, and image-based legal documents
- **AI-Powered Analysis**: Leverage Google Gemini API for intelligent contract analysis
- **Risk Assessment**: Automatically identify and categorize potential legal risks
- **Semantic Search**: Find similar clauses using vector embeddings (FAISS + Sentence Transformers)
- **Visual Reports**: Generate interactive dashboards and exportable PDF reports
- **User Management**: Secure authentication with role-based access (admin/user)
- **Document History**: Track and manage all analyzed documents with full audit trail

## 🛠️ Technology Stack

- **Frontend & Backend**: Streamlit (single application architecture)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: bcrypt password hashing
- **AI/ML**: 
  - Google Gemini API for contract analysis
  - Sentence Transformers for embeddings
  - FAISS for vector similarity search
- **Document Processing**:
  - pdfplumber (PDF extraction)
  - python-docx (DOCX parsing)
  - pytesseract + Pillow (OCR for images)
- **Reporting**: ReportLab, Pandas, Plotly

## 📋 Prerequisites

- Python 3.12 or higher
- **Tesseract OCR** (required for scanned PDF processing)
  - **Windows**: Download and install from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
    - After installation, add Tesseract to your system PATH or set the path in your code
    - Default installation path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - **macOS**: `brew install tesseract`
  - **Linux**: `sudo apt-get install tesseract-ocr`
- Google Gemini API key (for AI analysis features)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd contract-risk-analyzer
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Google Gemini API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

**Get a free Gemini API key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy and paste it into your `.env` file

### 5. Initialize Database

The database will be automatically initialized when you first run the application. It creates a SQLite database at `database/app.db`.

### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 🧪 Testing Authentication

To verify the authentication system is working correctly:

```bash
# Run the test script
py test_auth.py
```

This will test:
- Password hashing and verification
- Email validation
- User registration (including duplicate detection)
- User login (with correct/incorrect credentials)
- Admin user creation

## 🔐 Authentication Features

### Current Implementation
- **Session-based authentication** (no JWT tokens)
- **bcrypt password hashing** for secure storage
- **Email validation** using regex patterns
- **Password requirements**: Minimum 6 characters
- **Duplicate prevention**: Checks for existing usernames/emails
- **Role-based access control**: Admin and User roles
- **Default admin account**: Created on first run
  - Username: `admin`
  - Password: `admin123`
  - ⚠️ **Change this password in production!**

### Session State Management
The app uses Streamlit's `st.session_state` to track:
- `logged_in`: Boolean authentication status
- `user_id`: Database user ID
- `username`: Current username
- `email`: User email address
- `role`: User role (admin/user)
- `created_at`: Account creation timestamp

### Access Control
- **Public access**: Login and registration pages only
- **User access**: All features except Admin Panel
- **Admin access**: Full system access including user management

## 📁 Project Structure

```
contract-risk-analyzer/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # Project documentation
│
├── database/                  # Database layer
│   ├── __init__.py
│   ├── db.py                 # SQLAlchemy engine & session
│   ├── models.py             # ORM models (User, Document, Analysis, RiskReport)
│   └── app.db                # SQLite database (auto-created)
│
├── services/                  # Business logic layer
│   └── __init__.py
│
├── auth/                      # Authentication logic
│   └── __init__.py
│
├── utils/                     # Utility functions
│   └── __init__.py
│
├── reports/                   # Report generation
│   └── __init__.py
│
├── uploads/                   # Uploaded documents storage
│
├── vector_db/                 # FAISS vector database storage
│
└── sample_docs/              # Sample documents for testing
```

## 💾 Database Schema

### Users Table
- User authentication and role management
- Fields: id, username, email, hashed_password, role, created_at

### Documents Table
- Uploaded document metadata
- Fields: id, user_id, filename, file_type, upload_date, extracted_text

### Analyses Table
- Extracted contract details and structured data
- Fields: id, document_id, contract_type, parties, effective_date, expiry_date, payment_terms, renewal_clause, termination_clause, confidentiality, responsibilities, jurisdiction, raw_json, created_at

### Risk Reports Table
- Identified risks with confidence scores
- Fields: id, document_id, risk_title, risk_level, confidence_score, explanation, recommendation, created_at

### Summaries Table
- AI-generated executive summaries
- Fields: id, document_id, executive_summary, key_obligations, important_dates, important_clauses, payment_summary, termination_summary, risk_summary, recommended_actions, created_at

## 🔐 Security Features

- Password hashing with bcrypt
- Role-based access control (Admin/User)
- Secure session management
- Input validation and sanitization

## 📝 Usage

1. **Register/Login**: 
   - Create a new account with username, email, and password
   - Login with your credentials
   - Default admin account: username `admin`, password `admin123`

2. **User Roles**:
   - **User**: Access to all features except admin panel
   - **Admin**: Full access including user management and system settings

3. **Profile Management**:
   - View account information and creation date
   - Check activity statistics (documents, analyses)
   - Access account settings (coming soon)

4. **Upload & Analyze Documents**:
   - Upload PDF, DOCX, TXT, or image files
   - System automatically extracts text (with OCR for scanned documents)
   - AI analyzes contract structure and extracts key fields
   - Detect risks across 7 categories (missing clauses, high-risk conditions, ambiguous wording, etc.)
   - Generate business-friendly executive summary with actionable insights

5. **Risk Assessment**: 
   - Review identified risks color-coded by severity (High/Medium/Low)
   - View confidence scores and detailed explanations
   - Get specific recommendations for each risk

6. **Executive Summary**:
   - Plain-language overview for non-lawyers
   - Key obligations for each party
   - Important dates and deadlines
   - Critical clauses to review
   - Payment and termination summaries
   - Overall risk profile
   - Recommended actions checklist

7. **Reports**: Generate and export comprehensive reports (coming soon)
8. **History**: Access all previously analyzed documents

## 🔧 Development Status

**Current Phase**: AI Pipeline Complete ✅
- [x] Project structure created
- [x] Database models defined
- [x] Basic Streamlit shell
- [x] Authentication system (bcrypt password hashing)
- [x] User registration and login
- [x] Role-based access control (Admin/User)
- [x] Session management
- [x] User profile page
- [x] Document upload functionality (PDF, DOCX, TXT)
- [x] Text extraction services
- [x] OCR support for scanned PDFs
- [x] Document history and management
- [x] Upload statistics and analytics
- [x] Google Gemini API integration (gemini-2.5-flash)
- [x] AI-powered contract analysis
- [x] Structured data extraction (11 fields: contract_type, parties, dates, clauses, etc.)
- [x] Analysis result visualization
- [x] Risk detection engine (7 risk categories with confidence scores)
- [x] Executive summary generation (8 sections: overview, obligations, dates, clauses, payment, termination, risks, actions)
- [ ] Vector search implementation - Next step
- [ ] Report generation (PDF export)
- [ ] Advanced dashboard with analytics

**Core AI Pipeline**: Upload → Extract → Analyze → Detect Risks → Summarize ✅ COMPLETE

## 🤝 Contributing

This is a development project. Future enhancements will include:
- Advanced NLP features
- Multi-language support
- Batch document processing
- API integrations
- Custom risk templates

## 📄 License

[Add your license information here]

## 📧 Contact

[Add your contact information here]

---

**Note**: This application is designed as a single Streamlit application without a separate backend server. All business logic is implemented as Python modules that are directly imported into the Streamlit app.
