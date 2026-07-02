import google.generativeai as genai
from config import Config
import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API."""
    
    def __init__(self):
        """Initialize Gemini service."""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # Use the correct model name from the available models
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        logger.info("Gemini service initialized successfully with model: models/gemini-2.5-flash")
    
    def generate_content(self, prompt: str) -> str:
        """
        Generate content using Gemini API.
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            Generated text response
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {str(e)}")
            raise
    
    def generate_json_response(self, prompt: str) -> Dict[str, Any]:
        """
        Generate JSON response using Gemini API.
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            Parsed JSON response
        """
        try:
            response_text = self.generate_content(prompt)
            
            # Extract JSON from response (handle markdown code blocks)
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response from Gemini: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating JSON response: {str(e)}")
            raise
    
    def analyze_resume(self, resume_text: str, prompt_template: str) -> Dict[str, Any]:
        """
        Analyze resume using Gemini.
        
        Args:
            resume_text: Extracted resume text
            prompt_template: Prompt template for resume analysis
            
        Returns:
            Structured resume analysis
        """
        try:
            prompt = prompt_template.format(resume_text=resume_text)
            return self.generate_json_response(prompt)
        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            raise
    
    def generate_questions(self, candidate_info: Dict[str, Any], prompt_template: str) -> Dict[str, Any]:
        """
        Generate interview questions using Gemini.
        
        Args:
            candidate_info: Candidate information
            prompt_template: Prompt template for question generation
            
        Returns:
            Generated questions
        """
        try:
            # Calculate question distribution
            total_questions = Config.QUESTIONS_PER_INTERVIEW
            technical_count = int(total_questions * Config.TECHNICAL_QUESTIONS_PERCENT / 100)
            project_count = int(total_questions * Config.PROJECT_QUESTIONS_PERCENT / 100)
            problem_solving_count = int(total_questions * Config.PROBLEM_SOLVING_PERCENT / 100)
            system_design_count = int(total_questions * Config.SYSTEM_DESIGN_PERCENT / 100)
            behavioral_count = total_questions - (technical_count + project_count + problem_solving_count + system_design_count)
            
            prompt = prompt_template.format(
                name=candidate_info.get('name', ''),
                experience_years=candidate_info.get('experience_years', 0),
                skills=', '.join(candidate_info.get('skills', [])),
                projects=json.dumps(candidate_info.get('projects', [])),
                total_questions=total_questions,
                technical_count=technical_count,
                technical_percent=Config.TECHNICAL_QUESTIONS_PERCENT,
                project_count=project_count,
                project_percent=Config.PROJECT_QUESTIONS_PERCENT,
                problem_solving_count=problem_solving_count,
                problem_solving_percent=Config.PROBLEM_SOLVING_PERCENT,
                system_design_count=system_design_count,
                system_design_percent=Config.SYSTEM_DESIGN_PERCENT,
                behavioral_count=behavioral_count,
                behavioral_percent=Config.BEHAVIORAL_PERCENT
            )
            
            return self.generate_json_response(prompt)
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            raise
    
    def evaluate_answer(
        self,
        question: str,
        answer: str,
        question_type: str,
        difficulty: str,
        candidate_info: Dict[str, Any],
        prompt_template: str
    ) -> Dict[str, Any]:
        """
        Evaluate candidate answer using Gemini.
        
        Args:
            question: The question asked
            answer: Candidate's answer
            question_type: Type of question
            difficulty: Question difficulty
            candidate_info: Candidate information
            prompt_template: Prompt template for answer evaluation
            
        Returns:
            Answer evaluation scores and feedback
        """
        try:
            prompt = prompt_template.format(
                question=question,
                question_type=question_type,
                difficulty=difficulty,
                answer=answer,
                skills=', '.join(candidate_info.get('skills', [])),
                experience_years=candidate_info.get('experience_years', 0)
            )
            
            return self.generate_json_response(prompt)
        except Exception as e:
            logger.error(f"Error evaluating answer: {str(e)}")
            raise
    
    def generate_followup(
        self,
        original_question: str,
        answer: str,
        evaluation: Dict[str, Any],
        candidate_info: Dict[str, Any],
        prompt_template: str
    ) -> Dict[str, Any]:
        """
        Generate follow-up questions using Gemini.
        
        Args:
            original_question: Original question asked
            answer: Candidate's answer
            evaluation: Answer evaluation
            candidate_info: Candidate information
            prompt_template: Prompt template for follow-up generation
            
        Returns:
            Follow-up questions
        """
        try:
            prompt = prompt_template.format(
                original_question=original_question,
                answer=answer,
                technical_score=evaluation.get('technical_score', 0),
                depth_score=evaluation.get('depth_score', 0),
                feedback=evaluation.get('feedback', ''),
                skills=', '.join(candidate_info.get('skills', [])),
                experience_years=candidate_info.get('experience_years', 0)
            )
            
            return self.generate_json_response(prompt)
        except Exception as e:
            logger.error(f"Error generating follow-up: {str(e)}")
            raise
    
    def generate_hiring_recommendation(
        self,
        candidate_info: Dict[str, Any],
        performance_metrics: Dict[str, Any],
        prompt_template: str
    ) -> Dict[str, Any]:
        """
        Generate hiring recommendation using Gemini.
        
        Args:
            candidate_info: Candidate information
            performance_metrics: Interview performance metrics
            prompt_template: Prompt template for hiring decision
            
        Returns:
            Hiring recommendation
        """
        try:
            prompt = prompt_template.format(
                name=candidate_info.get('name', ''),
                experience_years=candidate_info.get('experience_years', 0),
                skills=', '.join(candidate_info.get('skills', [])),
                overall_score=performance_metrics.get('overall_score', 0),
                technical_score=performance_metrics.get('technical_score', 0),
                communication_score=performance_metrics.get('communication_score', 0),
                problem_solving_score=performance_metrics.get('problem_solving_score', 0),
                confidence_score=performance_metrics.get('confidence_score', 0),
                depth_score=performance_metrics.get('depth_score', 0),
                total_questions=performance_metrics.get('total_questions', 0),
                avg_answer_score=performance_metrics.get('avg_answer_score', 0)
            )
            
            return self.generate_json_response(prompt)
        except Exception as e:
            logger.error(f"Error generating hiring recommendation: {str(e)}")
            raise
    
    def generate_report_summary(
        self,
        candidate_info: Dict[str, Any],
        session_info: Dict[str, Any],
        performance_metrics: Dict[str, Any],
        qa_summary: str,
        prompt_template: str
    ) -> Dict[str, Any]:
        """
        Generate report summary using Gemini.
        
        Args:
            candidate_info: Candidate information
            session_info: Interview session information
            performance_metrics: Performance metrics
            qa_summary: Questions and answers summary
            prompt_template: Prompt template for report generation
            
        Returns:
            Report summary
        """
        try:
            prompt = prompt_template.format(
                candidate_info=json.dumps(candidate_info, indent=2),
                session_info=json.dumps(session_info, indent=2),
                performance_metrics=json.dumps(performance_metrics, indent=2),
                qa_summary=qa_summary
            )
            
            return self.generate_json_response(prompt)
        except Exception as e:
            logger.error(f"Error generating report summary: {str(e)}")
            raise


# Global Gemini service instance
gemini_service = GeminiService()
