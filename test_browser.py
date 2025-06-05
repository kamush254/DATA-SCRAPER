from browser_controller import create_driver
import time

def test_browser():
    driver = None
    try:
        print("Creating browser...")
        driver = create_driver()
        print("Browser created successfully")
        
        print("Testing navigation...")
        driver.get("https://www.google.com")
        print(f"Page title: {driver.title}")
        
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
        
    finally:
        if driver:
            driver.quit()
            print("Browser closed")

if __name__ == "__main__":
    test_browser()