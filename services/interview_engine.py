import logging
from typing import Dict, Any, Optional
from datetime import datetime
from database.db import get_db_session
from database.models import (
    Candidate, Resume, Skill, InterviewSession, Question, Answer,
    InterviewStatus, QuestionType, DifficultyLevel
)
from services.resume_parser import resume_parser
from services.gemini_service import gemini_service
from services.skill_extractor import skill_extractor
from services.question_generator import question_generator
from services.answer_evaluator import answer_evaluator
from services.followup_generator import followup_generator
from services.vector_store import vector_store
from services.scoring_engine import scoring_engine

logger = logging.getLogger(__name__)


class InterviewEngine:
    """Main service for orchestrating the interview process."""
    
    def __init__(self):
        """Initialize interview engine."""
        self.resume_parser = resume_parser
        self.gemini = gemini_service
        self.skill_extractor = skill_extractor
        self.question_generator = question_generator
        self.answer_evaluator = answer_evaluator
        self.followup_generator = followup_generator
        self.vector_store = vector_store
        self.scoring_engine = scoring_engine
    
    def load_prompt_template(self, prompt_file: str) -> str:
        """Load prompt template from file."""
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt template: {str(e)}")
            raise
    
    def process_resume(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """
        Process uploaded resume.
        
        Args:
            file_path: Path to resume file
            file_name: Original file name
            
        Returns:
            Dictionary containing candidate and resume information
        """
        db = get_db_session()
        
        try:
            # Parse resume
            logger.info(f"Parsing resume: {file_name}")
            resume_text = self.resume_parser.parse_resume(file_path)
            
            if not self.resume_parser.validate_resume_text(resume_text):
                raise ValueError("Resume text is invalid or too short")
            
            # Analyze resume with Gemini
            logger.info("Analyzing resume with Gemini")
            prompt_template = self.load_prompt_template('prompts/resume_analysis.txt')
            resume_analysis = self.gemini.analyze_resume(resume_text, prompt_template)
            
            # Create or get candidate
            candidate = db.query(Candidate).filter_by(
                email=resume_analysis.get('email', f"candidate_{datetime.utcnow().timestamp()}@example.com")
            ).first()
            
            if not candidate:
                candidate = Candidate(
                    name=resume_analysis.get('name', 'Unknown'),
                    email=resume_analysis.get('email', f"candidate_{datetime.utcnow().timestamp()}@example.com"),
                    phone=resume_analysis.get('phone', ''),
                    experience_years=resume_analysis.get('experience_years', 0)
                )
                db.add(candidate)
                db.flush()
            
            # Create resume record
            resume = Resume(
                candidate_id=candidate.id,
                file_name=file_name,
                file_path=file_path,
                raw_text=resume_text
            )
            db.add(resume)
            db.flush()
            
            # Extract and classify skills
            logger.info("Extracting and classifying skills")
            skills_with_categories = self.skill_extractor.extract_skills_from_resume(resume_analysis)
            
            # Save skills
            for skill_data in skills_with_categories:
                skill = Skill(
                    candidate_id=candidate.id,
                    skill_name=skill_data['skill_name'],
                    category=skill_data['category']
                )
                db.add(skill)
            
            db.commit()
            
            logger.info(f"Resume processed successfully for candidate: {candidate.name}")
            
            return {
                'candidate': candidate.to_dict(),
                'resume': resume.to_dict(),
                'analysis': resume_analysis,
                'skills': skills_with_categories
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing resume: {str(e)}")
            raise
        finally:
            db.close()
    
    def start_interview(self, candidate_id: int) -> Dict[str, Any]:
        """
        Start a new interview session.
        
        Args:
            candidate_id: Candidate ID
            
        Returns:
            Interview session information
        """
        db = get_db_session()
        
        try:
            # Get candidate with skills
            candidate = db.query(Candidate).filter_by(id=candidate_id).first()
            if not candidate:
                raise ValueError(f"Candidate not found: {candidate_id}")
            
            # Get resume
            resume = db.query(Resume).filter_by(candidate_id=candidate_id).order_by(
                Resume.uploaded_at.desc()
            ).first()
            
            if not resume:
                raise ValueError(f"No resume found for candidate: {candidate_id}")
            
            # Create interview session
            session = InterviewSession(
                candidate_id=candidate_id,
                status=InterviewStatus.IN_PROGRESS,
                started_at=datetime.utcnow()
            )
            db.add(session)
            db.flush()
            
            # Get candidate info for question generation
            skills = db.query(Skill).filter_by(candidate_id=candidate_id).all()
            
            candidate_info = {
                'name': candidate.name,
                'experience_years': candidate.experience_years,
                'skills': [s.skill_name for s in skills],
                'projects': []  # Would be extracted from resume analysis
            }
            
            # Add resume context to vector store
            logger.info(f"Adding resume context to vector store for session {session.id}")
            self.vector_store.add_resume_context(session.id, resume.raw_text, candidate_info)
            
            # Generate interview questions
            logger.info(f"Generating interview questions for session {session.id}")
            questions = self.question_generator.generate_interview_questions(
                session.id,
                candidate_info
            )
            
            # Save questions to database
            for q_data in questions:
                question = Question(
                    session_id=session.id,
                    question_text=q_data.get('question_text', ''),
                    question_type=QuestionType(q_data.get('question_type', 'technical')),
                    difficulty=DifficultyLevel(q_data.get('difficulty', 'medium'))
                )
                db.add(question)
                db.flush()
                
                # Add question to vector store
                self.vector_store.add_question(
                    session.id,
                    question.id,
                    question.question_text,
                    question.question_type.value
                )
            
            db.commit()
            
            logger.info(f"Interview session {session.id} started successfully")
            
            return {
                'session': session.to_dict(),
                'candidate': candidate.to_dict(),
                'total_questions': len(questions)
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error starting interview: {str(e)}")
            raise
        finally:
            db.close()
    
    def get_next_question(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the next unanswered question.
        
        Args:
            session_id: Interview session ID
            
        Returns:
            Next question or None if interview is complete
        """
        db = get_db_session()
        
        try:
            # Get next unanswered question
            question = db.query(Question).filter_by(session_id=session_id).outerjoin(
                Answer
            ).filter(Answer.id == None).order_by(Question.id).first()
            
            if question:
                return question.to_dict()
            
            return None
        except Exception as e:
            logger.error(f"Error getting next question: {str(e)}")
            raise
        finally:
            db.close()
    
    def submit_answer(
        self,
        question_id: int,
        transcript: str,
        audio_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit and evaluate an answer.
        
        Args:
            question_id: Question ID
            transcript: Answer transcript
            audio_file: Path to audio file (optional)
            
        Returns:
            Answer evaluation and follow-up questions
        """
        db = get_db_session()
        
        try:
            # Get question and session
            question = db.query(Question).filter_by(id=question_id).first()
            if not question:
                raise ValueError(f"Question not found: {question_id}")
            
            session = db.query(InterviewSession).filter_by(id=question.session_id).first()
            candidate = db.query(Candidate).filter_by(id=session.candidate_id).first()
            
            # Get candidate skills
            skills = db.query(Skill).filter_by(candidate_id=candidate.id).all()
            candidate_info = {
                'name': candidate.name,
                'experience_years': candidate.experience_years,
                'skills': [s.skill_name for s in skills]
            }
            
            # Evaluate answer
            logger.info(f"Evaluating answer for question {question_id}")
            evaluation = self.answer_evaluator.evaluate_answer(
                question=question.question_text,
                answer=transcript,
                question_type=question.question_type.value,
                difficulty=question.difficulty.value,
                candidate_info=candidate_info
            )
            
            # Save answer
            answer = Answer(
                question_id=question_id,
                transcript=transcript,
                audio_file=audio_file,
                technical_score=evaluation.get('technical_score', 0),
                communication_score=evaluation.get('communication_score', 0),
                problem_solving_score=evaluation.get('problem_solving_score', 0),
                confidence_score=evaluation.get('confidence_score', 0),
                depth_score=evaluation.get('depth_score', 0),
                feedback=evaluation.get('feedback', ''),
                strengths=evaluation.get('strengths', []),
                weaknesses=evaluation.get('weaknesses', [])
            )
            db.add(answer)
            db.flush()
            
            # Add answer to vector store
            self.vector_store.add_answer(
                question.session_id,
                question_id,
                transcript,
                evaluation
            )
            
            # Generate follow-up questions if appropriate
            followup_questions = []
            if False:
                logger.info(f"Generating follow-up questions for question {question_id}")
                followups = self.followup_generator.generate_followup_questions(
                    session_id=question.session_id,
                    original_question=question.question_text,
                    answer=transcript,
                    evaluation=evaluation,
                    candidate_info=candidate_info
                )
                
                # Save follow-up questions
                for followup in followups:
                    followup_q = Question(
                        session_id=question.session_id,
                        question_text=followup.get('question_text', ''),
                        question_type=QuestionType.FOLLOW_UP,
                        difficulty=DifficultyLevel(followup.get('difficulty', 'medium'))
                    )
                    db.add(followup_q)
                    db.flush()
                    
                    # Add to vector store
                    self.vector_store.add_question(
                        question.session_id,
                        followup_q.id,
                        followup_q.question_text,
                        followup_q.question_type.value
                    )
                    
                    followup_questions.append(followup_q.to_dict())
            
            db.commit()
            
            logger.info(f"Answer submitted and evaluated successfully")
            
            return {
                'answer': answer.to_dict(),
                'evaluation': evaluation,
                'followup_questions': followup_questions
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error submitting answer: {str(e)}")
            raise
        finally:
            db.close()


# Global interview engine instance
interview_engine = InterviewEngine()
