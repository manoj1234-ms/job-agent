import os
import json
import httpx
from typing import List, Dict, Any

class GitHubSelector:
    def __init__(self, config):
        self.github_username = config.get('user', {}).get('github_username', '')
        self.cache_path = 'data/github_projects.json'
        
    def fetch_repositories(self) -> List[Dict[str, Any]]:
        if not self.github_username or self.github_username == "REPLACE_WITH_YOUR_GITHUB_USERNAME":
            print("GitHub username not configured. Skipping project matching.")
            return []
            
        cache_file = self.cache_path
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
                
        try:
            url = f"https://api.github.com/users/{self.github_username}/repos"
            response = httpx.get(url, timeout=30)
            response.raise_for_status()
            repos = response.json()
            
            projects = []
            for repo in repos:
                projects.append({
                    'name': repo.get('name', ''),
                    'description': repo.get('description', ''),
                    'language': repo.get('language', ''),
                    'stars': repo.get('stargazers_count', 0),
                    'url': repo.get('html_url', ''),
                    'topics': repo.get('topics', [])
                })
                
            os.makedirs('data', exist_ok=True)
            with open(cache_file, 'w') as f:
                json.dump(projects, f, indent=2)
                
            return projects
            
        except Exception as e:
            print(f"Error fetching GitHub repos: {e}")
            return []
            
    def match_projects_to_job(self, job_description: str, projects: List[Dict] = None) -> List[Dict]:
        if projects is None:
            projects = self.fetch_repositories()
            
        if not projects:
            return []
            
        job_lower = job_description.lower()
        
        tech_keywords = {
            'python': ['python', 'pandas', 'numpy', 'django', 'flask', 'tensorflow', 'pytorch'],
            'java': ['java', 'spring', 'hibernate'],
            'javascript': ['javascript', 'react', 'angular', 'vue', 'node', 'express'],
            'ml': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras', 'ml'],
            'data': ['data analysis', 'data science', 'pandas', 'sql', 'tableau', 'visualization'],
            'cloud': ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes'],
            'sql': ['sql', 'mysql', 'postgresql', 'mongodb', 'database'],
            'web': ['html', 'css', 'api', 'rest', 'frontend', 'backend']
        }
        
        scored_projects = []
        
        for project in projects:
            score = 0
            proj_text = f"{project['name']} {project['description']} {project['language']}".lower()
            
            for category, keywords in tech_keywords.items():
                if any(kw in job_lower for kw in keywords):
                    if any(kw in proj_text for kw in keywords):
                        score += 2
                        
            if project.get('stars', 0) > 0:
                score += min(project['stars'] / 10, 3)
                
            if project.get('language'):
                if project['language'].lower() in job_lower:
                    score += 3
                    
            if score > 0:
                scored_projects.append({
                    **project,
                    'match_score': score
                })
                
        scored_projects.sort(key=lambda x: x['match_score'], reverse=True)
        
        return scored_projects[:5]
        
    def get_top_projects(self, limit: int = 5) -> List[Dict]:
        projects = self.fetch_repositories()
        if not projects:
            return []
            
        sorted_projects = sorted(projects, key=lambda x: x.get('stars', 0), reverse=True)
        return sorted_projects[:limit]
