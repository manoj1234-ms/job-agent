# Job Application Agent - Specification

## Overview
An autonomous AI agent that daily searches for SDE, Data Analyst, and ML Engineer positions, tailors your resume to each job, selects relevant GitHub projects, and applies on your behalf. Alerts you via desktop popup when intervention is needed.

## Configuration (config.yaml)
```yaml
user:
  name: "Manoj Sharma"
  github_username: "TO_BE_PROVIDED"  # User will provide
  resume_path: "manoj sharma.pdf"    # or "Data (1).pdf"
  resume_text_path: "resume_text.txt"  # Extracted text for parsing
  
jobs:
  target_roles:
    - "SDE"
    - "Software Development Engineer"
    - "Data Analyst"
    - "ML Engineer"
    - "Machine Learning Engineer"
    - "Data Scientist"
  locations:
    - "Remote"
    - "USA"
    - "India"
  platforms:
    - "linkedin"
    - "indeed"
    - "glassdoor"
  
search:
  daily_limit: 20
  min_match_score: 0.6
  
notifications:
  alert_method: "popup"  # popup, whatsapp, email
  twilio:
    account_sid: ""
    auth_token: ""
    from_number: ""
    to_number: ""
    
storage:
  type: "json"
  path: "data/applications.json"
  
logging:
  path: "logs/agent.log"
  level: "INFO"
```

## Core Modules

### 1. Job Search Module (`job_searcher.py`)
- Searches multiple job platforms (LinkedIn, Indeed, Glassdoor)
- Uses Playwright/Selenium for dynamic content
- Filters by roles: SDE, Data Analyst, ML Engineer
- Scores jobs by relevance to target roles
- Returns: List of Job objects with title, company, description, URL, match_score

### 2. Resume Parser (`resume_parser.py`)
- Extracts text from PDF resumes
- Parses skills, experience, projects
- Stores structured resume data in JSON
- Handles both resume files

### 3. Resume Tailor (`resume_tailor.py`)
- Analyzes job description
- Identifies required skills, keywords
- Rewrites resume bullet points to match
- Generates tailored resume version
- Uses LLM (OpenAI API) for intelligent tailoring

### 4. GitHub Project Selector (`github_selector.py`)
- Fetches user's repositories from GitHub API
- Analyzes repo descriptions, languages, stars
- Matches projects to job requirements
- Returns ranked list of relevant projects

### 5. Application Manager (`application_manager.py`)
- Tracks all applications in JSON
- Records: job info, tailored resume, selected projects, status
- Handles auto-apply when possible
- Flags jobs requiring manual apply

### 6. Alert System (`alerter.py`)
- Desktop popup notifications (Windows toast via plyer/ntfy)
- Optional: WhatsApp via Twilio
- Optional: Email notifications
- Creates alert log file

### 7. Agent Orchestrator (`agent.py`)
- Main loop: runs daily or on demand
- Coordinates all modules
- Decision tree for auto-apply vs alert user
- Generates daily report

## Data Structures

### Job Object
```python
{
  "id": "unique_id",
  "title": "ML Engineer",
  "company": "Tech Corp",
  "location": "Remote",
  "url": "https://...",
  "description": "Full JD...",
  "posted_date": "2026-02-14",
  "match_score": 0.85,
  "required_skills": ["Python", "TensorFlow", "SQL"],
  "status": "new|applied|manual|rejected"
}
```

### Application Record
```python
{
  "job_id": "...",
  "tailored_resume_path": "data/tailored/...",
  "selected_projects": ["repo1", "repo2"],
  "applied_date": "2026-02-14",
  "status": "auto_applied|pending_manual|submitted",
  "notes": "..."
}
```

## Workflow

1. **Daily Trigger** (cron/scheduler)
2. **Job Search** → Fetch new jobs from all platforms
3. **Filter & Score** → Keep jobs matching target roles
4. **For Each Job**:
   a. Parse job requirements
   b. Match GitHub projects
   c. Calculate match score
   d. IF score > threshold AND auto-apply possible:
      - Tailor resume
      - Apply automatically
   e. ELSE:
      - Alert user via popup
      - Wait for user decision
      - Apply when user confirms
5. **Log & Report** → Save to JSON, show summary

## File Structure
```
job-apply-agent/
├── config.yaml
├── requirements.txt
├── agent.py              # Main orchestrator
├── job_searcher.py       # Job search
├── resume_parser.py      # Resume extraction
├── resume_tailor.py      # Resume customization
├── github_selector.py    # Project matching
├── application_manager.py # Track applications
├── alerter.py            # Notifications
├── data/
│   ├── applications.json
│   └── tailored_resumes/
├── logs/
└── README.md
```

## Usage
```bash
# Install dependencies
pip install -r requirements.txt

# Run agent manually
python agent.py

# Or set up daily cron
# 0 9 * * * python /path/to/agent.py
```
