"""
AI-Powered Contract & Legal Document Risk Analyzer
Main Streamlit Application

This is a single Streamlit application that combines frontend and backend logic.
No separate FastAPI server is required.
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
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #e0e0e0;
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)
# Initialize database on startup
# Using @st.cache_resource to ensure it runs only once
@st.cache_resource
def initialize_database():
    """Initialize the database tables and seed admin user if needed"""
    init_db()
    seed_admin_user()
    return True

# Call database initialization
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


def main():
    """Main application entry point"""
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        # Show login/register page
        display_login_register()
    else:
        # User is logged in - show full application
        
        # Sidebar navigation
        st.sidebar.title("🔍 Contract Analyzer")
        st.sidebar.markdown("---")
        
        # User info in sidebar
        st.sidebar.success(f"👤 Logged in as: **{st.session_state.username}**")
        st.sidebar.caption(f"Role: {st.session_state.role.upper()}")
        
        # Logout button
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()
        
        st.sidebar.markdown("---")
        
        # Build navigation menu based on role
        menu_options = [
            "🏠 Home",
            "📤 Upload Document",
            "📊 Dashboard",
            "📜 History",
            "📈 Reports",
            "👤 Profile"
        ]
        
        # Add Admin Panel only for admin users
        if st.session_state.role == "admin":
            menu_options.append("⚙️ Admin Panel")
        
        # Navigation menu
        menu_option = st.sidebar.radio("Navigation", menu_options)
        
        st.sidebar.markdown("---")
        st.sidebar.info("**Status:** Ready")
        
        # Main content area
        st.title("📄 AI-Powered Contract & Legal Document Risk Analyzer")
        st.markdown("### Intelligent Contract Analysis & Risk Assessment")
        
        # Display content based on selected menu option
        if menu_option == "🏠 Home":
            display_home()
        elif menu_option == "📤 Upload Document":
            display_upload()
        elif menu_option == "📊 Dashboard":
            display_dashboard()
        elif menu_option == "📜 History":
            display_history()
        elif menu_option == "📈 Reports":
            display_reports()
        elif menu_option == "👤 Profile":
            display_profile()
        elif menu_option == "⚙️ Admin Panel":
            display_admin_panel()


def display_home():
    """Home page content"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Features")
        st.markdown("""
        - **Smart Upload**: PDF, DOCX, and image support
        - **AI Analysis**: Powered by Google Gemini
        - **Risk Detection**: Identify potential legal risks
        - **Semantic Search**: Find similar clauses
        - **Export Reports**: Generate professional PDFs
        """)
    
    with col2:
        st.markdown("### 📊 Analytics")
        st.markdown("""
        - **Visual Dashboards**: Interactive charts
        - **Risk Scoring**: Confidence-based metrics
        - **Trend Analysis**: Track document patterns
        - **Compliance Checks**: Regulatory alignment
        - **History Tracking**: Full audit trail
        """)
    
    with col3:
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


def display_login_register():
    """Login/Register page with tabs for authentication"""
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🔐 Welcome to Contract Risk Analyzer")
        st.markdown("Please login or create a new account to continue")
        st.markdown("---")
        
        # Create tabs for Login and Register
        tab_login, tab_register = st.tabs(["Login", "Register"])
        
        # LOGIN TAB
        with tab_login:
            st.subheader("Login to Your Account")
            
            with st.form("login_form"):
                login_username = st.text_input("Username", key="login_username")
                login_password = st.text_input("Password", type="password", key="login_password")
                
                submit_login = st.form_submit_button("Login", use_container_width=True)
                
                if submit_login:
                    if not login_username or not login_password:
                        st.error("Please enter both username and password")
                    else:
                        # Attempt login
                        success, user_data, message = login_user(login_username, login_password)
                        
                        if success:
                            # Set session state
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
            
            # Help text
            st.info("💡 **Default Admin Credentials** (for testing):\n\nUsername: `admin`\n\nPassword: `admin123`")
        
        # REGISTER TAB
        with tab_register:
            st.subheader("Create New Account")
            
            with st.form("register_form"):
                reg_username = st.text_input("Username", key="reg_username", 
                                             help="Choose a unique username")
                reg_email = st.text_input("Email", key="reg_email",
                                          help="Enter a valid email address")
                reg_password = st.text_input("Password", type="password", key="reg_password",
                                            help="Minimum 6 characters")
                reg_confirm_password = st.text_input("Confirm Password", type="password", 
                                                     key="reg_confirm_password")
                
                submit_register = st.form_submit_button("Register", use_container_width=True)
                
                if submit_register:
                    # Validation
                    if not reg_username or not reg_email or not reg_password or not reg_confirm_password:
                        st.error("All fields are required")
                    elif not validate_email(reg_email):
                        st.error("Invalid email format")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters long")
                    elif reg_password != reg_confirm_password:
                        st.error("Passwords do not match")
                    else:
                        # Attempt registration
                        success, message = register_user(reg_username, reg_email, reg_password, role="user")
                        
                        if success:
                            st.success(message)
                            st.info("✅ You can now login with your credentials")
                            st.balloons()
                        else:
                            st.error(message)
            
            # Additional info
            st.caption("By registering, you agree to our terms of service and privacy policy.")


