import time
import random
from newspaper import Article
from datetime import datetime
from news_database import NewsDatabase

class ArticleFetcher:
    def __init__(self, db_path='financial_news.db'):
        """Initialize the ArticleFetcher with a database connection"""
        self.db = NewsDatabase(db_path)
        
    def fetch_article(self, url, ticker_symbol, sleep_time=2):
        """Fetch and parse an article from the given URL"""
        print(f"Fetching article: {url}")
        
        # Check if article already exists in the database
        if self.db.url_exists(url):
            print(f"Article already exists in database: {url}")
            return False
        
        # Add a random delay to avoid rate limiting
        time.sleep(sleep_time + random.uniform(0, 1))
        
        try:
            # Use newspaper3k to download and parse the article
            article = Article(url)
            article.download()
            article.parse()
            
            # Get NLP analysis
            try:
                article.nlp()
                summary = article.summary
            except:
                summary = None
            
            # Extract information
            title = article.title
            text = article.text
            date_published = article.publish_date or datetime.now()
            authors = ', '.join(article.authors) if article.authors else 'Unknown'
            
            # Extract source from URL
            source = 'Unknown'
            if 'yahoo.com' in url:
                source = 'Yahoo Finance'
            elif 'bloomberg.com' in url:
                source = 'Bloomberg'
            elif 'reuters.com' in url:
                source = 'Reuters'
            elif 'marketwatch.com' in url:
                source = 'MarketWatch'
            elif 'seekingalpha.com' in url:
                source = 'Seeking Alpha'
            elif 'ft.com' in url:
                source = 'Financial Times'
            
            # Add to database
            success = self.db.add_article(
                ticker_symbol=ticker_symbol,
                url=url,
                title=title,
                date_published=date_published,
                source=source,
                author=authors,
                text=text,
                summary=summary,
                sentiment=None  # We'll add sentiment analysis in a future update
            )
            
            if success:
                print(f"Successfully added article: {title}")
                return True
            else:
                print(f"Failed to add article to database")
                return False
                
        except Exception as e:
            print(f"Error fetching article {url}: {e}")
            return False
    
    def fetch_articles_from_csv(self, csv_file, ticker_symbol):
        """Fetch all articles from a CSV file of URLs"""
        import csv
        
        success_count = 0
        fail_count = 0
        
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            
            for row in reader:
                if not row:
                    continue
                    
                url = row[0]
                if self.fetch_article(url, ticker_symbol):
                    success_count += 1
                else:
                    fail_count += 1
        
        print(f"Completed fetching articles. Success: {success_count}, Failed: {fail_count}")
        return success_count, fail_count
    
    def close(self):
        """Close the database connection"""
        self.db.close()
