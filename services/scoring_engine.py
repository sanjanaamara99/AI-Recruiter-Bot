import logging
from typing import Dict, List, Any
from database.models import Answer, Question, InterviewSession, Recommendation
from config import Config

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Service for calculating interview scores and recommendations."""
    
    @staticmethod
    def calculate_session_scores(answers: List[Answer]) -> Dict[str, float]:
        """
        Calculate overall session scores from all answers.
        
        Args:
            answers: List of Answer objects
            
        Returns:
            Dictionary of calculated scores
        """
        if not answers:
            return {
                'technical_score': 0,
                'communication_score': 0,
                'problem_solving_score': 0,
                'confidence_score': 0,
                'depth_score': 0,
                'overall_score': 0,
                'avg_answer_score': 0
            }
        
        # Calculate average scores
        technical_scores = [a.technical_score for a in answers if a.technical_score is not None]
        communication_scores = [a.communication_score for a in answers if a.communication_score is not None]
        problem_solving_scores = [a.problem_solving_score for a in answers if a.problem_solving_score is not None]
        confidence_scores = [a.confidence_score for a in answers if a.confidence_score is not None]
        depth_scores = [a.depth_score for a in answers if a.depth_score is not None]
        
        technical_avg = sum(technical_scores) / len(technical_scores) if technical_scores else 0
        communication_avg = sum(communication_scores) / len(communication_scores) if communication_scores else 0
        problem_solving_avg = sum(problem_solving_scores) / len(problem_solving_scores) if problem_solving_scores else 0
        confidence_avg = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        depth_avg = sum(depth_scores) / len(depth_scores) if depth_scores else 0
        
        # Calculate overall score (weighted average, normalized to 100)
        overall_score = (
            technical_avg * 0.30 +
            communication_avg * 0.20 +
            problem_solving_avg * 0.25 +
            confidence_avg * 0.10 +
            depth_avg * 0.15
        ) * 10  # Convert from 0-10 scale to 0-100 scale
        
        # Calculate average answer score
        all_scores = technical_scores + communication_scores + problem_solving_scores + confidence_scores + depth_scores
        avg_answer_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        return {
            'technical_score': round(technical_avg * 10, 2),
            'communication_score': round(communication_avg * 10, 2),
            'problem_solving_score': round(problem_solving_avg * 10, 2),
            'confidence_score': round(confidence_avg * 10, 2),
            'depth_score': round(depth_avg * 10, 2),
            'overall_score': round(overall_score, 2),
            'avg_answer_score': round(avg_answer_score, 2)
        }
    
    @staticmethod
    def determine_recommendation(overall_score: float) -> Recommendation:
        """
        Determine hiring recommendation based on overall score.
        
        Args:
            overall_score: Overall interview score (0-100)
            
        Returns:
            Recommendation enum value
        """
        if overall_score >= Config.STRONG_HIRE_THRESHOLD:
            return Recommendation.STRONG_HIRE
        elif overall_score >= Config.HIRE_THRESHOLD:
            return Recommendation.HIRE
        elif overall_score >= Config.BORDERLINE_THRESHOLD:
            return Recommendation.BORDERLINE
        else:
            return Recommendation.REJECT
    
    @staticmethod
    def calculate_question_type_distribution(questions: List[Question]) -> Dict[str, int]:
        """
        Calculate distribution of question types.
        
        Args:
            questions: List of Question objects
            
        Returns:
            Dictionary of question type counts
        """
        distribution = {}
        
        for question in questions:
            q_type = question.question_type.value if question.question_type else 'unknown'
            distribution[q_type] = distribution.get(q_type, 0) + 1
        
        return distribution
    
    @staticmethod
    def calculate_difficulty_distribution(questions: List[Question]) -> Dict[str, int]:
        """
        Calculate distribution of question difficulties.
        
        Args:
            questions: List of Question objects
            
        Returns:
            Dictionary of difficulty counts
        """
        distribution = {}
        
        for question in questions:
            difficulty = question.difficulty.value if question.difficulty else 'unknown'
            distribution[difficulty] = distribution.get(difficulty, 0) + 1
        
        return distribution
    
    @staticmethod
    def get_performance_summary(scores: Dict[str, float]) -> Dict[str, str]:
        """
        Get performance summary based on scores.
        
        Args:
            scores: Dictionary of scores
            
        Returns:
            Dictionary of performance summaries
        """
        def get_rating(score: float) -> str:
            if score >= 80:
                return "Excellent"
            elif score >= 60:
                return "Good"
            elif score >= 40:
                return "Average"
            else:
                return "Needs Improvement"
        
        return {
            'technical': get_rating(scores.get('technical_score', 0)),
            'communication': get_rating(scores.get('communication_score', 0)),
            'problem_solving': get_rating(scores.get('problem_solving_score', 0)),
            'confidence': get_rating(scores.get('confidence_score', 0)),
            'depth': get_rating(scores.get('depth_score', 0)),
            'overall': get_rating(scores.get('overall_score', 0))
        }


# Global scoring engine instance
scoring_engine = ScoringEngine()
