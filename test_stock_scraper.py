from YahooFinanceStockScraper import YahooFinanceStockScraper
from datetime import datetime, timedelta
import os
import traceback

def test_stock_scraper():
    """Test the Yahoo Finance stock scraper with an ASX stock"""
    
    try:
        # Use a 30-day range
        today = datetime.now()
        month_ago = today - timedelta(days=30)
        
        # Format dates as strings
        end_date = today.strftime('%Y-%m-%d')
        start_date = month_ago.strftime('%Y-%m-%d')
        
        # Use Woolworths ASX ticker
        ticker = "WOW.AX"
        print(f"Fetching news for {ticker} from {start_date} to {end_date}")
        
        # Initialize the scraper
        scraper = YahooFinanceStockScraper("Yahoo Finance", ticker, start_date, end_date)
        
        # Get the article links
        links = scraper.get_pages()
        
        # Print results
        print(f"\nFound {len(links)} articles for {ticker}")
        if links:
            print("\nFirst few articles:")
            for i, link in enumerate(links[:5]):
                print(f"{i+1}. {link}")
        
        # Save results to CSV
        if links:
            with open(f"{ticker}_links.csv", "w") as f:
                f.write("article_link\n")
                for link in links:
                    f.write(f"{link}\n")
            print(f"\nSaved links to {ticker}_links.csv")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Yahoo Finance Stock Scraper...")
    success = test_stock_scraper()
    if success:
        print("\nStock scraper test completed successfully!")
    else:
        print("\nStock scraper test failed!")
