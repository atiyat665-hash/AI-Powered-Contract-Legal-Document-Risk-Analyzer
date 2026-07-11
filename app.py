"""
AI-Powered Contract & Legal Document Risk Analyzer
Main Streamlit Application

This is a single Streamlit application that combines frontend and backend logic.
Uses st.navigation for true multipage routing (each sidebar item = its own URL/page).
"""
import streamlit as st
from datetime import datetime
from database.db import init_db
from auth.auth_utils import (
    register_user,
    login_user,
    seed_admin_user,
    validate_email
)

# Page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="Contract Risk Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# GLOBAL STYLING - Professional Dark Theme
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg-main: #262e42;
        --bg-card: #333c56;
        --bg-card-hover: #3c4661;
        --border-color: #4d5875;
        --border-color-soft: #434e6c;
        --text-primary: #f5f7fb;
        --text-secondary: #b6bed2;
        --accent: #14b8a6;
        --accent-hover: #2dd4bf;
        --accent-soft: rgba(20, 184, 166, 0.16);
        --danger: #f85149;
        --success: #3fb950;
        --warning: #d29922;
    }

    /* Font setup */
    html, body, .stApp, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    h1, h2, h3, h4, h5, h6,
    .stButton button,
    section[data-testid="stSidebar"] .stButton button {
        font-family: 'Poppins', 'Inter', sans-serif !important;
    }

    /* App background */
    .stApp {
        background-color: var(--bg-main);
        color: var(--text-primary);
    }

    /* Main block container spacing */
    .main .block-container {
        padding-top: 2rem;
    }

    /* Card-style containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--bg-card);
        border-radius: 14px;
        border: 1px solid var(--border-color);
        padding: 1.3rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
        margin-bottom: 1rem;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #333c56 0%, #3c4661 100%);
        border-radius: 12px;
        padding: 16px;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 6px rgba(0,0,0,0.18);
    }
    div[data-testid="stMetricValue"] {
        color: var(--text-primary);
    }
    div[data-testid="stMetricLabel"] {
        color: var(--text-secondary);
    }

    /* Buttons */
    .stButton button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
        background-color: #3c4661;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }
    .stButton button:hover {
        box-shadow: 0 4px 14px rgba(20, 184, 166, 0.25);
        transform: translateY(-1px);
        border-color: var(--accent);
        color: var(--accent-hover);
    }
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent) 0%, #0d9488 100%);
        border: none;
        color: #ffffff;
    }
    .stButton button[kind="primary"]:hover {
        box-shadow: 0 6px 18px rgba(20, 184, 166, 0.45);
        color: #ffffff;
    }

    /* Headings */
    h1, h2, h3 {
        color: var(--text-primary);
        font-weight: 800;
    }
    h3 {
        padding-left: 0;
        letter-spacing: 0.01em;
    }
    p, span, label, .stMarkdown, .stCaption {
        color: var(--text-primary);
    }

    /* Streamlit's built-in JSON viewer (st.json) always renders on a
       white background regardless of our dark theme. The global "span"
       rule above was leaking light/white text color into it, making the
       JSON content (raw analysis result) invisible. Force it back to a
       readable dark-on-white look. */
    [data-testid="stJson"] {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 6px 4px;
    }
    [data-testid="stJson"] * {
        color: initial !important;
    }

    /* Key terms (bold text) inside markdown lists - distinct font & color */
    .stMarkdown strong, .stMarkdown b {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: var(--accent-hover);
    }

    /* Alerts */
    .stAlert {
        border-radius: 12px;
        border: 1px solid var(--border-color);
    }
    div[data-testid="stAlertContentInfo"] {
        color: var(--text-primary);
    }

    /* Sidebar - dark navy/black */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #202840 0%, #283050 100%);
        border-right: 1px solid var(--border-color-soft);
    }
    section[data-testid="stSidebar"] * {
        color: #e6edf3 !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background-color: var(--danger);
        color: white !important;
        border: none;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: #ff6b64;
        box-shadow: 0 4px 12px rgba(248, 81, 73, 0.35);
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        border-radius: 12px;
        border: 1px solid var(--border-color);
        background-color: var(--bg-card);
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-weight: 600;
        color: var(--text-secondary);
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--accent-hover);
    }
    div[data-baseweb="tab-highlight"] {
        background-color: var(--accent) !important;
    }

    /* Text inputs */
    .stTextInput input, .stTextArea textarea {
        background-color: #262e42;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 1px var(--accent);
    }

    /* Disabled/read-only text areas (e.g. "Extracted Text Preview") lose
       contrast because browsers force their own low-contrast style on
       disabled fields, overriding the rule above. Force it back. */
    .stTextArea textarea:disabled,
    .stTextArea textarea[disabled],
    .stTextInput input:disabled,
    .stTextInput input[disabled] {
        background-color: #262e42 !important;
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
        opacity: 1 !important;
    }

    /* File uploader */
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #262e42;
        border: 1.5px dashed var(--border-color);
        border-radius: 12px;
    }

    /* Hide Streamlit default footer/menu for polish */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# Initialize database on startup
@st.cache_resource
def initialize_database():
    """Initialize the database tables and seed admin user if needed"""
    init_db()
    seed_admin_user()
    return True


initialize_database()

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'email' not in st.session_state:
    st.session_state.email = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'created_at' not in st.session_state:
    st.session_state.created_at = None


def logout():
    """Logout function to clear session state"""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.email = None
    st.session_state.role = None
    st.session_state.created_at = None
    st.rerun()


