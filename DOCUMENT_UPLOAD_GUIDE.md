# Document Upload & Extraction Guide

## Overview

The Contract Risk Analyzer now supports uploading and processing documents with automatic text extraction. This guide covers the upload functionality, supported formats, and technical implementation.

---

## 📁 Supported File Types

### 1. PDF Files (`.pdf`)
- **Standard PDFs**: Direct text extraction using pdfplumber
- **Scanned PDFs**: Automatic OCR fallback using pytesseract
- **Features**:
  - Multi-page support
  - Preserves document structure
  - Automatic scanned document detection
  - High-quality OCR (300 DPI)

### 2. Word Documents (`.docx`)
- **Microsoft Word files**: Modern DOCX format
- **Features**:
  - Paragraph extraction
  - Table content extraction
  - Maintains text order
  - Cell-by-cell table processing

### 3. Text Files (`.txt`)
- **Plain text documents**
- **Features**:
  - UTF-8 encoding (primary)
  - Latin-1 fallback encoding
  - Direct reading, no parsing needed

---

## 🔧 Technical Architecture

### Services Overview

```
services/
├── extraction_service.py    # Text extraction logic
└── upload_service.py        # File handling & database
```

### Extraction Service Functions

#### `extract_text_from_pdf(file_path: str) -> str`
Extracts text from PDF files using pdfplumber.

**Process:**
1. Opens PDF file
2. Iterates through all pages
3. Extracts text from each page
4. Combines into single document

**Returns:** Extracted text with page separations

#### `extract_text_from_docx(file_path: str) -> str`
Extracts text from Word documents using python-docx.

**Process:**
1. Opens DOCX file
2. Extracts paragraphs
3. Extracts table content (cell by cell)
4. Combines in document order

**Returns:** Full document text with table data

#### `extract_text_from_txt(file_path: str) -> str`
Reads plain text files with encoding handling.

**Process:**
1. Attempts UTF-8 decoding
2. Falls back to Latin-1 if needed
3. Returns raw content

**Returns:** File content as string

#### `extract_text_from_scanned_pdf(file_path: str) -> str`
OCR fallback for scanned PDFs using pytesseract.

**Process:**
1. Converts each PDF page to image (300 DPI)
2. Applies Tesseract OCR
3. Combines results with page markers

**Returns:** OCR-extracted text

**Requirements:**
- Tesseract OCR installed on system
- Windows: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)

#### `clean_text(text: str) -> str`
Cleans and normalizes extracted text.

**Operations:**
- Removes control characters
- Normalizes line breaks
- Removes excessive whitespace
- Strips trailing spaces
- Consolidates blank lines

**Returns:** Cleaned, formatted text

#### `extract_text(file_path: str, file_type: str) -> tuple[str, bool]`
Main extraction function with automatic routing.

**Process:**
1. Routes to appropriate extractor based on file type
2. For PDFs: Checks if scanned (< 50 chars extracted)
3. Automatically applies OCR if needed
4. Cleans all extracted text

**Returns:** `(cleaned_text, used_ocr_flag)`

#### `get_text_stats(text: str) -> dict`
Calculates statistics about extracted text.

**Returns:**
```python
{
    'characters': int,  # Non-whitespace characters
    'words': int,       # Word count
    'lines': int,       # Non-empty lines
    'paragraphs': int   # Paragraph count
}
```

---

## 📤 Upload Service Functions

#### `validate_file(uploaded_file) -> tuple[bool, str]`
Validates uploaded files before processing.

**Checks:**
- File exists
- Extension is allowed (pdf, docx, txt)
- File is not empty
- File size under 10MB

**Returns:** `(is_valid, error_message)`

#### `save_uploaded_file(uploaded_file, user_id: int) -> tuple[str, str]`
Saves file to disk with unique naming.

**Naming Convention:**
```
{12_char_uuid}_user{user_id}.{extension}
Example: a1b2c3d4e5f6_user1.pdf
```

**Process:**
1. Creates `uploads/` directory if needed
2. Generates unique filename
3. Writes file to disk
4. Returns file path and original name

**Returns:** `(file_path, original_filename)`

#### `create_document_record(user_id, filename, file_type, extracted_text) -> Document`
Creates database record for uploaded document.

**Fields Saved:**
- `user_id`: Owner of document
- `filename`: Original filename
- `file_type`: Extension (pdf, docx, txt)
- `upload_date`: Current timestamp
- `extracted_text`: Full extracted content

**Returns:** Document object with database ID

#### `get_user_documents(user_id: int, limit: int = 50) -> list[Document]`
Retrieves user's uploaded documents.

**Parameters:**
- `user_id`: User to fetch documents for
- `limit`: Maximum documents to return (default: 50)

**Returns:** List of Document objects (newest first)

#### `get_document_by_id(document_id: int) -> Document`
Fetches a specific document by ID.

**Returns:** Document object or None

#### `delete_document(document_id: int, user_id: int) -> tuple[bool, str]`
Deletes a document (database record only).

**Security:**
- Verifies document ownership
- Only allows deletion of own documents

**Note:** Physical files are retained for data recovery

