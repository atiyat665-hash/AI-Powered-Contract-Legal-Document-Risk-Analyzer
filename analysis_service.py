from database.models import Report

def save_report_record(document_id, report_type, file_path):
    session = SessionLocal()
    try:
        report = Report(document_id=document_id, report_type=report_type,
                         file_path=file_path, generated_at=datetime.now())
        session.add(report)
        session.commit()
        session.refresh(report)
        return report
    finally:
        session.close()


def get_reports_by_document(document_id):
    session = SessionLocal()
    try:
        return session.query(Report).filter(Report.document_id == document_id).all()
    finally:
        session.close()