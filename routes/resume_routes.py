import os
import logging
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional
from config import Config
from services.interview_engine import interview_engine

logger = logging.getLogger(__name__)

resume_bp = Blueprint('resume', __name__, url_prefix='/api')


class ResumeUploadResponse(BaseModel):
    """Response model for resume upload."""
    success: bool
    message: str
    candidate_id: Optional[int] = None
    candidate_name: Optional[str] = None
    skills_count: Optional[int] = None


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@resume_bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    """
    Upload and process candidate resume.
    
    Request:
        - file: Resume file (PDF or DOCX)
        
    Response:
        - candidate information
        - resume analysis
        - extracted skills
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed types: {", ".join(Config.ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        logger.info(f"Resume file saved: {file_path}")
        
        # Process resume
        result = interview_engine.process_resume(file_path, filename)
        
        return jsonify({
            'success': True,
            'message': 'Resume processed successfully',
            'data': {
                'candidate': result['candidate'],
                'resume': result['resume'],
                'analysis': result['analysis'],
                'skills': result['skills']
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
