import os
import logging
import tempfile
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from pydantic import BaseModel, ValidationError
from typing import Optional
from datetime import datetime
from config import Config
from services.interview_engine import interview_engine
from services.speech_to_text import speech_to_text_service
from database.db import get_db_session
from database.models import InterviewSession, InterviewStatus

logger = logging.getLogger(__name__)

interview_bp = Blueprint('interview', __name__, url_prefix='/api')


class StartInterviewRequest(BaseModel):
    """Request model for starting interview."""
    candidate_id: int


class SubmitAnswerRequest(BaseModel):
    """Request model for submitting answer."""
    question_id: int
    transcript: Optional[str] = None


def allowed_audio_file(filename: str) -> bool:
    """Check if audio file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_AUDIO_EXTENSIONS


@interview_bp.route('/start-interview', methods=['POST'])
def start_interview():
    """
    Start a new interview session.
    
    Request:
        - candidate_id: ID of the candidate
        
    Response:
        - session information
        - first question
    """
    try:
        data = request.get_json()
        
        if not data or 'candidate_id' not in data:
            return jsonify({
                'success': False,
                'error': 'candidate_id is required'
            }), 400
        
        # Validate request
        try:
            req = StartInterviewRequest(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        
        # Start interview
        result = interview_engine.start_interview(req.candidate_id)
        
        # Get first question
        first_question = interview_engine.get_next_question(result['session']['id'])
        
        return jsonify({
            'success': True,
            'message': 'Interview started successfully',
            'data': {
                'session': result['session'],
                'candidate': result['candidate'],
                'total_questions': result['total_questions'],
                'first_question': first_question
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error starting interview: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@interview_bp.route('/next-question', methods=['GET'])
def get_next_question():
    """
    Get the next unanswered question.
    
    Query Parameters:
        - session_id: Interview session ID
        
    Response:
        - next question or completion message
    """
    try:
        session_id = request.args.get('session_id', type=int)
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'session_id is required'
            }), 400
        
        # Get next question
        question = interview_engine.get_next_question(session_id)
        
        if question:
            return jsonify({
                'success': True,
                'data': {
                    'question': question,
                    'has_more_questions': True
                }
            }), 200
        else:
            # No more questions - interview complete
            db = get_db_session()
            try:
                session = db.query(InterviewSession).filter_by(id=session_id).first()
                if session:
                    session.status = InterviewStatus.COMPLETED
                    session.ended_at = datetime.utcnow()
                    db.commit()
            finally:
                db.close()
            
            return jsonify({
                'success': True,
                'message': 'Interview completed',
                'data': {
                    'question': None,
                    'has_more_questions': False
                }
            }), 200
    
    except Exception as e:
        logger.error(f"Error getting next question: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@interview_bp.route('/upload-audio-answer', methods=['POST'])
def upload_audio_answer():
    """
    Upload audio answer and convert to text.
    
    Request:
        - audio: Audio file
        - question_id: Question ID
        
    Response:
        - transcript
        - evaluation
        - follow-up questions
    """
    try:
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        question_id = request.form.get('question_id', type=int)
        
        if not question_id:
            return jsonify({
                'success': False,
                'error': 'question_id is required'
            }), 400
        
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No audio file selected'
            }), 400
        
        if not allowed_audio_file(audio_file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid audio file type. Allowed types: {", ".join(Config.ALLOWED_AUDIO_EXTENSIONS)}'
            }), 400
        
        # Save audio file
        filename = secure_filename(audio_file.filename)
        audio_path = os.path.join(Config.AUDIO_FOLDER, f"{question_id}_{filename}")
        audio_file.save(audio_path)
        
        logger.info(f"Audio file saved: {audio_path}")
        
        # Transcribe audio
        transcription = speech_to_text_service.transcribe_audio(audio_path)
        transcript = transcription['text']
        
        logger.info(f"Audio transcribed: {len(transcript)} characters")
        
        # Submit answer
        result = interview_engine.submit_answer(
            question_id=question_id,
            transcript=transcript,
            audio_file=audio_path
        )
        
        return jsonify({
            'success': True,
            'message': 'Answer submitted successfully',
            'data': {
                'transcript': transcript,
                'answer': result['answer'],
                'evaluation': result['evaluation'],
                'followup_questions': result['followup_questions']
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error uploading audio answer: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@interview_bp.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Transcribe audio to text only (no evaluation).
    
    Request:
        - audio: Audio file
        
    Response:
        - transcript text
    """
    try:
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No audio file selected'
            }), 400
        
        # Save audio file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_audio_path = temp_audio.name
        
        logger.info(f"Temporary audio file saved: {temp_audio_path}")
        
        try:
            # Transcribe audio
            transcription = speech_to_text_service.transcribe_audio(temp_audio_path)
            transcript = transcription['text']
            
            logger.info(f"Audio transcribed: {len(transcript)} characters")
            
            return jsonify({
                'success': True,
                'message': 'Audio transcribed successfully',
                'data': {
                    'transcript': transcript
                }
            }), 200
        finally:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
    
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@interview_bp.route('/evaluate-answer', methods=['POST'])
def evaluate_answer():
    """
    Submit text answer for evaluation.
    
    Request:
        - question_id: Question ID
        - transcript: Answer text
        
    Response:
        - evaluation
        - follow-up questions
    """
    try:
        data = request.get_json()
        
        if not data or 'question_id' not in data or 'transcript' not in data:
            return jsonify({
                'success': False,
                'error': 'question_id and transcript are required'
            }), 400
        
        # Validate request
        try:
            req = SubmitAnswerRequest(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        
        # Submit answer
        result = interview_engine.submit_answer(
            question_id=req.question_id,
            transcript=req.transcript
        )
        
        return jsonify({
            'success': True,
            'message': 'Answer evaluated successfully',
            'data': {
                'answer': result['answer'],
                'evaluation': result['evaluation'],
                'followup_questions': result['followup_questions']
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error evaluating answer: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@interview_bp.route('/interview-status/<int:session_id>', methods=['GET'])
def get_interview_status(session_id: int):
    """
    Get interview session status and progress.
    
    Path Parameters:
        - session_id: Interview session ID
        
    Response:
        - session information
        - progress statistics
    """
    try:
        db = get_db_session()
        
        try:
            from database.models import Question, Answer
            
            session = db.query(InterviewSession).filter_by(id=session_id).first()
            
            if not session:
                return jsonify({
                    'success': False,
                    'error': 'Interview session not found'
                }), 404
            
            # Get progress statistics
            total_questions = db.query(Question).filter_by(session_id=session_id).count()
            answered_questions = db.query(Answer).join(Question).filter(
                Question.session_id == session_id
            ).count()
            
            return jsonify({
                'success': True,
                'data': {
                    'session': session.to_dict(),
                    'progress': {
                        'total_questions': total_questions,
                        'answered_questions': answered_questions,
                        'remaining_questions': total_questions - answered_questions,
                        'completion_percentage': round((answered_questions / total_questions * 100), 2) if total_questions > 0 else 0
                    }
                }
            }), 200
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error getting interview status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
