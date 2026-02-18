import os
import json
import httpx
import asyncio
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from datetime import datetime

class JobSearcher:
    def __init__(self, config):
        self.target_roles = config.get('jobs', {}).get('target_roles', [])
        self.locations = config.get('jobs', {}).get('locations', [])
        self.platforms = config.get('jobs', {}).get('platforms', [])
        self.daily_limit = config.get('search', {}).get('daily_limit', 20)
        self.min_match_score = config.get('search', {}).get('min_match_score', 0.5)
        self.jobs_cache_path = 'data/jobs_cache.json'
        
    def search_all_platforms(self) -> List[Dict[str, Any]]:
        all_jobs = []
        
        # 1. API-based platforms (Fast)
        print("Searching API-based platforms...")
        all_jobs.extend(self.search_remote_ok())
        all_jobs.extend(self.search_remotive())
        all_jobs.extend(self.search_weworkremotely())
        
        # 2. Browser-based platforms (Slow but necessary)
        # We run these using a helper to manage the event loop
        print("Searching browser-based platforms (Naukri, Internshala)...")
        browser_jobs = self._run_browser_search()
        all_jobs.extend(browser_jobs)
        
        # 3. Dedicated niche platforms
        all_jobs.extend(self.search_python_jobs())
        
        # Deduplicate and Filter
        unique_jobs = self._deduplicate_and_filter(all_jobs)
        
        # Cache results
        self._cache_jobs(unique_jobs)
        
        return unique_jobs[:self.daily_limit]

    def _deduplicate_and_filter(self, jobs: List[Dict]) -> List[Dict]:
        seen = set()
        unique = []
        for j in jobs:
            key = (j.get('title', '').lower().strip(), j.get('company', '').lower().strip())
            if key not in seen:
                score = j.get('match_score', 0)
                if score == 0: # Recalculate if missing
                    score = self._calculate_match_score(j.get('title', ''), j.get('description', ''))
                    j['match_score'] = score
                
                if score >= self.min_match_score:
                    seen.add(key)
                    unique.append(j)
        
        unique.sort(key=lambda x: x['match_score'], reverse=True)
        return unique

    def _calculate_match_score(self, title: str, description: str) -> float:
        title_lower = title.lower()
        desc_lower = description.lower()
        
        score = 0.2 # Base score
        
        # Title match (high priority)
        for role in self.target_roles:
            if role.lower() in title_lower:
                score += 0.5
                break
        
        # Description keywords
        keywords = ['python', 'pytorch', 'tensorflow', 'scikit-learn', 'deep learning', 'machine learning', 'data', 'ml', 'ai', 'nlp', 'vision']
        for kw in keywords:
            if kw in desc_lower:
                score += 0.05
                
        # Seniority penalty
        seniors = ['senior', 'staff', 'principal', 'lead', 'manager', 'head', 'director']
        if any(s in title_lower for s in seniors):
            score -= 0.4
            
        return min(max(score, 0), 1.0)

    def search_remote_ok(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            url = "https://remoteok.com/api"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = httpx.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for item in data[1:30]:
                    job = {
                        'id': f"remoteok_{item.get('id')}",
                        'title': item.get('position', ''),
                        'company': item.get('company', ''),
                        'location': 'Remote',
                        'url': f"https://remoteok.com{item.get('url', '')}" if not item.get('url', '').startswith('http') else item.get('url'),
                        'description': item.get('description', '')[:500],
                        'platform': 'RemoteOK',
                        'posted_date': item.get('date', 'Recent'),
                        'match_score': self._calculate_match_score(item.get('position', ''), item.get('description', ''))
                    }
                    jobs.append(job)
        except Exception as e:
            print(f"RemoteOK error: {e}")
        return jobs

    def search_remotive(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            url = "https://remotive.com/api/remote-jobs?limit=20"
            response = httpx.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('jobs', []):
                    job = {
                        'id': f"remotive_{item.get('id')}",
                        'title': item.get('title', ''),
                        'company': item.get('company_name', ''),
                        'location': item.get('candidate_required_location', 'Remote'),
                        'url': item.get('url', ''),
                        'description': item.get('description', '')[:500],
                        'platform': 'Remotive',
                        'posted_date': item.get('published_at', 'Recent'),
                        'match_score': self._calculate_match_score(item.get('title', ''), item.get('description', ''))
                    }
                    jobs.append(job)
        except Exception as e:
            print(f"Remotive error: {e}")
        return jobs

    def search_weworkremotely(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            url = "https://weworkremotely.com/api/jobs"
            response = httpx.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('jobs', [])[:20]:
                    job = {
                        'id': f"wework_{item.get('id')}",
                        'title': item.get('title', ''),
                        'company': item.get('company_name', ''),
                        'location': 'Remote',
                        'url': f"https://weworkremotely.com{item.get('url', '')}",
                        'description': item.get('description', '')[:500],
                        'platform': 'WeWorkRemotely',
                        'posted_date': item.get('published_at', 'Recent'),
                        'match_score': self._calculate_match_score(item.get('title', ''), item.get('description', ''))
                    }
                    jobs.append(job)
        except Exception as e:
            print(f"WeWorkRemotely error: {e}")
        return jobs

    def search_python_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            url = "https://www.python.org/jobs/"
            response = httpx.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                listings = soup.select('.listing-row')[:10]
                for l in listings:
                    title_elem = l.select_one('.listing-row-title')
                    if title_elem:
                        link = title_elem.select_one('a')
                        job = {
                            'id': f"python_{l.get('id', 'N/A')}",
                            'title': title_elem.get_text(strip=True),
                            'company': l.select_one('.listing-company-name').get_text(strip=True),
                            'location': l.select_one('.listing-location').get_text(strip=True),
                            'url': 'https://www.python.org' + link.get('href', '') if link else '',
                            'description': 'Python-specific opportunity',
                            'platform': 'Python.org',
                            'posted_date': 'Recent',
                            'match_score': 0.75
                        }
                        jobs.append(job)
        except Exception as e:
            print(f"Python.org error: {e}")
        return jobs

    def _run_browser_search(self) -> List[Dict]:
        try:
            return asyncio.run(self._async_browser_search())
        except Exception as e:
            print(f"Browser search error: {e}")
            return []

    async def _async_browser_search(self) -> List[Dict]:
        from playwright.async_api import async_playwright
        all_browser_jobs = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1280, 'height': 800}
            )
            
            # 1. Search Naukri
            print("  - Searching Naukri...")
            naukri_jobs = await self._search_naukri_playwright(context)
            all_browser_jobs.extend(naukri_jobs)
            
            # 2. Search Internshala
            print("  - Searching Internshala...")
            internshala_jobs = await self._search_internshala_playwright(context)
            all_browser_jobs.extend(internshala_jobs)
            
            # 3. Search LinkedIn Guest
            print("  - Searching LinkedIn Guest...")
            linkedin_jobs = await self._search_linkedin_guest(context)
            all_browser_jobs.extend(linkedin_jobs)

            # 4. Search Indeed India Guest
            print("  - Searching Indeed India...")
            indeed_jobs = await self._search_indeed_india(context)
            all_browser_jobs.extend(indeed_jobs)

            # 5. Search Cuvette (India Freshers)
            print("  - Searching Cuvette...")
            cuvette_jobs = await self._search_cuvette(context)
            all_browser_jobs.extend(cuvette_jobs)

            # 6. Search Unstop (Formerly Dare2Compete)
            print("  - Searching Unstop...")
            unstop_jobs = await self._search_unstop(context)
            all_browser_jobs.extend(unstop_jobs)

            # 7. Search Instahyre
            print("  - Searching Instahyre...")
            instahyre_jobs = await self._search_instahyre(context)
            all_browser_jobs.extend(instahyre_jobs)
            
            await browser.close()
            
        return all_browser_jobs

    async def _search_cuvette(self, context) -> List[Dict]:
        jobs = []
        try:
            page = await context.new_page()
            # Cuvette is very specific to freshers
            url = "https://cuvette.tech/app/student/jobs/all"
            await page.goto(url, timeout=30000, wait_until='domcontentloaded')
            await asyncio.sleep(5)
            
            cards = await page.query_selector_all('.job-card, [class*="JobCard"]')
            for card in cards[:10]:
                title_elem = await card.query_selector('.job-title, [class*="JobTitle"]')
                company_elem = await card.query_selector('.company-name, [class*="CompanyName"]')
                
                if title_elem:
                    title = await title_elem.inner_text()
                    company = await company_elem.inner_text() if company_elem else 'N/A'
                    
                    # Cuvette usually requires login for links, but list is public sometimes
                    jobs.append({
                        'id': f"cuvette_{title}_{company}",
                        'title': title.strip(),
                        'company': company.strip(),
                        'location': 'India/Remote',
                        'url': url, # Primary URL if specific link not found
                        'description': 'Freshers Job on Cuvette',
                        'platform': 'Cuvette',
                        'posted_date': 'Recent',
                        'match_score': 0.75
                    })
            await page.close()
        except Exception as e:
            print(f"    Cuvette error: {e}")
        return jobs

    async def _search_unstop(self, context) -> List[Dict]:
        jobs = []
        try:
            page = await context.new_page()
            url = "https://unstop.com/job/all"
            await page.goto(url, timeout=30000, wait_until='domcontentloaded')
            await asyncio.sleep(5)
            
            cards = await page.query_selector_all('app-job-card, .job-card')
            for card in cards[:10]:
                title_elem = await card.query_selector('.job-title, h3')
                company_elem = await card.query_selector('.company-title, .sub-title')
                link_elem = await card.query_selector('a')
                
                if title_elem:
                    title = await title_elem.inner_text()
                    company = await company_elem.inner_text() if company_elem else 'N/A'
                    link = await link_elem.get_attribute('href') if link_elem else ''
                    
                    jobs.append({
                        'id': f"unstop_{title}",
                        'title': title.strip(),
                        'company': company.strip(),
                        'location': 'India',
                        'url': 'https://unstop.com' + link if link.startswith('/') else (link or url),
                        'description': 'Student Opportunity on Unstop',
                        'platform': 'Unstop',
                        'posted_date': 'Recent',
                        'match_score': 0.8
                    })
            await page.close()
        except Exception as e:
            print(f"    Unstop error: {e}")
        return jobs

    async def _search_instahyre(self, context) -> List[Dict]:
        jobs = []
        for role in self.target_roles[:1]:
            try:
                page = await context.new_page()
                url = f"https://www.instahyre.com/jobs-search/?keywords={role.replace(' ', '+')}"
                await page.goto(url, timeout=30000, wait_until='domcontentloaded')
                await asyncio.sleep(5)
                
                cards = await page.query_selector_all('.job-listing')
                for card in cards[:10]:
                    title_elem = await card.query_selector('.job-title')
                    company_elem = await card.query_selector('.company-name')
                    link_elem = await card.query_selector('a')
                    
                    if title_elem:
                        title = await title_elem.inner_text()
                        company = await company_elem.inner_text() if company_elem else 'N/A'
                        link = await link_elem.get_attribute('href') if link_elem else ''
                        
                        jobs.append({
                            'id': f"instahyre_{title}",
                            'title': title.strip(),
                            'company': company.strip(),
                            'location': 'India',
                            'url': 'https://www.instahyre.com' + link if link.startswith('/') else link,
                            'description': 'Tech Job on Instahyre',
                            'platform': 'Instahyre',
                            'posted_date': 'Recent',
                            'match_score': 0.7
                        })
                await page.close()
            except Exception as e:
                print(f"    Instahyre error: {e}")
        return jobs

    async def _search_naukri_playwright(self, context) -> List[Dict]:
        jobs = []
        for role in self.target_roles[:2]:
            try:
                page = await context.new_page()
                url = f"https://www.naukri.com/{role.lower().replace(' ', '-')}-jobs"
                await page.goto(url, timeout=30000, wait_until='domcontentloaded')
                await asyncio.sleep(4)
                
                cards = await page.query_selector_all('.jobTuple, .tuple, .srp-jobtuple-wrapper')
                for card in cards[:10]:
                    title_elem = await card.query_selector('.title, .job-title')
                    company_elem = await card.query_selector('.companyInfo, .company-name')
                    link_elem = await card.query_selector('a.title, a')
                    
                    if title_elem:
                        title = await title_elem.inner_text()
                        company = await company_elem.inner_text() if company_elem else 'N/A'
                        link = await link_elem.get_attribute('href') if link_elem else ''
                        
                        jobs.append({
                            'id': f"naukri_{title}_{company}",
                            'title': title.strip(),
                            'company': company.strip().split('\n')[0],
                            'location': 'India',
                            'url': link,
                            'description': f"{role} position on Naukri",
                            'platform': 'Naukri',
                            'posted_date': 'Recent',
                            'match_score': 0.7
                        })
                await page.close()
            except Exception as e:
                print(f"    Naukri error: {e}")
        return jobs

    async def _search_internshala_playwright(self, context) -> List[Dict]:
        jobs = []
        for role in self.target_roles[:2]:
            try:
                page = await context.new_page()
                url = f"https://internshala.com/students/jobs#keywords={role.replace(' ', '%20')}"
                await page.goto(url, timeout=30000, wait_until='domcontentloaded')
                await asyncio.sleep(4)
                
                cards = await page.query_selector_all('.individual_detail')
                for card in cards[:10]:
                    title_elem = await card.query_selector('.job-title')
                    company_elem = await card.query_selector('.company-name')
                    link_elem = await card.query_selector('a')
                    
                    if title_elem:
                        title = await title_elem.inner_text()
                        company = await company_elem.inner_text() if company_elem else 'N/A'
                        link = await link_elem.get_attribute('href') if link_elem else ''
                        
                        jobs.append({
                            'id': f"internshala_{title}",
                            'title': title.strip(),
                            'company': company.strip(),
                            'location': 'India/Remote',
                            'url': 'https://internshala.com' + link if link.startswith('/') else link,
                            'description': f"Internship: {role}",
                            'platform': 'Internshala',
                            'posted_date': 'Recent',
                            'match_score': 0.8
                        })
                await page.close()
            except Exception as e:
                print(f"    Internshala error: {e}")
        return jobs

    async def _search_linkedin_guest(self, context) -> List[Dict]:
        jobs = []
        for role in self.target_roles[:2]:
            try:
                page = await context.new_page()
                url = f"https://www.linkedin.com/jobs/search?keywords={role.replace(' ', '%20')}&location=India&f_TPR=r86400"
                await page.goto(url, timeout=30000, wait_until='domcontentloaded')
                await asyncio.sleep(5)
                
                cards = await page.query_selector_all('.base-card')
                for card in cards[:10]:
                    title_elem = await card.query_selector('.base-search-card__title')
                    company_elem = await card.query_selector('.base-search-card__subtitle')
                    link_elem = await card.query_selector('.base-card__full-link')
                    
                    if title_elem:
                        title = await title_elem.inner_text()
                        company = await company_elem.inner_text() if company_elem else 'N/A'
                        link = await link_elem.get_attribute('href') if link_elem else ''
                        
                        jobs.append({
                            'id': f"linkedin_{title}",
                            'title': title.strip(),
                            'company': company.strip(),
                            'location': 'India',
                            'url': link,
                            'description': 'LinkedIn Guest Job',
                            'platform': 'LinkedIn',
                            'posted_date': 'Recent',
                            'match_score': 0.75
                        })
                await page.close()
            except Exception as e:
                print(f"    LinkedIn Guest error: {e}")
        return jobs

    async def _search_indeed_india(self, context) -> List[Dict]:
        jobs = []
        for role in self.target_roles[:1]:
            try:
                page = await context.new_page()
                # Use Indeed India mobile-friendly search
                url = f"https://in.indeed.com/jobs?q={role.replace(' ', '+')}&l=India&fromage=1"
                await page.goto(url, timeout=30000, wait_until='domcontentloaded')
                await asyncio.sleep(4)
                
                cards = await page.query_selector_all('.job_seen_beacon')
                for card in cards[:10]:
                    title_elem = await card.query_selector('h2.jobTitle span[title]')
                    company_elem = await card.query_selector('[data-testid="company-name"]')
                    link_elem = await card.query_selector('h2.jobTitle a')
                    
                    if title_elem:
                        title = await title_elem.inner_text()
                        company = await company_elem.inner_text() if company_elem else 'N/A'
                        link = await link_elem.get_attribute('href') if link_elem else ''
                        if link and not link.startswith('http'):
                            link = 'https://in.indeed.com' + link
                            
                        jobs.append({
                            'id': f"indeed_{title}",
                            'title': title.strip(),
                            'company': company.strip(),
                            'location': 'India',
                            'url': link,
                            'description': 'Indeed India Job',
                            'platform': 'Indeed India',
                            'posted_date': 'Recent',
                            'match_score': 0.7
                        })
                await page.close()
            except Exception as e:
                print(f"    Indeed error: {e}")
        return jobs

    def _cache_jobs(self, jobs: List[Dict]):
        os.makedirs('data', exist_ok=True)
        with open(self.jobs_cache_path, 'w') as f:
            json.dump(jobs, f, indent=2)

    def load_cached_jobs(self) -> List[Dict]:
        if os.path.exists(self.jobs_cache_path):
            with open(self.jobs_cache_path, 'r') as f:
                return json.load(f)
        return []
