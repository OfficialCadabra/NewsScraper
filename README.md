# Financial News Database System - Setup and Usage Guide

## System Overview
This system allows you to scrape financial news articles from Yahoo Finance and other sources, store them in a SQLite database, and browse/search the collected articles. It's particularly useful for tracking news about specific stocks over time.

## Setup Instructions (PowerShell)

```powershell
# Create project directory and navigate to it
New-Item -Path "C:\FinancialNewsDB" -ItemType Directory -Force
Set-Location -Path "C:\FinancialNewsDB"

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install required packages
pip install requests selenium beautifulsoup4 newspaper3k webdriver-manager python-dateutil

# Create the necessary files
# See detailed installation guide for all file contents
```

## File Structure
- `news_database.py` - Database interaction module
- `YahooFinanceStockScraper.py` - Scraper for Yahoo Finance stock news
- `article_fetcher.py` - Article fetching and parsing module
- `process_articles.py` - Process CSV files containing article URLs
- `browse_articles.py` - Browse and search stored articles
- `news_manager.py` - Combined functionality script

## Usage Instructions

### Scraping Articles
To scrape and store news articles for a specific stock:
```
python news_manager.py scrape WOW.AX --days 60
```

### Processing CSV Files
If you have a CSV file with article links:
```
python process_articles.py WOW.AX_links.csv WOW.AX
```

### Browsing Articles
List articles for a specific ticker:
```
python browse_articles.py list WOW.AX
```

Search for articles containing specific text:
```
python browse_articles.py search "earnings"
```

View a specific article by ID:
```
python browse_articles.py view --id 1
```

View statistics for a ticker:
```
python browse_articles.py stats WOW.AX
```

### Using the Batch File
For easier access, use the provided batch file:
```
run_news_manager.bat scrape WOW.AX
run_news_manager.bat browse list WOW.AX
run_news_manager.bat browse search "profit"
run_news_manager.bat process WOW.AX_links.csv WOW.AX
```

## Database Structure
The system uses SQLite with two main tables:
1. `tickers` - Stores ticker symbols and metadata
2. `articles` - Stores article content, metadata, and analysis

## Requirements
- Python 3.6+
- Chrome or Firefox browser (for Selenium)
- Internet connection

## Troubleshooting
- If the scraper fails to find articles, check the Yahoo Finance page structure
- If article parsing fails, ensure newspaper3k is properly installed
- For database errors, check file permissions in your directory

## Extensions
This system can be extended with:
- Sentiment analysis of articles
- Topic modeling to categorize articles
- Additional news sources
- Data visualization of news trends