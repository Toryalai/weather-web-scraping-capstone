from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime

URL = "https://www.timeanddate.com/weather/usa/washington-dc/hourly"

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)
driver.get(URL)

wait = WebDriverWait(driver, 15)
wait.until(
    EC.presence_of_element_located((By.ID, "wt-hbh"))
)

rows = driver.find_elements(
    By.XPATH, "//table[@id='wt-hbh']/tbody/tr"
)

print(f"Found {len(rows)} rows")

results = []

for row in rows:
    try:
        time_text = row.find_element(By.XPATH, "./th").text.strip()
        temp = row.find_element(By.XPATH, "./td[2]").text.strip()
        weather = row.find_element(By.XPATH, "./td[3]").text.strip()
        wind = row.find_element(By.XPATH, "./td[5]").text.strip()
        humidity = row.find_element(By.XPATH, "./td[7]").text.strip()

        results.append({
            "City": "Washington, DC",
            "Time": time_text,
            "Temperature": temp,
            "Weather": weather,
            "Wind": wind,
            "Humidity": humidity,
            "Scraped_At": datetime.now().isoformat()
        })

    except Exception as e:
        print("Skipping row:", e)

driver.quit()

df = pd.DataFrame(results)
df.to_csv("data/raw_weather.csv", index=False)

print("Scraping successful")
print(df.head())
