from browser_controller import create_driver
from scraper import scrape_google_maps
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_scraper():
    driver = None
    try:
        setup_logging()
        logging.info("Starting test scrape...")
        
        driver = create_driver()
        results = scrape_google_maps(
            driver=driver,
            query="restaurants",
            location="Westlands Nairobi",
            max_results=5
        )
        
        if results:
            print(f"\nFound {len(results)} businesses:")
            for business in results:
                print(f"\nName: {business['name']}")
                print(f"Address: {business['address']}")
                print("-" * 50)
        else:
            print("\nNo businesses found!")
            
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_scraper()