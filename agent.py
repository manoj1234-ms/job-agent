import os
import sys
import yaml
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from job_searcher import JobSearcher
from job_analyzer import JobAnalyzer
from resume_parser import ResumeParser
from latex_resume import LaTeXResumeGenerator
from github_selector import GitHubSelector
from application_manager import ApplicationManager
from alerter import Alerter
from telegram_bot import TelegramNotifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JobAgent:
    def __init__(self, config_path='config.yaml'):
        self.config = self._load_config(config_path)
        
        self.job_searcher = JobSearcher(self.config)
        self.resume_parser = ResumeParser(self.config)
        self.github_selector = GitHubSelector(self.config)
        self.app_manager = ApplicationManager(self.config)
        self.alerter = Alerter(self.config)
        self.telegram = TelegramNotifier(self.config)
        self.latex_resume = LaTeXResumeGenerator(self.config)
        
        self.github_projects = self.github_selector.fetch_repositories()
        
        # Initialize job analyzer with parsed resume data
        print("\n[1/4] Parsing resume for ATS baseline...")
        self.parsed_resume = self.resume_parser.parse()
        self.resume_text = self.parsed_resume.get('full_text', '')
        
        self.job_analyzer = JobAnalyzer(self.config, self.github_projects, self.parsed_resume)
        self.auto_apply_enabled = self.config.get('auto_apply', {}).get('enabled', False)
        self.ats_threshold = self.config.get('auto_apply', {}).get('ats_threshold', 0.85)
        self.fallback_threshold = self.config.get('auto_apply', {}).get('fallback_threshold', 0.60)
        
    def _load_config(self, config_path: str) -> dict:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        print(f"Config file {config_path} not found. Using defaults.")
        return {}
        
    def initialize(self):
        print("\n" + "="*60)
        print("JOB APPLICATION AGENT - INITIALIZING")
        print("="*60)
        
        print(f"\n[1/4] Resume Data Ready: {len(self.resume_text)} characters extracted")
        print(f"   - Identified ML Skills: {', '.join(self.parsed_resume.get('skills', [])[:8])}")
            
        print("\n[2/4] Fetching GitHub projects...")
        repos = self.github_selector.fetch_repositories()
        print(f"   - Found {len(repos)} repositories")
        
        print("\n[3/4] Loading application history...")
        stats = self.app_manager.get_stats()
        print(f"   - Total applications: {stats['total']}")
        print(f"   - Applied: {stats['applied']}")
        print(f"   - Pending: {stats['pending']}")
        
        print("\n[4/4] Ready!")
        print("="*60 + "\n")
        
    def run_daily(self):
        print(f"\n{'='*60}")
        print(f"JOB AGENT RUN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        print("[1/3] Searching for jobs...")
        jobs = self.job_searcher.search_all_platforms()
        print(f"   Found {len(jobs)} relevant jobs")
        
        new_jobs = [j for j in jobs if not self.app_manager.is_job_applied(
            job_url=j.get('url', ''),
            job_title=j.get('title', ''),
            job_company=j.get('company', '')
        )]
        print(f"   New jobs (not applied): {len(new_jobs)}")
        
        print("\n[2/3] Processing jobs...")
        
        notified_count = 0
        for job in new_jobs[:self.config.get('search', {}).get('daily_limit', 10)]:
            result = self._process_job(job)
            if result == 'notified':
                notified_count += 1
                
        print("\n[3/3] Summary...")
        stats = self.app_manager.get_stats()
        print(f"   - Notified today: {notified_count}")
        print(f"   - Total notifications: {stats['total']}")
        
        self.alerter.send_popup("Job Agent Complete", f"Sent alerts for {notified_count} jobs today")
        
    def _process_job(self, job: dict) -> str:
        print(f"\n   Processing: {job['title']} at {job['company']}")
        
        # Step 1: Detect job type
        job_type = self.job_analyzer.detect_job_type(
            job.get('description', ''),
            job.get('title', '')
        )
        print(f"   Job Type: {job_type}")
        
        # Step 2: Calculate FAANG ATS score
        ats_result = self.job_analyzer.calculate_ats_score(
            job.get('description', ''),
            job_type
        )
        ats_score = ats_result['total']
        print(f"   FAANG ATS Score: {ats_score:.0f}/100")
        
        # Send Telegram alert with Link
        self.telegram.send_job_alert(job, ats_score / 100)
        
        # Step 3: CUSTOM LOGIC - If ATS < 90, create a tailored resume
        tailored_resume_path = None
        if ats_score < 90:
            print(f"   [ACTION] ATS < 90% ({ats_score:.0f}%) - Generating tailored resume...")
            
            # Using LaTeX generator for premium quality
            # It internally uses the master resume and job description to tailor
            latex_content, refined_score, path = self.latex_resume.tailor_resume(
                job.get('description', ''),
                job.get('title', ''),
                job.get('company', '')
            )
            
            if path:
                tailored_resume_path = path
                print(f"   [OK] Tailored Resume Created: {os.path.basename(path)}")
                
                # Send the tailored resume document to Telegram
                caption = f"📄 <b>Tailored Resume for {job['company']}</b>\n"
                caption += f"Job: {job['title']}\n"
                caption += f"Improved ATS Score: {refined_score:.0%}"
                
                self.telegram.send_document(path, caption)
            else:
                print("   [WARN] Tailoring failed, using fallback.")

        # Mark as notified in application manager
        self.app_manager.add_application(job, tailored_resume_path, status='notified')
        
        return 'notified'
        
    def interactive_mode(self):
        print("\n--- INTERACTIVE MODE ---\n")
        
        print("1. Search for jobs")
        print("2. View application status")
        print("3. View matched projects")
        print("4. Tailor resume for a job")
        print("5. Check GitHub projects")
        print("6. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            self.run_daily()
        elif choice == '2':
            apps = self.app_manager.get_all_applications()
            for app in apps[-10:]:
                print(f"\n{app['job']['title']} at {app['job']['company']}")
                print(f"Status: {app['status']}")
        elif choice == '3':
            jobs = self.job_searcher.load_cached_jobs()
            if jobs:
                for job in jobs[:5]:
                    projects = self.github_selector.match_projects_to_job(job.get('description', ''))
                    print(f"\n{job['title']}: {[p['name'] for p in projects[:3]]}")
        elif choice == '4':
            print("\nEnter job description:")
            jd = input("> ")
            if jd and self.resume_text:
                tailored = self.resume_tailor.tailor_resume(self.resume_text, jd, "Custom Job")
                path = self.resume_tailor.save_tailored_resume(tailored, "Custom", "Job")
                print(f"Saved to: {path}")
        elif choice == '5':
            repos = self.github_selector.fetch_repositories()
            print(f"\nYour projects: {len(repos)}")
            for r in repos[:10]:
                print(f"  - {r['name']} ({r.get('language', 'N/A')})")
                
        print()
        
        
def main():
    agent = JobAgent()
    agent.initialize()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--daily':
            agent.run_daily()
        elif sys.argv[1] == '--test':
            agent.run_daily()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
    else:
        print("\nStarting in interactive mode...")
        while True:
            try:
                print("\n" + "="*50)
                print("JOB APPLICATION AGENT")
                print("="*50)
                print("1. Run daily job search & apply")
                print("2. Interactive mode")
                print("3. Exit")
                
                choice = input("\nSelect (1-3): ").strip()
                
                if choice == '1':
                    agent.run_daily()
                elif choice == '2':
                    agent.interactive_mode()
                elif choice == '3' or choice == '':
                    print("Goodbye!")
                    break
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nInterrupted. Goodbye!")
                break
                
                
if __name__ == '__main__':
    main()
