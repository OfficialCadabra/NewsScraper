import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.parser import parse
from newspaper import Article
from NewspaperScraper import NewspaperScraper, NewspaperScraperWithAuthentication


class MarketWatchScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')

        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service)
        links = []
        stop = False
        index = 1

        while not stop:
            browser.get('https://www.marketwatch.com/search?q=' 
                        + self.searchTerm 
                        + '&m=Keyword&rpp=100'
                        + '&mp=' + str(index)
                        + '&bd=false&bd=false'
                        + '&bd=' + self.dateStart.strftime('%m/%d/%Y')
                        + '&ed=' + self.dateEnd.strftime('%m/%d/%Y')
                        + '&ts=0')
            
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            results = soup.find_all('div', class_='searchresult')
            
            if not results:
                stop = True
                continue
                
            for result in results:
                date_element = result.find('span', class_='deemphasized')
                if date_element:
                    pub_date = date_element.get_text().strip()
                    if self.check_dates(pub_date):
                        link_element = result.find('a', class_='link')
                        if link_element:
                            ltext = link_element.get('href')
                            if ltext not in links:
                                print(ltext)
                                links.append(ltext)
                    else:
                        stop = True
                        break
            
            index += 1
            time.sleep(sleep_time)
        
        browser.close()
        self.links = links
        return links


class YahooFinanceScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')
        
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service)
        links = []
        stop = False
        start_date_unix = int(datetime.combine(self.dateStart, datetime.min.time()).timestamp())
        end_date_unix = int(datetime.combine(self.dateEnd, datetime.max.time()).timestamp())
        
        browser.get('https://finance.yahoo.com/search?q=' + self.searchTerm)
        
        # Click on News tab
        try:
            tabs = browser.find_elements(By.CSS_SELECTOR, '.SearchTabs_root li')
            for tab in tabs:
                if 'News' in tab.text:
                    tab.click()
                    time.sleep(2)
                    break
        except:
            pass
            
        last_height = browser.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_attempts = 20
        
        while not stop and scroll_attempts < max_attempts:
            # Scroll down
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(sleep_time)
            
            # Get current page content
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            articles = soup.find_all('div', {'data-test': 'article'})
            
            for article in articles:
                time_element = article.find('span', {'data-test': 'article-timestamp'})
                if not time_element:
                    continue
                    
                # Extract timestamp and convert to date
                timestamp_text = time_element.get_text()
                current_date = datetime.now()
                
                if 'minute' in timestamp_text:
                    minutes = int(re.search(r'(\d+)', timestamp_text).group(1))
                    pub_date = current_date - timedelta(minutes=minutes)
                elif 'hour' in timestamp_text:
                    hours = int(re.search(r'(\d+)', timestamp_text).group(1))
                    pub_date = current_date - timedelta(hours=hours)
                elif 'day' in timestamp_text:
                    days = int(re.search(r'(\d+)', timestamp_text).group(1))
                    pub_date = current_date - timedelta(days=days)
                else:
                    try:
                        pub_date = datetime.strptime(timestamp_text, '%B %d, %Y')
                    except:
                        continue
                
                if self.check_dates(pub_date.strftime('%Y-%m-%d')):
                    link_element = article.find('a')
                    if link_element:
                        ltext = link_element.get('href')
                        if not ltext.startswith('http'):
                            ltext = 'https://finance.yahoo.com' + ltext
                        if ltext not in links:
                            print(ltext)
                            links.append(ltext)
                else:
                    oldest_date_found = pub_date.strftime('%Y-%m-%d')
                    if pub_date < self.dateStart:
                        stop = True
                        break
            
            # Check if we've reached the bottom
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
                last_height = new_height
        
        browser.close()
        self.links = links
        return links


