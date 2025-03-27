import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.parser import parse
from newspaper import Article
from NewspaperScraper import NewspaperScraper

class FinancialStockScraper:
    """
    A facade class that coordinates scraping stock news from multiple sources
    """
    
    def __init__(self, ticker, start_date=None, end_date=None):
        """
        Initialize the stock scraper with a ticker and optional date range
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'WOW.AX')
            start_date (str, optional): Start date in format YYYY-MM-DD. Defaults to 30 days ago.
            end_date (str, optional): End date in format YYYY-MM-DD. Defaults to today.
        """
        self.ticker = ticker
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
        self.start_date = start_date
        self.end_date = end_date
        self.results = {}
    
    def scrape_yahoo_finance(self):
        """Scrape news from Yahoo Finance"""
        print(f"Scraping Yahoo Finance for {self.ticker}...")
        
        scraper = YahooFinanceStockScraper("Yahoo Finance", self.ticker, self.start_date, self.end_date)
        links = scraper.get_pages()
        
        self.results["Yahoo Finance"] = {
            "links": links,
            "count": len(links)
        }
        
        return links
    
    def scrape_marketwatch(self):
        """Scrape news from MarketWatch (simplified implementation)"""
        print(f"Scraping MarketWatch for {self.ticker}...")
        
        links = []
        try:
            service = Service(ChromeDriverManager().install())
            browser = webdriver.Chrome(service=service)
            
            # MarketWatch uses different URL format for stocks
            # Extract the ticker without exchange suffix if any
            base_ticker = self.ticker.split('.')[0]
            
            # Try different URL formats
            urls_to_try = [
                f"https://www.marketwatch.com/investing/stock/{base_ticker}/news",
                f"https://www.marketwatch.com/investing/stock/{self.ticker}/news"
            ]
            
            # For Australian stocks, try ASX format
            if '.AX' in self.ticker:
                urls_to_try.append(f"https://www.marketwatch.com/investing/stock/{base_ticker}?countrycode=au")
            
            success = False
            for url in urls_to_try:
                browser.get(url)
                time.sleep(3)
                
                # Check if we landed on a valid page
                if "not found" not in browser.title.lower():
                    success = True
                    break
            
            if success:
                # Find news articles
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                articles = soup.find_all('div', class_='element--article')
                
                for article in articles:
                    link_element = article.find('a', class_='link')
                    if link_element:
                        link = link_element.get('href')
                        if link not in links:
                            print(f"Found MarketWatch article: {link}")
                            links.append(link)
            
            browser.close()
        except Exception as e:
            print(f"Error scraping MarketWatch: {e}")
        
        self.results["MarketWatch"] = {
            "links": links,
            "count": len(links)
        }
        
        return links
    
    def scrape_all_sources(self):
        """Scrape news from all available sources"""
        self.scrape_yahoo_finance()
        self.scrape_marketwatch()
        
        # Combine all results
        all_links = []
        for source, data in self.results.items():
            all_links.extend(data["links"])
        
        return all_links
    
    def save_results_to_csv(self, filename=None):
        """Save all collected links to a CSV file"""
        if not filename:
            filename = f"{self.ticker}_stock_news_{self.start_date}_to_{self.end_date}.csv"
            filename = filename.replace('-', '')
        
        print(f"Saving results to {filename}")
        
        with open(filename, 'w') as f:
            f.write("source,article_link\n")
            
            for source, data in self.results.items():
                for link in data["links"]:
                    f.write(f"{source},{link}\n")
        
        return filename
    
    def print_summary(self):
        """Print a summary of results"""
        print("\n===== SCRAPING RESULTS =====")
        print(f"Stock: {self.ticker}")
        print(f"Date range: {self.start_date} to {self.end_date}")
        print("----------------------------")
        
        total = 0
        for source, data in self.results.items():
            count = data["count"]
            total += count
            print(f"{source}: {count} articles")
        
        print("----------------------------")
        print(f"Total: {total} articles")
        print("=============================\n")


# Import Yahoo Finance stock scraper implementation
from YahooFinanceStockScraper import YahooFinanceStockScraper
