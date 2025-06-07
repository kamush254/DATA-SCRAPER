from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import logging
import random
from urllib.parse import quote
import re

logger = logging.getLogger(__name__)

def scrape_google_maps(driver, search_term, location, max_results=100):
    """
    Scrape Google Maps for business listings using Selenium
    
    Args:
        driver: Selenium WebDriver instance
        search_term: What to search for (e.g., "restaurants")
        location: Where to search (e.g., "Nairobi, Kenya")
        max_results: Maximum number of results to scrape
    
    Returns:
        List of business dictionaries
    """
    businesses = []
    
    try:
        # Construct search URL
        query = f"{search_term} in {location}"
        encoded_query = quote(query)
        url = f"https://www.google.com/maps/search/{encoded_query}"
        
        logger.info(f"Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 20)
        time.sleep(5)  # Give page time to fully load
        
        # Accept cookies if present
        try:
            accept_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'I agree')]")
            accept_button.click()
            time.sleep(2)
        except NoSuchElementException:
            pass
        
        # Wait for search results to appear
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[role="main"]')))
            logger.info("Search results loaded")
        except TimeoutException:
            logger.warning("Timeout waiting for search results")
            return businesses
        
        # Find the scrollable results panel
        try:
            results_panel = driver.find_element(By.CSS_SELECTOR, '[role="main"]')
        except NoSuchElementException:
            logger.error("Could not find results panel")
            return businesses
        
        # Scroll and collect results
        last_height = 0
        scroll_attempts = 0
        max_scroll_attempts = 15
        
        while len(businesses) < max_results and scroll_attempts < max_scroll_attempts:
            # Find all business listings
            business_links = driver.find_elements(By.CSS_SELECTOR, 'a[data-result-index]')
            
            if not business_links:
                # Try alternative selectors
                business_links = driver.find_elements(By.CSS_SELECTOR, '.hfpxzc')
            
            logger.info(f"Found {len(business_links)} business links on page")
            
            # Process new businesses
            for i, link in enumerate(business_links):
                if len(businesses) >= max_results:
                    break
                
                try:
                    # Skip if we've already processed this business
                    if i < len(businesses):
                        continue
                    
                    business_data = extract_business_data_from_link(link, driver, wait)
                    if business_data and business_data not in businesses:
                        businesses.append(business_data)
                        logger.debug(f"Extracted business {len(businesses)}: {business_data.get('name', 'Unknown')}")
                    
                    # Small delay between extractions
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    logger.warning(f"Error extracting business {i}: {str(e)}")
                    continue
            
            # Scroll down to load more results
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_panel)
            time.sleep(random.uniform(2, 4))
            
            # Check if we've reached the bottom
            new_height = driver.execute_script("return arguments[0].scrollHeight", results_panel)
            if new_height == last_height:
                scroll_attempts += 1
                if scroll_attempts >= 3:  # If no new content for 3 attempts, stop
                    logger.info("Reached end of results")
                    break
            else:
                scroll_attempts = 0
                last_height = new_height
        
        logger.info(f"Successfully scraped {len(businesses)} businesses")
        return businesses
        
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        return businesses

def extract_business_data_from_link(link_element, driver, wait):
    """
    Extract business data by clicking on a business link
    
    Args:
        link_element: Selenium WebElement for the business link
        driver: WebDriver instance
        wait: WebDriverWait instance
    
    Returns:
        Dictionary with business data or None if extraction fails
    """
    business_data = {}
    
    try:
        # Scroll element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", link_element)
        time.sleep(1)
        
        # Click on the business link
        try:
            link_element.click()
        except ElementClickInterceptedException:
            # Try clicking with JavaScript if normal click fails
            driver.execute_script("arguments[0].click();", link_element)
        
        # Wait for business details to load
        time.sleep(random.uniform(2, 4))
        
        # Extract business name
        business_data['name'] = extract_business_name(driver)
        
        # Extract rating
        business_data['rating'] = extract_rating(driver)
        
        # Extract reviews count
        business_data['reviews_count'] = extract_reviews_count(driver)
        
        # Extract address
        business_data['address'] = extract_address(driver)
        
        # Extract phone number
        business_data['phone'] = extract_phone(driver)
        
        # Extract website
        business_data['website'] = extract_website(driver)
        
        # Extract category
        business_data['category'] = extract_category(driver)
        
        # Extract hours
        business_data['hours'] = extract_hours(driver)
        
        # Extract price level
        business_data['price_level'] = extract_price_level(driver)
        
        # Add location context
        business_data['location'] = driver.current_url
        
        return business_data if business_data.get('name') else None
        
    except Exception as e:
        logger.warning(f"Error extracting business data: {str(e)}")
        return None

