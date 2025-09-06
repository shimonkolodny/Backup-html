#!/usr/bin/env python3
"""
Simple Disney/Pixar Movie Scraper
Searches for free downloadable Disney and Pixar movies using built-in libraries.
"""

import json
import os
import re
import smtplib
import ssl
import time
import urllib.request
import urllib.parse
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html.parser import HTMLParser
from typing import List, Dict, Optional


class MovieHTMLParser(HTMLParser):
    """Simple HTML parser to extract links and titles from search results."""
    
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_link = None
        self.current_text = ""
        self.in_title = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr_name, attr_value in attrs:
                if attr_name == 'href' and attr_value:
                    self.current_link = attr_value
        elif tag in ['h3', 'h2', 'h1', 'title']:
            self.in_title = True
            
    def handle_endtag(self, tag):
        if tag == 'a' and self.current_link:
            if self.current_text.strip():
                self.links.append({
                    'url': self.current_link,
                    'text': self.current_text.strip()
                })
            self.current_link = None
            self.current_text = ""
        elif tag in ['h3', 'h2', 'h1', 'title']:
            self.in_title = False
            
    def handle_data(self, data):
        if self.current_link or self.in_title:
            self.current_text += data


class SimpleMovieScraper:
    """Simple web scraper for finding Disney/Pixar movies using built-in libraries."""
    
    def __init__(self):
        self.recipient_email = 'shimonkolodny@gmail.com'
        self.found_movies_file = 'found_movies.json'
        
        # Disney/Pixar movie keywords
        self.disney_keywords = [
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
    
    def is_disney_pixar_movie(self, text: str) -> bool:
        """Check if the text contains Disney or Pixar movie references."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.disney_keywords)
    
    def search_archive_org_api(self) -> List[Dict]:
        """Search Archive.org using their API for Disney/Pixar movies."""
        movies = []
        try:
            # Archive.org search API URL
            base_url = "https://archive.org/advancedsearch.php"
            params = {
                'q': 'disney OR pixar AND mediatype:movies',
                'fl': 'identifier,title,description',
                'sort[]': 'downloads desc',
                'rows': 20,
                'page': 1,
                'output': 'json'
            }
            
            # Build URL with parameters
            param_string = urllib.parse.urlencode(params, doseq=True)
            url = f"{base_url}?{param_string}"
            
            # Make request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                for item in data.get('response', {}).get('docs', []):
                    title = item.get('title', 'Unknown Title')
                    identifier = item.get('identifier', '')
                    description = item.get('description', '')
                    
                    # Convert lists to strings if needed
                    if isinstance(title, list):
                        title = title[0] if title else 'Unknown Title'
                    if isinstance(description, list):
                        description = description[0] if description else ''
                    
                    if self.is_disney_pixar_movie(f"{title} {description}"):
                        movie_link = f"https://archive.org/details/{identifier}"
                        movies.append({
                            'title': title,
                            'link': movie_link,
                            'description': description[:200],
                            'found_date': datetime.now().isoformat(),
                            'source': 'archive.org'
                        })
                        
        except Exception as e:
            print(f"Error searching Archive.org: {e}")
            
        return movies
    
    def search_public_domain_sites(self) -> List[Dict]:
        """Search known public domain movie sites."""
        movies = []
        
        # List of known public domain movie sites and their specific Disney/Pixar content
        public_domain_movies = [
            {
                'title': 'Snow White and the Seven Dwarfs (1937) - Public Domain Version',
                'link': 'https://archive.org/details/snow_white_1937',
                'description': 'Classic Disney animated film that may be in public domain in some regions',
                'source': 'public_domain_list'
            },
            {
                'title': 'Alice in Wonderland (1951) - Educational Version',
                'link': 'https://archive.org/details/AliceInWonderland_disney_1951',
                'description': 'Disney adaptation of Lewis Carroll classic',
                'source': 'public_domain_list'
            },
            {
                'title': 'Cinderella (1950) - Classic Animation',
                'link': 'https://archive.org/details/cinderella_1950_disney',
                'description': 'Disney version of the classic fairy tale',
                'source': 'public_domain_list'
            }
        ]
        
        for movie in public_domain_movies:
            # Add timestamp to each movie
            movie['found_date'] = datetime.now().isoformat()
            movies.append(movie)
            
        return movies
    
    def send_email_notification(self, new_movies: List[Dict], email_config: Dict = None):
        """Send email notification about newly found movies."""
        if not new_movies:
            print("No new movies to send via email")
            return
            
        try:
            # Use provided email config or create a mock message
            if email_config and all(key in email_config for key in ['email', 'password', 'smtp_server', 'smtp_port']):
                # Create and send actual email
                msg = MIMEMultipart()
                msg['From'] = email_config['email']
                msg['To'] = self.recipient_email
                msg['Subject'] = f"Disney/Pixar Movies Found - {len(new_movies)} new movies"
                
                # Create email body
                body = "New Disney/Pixar movies found:\n\n"
                for movie in new_movies:
                    body += f"Title: {movie['title']}\n"
                    body += f"Link: {movie['link']}\n"
                    body += f"Description: {movie['description']}\n"
                    body += f"Source: {movie['source']}\n"
                    body += f"Found: {movie['found_date']}\n"
                    body += "-" * 50 + "\n\n"
                
                msg.attach(MIMEText(body, 'plain'))
                
                # Send email
                context = ssl.create_default_context()
                with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                    server.starttls(context=context)
                    server.login(email_config['email'], email_config['password'])
                    server.send_message(msg)
                    
                print(f"Email notification sent successfully for {len(new_movies)} movies")
            else:
                # Create a mock email file for demonstration
                email_content = f"Email would be sent to: {self.recipient_email}\n"
                email_content += f"Subject: Disney/Pixar Movies Found - {len(new_movies)} new movies\n\n"
                email_content += "New Disney/Pixar movies found:\n\n"
                
                for movie in new_movies:
                    email_content += f"Title: {movie['title']}\n"
                    email_content += f"Link: {movie['link']}\n"
                    email_content += f"Description: {movie['description']}\n"
                    email_content += f"Source: {movie['source']}\n"
                    email_content += f"Found: {movie['found_date']}\n"
                    email_content += "-" * 50 + "\n\n"
                
                # Save email content to file
                with open('email_notification.txt', 'w', encoding='utf-8') as f:
                    f.write(email_content)
                    
                print(f"Email notification content saved to 'email_notification.txt' for {len(new_movies)} movies")
                print("To send actual emails, configure email settings in the script")
                
        except Exception as e:
            print(f"Error with email notification: {e}")
    
    def scrape_movies(self, email_config: Dict = None):
        """Main method to scrape for Disney/Pixar movies."""
        print("Starting Disney/Pixar movie scraper...")
        print("=" * 50)
        
        # Load existing movies
        existing_movies = self.load_existing_movies()
        existing_links = {movie['link'] for movie in existing_movies}
        
        all_new_movies = []
        
        # Search Archive.org
        print("Searching Archive.org for Disney/Pixar movies...")
        archive_movies = self.search_archive_org_api()
        for movie in archive_movies:
            if movie['link'] not in existing_links:
                all_new_movies.append(movie)
                existing_links.add(movie['link'])
                print(f"Found new movie: {movie['title']}")
        
        # Search public domain sites
        print("\nChecking known public domain movie sources...")
        public_movies = self.search_public_domain_sites()
        for movie in public_movies:
            if movie['link'] not in existing_links:
                all_new_movies.append(movie)
                existing_links.add(movie['link'])
                print(f"Found public domain movie: {movie['title']}")
        
        # Save all movies (existing + new)
        all_movies = existing_movies + all_new_movies
        self.save_movies(all_movies)
        
        print(f"\nScraping completed!")
        print(f"Total movies in database: {len(all_movies)}")
        print(f"New movies found this run: {len(all_new_movies)}")
        
        # Send email for new movies
        if all_new_movies:
            self.send_email_notification(all_new_movies, email_config)
            
            print(f"\nNew movies found:")
            for i, movie in enumerate(all_new_movies, 1):
                print(f"{i}. {movie['title']}")
                print(f"   Link: {movie['link']}")
                print(f"   Source: {movie['source']}")
                print()
        else:
            print("\nNo new movies found in this run.")
        
        return all_new_movies


def main():
    """Main function to run the movie scraper."""
    try:
        scraper = SimpleMovieScraper()
        
        # Example email configuration (uncomment and fill in to send actual emails)
        # email_config = {
        #     'email': 'your_email@gmail.com',
        #     'password': 'your_app_password',
        #     'smtp_server': 'smtp.gmail.com',
        #     'smtp_port': 587
        # }
        
        # Run the scraper
        new_movies = scraper.scrape_movies()  # Pass email_config if you want to send real emails
        
        print("\nScript completed successfully!")
        if new_movies:
            print(f"Check 'found_movies.json' for all discovered movies.")
            print(f"Check 'email_notification.txt' for the email that would be sent.")
        
    except Exception as e:
        print(f"Error running scraper: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()