def display_login_register():
    """Redesigned Login/Register page - split hero layout with dark professional theme"""

    # Extra CSS specific to the login/register hero screen
    st.markdown("""
    <style>
        .auth-hero {
            background: linear-gradient(160deg, #2d3555 0%, #283050 60%, #202840 100%);
            border-radius: 20px;
            border: 1px solid #434e6c;
            padding: 3rem 2.5rem;
            height: 100%;
            box-shadow: 0 8px 30px rgba(0,0,0,0.25);
        }
        .auth-hero h1 {
            font-family: 'Poppins', sans-serif;
            font-size: 2.1rem;
            margin-bottom: 0.4rem;
            background: linear-gradient(90deg, #2dd4bf, #5eead4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .auth-hero p.tagline {
            color: #a3acc2;
            font-size: 1.02rem;
            margin-bottom: 1.8rem;
        }
        .auth-feature {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 1.1rem;
        }
        .auth-feature-icon {
            font-size: 1.3rem;
            background: rgba(20, 184, 166, 0.14);
            border: 1px solid rgba(20, 184, 166, 0.35);
            border-radius: 10px;
            padding: 8px 10px;
        }
        .auth-feature-text b {
            color: #eef1f6;
            display: block;
            font-size: 0.95rem;
        }
        .auth-feature-text span {
            color: #a3acc2;
            font-size: 0.85rem;
        }
        .auth-badge {
            display: inline-block;
            background: rgba(20, 184, 166, 0.14);
            border: 1px solid rgba(20, 184, 166, 0.4);
            color: #5eead4;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    col_hero, col_form = st.columns([1.1, 1], gap="large")

    with col_hero:
        st.markdown("""
        <div class="auth-hero">
            <div class="auth-badge">📄 AI CONTRACT INTELLIGENCE</div>
            <h1>Contract Risk Analyzer</h1>
            <p class="tagline">Review contracts in minutes, not hours — powered by AI.</p>
            <div class="auth-feature">
                <div class="auth-feature-icon">🤖</div>
                <div class="auth-feature-text">
                    <b>AI-Powered Analysis</b>
                    <span>Automatic clause extraction with Google Gemini</span>
                </div>
            </div>
            <div class="auth-feature">
                <div class="auth-feature-icon">⚠️</div>
                <div class="auth-feature-text">
                    <b>Risk Detection</b>
                    <span>Spot high-risk clauses and missing terms instantly</span>
                </div>
            </div>
            <div class="auth-feature">
                <div class="auth-feature-icon">📝</div>
                <div class="auth-feature-text">
                    <b>Executive Summaries</b>
                    <span>Plain-language overviews for faster decisions</span>
                </div>
            </div>
            <div class="auth-feature">
                <div class="auth-feature-icon">🔒</div>
                <div class="auth-feature-text">
                    <b>Secure & Role-Based</b>
                    <span>Encrypted sessions with admin/user access control</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_form:
        with st.container(border=True):
            tab_login, tab_register = st.tabs(["🔐 Login", "✨ Register"])

            with tab_login:
                st.markdown("#### Welcome back")
                st.caption("Sign in to continue to your dashboard")

                with st.form("login_form"):
                    login_username = st.text_input("Username", key="login_username", placeholder="e.g. john_doe")
                    login_password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")

                    submit_login = st.form_submit_button("Sign In", use_container_width=True, type="primary")

                    if submit_login:
                        if not login_username or not login_password:
                            st.error("Please enter both username and password")
                        else:
                            success, user_data, message = login_user(login_username, login_password)

                            if success:
                                st.session_state.logged_in = True
                                st.session_state.user_id = user_data['id']
                                st.session_state.username = user_data['username']
                                st.session_state.email = user_data['email']
                                st.session_state.role = user_data['role']
                                st.session_state.created_at = user_data['created_at']

                                st.success(message)
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(message)

                st.info("💡 **Demo Admin Access**\n\nUsername: `admin`  •  Password: `admin123`")

            with tab_register:
                st.markdown("#### Create your account")
                st.caption("Get started analyzing contracts in seconds")

                with st.form("register_form"):
                    reg_username = st.text_input("Username", key="reg_username",
                                                 placeholder="Choose a username")
                    reg_email = st.text_input("Email", key="reg_email",
                                              placeholder="you@example.com")
                    reg_password = st.text_input("Password", type="password", key="reg_password",
                                                placeholder="Minimum 6 characters")
                    reg_confirm_password = st.text_input("Confirm Password", type="password",
                                                         key="reg_confirm_password",
                                                         placeholder="Re-enter password")

                    submit_register = st.form_submit_button("Create Account", use_container_width=True, type="primary")

                    if submit_register:
                        if not reg_username or not reg_email or not reg_password or not reg_confirm_password:
                            st.error("All fields are required")
                        elif not validate_email(reg_email):
                            st.error("Invalid email format")
                        elif len(reg_password) < 6:
                            st.error("Password must be at least 6 characters long")
                        elif reg_password != reg_confirm_password:
                            st.error("Passwords do not match")
                        else:
                            success, message = register_user(reg_username, reg_email, reg_password, role="user")

                            if success:
                                st.success(message)
                                st.info("✅ You can now sign in with your credentials")
                                st.balloons()
                            else:
                                st.error(message)

                st.caption("By registering, you agree to our terms of service and privacy policy.")


def display_analysis_results(analysis):
    """Display contract analysis results in a structured format."""
    from services.analysis_service import format_analysis_for_display

    st.markdown("### 📋 Analysis Results")

    data = format_analysis_for_display(analysis)

    st.markdown("#### Contract Overview")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("📄 Contract Type", data['contract_type'])

    with col2:
        st.metric("⚖️ Jurisdiction", data['jurisdiction'])

    st.markdown("#### 👥 Parties Involved")
    if data['parties']:
        for i, party in enumerate(data['parties'], 1):
            st.markdown(f"{i}. **{party}**")
    else:
        st.caption("No parties specified")

    st.markdown("---")

    st.markdown("#### 📅 Key Dates")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Effective Date", data['effective_date'])

    with col2:
        st.metric("Expiry Date", data['expiry_date'])

    with col3:
        notice_period = analysis.raw_json
        import json
        try:
            raw_data = json.loads(notice_period)
            notice = raw_data.get('notice_period', 'Not specified')
        except:
            notice = 'Not specified'
        st.metric("Notice Period", notice)

    st.markdown("---")

    st.markdown("#### 📝 Terms and Clauses")

    with st.expander("💰 Payment Terms", expanded=True):
        st.write(data['payment_terms'])

    with st.expander("🔄 Renewal Clause"):
        st.write(data['renewal_clause'])

    with st.expander("❌ Termination Clause"):
        st.write(data['termination_clause'])

    with st.expander("🔒 Confidentiality"):
        st.write(data['confidentiality'])

    with st.expander("📋 Responsibilities"):
        st.write(data['responsibilities'])

    st.markdown("---")

    st.caption(f"✅ Analyzed on {data['analyzed_at']}")

    with st.expander("🔍 View Raw JSON"):
        st.json(analysis.raw_json)


# ============================================================================
# PAGE FUNCTIONS (each becomes its own URL via st.navigation)
# ============================================================================

def page_home():
    """Home page content"""
    st.title("📄 AI-Powered Contract & Legal Document Risk Analyzer")
    st.markdown("### Intelligent Contract Analysis & Risk Assessment")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("### 🎯 Features")
            st.markdown("""
            - **Smart Upload**: PDF, DOCX, and image support
            - **AI Analysis**: Powered by Google Gemini
            - **Risk Detection**: Identify potential legal risks
            - **Semantic Search**: Find similar clauses
            - **Export Reports**: Generate professional PDFs
            """)

    with col2:
        with st.container(border=True):
            st.markdown("### 📊 Analytics")
            st.markdown("""
            - **Visual Dashboards**: Interactive charts
            - **Risk Scoring**: Confidence-based metrics
            - **Trend Analysis**: Track document patterns
            - **Compliance Checks**: Regulatory alignment
            - **History Tracking**: Full audit trail
            """)

    with col3:
        with st.container(border=True):
            st.markdown("### 🔒 Security")
            st.markdown("""
            - **User Authentication**: Secure login system
            - **Role-based Access**: Admin and user roles
            - **Data Encryption**: Protected storage
            - **Audit Logs**: Complete traceability
            - **Privacy First**: Your data stays secure
            """)

    st.markdown("---")
    st.info("👈 Use the sidebar to navigate through the application")


def page_upload():
    """Document upload page with file processing and AI analysis"""
    st.title("📤 Upload Document")
    st.markdown("Upload PDF, DOCX, or TXT files for analysis")
    st.markdown("---")

    from services.upload_service import validate_file, save_uploaded_file, create_document_record
    from services.extraction_service import extract_text, get_text_stats
    from services.gemini_service import is_gemini_configured, analyze_contract
    from services.analysis_service import save_analysis, get_analysis_by_document, format_analysis_for_display

    if not is_gemini_configured():
        st.warning("⚠️ **Gemini API not configured**")
        st.info("""
        AI analysis features require a Google Gemini API key. To enable:

        1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Create a `.env` file in the project root (or edit existing)
        3. Add: `GEMINI_API_KEY=your_key_here`
        4. Restart the application

        You can still upload and extract text from documents without AI analysis.
        """)
        st.markdown("---")

    with st.container(border=True):
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=['pdf', 'docx', 'txt'],
            help="Maximum file size: 10MB"
        )

        if uploaded_file is not None:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Filename", uploaded_file.name)
            with col2:
                file_size_mb = uploaded_file.size / (1024 * 1024)
                st.metric("File Size", f"{file_size_mb:.2f} MB")
            with col3:
                file_type = uploaded_file.name.split('.')[-1].upper()
                st.metric("File Type", file_type)

            st.markdown("---")

            if st.button("📄 Process Document", type="primary", use_container_width=True):

                is_valid, error_message = validate_file(uploaded_file)

                if not is_valid:
                    st.error(f"❌ {error_message}")
                    return

                try:
                    with st.spinner("Processing document..."):

                        status_placeholder = st.empty()
                        status_placeholder.info("💾 Saving file...")

                        file_path, original_filename = save_uploaded_file(
                            uploaded_file,
                            st.session_state.user_id
                        )

                        status_placeholder.info("📝 Extracting text...")

                        file_extension = original_filename.split('.')[-1].lower()
                        extracted_text, used_ocr = extract_text(file_path, file_extension)

                        if not extracted_text or len(extracted_text.strip()) < 10:
                            status_placeholder.error("⚠️ Failed to extract text from document. The file may be corrupted or empty.")
                            return

                        status_placeholder.info("💾 Saving to database...")

                        document = create_document_record(
                            user_id=st.session_state.user_id,
                            filename=original_filename,
                            file_type=file_extension,
                            extracted_text=extracted_text
                        )

                        status_placeholder.empty()

                    st.session_state.current_document_id = document.id
                    st.session_state.current_document_text = extracted_text

                    st.success(f"✅ Document processed successfully! Document ID: {document.id}")

                    if used_ocr:
                        st.info("ℹ️ OCR was used to extract text from this document (scanned PDF detected)")

                    st.markdown("### 📊 Extraction Statistics")
                    stats = get_text_stats(extracted_text)

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Characters", f"{stats['characters']:,}")
                    with col2:
                        st.metric("Words", f"{stats['words']:,}")
                    with col3:
                        st.metric("Lines", f"{stats['lines']:,}")
                    with col4:
                        st.metric("Paragraphs", f"{stats['paragraphs']:,}")

                    st.markdown("### 📄 Extracted Text Preview")

                    preview_length = 2000
                    preview_text = extracted_text[:preview_length]

                    if len(extracted_text) > preview_length:
                        preview_text += f"\n\n... (showing first {preview_length} characters of {len(extracted_text)} total)"

                    with st.expander("Click to view extracted text", expanded=True):
                        st.text_area(
                            "Extracted Content",
                            preview_text,
                            height=400,
                            disabled=True,
                            label_visibility="collapsed"
                        )

                    if len(extracted_text) > preview_length:
                        with st.expander("View Full Text"):
                            st.text_area(
                                "Full Extracted Content",
                                extracted_text,
                                height=600,
                                disabled=True,
                                label_visibility="collapsed"
                            )

                    st.markdown("---")

                except ValueError as ve:
                    st.error(f"❌ Extraction Error: {str(ve)}")
                    st.error("The file format may not be supported or the file may be corrupted.")
                    return

                except Exception as e:
                    st.error(f"❌ An error occurred while processing the document: {str(e)}")
                    st.error("Please try again or contact support if the problem persists.")
                    print(f"Upload error: {e}")
                    return

    if uploaded_file is not None:
        if 'current_document_id' in st.session_state and st.session_state.get('current_document_id'):
            existing_risks = []
            existing_summary = None
            existing_analysis = None

            with st.container(border=True):
                st.markdown("### 🤖 AI Analysis")

                existing_analysis = get_analysis_by_document(st.session_state.current_document_id)

                if existing_analysis:
                    st.info("✅ This document has already been analyzed. Showing results below.")
                    display_analysis_button = st.button("🔄 Re-analyze with AI", key="reanalyze_btn", use_container_width=True)
                else:
                    display_analysis_button = st.button("🤖 Analyze with AI", type="primary", key="analyze_btn", use_container_width=True)

                if display_analysis_button:
                    if not is_gemini_configured():
                        st.error("❌ Gemini API is not configured. Please add your API key to continue.")
                    else:
                        try:
                            with st.spinner("🤖 Analyzing document with AI... This may take a moment."):
                                analysis_result = analyze_contract(st.session_state.current_document_text)

                                if 'error' in analysis_result:
                                    st.error(f"❌ {analysis_result['message']}")

                                    if st.button("🔄 Retry Analysis"):
                                        st.rerun()

                                    if analysis_result.get('raw_response'):
                                        with st.expander("🔍 Debug Information"):
                                            st.text_area("Raw Response", analysis_result['raw_response'], height=200)

                                else:
                                    saved_analysis = save_analysis(
                                        st.session_state.current_document_id,
                                        analysis_result
                                    )

                                    st.success("✅ Analysis completed successfully!")
                                    existing_analysis = saved_analysis

                        except Exception as e:
                            st.error(f"❌ An error occurred during analysis: {str(e)}")
                            if st.button("🔄 Retry Analysis", key="retry_after_error"):
                                st.rerun()

                if existing_analysis:
                    display_analysis_results(existing_analysis)

            if existing_analysis:
                with st.container(border=True):
                    st.markdown("### ⚠️ Risk Detection")

                    from services.gemini_service import detect_risks
                    from services.analysis_service import save_risk_reports, get_risk_reports_by_document, format_risk_for_display

                    existing_risks = get_risk_reports_by_document(st.session_state.current_document_id)

                    if existing_risks and len(existing_risks) > 0:
                        st.info(f"✅ {len(existing_risks)} risk(s) detected. Showing results below.")
                        detect_risks_button = st.button("🔄 Re-detect Risks", key="redetect_risks_btn", use_container_width=True)
                    else:
                        detect_risks_button = st.button("⚠️ Detect Risks", type="primary", key="detect_risks_btn", use_container_width=True)

                    if detect_risks_button:
                        try:
                            with st.spinner("⚠️ Detecting risks... This may take a moment."):
                                import json
                                analysis_dict = json.loads(existing_analysis.raw_json) if existing_analysis.raw_json else {}

                                risks_result = detect_risks(
                                    st.session_state.current_document_text,
                                    analysis_dict
                                )

                                saved_risks = save_risk_reports(
                                    st.session_state.current_document_id,
                                    risks_result
                                )

                                st.success(f"✅ Risk detection completed! Found {len(saved_risks)} risk(s).")
                                existing_risks = saved_risks

                        except Exception as e:
                            st.error(f"❌ An error occurred during risk detection: {str(e)}")
                            if st.button("🔄 Retry Risk Detection", key="retry_risk_detection"):
                                st.rerun()

                    if existing_risks and len(existing_risks) > 0:
                        high_risks = sum(1 for r in existing_risks if r.risk_level == 'High')
                        medium_risks = sum(1 for r in existing_risks if r.risk_level == 'Medium')
                        low_risks = sum(1 for r in existing_risks if r.risk_level == 'Low')

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Risks", len(existing_risks))
                        with col2:
                            st.metric("🔴 High", high_risks)
                        with col3:
                            st.metric("🟡 Medium", medium_risks)
                        with col4:
                            st.metric("🟢 Low", low_risks)

                        st.markdown("---")

                        for risk in existing_risks:
                            risk_data = format_risk_for_display(risk)

                            if risk_data['risk_level'] == 'High':
                                risk_color = "🔴"
                            elif risk_data['risk_level'] == 'Medium':
                                risk_color = "🟡"
                            else:
                                risk_color = "🟢"

                            with st.expander(f"{risk_color} {risk_data['risk_title']} ({risk_data['risk_level']} - {risk_data['confidence_percent']}% confidence)"):
                                st.markdown(f"**Risk Level:** {risk_data['risk_level']}")
                                st.markdown(f"**Confidence:** {risk_data['confidence_percent']}%")
                                st.markdown(f"**Explanation:** {risk_data['explanation']}")
                                st.markdown(f"**Recommendation:** {risk_data['recommendation']}")

                with st.container(border=True):
                    st.markdown("### 📝 Executive Summary")

                    from services.gemini_service import generate_summary
                    from services.analysis_service import save_summary, get_summary_by_document, format_summary_for_display

                    existing_summary = get_summary_by_document(st.session_state.current_document_id)

                    if not existing_risks or len(existing_risks) == 0:
                        st.info("⚠️ Please detect risks first before generating a summary.")
                        st.button("📝 Generate Summary", disabled=True, use_container_width=True)
                    else:
                        if existing_summary:
                            st.info("✅ Executive summary has been generated. Showing results below.")
                            generate_summary_button = st.button("🔄 Re-generate Summary", key="regenerate_summary_btn", use_container_width=True)
                        else:
                            generate_summary_button = st.button("📝 Generate Summary", type="primary", key="generate_summary_btn", use_container_width=True)

                        if generate_summary_button:
                            try:
                                with st.spinner("📝 Generating executive summary... This may take a moment."):
                                    import json
                                    analysis_dict = json.loads(existing_analysis.raw_json) if existing_analysis.raw_json else {}

                                    risks_list = []
                                    for risk in existing_risks:
                                        risks_list.append({
                                            'risk_title': risk.risk_title,
                                            'risk_level': risk.risk_level,
                                            'confidence_score': risk.confidence_score,
                                            'explanation': risk.explanation,
                                            'recommendation': risk.recommendation
                                        })

                                    summary_result = generate_summary(
                                        st.session_state.current_document_text,
                                        analysis_dict,
                                        risks_list
                                    )

                                    if 'error' in summary_result and not summary_result.get('executive_summary'):
                                        st.error(f"❌ {summary_result.get('message', 'Unknown error')}")
                                        if st.button("🔄 Retry Summary Generation"):
                                            st.rerun()
                                    else:
                                        saved_summary = save_summary(
                                            st.session_state.current_document_id,
                                            summary_result
                                        )

                                        st.success("✅ Executive summary generated successfully!")
                                        existing_summary = saved_summary

                            except Exception as e:
                                st.error(f"❌ An error occurred during summary generation: {str(e)}")
                                if st.button("🔄 Retry Summary Generation", key="retry_summary_generation"):
                                    st.rerun()

                    if existing_summary:
                        summary_data = format_summary_for_display(existing_summary)

                        st.info(f"**Executive Summary**\n\n{summary_data['executive_summary']}")

                        st.markdown("---")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("#### 💰 Payment Summary")
                            st.write(summary_data['payment_summary'])

                            st.markdown("---")

                            st.markdown("#### ❌ Termination Summary")
                            st.write(summary_data['termination_summary'])

                        with col2:
                            st.markdown("#### ⚠️ Risk Summary")
                            st.write(summary_data['risk_summary'])

                        st.markdown("---")

                        st.markdown("#### 📋 Key Obligations")
                        if summary_data['key_obligations']:
                            for obligation in summary_data['key_obligations']:
                                st.markdown(f"- {obligation}")
                        else:
                            st.caption("No key obligations specified")

                        st.markdown("---")

                        st.markdown("#### 📅 Important Dates")
                        if summary_data['important_dates']:
                            for date in summary_data['important_dates']:
                                st.markdown(f"- {date}")
                        else:
                            st.caption("No important dates specified")

                        st.markdown("---")

                        st.markdown("#### 📄 Important Clauses")
                        if summary_data['important_clauses']:
                            for clause in summary_data['important_clauses']:
                                st.markdown(f"- {clause}")
                        else:
                            st.caption("No important clauses highlighted")

                        st.markdown("---")

                        st.markdown("#### ✅ Recommended Actions")
                        if summary_data['recommended_actions']:
                            for i, action in enumerate(summary_data['recommended_actions'], 1):
                                st.markdown(f"{i}. {action}")
                        else:
                            st.caption("No specific actions recommended")

                        st.markdown("---")
                        st.caption(f"📝 Summary generated on {summary_data['created_at']}")

                if existing_summary:
                    with st.container(border=True):
                        st.markdown("### 📥 Download Report")

                        from services.report_service import generate_pdf_report, generate_docx_report
                        from services.analysis_service import save_report_record
                        from services.upload_service import get_document_by_id
                        import os

                        doc_obj = get_document_by_id(st.session_state.current_document_id)

                        col_pdf, col_docx = st.columns(2)

                        with col_pdf:
                            if st.button("📄 Generate PDF Report", use_container_width=True):
                                try:
                                    filepath = generate_pdf_report(doc_obj, existing_analysis, existing_risks, existing_summary)
                                    save_report_record(doc_obj.id, "pdf", filepath)
                                    with open(filepath, "rb") as f:
                                        st.download_button("⬇️ Download PDF", f, file_name=os.path.basename(filepath), key="dl_pdf")
                                except Exception as e:
                                    st.error(f"Failed to generate PDF: {e}")

                        with col_docx:
                            if st.button("📝 Generate DOCX Report", use_container_width=True):
                                try:
                                    filepath = generate_docx_report(doc_obj, existing_analysis, existing_risks, existing_summary)
                                    save_report_record(doc_obj.id, "docx", filepath)
                                    with open(filepath, "rb") as f:
                                        st.download_button("⬇️ Download DOCX", f, file_name=os.path.basename(filepath), key="dl_docx")
                                except Exception as e:
                                    st.error(f"Failed to generate DOCX: {e}")

    if uploaded_file is None:
        st.info("👆 Upload a document to get started")

        st.markdown("### 📋 Supported File Types")
        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border=True):
                st.markdown("**📕 PDF**")
                st.markdown("- Standard PDF documents")
                st.markdown("- Scanned PDFs (with OCR)")

        with col2:
            with st.container(border=True):
                st.markdown("**📘 DOCX**")
                st.markdown("- Microsoft Word documents")
                st.markdown("- Extracts from paragraphs and tables")

        with col3:
            with st.container(border=True):
                st.markdown("**📄 TXT**")
                st.markdown("- Plain text files")
                st.markdown("- UTF-8 and Latin-1 encoding")

        st.markdown("---")
        st.markdown("### ⚙️ Processing Features")
        st.markdown("""
        - ✅ Automatic text extraction
        - ✅ OCR for scanned documents
        - ✅ AI-powered contract analysis
        - ✅ Structured data extraction
        - ✅ Text cleaning and formatting
        - ✅ File validation and security checks
        - ✅ Maximum file size: 10MB
        """)


