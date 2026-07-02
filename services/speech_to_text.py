import os
import logging
# import whisper  # Commented out - install separately if needed
from typing import Optional

logger = logging.getLogger(__name__)


class SpeechToTextService:
    """Service for converting speech to text using Whisper."""
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper model.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
        """
        try:
            logger.info(f"Loading Whisper model: {model_name}")
            # Lazy loading - only load when actually needed
            import whisper
            self.model = whisper.load_model(model_name)
            logger.info("Whisper model loaded successfully")
        except ImportError:
            logger.warning("Whisper not installed. Audio transcription will not be available.")
            self.model = None
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            self.model = None
    
    def transcribe_audio(self, audio_file_path: str, language: str = "en") -> dict:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to audio file
            language: Language code (default: en)
            
        Returns:
            Transcription result with text and metadata
        """
        if not self.model:
            raise RuntimeError("Whisper model not loaded. Please install openai-whisper: pip install openai-whisper")
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            logger.info(f"Transcribing audio file: {audio_file_path}")
            
            result = self.model.transcribe(
                audio_file_path,
                language=language,
                fp16=False  # Use FP32 for CPU compatibility
            )
            
            transcript = result['text'].strip()
            
            logger.info(f"Transcription completed. Length: {len(transcript)} characters")
            
            return {
                'text': transcript,
                'language': result.get('language', language),
                'segments': result.get('segments', [])
            }
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise
    
    def validate_audio_file(self, file_path: str) -> bool:
        """
        Validate audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"Audio file does not exist: {file_path}")
            return False
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            logger.error(f"Audio file is empty: {file_path}")
            return False
        
        # Check file extension
        valid_extensions = ['.wav', '.mp3', '.m4a', '.ogg', '.flac']
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in valid_extensions:
            logger.error(f"Invalid audio file extension: {file_extension}")
            return False
        
        return True


# Global speech-to-text service instance
speech_to_text_service = SpeechToTextService()
