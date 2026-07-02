import logging
from typing import Dict, List, Any
from services.gemini_service import gemini_service
from services.vector_store import vector_store

logger = logging.getLogger(__name__)


class FollowupGenerator:
    """Service for generating follow-up questions."""
    
    def __init__(self):
        """Initialize follow-up generator."""
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
    
    def generate_followup_questions(
        self,
        session_id: int,
        original_question: str,
        answer: str,
        evaluation: Dict[str, Any],
        candidate_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate intelligent follow-up questions.
        
        Args:
            session_id: Interview session ID
            original_question: Original question asked
            answer: Candidate's answer
            evaluation: Answer evaluation
            candidate_info: Candidate information
            
        Returns:
            List of follow-up questions
        """
        try:
            prompt_template = self.load_prompt_template('prompts/followup_generation.txt')
            
            result = self.gemini.generate_followup(
                original_question=original_question,
                answer=answer,
                evaluation=evaluation,
                candidate_info=candidate_info,
                prompt_template=prompt_template
            )
            
            followup_questions = result.get('follow_up_questions', [])
            
            # Filter out duplicate questions
            unique_followups = []
            for followup in followup_questions:
                question_text = followup.get('question_text', '')
                
                # Check if similar question already exists
                is_duplicate = self.vector_store.check_duplicate_question(
                    session_id,
                    question_text,
                    threshold=0.85
                )
                
                if not is_duplicate:
                    unique_followups.append(followup)
                else:
                    logger.info(f"Skipping duplicate follow-up: {question_text[:50]}...")
            
            logger.info(f"Generated {len(unique_followups)} unique follow-up questions")
            return unique_followups
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {str(e)}")
            return []
    
    def should_generate_followup(self, evaluation: Dict[str, Any]) -> bool:
        """
        Determine if follow-up questions should be generated.
        
        Args:
            evaluation: Answer evaluation
            
        Returns:
            True if follow-up should be generated, False otherwise
        """
        # Generate follow-up if answer shows partial understanding
        # or if there's room for deeper exploration
        avg_score = (
            evaluation.get('technical_score', 0) +
            evaluation.get('depth_score', 0)
        ) / 2
        
        # Generate follow-up for medium-scoring answers (4-8 out of 10)
        return 4 <= avg_score <= 8


# Global follow-up generator instance
followup_generator = FollowupGenerator()