class BarronsScraperWithAuthentication(NewspaperScraperWithAuthentication):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')
        
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service)
        links = []
        stop = False
        page = 1
        
        # Login first
        browser.get(self.login_url)
        time.sleep(3)
        
        # Fill in credentials
        cred_keys = list(self.credentials.keys())
        browser.find_element(By.ID, cred_keys[0]).send_keys(self.credentials[cred_keys[0]])
        browser.find_element(By.ID, cred_keys[1]).send_keys(self.credentials[cred_keys[1]])
        browser.find_element(By.ID, self.submit_id).click()
        time.sleep(10)  # Wait for login to complete
        
        # Now search for articles
        while not stop:
            search_url = ('https://www.barrons.com/search?keyword=' + self.searchTerm +
                         '&page=' + str(page) +
                         '&min-date=' + self.dateStart.strftime('%Y/%m/%d') +
                         '&max-date=' + self.dateEnd.strftime('%Y/%m/%d'))
            
            browser.get(search_url)
            time.sleep(sleep_time)
            
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            results = soup.find_all('article', class_='SearchResult')
            
            if not results:
                stop = True
                continue
                
            for result in results:
                date_element = result.find('p', class_='SearchResult-time')
                if date_element:
                    pub_date = date_element.get_text().strip()
                    if self.check_dates(pub_date):
                        link_element = result.find('h3', class_='SearchResult-headline').find('a')
                        if link_element:
                            ltext = link_element.get('href')
                            if ltext not in links:
                                print(ltext)
                                links.append(ltext)
                    else:
                        stop = True
                        break
            
            page += 1
            
        browser.close()
        self.links = links
        return links
        
    def __init__(self, newspaper, searchTerm, dateStart, dateEnd, userID, password):
        NewspaperScraperWithAuthentication.__init__(self, newspaper, searchTerm, dateStart, dateEnd, userID, password)
        # Set Barrons-specific login parameters
        self.credentials = {
            'username': userID,
            'password': password
        }
        self.login_url = 'https://accounts.barrons.com/login'
        self.submit_id = 'password-submit'


class FinancialTimesScraper(NewspaperScraperWithAuthentication):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')
        
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service)
        links = []
        stop = False
        page = 1
        
        # Login first
        browser.get(self.login_url)
        time.sleep(3)
        
        # Fill in credentials
        browser.find_element(By.ID, 'email').send_keys(self.credentials['email'])
        browser.find_element(By.ID, 'password').send_keys(self.credentials['password'])
        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(10)  # Wait for login to complete
        
        # Now search for articles
        while not stop:
            # Format for FT's search
            from_date = self.dateStart.strftime('%Y-%m-%d')
            to_date = self.dateEnd.strftime('%Y-%m-%d')
            
            search_url = (f'https://www.ft.com/search?q={self.searchTerm}'
                         f'&dateTo={to_date}&dateFrom={from_date}&page={page}')
            
            browser.get(search_url)
            time.sleep(sleep_time)
            
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            results = soup.find_all('li', class_='o-teaser')
            
            if not results:
                stop = True
                continue
                
            for result in results:
                date_element = result.find('div', class_='o-teaser__timestamp')
                if date_element:
                    pub_date = date_element.get_text().strip()
                    if self.check_dates(pub_date):
                        link_element = result.find('a', class_='js-teaser-heading-link')
                        if link_element:
                            ltext = 'https://www.ft.com' + link_element.get('href')
                            if ltext not in links:
                                print(ltext)
                                links.append(ltext)
                    else:
                        stop = True
                        break
            
            page += 1
            
        browser.close()
        self.links = links
        return links
        
    def __init__(self, newspaper, searchTerm, dateStart, dateEnd, userID, password):
        NewspaperScraperWithAuthentication.__init__(self, newspaper, searchTerm, dateStart, dateEnd, userID, password)
        # Set FT-specific login parameters
        self.credentials = {
            'email': userID,
            'password': password
        }
        self.login_url = 'https://accounts.ft.com/login'


class SeekingAlphaScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')
        
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service)
        links = []
        stop = False
        page = 1
        
        while not stop:
            browser.get('https://seekingalpha.com/search?q=' + self.searchTerm + '&page=' + str(page))
            time.sleep(sleep_time)
            
            # Select Articles tab if on first page
            if page == 1:
                try:
                    tabs = browser.find_elements(By.CSS_SELECTOR, '.tabs__tab-label')
                    for tab in tabs:
                        if 'Articles' in tab.text:
                            tab.click()
                            time.sleep(2)
                            break
                except:
                    pass
            
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            results = soup.find_all('li', class_='search-pages-result')
            
            if not results:
                stop = True
                continue
                
            for result in results:
                date_element = result.find('span', class_='search-result-date')
                if date_element:
                    pub_date = date_element.get_text().strip()
                    if self.check_dates(pub_date):
                        link_element = result.find('a', class_='search-result-title')
                        if link_element:
                            ltext = 'https://seekingalpha.com' + link_element.get('href')
                            if ltext not in links:
                                print(ltext)
                                links.append(ltext)
                    else:
                        stop = True
                        break
            
            page += 1
            
        browser.close()
        self.links = links
        return links


class ReutersFinanceScraper(NewspaperScraper):
    def get_pages(self, sleep_time=3):
        print('running get_pages()...')
        
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service)
        links = []
        stop = False
        
        # Reuters has a different search structure - we need to load all results by scrolling
        search_url = 'https://www.reuters.com/site-search/?query=' + self.searchTerm + '&sort=newest'
        browser.get(search_url)
        time.sleep(sleep_time)
        
        # Try to select "Business" category if available
        try:
            categories = browser.find_elements(By.CSS_SELECTOR, '.search-results__section-filter button')
            for cat in categories:
                if 'Business' in cat.text:
                    cat.click()
                    time.sleep(sleep_time)
                    break
        except:
            pass
            
        # Scroll down to load more results until we hit the date limit or no more results
        last_height = browser.execute_script("return document.body.scrollHeight")
        continue_scrolling = True
        scroll_count = 0
        max_scrolls = 50  # Set a limit to prevent infinite scrolling
        
        while continue_scrolling and scroll_count < max_scrolls:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(sleep_time)
            
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            
            # Check the date of the last article loaded
            results = soup.find_all('li', class_='search-results__item__22R6z')
            if results:
                last_result = results[-1]
                date_element = last_result.find('time')
                if date_element:
                    # Parse date
                    pub_date = date_element.get_text().strip()
                    try:
                        # Parse different possible date formats
                        if 'ago' in pub_date:
                            # Current date for relative dates like "1 hour ago"
                            pub_date = datetime.now().strftime('%Y-%m-%d')
                        else:
                            # Parse absolute dates
                            pub_date = parse(pub_date).strftime('%Y-%m-%d')
                            
                        # Check if we've gone past our start date
                        if parse(pub_date) < self.dateStart:
                            continue_scrolling = False
                    except:
                        pass
            
            # Check if we've reached the bottom or no new content is loading
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_count += 1
                # Wait a bit longer to see if more content loads
                time.sleep(2)
                if scroll_count >= 3:  # If we've waited for a while with no new content
                    continue_scrolling = False
            else:
                scroll_count = 0
                last_height = new_height
        
        # Now extract all the links within our date range
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        results = soup.find_all('li', class_='search-results__item__22R6z')
        
        for result in results:
            date_element = result.find('time')
            if date_element:
                pub_date = date_element.get_text().strip()
                try:
                    # Convert relative dates
                    if 'ago' in pub_date:
                        pub_date = datetime.now().strftime('%Y-%m-%d')
                    else:
                        pub_date = parse(pub_date).strftime('%Y-%m-%d')
                        
                    if self.check_dates(pub_date):
                        link_element = result.find('a')
                        if link_element:
                            ltext = 'https://www.reuters.com' + link_element.get('href')
                            if ltext not in links:
                                print(ltext)
                                links.append(ltext)
                except:
                    continue
                    
        browser.close()
        self.links = links
        return links
