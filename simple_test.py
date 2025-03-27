from FinancialNewsScraper import YahooFinanceScraper
from datetime import datetime, timedelta

def simple_test():
    """A simple test that doesn't require MongoDB"""
    
    # Use yesterday to today as the date range
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    # Format dates as strings
    end_date = today.strftime('%Y-%m-%d')
    start_date = yesterday.strftime('%Y-%m-%d')
    
    # Create the scraper for Yahoo Finance
    search_term = "Microsoft"
    print(f"Searching Yahoo Finance for '{search_term}' from {start_date} to {end_date}")
    
    try:
        # Initialize the scraper
        scraper = YahooFinanceScraper("Yahoo Finance", search_term, start_date, end_date)
        
        # Just get links (faster test)
        links = scraper.get_pages()
        
        print(f"Success! Found {len(links)} article links.")
        if links:
            print("First few links:")
            for link in links[:3]:
                print(f"- {link}")
        
        return True
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running simple test...")
    success = simple_test()
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed!")
