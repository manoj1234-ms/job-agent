import os
import json
import re
import pdfplumber
from typing import Dict, List, Any

class ResumeParser:
    def __init__(self, config):
        self.resume_path = config.get('user', {}).get('resume_path', 'resume.pdf')
        self.output_path = config.get('user', {}).get('resume_text_path', 'resume_text.txt')
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""
        return text
    
    def extract_skills(self, text: str) -> List[str]:
        skill_keywords = [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
            'Data Analysis', 'Data Science', 'Pandas', 'NumPy', 'Scikit-learn',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask',
            'NLP', 'Computer Vision', 'Tableau', 'PowerBI', 'Excel',
            'Statistics', 'Linear Algebra', 'Probability'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
                
        return found_skills
        
    def extract_experience(self, text: str) -> List[Dict[str, str]]:
        experiences = []
        
        exp_patterns = [
            r'(?:Experience|Work Experience)[:\n](.*?)(?:Education|Skills|$)',
            r'(\d+\+?\s*years?.*?(?:experience|Work).*?)(?:\n\n|Education|Skills|$)',
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if len(match) > 20:
                    experiences.append({
                        'description': match.strip()[:500]
                    })
                    break
                    
        return experiences
        
    def extract_projects(self, text: str) -> List[Dict[str, str]]:
        projects = []
        
        project_pattern = r'(?:Projects?|Project)[:\n](.*?)(?:Experience|Education|Skills|$)'
        matches = re.findall(project_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            lines = [l.strip() for l in match.split('\n') if l.strip()]
            for line in lines[:3]:
                if len(line) > 10:
                    projects.append({'name': line[:50], 'description': line})
                    
        return projects
        
    def parse(self) -> Dict[str, Any]:
        if not os.path.exists(self.resume_path):
            print(f"Resume not found at {self.resume_path}")
            return {}
            
        text = self.extract_text_from_pdf(self.resume_path)
        
        if not text:
            print("Could not extract text from resume")
            return {}
            
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(text)
            
        parsed = {
            'full_text': text,
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'projects': self.extract_projects(text),
            'word_count': len(text.split())
        }
        
        return parsed
        
    def get_resume_text(self) -> str:
        if os.path.exists(self.output_path):
            with open(self.output_path, 'r', encoding='utf-8') as f:
                return f.read()
        return self.extract_text_from_pdf(self.resume_path)