def extract_business_name(driver):
    """Extract business name with multiple fallback selectors"""
    selectors = [
        'h1[data-attrid="title"]',
        '.DUwDvf.fontHeadlineSmall',
        '.qrShPb .fontHeadlineSmall',
        'h1.DUwDvf',
        '.x3AX1-LfntMc-header-title-title'
    ]
    
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            name = element.text.strip()
            if name:
                return name
        except NoSuchElementException:
            continue
    
    return "Unknown"

def extract_rating(driver):
    """Extract rating with multiple fallback selectors"""
    selectors = [
        '.MW4etd',
        '.ceNzKf',
        '[data-value]',
        '.gm2-body-2'
    ]
    
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            rating_text = element.text.strip()
            # Extract numeric rating
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                return float(rating_match.group(1))
        except (NoSuchElementException, ValueError):
            continue
    
    return None

def extract_reviews_count(driver):
    """Extract reviews count with multiple fallback selectors"""
    selectors = [
        '.UY7F9',
        '.ceNzKf',
        '[data-value] + span',
        '.gm2-body-2'
    ]
    
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            reviews_text = element.text.strip()
            # Extract number from text like "(123)" or "123 reviews"
            reviews_match = re.search(r'(\d+)', reviews_text.replace(',', ''))
            if reviews_match:
                return int(reviews_match.group(1))
        except (NoSuchElementException, ValueError):
            continue
    
    return 0

def extract_address(driver):
    """Extract address with multiple fallback selectors"""
    selectors = [
        '.Io6YTe',
        '[data-item-id*="address"]',
        '.rogA2c .Io6YTe',
        '.LrzXr'
    ]
    
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            address = element.text.strip()
            if address and len(address) > 5:  # Basic validation
                return address
        except NoSuchElementException:
            continue
    
    return None

def extract_phone(driver):
    """Extract phone number with multiple fallback selectors"""
    selectors = [
        '[data-item-id*="phone"]',
        '.rogA2c .Io6YTe',
        'span[data-dtype="d3ph"]'
    ]
    
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            phone = element.text.strip()
            # Basic phone validation
            if phone and ('+' in phone or len(re.findall(r'\d', phone)) >= 7):
                return phone
        except NoSuchElementException:
            continue
    
    return None

def extract_website(driver):
    """Extract website URL with multiple fallback selectors"""
    selectors = [
        'a[data-item-id*="authority"]',
        'a[href*="http"]:not([href*="google"])',
        '.CsEnBe a[href*="http"]'
    ]
    
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            href = element.get_attribute('href')
            if href and 'google' not in href.lower():
                return href
        except NoSuchElementException:
            continue
    
    return None

def extract_category(driver):
    """Extract business category with multiple fallback selectors"""
    selectors = [
        '.DkEaL',
        '.mgr77e .DkEaL',
        '.LBgpqf .DkEaL'
    ]
    
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            category = element.text.strip()
            if category:
                return category
        except NoSuchElementException:
            continue
    
    return None

def extract_hours(driver):
    """Extract business hours with multiple fallback selectors"""
    selectors = [
        '.t39EBf',
        '.OqCZI .t39EBf',
        '[data-dtype="d3oh"]'
    ]
    
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            hours = element.text.strip()
            if hours:
                return hours
        except NoSuchElementException:
            continue
    
    return None

def extract_price_level(driver):
    """Extract price level (number of $ symbols)"""
    selectors = [
        '.mgr77e',
        '.priceRange',
        '[data-dtype="d3pr"]'
    ]
    
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            price_text = element.text.strip()
            if '$' in price_text:
                return price_text.count('$')
        except NoSuchElementException:
            continue
    
    return None

def filter_businesses(businesses, min_rating=None, require_no_website=False, min_reviews=0):
    """
    Filter businesses based on specified criteria
    
    Args:
        businesses: List of business dictionaries
        min_rating: Minimum rating required (float)
        require_no_website: If True, only include businesses without websites
        min_reviews: Minimum number of reviews required
    
    Returns:
        Filtered list of businesses
    """
    filtered = []
    
    for business in businesses:
        # Check rating filter
        if min_rating and business.get('rating'):
            if business['rating'] < min_rating:
                continue
        
        # Check website filter
        if require_no_website and business.get('website'):
            continue
        
        # Check reviews filter
        if business.get('reviews_count', 0) < min_reviews:
            continue
        
        filtered.append(business)
    
    logger.info(f"Filtered {len(businesses)} businesses down to {len(filtered)}")
    return filtered