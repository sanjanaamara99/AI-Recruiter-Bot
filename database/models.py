from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class InterviewStatus(enum.Enum):
    """Interview session status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class QuestionType(enum.Enum):
    """Question type enumeration."""
    TECHNICAL = "technical"
    PROJECT_BASED = "project_based"
    PROBLEM_SOLVING = "problem_solving"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"
    FOLLOW_UP = "follow_up"


class DifficultyLevel(enum.Enum):
    """Question difficulty level enumeration."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Recommendation(enum.Enum):
    """Hiring recommendation enumeration."""
    STRONG_HIRE = "strong_hire"
    HIRE = "hire"
    BORDERLINE = "borderline"
    REJECT = "reject"


class Candidate(Base):
    """Candidate model."""
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    experience_years = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resumes = relationship('Resume', back_populates='candidate', cascade='all, delete-orphan')
    skills = relationship('Skill', back_populates='candidate', cascade='all, delete-orphan')
    interview_sessions = relationship('InterviewSession', back_populates='candidate', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'experience_years': self.experience_years,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Resume(Base):
    """Resume model."""
    __tablename__ = 'resumes'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    raw_text = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship('Candidate', back_populates='resumes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'file_name': self.file_name,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class Skill(Base):
    """Skill model."""
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    skill_name = Column(String(255), nullable=False)
    category = Column(String(100))
    
    # Relationships
    candidate = relationship('Candidate', back_populates='skills')
    
    def to_dict(self):
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'category': self.category
        }


class InterviewSession(Base):
    """Interview session model."""
    __tablename__ = 'interview_sessions'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.PENDING)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    overall_score = Column(Float)
    recommendation = Column(Enum(Recommendation))
    
    # Relationships
    candidate = relationship('Candidate', back_populates='interview_sessions')
    questions = relationship('Question', back_populates='session', cascade='all, delete-orphan')
    reports = relationship('Report', back_populates='session', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'status': self.status.value if self.status else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'overall_score': self.overall_score,
            'recommendation': self.recommendation.value if self.recommendation else None
        }


class Question(Base):
    """Question model."""
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('interview_sessions.id'), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship('InterviewSession', back_populates='questions')
    answers = relationship('Answer', back_populates='question', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'question_text': self.question_text,
            'question_type': self.question_type.value if self.question_type else None,
            'difficulty': self.difficulty.value if self.difficulty else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Answer(Base):
    """Answer model."""
    __tablename__ = 'answers'
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    transcript = Column(Text)
    audio_file = Column(String(500))
    technical_score = Column(Float)
    communication_score = Column(Float)
    problem_solving_score = Column(Float)
    confidence_score = Column(Float)
    depth_score = Column(Float)
    feedback = Column(Text)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    question = relationship('Question', back_populates='answers')
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'transcript': self.transcript,
            'technical_score': self.technical_score,
            'communication_score': self.communication_score,
            'problem_solving_score': self.problem_solving_score,
            'confidence_score': self.confidence_score,
            'depth_score': self.depth_score,
            'feedback': self.feedback,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Report(Base):
    """Report model."""
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('interview_sessions.id'), nullable=False)
    report_json = Column(JSON)
    pdf_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship('InterviewSession', back_populates='reports')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'pdf_path': self.pdf_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
