import logging
import json
from typing import Dict, Any
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from database.db import get_db_session
from database.models import InterviewSession, Candidate, Question, Answer, Report
from services.gemini_service import gemini_service
from services.scoring_engine import scoring_engine
from config import Config
import os

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Service for generating interview reports."""
    
    def __init__(self):
        """Initialize report generator."""
        self.gemini = gemini_service
        self.scoring_engine = scoring_engine
    
    def load_prompt_template(self, prompt_file: str) -> str:
        """Load prompt template from file."""
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt template: {str(e)}")
            raise
    
    def generate_report(self, session_id: int) -> Dict[str, Any]:
        """
        Generate comprehensive interview report.
        
        Args:
            session_id: Interview session ID
            
        Returns:
            Report data and file paths
        """
        db = get_db_session()
        
        try:
            # Get session data
            session = db.query(InterviewSession).filter_by(id=session_id).first()
            if not session:
                raise ValueError(f"Interview session not found: {session_id}")
            
            candidate = db.query(Candidate).filter_by(id=session.candidate_id).first()
            questions = db.query(Question).filter_by(session_id=session_id).all()
            answers = db.query(Answer).join(Question).filter(
                Question.session_id == session_id
            ).all()
            
            # Calculate scores
            scores = self.scoring_engine.calculate_session_scores(answers)
            recommendation = self.scoring_engine.determine_recommendation(scores['overall_score'])
            
            # Update session with scores
            session.overall_score = scores['overall_score']
            session.recommendation = recommendation
            
            # Prepare data for report
            candidate_info = {
                'name': candidate.name,
                'email': candidate.email,
                'phone': candidate.phone,
                'experience_years': candidate.experience_years
            }
            
            session_info = {
                'session_id': session.id,
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'ended_at': session.ended_at.isoformat() if session.ended_at else None,
                'status': session.status.value if session.status else None
            }
            
            performance_metrics = scores
            performance_metrics['recommendation'] = recommendation.value
            
            # Prepare Q&A summary
            qa_summary = self._prepare_qa_summary(questions, answers)
            
            # Generate AI summary using Gemini
            logger.info("Generating AI summary for report")
            prompt_template = self.load_prompt_template('prompts/report_generation.txt')
            ai_summary = self.gemini.generate_report_summary(
                candidate_info=candidate_info,
                session_info=session_info,
                performance_metrics=performance_metrics,
                qa_summary=qa_summary,
                prompt_template=prompt_template
            )
            
            # Generate hiring recommendation
            logger.info("Generating hiring recommendation")
            hiring_prompt = self.load_prompt_template('prompts/hiring_decision.txt')
            hiring_recommendation = self.gemini.generate_hiring_recommendation(
                candidate_info=candidate_info,
                performance_metrics=performance_metrics,
                prompt_template=hiring_prompt
            )
            
            # Compile full report
            report_data = {
                'candidate': candidate_info,
                'session': session_info,
                'performance_metrics': performance_metrics,
                'question_distribution': self.scoring_engine.calculate_question_type_distribution(questions),
                'difficulty_distribution': self.scoring_engine.calculate_difficulty_distribution(questions),
                'performance_summary': self.scoring_engine.get_performance_summary(scores),
                'ai_summary': ai_summary,
                'hiring_recommendation': hiring_recommendation,
                'questions_and_answers': qa_summary,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Generate PDF report
            pdf_path = self._generate_pdf_report(session_id, report_data)
            
            # Save report to database
            report = Report(
                session_id=session_id,
                report_json=report_data,
                pdf_path=pdf_path
            )
            db.add(report)
            db.commit()
            
            logger.info(f"Report generated successfully for session {session_id}")
            
            return {
                'report_id': report.id,
                'report_data': report_data,
                'pdf_path': pdf_path
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error generating report: {str(e)}")
            raise
        finally:
            db.close()
    
    def _prepare_qa_summary(self, questions: list, answers: list) -> str:
        """Prepare Q&A summary text."""
        qa_list = []
        
        # Create a mapping of question_id to answer
        answer_map = {a.question_id: a for a in answers}
        
        for question in questions:
            answer = answer_map.get(question.id)
            
            qa_item = f"Q: {question.question_text}\n"
            qa_item += f"Type: {question.question_type.value}, Difficulty: {question.difficulty.value}\n"
            
            if answer:
                qa_item += f"A: {answer.transcript[:200]}...\n"
                qa_item += f"Scores: Tech={answer.technical_score}, Comm={answer.communication_score}, "
                qa_item += f"PS={answer.problem_solving_score}, Conf={answer.confidence_score}, Depth={answer.depth_score}\n"
            else:
                qa_item += "A: Not answered\n"
            
            qa_list.append(qa_item)
        
        return "\n\n".join(qa_list)
    
    def _generate_pdf_report(self, session_id: int, report_data: Dict[str, Any]) -> str:
        """Generate PDF report."""
        try:
            # Create PDF file path
            pdf_filename = f"interview_report_{session_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(Config.REPORT_FOLDER, pdf_filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Title
            story.append(Paragraph("AI Interview Report", title_style))
            story.append(Spacer(1, 0.2 * inch))
            
            # Candidate Information
            story.append(Paragraph("Candidate Information", heading_style))
            candidate = report_data['candidate']
            candidate_data = [
                ['Name:', candidate['name']],
                ['Email:', candidate['email']],
                ['Phone:', candidate.get('phone', 'N/A')],
                ['Experience:', f"{candidate['experience_years']} years"]
            ]
            candidate_table = Table(candidate_data, colWidths=[2*inch, 4*inch])
            candidate_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(candidate_table)
            story.append(Spacer(1, 0.3 * inch))
            
            # Performance Metrics
            story.append(Paragraph("Performance Metrics", heading_style))
            metrics = report_data['performance_metrics']
            metrics_data = [
                ['Metric', 'Score'],
                ['Technical Score', f"{metrics['technical_score']}/100"],
                ['Communication Score', f"{metrics['communication_score']}/100"],
                ['Problem Solving Score', f"{metrics['problem_solving_score']}/100"],
                ['Confidence Score', f"{metrics['confidence_score']}/100"],
                ['Knowledge Depth Score', f"{metrics['depth_score']}/100"],
                ['Overall Score', f"{metrics['overall_score']}/100"]
            ]
            metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(metrics_table)
            story.append(Spacer(1, 0.3 * inch))
            
            # Hiring Recommendation
            story.append(Paragraph("Hiring Recommendation", heading_style))
            recommendation = report_data['hiring_recommendation']
            rec_text = f"<b>Decision:</b> {recommendation['recommendation'].upper()}<br/>"
            rec_text += f"<b>Confidence:</b> {recommendation.get('confidence', 'N/A').upper()}<br/><br/>"
            rec_text += f"<b>Summary:</b> {recommendation.get('summary', 'N/A')}"
            story.append(Paragraph(rec_text, styles['Normal']))
            story.append(Spacer(1, 0.3 * inch))
            
            # Strengths
            if recommendation.get('strengths'):
                story.append(Paragraph("<b>Key Strengths:</b>", styles['Normal']))
                for strength in recommendation['strengths'][:5]:
                    story.append(Paragraph(f"• {strength}", styles['Normal']))
                story.append(Spacer(1, 0.2 * inch))
            
            # Weaknesses
            if recommendation.get('weaknesses'):
                story.append(Paragraph("<b>Areas for Improvement:</b>", styles['Normal']))
                for weakness in recommendation['weaknesses'][:5]:
                    story.append(Paragraph(f"• {weakness}", styles['Normal']))
                story.append(Spacer(1, 0.3 * inch))
            
            # Executive Summary
            story.append(PageBreak())
            story.append(Paragraph("Executive Summary", heading_style))
            ai_summary = report_data['ai_summary']
            story.append(Paragraph(ai_summary.get('executive_summary', 'N/A'), styles['Normal']))
            story.append(Spacer(1, 0.3 * inch))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report generated: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise


# Global report generator instance
report_generator = ReportGenerator()
