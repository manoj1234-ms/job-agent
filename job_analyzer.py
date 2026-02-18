import re
from typing import Dict, List, Tuple

class JobAnalyzer:
    def __init__(self, config, github_projects, parsed_resume=None):
        self.config = config
        self.github_projects = github_projects or []
        self.resume_data = parsed_resume or {}
        self.resume_skills = self.resume_data.get('skills', [])
        
    def detect_job_type(self, job_description: str, job_title: str = "") -> str:
        """Detect if job is SDE, Data Analyst, or ML Engineer"""
        text = f"{job_title} {job_description}".lower()
        
        ml_keywords = ['machine learning', 'ml engineer', 'deep learning', 'ai engineer', 
                     'artificial intelligence', 'data scientist', 'nlp', 'computer vision',
                     'tensorflow', 'pytorch', 'neural network', 'model training',
                     'mlops', 'ai/ml']
        
        data_analyst_keywords = ['data analyst', 'data analytics', 'business analyst',
                                'bi analyst', 'tableau', 'power bi', 'data visualization',
                                'etl', 'data warehouse', 'sql analyst', 'analytics']
        
        sde_keywords = ['sde', 'software engineer', 'software developer', 'full stack',
                      'backend', 'frontend', 'fullstack', 'web developer', 'api developer',
                      'cloud engineer', 'devops', 'site reliability']
        
        ml_score = sum(1 for kw in ml_keywords if kw in text)
        data_score = sum(1 for kw in data_analyst_keywords if kw in text)
        sde_score = sum(1 for kw in sde_keywords if kw in text)
        
        if ml_score >= data_score and ml_score >= sde_score:
            return "ML Engineer"
        elif data_score >= sde_score:
            return "Data Analyst"
        else:
            return "SDE"
    
    def get_github_projects_for_job(self, job_type: str, job_description: str) -> List[Dict]:
        """Get matching GitHub projects based on job type"""
        text = f"{job_type} {job_description}".lower()
        
        project_keywords = {
            'SDE': ['react', 'next', 'node', 'javascript', 'typescript', 'python', 
                    'flask', 'django', 'express', 'api', 'fullstack', 'web'],
            'Data Analyst': ['python', 'pandas', 'numpy', 'jupyter', 'sql', 'analysis',
                           'analytics', 'visualization', 'tableau', 'bi', 'etl'],
            'ML Engineer': ['python', 'tensorflow', 'pytorch', 'ml', 'ai', 'nlp', 'cv',
                          'machine learning', 'deep learning', 'neural', 'whisper', 'gpt']
        }
        
        keywords = project_keywords.get(job_type, project_keywords['SDE'])
        
        scored_projects = []
        for proj in self.github_projects:
            score = 0
            proj_text = f"{proj.get('name', '')} {proj.get('description', '')} {proj.get('language', '')}".lower()
            
            for kw in keywords:
                if kw in proj_text:
                    score += 2
            
            if proj.get('stars', 0) > 0:
                score += min(proj.get('stars', 0) / 10, 3)
            
            if score > 0:
                scored_projects.append({
                    **proj,
                    'match_score': score
                })
        
        scored_projects.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        return scored_projects[:5]
    
    def calculate_ats_score(self, job_description: str, job_type: str) -> Dict:
        """Calculate FAANG-level ATS score with new formula
        
        Formula:
        ATS = (0.25×RM) + (0.25×WE) + (0.20×PR) + (0.15×PS) + (0.10×ES) + (0.05×KW)
        """
        job_lower = job_description.lower()
        
        # Role Match (RM) - 25%
        rm_score = self._calculate_role_match_score(job_description, job_type)
        
        # Work Experience Impact (WE) - 25%
        we_score = self._calculate_work_experience_score(job_description)
        
        # Project Depth (PR) - 20%
        pr_score = self._calculate_project_depth_score(job_type, job_description)
        
        # Problem Solving (PS) - 15%
        ps_score = self._calculate_problem_solving_score()
        
        # Education Signal (ES) - 10%
        es_score = self._calculate_education_signal_score(job_description)
        
        # Keyword Optimization (KW) - 5%
        kw_score = self._calculate_keyword_optimization_score(job_description)
        
        # Calculate total
        total = (0.25 * rm_score) + (0.25 * we_score) + (0.20 * pr_score) + (0.15 * ps_score) + (0.10 * es_score) + (0.05 * kw_score)
        
        score_breakdown = {
            'role_match': rm_score * 0.25,
            'work_experience': we_score * 0.25,
            'project_depth': pr_score * 0.20,
            'problem_solving': ps_score * 0.15,
            'education': es_score * 0.10,
            'keywords': kw_score * 0.05
        }
        
        matching_projects = self.get_github_projects_for_job(job_type, job_description)
        matched_skills = self._match_skills(self._extract_skills(job_description))
        
        return {
            'total': total,
            'breakdown': score_breakdown,
            'raw_scores': {
                'RM': rm_score,
                'WE': we_score,
                'PR': pr_score,
                'PS': ps_score,
                'ES': es_score,
                'KW': kw_score
            },
            'matched_skills': matched_skills,
            'matching_projects': matching_projects,
            'job_type': job_type,
            'networking_hook': self._generate_networking_hook(job_type, job_description, matching_projects)
        }

    def _generate_networking_hook(self, job_type: str, job_description: str, matching_projects: List[Dict]) -> str:
        """Generate a personalized LinkedIn networking hook"""
        # User details for the hook
        batch = "2027"
        major = "CSE"
        primary_project = "VetNet AI" # Default strong project
        
        if matching_projects:
            # Use the best matching project if available
            primary_project = matching_projects[0].get('name', primary_project)
            
        role_name = "ML Intern" if job_type == 'ML Engineer' else "Data/Software Intern"
        if 'intern' in job_description.lower():
            role_name = "Intern"
            
        hook = f"Hi [Name], I'm a {batch} batch {major} student interested in the {role_name} role. "
        hook += f"I've built {primary_project}, which handles similar tech like "
        
        if job_type == 'ML Engineer':
            hook += "PyTorch and FastAPI telemetry."
        elif job_type == 'Data Analyst':
            hook += "predictive modeling and data pipelines."
        else:
            hook += "REST APIs and system architecture."
            
        hook += " I'd love to connect and learn more about the team's work!"
        return hook
    
    def _calculate_role_match_score(self, job_description: str, job_type: str) -> float:
        """Role Match (RM) - How well the role matches"""
        score = 0
        text = job_description.lower()
        
        # Exact role match
        if job_type.lower() in text:
            score += 50
        
        # Related terms
        if job_type == 'SDE':
            if any(t in text for t in ['software engineer', 'developer', 'sde', 'programming']):
                score += 30
        elif job_type == 'ML Engineer':
            if any(t in text for t in ['machine learning', 'ml engineer', 'ai engineer', 'data scientist', 'computer vision', 'nlp']):
                score += 40 # Increased weight for ML roles
        elif job_type == 'Data Analyst':
            if any(t in text for t in ['data analyst', 'analytics', 'bi analyst', 'business analyst', 'data science']):
                score += 30
        
        # Seniority match (fresher/intern friendly = higher score)
        if any(t in text for t in ['entry', 'fresher', 'junior', 'graduate', 'new grad', 'intern', 'student']):
            score += 20
        
        return min(score, 100)
    
    def _calculate_work_experience_score(self, job_description: str) -> float:
        """Work Experience Impact (WE) - 25%"""
        score = 0
        text = job_description.lower()
        
        # User has specific internship experience: Alfido Tech (Data Analyst), Infotact (Python Developer)
        score += 40  # Solid internship foundation in both Data and Backend
        
        # Quantifiable achievements keywords (User has many: 22% accuracy, 90% reduction, 95.47% accuracy)
        impact_keywords = ['accuracy', 'predictive', 'automated', 'pipeline', 'handling', 'scalability', 'performance']
        matches = sum(1 for kw in impact_keywords if kw in text)
        score += min(matches * 8, 40)
        
        # Freshers/Students often welcomed in these roles
        if any(kw in text for kw in ['intern', 'junior', 'student', 'graduate']):
            score += 20
        
        return min(score, 100)
    
    def _calculate_project_depth_score(self, job_type: str, job_description: str) -> float:
        """Project Depth (PR) - 20%"""
        # We manually boost this because we know the user's projects are extremely deep (VetNet AI, OpenWork Agent)
        matching_projects = self.get_github_projects_for_job(job_type, job_description)
        
        score = 40 # Base for high quality projects
        
        if matching_projects:
            score += min(len(matching_projects) * 15, 60)
            
        # Specific mentions of complex ML tasks
        if job_type == 'ML Engineer' and any(kw in job_description.lower() for kw in ['pytorch', 'fastapi', 'iot', 'hybrid']):
            score += 20 # Bonus for VetNet style alignment
            
        return min(score, 100)
    
    def _calculate_problem_solving_score(self) -> float:
        """Problem Solving (PS) - 15%"""
        score = 0
        
        # LeetCode (user has 1000+ problems)
        score += 60  # Extremely high for a student
        
        # Achievements (Amazon ML Challenge, LeetCode rank)
        score += 30
        
        # Certifications (Oracle, IBM)
        score += 10
        
        return min(score, 100)
    
    def _calculate_education_signal_score(self, job_description: str) -> float:
        """Education Signal (ES) - 10%"""
        score = 0
        text = job_description.lower()
        
        # B.Tech CSE (2027)
        score += 50
        
        # CGPA 7.8
        score += 20
        
        # Relevant keywords
        if 'computer science' in text or 'engineering' in text:
            score += 30
        
        return min(score, 100)
    
    def _calculate_keyword_optimization_score(self, job_description: str) -> float:
        """Keyword Optimization (KW) - 5%"""
        score = 0
        text = job_description.lower()
        
        # AI/ML specific keywords the user actually has
        ml_keywords = ['pytorch', 'tensorflow', 'scikit-learn', 'fastapi', 'nlp', 'cnn', 'lstm', 'xgboost', 'eda']
        matches = sum(1 for kw in ml_keywords if kw in text)
        score += min(matches * 15, 100)
        
        return min(score, 100)
    
    def _extract_skills(self, job_description: str) -> List[str]:
        all_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Express', 'Next.js',
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git',
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
            'NLP', 'Computer Vision', 'RAG', 'Generative AI', 'LLM', 'Hugging Face',
            'Pandas', 'NumPy', 'Scikit-learn', 'Matplotlib',
            'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum',
            'Linux', 'Jenkins', 'CI/CD', 'Docker',
            'Data Analysis', 'Data Science', 'ETL', 'Tableau', 'PowerBI'
        ]
        
        found = []
        job_lower = job_description.lower()
        
        for skill in all_skills:
            if skill.lower() in job_lower:
                found.append(skill)
        
        return found
    
    def _match_skills(self, required_skills: List[str]) -> List[str]:
        # Use dynamic skills from the parsed resume if available, otherwise fallback to a fallback list
        master_skills = self.resume_skills if self.resume_skills else [
            'Python', 'Machine Learning', 'Deep Learning', 'PyTorch', 'TensorFlow', 
            'FastAPI', 'Flask', 'SQL', 'NLP', 'Computer Vision'
        ]
        
        matched = []
        for skill in required_skills:
            if any(skill.lower() == ms.lower() for ms in master_skills):
                matched.append(skill)
        
        return matched
    
    def _calculate_experience_score(self, job_description: str) -> float:
        score = 0
        text = job_description.lower()
        
        # Internships count (user has 3)
        if 'intern' in text:
            score += 15
        
        # Junior/fresher friendly
        if any(kw in text for kw in ['entry', 'fresher', 'junior', 'graduate', 'new grad']):
            score += 15
        else:
            score += 10
        
        return min(score, 30)
    
    def _calculate_education_score(self, job_description: str) -> float:
        score = 0
        text = job_description.lower()
        
        if 'bachelor' in text or 'b.tech' in text or 'degree' in text:
            score += 5
        
        if 'computer science' in text or 'cse' in text:
            score += 3
        
        if '2027' in text or '2026' in text:
            score += 2
        
        return min(score + 2, 10)  # Base score 2
    
    def _calculate_keyword_score(self, job_description: str) -> float:
        keywords = [
            'remote', 'remote-friendly', 'worldwide',
            'problem solving', 'team player', 'communication',
            'fast-paced', 'startup', 'innovative'
        ]
        
        matches = sum(1 for kw in keywords if kw in job_description.lower())
        return min(matches * 2, 10)
    
    def select_resume(self, job_type: str) -> str:
        """Select appropriate resume based on job type"""
        # Note: 'manoj_ml.pdf' is now the primary master resume for Data/AI/ML roles
        return 'manoj_ml.pdf'
    
    def get_application_decision(self, ats_result: Dict) -> Tuple[str, str]:
        """Determine application approach based on ATS score"""
        total = ats_result['total']
        
        if total >= 85:
            return 'apply_tailored', 'Generate new tailored resume and apply'
        elif total >= 60:
            return 'apply_fallback', 'Use fallback resume and apply'
        else:
            return 'manual', 'Send to Telegram for manual apply'
