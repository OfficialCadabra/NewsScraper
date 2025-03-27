import sqlite3
import os
from datetime import datetime

class NewsDatabase:
    def __init__(self, db_name='financial_news.db'):
        """Initialize the database connection"""
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()
        
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        # Table for storing ticker information
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickers (
            id INTEGER PRIMARY KEY,
            symbol TEXT UNIQUE,
            name TEXT,
            exchange TEXT,
            last_updated TIMESTAMP
        )
        ''')
        
        # Table for storing article information
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY,
            ticker_id INTEGER,
            url TEXT UNIQUE,
            title TEXT,
            date_published TIMESTAMP,
            source TEXT,
            author TEXT,
            text TEXT,
            summary TEXT,
            sentiment REAL,
            fetch_date TIMESTAMP,
            FOREIGN KEY (ticker_id) REFERENCES tickers (id)
        )
        ''')
        
        # Create indexes for faster lookups
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker_symbol ON tickers (symbol)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_article_url ON articles (url)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_article_ticker ON articles (ticker_id)')
        
        self.conn.commit()
    
    def add_ticker(self, symbol, name=None, exchange=None):
        """Add a ticker to the database"""
        now = datetime.now()
        try:
            self.cursor.execute(
                'INSERT OR REPLACE INTO tickers (symbol, name, exchange, last_updated) VALUES (?, ?, ?, ?)',
                (symbol, name, exchange, now)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def get_ticker_id(self, symbol):
        """Get the ID for a ticker symbol"""
        self.cursor.execute('SELECT id FROM tickers WHERE symbol = ?', (symbol,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None
    
    def add_article(self, ticker_symbol, url, title, date_published, source, author, text, summary=None, sentiment=None):
        """Add an article to the database"""
        # Get or create ticker ID
        ticker_id = self.get_ticker_id(ticker_symbol)
        if not ticker_id:
            ticker_id = self.add_ticker(ticker_symbol)
            if not ticker_id:
                return False
        
        # Add the article
        fetch_date = datetime.now()
        
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO articles 
            (ticker_id, url, title, date_published, source, author, text, summary, sentiment, fetch_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ticker_id, url, title, date_published, source, author, text, summary, sentiment, fetch_date))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def url_exists(self, url):
        """Check if an article URL already exists in the database"""
        self.cursor.execute('SELECT id FROM articles WHERE url = ?', (url,))
        return self.cursor.fetchone() is not None
    
    def get_articles_for_ticker(self, ticker_symbol, limit=None):
        """Get all articles for a specific ticker"""
        ticker_id = self.get_ticker_id(ticker_symbol)
        if not ticker_id:
            return []
        
        query = 'SELECT id, url, title, date_published, source, author, text, summary, sentiment FROM articles WHERE ticker_id = ? ORDER BY date_published DESC'
        if limit:
            query += f' LIMIT {int(limit)}'
        
        self.cursor.execute(query, (ticker_id,))
        return self.cursor.fetchall()
    
    def get_article_by_url(self, url):
        """Get an article by its URL"""
        self.cursor.execute(
            'SELECT id, url, title, date_published, source, author, text, summary, sentiment FROM articles WHERE url = ?', 
            (url,)
        )
        return self.cursor.fetchone()
    
    def search_articles(self, query, limit=10):
        """Search for articles containing the query in title or text"""
        search_param = f"%{query}%"
        self.cursor.execute('''
        SELECT a.id, a.url, a.title, a.date_published, a.source, a.author, a.text, a.summary, t.symbol
        FROM articles a
        JOIN tickers t ON a.ticker_id = t.id
        WHERE a.title LIKE ? OR a.text LIKE ?
        ORDER BY a.date_published DESC
        LIMIT ?
        ''', (search_param, search_param, limit))
        
        return self.cursor.fetchall()
    
    def get_ticker_stats(self, ticker_symbol):
        """Get statistics about articles for a ticker"""
        ticker_id = self.get_ticker_id(ticker_symbol)
        if not ticker_id:
            return None
        
        self.cursor.execute('''
        SELECT 
            COUNT(*) as article_count,
            MIN(date_published) as oldest_article,
            MAX(date_published) as newest_article,
            AVG(sentiment) as avg_sentiment
        FROM articles 
        WHERE ticker_id = ?
        ''', (ticker_id,))
        
        return self.cursor.fetchone()
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
