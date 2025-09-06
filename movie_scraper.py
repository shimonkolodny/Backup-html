#!/usr/bin/env python3
"""
Disney/Pixar Movie Scraper for Zyte
Searches for free downloadable Disney and Pixar movies and sends email notifications.
"""

import json
import os
import re
import smtplib
import ssl
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class MovieScraper:
    """Web scraper for finding free downloadable Disney/Pixar movies."""
    
    def __init__(self):
        load_dotenv()
        self.recipient_email = os.getenv('RECIPIENT_EMAIL', 'shimonkolodny@gmail.com')
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        
        self.search_keywords = os.getenv('SEARCH_KEYWORDS', 'disney pixar movies free download')
        self.max_results = int(os.getenv('MAX_RESULTS_PER_SEARCH', '10'))
        self.search_delay = int(os.getenv('SEARCH_DELAY_SECONDS', '2'))
        
        self.found_movies_file = 'found_movies.json'
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def load_existing_movies(self) -> List[Dict]:
        """Load previously found movies from JSON file."""
        if os.path.exists(self.found_movies_file):
            try:
                with open(self.found_movies_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_movies(self, movies: List[Dict]):
        """Save found movies to JSON file."""
        with open(self.found_movies_file, 'w', encoding='utf-8') as f:
            json.dump(movies, f, indent=2, ensure_ascii=False)
    
    def is_disney_pixar_movie(self, title: str, description: str = "") -> bool:
        """Check if the content is likely a Disney or Pixar movie."""
        disney_keywords = [
            'disney', 'pixar', 'walt disney', 'disney pictures', 'pixar animation',
            'toy story', 'finding nemo', 'monsters inc', 'cars', 'up',
            'frozen', 'moana', 'coco', 'incredibles', 'lion king',
            'beauty and the beast', 'little mermaid', 'aladdin', 'pocahontas',
            'mulan', 'tarzan', 'hercules', 'bambi', 'dumbo', 'cinderella',
            'snow white', 'sleeping beauty', 'jungle book', 'peter pan',
            'lady and the tramp', 'alice in wonderland', 'pinocchio',
            'brave', 'inside out', 'ratatouille', 'wall-e', 'finding dory',
            'good dinosaur', 'onward', 'soul', 'luca', 'encanto', 'turning red'
        ]
        
        text = f"{title} {description}".lower()
        return any(keyword in text for keyword in disney_keywords)
    
    def extract_movie_info(self, element) -> Optional[Dict]:
        """Extract movie information from a search result element."""
        try:
            title_element = element.find_element(By.TAG_NAME, "h3")
            title = title_element.text.strip() if title_element else "Unknown Title"
            
            link_element = element.find_element(By.TAG_NAME, "a")
            link = link_element.get_attribute("href") if link_element else ""
            
            description_elements = element.find_elements(By.TAG_NAME, "span")
            description = " ".join([elem.text for elem in description_elements[:2]])
            
            if self.is_disney_pixar_movie(title, description):
                return {
                    'title': title,
                    'link': link,
                    'description': description,
                    'found_date': datetime.now().isoformat(),
                    'source': 'search_engine'
                }
        except Exception as e:
            print(f"Error extracting movie info: {e}")
        
        return None
    
    def search_google(self, query: str) -> List[Dict]:
        """Search Google for movies with the given query."""
        movies = []
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            self.driver.get(search_url)
            time.sleep(self.search_delay)
            
            # Find search result elements
            search_results = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
            
            for result in search_results[:self.max_results]:
                movie_info = self.extract_movie_info(result)
                if movie_info:
                    movies.append(movie_info)
                    
        except Exception as e:
            print(f"Error searching Google: {e}")
            
        return movies
    
    def search_archive_org(self) -> List[Dict]:
        """Search Archive.org for Disney/Pixar movies."""
        movies = []
        try:
            # Archive.org search API
            search_url = "https://archive.org/advancedsearch.php"
            params = {
                'q': 'disney OR pixar AND mediatype:movies',
                'fl': 'identifier,title,description,downloads,item_size',
                'sort[]': 'downloads desc',
                'rows': self.max_results,
                'page': 1,
                'output': 'json'
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('response', {}).get('docs', []):
                    title = item.get('title', ['Unknown'])[0] if isinstance(item.get('title'), list) else item.get('title', 'Unknown')
                    identifier = item.get('identifier', '')
                    description = item.get('description', [''])[0] if isinstance(item.get('description'), list) else item.get('description', '')
                    
                    if self.is_disney_pixar_movie(title, description):
                        movie_link = f"https://archive.org/details/{identifier}"
                        movies.append({
                            'title': title,
                            'link': movie_link,
                            'description': description,
                            'found_date': datetime.now().isoformat(),
                            'source': 'archive.org'
                        })
                        
        except Exception as e:
            print(f"Error searching Archive.org: {e}")
            
        return movies
    
    def send_email_notification(self, new_movies: List[Dict]):
        """Send email notification about newly found movies."""
        if not new_movies or not self.email_address or not self.email_password:
            print("No new movies found or email credentials not configured")
            return
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = self.recipient_email
            msg['Subject'] = f"Disney/Pixar Movies Found - {len(new_movies)} new movies"
            
            # Create email body
            body = "New Disney/Pixar movies found:\n\n"
            for movie in new_movies:
                body += f"Title: {movie['title']}\n"
                body += f"Link: {movie['link']}\n"
                body += f"Description: {movie['description'][:200]}...\n"
                body += f"Source: {movie['source']}\n"
                body += f"Found: {movie['found_date']}\n"
                body += "-" * 50 + "\n\n"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
                
            print(f"Email notification sent successfully for {len(new_movies)} movies")
            
        except Exception as e:
            print(f"Error sending email: {e}")
    
    def scrape_movies(self):
        """Main method to scrape for Disney/Pixar movies."""
        print("Starting Disney/Pixar movie scraper...")
        
        # Load existing movies
        existing_movies = self.load_existing_movies()
        existing_links = {movie['link'] for movie in existing_movies}
        
        all_new_movies = []
        
        # Search different sources
        search_queries = [
            f"{self.search_keywords} filetype:mp4",
            f"{self.search_keywords} archive.org",
            f"{self.search_keywords} public domain",
            "disney movies free legal download",
            "pixar movies free legal download"
        ]
        
        # Search Google with different queries
        for query in search_queries:
            print(f"Searching: {query}")
            movies = self.search_google(query)
            for movie in movies:
                if movie['link'] not in existing_links:
                    all_new_movies.append(movie)
                    existing_links.add(movie['link'])
            time.sleep(self.search_delay)
        
        # Search Archive.org
        print("Searching Archive.org...")
        archive_movies = self.search_archive_org()
        for movie in archive_movies:
            if movie['link'] not in existing_links:
                all_new_movies.append(movie)
                existing_links.add(movie['link'])
        
        # Save all movies (existing + new)
        all_movies = existing_movies + all_new_movies
        self.save_movies(all_movies)
        
        # Send email for new movies
        if all_new_movies:
            print(f"Found {len(all_new_movies)} new movies")
            self.send_email_notification(all_new_movies)
        else:
            print("No new movies found")
        
        return all_new_movies
    
    def close(self):
        """Close the WebDriver."""
        if hasattr(self, 'driver'):
            self.driver.quit()


def main():
    """Main function to run the movie scraper."""
    scraper = None
    try:
        scraper = MovieScraper()
        new_movies = scraper.scrape_movies()
        
        print(f"\nScraping completed!")
        print(f"New movies found: {len(new_movies)}")
        
        if new_movies:
            print("\nNew movies:")
            for movie in new_movies:
                print(f"- {movie['title']}: {movie['link']}")
                
    except Exception as e:
        print(f"Error running scraper: {e}")
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()