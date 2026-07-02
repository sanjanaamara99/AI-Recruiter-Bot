import logging
from flask import Blueprint, request, jsonify, send_file
from database.db import get_db_session
from database.models import Report
from services.report_generator import report_generator
import os

logger = logging.getLogger(__name__)

report_bp = Blueprint('report', __name__, url_prefix='/api')


@report_bp.route('/report/<int:session_id>', methods=['GET'])
def get_report(session_id: int):
    """
    Get interview report (JSON format).
    
    Path Parameters:
        - session_id: Interview session ID
        
    Response:
        - complete interview report in JSON format
    """
    try:
        db = get_db_session()
        
        try:
            # Check if report already exists
            report = db.query(Report).filter_by(session_id=session_id).first()
            
            if report:
                return jsonify({
                    'success': True,
                    'data': {
                        'report_id': report.id,
                        'report': report.report_json,
                        'pdf_available': report.pdf_path is not None,
                        'created_at': report.created_at.isoformat() if report.created_at else None
                    }
                }), 200
            
            # Generate new report
            logger.info(f"Generating new report for session {session_id}")
            result = report_generator.generate_report(session_id)
            
            return jsonify({
                'success': True,
                'message': 'Report generated successfully',
                'data': {
                    'report_id': result['report_id'],
                    'report': result['report_data'],
                    'pdf_available': True
                }
            }), 200
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error getting report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@report_bp.route('/download-report/<int:session_id>', methods=['GET'])
def download_report(session_id: int):
    """
    Download interview report as PDF.
    
    Path Parameters:
        - session_id: Interview session ID
        
    Response:
        - PDF file download
    """
    try:
        db = get_db_session()
        
        try:
            # Check if report exists
            report = db.query(Report).filter_by(session_id=session_id).first()
            
            if not report:
                # Generate report if it doesn't exist
                logger.info(f"Generating report for session {session_id}")
                result = report_generator.generate_report(session_id)
                pdf_path = result['pdf_path']
            else:
                pdf_path = report.pdf_path
            
            # Check if PDF file exists
            if not os.path.exists(pdf_path):
                return jsonify({
                    'success': False,
                    'error': 'PDF file not found'
                }), 404
            
            # Send PDF file
            return send_file(
                pdf_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'interview_report_{session_id}.pdf'
            )
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
