from datetime import datetime, timedelta
import time
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.parser import parse
from newspaper import Article
from NewspaperScraper import NewspaperScraper

class YahooFinanceStockScraper(NewspaperScraper):
    """A specialized scraper for Yahoo Finance stock news"""
    
    def __init__(self, newspaper, ticker, dateStart, dateEnd):
        """
        Initialize with a stock ticker instead of a search term
        
        Args:
            newspaper (str): Name of the news source (e.g., 'Yahoo Finance')
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'WOW.AX')
            dateStart (str): Start date in format YYYY-MM-DD
            dateEnd (str): End date in format YYYY-MM-DD
        """
        super().__init__(newspaper, ticker, dateStart, dateEnd)
        self.ticker = ticker
        
    def get_pages(self, sleep_time=3):
        print(f'running get_pages() for ticker {self.ticker}...')
        
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service)
        links = []
        
        # Go directly to the stock quote page
        quote_url = f'https://au.finance.yahoo.com/quote/{self.ticker}'
        browser.get(quote_url)
        
        print(f"Loaded quote page for {self.ticker}")
        time.sleep(sleep_time)
        
        # Find the News tab content
        try:
            # Wait for the news panel to load
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "tabpanel-news"))
            )
            
            # Get all story items
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            news_panel = soup.find('div', id='tabpanel-news')
            
            if news_panel:
                # Find all story items - trying multiple selectors
                story_items = news_panel.find_all('section', attrs={'data-testid': 'storyitem'})
                
                print(f"Found {len(story_items)} news articles")
                
                for story in story_items:
                    # Try multiple ways to find the link
                    link_element = None
                    
                    # Method 1: Look for the title link
                    link_element = story.find('a', class_='subtle-link fin-size-small titles noUnderline')
                    
                    # Method 2: Try any a tag with 'subtle-link' class
                    if not link_element:
                        link_element = story.find('a', class_='subtle-link')
                    
                    # Method 3: Try any a tag
                    if not link_element:
                        link_element = story.find('a')
                    
                    if link_element and link_element.get('href'):
                        article_url = link_element.get('href')
                        print(f"Found article URL: {article_url}")
                        
                        # Default - include all articles regardless of date
                        include_article = True
                        
                        # Try to get the date
                        date_element = story.find('div', class_='publishing')
                        if date_element:
                            date_text = date_element.get_text().strip()
                            print(f"Found date text: {date_text}")
                            
                            # Extract the time ago part (after the "•" symbol)
                            if "•" in date_text:
                                time_ago = date_text.split("•")[1].strip()
                                
                                # Try to convert relative time to date
                                try:
                                    current_date = datetime.now()
                                    
                                    if 'minute' in time_ago:
                                        minutes = int(re.search(r'(\d+)', time_ago).group(1))
                                        pub_date = current_date - timedelta(minutes=minutes)
                                    elif 'hour' in time_ago:
                                        hours = int(re.search(r'(\d+)', time_ago).group(1))
                                        pub_date = current_date - timedelta(hours=hours)
                                    elif 'day' in time_ago:
                                        days = int(re.search(r'(\d+)', time_ago).group(1))
                                        pub_date = current_date - timedelta(days=days)
                                    elif 'month' in time_ago:
                                        months = int(re.search(r'(\d+)', time_ago).group(1))
                                        # Approximate months as 30 days
                                        pub_date = current_date - timedelta(days=30*months)
                                    elif 'year' in time_ago:
                                        years = int(re.search(r'(\d+)', time_ago).group(1))
                                        # Approximate years as 365 days
                                        pub_date = current_date - timedelta(days=365*years)
                                    else:
                                        # Default to current date if format not recognized
                                        pub_date = current_date
                                    
                                    print(f"Parsed date: {pub_date}, Looking for range {self.dateStart} to {self.dateEnd}")
                                    
                                    # Check if date is within our range
                                    if pub_date.date() >= self.dateStart.date() and pub_date.date() <= self.dateEnd.date():
                                        print(f"Date is within range")
                                        include_article = True
                                    else:
                                        print(f"Article date out of range: {time_ago}")
                                        # For now, include all articles as we're debugging
                                        include_article = True
                                except Exception as e:
                                    print(f"Error parsing date '{time_ago}': {e}")
                                    # If we can't parse the date, include the article anyway
                                    include_article = True
                        
                        if include_article and article_url not in links:
                            print(f"Adding article: {article_url}")
                            links.append(article_url)
        except Exception as e:
            print(f"Error extracting news: {e}")
            import traceback
            traceback.print_exc()
        
        browser.close()
        print(f"Found {len(links)} articles for {self.ticker}")
        self.links = links
        return links
