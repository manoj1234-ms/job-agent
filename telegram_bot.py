import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, config):
        self.config = config
        self.telegram_config = config.get('telegram', {})
        self.enabled = self.telegram_config.get('enabled', False)
        # Priority: Environment Variable > Config File
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', self.telegram_config.get('bot_token', ''))
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', self.telegram_config.get('chat_id', ''))
        
    def send_message(self, message: str) -> bool:
        if not self.enabled or not self.bot_token or not self.chat_id:
            logger.info("Telegram not enabled")
            return False
            
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False

    def send_document(self, file_path: str, caption: str = "") -> bool:
        if not self.enabled or not self.bot_token or not self.chat_id:
            return False
            
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
            
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
            files = {'document': open(file_path, 'rb')}
            data = {'chat_id': self.chat_id, 'caption': caption, 'parse_mode': 'HTML'}
            response = requests.post(url, data=data, files=files, timeout=20)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Telegram document error: {e}")
            return False
            
    def send_job_alert(self, job: dict, match_score: float) -> bool:
        platform = job.get('platform', 'Job Board')
        company = job.get('company', 'Company')
        title = job.get('title', 'Position')
        location = job.get('location', 'Remote')
        url = job.get('url', '')
        salary = job.get('salary', '')
        
        message = f"""
<b>🔔 NEW JOB ALERT</b>

<b>💼 {title}</b>
🏢 {company}
📍 {location}
📊 Match: {match_score:.0%}
🔗 <a href="{url}">Apply Here</a>

<i>Source: {platform}</i>
"""
        if salary:
            message += f"\n💰 {salary}"
            
        return self.send_message(message)
        
    def send_jobs_summary(self, jobs: list) -> bool:
        if not jobs:
            return False
            
        message = f"""
<b>📋 JOBS FOUND - {datetime.now().strftime('%Y-%m-%d')}</b>

<b>Found {len(jobs)} new jobs!</b>

"""
        
        for i, job in enumerate(jobs[:10], 1):
            title = job.get('title', 'Position')[:40]
            company = job.get('company', 'Company')[:25]
            url = job.get('url', '')
            match = job.get('match_score', 0)
            
            message += f"{i}. <b>{title}</b>\n"
            message += f"   🏢 {company} | ⭐ {match:.0%}\n"
            message += f"   🔗 <a href=\"{url}\">Apply</a>\n\n"
        
        if len(jobs) > 10:
            message += f"\n...and {len(jobs) - 10} more jobs"
            
        return self.send_message(message)
        
    def send_application_success(self, job: dict) -> bool:
        message = f"""
<b>✅ APPLICATION SENT!</b>

<b>{job.get('title', 'Position')}</b>
🏢 {job.get('company', 'Company')}

<i>Resume sent with matched skills & projects</i>
"""
        return self.send_message(message)
        
    def send_daily_summary(self, applied_count: int, total_applied: int, jobs_found: int) -> bool:
        message = f"""
<b>📊 DAILY SUMMARY - {datetime.now().strftime('%Y-%m-%d')}</b>

✅ Applied today: {applied_count}
📨 Total applications: {total_applied}
🔍 Jobs found: {jobs_found}

Keep applying! 💪
"""
        return self.send_message(message)
        
    def ask_approval(self, question: str, options: list) -> str:
        if not self.enabled:
            return None
            
        message = f"""
<b>❓ ACTION NEEDED</b>

{question}

"""
        for i, opt in enumerate(options, 1):
            message += f"{i}. {opt}\n"
            
        self.send_message(message)
        return None
        
    def check_for_commands(self) -> dict:
        if not self.enabled or not self.bot_token:
            return None
            
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and data.get('result'):
                    updates = data['result']
                    if updates:
                        last_update = updates[-1]
                        if 'message' in last_update:
                            return {
                                'chat_id': last_update['message']['chat']['id'],
                                'text': last_update['message'].get('text', ''),
                            }
        except Exception as e:
            logger.error(f"Telegram check error: {e}")
        return None
