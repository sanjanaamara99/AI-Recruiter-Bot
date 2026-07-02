import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/ai_interviewer'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Google Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    AUDIO_FOLDER = os.path.join(os.path.dirname(__file__), 'audio')
    REPORT_FOLDER = os.path.join(os.path.dirname(__file__), 'reports')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'flac'}
    
    # ChromaDB Configuration
    CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), 'chroma_db')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(os.path.dirname(__file__), 'logs', 'app.log')
    
    # Interview Configuration
    QUESTIONS_PER_INTERVIEW = 10
    TECHNICAL_QUESTIONS_PERCENT = 40
    PROJECT_QUESTIONS_PERCENT = 20
    PROBLEM_SOLVING_PERCENT = 20
    SYSTEM_DESIGN_PERCENT = 10
    BEHAVIORAL_PERCENT = 10
    
    # Scoring Thresholds
    STRONG_HIRE_THRESHOLD = 90
    HIRE_THRESHOLD = 75
    BORDERLINE_THRESHOLD = 60
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.AUDIO_FOLDER, exist_ok=True)
        os.makedirs(Config.REPORT_FOLDER, exist_ok=True)
        os.makedirs(Config.CHROMA_DB_PATH, exist_ok=True)
        os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)
