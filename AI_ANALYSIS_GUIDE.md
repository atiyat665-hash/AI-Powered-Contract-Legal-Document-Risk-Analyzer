# AI Contract Analysis Guide

## Overview

The Contract Risk Analyzer uses Google's Gemini 2.5 Flash model to analyze contract documents and extract structured information automatically. This guide covers setup, usage, and technical implementation.

---

## 🔑 Setup

### 1. Get a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

### 2. Configure the Application

Create or edit `.env` file in the project root:

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

**Important:** Never commit your `.env` file to version control. It's already in `.gitignore`.

### 3. Verify Configuration

Run the test script:

```bash
py test_gemini.py
```

This will:
- Check if API key is configured
- Test connection to Gemini
- Run a sample contract analysis
- Verify JSON parsing

---

## 🎯 Features

### Extracted Information

The AI extracts the following fields from contracts:

| Field | Description | Example |
|-------|-------------|---------|
| **contract_type** | Type of agreement | "Service Agreement", "NDA", "Lease Agreement" |
| **parties** | Parties involved | ["ABC Corp", "John Doe"] |
| **effective_date** | When contract starts | "2024-01-01", "January 1, 2024" |
| **expiry_date** | When contract ends | "2025-01-01", "12 months from effective date" |
| **payment_terms** | Payment obligations | "Monthly fee of $10,000 USD" |
| **renewal_clause** | Automatic renewal terms | "Automatically renews for 1 year" |
| **termination_clause** | How to end contract | "60 days written notice required" |
| **confidentiality** | NDA/confidentiality terms | "3 years after termination" |
| **responsibilities** | Key obligations | "Consultant provides development services" |
| **jurisdiction** | Governing law | "State of California", "England and Wales" |
| **notice_period** | Required notice time | "30 days", "60 days written notice" |

### Handling Missing Data

- If a field is not found: Returns `null`
- AI does not hallucinate or guess
- Only extracts explicitly stated information

---

## 📖 Usage

### Via Streamlit UI

1. **Upload a document**
   - Navigate to "Upload Document"
   - Choose PDF, DOCX, or TXT file
   - Click "Process Document"

2. **Analyze with AI**
   - After successful upload, click "Analyze with AI"
   - Wait for analysis (10-30 seconds typically)
   - View structured results

3. **View results**
   - Contract overview (type, jurisdiction)
   - Parties involved
   - Key dates (effective, expiry, notice period)
   - Terms and clauses (expandable sections)
   - Raw JSON (for debugging)

### From History

1. Go to "Document History"
2. Click "View" on any document
3. If not analyzed: Click "Analyze Now"
4. If already analyzed: View results or click "Re-analyze"

---

## 🔧 Technical Implementation

### Architecture

```
prompts/
  └── analysis_prompts.py        # Prompt engineering

services/
  ├── gemini_service.py          # API integration
  └── analysis_service.py        # Database operations

app.py                           # UI integration
```

### Key Components

#### 1. Prompt Engineering (`prompts/analysis_prompts.py`)

**CONTRACT_ANALYSIS_PROMPT:**
- Instructs Gemini to extract specific fields
- Emphasizes JSON-only output (no markdown)
- Specifies to use `null` for missing fields
- Warns against hallucination

**RETRY_STRICT_PROMPT:**
- Fallback prompt if first attempt fails
- Even stricter JSON requirements
- Used automatically on parsing errors

#### 2. Gemini Service (`services/gemini_service.py`)

**Key Functions:**

```python
# Initialize API
initialize_gemini() -> bool

# Check configuration
is_gemini_configured() -> bool

# Test connection
test_gemini_connection() -> tuple[bool, str]

# Main analysis function
analyze_contract(contract_text: str) -> Dict

# Utilities
strip_markdown_fences(text: str) -> str
truncate_contract_text(text: str, max_length: int) -> str
parse_json_response(response_text: str) -> Dict
```

**Error Handling:**
- API not configured → Clear setup instructions
- Rate limits → Retry suggestion
- Invalid JSON → Automatic retry with stricter prompt
- Network errors → User-friendly messages
- Safety filters → Feedback message

**Text Truncation:**
- Maximum: 15,000 characters (token limit protection)
- Smart truncation at sentence boundaries
- Maintains context integrity

#### 3. Analysis Service (`services/analysis_service.py`)

**Key Functions:**

