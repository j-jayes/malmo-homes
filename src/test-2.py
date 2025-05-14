from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
import re

# Setup Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Commented out for debugging
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# Enable performance logging
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

# Initialize driver
driver = webdriver.Chrome(options=chrome_options)

# Navigate to the property page
property_url = "https://www.hemnet.se/salda/lagenhet-3rum-lund-centrum-lunds-kommun-trollebergsvagen-9-1610253269102435008"
driver.get(property_url)

# Give the page some time to load and make API calls
time.sleep(5)

# Extract coordinates from performance logs
coordinates = None
logs = driver.get_log("performance")

for log in logs:
    log_entry = json.loads(log["message"])
    
    # Check if this is a network event
    if "message" in log_entry and log_entry["message"].get("method") == "Network.requestWillBeSent":
        request_data = log_entry["message"].get("params", {})
        request_url = request_data.get("request", {}).get("url", "")
        
        # Check if this is the Maps API call we're looking for
        if "SingleImageSearch" in request_url:
            # Get the post data
            post_data = request_data.get("request", {}).get("postData", "")
            
            if post_data:
                # Look for coordinates pattern
                coord_match = re.search(r'\[null,null,(\d+\.\d+),(\d+\.\d+)\]', post_data)
                if coord_match:
                    lat = coord_match.group(1)
                    lng = coord_match.group(2)
                    coordinates = (float(lat), float(lng))
                    print(f"Found coordinates: {coordinates}")
                    break

driver.quit()

if coordinates:
    print(f"Property coordinates: {coordinates}")
else:
    print("Could not find coordinates in requests")