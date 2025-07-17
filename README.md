# Disney/Pixar Movie Scraper

This repository contains a web scraper that searches for free downloadable Disney and Pixar movies and sends email notifications with the found links.

## Features

- Searches multiple sources for Disney/Pixar movies:
  - Archive.org API
  - Known public domain movie databases
  - Extensible for additional sources
- Sends email notifications to `shimonkolodny@gmail.com` with movie details
- Saves found movies to `found_movies.json` to avoid duplicates
- Tracks movie metadata including title, link, description, source, and discovery date

## Files

- `simple_movie_scraper.py` - Main scraper script using built-in Python libraries
- `movie_scraper.py` - Advanced scraper script (requires additional dependencies)
- `requirements.txt` - Python package dependencies
- `found_movies.json` - Database of discovered movies (auto-generated)
- `email_notification.txt` - Preview of email content (auto-generated)
- `.env.template` - Template for email configuration
- `.gitignore` - Git ignore rules

## Quick Start

### Using the Simple Scraper (Recommended)

The simple scraper uses only built-in Python libraries and works immediately:

```bash
python3 simple_movie_scraper.py
```

### Using the Advanced Scraper

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Run the scraper:
```bash
python3 movie_scraper.py
```

## Email Configuration

To send actual emails instead of generating preview files:

1. Copy the email template:
```bash
cp .env.template .env
```

2. Edit `.env` with your email credentials:
```
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
RECIPIENT_EMAIL=shimonkolodny@gmail.com
```

3. For Gmail, you'll need to:
   - Enable 2-factor authentication
   - Generate an app-specific password
   - Use the app password instead of your regular password

## Output

The scraper creates:

- `found_movies.json` - JSON database of all discovered movies
- `email_notification.txt` - Preview of what would be emailed (if email not configured)

### Sample Output

```json
[
  {
    "title": "Snow White and the Seven Dwarfs (1937) - Public Domain Version",
    "link": "https://archive.org/details/snow_white_1937",
    "description": "Classic Disney animated film that may be in public domain in some regions",
    "source": "public_domain_list",
    "found_date": "2025-07-15T16:09:18.505161"
  }
]
```

## How It Works

1. **Source Scanning**: The scraper searches multiple sources for Disney/Pixar content:
   - Archive.org's movie database via API
   - Curated list of known public domain movies
   - Can be extended to include additional sources

2. **Content Filtering**: Uses keyword matching to identify Disney/Pixar movies:
   - Studio names: Disney, Pixar, Walt Disney Pictures
   - Popular titles: Toy Story, Finding Nemo, Frozen, etc.
   - Classic titles: Snow White, Cinderella, Bambi, etc.

3. **Duplicate Prevention**: Maintains a database of previously found movies to avoid sending duplicate notifications

4. **Email Notifications**: Sends formatted emails with:
   - Movie title and description
   - Direct download/view link
   - Source information
   - Discovery timestamp

## Legal Note

This scraper only searches for movies that are:
- In the public domain
- Available through legitimate free sources
- Educational or promotional content

Users should verify the legal status of any content before downloading.

## Extending the Scraper

To add new movie sources, modify the `scrape_movies()` method to include additional search functions. Each search function should return a list of dictionaries with the required movie metadata format.

## Troubleshooting

- **Network Issues**: The scraper includes error handling for network timeouts
- **Missing Dependencies**: Use the simple scraper if package installation fails
- **Email Issues**: Check `.env` configuration and Gmail app password setup
- **No Movies Found**: The scraper may not find new content on every run