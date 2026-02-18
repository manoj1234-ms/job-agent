import os
import sys
import time
import yaml
import logging
from datetime import datetime, timedelta
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobAgentScheduler:
    def __init__(self, run_time="08:00", continuous=False, interval_hours=2):
        self.run_time = run_time
        self.running = True
        self.continuous = continuous
        self.interval_hours = interval_hours
        
    def get_next_run(self):
        now = datetime.now()
        hour, minute = map(int, self.run_time.split(':'))
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_run <= now:
            next_run += timedelta(days=1)
            
        return next_run
        
    def wait_until_run_time(self):
        while self.running:
            if self.continuous:
                # Continuous mode - run every X hours
                logger.info(f"Continuous mode: Running every {self.interval_hours} hours")
                self.run_agent()
                logger.info(f"Sleeping for {self.interval_hours} hours...")
                time.sleep(self.interval_hours * 3600)
            else:
                # Daily mode
                next_run = self.get_next_run()
                wait_seconds = (next_run - datetime.now()).total_seconds()
                
                if wait_seconds > 0:
                    logger.info(f"Next run at {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                    time.sleep(min(wait_seconds, 60))
                else:
                    time.sleep(1)
                    
                current_time = datetime.now()
                if current_time.hour == int(self.run_time.split(':')[0]) and current_time.minute < 5:
                    self.run_agent()
                    
    def run_agent(self):
        logger.info("Running job agent...")
        try:
            from agent import JobAgent
            agent = JobAgent()
            agent.initialize()
            agent.run_daily()
            logger.info("Run completed")
        except Exception as e:
            logger.error(f"Run failed: {e}")
            import traceback
            traceback.print_exc()
            
    def start(self):
        mode = "Continuous" if self.continuous else "Daily"
        logger.info(f"Scheduler started. {mode} mode.")
        try:
            self.wait_until_run_time()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped")
            self.running = False
            
            
def main():
    config = {}
    if os.path.exists('config.yaml'):
        with open('config.yaml') as f:
            config = yaml.safe_load(f)
    
    continuous_config = config.get('continuous', {})
    continuous = continuous_config.get('enabled', False)
    interval = continuous_config.get('interval_hours', 2)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--now':
            from agent import JobAgent
            agent = JobAgent()
            agent.initialize()
            agent.run_daily()
        elif sys.argv[1] == '--continuous':
            scheduler = JobAgentScheduler(continuous=True, interval_hours=interval)
            scheduler.start()
        elif sys.argv[1] == '--install':
            install_windows_task()
        else:
            scheduler = JobAgentScheduler(sys.argv[1])
            scheduler.start()
    else:
        if continuous:
            scheduler = JobAgentScheduler(continuous=True, interval_hours=interval)
        else:
            run_time = config.get('scheduler', {}).get('run_time', '08:00')
            scheduler = JobAgentScheduler(run_time)
        scheduler.start()
        
        
def install_windows_task():
    import subprocess
    script_path = os.path.abspath(__file__)
    python_path = sys.executable
    
    cmd = f'schtasks /create /tn "JobAgentDaily" /tr "{python_path} {script_path} --now" /sc daily /st 08:00'
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("Windows Task Scheduler: Job created successfully!")
        print("Task will run daily at 8:00 AM")
    except Exception as e:
        print(f"Failed to create task: {e}")
        print("You can manually create a task in Task Scheduler")
        
        
if __name__ == '__main__':
    main()
