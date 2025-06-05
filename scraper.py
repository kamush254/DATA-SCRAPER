from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import logging
from config import MIN_RATING, REQUIRE_NO_WEBSITE  # Import new configs

def wait_for_results(driver, timeout=20):
    """Wait for search results to load"""
    wait = WebDriverWait(driver, timeout)
    try:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd"))
        )
        return True
    except TimeoutException:
        return False

def extract_business_details(driver):
    """Extract details from business info panel"""
    details = {
        'name': 'N/A',
        'address': 'N/A',
        'phone': 'N/A',
        'website': 'N/A',
        'rating': '0.0'
    }
    
    try:
        # Extract name
        name_elem = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf"))
        )
        details['name'] = name_elem.text.strip()
    except (NoSuchElementException, TimeoutException):
        pass
    
    try:
        # Extract rating
        rating_elem = driver.find_element(By.CSS_SELECTOR, "div.F7nice > span:first-child")
        details['rating'] = rating_elem.get_attribute('aria-label').split()[0]
    except NoSuchElementException:
        pass
    
    try:
        # Extract address
        address_elem = driver.find_element(By.CSS_SELECTOR, "div[data-item-id='address']")
        details['address'] = address_elem.text.strip()
    except NoSuchElementException:
        pass
    
    try:
        # Extract phone
        phone_elem = driver.find_element(By.CSS_SELECTOR, "div[data-item-id*='phone'] button")
        details['phone'] = phone_elem.get_attribute('aria-label').replace('Phone: ', '')
    except NoSuchElementException:
        pass
    
    try:
        # Extract website
        website_elem = driver.find_element(By.CSS_SELECTOR, "a[data-item-id*='website']")
        details['website'] = website_elem.get_attribute('href')
    except NoSuchElementException:
        pass
    
    return details

def scrape_google_maps(driver, query, location, max_results):
    try:
        search_query = f"{query} in {location}"
        url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        
        logging.info(f"Navigating to: {url}")
        driver.get(url)
        
        if not wait_for_results(driver):
            logging.error("Timeout waiting for results to load")
            return []
        
        time.sleep(3)  # Allow results to populate
        
        # Find business listings
        listings = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK.tH5CWc.THOPZb")
        if not listings:
            logging.warning("No results with primary selector, trying alternative...")
            listings = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
        
        logging.info(f"Found {len(listings)} listings")
        
        businesses = []
        processed = 0
        
        for listing in listings:
            if processed >= max_results:
                break
                
            try:
                # Click on listing to open details panel
                driver.execute_script("arguments[0].scrollIntoView();", listing)
                driver.execute_script("arguments[0].click();", listing)
                time.sleep(2)  # Allow panel to load
                
                # Extract details from info panel
                business_data = extract_business_details(driver)
                business_data.update({
                    'category': query,
                    'location': location
                })
                
                # Apply filters
                try:
                    rating = float(business_data['rating'])
                    if rating < MIN_RATING:
                        logging.info(f"Skipping {business_data['name']} - Rating {rating} < {MIN_RATING}")
                        continue
                except (ValueError, TypeError):
                    pass
                
                if REQUIRE_NO_WEBSITE and business_data['website'] != 'N/A':
                    logging.info(f"Skipping {business_data['name']} - Has website")
                    continue
                
                businesses.append(business_data)
                processed += 1
                logging.info(f"Added business: {business_data['name']} | Rating: {business_data['rating']} | Website: {business_data['website']}")
                
            except Exception as e:
                logging.warning(f"Error processing listing: {str(e)}")
            finally:
                # Close details panel
                try:
                    close_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']")
                    close_btn.click()
                    time.sleep(0.5)
                except NoSuchElementException:
                    pass
                
                # Random delay between listings
                time.sleep(random.uniform(1, 2))
        
        return businesses
        
    except Exception as e:
        logging.error(f"Scraping error: {str(e)}")
        return []