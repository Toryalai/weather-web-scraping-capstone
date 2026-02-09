import os
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


URL = "https://www.timeanddate.com/weather/usa/washington-dc/hourly"
RAW_DATA_FILE = "data/raw_weather.csv"
WAIT_TIMEOUT = 15  
SCRAPE_DELAY = 2   

# HELPER FUNCTIONS
def setup_driver():
    chrome_options = Options()
    
    # Add user-agent to avoid being blocked
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Additional options for stability
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    return driver


def check_for_duplicates(new_data):

    if not os.path.exists(RAW_DATA_FILE):
        return False
    
    try:
        existing_df = pd.read_csv(RAW_DATA_FILE)
        new_df = pd.DataFrame(new_data)
        
        # Check if we have the same time entries from today
        if len(existing_df) > 0:
            existing_df['Scraped_At'] = pd.to_datetime(existing_df['Scraped_At'])
            today = datetime.now().date()
            
            # Check if we already scraped data today
            today_scrapes = existing_df[
                existing_df['Scraped_At'].dt.date == today
            ]
            
            if len(today_scrapes) > 0:
                print(f"Found {len(today_scrapes)} records already scraped today.")
                print("Skipping duplicate scraping. Delete the CSV to force re-scrape.")
                return True
                
    except Exception as e:
        print(f"Note: Could not check for duplicates: {e}")
        return False
    
    return False


def scrape_weather_data(driver):
    results = []
    
    try:
        # Wait for the weather table to load
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        wait.until(
            EC.presence_of_element_located((By.ID, "wt-hbh"))
        )
        
        # Give the page a moment to fully render
        time.sleep(SCRAPE_DELAY)
        
        # Find all rows in the hourly weather table
        rows = driver.find_elements(
            By.XPATH, "//table[@id='wt-hbh']/tbody/tr"
        )
        
        print(f"Found {len(rows)} hourly weather entries")
        
        # Extract data from each row
        for idx, row in enumerate(rows, 1):
            try:
                # Extract each field with error handling for missing elements
                time_text = row.find_element(By.XPATH, "./th").text.strip()
                
                # Temperature (column 2)
                try:
                    temp = row.find_element(By.XPATH, "./td[2]").text.strip()
                except:
                    temp = None
                
                # Weather condition (column 3)
                try:
                    weather = row.find_element(By.XPATH, "./td[3]").text.strip()
                except:
                    weather = None
                
                # Wind (column 5)
                try:
                    wind = row.find_element(By.XPATH, "./td[5]").text.strip()
                except:
                    wind = None
                
                # Humidity (column 7)
                try:
                    humidity = row.find_element(By.XPATH, "./td[7]").text.strip()
                except:
                    humidity = None
                
                # Create data record
                results.append({
                    "City": "Washington, DC",
                    "Time": time_text,
                    "Temperature": temp,
                    "Weather": weather,
                    "Wind": wind,
                    "Humidity": humidity,
                    "Scraped_At": datetime.now().isoformat()
                })
                
                # Progress indicator
                if idx % 10 == 0:
                    print(f"Processed {idx}/{len(rows)} rows...")
                    
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                continue
        
        print(f"Successfully scraped {len(results)} weather records")
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        raise
    
    return results


def save_to_csv(data, filename):

    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Convert to DataFrame
    new_df = pd.DataFrame(data)
    
    # Append to existing file or create new one
    if os.path.exists(filename):
        existing_df = pd.read_csv(filename)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(filename, index=False)
        print(f"Appended {len(new_df)} rows to existing file")
    else:
        new_df.to_csv(filename, index=False)
        print(f"Created new file with {len(new_df)} rows")
    
    print(f"Data saved to: {filename}")


# MAIN EXECUTION

def main():

    print("WEATHER SCRAPING SCRIPT")
    print(f"Target URL: {URL}")
    print(f"Output File: {RAW_DATA_FILE}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    driver = None
    
    try:
        # Setup Chrome driver
        print("\nSetting up Chrome WebDriver...")
        driver = setup_driver()
        
        # Navigate to the weather page
        print(f"Loading page: {URL}")
        driver.get(URL)
        
        # Scrape the weather data
        print("\nStarting data extraction...")
        weather_data = scrape_weather_data(driver)
        
        # Check for duplicates
        if not check_for_duplicates(weather_data):
            # Save to CSV
            print("\nSaving data to CSV...")
            save_to_csv(weather_data, RAW_DATA_FILE)
            
            # Display sample of scraped data
            print("\nSample of scraped data:")
            df = pd.DataFrame(weather_data)
            print(df.head(10))
            print(f"\nTotal records: {len(df)}")
            print(f"Columns: {list(df.columns)}")
        
        print("\n" + "=" * 70)
        print("SCRAPING COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"ERROR: {e}")
        print("=" * 70)
        raise
        
    finally:
        # Always close the browser
        if driver:
            driver.quit()
            print("Browser closed")


if __name__ == "__main__":
    main()