import re
import csv
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.parser import parse
from newspaper import Article


class NewspaperScraper:
    def __init__ (self, newspaper, searchTerm, dateStart, dateEnd):
        self.newspaper = newspaper
        self.searchTerm = searchTerm
        self.dateStart = parse(dateStart)
        self.dateEnd = parse(dateEnd)
        self.links = []

    def get_newspaper_name (self):
        return self.newspaper

    def get_pages (self):
        print('Unimplemented for ' + self.newspaper + ' scraper')
        return

    def check_dates (self, date):
        page_date = parse(date)
        if page_date >= self.dateStart and page_date <= self.dateEnd:
            return True
        return False

    def newspaper_parser (self, sleep_time=0):
        print('running newspaper_parser()...')

        results = []
        count = 0

        for l in self.links:
            article = Article(url=l)
            try:
                article.build()
            except:
                time.sleep(60)
                continue

            data = {
                'title': article.title,
                'date_published': article.publish_date,
                'news_outlet': self.newspaper,
                'authors': article.authors,
                'feature_img': article.top_image,
                'article_link': article.canonical_link,
                'keywords': article.keywords,
                'movies': article.movies,
                'summary': article.summary,
                'text': article.text,
                'html': article.html
            }

            print(data['title'])
            print(data['text'])
            print()
            print()
            results.append(data)

            count += 1
            print(count)
            time.sleep(sleep_time)

        return results

    def write_to_csv (self, data, file_name):
        print('writing to CSV...')

        keys = data[0].keys()
        with open(file_name, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)

    def write_to_mongo (self, data, collection):
        print('writing to mongoDB...')
        count = 0

        for d in data:
            collection.insert_one(d)
            count += 1
            print(count)


class NewspaperScraperWithAuthentication(NewspaperScraper):
    def __init__ (self, newspaper, searchTerm, dateStart, dateEnd, userID, password):
        NewspaperScraper.__init__(self, newspaper, searchTerm, dateStart, dateEnd)
        self.userId = userID
        self.password = password
