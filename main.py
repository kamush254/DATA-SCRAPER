from selenium.common.exceptions import WebDriverException
from browser_controller import create_driver
from scraper import scrape_google_maps
from config import MIN_RATING, REQUIRE_NO_WEBSITE
from config import SEARCH_TERMS, LOCATIONS, MAX_RESULTS, OUTPUT_FILE
import pandas as pd
import time
import logging
import random
import sys
from datetime import datetime

def setup_logging():
    """Configure logging with timestamp and both file/console output"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'scraper_{timestamp}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

def save_results(businesses, output_file):
    """Save scraped data to CSV file"""
    try:
        df = pd.DataFrame(businesses)
        
        # Reorder columns for better readability
        column_order = ['name', 'category', 'rating', 'address', 'phone', 'website', 'location']
        df = df.reindex(columns=column_order)
        
        df.to_csv(output_file, index=False)
        logging.info(f"Successfully saved {len(df)} records to {output_file}")
    except Exception as e:
        logging.error(f"Failed to save results: {str(e)}")
        raise
def main():
    setup_logging()
    logging.info("Starting scraper...")
    
    driver = None
    all_businesses = []
    
    try:
        driver = create_driver()
        
        for location in LOCATIONS:
            for term in SEARCH_TERMS:
                try:
                    logging.info(f"Scraping: {term} in {location}")
                    businesses = scrape_google_maps(driver, term, location, MAX_RESULTS)
                    
                    if businesses:
                        all_businesses.extend(businesses)
                        logging.info(f"Found {len(businesses)} results")
                    else:
                        logging.warning(f"No results found for {term} in {location}")
                    
                    # Add delay between searches
                    delay = random.uniform(2.0, 5.0)
                    logging.debug(f"Waiting {delay:.2f} seconds before next search")
                    time.sleep(delay)
                    
                except WebDriverException as e:
                    logging.error(f"WebDriver error for {term} in {location}: {str(e)}")
                    continue
                except Exception as e:
                    logging.error(f"Unexpected error for {term} in {location}: {str(e)}")
                    continue
        
        if all_businesses:
            save_results(all_businesses, OUTPUT_FILE)
        else:
            logging.warning("No data was collected during the scraping process")
            
    except Exception as e:
        logging.error(f"Fatal error in main process: {str(e)}")
        raise
    
    finally:
        if driver:
            try:
                driver.quit()
                logging.info("Browser closed successfully")
            except Exception as e:
                logging.error(f"Error closing browser: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"Critical error: {str(e)}")
        sys.exit(1)