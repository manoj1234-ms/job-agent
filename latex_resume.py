import os
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple

class LaTeXResumeGenerator:
    def __init__(self, config):
        self.config = config
        self.master_resume = self._load_master_resume()
        
    def _load_master_resume(self) -> dict:
        resume_text = ""
        if os.path.exists('resume_text.txt'):
            with open('resume_text.txt', 'r', encoding='utf-8') as f:
                resume_text = f.read()
        
        return {
            'name': 'Manoj Sharma',
            'email': 'manojsharma02620@gmail.com',
            'phone': '+91-7742626735',
            'linkedin': 'linkedin.com/in/manojsharma',
            'github': 'github.com/manoj1234-ms',
            'leetcode': 'leetcode.com/manojsharma',
            'summary': 'AI and ML focused developer experienced in building machine learning models, computer vision systems, and AI-powered applications with high-performance backend systems.',
            'education': {
                'degree': 'B.Tech in Computer Science and Engineering',
                'cgpa': '7.6/10',
                'institute': 'Gurukul Kangri Vishwavidyalaya (FET), Haridwar',
                'duration': 'Aug 2023 – Apr 2027 (Expected)'
            },
            'skills': {
                'languages': ['Python', 'C++', 'Java', 'SQL', 'JavaScript'],
                'frameworks': ['PyTorch', 'TensorFlow', 'Scikit-Learn', 'Flask', 'FastAPI'],
                'databases': ['PostgreSQL', 'MongoDB', 'Redis'],
                'core_cs': ['Machine Learning', 'Deep Learning', 'Data Analysis', 'NLP', 'Computer Vision'],
                'cloud_tools': ['AWS (Sagemaker, S3, IAM)', 'Docker', 'Kubernetes', 'Git', 'GitHub', 'MLOps'],
                'ai_ml': ['RAG', 'LLMs', 'Generative AI', 'CNNs', 'OpenAI API', 'Hugging Face', 'LangChain']
            },
            'experience': [
                {
                    'title': 'Software Development Engineer Intern',
                    'company': 'YugYatra.com',
                    'duration': 'Dec 2025 – Present',
                    'achievements': [
                        'Developed and optimized full-stack web features using React.js, Node.js, Express, and MongoDB',
                        'Improved application responsiveness and increased user engagement by 25%',
                        'Designed and integrated RESTful APIs for scalable production use',
                        'Handled backend logic, authentication, and database operations'
                    ]
                },
                {
                    'title': 'Frontend Developer Intern',
                    'company': 'Bootcoding Pvt. Ltd.',
                    'duration': 'Nov 2025 – Dec 2025',
                    'achievements': [
                        'Built responsive UI components using React, HTML5, CSS3, and JavaScript',
                        'Translated UI/UX and Figma designs into pixel-perfect web interfaces',
                        'Improved frontend performance and user experience through code optimization'
                    ]
                },
                {
                    'title': 'Python Developer Intern',
                    'company': 'Infotact Solutions',
                    'duration': 'May 2025 – Aug 2025',
                    'achievements': [
                        'Built backend automation tools using Python, Flask, SQLite, reducing manual tracking by 30%',
                        'Developed price-tracking system for 200+ e-commerce products using Flask + BeautifulSoup',
                        'Saved 20+ hours/week and increased price update frequency by 40%'
                    ]
                }
            ],
            'projects': [
                {
                    'name': 'AI Voice Interview System',
                    'github': 'github.com/manoj1234-ms/ai_voice-_interview',
                    'description': 'Full-stack AI-driven web application for real-time voice interviews',
                    'tech': ['Flask', 'OpenAI API', 'Speech Recognition', 'Whisper', 'GPT'],
                    'achievements': [
                        'Conducted real-time voice interviews using browser-based Speech Recognition',
                        'Integrated Whisper-based speech-to-text and GPT-driven evaluation',
                        'Automated feedback generation for interview responses'
                    ]
                },
                {
                    'name': 'Trip Planner with AI',
                    'live': 'trip-planner-ai.vercel.app',
                    'description': 'AI-powered personalized travel itinerary generator',
                    'tech': ['Next.js', 'Tailwind CSS', 'OpenAI API', 'Vercel'],
                    'achievements': [
                        'Reduced manual planning time by 70% using AI-generated itineraries',
                        'Achieved < 200ms response latency globally via serverless API'
                    ]
                }
            ],
            'certifications': [
                'Oracle AI Foundations Associate (2025)',
                'Oracle AI Vector Search Certified Professional (2025)',
                'Programming in Java – AICTE (2024)'
            ],
            'achievements': [
                'Solved 1000+ coding problems on LeetCode and CodeChef',
                'Global LeetCode rank: ~121K among 2M+ users (Top 6%)',
                'GSSoC 2025 Contributor',
                'Hackathon Finalist – Microsoft (2025), Adobe (2025), IIT Bhubaneswar'
            ]
        }
    
    def calculate_ats_score(self, job_description: str) -> float:
        """Calculate ATS match score based on job requirements"""
        job_lower = job_description.lower()
        score = 30  # Base score
        
        # Required skills from job
        required_skills = self._extract_skills(job_description)
        
        # Check each skill against resume
        resume_text = str(self.master_resume).lower()
        
        skill_matches = 0
        for skill in required_skills:
            if skill.lower() in resume_text:
                skill_matches += 1
        
        if required_skills:
            skill_score = (skill_matches / len(required_skills)) * 50
            score += skill_score
        
        # Experience keywords
        exp_keywords = ['experience', 'years', 'senior', 'lead', 'manager', 'expert', 'proficient']
        for kw in exp_keywords:
            if kw in job_lower:
                score += 2
        
        # Education keywords
        edu_keywords = ['bachelor', 'master', 'degree', 'computer science', 'engineering']
        for kw in edu_keywords:
            if kw in job_lower:
                score += 1
        
        return min(score / 100, 1.0)
    
    def _extract_skills(self, job_description: str) -> List[str]:
        all_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Express', 'Next.js',
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git',
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
            'NLP', 'Computer Vision', 'RAG', 'Generative AI', 'LLM', 'Hugging Face',
            'Data Analysis', 'Data Science', 'Pandas', 'NumPy', 'Scikit-learn',
            'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum',
            'Figma', 'HTML', 'CSS', 'Linux', 'Jenkins', 'CI/CD'
        ]
        
        found = []
        job_lower = job_description.lower()
        
        for skill in all_skills:
            if skill.lower() in job_lower:
                found.append(skill)
        
        return found
    
    def tailor_resume(self, job_description: str, job_title: str, company: str) -> Tuple[str, float, str]:
        """Generate tailored LaTeX resume and return (latex_code, ats_score, pdf_path)"""
        
        ats_score = self.calculate_ats_score(job_description)
        required_skills = self._extract_skills(job_description)
        
        # Build tailored LaTeX resume
        latex = self._generate_latex(required_skills)
        
        # Save LaTeX
        os.makedirs('tailored_resumes', exist_ok=True)
        safe_title = ''.join(c for c in job_title if c.isalnum() or c in ' -').strip()
        safe_company = ''.join(c for c in company if c.isalnum() or c in ' -').strip()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        tex_path = f'tailored_resumes/tailored_{safe_title}_{safe_company}_{timestamp}.tex'
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex)
        
        # Try to convert to PDF
        pdf_path = self._compile_latex(tex_path)
        
        return latex, ats_score, pdf_path if pdf_path else tex_path
    
    def _generate_latex(self, required_skills: List[str]) -> str:
        r = self.master_resume
        
        # Prioritize skills that match job
        prioritized_skills = []
        other_skills = []
        
        for cat, skills in r['skills'].items():
            for skill in skills:
                if any(skill.lower() in req.lower() for req in required_skills):
                    if skill not in prioritized_skills:
                        prioritized_skills.append(skill)
                else:
                    if skill not in other_skills:
                        other_skills.append(skill)
        
        final_skills = prioritized_skills + other_skills[:15]
        
        latex = r"""\documentclass[a4paper,10pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{geometry}
\geometry{a4paper, left=0.5in, right=0.5in, top=0.5in, bottom=0.5in}

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,
    urlcolor=blue,
}

\definecolor{darkblue}{RGB}{0,0,139}
\definecolor{gray}{RGB}{100,100,100}

\begin{document}

\centerline{\textbf{\Large\textcolor{darkblue}{""" + r['name'] + r"""}}
\vspace{0.2cm}

\centerline{
""" + r['email'] + r""" \quad $\vert$ \quad 
""" + r['phone'] + r""" \quad $\vert$ \quad 
\href{https://""" + r['linkedin'] + r"""}{LinkedIn}
}

\centerline{
\href{https://github.com/""" + r['github'][11:] + r"""}{GitHub} \quad $\vert$ \quad 
\href{https://leetcode.com/""" + r['leetcode'][11:] + r"""}{LeetCode}
}

\vspace{0.3cm}

\textcolor{darkblue}{\textbf{PROFESSIONAL SUMMARY}}
\\
\textbf{""" + r['summary'] + r"""}

\vspace{0.2cm}

\textcolor{darkblue}{\textbf{TECHNICAL SKILLS}}
\\
\textbf{Languages:} """ + ', '.join(r['skills']['languages']) + r"""
\\
\textbf{Frameworks:} """ + ', '.join(r['skills']['frameworks']) + r"""
\\
\textbf{Databases:} """ + ', '.join(r['skills']['databases']) + r"""
\\
\textbf{Cloud \& Tools:} """ + ', '.join(r['skills']['cloud_tools']) + r"""
\\
\textbf{AI/ML:} """ + ', '.join(r['skills']['ai_ml']) + r"""

\vspace{0.2cm}

\textcolor{darkblue}{\textbf{EDUCATION}}
\\
\textbf{""" + r['education']['degree'] + r"""}
\\
""" + r['education']['institute'] + r""" \quad $\vert$ \quad CGPA: """ + r['education']['cgpa'] + r""" \quad $\vert$ \quad """ + r['education']['duration'] + r"""

\vspace{0.2cm}

\textcolor{darkblue}{\textbf{EXPERIENCE}}
"""
        
        for exp in r['experience']:
            latex += r"""\\
\textbf{""" + exp['title'] + r"""}
\\
""" + exp['company'] + r""" \quad $\vert$ \quad """ + exp['duration'] + r"""
\\
\begin{itemize}
"""
            for ach in exp['achievements']:
                latex += r"\item " + ach + "\n"
            latex += r"\end{itemize}"
        
        latex += r"""

\vspace{0.2cm}

\textcolor{darkblue}{\textbf{PROJECTS}}
"""
        
        for proj in r['projects']:
            latex += r"""\\
\textbf{""" + proj['name'] + r"""}"""
            if proj.get('github'):
                latex += r" \quad \href{" + proj['github'] + r"}{[GitHub]}"
            if proj.get('live'):
                latex += r" \quad \href{" + proj['live'] + r"}{[Live]}"
            latex += r"""\\
""" + proj['description'] + r"""
\\
\textbf{Tech Stack:} """ + ', '.join(proj['tech']) + r"""
\\
\begin{itemize}
"""
            for ach in proj.get('achievements', []):
                latex += r"\item " + ach + "\n"
            latex += r"\end{itemize}"
        
        latex += r"""

\vspace{0.2cm}

\textcolor{darkblue}{\textbf{CERTIFICATIONS \& ACHIEVEMENTS}}
\\
\begin{itemize}
"""
        for cert in r['certifications']:
            latex += r"\item " + cert + "\n"
        for ach in r['achievements']:
            latex += r"\item " + ach + "\n"
        latex += r"""\end{itemize}

\end{document}
"""
        
        return latex
    
    def _compile_latex(self, tex_path: str) -> str:
        """Try to compile LaTeX to PDF"""
        try:
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_path],
                capture_output=True,
                timeout=30,
                cwd=os.path.dirname(tex_path) or '.'
            )
            
            if result.returncode == 0:
                pdf_path = tex_path.replace('.tex', '.pdf')
                if os.path.exists(pdf_path):
                    return pdf_path
        except Exception as e:
            print(f"LaTeX compilation failed: {e}")
        
        # Try HTML to PDF as fallback
        return self._html_to_pdf(tex_path.replace('.tex', '.html'))
    
    def generate_html(self, required_skills: List[str] = None) -> str:
        """Generate HTML version of resume"""
        if required_skills is None:
            required_skills = []
            
        r = self.master_resume
        
        # Prioritize skills that match job
        prioritized = []
        for cat, skills in r['skills'].items():
            for skill in skills:
                if any(skill.lower() in req.lower() for req in required_skills):
                    prioritized.append(skill)
        
        other_skills = []
        for cat, skills in r['skills'].items():
            for skill in skills:
                if skill not in prioritized and skill not in other_skills:
                    other_skills.append(skill)
        
        final_skills = prioritized + other_skills[:15]
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{r['name']} - Resume</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 11pt; line-height: 1.4; color: #333; max-width: 800px; margin: 0 auto; padding: 40px; }}
        .header {{ text-align: center; margin-bottom: 20px; }}
        .name {{ font-size: 24pt; font-weight: bold; color: #1a1a2e; margin-bottom: 8px; }}
        .contact {{ font-size: 10pt; color: #555; }}
        .contact a {{ color: #0066cc; text-decoration: none; }}
        .section {{ margin-bottom: 18px; }}
        .section-title {{ font-size: 12pt; font-weight: bold; color: #1a1a2e; border-bottom: 2px solid #1a1a2e; padding-bottom: 4px; margin-bottom: 10px; }}
        .subsection {{ margin-bottom: 12px; }}
        .job-title {{ font-weight: bold; color: #333; }}
        .company {{ color: #555; }}
        .duration {{ color: #777; font-size: 10pt; float: right; }}
        ul {{ margin-left: 20px; }}
        li {{ margin-bottom: 4px; }}
        .skills-list {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .skill {{ background: #f0f0f0; padding: 3px 10px; border-radius: 4px; font-size: 10pt; }}
        .skill.priority {{ background: #1a1a2e; color: white; }}
        @media print {{ body {{ padding: 20px; }} }}
    </style>
</head>
<body>
    <div class="header">
        <div class="name">{r['name']}</div>
        <div class="contact">
            {r['email']} | {r['phone']} | 
            <a href="https://{r['linkedin']}">LinkedIn</a> | 
            <a href="https://github.com/{r['github'][11:]}">GitHub</a> | 
            <a href="https://{r['leetcode']}">LeetCode</a>
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">PROFESSIONAL SUMMARY</div>
        <p>{r['summary']}</p>
    </div>
    
    <div class="section">
        <div class="section-title">TECHNICAL SKILLS</div>
        <div class="skills-list">
"""
        
        for skill in final_skills:
            is_priority = skill in prioritized
            html += f'            <span class="skill{" priority" if is_priority else ""}">{skill}</span>\n'
        
        html += """        </div>
    </div>
    
    <div class="section">
        <div class="section-title">EDUCATION</div>
        <div class="subsection">
            <span class="job-title">""" + r['education']['degree'] + """</span>
            <span class="duration">""" + r['education']['duration'] + """</span><br>
            """ + r['education']['institute'] + """ | CGPA: """ + r['education']['cgpa'] + """
        </div>
    </div>
    
    <div class="section">
        <div class="section-title">EXPERIENCE</div>
"""
        
        for exp in r['experience']:
            html += f"""        <div class="subsection">
            <span class="job-title">{exp['title']}</span>
            <span class="duration">{exp['duration']}</span><br>
            <span class="company">{exp['company']}</span>
            <ul>
"""
            for ach in exp['achievements']:
                html += f"                <li>{ach}</li>\n"
            html += """            </ul>
        </div>
"""
        
        html += """    </div>
    
    <div class="section">
        <div class="section-title">PROJECTS</div>
"""
        
        for proj in r['projects']:
            html += f"""        <div class="subsection">
            <span class="job-title">{proj['name']}</span>
"""
            if proj.get('github'):
                html += f' <a href="{proj["github"]}">[GitHub]</a>'
            if proj.get('live'):
                html += f' <a href="{proj["live"]}">[Live]</a>'
            html += f"""<br>
            {proj['description']}<br>
            <strong>Tech:</strong> {', '.join(proj['tech'])}
            <ul>
"""
            for ach in proj.get('achievements', []):
                html += f"                <li>{ach}</li>\n"
            html += """            </ul>
        </div>
"""
        
        html += """    </div>
    
    <div class="section">
        <div class="section-title">CERTIFICATIONS & ACHIEVEMENTS</div>
        <ul>
"""
        
        for cert in r['certifications']:
            html += f"            <li>{cert}</li>\n"
        for ach in r['achievements']:
            html += f"            <li>{ach}</li>\n"
        
        html += """        </ul>
    </div>
</body>
</html>"""
        
        return html
    
    def _html_to_pdf(self, html_path: str) -> str:
        """Convert HTML to PDF using weasyprint or browser"""
        if not os.path.exists(html_path):
            # Generate HTML first
            html = self.generate_html()
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        # Try weasyprint
        try:
            import weasyprint
            pdf_path = html_path.replace('.html', '.pdf')
            weasyprint.HTML(html_path).write_pdf(pdf_path)
            if os.path.exists(pdf_path):
                return pdf_path
        except Exception as e:
            print(f"WeasyPrint error: {e}")
        
        # Try playwright
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(f'file://{os.path.abspath(html_path)}')
                pdf_path = html_path.replace('.html', '.pdf')
                page.pdf(path=pdf_path, format='A4', margin={'top': '0.5in', 'bottom': '0.5in', 'left': '0.5in', 'right': '0.5in'})
                browser.close()
                if os.path.exists(pdf_path):
                    return pdf_path
        except Exception as e:
            print(f"Playwright error: {e}")
        
        # Return HTML path as fallback - user can print to PDF from browser
        return html_path
    
    def generate_ats_resume(self, job_description: str, job_title: str, company: str) -> Tuple[str, float, str]:
        """Generate ATS-optimized resume and return (html_path, ats_score, pdf_path)"""
        
        ats_score = self.calculate_ats_score(job_description)
        required_skills = self._extract_skills(job_description)
        
        # Generate HTML
        html = self.generate_html(required_skills)
        
        os.makedirs('tailored_resumes', exist_ok=True)
        safe_title = ''.join(c for c in job_title if c.isalnum() or c in ' -').strip()
        safe_company = ''.join(c for c in company if c.isalnum() or c in ' -').strip()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        html_path = f'tailored_resumes/tailored_{safe_title}_{safe_company}_{timestamp}.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Also save LaTeX
        latex = self._generate_latex(required_skills)
        tex_path = html_path.replace('.html', '.tex')
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex)
        
        # Try to convert to PDF
        pdf_path = self._html_to_pdf(html_path)
        
        return html_path, ats_score, pdf_path