**Returns:** `(success, message)`

#### `get_upload_statistics(user_id: int = None) -> dict`
Calculates upload statistics.

**Parameters:**
- `user_id`: Optional. If None, returns system-wide stats

**Returns:**
```python
{
    'total_documents': int,
    'pdf_count': int,
    'docx_count': int,
    'txt_count': int
}
```

---

## 🎨 User Interface Flow

### Upload Page (`display_upload()`)

**When no file is selected:**
- Shows upload instructions
- Lists supported file types
- Displays feature list

**When file is selected:**
1. Shows file metadata (name, size, type)
2. "Process Document" button appears
3. On click:
   - Validates file
   - Saves to disk
   - Extracts text
   - Saves to database
   - Shows success message with Document ID
   - Displays extraction statistics
   - Shows text preview (first 2000 chars)
   - Provides full text view option

**Error Handling:**
- Invalid file type → Clear error message
- File too large → Size limit message
- Extraction failure → Corruption warning
- OCR required → Informational notice

### History Page (`display_history()`)

**Features:**
- Lists all user documents
- Shows document statistics
- File type badges
- Upload date display
- View document details
- Delete functionality (with confirmation)

**Document Details View:**
- Document ID and metadata
- Text length and word count
- Text preview (first 1000 chars)
- Action buttons:
  - Analyze (coming soon)
  - Close details
  - Delete (requires confirmation)

### Dashboard Page (`display_dashboard()`)

**Features:**
- Total document count
- Breakdown by file type
- Quick action buttons
- Visual chart of document types
- Upload prompts for new users

### Profile Page (`display_profile()`)

**Updated Statistics:**
- Real document upload count
- File type breakdown
- Analysis count (placeholder)

### Admin Panel (`display_admin_panel()`)

**System Statistics Tab:**
- System-wide document count
- Total users
- Document type distribution
- Visual charts

---

## 💻 Code Examples

### Basic Upload Flow

```python
from services.upload_service import validate_file, save_uploaded_file, create_document_record
from services.extraction_service import extract_text

# 1. Validate
is_valid, error = validate_file(uploaded_file)
if not is_valid:
    print(f"Error: {error}")
    return

# 2. Save file
file_path, original_name = save_uploaded_file(uploaded_file, user_id)

# 3. Extract text
file_type = original_name.split('.')[-1]
extracted_text, used_ocr = extract_text(file_path, file_type)

# 4. Save to database
document = create_document_record(user_id, original_name, file_type, extracted_text)

print(f"Document saved with ID: {document.id}")
```

### Get User Documents

```python
from services.upload_service import get_user_documents

# Fetch documents
documents = get_user_documents(user_id=1, limit=10)

for doc in documents:
    print(f"{doc.id}: {doc.filename} ({doc.file_type})")
    print(f"  Uploaded: {doc.upload_date}")
    print(f"  Text length: {len(doc.extracted_text)} chars")
```

### Text Extraction with Stats

```python
from services.extraction_service import extract_text, get_text_stats

# Extract
text, used_ocr = extract_text("document.pdf", "pdf")

# Get statistics
stats = get_text_stats(text)
print(f"Characters: {stats['characters']:,}")
print(f"Words: {stats['words']:,}")
print(f"Lines: {stats['lines']:,}")
print(f"Paragraphs: {stats['paragraphs']:,}")
```

---

## 🔒 Security Features

### File Validation
- ✅ Extension whitelist (pdf, docx, txt only)
- ✅ File size limit (10MB maximum)
- ✅ Empty file detection
- ✅ Existence check

### Access Control
- ✅ User-based document ownership
- ✅ Delete authorization check
- ✅ Unique filename generation (UUID)
- ✅ User ID in filename for tracking

### Error Handling
- ✅ Graceful degradation on extraction failure
- ✅ Encoding fallback (UTF-8 → Latin-1)
- ✅ Try-except blocks throughout
- ✅ User-friendly error messages
- ✅ Console logging for debugging

---

## 📊 Database Schema Usage

### Document Table

```python
class Document(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    filename = Column(String(255))              # Original name
    file_type = Column(String(50))              # pdf, docx, txt
    upload_date = Column(DateTime)              # Upload timestamp
    extracted_text = Column(Text)               # Full text content
    
    # Relationships
    user = relationship('User')
    analyses = relationship('Analysis')
    risk_reports = relationship('RiskReport')
```

**Indexed Fields:**
- `user_id` (for fast user queries)

**Storage:**
- `extracted_text` can store large amounts of text (TEXT type)
- SQLite has no practical limit for TEXT fields

---

## 🎯 Configuration

### File Size Limit

```python
# In services/upload_service.py
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
```

**To change:** Modify the `MAX_FILE_SIZE_MB` constant

### Allowed File Types

```python
# In services/upload_service.py
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
```

**To add types:** Add extensions to the set

### Upload Folder

```python
# In services/upload_service.py
UPLOAD_FOLDER = "uploads"
```

**To change:** Modify the `UPLOAD_FOLDER` constant

### OCR Threshold

```python
# In services/extraction_service.py (extract_text function)
if len(raw_text.strip()) < 50:  # Characters threshold
    # Apply OCR
```