def page_dashboard():
    """Dashboard page with statistics"""
    st.title("📊 Dashboard")
    st.markdown("Overview of your document analysis activity")
    st.markdown("---")

    from services.upload_service import get_upload_statistics
    from services.analysis_service import get_analysis_statistics

    upload_stats = get_upload_statistics(st.session_state.user_id)
    analysis_stats = get_analysis_statistics(st.session_state.user_id)

    st.markdown("### 📈 Your Statistics")

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Documents", upload_stats['total_documents'],
                      help="Total number of documents uploaded")

        with col2:
            st.metric("AI Analyses", analysis_stats['total_analyses'],
                      help="Number of documents analyzed with AI")

        with col3:
            analysis_percentage = 0
            if upload_stats['total_documents'] > 0:
                analysis_percentage = int((analysis_stats['total_analyses'] / upload_stats['total_documents']) * 100)
            st.metric("Analyzed", f"{analysis_percentage}%",
                      help="Percentage of documents analyzed")

        with col4:
            st.metric("Risk Reports", "0", help="Coming soon")

    st.markdown("---")

    if analysis_stats['top_contract_types']:
        with st.container(border=True):
            st.markdown("### 📋 Top Contract Types")

            for contract_type, count in analysis_stats['top_contract_types'].items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{contract_type}**")
                with col2:
                    st.markdown(f"**{count}** document{'s' if count > 1 else ''}")

        st.markdown("---")

    st.markdown("### ⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📤 Upload New Document", use_container_width=True, type="primary"):
            st.info("👈 Use the sidebar to navigate to Upload")

    with col2:
        if st.button("📜 View History", use_container_width=True):
            st.info("👈 Use the sidebar to navigate to History")

    with col3:
        if st.button("📈 Generate Report", use_container_width=True, disabled=True):
            st.info("Report generation coming soon!")

    st.markdown("---")

    if upload_stats['total_documents'] > 0:
        with st.container(border=True):
            st.markdown("### 📊 Document Type Distribution")

            import pandas as pd

            chart_data = pd.DataFrame({
                'Type': ['PDF', 'DOCX', 'TXT'],
                'Count': [upload_stats['pdf_count'], upload_stats['docx_count'], upload_stats['txt_count']]
            })

            st.bar_chart(chart_data.set_index('Type'))

    else:
        st.info("📭 No documents yet. Upload your first document to see statistics!")


