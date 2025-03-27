from datetime import datetime, timedelta
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def scrape_yahoo_finance_stock_news(ticker):
    """A simplified function to scrape Yahoo Finance stock news"""
    
    # Initialize Chrome driver
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service)
    
    # Navigate to the stock page
    url = f'https://au.finance.yahoo.com/quote/{ticker}'
    print(f"Navigating to {url}")
    browser.get(url)
    
    # Wait for page to load
    time.sleep(5)
    
    # Get page source and parse with BeautifulSoup
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    
    # Find all news links
    links = []
    
    # Find the news panel
    news_panel = soup.find('div', id='tabpanel-news')
    if news_panel:
        # Find all links in the news panel
        for link in news_panel.find_all('a'):
            href = link.get('href')
            if href and '/news/' in href:
                if href not in links:
                    links.append(href)
    
    browser.close()
    
    # Save links to CSV
    with open(f"{ticker}_links.csv", "w") as f:
        f.write("article_link\n")
        for link in links:
            f.write(f"{link}\n")
    
    print(f"Found {len(links)} news articles for {ticker}")
    for i, link in enumerate(links[:5], 1):
        print(f"{i}. {link}")
    
    print(f"Saved links to {ticker}_links.csv")
    
    return links

if __name__ == "__main__":
    ticker = "WOW.AX"  # Woolworths on ASX
    scrape_yahoo_finance_stock_news(ticker)
