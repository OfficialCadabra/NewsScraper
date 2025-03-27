from FinancialNewsScraper import YahooFinanceScraper
from dateutil.parser import parse
from datetime import datetime, timedelta
import os
import traceback

def run_example():
    try:
        # Use yesterday to today as the date range
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        # Format dates as strings
        end_date = today.strftime('%Y-%m-%d')
        start_date = yesterday.strftime('%Y-%m-%d')
        
        # Create the scraper for Yahoo Finance
        search_term = "Microsoft"
        print(f"Searching Yahoo Finance for '{search_term}' from {start_date} to {end_date}")
        
        scraper = YahooFinanceScraper("Yahoo Finance", search_term, start_date, end_date)
        
        # Get article links
        links = scraper.get_pages()
        print(f"Found {len(links)} articles")
        
        # Parse articles (limit to 3 for test)
        scraper.links = links[:3] if len(links) > 3 else links
        articles = scraper.newspaper_parser()
        
        # Save to CSV
        if articles:
            output_file = f"yahoo_finance_{search_term.lower()}_{start_date}.csv"
            scraper.write_to_csv(articles, output_file)
            print(f"Data saved to {output_file}")
        else:
            print("No articles were successfully parsed")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_example()
