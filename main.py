from selenium.common.exceptions import WebDriverException
from browser_controller import create_driver
from scraper import scrape_google_maps
from config import (
    MIN_RATING, REQUIRE_NO_WEBSITE, SEARCH_TERMS, 
    LOCATIONS, MAX_RESULTS, OUTPUT_FILE, 
    MIN_DELAY, MAX_DELAY, MAX_RETRIES
)
import pandas as pd
import time
import logging
import random
import sys
from datetime import datetime
from pathlib import Path

def setup_logging():
    """Configure logging with timestamp and both file/console output"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    log_filename = logs_dir / f'scraper_{timestamp}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

def save_results(businesses, output_file):
    """Save scraped data to CSV file and backup"""
    try:
        df = pd.DataFrame(businesses)
        
        # Additional data cleaning and validation
        df = df.drop_duplicates()
        df = df.dropna(subset=['name', 'address'])  # Remove entries without crucial info
        
        # Reorder and select columns
        column_order = [
            'name', 'category', 'rating', 'reviews_count',
            'address', 'phone', 'website', 'location',
            'price_level', 'hours'
        ]
        df = df.reindex(columns=[col for col in column_order if col in df.columns])
        
        # Create backup before saving
        backup_file = f"{output_file}.backup"
        if Path(output_file).exists():
            Path(output_file).rename(backup_file)
        
        df.to_csv(output_file, index=False, encoding='utf-8')
        logging.info(f"Successfully saved {len(df)} records to {output_file}")
    except Exception as e:
        logging.error(f"Failed to save results: {str(e)}")
        raise

def scrape_with_retry(driver, term, location, max_retries=MAX_RETRIES):
    """Implement retry logic for scraping"""
    for attempt in range(max_retries):
        try:
            businesses = scrape_google_maps(driver, term, location, MAX_RESULTS)
            return businesses
        except WebDriverException as e:
            if attempt < max_retries - 1:
                logging.warning(f"Attempt {attempt + 1} failed, retrying... Error: {str(e)}")
                time.sleep(random.uniform(MIN_DELAY * 2, MAX_DELAY * 2))
                continue
            raise
    return []

def main():
    setup_logging()
    logging.info(f"Starting scraper version 1.1")
    
    driver = None
    all_businesses = []
    start_time = time.time()
    
    try:
        driver = create_driver()
        
        for location in LOCATIONS:
            for term in SEARCH_TERMS:
                try:
                    logging.info(f"Scraping: {term} in {location}")
                    businesses = scrape_with_retry(driver, term, location)
                    
                    if businesses:
                        all_businesses.extend(businesses)
                        logging.info(f"Found {len(businesses)} results")
                    else:
                        logging.warning(f"No results found for {term} in {location}")
                    
                    delay = random.uniform(MIN_DELAY, MAX_DELAY)
                    logging.debug(f"Waiting {delay:.2f} seconds before next search")
                    time.sleep(delay)
                    
                except Exception as e:
                    logging.error(f"Error processing {term} in {location}: {str(e)}")
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
        
        elapsed_time = time.time() - start_time
        logging.info(f"Scraping completed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"Critical error: {str(e)}")
        sys.exit(1)