def display_analysis_results(analysis):
    """
    Display contract analysis results in a structured format.
    
    Args:
        analysis: Analysis object from database
    """
    from services.analysis_service import format_analysis_for_display
    
    st.markdown("### 📋 Analysis Results")
    
    # Format data
    data = format_analysis_for_display(analysis)
    
    # Contract Overview
    st.markdown("#### Contract Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("📄 Contract Type", data['contract_type'])
    
    with col2:
        st.metric("⚖️ Jurisdiction", data['jurisdiction'])
    
    # Parties
    st.markdown("#### 👥 Parties Involved")
    if data['parties']:
        for i, party in enumerate(data['parties'], 1):
            st.markdown(f"{i}. **{party}**")
    else:
        st.caption("No parties specified")
    
    st.markdown("---")
    
    # Dates
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
    
    # Terms and Clauses
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
    
    # Metadata
    st.caption(f"✅ Analyzed on {data['analyzed_at']}")
    
    # View raw JSON
    with st.expander("🔍 View Raw JSON"):
        st.json(analysis.raw_json)


def display_upload():
    """Document upload page with file processing and AI analysis"""
    st.subheader("📤 Upload Document")
    st.markdown("Upload PDF, DOCX, or TXT files for analysis")
    st.markdown("---")
    
    # Import services
    from services.upload_service import validate_file, save_uploaded_file, create_document_record
    from services.extraction_service import extract_text, get_text_stats
    from services.gemini_service import is_gemini_configured, analyze_contract
    from services.analysis_service import save_analysis, get_analysis_by_document, format_analysis_for_display
    
    # Check Gemini configuration
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
    
    # File upload widget
    uploaded_file = st.file_uploader(
        "Choose a document",
        type=['pdf', 'docx', 'txt'],
        help="Maximum file size: 10MB"
    )
    
    if uploaded_file is not None:
        # Display file info
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
        
        # Process button
        if st.button("📄 Process Document", type="primary", use_container_width=True):
            
            # Validate file
            is_valid, error_message = validate_file(uploaded_file)
            
            if not is_valid:
                st.error(f"❌ {error_message}")
                return
            
            try:
                # Show progress
                with st.spinner("Processing document..."):
                    
                    # Step 1: Save file
                    status_placeholder = st.empty()
                    status_placeholder.info("💾 Saving file...")
                    
                    file_path, original_filename = save_uploaded_file(
                        uploaded_file,
                        st.session_state.user_id
                    )
                    
                    # Step 2: Extract text
                    status_placeholder.info("📝 Extracting text...")
                    
                    file_extension = original_filename.split('.')[-1].lower()
                    extracted_text, used_ocr = extract_text(file_path, file_extension)
                    
                    # Check if extraction was successful
                    if not extracted_text or len(extracted_text.strip()) < 10:
                        status_placeholder.error("⚠️ Failed to extract text from document. The file may be corrupted or empty.")
                        return
                    
                    # Step 3: Save to database
                    status_placeholder.info("💾 Saving to database...")
                    
                    document = create_document_record(
                        user_id=st.session_state.user_id,
                        filename=original_filename,
                        file_type=file_extension,
                        extracted_text=extracted_text
                    )
                    
                    status_placeholder.empty()
                
                # Store document ID in session state for analysis
                st.session_state.current_document_id = document.id
                st.session_state.current_document_text = extracted_text
                
                # Success message
                st.success(f"✅ Document processed successfully! Document ID: {document.id}")
                
                if used_ocr:
                    st.info("ℹ️ OCR was used to extract text from this document (scanned PDF detected)")
                
                # Display text statistics
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
                
                # Display extracted text preview
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
                
                # Show full text option
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
        
        # AI Analysis section (only if document was processed)
        if 'current_document_id' in st.session_state and st.session_state.get('current_document_id'):
            st.markdown("### 🤖 AI Analysis")
            
            # Check if already analyzed
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
                            # Analyze contract
                            analysis_result = analyze_contract(st.session_state.current_document_text)
                            
                            # Check for errors
                            if 'error' in analysis_result:
                                st.error(f"❌ {analysis_result['message']}")
                                
                                # Show retry button
                                if st.button("🔄 Retry Analysis"):
                                    st.rerun()
                                
                                # Show raw response for debugging
                                if analysis_result.get('raw_response'):
                                    with st.expander("🔍 Debug Information"):
                                        st.text_area("Raw Response", analysis_result['raw_response'], height=200)
                                
                            else:
                                # Save analysis
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
            
            # Display analysis results if available
            if existing_analysis:
                display_analysis_results(existing_analysis)
                
                # Risk Detection section
                st.markdown("---")
                st.markdown("### ⚠️ Risk Detection")
                
                from services.gemini_service import detect_risks
                from services.analysis_service import save_risk_reports, get_risk_reports_by_document, format_risk_for_display
                
                # Check if risks already exist
                existing_risks = get_risk_reports_by_document(st.session_state.current_document_id)
                
                if existing_risks and len(existing_risks) > 0:
                    st.info(f"✅ {len(existing_risks)} risk(s) detected. Showing results below.")
                    detect_risks_button = st.button("🔄 Re-detect Risks", key="redetect_risks_btn", use_container_width=True)
                else:
                    detect_risks_button = st.button("⚠️ Detect Risks", type="primary", key="detect_risks_btn", use_container_width=True)
                
                if detect_risks_button:
                    try:
                        with st.spinner("⚠️ Detecting risks... This may take a moment."):
                            # Get analysis dict for context
                            import json
                            analysis_dict = json.loads(existing_analysis.raw_json) if existing_analysis.raw_json else {}
                            
                            # Detect risks
                            risks_result = detect_risks(
                                st.session_state.current_document_text,
                                analysis_dict
                            )
                            
                            # Save risks
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
                
                # Display risks if available
                if existing_risks and len(existing_risks) > 0:
                    # Summary metrics
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
                    
                    # Display each risk
                    for risk in existing_risks:
                        risk_data = format_risk_for_display(risk)
                        
                        # Color-code by risk level
                        if risk_data['risk_level'] == 'High':
                            risk_color = "🔴"
                            container_type = "error"
                        elif risk_data['risk_level'] == 'Medium':
                            risk_color = "🟡"
                            container_type = "warning"
                        else:
                            risk_color = "🟢"
                            container_type = "info"
                        
                        with st.expander(f"{risk_color} {risk_data['risk_title']} ({risk_data['risk_level']} - {risk_data['confidence_percent']}% confidence)"):
                            st.markdown(f"**Risk Level:** {risk_data['risk_level']}")
                            st.markdown(f"**Confidence:** {risk_data['confidence_percent']}%")
                            st.markdown(f"**Explanation:** {risk_data['explanation']}")
                            st.markdown(f"**Recommendation:** {risk_data['recommendation']}")
                
                # Executive Summary section
                st.markdown("---")
                st.markdown("### 📝 Executive Summary")
                
                from services.gemini_service import generate_summary
                from services.analysis_service import save_summary, get_summary_by_document, format_summary_for_display
                
                # Check if summary already exists
                existing_summary = get_summary_by_document(st.session_state.current_document_id)
                
                # Only enable summary button if risks have been detected
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
                                # Get analysis dict and risks list
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
                                
                                # Generate summary
                                summary_result = generate_summary(
                                    st.session_state.current_document_text,
                                    analysis_dict,
                                    risks_list
                                )
                                
                                # Check for errors
                                if 'error' in summary_result and not summary_result.get('executive_summary'):
                                    st.error(f"❌ {summary_result.get('message', 'Unknown error')}")
                                    if st.button("🔄 Retry Summary Generation"):
                                        st.rerun()
                                else:
                                    # Save summary
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
                
                # Display summary if available
                if existing_summary:
                    summary_data = format_summary_for_display(existing_summary)
                    
                    # Executive Summary (highlighted)
                    st.info(f"**Executive Summary**\n\n{summary_data['executive_summary']}")
                    
                    st.markdown("---")
                    
                    # Two column layout for summaries
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Payment Summary
                        st.markdown("#### 💰 Payment Summary")
                        st.write(summary_data['payment_summary'])
                        
                        st.markdown("---")
                        
                        # Termination Summary
                        st.markdown("#### ❌ Termination Summary")
                        st.write(summary_data['termination_summary'])
                    
                    with col2:
                        # Risk Summary
                        st.markdown("#### ⚠️ Risk Summary")
                        st.write(summary_data['risk_summary'])
                    
                    st.markdown("---")
                    
                    # Key Obligations
                    st.markdown("#### 📋 Key Obligations")
                    if summary_data['key_obligations']:
                        for obligation in summary_data['key_obligations']:
                            st.markdown(f"- {obligation}")
                    else:
                        st.caption("No key obligations specified")
                    
                    st.markdown("---")
                    
                    # Important Dates
                    st.markdown("#### 📅 Important Dates")
                    if summary_data['important_dates']:
                        for date in summary_data['important_dates']:
                            st.markdown(f"- {date}")
                    else:
                        st.caption("No important dates specified")
                    
                    st.markdown("---")
                    
                    # Important Clauses
                    st.markdown("#### 📄 Important Clauses")
                    if summary_data['important_clauses']:
                        for clause in summary_data['important_clauses']:
                            st.markdown(f"- {clause}")
                    else:
                        st.caption("No important clauses highlighted")
                    
                    st.markdown("---")
                    
                    # Recommended Actions (numbered checklist)
                    st.markdown("#### ✅ Recommended Actions")
                    if summary_data['recommended_actions']:
                        for i, action in enumerate(summary_data['recommended_actions'], 1):
                            st.markdown(f"{i}. {action}")
                    else:
                        st.caption("No specific actions recommended")
                    
                    st.markdown("---")
                    st.caption(f"📝 Summary generated on {summary_data['created_at']}")

                    # Report Generation section
                    st.markdown("---")
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

    else:
        # Show upload instructions when no file is selected
        st.info("👆 Upload a document to get started")
        
        st.markdown("### 📋 Supported File Types")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📕 PDF**")
            st.markdown("- Standard PDF documents")
            st.markdown("- Scanned PDFs (with OCR)")
            
        with col2:
            st.markdown("**📘 DOCX**")
            st.markdown("- Microsoft Word documents")
            st.markdown("- Extracts from paragraphs and tables")
            
        with col3:
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


def display_dashboard():
    """Dashboard page with statistics"""
    st.subheader("📊 Dashboard")
    st.markdown("Overview of your document analysis activity")
    st.markdown("---")
    
    from services.upload_service import get_upload_statistics
    from services.analysis_service import get_analysis_statistics
    
    # Get user statistics
    upload_stats = get_upload_statistics(st.session_state.user_id)
    analysis_stats = get_analysis_statistics(st.session_state.user_id)
    
    # Display metrics
    st.markdown("### 📈 Your Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Documents",
            upload_stats['total_documents'],
            help="Total number of documents uploaded"
        )
    
    with col2:
        st.metric(
            "AI Analyses",
            analysis_stats['total_analyses'],
            help="Number of documents analyzed with AI"
        )
    
    with col3:
        analysis_percentage = 0
        if upload_stats['total_documents'] > 0:
            analysis_percentage = int((analysis_stats['total_analyses'] / upload_stats['total_documents']) * 100)
        st.metric(
            "Analyzed",
            f"{analysis_percentage}%",
            help="Percentage of documents analyzed"
        )
    
    with col4:
        st.metric(
            "Risk Reports",
            "0",
            help="Coming soon"
        )
    
    st.markdown("---")
    
    # Contract types breakdown
    if analysis_stats['top_contract_types']:
        st.markdown("### 📋 Top Contract Types")
        
        for contract_type, count in analysis_stats['top_contract_types'].items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{contract_type}**")
            with col2:
                st.markdown(f"**{count}** document{'s' if count > 1 else ''}")
        
        st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload New Document", use_container_width=True, type="primary"):
            # Navigation will be handled by sidebar
            st.info("👈 Use the sidebar to navigate to Upload")
    
    with col2:
        if st.button("📜 View History", use_container_width=True):
            st.info("👈 Use the sidebar to navigate to History")
    
    with col3:
        if st.button("📈 Generate Report", use_container_width=True, disabled=True):
            st.info("Report generation coming soon!")
    
    st.markdown("---")
    
    # Visual breakdown if there are documents
    if upload_stats['total_documents'] > 0:
        st.markdown("### 📊 Document Type Distribution")
        
        # Create simple bar chart data
        import pandas as pd
        
        chart_data = pd.DataFrame({
            'Type': ['PDF', 'DOCX', 'TXT'],
            'Count': [upload_stats['pdf_count'], upload_stats['docx_count'], upload_stats['txt_count']]
        })
        
        # Display as bar chart
        st.bar_chart(chart_data.set_index('Type'))
    
    else:
        st.info("📭 No documents yet. Upload your first document to see statistics!")
    
    st.markdown("---")
    
    # Coming soon features
    st.markdown("### 🚧 Coming Soon")
    st.markdown("""
    - 🔍 Semantic search across documents
    - 📊 Advanced analytics and trends
    - 📧 Automated alerts and notifications
    """)


def display_history():
    """History page showing uploaded documents"""
    st.subheader("📜 Document History")
    st.markdown("View and manage your uploaded documents")
    st.markdown("---")
    
    from services.upload_service import get_user_documents, delete_document
    from services.analysis_service import get_analysis_by_document
    
    # Fetch user's documents
    documents = get_user_documents(st.session_state.user_id)
    
    if not documents:
        st.info("📭 No documents uploaded yet. Upload your first document to get started!")
        if st.button("📤 Go to Upload"):
            st.session_state.nav_trigger = "📤 Upload Document"
            st.rerun()
        return
    
    # Display statistics
    st.markdown(f"### 📊 Total Documents: {len(documents)}")
    
    # Count by type
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
    
    # Display documents in a table-like format
    for idx, doc in enumerate(documents):
        # Check if document has analysis
        has_analysis = get_analysis_by_document(doc.id) is not None
        
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 2, 1, 1])
            
            with col1:
                st.markdown(f"**📄 {doc.filename}**")
                st.caption(f"ID: {doc.id}")
            
            with col2:
                # File type badge
                type_emoji = {
                    'pdf': '📕',
                    'docx': '📘',
                    'txt': '📄'
                }.get(doc.file_type, '📄')
                st.markdown(f"{type_emoji} **{doc.file_type.upper()}**")
            
            with col3:
                upload_date = doc.upload_date.strftime("%Y-%m-%d %H:%M")
                st.markdown(f"📅 {upload_date}")
            
            with col4:
                # Analysis status badge
                if has_analysis:
                    st.success("✅ Analyzed")
                else:
                    st.warning("⏳ Pending")
            
            with col5:
                # View button
                if st.button("👁️ View", key=f"view_{doc.id}", use_container_width=True):
                    st.session_state.selected_document = doc.id
                    st.session_state.show_document_details = True
            
            # Show document details if selected
            if st.session_state.get('show_document_details') and st.session_state.get('selected_document') == doc.id:
                with st.expander("📋 Document Details", expanded=True):
                    
                    # Document info
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
                    
                    # Show analysis if available
                    analysis = get_analysis_by_document(doc.id)
                    if analysis:
                        st.markdown("### 🤖 AI Analysis")
                        display_analysis_results(analysis)
                        st.markdown("---")
                    
                    # Extracted text preview
                    if doc.extracted_text:
                        st.markdown("**Extracted Text:**")
                        preview = doc.extracted_text[:1000]
                        if len(doc.extracted_text) > 1000:
                            preview += "\n\n... (truncated)"
                        st.text_area("", preview, height=200, disabled=True, label_visibility="collapsed")
                    else:
                        st.warning("No extracted text available")
                    
                    # Action buttons
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    
                    with btn_col1:
                        if analysis:
                            if st.button("🔄 Re-analyze", key=f"reanalyze_{doc.id}", use_container_width=True):
                                # Store doc for reanalysis
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
                                # Perform deletion
                                success, message = delete_document(doc.id, st.session_state.user_id)
                                if success:
                                    st.success(message)
                                    st.session_state.show_document_details = False
                                    st.rerun()
                                else:
                                    st.error(message)
                            else:
                                # Ask for confirmation
                                st.session_state[f"confirm_delete_{doc.id}"] = True
                                st.warning("⚠️ Click Delete again to confirm")
            
            st.markdown("---")
    
    # Pagination note (for future enhancement)
    if len(documents) >= 50:
        st.caption("📌 Showing most recent 50 documents")


