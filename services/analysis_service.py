"""
Analysis Service
Handles saving and retrieving contract analysis results from the database
"""
import json
from datetime import datetime
from typing import Dict, Optional
from database.db import get_db, close_db
from database.models import Analysis


def save_analysis(document_id: int, analysis_dict: Dict) -> Analysis:
    """
    Save contract analysis results to the database.
    
    Args:
        document_id: ID of the document being analyzed
        analysis_dict: Dictionary containing analysis results from Gemini
        
    Returns:
        Created Analysis object
        
    Raises:
        Exception: If database operation fails
    """
    db = get_db()
    
    try:
        # Check if analysis already exists for this document
        existing = db.query(Analysis)\
            .filter(Analysis.document_id == document_id)\
            .first()
        
        if existing:
            # Update existing analysis
            existing.contract_type = analysis_dict.get('contract_type')
            existing.parties = json.dumps(analysis_dict.get('parties')) if analysis_dict.get('parties') else None
            existing.effective_date = analysis_dict.get('effective_date')
            existing.expiry_date = analysis_dict.get('expiry_date')
            existing.payment_terms = analysis_dict.get('payment_terms')
            existing.renewal_clause = analysis_dict.get('renewal_clause')
            existing.termination_clause = analysis_dict.get('termination_clause')
            existing.confidentiality = analysis_dict.get('confidentiality')
            existing.responsibilities = analysis_dict.get('responsibilities')
            existing.jurisdiction = analysis_dict.get('jurisdiction')
            existing.raw_json = json.dumps(analysis_dict, indent=2)
            existing.created_at = datetime.utcnow()
            
            db.commit()
            db.refresh(existing)
            
            print(f"✓ Updated existing analysis for document {document_id}")
            return existing
        
        else:
            # Create new analysis
            # Handle parties list - store as JSON string
            parties_json = None
            if analysis_dict.get('parties'):
                if isinstance(analysis_dict['parties'], list):
                    parties_json = json.dumps(analysis_dict['parties'])
                else:
                    parties_json = str(analysis_dict['parties'])
            
            new_analysis = Analysis(
                document_id=document_id,
                contract_type=analysis_dict.get('contract_type'),
                parties=parties_json,
                effective_date=analysis_dict.get('effective_date'),
                expiry_date=analysis_dict.get('expiry_date'),
                payment_terms=analysis_dict.get('payment_terms'),
                renewal_clause=analysis_dict.get('renewal_clause'),
                termination_clause=analysis_dict.get('termination_clause'),
                confidentiality=analysis_dict.get('confidentiality'),
                responsibilities=analysis_dict.get('responsibilities'),
                jurisdiction=analysis_dict.get('jurisdiction'),
                raw_json=json.dumps(analysis_dict, indent=2),
                created_at=datetime.utcnow()
            )
            
            db.add(new_analysis)
            db.commit()
            db.refresh(new_analysis)
            
            print(f"✓ Created new analysis record: ID={new_analysis.id}, document_id={document_id}")
            return new_analysis
            
    except Exception as e:
        db.rollback()
        print(f"✗ Error saving analysis: {e}")
        raise Exception(f"Failed to save analysis: {str(e)}")
        
    finally:
        close_db(db)


def get_analysis_by_document(document_id: int) -> Optional[Analysis]:
    """
    Retrieve existing analysis for a document.
    
    Args:
        document_id: ID of the document
        
    Returns:
        Analysis object if found, None otherwise
    """
    db = get_db()
    
    try:
        analysis = db.query(Analysis)\
            .filter(Analysis.document_id == document_id)\
            .first()
        
        return analysis
        
    except Exception as e:
        print(f"✗ Error fetching analysis: {e}")
        return None
        
    finally:
        close_db(db)


