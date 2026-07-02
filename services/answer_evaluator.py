import logging
from typing import Dict, Any
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class AnswerEvaluator:
    """Service for evaluating candidate answers."""
    
    def __init__(self):
        """Initialize answer evaluator."""
        self.gemini = gemini_service
    
    def load_prompt_template(self, prompt_file: str) -> str:
        """Load prompt template from file."""
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt template: {str(e)}")
            raise
    
    def evaluate_answer(
        self,
        question: str,
        answer: str,
        question_type: str,
        difficulty: str,
        candidate_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate candidate's answer.
        
        Args:
            question: The question asked
            answer: Candidate's answer
            question_type: Type of question
            difficulty: Question difficulty
            candidate_info: Candidate information
            
        Returns:
            Evaluation scores and feedback
        """
        try:
            prompt_template = self.load_prompt_template('prompts/answer_evaluation.txt')
            
            evaluation = self.gemini.evaluate_answer(
                question=question,
                answer=answer,
                question_type=question_type,
                difficulty=difficulty,
                candidate_info=candidate_info,
                prompt_template=prompt_template
            )
            
            # Ensure all required fields are present
            required_fields = [
                'technical_score',
                'communication_score',
                'problem_solving_score',
                'confidence_score',
                'depth_score',
                'feedback',
                'strengths',
                'weaknesses'
            ]
            
            for field in required_fields:
                if field not in evaluation:
                    if field in ['strengths', 'weaknesses']:
                        evaluation[field] = []
                    elif field == 'feedback':
                        evaluation[field] = ''
                    else:
                        evaluation[field] = 0
            
            logger.info(f"Answer evaluated successfully")
            return evaluation
        except Exception as e:
            logger.error(f"Error evaluating answer: {str(e)}")
            raise
    
    def calculate_average_score(self, evaluation: Dict[str, Any]) -> float:
        """
        Calculate average score from evaluation.
        
        Args:
            evaluation: Answer evaluation
            
        Returns:
            Average score
        """
        scores = [
            evaluation.get('technical_score', 0),
            evaluation.get('communication_score', 0),
            evaluation.get('problem_solving_score', 0),
            evaluation.get('confidence_score', 0),
            evaluation.get('depth_score', 0)
        ]
        
        return sum(scores) / len(scores) if scores else 0


# Global answer evaluator instance
answer_evaluator = AnswerEvaluator()