def page_history():
    """History page showing uploaded documents"""
    st.title("📜 Document History")
    st.markdown("View and manage your uploaded documents")
    st.markdown("---")

    from services.upload_service import get_user_documents, delete_document
    from services.analysis_service import get_analysis_by_document

    documents = get_user_documents(st.session_state.user_id)

    if not documents:
        st.info("📭 No documents uploaded yet. Upload your first document to get started!")
        return

    with st.container(border=True):
        st.markdown(f"### 📊 Total Documents: {len(documents)}")

        pdf_count = sum(1 for doc in documents if doc.file_type == 'pdf')
        docx_count = sum(1 for doc in documents if doc.file_type == 'docx')
        txt_count = sum(1 for doc in documents if doc.file_type == 'txt')
        analyzed_count = sum(1 for doc in documents if get_analysis_by_document(doc.id))

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📕 PDF", pdf_count)
        with col2:
            st.metric("📘 DOCX", docx_count)
        with col3:
            st.metric("📄 TXT", txt_count)
        with col4:
            st.metric("🤖 Analyzed", analyzed_count)

    st.markdown("---")

    for idx, doc in enumerate(documents):
        has_analysis = get_analysis_by_document(doc.id) is not None

        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns([3, 1, 2, 1, 1])

            with col1:
                st.markdown(f"**📄 {doc.filename}**")
                st.caption(f"ID: {doc.id}")

            with col2:
                type_emoji = {'pdf': '📕', 'docx': '📘', 'txt': '📄'}.get(doc.file_type, '📄')
                st.markdown(f"{type_emoji} **{doc.file_type.upper()}**")

            with col3:
                upload_date = doc.upload_date.strftime("%Y-%m-%d %H:%M")
                st.markdown(f"📅 {upload_date}")

            with col4:
                if has_analysis:
                    st.success("✅ Analyzed")
                else:
                    st.warning("⏳ Pending")

            with col5:
                if st.button("👁️ View", key=f"view_{doc.id}", use_container_width=True):
                    st.session_state.selected_document = doc.id
                    st.session_state.show_document_details = True

            if st.session_state.get('show_document_details') and st.session_state.get('selected_document') == doc.id:
                with st.expander("📋 Document Details", expanded=True):

                    info_col1, info_col2 = st.columns(2)
                    with info_col1:
                        st.markdown(f"**Document ID:** {doc.id}")
                        st.markdown(f"**Filename:** {doc.filename}")
                        st.markdown(f"**File Type:** {doc.file_type.upper()}")
                    with info_col2:
                        st.markdown(f"**Upload Date:** {doc.upload_date.strftime('%B %d, %Y at %I:%M %p')}")
                        text_length = len(doc.extracted_text) if doc.extracted_text else 0
                        st.markdown(f"**Text Length:** {text_length:,} characters")
                        word_count = len(doc.extracted_text.split()) if doc.extracted_text else 0
                        st.markdown(f"**Word Count:** {word_count:,} words")

                    st.markdown("---")

                    analysis = get_analysis_by_document(doc.id)
                    if analysis:
                        st.markdown("### 🤖 AI Analysis")
                        display_analysis_results(analysis)
                        st.markdown("---")

                    if doc.extracted_text:
                        st.markdown("**Extracted Text:**")
                        preview = doc.extracted_text[:1000]
                        if len(doc.extracted_text) > 1000:
                            preview += "\n\n... (truncated)"
                        st.text_area("", preview, height=200, disabled=True, label_visibility="collapsed")
                    else:
                        st.warning("No extracted text available")

                    btn_col1, btn_col2, btn_col3 = st.columns(3)

                    with btn_col1:
                        if analysis:
                            if st.button("🔄 Re-analyze", key=f"reanalyze_{doc.id}", use_container_width=True):
                                st.session_state.current_document_id = doc.id
                                st.session_state.current_document_text = doc.extracted_text
                                st.info("Go to Upload page to re-analyze")
                        else:
                            if st.button("🤖 Analyze Now", key=f"analyze_{doc.id}", use_container_width=True, type="primary"):
                                st.session_state.current_document_id = doc.id
                                st.session_state.current_document_text = doc.extracted_text
                                st.info("Go to Upload page to analyze")

                    with btn_col2:
                        if st.button("❌ Close Details", key=f"close_{doc.id}", use_container_width=True):
                            st.session_state.show_document_details = False
                            st.rerun()

                    with btn_col3:
                        if st.button("🗑️ Delete", key=f"delete_{doc.id}", use_container_width=True, type="secondary"):
                            if st.session_state.get(f"confirm_delete_{doc.id}"):
                                success, message = delete_document(doc.id, st.session_state.user_id)
                                if success:
                                    st.success(message)
                                    st.session_state.show_document_details = False
                                    st.rerun()
                                else:
                                    st.error(message)
                            else:
                                st.session_state[f"confirm_delete_{doc.id}"] = True
                                st.warning("⚠️ Click Delete again to confirm")

    if len(documents) >= 50:
        st.caption("📌 Showing most recent 50 documents")


