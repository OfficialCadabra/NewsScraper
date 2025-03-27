import sys
import argparse
from datetime import datetime, timedelta
from FinancialStockScraper import FinancialStockScraper

def parse_arguments():
    parser = argparse.ArgumentParser(description='Scrape financial news for a specific stock ticker')
    
    parser.add_argument('ticker', 
                        help='Stock ticker symbol (e.g., AAPL, WOW.AX)')
    
    parser.add_argument('--start-date', '-s', 
                        help='Start date in YYYY-MM-DD format (default: 30 days ago)')
    
    parser.add_argument('--end-date', '-e', 
                        help='End date in YYYY-MM-DD format (default: today)')
    
    parser.add_argument('--output', '-o',
                        help='Output CSV filename (default: {ticker}_stock_news_{dates}.csv)')
    
    parser.add_argument('--yahoo-only', action='store_true',
                        help='Only scrape from Yahoo Finance')
    
    parser.add_argument('--marketwatch-only', action='store_true',
                        help='Only scrape from MarketWatch')
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Initialize the stock scraper
    scraper = FinancialStockScraper(args.ticker, args.start_date, args.end_date)
    
    # Determine which sources to scrape
    if args.yahoo_only:
        scraper.scrape_yahoo_finance()
    elif args.marketwatch_only:
        scraper.scrape_marketwatch()
    else:
        scraper.scrape_all_sources()
    
    # Print summary and save results
    scraper.print_summary()
    output_file = scraper.save_results_to_csv(args.output)
    
    print(f"Saved results to {output_file}")

if __name__ == "__main__":
    main()
