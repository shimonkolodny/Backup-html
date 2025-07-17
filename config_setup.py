#!/usr/bin/env python3
"""
Configuration setup script for the Disney/Pixar Movie Scraper
"""

import os
import getpass
from simple_movie_scraper import SimpleMovieScraper


def setup_email_config():
    """Interactive setup for email configuration."""
    print("Disney/Pixar Movie Scraper - Email Configuration")
    print("=" * 50)
    
    email = input("Enter your email address: ").strip()
    if not email:
        print("Email address is required!")
        return None
    
    password = getpass.getpass("Enter your email password (app password for Gmail): ").strip()
    if not password:
        print("Password is required!")
        return None
    
    smtp_server = input("SMTP server (default: smtp.gmail.com): ").strip() or "smtp.gmail.com"
    smtp_port = input("SMTP port (default: 587): ").strip() or "587"
    
    try:
        smtp_port = int(smtp_port)
    except ValueError:
        print("Invalid port number, using default 587")
        smtp_port = 587
    
    return {
        'email': email,
        'password': password,
        'smtp_server': smtp_server,
        'smtp_port': smtp_port
    }


def test_email_config(email_config):
    """Test email configuration by sending a test email."""
    print("\nTesting email configuration...")
    
    # Create a test movie entry
    test_movie = [{
        'title': 'Test Movie - Configuration Check',
        'link': 'https://example.com/test',
        'description': 'This is a test email to verify your email configuration is working.',
        'source': 'configuration_test',
        'found_date': '2025-07-15T16:00:00.000000'
    }]
    
    scraper = SimpleMovieScraper()
    try:
        scraper.send_email_notification(test_movie, email_config)
        print("✓ Test email sent successfully!")
        return True
    except Exception as e:
        print(f"✗ Email test failed: {e}")
        return False


def save_env_file(email_config):
    """Save email configuration to .env file."""
    env_content = f"""# Email configuration for Disney/Pixar Movie Scraper
EMAIL_ADDRESS={email_config['email']}
EMAIL_PASSWORD={email_config['password']}
EMAIL_SMTP_SERVER={email_config['smtp_server']}
EMAIL_SMTP_PORT={email_config['smtp_port']}
RECIPIENT_EMAIL=shimonkolodny@gmail.com

# Scraper settings
SEARCH_KEYWORDS=disney pixar movies free download
MAX_RESULTS_PER_SEARCH=10
SEARCH_DELAY_SECONDS=2
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✓ Email configuration saved to .env file")


def run_scraper_with_email():
    """Run the movie scraper with email notifications enabled."""
    print("\nRunning Disney/Pixar movie scraper with email notifications...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("No .env file found. Please run setup first.")
        return
    
    # Load configuration from .env
    config = {}
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
    
    if not all([email_config['email'], email_config['password']]):
        print("Email configuration incomplete. Please run setup first.")
        return
    
    # Run the scraper
    scraper = SimpleMovieScraper()
    new_movies = scraper.scrape_movies(email_config)
    
    if new_movies:
        print(f"\n✓ Found {len(new_movies)} new movies and sent email notification!")
    else:
        print("\n• No new movies found this time.")


def main():
    """Main configuration menu."""
    while True:
        print("\nDisney/Pixar Movie Scraper - Configuration Menu")
        print("=" * 50)
        print("1. Setup email configuration")
        print("2. Test email configuration")
        print("3. Run scraper with email notifications")
        print("4. Run scraper without email (preview mode)")
        print("5. View current configuration")
        print("6. Exit")
        
        choice = input("\nSelect an option (1-6): ").strip()
        
        if choice == '1':
            email_config = setup_email_config()
            if email_config:
                save_env_file(email_config)
                print("\n✓ Email configuration completed!")
                
                # Ask if user wants to test
                test = input("\nWould you like to send a test email? (y/n): ").strip().lower()
                if test in ['y', 'yes']:
                    test_email_config(email_config)
        
        elif choice == '2':
            if os.path.exists('.env'):
                # Load and test existing configuration
                config = {}
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
                
                if all([email_config['email'], email_config['password']]):
                    test_email_config(email_config)
                else:
                    print("Email configuration not found. Please setup first.")
            else:
                print("No configuration found. Please setup first.")
        
        elif choice == '3':
            run_scraper_with_email()
        
        elif choice == '4':
            print("\nRunning scraper in preview mode (no emails sent)...")
            scraper = SimpleMovieScraper()
            new_movies = scraper.scrape_movies()
            if new_movies:
                print(f"\n✓ Found {len(new_movies)} new movies! Check email_notification.txt for preview.")
            else:
                print("\n• No new movies found this time.")
        
        elif choice == '5':
            if os.path.exists('.env'):
                print("\nCurrent configuration:")
                with open('.env', 'r') as f:
                    for line in f:
                        if not line.strip().startswith('#') and '=' in line:
                            key, value = line.strip().split('=', 1)
                            if 'PASSWORD' in key:
                                print(f"{key}=***hidden***")
                            else:
                                print(f"{key}={value}")
            else:
                print("No configuration file found.")
        
        elif choice == '6':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please select 1-6.")


if __name__ == "__main__":
    main()