import sys
import os
from article_fetcher import ArticleFetcher

def process_csv(csv_file, ticker_symbol):
    """Process a CSV file of article URLs"""
    
    if not os.path.exists(csv_file):
        print(f"Error: File {csv_file} does not exist")
        return False
    
    fetcher = ArticleFetcher()
    
    try:
        print(f"Processing articles for {ticker_symbol} from {csv_file}")
        success, failed = fetcher.fetch_articles_from_csv(csv_file, ticker_symbol)
        
        print(f"Processing complete. Successfully added {success} articles, {failed} failed.")
        return True
    except Exception as e:
        print(f"Error processing CSV: {e}")
        return False
    finally:
        fetcher.close()

def main():
    if len(sys.argv) < 3:
        print("Usage: python process_articles.py <csv_file> <ticker_symbol>")
        print("Example: python process_articles.py WOW.AX_links.csv WOW.AX")
        return
    
    csv_file = sys.argv[1]
    ticker_symbol = sys.argv[2]
    
    process_csv(csv_file, ticker_symbol)

if __name__ == "__main__":
    main()
