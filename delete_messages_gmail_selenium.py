from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os

def delete_gmail_label_emails():
    """
    Automates deleting all emails from Gmail label '_teverwijderen'
    Uses your existing Chrome profile to avoid login
    """
    
    # Setup Chrome options to use your existing profile
    chrome_options = Options()
    
    # Get the user's home directory
    home = os.path.expanduser("~")
    
    # Chrome user data directory paths for different OS
    if os.name == 'nt':  # Windows
        user_data_dir = os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data")
        #C:\Users\rcxsm\AppData\Local\Google\Chrome\User Data\Default
    elif os.name == 'posix':  # Mac/Linux
        if os.path.exists(os.path.join(home, "Library")):  # Mac
            user_data_dir = os.path.join(home, "Library", "Application Support", "Google", "Chrome")
        else:  # Linux
            user_data_dir = os.path.join(home, ".config", "google-chrome")
    
    print(f"Using Chrome profile from: {user_data_dir}")
    
    # Add the user data directory
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    chrome_options.add_argument("profile-directory=Default")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--remote-debugging-pipe')
    chrome_options.add_argument("start-maximized"); # https:#stackoverflow.com/a/26283818/1689770
    chrome_options.add_argument("enable-automation"); # https:#stackoverflow.com/a/43840128/1689770
    chrome_options.add_argument("--headless"); # only if you are ACTUALLY running headless
    chrome_options.add_argument("--no-sandbox"); #https:#stackoverflow.com/a/50725918/1689770
    chrome_options.add_argument("--disable-dev-shm-usage"); #https:#stackoverflow.com/a/50725918/1689770
    chrome_options.add_argument("--disable-browser-side-navigation"); #https:#stackoverflow.com/a/49123152/1689770
    chrome_options.add_argument("--disable-gpu"); #https:#stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc
    
    print ("opening driver")
    # Initialize Chrome driver with options
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the Gmail label
        url = "https:#mail.google.com/mail/u/0/#label/_teverwijderen"
        print ("Get URL")
        driver.get(url)
        
        print("Loading Gmail...")
        time.sleep(5)  # Wait for page to load
        
        # Wait for emails to load
        print("Waiting for emails to load...")
        time.sleep(3)
        
        # Look for the "Select all" checkbox
        try:
            # Try to find the select all checkbox
            select_all = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "#div[@role='checkbox'][@aria-label='Select']"))
            )
            select_all.click()
            print("✓ Clicked 'Select all' checkbox")
            time.sleep(2)
            
            # Check if there's a "Select all conversations" link
            try:
                select_all_link = driver.find_element(By.XPATH, "#span[contains(text(), 'Select all')]")
                select_all_link.click()
                print("✓ Clicked 'Select all conversations' link")
                time.sleep(2)
            except:
                print("→ No 'Select all conversations' link (might be < 50 emails)")
            
            # Click delete button
            delete_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "#div[@aria-label='Delete']"))
            )
            delete_button.click()
            print("✓ Clicked 'Delete' button")
            time.sleep(3)
            
            print("\n✓ Emails deleted successfully!")
            
        except Exception as e:
            print(f"⚠ Error with clicking method: {e}")
            print("\n→ Trying keyboard shortcut method...")
            
            # Alternative: Use keyboard shortcuts
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.CONTROL + 'a')  # Select all (use Keys.COMMAND on Mac)
                time.sleep(2)
                body.send_keys('#')  # Delete shortcut in Gmail
                time.sleep(3)
                print("✓ Used keyboard shortcuts to delete")
            except Exception as e2:
                print(f"✗ Keyboard shortcut also failed: {e2}")
                print("\nPlease check if you're on the correct page and try manually.")
        
        print("\nKeeping browser open for 10 seconds to verify...")
        time.sleep(10)
        
    except Exception as e:
        print(f"✗ An error occurred: {e}")
    
    finally:
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":

    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    #driver = webdriver.Chrome()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    print(driver.capabilities['chrome']['chromedriverVersion'])
    driver.quit()

    if 1==2:
        print("=" * 60)
        print("Gmail Auto-Delete Script (Using Your Chrome Profile)")
        print("=" * 60)
        print("This script will delete all emails in '_teverwijderen' label")
        print("Using your existing Chrome profile - no login needed!")
        print("=" * 60)
        print("\n⚠ IMPORTANT: Close all Chrome windows before running this!")
        print("=" * 60)
        
        input("\nPress Enter to continue...")
        delete_gmail_label_emails()