def get_analysis_by_id(analysis_id: int) -> Optional[Analysis]:
    """
    Retrieve analysis by its ID.
    
    Args:
        analysis_id: ID of the analysis record
        
    Returns:
        Analysis object if found, None otherwise
    """
    db = get_db()
    
    try:
        analysis = db.query(Analysis)\
            .filter(Analysis.id == analysis_id)\
            .first()
        
        return analysis
        
    except Exception as e:
        print(f"✗ Error fetching analysis: {e}")
        return None
        
    finally:
        close_db(db)


def get_all_analyses(user_id: int = None, limit: int = 50) -> list[Analysis]:
    """
    Retrieve all analyses, optionally filtered by user.
    
    Args:
        user_id: Optional user ID to filter by
        limit: Maximum number of results
        
    Returns:
        List of Analysis objects
    """
    db = get_db()
    
    try:
        query = db.query(Analysis)
        
        if user_id:
            # Join with Document table to filter by user
            from database.models import Document
            query = query.join(Document).filter(Document.user_id == user_id)
        
        analyses = query.order_by(Analysis.created_at.desc()).limit(limit).all()
        
        return analyses
        
    except Exception as e:
        print(f"✗ Error fetching analyses: {e}")
        return []
        
    finally:
        close_db(db)


def delete_analysis(analysis_id: int) -> tuple[bool, str]:
    """
    Delete an analysis record.
    
    Args:
        analysis_id: ID of the analysis to delete
        
    Returns:
        Tuple of (success, message)
    """
    db = get_db()
    
    try:
        analysis = db.query(Analysis)\
            .filter(Analysis.id == analysis_id)\
            .first()
        
        if not analysis:
            return False, "Analysis not found"
        
        db.delete(analysis)
        db.commit()
        
        return True, f"Analysis {analysis_id} deleted successfully"
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error deleting analysis: {e}")
        return False, f"Failed to delete analysis: {str(e)}"
        
    finally:
        close_db(db)


def parse_parties_json(parties_str: Optional[str]) -> list:
    """
    Parse the parties JSON string back into a list.
    
    Args:
        parties_str: JSON string of parties
        
    Returns:
        List of party names, or empty list if invalid
    """
    if not parties_str:
        return []
    
    try:
        parties = json.loads(parties_str)
        if isinstance(parties, list):
            return parties
        return [str(parties)]
    except:
        return [parties_str]


def format_analysis_for_display(analysis: Analysis) -> Dict:
    """
    Format analysis data for display in the UI.
    
    Args:
        analysis: Analysis object from database
        
    Returns:
        Dictionary with formatted fields
    """
    # Parse parties from JSON
    parties = parse_parties_json(analysis.parties)
    
    return {
        'id': analysis.id,
        'document_id': analysis.document_id,
        'contract_type': analysis.contract_type or 'Not specified',
        'parties': parties,
        'effective_date': analysis.effective_date or 'Not specified',
        'expiry_date': analysis.expiry_date or 'Not specified',
        'payment_terms': analysis.payment_terms or 'Not specified',
        'renewal_clause': analysis.renewal_clause or 'Not specified',
        'termination_clause': analysis.termination_clause or 'Not specified',
        'confidentiality': analysis.confidentiality or 'Not specified',
        'responsibilities': analysis.responsibilities or 'Not specified',
        'jurisdiction': analysis.jurisdiction or 'Not specified',
        'analyzed_at': analysis.created_at.strftime("%B %d, %Y at %I:%M %p") if analysis.created_at else 'Unknown'
    }


def get_analysis_statistics(user_id: int = None) -> Dict:
    """
    Get statistics about analyses.
    
    Args:
        user_id: Optional user ID to filter by
        
    Returns:
        Dictionary with analysis statistics
    """
    db = get_db()
    
    try:
        query = db.query(Analysis)
        
        if user_id:
            from database.models import Document
            query = query.join(Document).filter(Document.user_id == user_id)
        
        total_analyses = query.count()
        
        # Count by contract type (top 5)
        contract_types = {}
        all_analyses = query.all()
        
        for analysis in all_analyses:
            if analysis.contract_type:
                contract_types[analysis.contract_type] = contract_types.get(analysis.contract_type, 0) + 1
        
        top_types = sorted(contract_types.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_analyses': total_analyses,
            'top_contract_types': dict(top_types)
        }
        
    except Exception as e:
        print(f"✗ Error getting analysis statistics: {e}")
        return {
            'total_analyses': 0,
            'top_contract_types': {}
        }
        
    finally:
        close_db(db)