def display_reports():
    """Reports page showing all generated reports for the user's documents"""
    st.subheader("📈 Reports")
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
            st.markdown("---")

    if not any_reports:
        st.info("No reports generated yet. Go to 'Upload Document', analyze a document, then use the 'Download Report' section to generate one.")


def display_profile():
    """User profile page showing account information"""
    st.subheader("👤 User Profile")
    st.markdown("---")
    
    from services.upload_service import get_upload_statistics
    
    # Display user information in a nice card-like layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Profile icon
        st.markdown("### 👤")
        st.markdown(f"**{st.session_state.role.upper()}**")
    
    with col2:
        # User details
        st.markdown("### Account Information")
        
        # Create info display
        info_data = {
            "Username": st.session_state.username,
            "Email": st.session_state.email,
            "Role": st.session_state.role.capitalize(),
            "Account Created": st.session_state.created_at.strftime("%B %d, %Y at %I:%M %p") if st.session_state.created_at else "N/A"
        }
        
        for label, value in info_data.items():
            st.markdown(f"**{label}:** {value}")
    
    st.markdown("---")
    
    # Additional profile sections
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 📊 Activity Statistics")
        
        # Get real statistics
        stats = get_upload_statistics(st.session_state.user_id)
        
        # Display metrics
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("Documents Uploaded", stats['total_documents'])
        with metric_col2:
            st.metric("Analyses Completed", "0", help="Coming soon")
        
        # Document type breakdown
        if stats['total_documents'] > 0:
            st.markdown("**By File Type:**")
            st.markdown(f"- PDF: {stats['pdf_count']}")
            st.markdown(f"- DOCX: {stats['docx_count']}")
            st.markdown(f"- TXT: {stats['txt_count']}")
    
    with col4:
        st.markdown("### ⚙️ Account Actions")
        
        # Future features
        st.button("🔒 Change Password", disabled=True, use_container_width=True,
                 help="Password change feature coming soon")
        st.button("✏️ Update Email", disabled=True, use_container_width=True,
                 help="Email update feature coming soon")
        st.button("🗑️ Delete Account", disabled=True, use_container_width=True,
                 help="Account deletion feature coming soon")
    
    st.markdown("---")
    st.caption("💡 More profile features will be added in future updates")


