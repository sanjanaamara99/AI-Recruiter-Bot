import logging
from typing import Dict, List, Any
from services.gemini_service import gemini_service
from services.vector_store import vector_store

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Service for generating interview questions."""
    
    def __init__(self):
        """Initialize question generator."""
        self.gemini = gemini_service
        self.vector_store = vector_store
    
    def load_prompt_template(self, prompt_file: str) -> str:
        """Load prompt template from file."""
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt template: {str(e)}")
            raise
    
    def generate_interview_questions(
        self,
        session_id: int,
        candidate_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized interview questions.
        
        Args:
            session_id: Interview session ID
            candidate_info: Candidate information from resume analysis
            
        Returns:
            List of generated questions
        """
        try:
            prompt_template = self.load_prompt_template('prompts/question_generation.txt')
            
            result = self.gemini.generate_questions(candidate_info, prompt_template)
            questions = result.get('questions', [])
            
            # Filter out duplicate questions using vector store
            unique_questions = []
            for question in questions:
                question_text = question.get('question_text', '')
                
                # Check if similar question already exists
                is_duplicate = self.vector_store.check_duplicate_question(
                    session_id,
                    question_text,
                    threshold=0.85
                )
                
                if not is_duplicate:
                    unique_questions.append(question)
                else:
                    logger.info(f"Skipping duplicate question: {question_text[:50]}...")
            
            logger.info(f"Generated {len(unique_questions)} unique questions for session {session_id}")
            return unique_questions
        except Exception as e:
            logger.error(f"Error generating interview questions: {str(e)}")
            raise


# Global question generator instance
question_generator = QuestionGenerator()
