#!/bin/bash
# Sample cron job script for the Disney/Pixar Movie Scraper
# 
# To schedule this to run daily at 9 AM, add this line to your crontab:
# 0 9 * * * /path/to/Backup-html/cron_scraper.sh
#
# To edit your crontab: crontab -e

# Change to the script directory
cd "$(dirname "$0")"

# Activate virtual environment if you have one
# source venv/bin/activate

# Run the automated scraper
python3 run_scraper.py

# Optional: Clean up old log files (keep last 7 days)
find . -name "scraper_log_*.log" -mtime +7 -delete

# Optional: Backup found movies to a timestamped file weekly
if [ $(date +%u) -eq 1 ]; then  # Monday
    cp found_movies.json "backups/found_movies_$(date +%Y%m%d).json" 2>/dev/null || true
fi