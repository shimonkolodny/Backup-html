#!/usr/bin/env python3
"""
Automated runner for the Disney/Pixar Movie Scraper
Can be used for scheduled/automated runs (cron jobs, etc.)
"""

import os
import sys
import logging
from datetime import datetime
from simple_movie_scraper import SimpleMovieScraper


def setup_logging():
    """Setup logging for the automated runner."""
    log_filename = f"scraper_log_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def load_email_config():
    """Load email configuration from .env file."""
    if not os.path.exists('.env'):
        return None
    
    config = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
        
        email_config = {
            'email': config.get('EMAIL_ADDRESS'),
            'password': config.get('EMAIL_PASSWORD'),
            'smtp_server': config.get('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(config.get('EMAIL_SMTP_PORT', 587))
        }
        
        # Validate required fields
        if email_config['email'] and email_config['password']:
            return email_config
        else:
            return None
            
    except Exception as e:
        logging.error(f"Error loading email configuration: {e}")
        return None


def run_automated_scraper():
    """Run the scraper in automated mode."""
    logger = setup_logging()
    logger.info("Starting automated Disney/Pixar movie scraper run")
    
    try:
        # Load email configuration
        email_config = load_email_config()
        if email_config:
            logger.info("Email configuration loaded - email notifications enabled")
        else:
            logger.info("No email configuration found - running in preview mode")
        
        # Create and run scraper
        scraper = SimpleMovieScraper()
        new_movies = scraper.scrape_movies(email_config)
        
        # Log results
        if new_movies:
            logger.info(f"SUCCESS: Found {len(new_movies)} new Disney/Pixar movies")
            for movie in new_movies:
                logger.info(f"  - {movie['title']} ({movie['source']})")
            
            if email_config:
                logger.info(f"Email notification sent to shimonkolodny@gmail.com")
            else:
                logger.info("Email preview saved to email_notification.txt")
        else:
            logger.info("No new movies found in this run")
        
        logger.info("Automated scraper run completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"ERROR: Automated scraper run failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = run_automated_scraper()
    sys.exit(0 if success else 1)