# ============================================================================
# RISK REPORT FUNCTIONS
# ============================================================================

def save_risk_reports(document_id: int, risks_list: list[Dict]) -> list:
    """
    Save multiple risk reports for a document.
    Deletes existing risks for the document first to avoid duplicates.
    
    Args:
        document_id: ID of the document
        risks_list: List of risk dictionaries from Gemini
        
    Returns:
        List of created RiskReport objects
        
    Raises:
        Exception: If database operation fails
    """
    from database.models import RiskReport
    
    db = get_db()
    
    try:
        # Delete existing risks for this document
        db.query(RiskReport)\
            .filter(RiskReport.document_id == document_id)\
            .delete()
        
        # Create new risk reports
        created_risks = []
        for risk_dict in risks_list:
            risk_report = RiskReport(
                document_id=document_id,
                risk_title=risk_dict.get('risk_title', 'Unknown Risk'),
                risk_level=risk_dict.get('risk_level', 'Medium'),
                confidence_score=float(risk_dict.get('confidence_score', 0.5)),
                explanation=risk_dict.get('explanation', 'No explanation provided'),
                recommendation=risk_dict.get('recommendation', 'No recommendation provided'),
                created_at=datetime.utcnow()
            )
            db.add(risk_report)
            created_risks.append(risk_report)
        
        db.commit()
        
        # Refresh all created objects
        for risk in created_risks:
            db.refresh(risk)
        
        print(f"✓ Saved {len(created_risks)} risk report(s) for document {document_id}")
        return created_risks
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error saving risk reports: {e}")
        raise Exception(f"Failed to save risk reports: {str(e)}")
        
    finally:
        close_db(db)


def get_risk_reports_by_document(document_id: int) -> list:
    """
    Retrieve all risk reports for a document.
    
    Args:
        document_id: ID of the document
        
    Returns:
        List of RiskReport objects
    """
    from database.models import RiskReport
    
    db = get_db()
    
    try:
        risks = db.query(RiskReport)\
            .filter(RiskReport.document_id == document_id)\
            .order_by(RiskReport.created_at.desc())\
            .all()
        
        return risks
        
    except Exception as e:
        print(f"✗ Error fetching risk reports: {e}")
        return []
        
    finally:
        close_db(db)


def get_risk_statistics(user_id: int = None) -> Dict:
    """
    Get statistics about risk reports.
    
    Args:
        user_id: Optional user ID to filter by
        
    Returns:
        Dictionary with risk statistics
    """
    from database.models import RiskReport, Document
    
    db = get_db()
    
    try:
        query = db.query(RiskReport).join(Document)
        
        if user_id:
            query = query.filter(Document.user_id == user_id)
        
        all_risks = query.all()
        total_risks = len(all_risks)
        
        # Count by risk level
        high_risks = sum(1 for r in all_risks if r.risk_level == 'High')
        medium_risks = sum(1 for r in all_risks if r.risk_level == 'Medium')
        low_risks = sum(1 for r in all_risks if r.risk_level == 'Low')
        
        # Count documents with risks
        documents_with_risks = db.query(Document.id)\
            .join(RiskReport)\
            .filter(Document.user_id == user_id if user_id else True)\
            .distinct()\
            .count()
        
        return {
            'total_risks': total_risks,
            'high_risks': high_risks,
            'medium_risks': medium_risks,
            'low_risks': low_risks,
            'documents_with_risks': documents_with_risks
        }
        
    except Exception as e:
        print(f"✗ Error getting risk statistics: {e}")
        return {
            'total_risks': 0,
            'high_risks': 0,
            'medium_risks': 0,
            'low_risks': 0,
            'documents_with_risks': 0
        }
        
    finally:
        close_db(db)


