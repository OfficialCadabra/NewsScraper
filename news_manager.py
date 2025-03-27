import argparse
from article_fetcher import ArticleFetcher
from news_database import NewsDatabase
import os
from YahooFinanceStockScraper import YahooFinanceStockScraper
from datetime import datetime, timedelta

def scrape_and_store(ticker, days=30):
    """Scrape articles for a ticker and store them in the database"""
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates as strings
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_date_str = start_date.strftime('%Y-%m-%d')
    
    print(f"Scraping news for {ticker} from {start_date_str} to {end_date_str}")
    
    # Initialize scraper
    scraper = YahooFinanceStockScraper("Yahoo Finance", ticker, start_date_str, end_date_str)
    
    # Get article links
    links = scraper.get_pages()
    
    if not links:
        print("No articles found!")
        return False
    
    print(f"Found {len(links)} articles for {ticker}")
    
    # Create a fetcher and add articles to database
    fetcher = ArticleFetcher()
    
    success_count = 0
    for url in links:
        if fetcher.fetch_article(url, ticker):
            success_count += 1
    
    print(f"Successfully added {success_count} out of {len(links)} articles to the database")
    fetcher.close()
    
    return True

def list_articles(ticker, limit=10):
    """List articles for a ticker"""
    db = NewsDatabase()
    
    try:
        articles = db.get_articles_for_ticker(ticker, limit)
        
        if not articles:
            print(f"No articles found for {ticker}")
            return
        
        print(f"Showing {len(articles)} articles for {ticker}:")
        for article in articles:
            id, url, title, date_published, source, author, text, summary, sentiment = article
            
            # Format date
            if isinstance(date_published, str):
                date_str = date_published
            else:
                date_str = date_published.strftime('%Y-%m-%d') if date_published else 'Unknown'
            
            print(f"ID: {id} | {date_str} | {title}")
        
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description='Financial News Article Manager')
    
    subparsers = parser.add_subparsers(dest='command', help='command')
    
    # Scrape articles
    scrape_parser = subparsers.add_parser('scrape', help='Scrape and store articles')
    scrape_parser.add_argument('ticker', help='Ticker symbol')
    scrape_parser.add_argument('--days', '-d', type=int, default=30, help='Number of days to look back')
    
    # Process CSV
    csv_parser = subparsers.add_parser('csv', help='Process articles from a CSV file')
    csv_parser.add_argument('file', help='CSV file path')
    csv_parser.add_argument('ticker', help='Ticker symbol')
    
    # List articles
    list_parser = subparsers.add_parser('list', help='List articles for a ticker')
    list_parser.add_argument('ticker', help='Ticker symbol')
    list_parser.add_argument('--limit', '-l', type=int, default=10, help='Maximum number of articles to show')
    
    args = parser.parse_args()
    
    if args.command == 'scrape':
        scrape_and_store(args.ticker, args.days)
    elif args.command == 'csv':
        if not os.path.exists(args.file):
            print(f"Error: File {args.file} does not exist")
            return
        
        fetcher = ArticleFetcher()
        try:
            fetcher.fetch_articles_from_csv(args.file, args.ticker)
        finally:
            fetcher.close()
    elif args.command == 'list':
        list_articles(args.ticker, args.limit)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
