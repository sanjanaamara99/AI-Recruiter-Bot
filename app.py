import logging
import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database.db import init_database

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize configuration
    Config.init_app(app)
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    try:
        logger.info("Initializing database...")
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    # Register blueprints
    from routes.resume_routes import resume_bp
    from routes.interview_routes import interview_bp
    from routes.report_routes import report_bp
    
    app.register_blueprint(resume_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(report_bp)
    
    logger.info("Blueprints registered successfully")
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'Autonomous AI Interviewer',
            'version': '1.0.0'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with API information."""
        return jsonify({
            'service': 'Autonomous AI Interviewer API',
            'version': '1.0.0',
            'endpoints': {
                'resume': {
                    'POST /api/upload-resume': 'Upload and analyze candidate resume'
                },
                'interview': {
                    'POST /api/start-interview': 'Start a new interview session',
                    'GET /api/next-question': 'Get next interview question',
                    'POST /api/upload-audio-answer': 'Upload audio answer',
                    'POST /api/evaluate-answer': 'Submit text answer for evaluation',
                    'GET /api/interview-status/<session_id>': 'Get interview status'
                },
                'report': {
                    'GET /api/report/<session_id>': 'Get interview report (JSON)',
                    'GET /api/download-report/<session_id>': 'Download interview report (PDF)'
                }
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    logger.info("Starting Autonomous AI Interviewer API...")
    logger.info(f"Debug mode: {Config.DEBUG}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )
