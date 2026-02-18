import os
import json
import logging
from datetime import datetime
from plyer import notification

logger = logging.getLogger(__name__)


class Alerter:
    def __init__(self, config):
        self.config = config
        self.alert_method = config.get('notifications', {}).get('alert_method', 'popup')
        self.popup_title = config.get('notifications', {}).get('popup_title', 'Job Agent')
        self.alerts_log_path = 'logs/alerts.json'
        self._ensure_log_dir()
        
    def _ensure_log_dir(self):
        os.makedirs('logs', exist_ok=True)
        
    def _log_alert(self, alert_type, message, details=None):
        alert_record = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message,
            'details': details or {}
        }
        
        if os.path.exists(self.alerts_log_path):
            with open(self.alerts_log_path, 'r') as f:
                alerts = json.load(f)
        else:
            alerts = []
            
        alerts.append(alert_record)
        
        with open(self.alerts_log_path, 'w') as f:
            json.dump(alerts, f, indent=2)
            
    def send_popup(self, title, message):
        try:
            notification.notify(
                title=title,
                message=message,
                app_name='Job Agent',
                timeout=10
            )
            logger.info(f"Popup notification sent: {title}")
        except Exception as e:
            logger.error(f"Failed to send popup: {e}")
            print(f"\n{'='*50}")
            print(f"ALERT: {title}")
            print(f"{message}")
            print(f"{'='*50}\n")
            
    def alert_user_action_required(self, job_title, company, job_url):
        message = f"Action needed for: {job_title} at {company}\nClick to review and apply manually."
        self.send_popup(f"{self.popup_title} - Action Required", message)
        self._log_alert('action_required', message, {
            'job_title': job_title,
            'company': company,
            'job_url': job_url
        })
        
    def alert_job_found(self, job_title, company, match_score):
        message = f"Found: {job_title} at {company}\nMatch: {match_score:.0%}"
        self.send_popup(f"{self.popup_title} - New Job", message)
        
    def alert_application_success(self, job_title, company):
        message = f"Successfully applied to {job_title} at {company}"
        self.send_popup(f"{self.popup_title} - Applied!", message)
        self._log_alert('application_success', message)
        
    def alert_error(self, error_message):
        self.send_popup(f"{self.popup_title} - Error", error_message)
        self._log_alert('error', error_message)
        
    def prompt_user(self, question, options):
        self.send_popup(f"{self.popup_title} - Question", question)
        print(f"\n{'='*50}")
        print(f"QUESTION: {question}")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        print(f"{'='*50}\n")
        
        while True:
            try:
                choice = input("Enter your choice (number): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
            except (ValueError, EOFError):
                print("No input detected. Using default: Save for later")
                return options[1] if len(options) > 1 else options[0]
            print("Invalid choice. Please enter a number.")