```python
# Save to database
save_analysis(document_id: int, analysis_dict: Dict) -> Analysis

# Retrieve analysis
get_analysis_by_document(document_id: int) -> Analysis

# Format for display
format_analysis_for_display(analysis: Analysis) -> Dict

# Statistics
get_analysis_statistics(user_id: int) -> Dict
```

**Database Storage:**
- Structured fields in Analysis table
- Raw JSON in `raw_json` column
- Parties stored as JSON array
- Timestamps for audit trail

---

## 🎨 UI Components

### Upload Page Analysis Section

```python
# After document upload
if 'current_document_id' in st.session_state:
    # Check if already analyzed
    existing_analysis = get_analysis_by_document(doc_id)
    
    if existing_analysis:
        # Show re-analyze button
    else:
        # Show analyze button
    
    # Display results
    display_analysis_results(analysis)
```

### Analysis Results Display

**Sections:**
1. **Contract Overview**
   - Type and jurisdiction as metrics

2. **Parties Involved**
   - Numbered list of parties

3. **Key Dates**
   - Effective, expiry, and notice period

4. **Terms and Clauses**
   - Expandable sections for each clause
   - Payment, renewal, termination, etc.

5. **Raw JSON**
   - Collapsible debug view

---

## ⚙️ Configuration

### Model Selection

```python
# In services/gemini_service.py
MODEL_NAME = "gemini-2.5-flash"
```

**Why Gemini 2.5 Flash?**
- ⚡ Fast response times (10-30 seconds)
- 💰 Free tier friendly
- ✅ Good accuracy for structured extraction
- 📊 Cost-effective for high volume

**Alternatives:**
- `gemini-2.5-flash-thinking-exp`: Enhanced reasoning model
- `gemini-2.0-flash`: Older model (deprecated)
- `gemini-1.5-pro`: Older model (deprecated)

### Token Limits

```python
# In services/gemini_service.py
MAX_CONTRACT_LENGTH = 15000  # Characters
```

**Adjusting limits:**
- Increase for longer contracts
- Monitor API costs
- Consider multi-chunk processing for very long documents

### Retry Behavior

```python
# In gemini_service.py analyze_contract()
# First attempt with main prompt
response = model.generate_content(prompt)

# On JSON error, retry once
retry_response = model.generate_content(retry_prompt)
```

---

## 🚨 Error Handling

### Common Errors and Solutions

#### 1. API Not Configured

**Error:** "Gemini API not configured"

**Solution:**
1. Create `.env` file
2. Add `GEMINI_API_KEY=your_key`
3. Restart application

#### 2. Rate Limit Exceeded

**Error:** "API quota exceeded or rate limit reached"

**Solutions:**
- Wait a few minutes
- Check your quota at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Upgrade to paid tier if needed

#### 3. Invalid JSON Response

**Error:** "Invalid JSON response after retry"

**Causes:**
- Model returned text instead of JSON
- Markdown formatting added

**Handling:**
- Automatic retry with stricter prompt
- Fallback to error dict with raw response
- User can retry manually

#### 4. Network Errors

**Error:** "Network error"

**Solutions:**
- Check internet connection
- Verify firewall settings
- Try again

#### 5. Safety Filters

**Error:** "Content blocked by safety filters"

**Cause:** Document contains sensitive content

**Solution:**
- Review document content
- Remove sensitive information
- Contact support if legitimate content blocked

---

## 📊 Performance

### Typical Analysis Times

| Document Size | Time | Notes |
|---------------|------|-------|
| < 1,000 words | 5-10s | Very fast |
| 1,000-5,000 words | 10-20s | Normal |
| 5,000-10,000 words | 20-40s | Longer |
| > 10,000 words | 30-60s | May be truncated |

### Accuracy

**High accuracy for:**
- Standard contract formats
- Well-structured documents
- Common contract types

**May struggle with:**
- Highly unusual contract formats
- Very complex legal language
- Multiple languages in one document
- Scanned documents with OCR errors

**Tips for better accuracy:**
- Use clean, high-quality documents
- Ensure proper OCR for scanned docs
- Review and correct AI results

---

## 🔒 Security & Privacy

### Data Handling

1. **API Transmission:**
   - Contracts sent to Google Gemini API
   - Transmitted over HTTPS
   - Subject to Google's terms of service

2. **Local Storage:**
   - Analysis results stored in local SQLite database
   - Raw text and structured data saved
   - No data sent to third parties

3. **API Key Security:**
   - Stored in `.env` file (not committed)
   - Never exposed in UI or logs
   - Only prefix shown in debug info

### Best Practices