def display_admin_panel():
    """Admin panel with user info and system statistics"""
    st.subheader("⚙️ Admin Panel")
    
    # Check if user is admin
    if st.session_state.role != "admin":
        st.error("⛔ Access Denied: Admin privileges required")
        return
    
    st.markdown("---")
    st.success("✅ Admin access granted")
    
    from services.upload_service import get_upload_statistics
    from database.db import get_db, close_db
    from database.models import User
    
    # Admin sections
    tab1, tab2, tab3 = st.tabs(["👥 User Management", "📊 System Stats", "⚙️ Settings"])
    
    with tab1:
        st.markdown("### User Management")
        
        # Fetch all users
        db = get_db()
        try:
            users = db.query(User).order_by(User.created_at.desc()).all()
            
            st.markdown(f"**Total Users:** {len(users)}")
            st.markdown("---")
            
            # Display users in a table
            for user in users:
                with st.container():
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
                    
                    st.markdown("---")
            
        except Exception as e:
            st.error(f"Error fetching users: {e}")
        finally:
            close_db(db)
    
    with tab2:
        st.markdown("### System Statistics")
        
        # Get system-wide statistics
        system_stats = get_upload_statistics()  # No user_id = system-wide
        
        # Get user count
        db = get_db()
        try:
            user_count = db.query(User).count()
        except:
            user_count = 0
        finally:
            close_db(db)
        
        # Display metrics
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
        
        # Document type breakdown
        st.markdown("### 📄 Document Type Distribution")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📕 PDF Files", system_stats['pdf_count'])
        with col2:
            st.metric("📘 DOCX Files", system_stats['docx_count'])
        with col3:
            st.metric("📄 TXT Files", system_stats['txt_count'])
        
        # Visual chart if there are documents
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


if __name__ == "__main__":
    main()