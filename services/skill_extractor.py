import logging
from typing import Dict, List, Any
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class SkillExtractor:
    """Service for extracting and classifying skills."""
    
    def __init__(self):
        """Initialize skill extractor."""
        self.gemini = gemini_service
    
    def load_prompt_template(self, prompt_file: str) -> str:
        """Load prompt template from file."""
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt template: {str(e)}")
            raise
    
    def classify_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Classify skills into categories.
        
        Args:
            skills: List of skills to classify
            
        Returns:
            Dictionary of categorized skills
        """
        try:
            prompt_template = self.load_prompt_template('prompts/skill_extraction.txt')
            prompt = prompt_template.format(skills=', '.join(skills))
            
            classification = self.gemini.generate_json_response(prompt)
            
            logger.info(f"Successfully classified {len(skills)} skills")
            return classification
        except Exception as e:
            logger.error(f"Error classifying skills: {str(e)}")
            # Return default classification on error
            return {
                "Programming Languages": [],
                "Frameworks": [],
                "Databases": [],
                "Cloud": [],
                "DevOps": [],
                "AI/ML": [],
                "Other": skills
            }
    
    def extract_skills_from_resume(self, resume_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract and classify skills from resume analysis.
        
        Args:
            resume_analysis: Resume analysis from Gemini
            
        Returns:
            List of skills with categories
        """
        try:
            # Collect all skills from different fields
            all_skills = []
            all_skills.extend(resume_analysis.get('skills', []))
            all_skills.extend(resume_analysis.get('frameworks', []))
            all_skills.extend(resume_analysis.get('databases', []))
            all_skills.extend(resume_analysis.get('cloud', []))
            all_skills.extend(resume_analysis.get('tools', []))
            
            # Remove duplicates
            all_skills = list(set(all_skills))
            
            if not all_skills:
                logger.warning("No skills found in resume analysis")
                return []
            
            # Classify skills
            classification = self.classify_skills(all_skills)
            
            # Convert to list format with categories
            skills_with_categories = []
            for category, skills in classification.items():
                for skill in skills:
                    skills_with_categories.append({
                        'skill_name': skill,
                        'category': category
                    })
            
            logger.info(f"Extracted {len(skills_with_categories)} skills with categories")
            return skills_with_categories
        except Exception as e:
            logger.error(f"Error extracting skills from resume: {str(e)}")
            raise


# Global skill extractor instance
skill_extractor = SkillExtractor()
