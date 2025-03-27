import sys
from pymongo import MongoClient
from NewspaperScraper import NewspaperScraper
from FinancialNewsScraper import (
    MarketWatchScraper,
    YahooFinanceScraper,
    BarronsScraperWithAuthentication,
    FinancialTimesScraper,
    SeekingAlphaScraper,
    ReutersFinanceScraper
)

try:
    client = MongoClient()
    db = client.Financial_News_database
    mongodb_available = True
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    print("CSV output will be used instead")
    mongodb_available = False


def run_scraper(scraper):
    """
    Run the scraper workflow: get pages, parse articles, and store in MongoDB or CSV
    """
    print(f"Starting scraper for {scraper.get_newspaper_name()}...")
    scraper.get_pages()
    data = scraper.newspaper_parser()
    
    if not data:
        print(f"No articles found or parsed for {scraper.get_newspaper_name()}")
        return
    
    if mongodb_available:
        collection_name = f"articles_{scraper.searchTerm.replace(' ', '_').lower()}"
        scraper.write_to_mongo(data, db[collection_name])
    else:
        file_name = f"{scraper.get_newspaper_name().replace(' ', '_').lower()}_{scraper.searchTerm.replace(' ', '_').lower()}.csv"
        scraper.write_to_csv(data, file_name)
    
    print(f"Completed scraper for {scraper.get_newspaper_name()}. Found {len(data)} articles.")


def initialize_financial_scraper(args):
    """
    Initialize the appropriate scraper based on command line arguments
    
    Usage: python RunFinancialScrapers.py [news_source] [search_term] [start_date] [end_date] [username] [password]
    
    Username and password are only required for Barrons and Financial Times
    """
    if len(args) < 5:
        print("Usage: python RunFinancialScrapers.py [news_source] [search_term] [start_date] [end_date] [username] [password]")
        print("Username and password are only required for Barrons and Financial Times")
        return
        
    source = args[1]
    search_term = args[2]
    start_date = args[3]
    end_date = args[4]
    
    if source == "MarketWatch":
        run_scraper(MarketWatchScraper(source, search_term, start_date, end_date))
    elif source == "Yahoo Finance":
        run_scraper(YahooFinanceScraper(source, search_term, start_date, end_date))
    elif source == "Seeking Alpha":
        run_scraper(SeekingAlphaScraper(source, search_term, start_date, end_date))
    elif source == "Reuters Finance":
        run_scraper(ReutersFinanceScraper(source, search_term, start_date, end_date))
    elif source == "Barrons" and len(args) >= 7:
        run_scraper(BarronsScraperWithAuthentication(source, search_term, start_date, end_date, args[5], args[6]))
    elif source == "Financial Times" and len(args) >= 7:
        run_scraper(FinancialTimesScraper(source, search_term, start_date, end_date, args[5], args[6]))
    else:
        print(f"Error: {source} is either not supported or requires username/password")
        print("Supported sources: MarketWatch, Yahoo Finance, Seeking Alpha, Reuters Finance, Barrons*, Financial Times*")
        print("* Requires login credentials")


def run_all_financial_scrapers(search_term, start_date, end_date, barrons_creds=None, ft_creds=None):
    """
    Run all available financial news scrapers with the same search parameters
    
    Args:
        search_term (str): Term to search for
        start_date (str): Start date in format YYYY-MM-DD
        end_date (str): End date in format YYYY-MM-DD
        barrons_creds (tuple): Optional (username, password) for Barrons
        ft_creds (tuple): Optional (username, password) for Financial Times
    """
    scrapers = [
        MarketWatchScraper("MarketWatch", search_term, start_date, end_date),
        YahooFinanceScraper("Yahoo Finance", search_term, start_date, end_date),
        SeekingAlphaScraper("Seeking Alpha", search_term, start_date, end_date),
        ReutersFinanceScraper("Reuters Finance", search_term, start_date, end_date)
    ]
    
    # Add authenticated scrapers if credentials are provided
    if barrons_creds:
        scrapers.append(BarronsScraperWithAuthentication(
            "Barrons", search_term, start_date, end_date, barrons_creds[0], barrons_creds[1]
        ))
    
    if ft_creds:
        scrapers.append(FinancialTimesScraper(
            "Financial Times", search_term, start_date, end_date, ft_creds[0], ft_creds[1]
        ))
    
    for scraper in scrapers:
        try:
            run_scraper(scraper)
        except Exception as e:
            print(f"Error with {scraper.get_newspaper_name()} scraper: {str(e)}")
            continue


if __name__ == "__main__":
    initialize_financial_scraper(sys.argv)
