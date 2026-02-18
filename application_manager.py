import json
import os
from datetime import datetime
from typing import List, Dict, Any

class ApplicationManager:
    def __init__(self, config):
        self.storage_path = config.get('storage', {}).get('path', 'data/applications.json')
        self._ensure_storage_dir()
        self.applications = self._load_applications()
        
    def _ensure_storage_dir(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
    def _load_applications(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {'applications': [], 'stats': {'total': 0, 'applied': 0, 'pending': 0, 'rejected': 0}}
        
    def _save_applications(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.applications, f, indent=2)
            
    def add_application(self, job_data: Dict[str, Any], tailored_resume_path: str = None, 
                       selected_projects: List[str] = None, status: str = 'pending'):
        app_id = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        application = {
            'id': app_id,
            'job': job_data,
            'tailored_resume_path': tailored_resume_path,
            'selected_projects': selected_projects or [],
            'applied_date': None,
            'status': status,
            'created_at': datetime.now().isoformat()
        }
        
        self.applications['applications'].append(application)
        self._update_stats()
        self._save_applications()
        
        return app_id
        
    def update_status(self, app_id: str, status: str):
        for app in self.applications['applications']:
            if app['id'] == app_id:
                app['status'] = status
                if status == 'applied' and not app.get('applied_date'):
                    app['applied_date'] = datetime.now().isoformat()
                break
        self._update_stats()
        self._save_applications()
        
    def _update_stats(self):
        apps = self.applications['applications']
        self.applications['stats'] = {
            'total': len(apps),
            'applied': len([a for a in apps if a['status'] == 'applied']),
            'pending': len([a for a in apps if a['status'] == 'pending']),
            'rejected': len([a for a in apps if a['status'] == 'rejected'])
        }
        
    def get_pending_applications(self):
        return [a for a in self.applications['applications'] if a['status'] == 'pending']
        
    def is_job_applied(self, job_url: str = None, job_title: str = None, job_company: str = None) -> bool:
        for app in self.applications['applications']:
            if job_url and app['job'].get('url') == job_url:
                return True
            if job_title and job_company:
                if app['job'].get('title', '').lower() == job_title.lower() and \
                   app['job'].get('company', '').lower() == job_company.lower():
                    return True
        return False
        
    def get_stats(self):
        return self.applications['stats']
        
    def get_all_applications(self):
        return self.applications['applications']