def format_risk_for_display(risk) -> Dict:
    """
    Format a RiskReport object for display in the UI.
    
    Args:
        risk: RiskReport object from database
        
    Returns:
        Dictionary with formatted fields
    """
    return {
        'id': risk.id,
        'document_id': risk.document_id,
        'risk_title': risk.risk_title,
        'risk_level': risk.risk_level,
        'confidence_score': risk.confidence_score,
        'confidence_percent': int(risk.confidence_score * 100),
        'explanation': risk.explanation,
        'recommendation': risk.recommendation,
        'created_at': risk.created_at.strftime("%B %d, %Y at %I:%M %p") if risk.created_at else 'Unknown'
    }


def delete_risk_reports(document_id: int) -> tuple[bool, str]:
    """
    Delete all risk reports for a document.
    
    Args:
        document_id: ID of the document
        
    Returns:
        Tuple of (success, message)
    """
    from database.models import RiskReport
    
    db = get_db()
    
    try:
        count = db.query(RiskReport)\
            .filter(RiskReport.document_id == document_id)\
            .delete()
        
        db.commit()
        
        return True, f"Deleted {count} risk report(s)"
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error deleting risk reports: {e}")
        return False, f"Failed to delete risk reports: {str(e)}"
        
    finally:
        close_db(db)


# ============================================================================
# SUMMARY FUNCTIONS
# ============================================================================

def save_summary(document_id: int, summary_dict: Dict) -> 'Summary':
    """
    Save executive summary for a document.
    Replaces existing summary if one exists.
    
    Args:
        document_id: ID of the document
        summary_dict: Dictionary containing summary data from Gemini
        
    Returns:
        Created or updated Summary object
        
    Raises:
        Exception: If database operation fails
    """
    from database.models import Summary
    
    db = get_db()
    
    try:
        # Check if summary already exists
        existing = db.query(Summary)\
            .filter(Summary.document_id == document_id)\
            .first()
        
        # Serialize list fields to JSON
        key_obligations_json = json.dumps(summary_dict.get('key_obligations', [])) if summary_dict.get('key_obligations') else None
        important_dates_json = json.dumps(summary_dict.get('important_dates', [])) if summary_dict.get('important_dates') else None
        important_clauses_json = json.dumps(summary_dict.get('important_clauses', [])) if summary_dict.get('important_clauses') else None
        recommended_actions_json = json.dumps(summary_dict.get('recommended_actions', [])) if summary_dict.get('recommended_actions') else None
        
        if existing:
            # Update existing summary
            existing.executive_summary = summary_dict.get('executive_summary')
            existing.key_obligations = key_obligations_json
            existing.important_dates = important_dates_json
            existing.important_clauses = important_clauses_json
            existing.payment_summary = summary_dict.get('payment_summary')
            existing.termination_summary = summary_dict.get('termination_summary')
            existing.risk_summary = summary_dict.get('risk_summary')
            existing.recommended_actions = recommended_actions_json
            existing.created_at = datetime.utcnow()
            
            db.commit()
            db.refresh(existing)
            
            print(f"✓ Updated existing summary for document {document_id}")
            return existing
        
        else:
            # Create new summary
            new_summary = Summary(
                document_id=document_id,
                executive_summary=summary_dict.get('executive_summary'),
                key_obligations=key_obligations_json,
                important_dates=important_dates_json,
                important_clauses=important_clauses_json,
                payment_summary=summary_dict.get('payment_summary'),
                termination_summary=summary_dict.get('termination_summary'),
                risk_summary=summary_dict.get('risk_summary'),
                recommended_actions=recommended_actions_json,
                created_at=datetime.utcnow()
            )
            
            db.add(new_summary)
            db.commit()
            db.refresh(new_summary)
            
            print(f"✓ Created new summary: ID={new_summary.id}, document_id={document_id}")
            return new_summary
            
    except Exception as e:
        db.rollback()
        print(f"✗ Error saving summary: {e}")
        raise Exception(f"Failed to save summary: {str(e)}")
        
    finally:
        close_db(db)


