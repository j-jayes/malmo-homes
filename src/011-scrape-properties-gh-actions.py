import sys
import os

# Add the path to the utils module
utils_path = os.path.join(os.path.dirname(__file__), '../utils')
sys.path.append(utils_path)

# Check if the path is correctly added
print(f"Utils path added to sys.path: {utils_path}")
print(f"Current sys.path: {sys.path}")


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from requests_html import HTMLSession
from utils.scraper import parse_html, extract_coordinates_from_request
from utils.storage import save_to_parquet, load_parquet
import pandas as pd
import logging
import time
import random
import json
import re

def setup_selenium_driver():
    """Set up and return a Selenium WebDriver with appropriate options."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment for production
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    
    # Enable performance logging
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    # Initialize and return driver
    return webdriver.Chrome(options=chrome_options)

def extract_coordinates_from_selenium(driver, url):
    """Extract coordinates from Google Maps API requests using Selenium."""
    try:
        # Navigate to the URL
        driver.get(url)
        
        # Wait for page and map to load
        time.sleep(5)
        
        # Extract performance logs
        logs = driver.get_log("performance")
        
        # Process logs to find the Maps API request
        for entry in logs:
            try:
                log = json.loads(entry["message"])
                if "message" not in log or "params" not in log["message"]:
                    continue
                    
                params = log["message"]["params"]
                
                # Check for request will be sent
                if log["message"]["method"] == "Network.requestWillBeSent":
                    if "request" not in params:
                        continue
                        
                    request = params["request"]
                    request_url = request.get("url", "")
                    if "SingleImageSearch" in request_url:
                        if "postData" in request:
                            # Look for coordinates in the post data
                            post_data = request["postData"]
                            coord_match = re.search(r'\[null,null,(\d+\.\d+),(\d+\.\d+)\]', post_data)
                            if coord_match:
                                lat = float(coord_match.group(1))
                                lng = float(coord_match.group(2))
                                return (lat, lng)
                                
            except Exception as e:
                logging.error(f"Error processing log entry: {e}")
    
    except Exception as e:
        logging.error(f"Error extracting coordinates: {e}")
    
    return None

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    session = HTMLSession()
    
    # Initialize Selenium driver for coordinate extraction
    driver = setup_selenium_driver()
    
    # Get the date and time
    date_time = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")

    property_links_file = "data/interim/hemnet_links.parquet"
    df_links = pd.read_parquet(property_links_file)

    cache_file = 'data/interim/hemnet_properties_cache.parquet'
    try:
        property_data_cache = load_parquet(cache_file)
    except FileNotFoundError:
        property_data_cache = pd.DataFrame()

    # Filter links not in the cache
    if not property_data_cache.empty:
        cached_urls = set(property_data_cache['url'])
        df_links = df_links[~df_links['url'].isin(cached_urls)]

    # Select a subset new properties
    df_links_subset = df_links.head(1000)
    logging.info(f"Selected {len(df_links_subset)} new properties for processing.")

    for index, row in df_links_subset.iterrows():
        url = row['url']
        try:
            # First get the HTML content with requests-html
            r = session.get(url)
            data = parse_html(r.html.html)
            data['url'] = url
            
            # Then use Selenium to extract coordinates
            coordinates = extract_coordinates_from_selenium(driver, url)
            if coordinates:
                data['Latitude'] = coordinates[0]
                data['Longitude'] = coordinates[1]
                logging.info(f"Successfully extracted coordinates for {url}: {coordinates}")
            else:
                logging.warning(f"Could not extract coordinates for {url}")

            property_data_cache = pd.concat([property_data_cache, pd.DataFrame([data])], ignore_index=True)
            logging.info(f"Data collected for {url}")
            time.sleep(5 + 5 * random.random())  # Random delay between 5-10 seconds
        except Exception as e:
            logging.error(f"Error collecting data for {url}: {e}")

    # Clean up the Selenium driver
    driver.quit()

    # Save updated cache and new data
    save_to_parquet(property_data_cache, cache_file)
    logging.info("Cache updated with new properties.")

    if not property_data_cache.empty:
        # Save only the newly added properties
        new_properties = property_data_cache.tail(len(df_links_subset))
        output_file = f'data/raw/hemnet_properties_{date_time}.parquet'
        save_to_parquet(new_properties, output_file)
        logging.info(f"New property data saved to {output_file}")

if __name__ == "__main__":
    main()