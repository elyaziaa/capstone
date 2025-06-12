#!/usr/bin/env python3
"""
Modern LeetCode Problems Scraper
Based on Bishalsarang/Leetcode-Questions-Scraper approach
Updated for current LeetCode website structure
"""

import requests
import json
import time
import os
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import argparse
from colorama import init, Fore, Style
from datetime import datetime

# Initialize colorama for colored output
init(autoreset=True)

class LeetCodeScraper:
    def __init__(self, max_problems=10, difficulty=None):
        self.max_problems = max_problems
        self.difficulty = difficulty.upper() if difficulty else None
        self.api_url = "https://leetcode.com/api/problems/algorithms/"
        self.base_url = "https://leetcode.com/problems/"
        self.driver = None
        self.problems_data = []
        self.track_file = "track.conf"
        self.output_file = "leetcode_problems.html"
        self.pickle_file = "problems.pickle"
        
        # Setup Chrome driver
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome WebDriver with optimized options"""
        print(f"{Fore.YELLOW}🔧 Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print(f"{Fore.GREEN}✅ Chrome WebDriver initialized successfully")
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to initialize Chrome WebDriver: {e}")
            print(f"{Fore.YELLOW}💡 Make sure you have Chrome and ChromeDriver installed")
            exit(1)
    
    def fetch_problems_list(self):
        """Fetch problems list from LeetCode API"""
        print(f"{Fore.YELLOW}📡 Fetching problems list from LeetCode API...")
        
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            problems = data.get('stat_status_pairs', [])
            print(f"{Fore.GREEN}✅ Found {len(problems)} total problems")
            
            return problems
        except requests.RequestException as e:
            print(f"{Fore.RED}❌ Failed to fetch problems list: {e}")
            return []
    
    def filter_problems(self, problems):
        """Filter problems by difficulty and limit"""
        filtered = []
        
        difficulty_map = {
            'EASY': 1,
            'MEDIUM': 2, 
            'HARD': 3
        }
        
        for problem in problems:
            stat = problem.get('stat', {})
            difficulty_level = problem.get('difficulty', {}).get('level', 0)
            
            # Skip paid problems
            if problem.get('paid_only', False):
                continue
                
            # Filter by difficulty if specified
            if self.difficulty and difficulty_level != difficulty_map.get(self.difficulty, 0):
                continue
                
            problem_data = {
                'id': stat.get('frontend_question_id'),
                'title': stat.get('question__title'),
                'title_slug': stat.get('question__title_slug'),
                'difficulty': list(difficulty_map.keys())[difficulty_level - 1] if difficulty_level > 0 else 'Unknown',
                'acceptance_rate': round(stat.get('total_acs', 0) * 100.0 / max(stat.get('total_submitted', 1), 1), 2),
                'url': f"{self.base_url}{stat.get('question__title_slug')}/",
                'content': None
            }
            
            filtered.append(problem_data)
            
            if len(filtered) >= self.max_problems:
                break
        
        return filtered
    
    def scrape_problem_content(self, problem):
        """Scrape individual problem content"""
        url = problem['url']
        print(f"{Fore.CYAN}🔍 Scraping: {problem['title']} ({problem['id']})")
        
        try:
            self.driver.get(url)
            
            # Wait for content to load
            wait = WebDriverWait(self.driver, 10)
            
            try:
                # Wait for problem description to load
                content_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                        "div[data-track-load='description_content'], .content__u3I1, .question-content"))
                )
                
                # Get the problem description
                description_selectors = [
                    "div[data-track-load='description_content']",
                    ".content__u3I1 .question-content",
                    ".question-content",
                    "[data-cy='question-detail-main-tabs'] div[role='tabpanel']",
                    ".elfjS"  # New selector
                ]
                
                description_html = None
                for selector in description_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            description_html = elements[0].get_attribute('innerHTML')
                            break
                    except:
                        continue
                
                if not description_html:
                    # Fallback: get page source and parse
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    
                    # Try different selectors
                    content_div = (soup.find('div', {'data-track-load': 'description_content'}) or
                                 soup.find('div', class_='content__u3I1') or
                                 soup.find('div', class_='question-content') or
                                 soup.find('div', class_='elfjS'))
                    
                    if content_div:
                        description_html = str(content_div)
                    else:
                        description_html = f"<p>Could not fetch content for {problem['title']}</p>"
                
                problem['content'] = description_html
                print(f"{Fore.GREEN}✅ Successfully scraped {problem['title']}")
                
                # Small delay to be respectful
                time.sleep(1)
                
            except TimeoutException:
                print(f"{Fore.RED}⏱️ Timeout while loading {problem['title']}")
                problem['content'] = f"<p>Timeout while loading {problem['title']}</p>"
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error scraping {problem['title']}: {str(e)}")
            problem['content'] = f"<p>Error loading {problem['title']}: {str(e)}</p>"
        
        return problem
    
    def load_progress(self):
        """Load scraping progress from track file"""
        if os.path.exists(self.track_file):
            try:
                with open(self.track_file, 'r') as f:
                    return int(f.read().strip())
            except:
                return 0
        return 0
    
    def save_progress(self, index):
        """Save scraping progress to track file"""
        with open(self.track_file, 'w') as f:
            f.write(str(index))
    
    def save_to_pickle(self):
        """Save problems data to pickle file"""
        with open(self.pickle_file, 'wb') as f:
            pickle.dump(self.problems_data, f)
        print(f"{Fore.GREEN}💾 Saved problems data to {self.pickle_file}")
    
    def generate_html(self):
        """Generate HTML file with all problems"""
        print(f"{Fore.YELLOW}📝 Generating HTML file...")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LeetCode Problems - {self.difficulty or 'All Difficulties'}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .stats {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin: 40px 0 20px 0;
            font-size: 2em;
        }}
        p {{
            background: white;
            margin: 15px 0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
            font-size: 1.1em;
            line-height: 1.7;
        }}
        .problem-meta {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        .difficulty {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.8em;
            margin-right: 10px;
        }}
        .difficulty.EASY {{ background-color: #d4edda; color: #155724; }}
        .difficulty.MEDIUM {{ background-color: #fff3cd; color: #856404; }}
        .difficulty.HARD {{ background-color: #f8d7da; color: #721c24; }}
        .url-link {{
            color: #007bff;
            text-decoration: none;
            font-weight: bold;
        }}
        .url-link:hover {{
            text-decoration: underline;
        }}
        code {{
            background-color: #f1f3f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #d73a49;
        }}
        pre {{
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            border: 1px solid #d0d7de;
            margin: 15px 0;
        }}
        .content-wrapper {{
            background: white;
            padding: 0;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 style="border: none; margin: 0; color: white;">🧠 LeetCode Problems Collection</h1>
        <p style="background: none; box-shadow: none; border: none; color: white; margin: 10px 0;">Difficulty: {self.difficulty or 'All'} | Total Problems: {len(self.problems_data)}</p>
        <p style="background: none; box-shadow: none; border: none; color: white; margin: 10px 0;">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats">
        <h3 style="margin-top: 0;">📊 Statistics</h3>
        <div class="problem-meta">
            <strong>Total Problems:</strong> {len(self.problems_data)}<br>
            <strong>Difficulty Filter:</strong> {self.difficulty or 'None (All difficulties)'}<br>
            <strong>Average Acceptance Rate:</strong> {sum(p['acceptance_rate'] for p in self.problems_data) / len(self.problems_data) if self.problems_data else 0:.1f}%
        </div>
    </div>
"""
        
        # Add each problem with h1 header and p content
        for i, problem in enumerate(self.problems_data, 1):
            # Clean and format the content
            content = problem['content'] or 'Content not available'
            
            # Remove any existing HTML tags that might interfere
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract just the text content and basic formatting
            if soup.get_text().strip():
                content = str(soup)
            else:
                content = f"Problem content for {problem['title']} could not be loaded."
            
            html_content += f"""
    <div class="content-wrapper">
        <h1>Problem {i}</h1>
        
        <div class="problem-meta">
            <span class="difficulty {problem['difficulty']}">{problem['difficulty']}</span>
            <strong>ID:</strong> {problem['id']} | 
            <strong>Title:</strong> {problem['title']} | 
            <strong>Acceptance:</strong> {problem['acceptance_rate']}% | 
            <a href="{problem['url']}" target="_blank" class="url-link">View on LeetCode →</a>
        </div>
        
        <p>{content}</p>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"{Fore.GREEN}✅ HTML file generated: {self.output_file}")
    
    def scrape(self):
        """Main scraping function"""
        print(f"{Fore.BLUE}🚀 Starting LeetCode Problems Scraper")
        print(f"{Fore.BLUE}📋 Target: {self.max_problems} {self.difficulty or 'ANY'} difficulty problems")
        
        # Fetch problems list from API
        all_problems = self.fetch_problems_list()
        if not all_problems:
            print(f"{Fore.RED}❌ No problems found")
            return
        
        # Filter problems
        filtered_problems = self.filter_problems(all_problems)
        print(f"{Fore.GREEN}🎯 Filtered to {len(filtered_problems)} problems")
        
        if not filtered_problems:
            print(f"{Fore.RED}❌ No problems match the criteria")
            return
        
        # Load progress
        start_index = self.load_progress()
        print(f"{Fore.YELLOW}📍 Starting from index {start_index}")
        
        # Scrape problems
        try:
            for i, problem in enumerate(filtered_problems[start_index:], start_index):
                print(f"{Fore.BLUE}📖 Progress: {i+1}/{len(filtered_problems)}")
                
                scraped_problem = self.scrape_problem_content(problem)
                self.problems_data.append(scraped_problem)
                
                # Save progress
                self.save_progress(i + 1)
                
                # Save intermediate results
                if (i + 1) % 5 == 0:
                    self.save_to_pickle()
                    print(f"{Fore.GREEN}💾 Intermediate save completed")
        
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}⏹️ Scraping interrupted by user")
        except Exception as e:
            print(f"{Fore.RED}❌ Scraping error: {e}")
        finally:
            # Final save
            self.save_to_pickle()
            self.generate_html()
            
            # Cleanup
            if self.driver:
                self.driver.quit()
            
            # Clean up track file on successful completion
            if len(self.problems_data) == len(filtered_problems):
                if os.path.exists(self.track_file):
                    os.remove(self.track_file)
                print(f"{Fore.GREEN}🎉 Scraping completed successfully!")
            
            print(f"{Fore.BLUE}📁 Files generated:")
            print(f"{Fore.BLUE}  • HTML: {self.output_file}")
            print(f"{Fore.BLUE}  • Pickle: {self.pickle_file}")

def main():
    parser = argparse.ArgumentParser(description='Modern LeetCode Problems Scraper')
    parser.add_argument('--difficulty', '-d', choices=['easy', 'medium', 'hard'], 
                       help='Filter by difficulty (easy/medium/hard)')
    parser.add_argument('--max-problems', '-n', type=int, default=10,
                       help='Maximum number of problems to scrape (default: 10)')
    parser.add_argument('--resume', '-r', action='store_true',
                       help='Resume from last saved progress')
    
    args = parser.parse_args()
    
    # Clear progress if not resuming
    if not args.resume and os.path.exists('track.conf'):
        os.remove('track.conf')
        print(f"{Fore.YELLOW}🔄 Starting fresh (not resuming)")
    
    scraper = LeetCodeScraper(
        max_problems=args.max_problems,
        difficulty=args.difficulty
    )
    
    try:
        scraper.scrape()
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}👋 Goodbye!")
    except Exception as e:
        print(f"{Fore.RED}💥 Fatal error: {e}")

if __name__ == "__main__":
    main()