def get_summary_by_document(document_id: int) -> Optional['Summary']:
    """
    Retrieve summary for a document.
    
    Args:
        document_id: ID of the document
        
    Returns:
        Summary object if found, None otherwise
    """
    from database.models import Summary
    
    db = get_db()
    
    try:
        summary = db.query(Summary)\
            .filter(Summary.document_id == document_id)\
            .first()
        
        return summary
        
    except Exception as e:
        print(f"✗ Error fetching summary: {e}")
        return None
        
    finally:
        close_db(db)


def format_summary_for_display(summary: 'Summary') -> Dict:
    """
    Format a Summary object for display in the UI.
    Deserializes JSON fields back to lists.
    
    Args:
        summary: Summary object from database
        
    Returns:
        Dictionary with formatted and deserialized fields
    """
    def parse_json_field(field_value):
        """Helper to parse JSON field"""
        if not field_value:
            return []
        try:
            return json.loads(field_value)
        except:
            return []
    
    return {
        'id': summary.id,
        'document_id': summary.document_id,
        'executive_summary': summary.executive_summary or "Not available",
        'key_obligations': parse_json_field(summary.key_obligations),
        'important_dates': parse_json_field(summary.important_dates),
        'important_clauses': parse_json_field(summary.important_clauses),
        'payment_summary': summary.payment_summary or "Not specified in contract",
        'termination_summary': summary.termination_summary or "Not specified in contract",
        'risk_summary': summary.risk_summary or "Not available",
        'recommended_actions': parse_json_field(summary.recommended_actions),
        'created_at': summary.created_at.strftime("%B %d, %Y at %I:%M %p") if summary.created_at else 'Unknown'
    }


def delete_summary(document_id: int) -> tuple[bool, str]:
    """
    Delete summary for a document.
    
    Args:
        document_id: ID of the document
        
    Returns:
        Tuple of (success, message)
    """
    from database.models import Summary
    
    db = get_db()
    
    try:
        summary = db.query(Summary)\
            .filter(Summary.document_id == document_id)\
            .first()
        
        if not summary:
            return False, "Summary not found"
        
        db.delete(summary)
        db.commit()
        
        return True, "Summary deleted successfully"
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error deleting summary: {e}")
        return False, f"Failed to delete summary: {str(e)}"
        
    finally:
        close_db(db)


# ============================================================================
# REPORT FUNCTIONS
# ============================================================================

def save_report_record(document_id: int, report_type: str, file_path: str):
    """
    Save a record of a generated report (PDF/DOCX) to the database.

    Args:
        document_id: ID of the document the report belongs to
        report_type: 'pdf' or 'docx'
        file_path: Path where the report file was saved

    Returns:
        Created Report object

    Raises:
        Exception: If database operation fails
    """
    from database.models import Report

    db = get_db()

    try:
        report = Report(
            document_id=document_id,
            report_type=report_type,
            file_path=file_path,
            generated_at=datetime.utcnow()
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        print(f"✓ Saved report record: type={report_type}, document_id={document_id}")
        return report

    except Exception as e:
        db.rollback()
        print(f"✗ Error saving report record: {e}")
        raise Exception(f"Failed to save report record: {str(e)}")

    finally:
        close_db(db)


def get_reports_by_document(document_id: int) -> list:
    """
    Retrieve all generated reports for a document.

    Args:
        document_id: ID of the document

    Returns:
        List of Report objects, most recent first
    """
    from database.models import Report

    db = get_db()

    try:
        reports = db.query(Report)\
            .filter(Report.document_id == document_id)\
            .order_by(Report.generated_at.desc())\
            .all()

        return reports

    except Exception as e:
        print(f"✗ Error fetching reports: {e}")
        return []

    finally:
        close_db(db)