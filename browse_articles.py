import sys
from news_database import NewsDatabase
import argparse
from datetime import datetime
import textwrap

def format_article(article):
    """Format an article for display"""
    id, url, title, date_published, source, author, text, summary, sentiment = article
    
    # Format date
    if isinstance(date_published, str):
        date_str = date_published
    else:
        date_str = date_published.strftime('%Y-%m-%d') if date_published else 'Unknown'
    
    # Truncate and format text
    if text:
        truncated_text = textwrap.shorten(text, width=500, placeholder="...")
    else:
        truncated_text = "No text available"
    
    # Format sentiment
    sentiment_str = f"{sentiment:.2f}" if sentiment else "N/A"
    
    output = f"""
{'=' * 80}
ID: {id}
TITLE: {title}
DATE: {date_str}
SOURCE: {source}
AUTHOR: {author}
URL: {url}
SENTIMENT: {sentiment_str}

SUMMARY:
{summary if summary else 'No summary available'}

EXCERPT:
{truncated_text}
{'=' * 80}
"""
    return output

def list_articles(ticker=None, limit=10):
    """List articles from the database"""
    db = NewsDatabase()
    
    try:
        if ticker:
            articles = db.get_articles_for_ticker(ticker, limit)
            print(f"Showing up to {limit} articles for {ticker}:")
        else:
            print("Please specify a ticker symbol")
            return
            
        if not articles:
            print(f"No articles found for {ticker}")
            return
            
        for article in articles:
            print(format_article(article))
            
        print(f"Found {len(articles)} articles for {ticker}")
        
    finally:
        db.close()

def view_article(article_id=None, url=None):
    """View a specific article"""
    db = NewsDatabase()
    
    try:
        article = None
        if article_id:
            # This needs to be implemented in the NewsDatabase class
            db.cursor.execute(
                'SELECT id, url, title, date_published, source, author, text, summary, sentiment FROM articles WHERE id = ?',
                (article_id,)
            )
            article = db.cursor.fetchone()
        elif url:
            article = db.get_article_by_url(url)
            
        if not article:
            print(f"Article not found")
            return
            
        print(format_article(article))
        
    finally:
        db.close()

def search_articles(query, limit=10):
    """Search for articles containing a query"""
    db = NewsDatabase()
    
    try:
        results = db.search_articles(query, limit)
        
        if not results:
            print(f"No articles found matching '{query}'")
            return
            
        print(f"Search results for '{query}':")
        for article in results:
            id, url, title, date_published, source, author, text, summary, ticker = article
            # Format date
            if isinstance(date_published, str):
                date_str = date_published
            else:
                date_str = date_published.strftime('%Y-%m-%d') if date_published else 'Unknown'
                
            print(f"ID: {id} | {date_str} | {ticker} | {title}")
            
        print(f"\nFound {len(results)} articles matching '{query}'")
        print("Use 'view --id <ID>' to view a specific article")
        
    finally:
        db.close()

def show_ticker_stats(ticker):
    """Show statistics for a specific ticker"""
    db = NewsDatabase()
    
    try:
        stats = db.get_ticker_stats(ticker)
        
        if not stats:
            print(f"No data found for ticker {ticker}")
            return
            
        article_count, oldest_date, newest_date, avg_sentiment = stats
        
        # Format dates
        if isinstance(oldest_date, str):
            oldest_str = oldest_date
        else:
            oldest_str = oldest_date.strftime('%Y-%m-%d') if oldest_date else 'Unknown'
            
        if isinstance(newest_date, str):
            newest_str = newest_date
        else:
            newest_str = newest_date.strftime('%Y-%m-%d') if newest_date else 'Unknown'
        
        print(f"""
Statistics for {ticker}:
------------------------
Total articles: {article_count}
Date range: {oldest_str} to {newest_str}
Average sentiment: {avg_sentiment:.2f if avg_sentiment else 'N/A'}
""")
        
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description='Browse and search financial news articles')
    
    subparsers = parser.add_subparsers(dest='command', help='command')
    
    # List articles
    list_parser = subparsers.add_parser('list', help='List articles')
    list_parser.add_argument('ticker', help='Ticker symbol')
    list_parser.add_argument('--limit', '-l', type=int, default=10, help='Maximum number of articles to show')
    
    # View article
    view_parser = subparsers.add_parser('view', help='View a specific article')
    view_parser.add_argument('--id', type=int, help='Article ID')
    view_parser.add_argument('--url', help='Article URL')
    
    # Search articles
    search_parser = subparsers.add_parser('search', help='Search articles')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', '-l', type=int, default=10, help='Maximum number of results')
    
    # Show ticker stats
    stats_parser = subparsers.add_parser('stats', help='Show ticker statistics')
    stats_parser.add_argument('ticker', help='Ticker symbol')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_articles(args.ticker, args.limit)
    elif args.command == 'view':
        if args.id:
            view_article(article_id=args.id)
        elif args.url:
            view_article(url=args.url)
        else:
            print("Please specify either --id or --url")
    elif args.command == 'search':
        search_articles(args.query, args.limit)
    elif args.command == 'stats':
        show_ticker_stats(args.ticker)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