**To adjust:** Change the `50` to desired character threshold

### OCR Resolution

```python
# In services/extraction_service.py (extract_text_from_scanned_pdf)
page_image = page.to_image(resolution=300)  # DPI
```

**To adjust:** Change `300` to desired DPI (higher = better quality, slower)

---

## 🧪 Testing

### Manual Testing Checklist

**Upload Functionality:**
- [ ] Upload PDF (standard)
- [ ] Upload PDF (scanned) - verify OCR
- [ ] Upload DOCX with tables
- [ ] Upload TXT file
- [ ] Try uploading file > 10MB (should fail)
- [ ] Try uploading unsupported file type (should fail)
- [ ] Upload empty file (should fail)

**Text Extraction:**
- [ ] Verify PDF text extraction
- [ ] Verify DOCX paragraph extraction
- [ ] Verify DOCX table extraction
- [ ] Verify TXT encoding (UTF-8)
- [ ] Verify TXT encoding fallback (Latin-1)
- [ ] Verify OCR on scanned PDF
- [ ] Verify text cleaning (whitespace removal)

**History & Management:**
- [ ] View uploaded documents
- [ ] View document details
- [ ] Delete document (with confirmation)
- [ ] Verify statistics update after upload
- [ ] Verify document count in dashboard
- [ ] Check profile statistics

**Admin Features:**
- [ ] View system-wide statistics
- [ ] View all users
- [ ] Check document type distribution chart

### Test Files

Create test files for comprehensive testing:

1. **standard.pdf** - Normal PDF with text
2. **scanned.pdf** - Scanned document image
3. **contract.docx** - Word doc with tables
4. **agreement.txt** - Plain text file
5. **large.pdf** - File over 10MB (for validation test)
6. **empty.txt** - Empty file (for validation test)

---

## 🚧 Known Limitations

1. **OCR Requirements:**
   - Requires Tesseract OCR installation
   - May be slow for large scanned PDFs
   - Accuracy depends on image quality

2. **File Size:**
   - Current limit: 10MB
   - Can be increased in configuration
   - Large files may slow down processing

3. **File Types:**
   - Only PDF, DOCX, TXT supported
   - No support for DOC (old Word format)
   - No support for RTF, ODT, or other formats

4. **Physical File Deletion:**
   - Delete only removes database record
   - Physical files remain in `uploads/` folder
   - Manual cleanup may be needed

5. **Encoding:**
   - TXT files: UTF-8 or Latin-1 only
   - Other encodings may fail

---

## 🔜 Future Enhancements

### Planned Features
- [ ] Support for more file formats (DOC, RTF, ODT)
- [ ] Image file upload (PNG, JPG) with direct OCR
- [ ] Batch upload (multiple files at once)
- [ ] File preview before extraction
- [ ] Download original file option
- [ ] Physical file cleanup utility
- [ ] Progress bar for large file processing
- [ ] Background processing for OCR
- [ ] Extraction quality scoring
- [ ] Manual text correction interface

### Performance Improvements
- [ ] Async file processing
- [ ] Caching for large documents
- [ ] Database indexing optimization
- [ ] Chunked text storage for very large docs
- [ ] Thumbnail generation for PDFs

---

## 🆘 Troubleshooting

### Issue: OCR not working

**Symptoms:** Error when processing scanned PDFs

**Solutions:**
1. Verify Tesseract is installed:
   ```bash
   tesseract --version
   ```

2. Windows: Add Tesseract to PATH or set path:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

3. Install Tesseract:
   - Windows: [Download here](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

### Issue: Encoding errors with TXT files

**Symptoms:** UnicodeDecodeError or garbled text

**Solutions:**
1. The service tries UTF-8 then Latin-1 automatically
2. For other encodings, manually convert file before upload
3. Or extend `extract_text_from_txt()` to try more encodings

### Issue: File upload fails silently

**Symptoms:** No error message, file not saved

**Solutions:**
1. Check console output for Python errors
2. Verify `uploads/` directory permissions
3. Check disk space
4. Verify file size is under 10MB

### Issue: Extracted text is empty

**Symptoms:** Document uploaded but no text extracted

**Causes:**
- PDF is actually an image (scanned) and OCR failed
- DOCX is corrupted
- File is actually empty
- Unsupported PDF encryption

**Solutions:**
1. For PDFs: Check if OCR was attempted
2. Try opening file in native application to verify content
3. Check console logs for extraction errors
4. Try re-saving file in supported format

### Issue: Text extraction is slow

**Symptoms:** Processing takes a long time

**Causes:**
- Large scanned PDF requiring OCR
- High-resolution images in document
- Many pages to process

**Solutions:**
1. OCR is inherently slow - this is normal for scanned docs
2. Consider reducing OCR resolution (trade quality for speed)
3. For future: implement background processing

---

## 📚 API Reference

See code comments in:
- `services/extraction_service.py` - Full extraction API
- `services/upload_service.py` - Full upload API

---

**Version:** 1.0  
**Last Updated:** January 2025  
**Status:** ✅ Complete and Tested
