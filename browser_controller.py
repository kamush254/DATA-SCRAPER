from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import logging

def create_driver():
    chrome_options = Options()
    
    # Disable GPU and graphics acceleration completely
   # chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--use-gl=angle')
    chrome_options.add_argument('--use-angle=default')
    chrome_options.add_argument('--disable-software-rasterizer')
    
    # Stability improvements
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--disable-breakpad')
    
    # Memory and performance settings
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--disable-in-process-stack-traces')
    chrome_options.add_argument('--log-level=3')
    
    # Add user agent to avoid detection
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        
        # Set timeouts
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        driver.implicitly_wait(10)
        
        return driver
    except Exception as e:
        logging.error(f"Failed to create Chrome driver: {str(e)}")
        raise