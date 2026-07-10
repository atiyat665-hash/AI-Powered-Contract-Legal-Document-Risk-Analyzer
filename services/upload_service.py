"""
File Upload Service
Handles file validation, storage, and database record creation
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from database.db import get_db, close_db
from database.models import Document


# Configuration
UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}


def validate_file(uploaded_file) -> tuple[bool, str]:
    """
    Validate uploaded file based on extension and size.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if file passes validation, False otherwise
        - error_message: Description of validation error, empty string if valid
    """
    try:
        # Check if file exists
        if uploaded_file is None:
            return False, "No file uploaded"
        
        # Get file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        # Check file extension
        if file_extension not in ALLOWED_EXTENSIONS:
            return False, f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        
        # Check file size
        file_size = uploaded_file.size
        
        if file_size == 0:
            return False, "File is empty"
        
        if file_size > MAX_FILE_SIZE_BYTES:
            size_mb = file_size / (1024 * 1024)
            return False, f"File too large ({size_mb:.2f}MB). Maximum size: {MAX_FILE_SIZE_MB}MB"
        
        # All validations passed
        return True, ""
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def save_uploaded_file(uploaded_file, user_id: int) -> tuple[str, str]:
    """
    Save uploaded file to the uploads folder with a unique filename.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        user_id: ID of the user uploading the file
        
    Returns:
        Tuple of (file_path, original_filename)
        - file_path: Full path where file was saved
        - original_filename: Original name of the uploaded file
        
    Raises:
        Exception: If file cannot be saved
    """
    try:
        # Ensure upload folder exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Get original filename and extension
        original_filename = uploaded_file.name
        file_extension = original_filename.split('.')[-1].lower()
        
        # Generate unique filename: {uuid}_{user_id}.{extension}
        unique_id = uuid.uuid4().hex[:12]  # 12-character hex string
        unique_filename = f"{unique_id}_user{user_id}.{file_extension}"
        
        # Full file path
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Write file to disk
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        print(f"File saved: {file_path} (original: {original_filename})")
        
        return file_path, original_filename
        
    except Exception as e:
        print(f"Error saving file: {e}")
        raise Exception(f"Failed to save file: {str(e)}")


def create_document_record(
    user_id: int,
    filename: str,
    file_type: str,
    extracted_text: str
) -> Document:
    """
    Create a new document record in the database.
    
    Args:
        user_id: ID of the user who uploaded the document
        filename: Original filename of the document
        file_type: File extension (pdf, docx, txt)
        extracted_text: Extracted text content from the document
        
    Returns:
        Created Document object with all fields populated
        
    Raises:
        Exception: If database operation fails
    """
    db = get_db()
    
    try:
        # Create new document record
        new_document = Document(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            upload_date=datetime.utcnow(),
            extracted_text=extracted_text
        )
        
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
        
        print(f"Document record created: ID={new_document.id}, filename={filename}")
        
        return new_document
        
    except Exception as e:
        db.rollback()
        print(f"Error creating document record: {e}")
        raise Exception(f"Failed to create document record: {str(e)}")
        
    finally:
        close_db(db)


def get_user_documents(user_id: int, limit: int = 50) -> list[Document]:
    """
    Retrieve all documents uploaded by a specific user.
    
    Args:
        user_id: ID of the user
        limit: Maximum number of documents to return (default: 50)
        
    Returns:
        List of Document objects, ordered by upload_date descending
    """
    db = get_db()
    
    try:
        documents = db.query(Document)\
            .filter(Document.user_id == user_id)\
            .order_by(Document.upload_date.desc())\
            .limit(limit)\
            .all()
        
        return documents
        
    except Exception as e:
        print(f"Error fetching user documents: {e}")
        return []
        
    finally:
        close_db(db)


def get_document_by_id(document_id: int) -> Document:
    """
    Retrieve a specific document by ID.
    
    Args:
        document_id: ID of the document
        
    Returns:
        Document object or None if not found
    """
    db = get_db()
    
    try:
        document = db.query(Document)\
            .filter(Document.id == document_id)\
            .first()
        
        return document
        
    except Exception as e:
        print(f"Error fetching document: {e}")
        return None
        
    finally:
        close_db(db)


def delete_document(document_id: int, user_id: int) -> tuple[bool, str]:
    """
    Delete a document record and its associated file.
    Only allows deletion if the document belongs to the user.
    
    Args:
        document_id: ID of the document to delete
        user_id: ID of the user requesting deletion
        
    Returns:
        Tuple of (success, message)
    """
    db = get_db()
    
    try:
        # Fetch document
        document = db.query(Document)\
            .filter(Document.id == document_id)\
            .first()
        
        if not document:
            return False, "Document not found"
        
        # Check ownership
        if document.user_id != user_id:
            return False, "Unauthorized: You can only delete your own documents"
        
        # Delete database record
        db.delete(document)
        db.commit()
        
        # Note: Physical file deletion could be added here if needed
        # For now, we keep files for data recovery purposes
        
        return True, f"Document '{document.filename}' deleted successfully"
        
    except Exception as e:
        db.rollback()
        print(f"Error deleting document: {e}")
        return False, f"Failed to delete document: {str(e)}"
        
    finally:
        close_db(db)


def get_upload_statistics(user_id: int = None) -> dict:
    """
    Get upload statistics for a user or system-wide.
    
    Args:
        user_id: Optional user ID. If None, returns system-wide stats.
        
    Returns:
        Dictionary with upload statistics
    """
    db = get_db()
    
    try:
        query = db.query(Document)
        
        if user_id:
            query = query.filter(Document.user_id == user_id)
        
        total_documents = query.count()
        
        # Count by file type
        pdf_count = query.filter(Document.file_type == 'pdf').count()
        docx_count = query.filter(Document.file_type == 'docx').count()
        txt_count = query.filter(Document.file_type == 'txt').count()
        
        return {
            'total_documents': total_documents,
            'pdf_count': pdf_count,
            'docx_count': docx_count,
            'txt_count': txt_count
        }
        
    except Exception as e:
        print(f"Error getting upload statistics: {e}")
        return {
            'total_documents': 0,
            'pdf_count': 0,
            'docx_count': 0,
            'txt_count': 0
        }
        
    finally:
        close_db(db)
def get_document_by_id(document_id):
    """Fetch a single document by its ID."""
    from database.db import get_db, close_db
    from database.models import Document
    db = get_db()
    try:
        return db.query(Document).filter(Document.id == document_id).first()
    finally:
        close_db(db)