- ✅ Review terms before uploading sensitive contracts
- ✅ Use on internal documents first
- ✅ Verify AI results for critical contracts
- ✅ Keep API keys secure
- ✅ Rotate keys periodically
- ❌ Don't upload highly confidential contracts without review
- ❌ Don't share API keys

---

## 🧪 Testing

### Unit Tests

Run the test suite:

```bash
py test_gemini.py
```

**Tests include:**
1. Configuration check
2. API connection test
3. Contract analysis with sample
4. JSON parsing edge cases

### Integration Testing

1. **Upload and analyze:**
   ```
   streamlit run app.py
   → Upload test contract
   → Click "Analyze with AI"
   → Verify results
   ```

2. **Error scenarios:**
   - Remove API key → Check error message
   - Upload corrupted file → Check handling
   - Interrupt analysis → Check recovery

3. **Re-analysis:**
   - Analyze document twice
   - Verify update behavior
   - Check history shows latest

### Sample Test Contracts

Create test files with:
- Clear contract type
- Named parties
- Explicit dates
- Payment terms
- Termination clauses
- Jurisdiction

---

## 📈 Analytics

### Dashboard Metrics

- **Total Analyses:** Count of analyzed documents
- **Analyzed Percentage:** Ratio of analyzed/total
- **Top Contract Types:** Most common contract types

### History View

- **Analysis Status:** ✅ Analyzed or ⏳ Pending
- **Quick Actions:** Analyze or re-analyze
- **Inline Results:** View analysis in document details

---

## 🔮 Future Enhancements

### Planned Features

1. **Multi-language Support**
   - Detect document language
   - Extract in original language
   - Translate results

2. **Comparison Mode**
   - Compare two contracts
   - Highlight differences
   - Identify missing clauses

3. **Custom Fields**
   - User-defined extraction fields
   - Industry-specific templates
   - Custom prompts

4. **Batch Analysis**
   - Analyze multiple documents
   - Background processing
   - Progress tracking

5. **Analysis Confidence Scores**
   - Confidence per field
   - Highlight uncertain extractions
   - Suggest manual review

6. **Clause Library**
   - Save common clauses
   - Reuse in new contracts
   - Standard clause database

---

## 💡 Tips & Best Practices

### For Best Results

1. **Document Quality:**
   - Use high-quality PDFs
   - Ensure good OCR quality
   - Clean, formatted text

2. **Contract Format:**
   - Numbered sections
   - Clear headings
   - Standard terminology

3. **Review Results:**
   - Always verify AI extractions
   - Check dates and numbers carefully
   - Confirm party names

4. **Iterative Improvement:**
   - Note common errors
   - Refine prompt templates
   - Update extraction fields

### Prompt Engineering Tips

**Current prompt structure:**
1. Role definition ("expert legal contract analyzer")
2. Clear instructions
3. Field definitions with examples
4. Output format specification
5. Warnings against hallucination

**To customize:**
- Edit `prompts/analysis_prompts.py`
- Test with sample contracts
- Monitor accuracy
- Iterate and refine

---

## 🆘 Troubleshooting

### Issue: Analysis takes too long

**Causes:**
- Large document
- API slow response
- Network latency

**Solutions:**
- Check document size
- Try again during off-peak hours
- Consider document truncation

### Issue: Missing fields in results

**Causes:**
- Information not in contract
- Unusual phrasing
- Poor document quality

**Solutions:**
- Verify info exists in original
- Check extracted text quality
- Try re-analyzing
- Manual review and correction

### Issue: Incorrect extractions

**Causes:**
- Ambiguous contract language
- Non-standard format
- OCR errors

**Solutions:**
- Review original document
- Check OCR quality
- Consider manual correction
- Refine prompt if recurring

---

## 📚 API Reference

### Gemini Service API

```python
from services.gemini_service import analyze_contract

# Analyze contract
result = analyze_contract(contract_text)

# Check for errors
if 'error' in result:
    print(result['message'])
else:
    # Use structured data
    contract_type = result['contract_type']
    parties = result['parties']
    # ... etc
```

### Analysis Service API

```python
from services.analysis_service import save_analysis, get_analysis_by_document

# Save analysis
analysis = save_analysis(document_id, result_dict)

# Retrieve analysis
analysis = get_analysis_by_document(document_id)

# Format for display
data = format_analysis_for_display(analysis)
```

---

**Version:** 1.0  
**Last Updated:** January 2025  
**Model:** Google Gemini 2.5 Flash  
**Status:** ✅ Production Ready