def page_reports():
    """Reports page showing all generated reports for the user's documents"""
    st.title("📈 Reports")
    st.markdown("View and download previously generated reports")
    st.markdown("---")

    from services.upload_service import get_user_documents
    from services.analysis_service import get_reports_by_document

    documents = get_user_documents(st.session_state.user_id)

    if not documents:
        st.info("📭 No documents uploaded yet. Upload and analyze a document first, then generate a report.")
        return

    any_reports = False
    for doc in documents:
        reports = get_reports_by_document(doc.id)
        if reports:
            any_reports = True
            with st.container(border=True):
                st.markdown(f"#### 📄 {doc.filename}")
                for report in reports:
                    col1, col2, col3 = st.columns([3, 2, 2])
                    with col1:
                        st.write(f"Type: **{report.report_type.upper()}**")
                    with col2:
                        st.write(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M') if report.generated_at else 'N/A'}")
                    with col3:
                        try:
                            with open(report.file_path, "rb") as f:
                                st.download_button(
                                    "⬇️ Download",
                                    f,
                                    file_name=report.file_path.split("/")[-1].split("\\")[-1],
                                    key=f"report_dl_{report.id}"
                                )
                        except FileNotFoundError:
                            st.caption("File not found on disk")

    if not any_reports:
        st.info("No reports generated yet. Go to 'Upload Document', analyze a document, then use the 'Download Report' section to generate one.")


def page_profile():
    """User profile page showing account information"""
    st.title("👤 User Profile")
    st.markdown("---")

    from services.upload_service import get_upload_statistics

    with st.container(border=True):
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("### 👤")
            st.markdown(f"**{st.session_state.role.upper()}**")

        with col2:
            st.markdown("### Account Information")

            info_data = {
                "Username": st.session_state.username,
                "Email": st.session_state.email,
                "Role": st.session_state.role.capitalize(),
                "Account Created": st.session_state.created_at.strftime("%B %d, %Y at %I:%M %p") if st.session_state.created_at else "N/A"
            }

            for label, value in info_data.items():
                st.markdown(f"**{label}:** {value}")

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        with st.container(border=True):
            st.markdown("### 📊 Activity Statistics")

            stats = get_upload_statistics(st.session_state.user_id)

            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("Documents Uploaded", stats['total_documents'])
            with metric_col2:
                st.metric("Analyses Completed", "0", help="Coming soon")

            if stats['total_documents'] > 0:
                st.markdown("**By File Type:**")
                st.markdown(f"- PDF: {stats['pdf_count']}")
                st.markdown(f"- DOCX: {stats['docx_count']}")
                st.markdown(f"- TXT: {stats['txt_count']}")

    with col4:
        with st.container(border=True):
            st.markdown("### ⚙️ Account Actions")

            st.button("🔒 Change Password", disabled=True, use_container_width=True,
                     help="Password change feature coming soon")
            st.button("✏️ Update Email", disabled=True, use_container_width=True,
                     help="Email update feature coming soon")
            st.button("🗑️ Delete Account", disabled=True, use_container_width=True,
                     help="Account deletion feature coming soon")

    st.markdown("---")
    st.caption("💡 More profile features will be added in future updates")


def page_admin_panel():
    """Admin panel with user info and system statistics"""
    st.title("⚙️ Admin Panel")

    if st.session_state.role != "admin":
        st.error("⛔ Access Denied: Admin privileges required")
        return

    st.markdown("---")
    st.success("✅ Admin access granted")

    from services.upload_service import get_upload_statistics
    from database.db import get_db, close_db
    from database.models import User

    tab1, tab2, tab3 = st.tabs(["👥 User Management", "📊 System Stats", "⚙️ Settings"])

    with tab1:
        st.markdown("### User Management")

        db = get_db()
        try:
            users = db.query(User).order_by(User.created_at.desc()).all()

            st.markdown(f"**Total Users:** {len(users)}")
            st.markdown("---")

            for user in users:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 2])

                    with col1:
                        st.markdown(f"**{user.username}**")

                    with col2:
                        st.markdown(f"{user.email}")

                    with col3:
                        role_badge = "🛡️ Admin" if user.role == "admin" else "👤 User"
                        st.markdown(role_badge)

                    with col4:
                        created = user.created_at.strftime("%Y-%m-%d")
                        st.caption(f"Created: {created}")

        except Exception as e:
            st.error(f"Error fetching users: {e}")
        finally:
            close_db(db)

    with tab2:
        st.markdown("### System Statistics")

        system_stats = get_upload_statistics()

        db = get_db()
        try:
            user_count = db.query(User).count()
        except:
            user_count = 0
        finally:
            close_db(db)

        with st.container(border=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Users", user_count)
            with col2:
                st.metric("Total Documents", system_stats['total_documents'])
            with col3:
                st.metric("Total Analyses", "0", help="Coming soon")
            with col4:
                st.metric("Total Risks Found", "0", help="Coming soon")

        st.markdown("---")

        with st.container(border=True):
            st.markdown("### 📄 Document Type Distribution")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📕 PDF Files", system_stats['pdf_count'])
            with col2:
                st.metric("📘 DOCX Files", system_stats['docx_count'])
            with col3:
                st.metric("📄 TXT Files", system_stats['txt_count'])

            if system_stats['total_documents'] > 0:
                import pandas as pd

                st.markdown("---")
                chart_data = pd.DataFrame({
                    'Type': ['PDF', 'DOCX', 'TXT'],
                    'Count': [system_stats['pdf_count'], system_stats['docx_count'], system_stats['txt_count']]
                })
                st.bar_chart(chart_data.set_index('Type'))

    with tab3:
        st.markdown("### Application Settings")
        st.info("System configuration and settings will be available in future updates.")

        st.checkbox("Enable email notifications", value=False, disabled=True)
        st.checkbox("Enable automatic backups", value=False, disabled=True)
        st.selectbox("Default risk threshold", ["Low", "Medium", "High"], disabled=True)


# ============================================================================
# MAIN APP ENTRY / ROUTING
# ============================================================================

def main():
    """Main application entry point"""

    if not st.session_state.logged_in:
        display_login_register()
        return

    # Build the list of pages - each becomes its own URL via st.navigation
    pages = [
        st.Page(page_home, title="Home", icon="🏠", url_path="home", default=True),
        st.Page(page_upload, title="Upload Document", icon="📤", url_path="upload"),
        st.Page(page_dashboard, title="Dashboard", icon="📊", url_path="dashboard"),
        st.Page(page_history, title="History", icon="📜", url_path="history"),
        st.Page(page_reports, title="Reports", icon="📈", url_path="reports"),
        st.Page(page_profile, title="Profile", icon="👤", url_path="profile"),
    ]

    if st.session_state.role == "admin":
        pages.append(st.Page(page_admin_panel, title="Admin Panel", icon="⚙️", url_path="admin"))

    # Hide the built-in nav widget so we can place our own title/user-info
    # block ABOVE the navigation links, in whatever order we want.
    pg = st.navigation(pages, position="hidden")

    # --- Sidebar: title & user info FIRST, then navigation links below ---
    st.sidebar.title("🔍 Contract Analyzer")
    st.sidebar.success(f"👤 Logged in as: **{st.session_state.username}**")
    st.sidebar.caption(f"Role: {st.session_state.role.upper()}")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()

    for page in pages:
        st.sidebar.page_link(page, icon=page.icon)

    pg.run()


if __name__ == "__main__":
    main()