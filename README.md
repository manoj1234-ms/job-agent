# 🤖 AI/ML Job Alert Agent (Elite Edition)

A high-performance automated job radar and AI-powered resume tailoring system designed specifically for **Manoj Sharma** to dominate the **Data Science & Machine Learning** job market.

## 🚀 Core Features

- **Multi-Platform Scouting**: Scans 10+ platforms including LinkedIn, Indeed, Naukri, Internshala, Cuvette, Unstop, and Instahyre.
- **AI/ML Focus**: Prioritizes Data Science, ML Engineering, AI Research, and Analyst roles (Specialized for 3rd-year CSE students).
- **Deep ATS Analysis**: Calculates a FAANG-level ATS score (Role Match, WE Impact, Project Depth, Problem Solving) using your specific ML profile.
- **Automatic Resume Tailoring**: If a job is a good fit but the ATS score is < 90%, it automatically generates a premium **LaTeX Resume** optimized for that specific role.
- **Telegram Command Center**: Instant alerts delivered to your phone with:
    - Direct Apply Link
    - ATS Match Percentage
    - The Tailored Resume PDF (ready to upload)

## 🛠️ Project Structure

```text
├── agent.py               # Main Entry Point
├── job_searcher.py        # Web Scraping & Multi-Platform Search
├── job_analyzer.py        # ATS Scoring & ML Profile Matching
├── latex_resume.py        # Premium PDF Resume Generator
├── telegram_bot.py        # Telegram Notification System
├── application_manager.py # State & Notification Tracking
├── github_selector.py     # GitHub Project Metadata Integration
├── config.yaml            # Roles, Locations, and API Settings
└── manoj_ml.pdf           # Primary Master Resume
```

## 📋 Prerequisites

- Python 3.10+
- Playwright (for job scouting)
- A Telegram Bot Token & Chat ID
- MiKTeX or pdflatex (optional, for local PDF compilation)

## 🏁 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure Your Bot**:
   Update `config.yaml` with your Telegram `bot_token` and `chat_id`.

3. **Launch the Agent**:
   ```bash
   python agent.py
   ```

## 🎯 Target Roles
- Data Scientist / Data Analyst / Intern
- ML Engineer / AI Engineer
- Computer Vision / NLP Specialist
- SDE Intern (AI-focused)

## ☁️ Deploy on GitHub Actions (Run 24/7 for FREE)

Your agent can run automatically every 6 hours on GitHub's cloud — no laptop needed!

### Step 1: Add Secrets to your GitHub Repo

Go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret Name | Value |
|---|---|
| `USER_NAME` | Manoj Sharma |
| `USER_EMAIL` | your@email.com |
| `USER_PHONE` | +91-XXXXXXXXXX |
| `USER_LINKEDIN` | linkedin.com/in/yourprofile |
| `USER_GITHUB` | github.com/yourprofile |
| `GITHUB_USERNAME` | manoj1234-ms |
| `TELEGRAM_BOT_TOKEN` | Your Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | Your Telegram Chat ID |

### Step 2: Enable the Workflow

Go to the **Actions** tab in your GitHub repo and enable workflows. The agent will automatically run every 6 hours.

### Step 3: Manual Trigger (Optional)

You can also trigger the agent manually anytime:
1. Go to **Actions** tab
2. Select **🤖 AI/ML Job Agent**
3. Click **Run workflow**

---
*Built with ❤️ for Manoj Sharma's AI Career Journey.*
