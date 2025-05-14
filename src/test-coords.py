from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re

def extract_coordinates(url):
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Enable performance logging
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
    
    # Initialize the driver with your specific chromedriver path
    driver = webdriver.Chrome(service=Service("/opt/homebrew/bin/chromedriver"), options=chrome_options)
    
    try:
        # Navigate to the page
        driver.get(url)
        print(f"Loading page: {url}")
        
        # Wait for cookie consent dialog and accept it using the specific selector
        try:
            # Using the exact selector you provided
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.uc-accept-button#accept[data-action="consent"][data-action-type="accept"]'))
            )
            cookie_button.click()
            print("Accepted cookies")
        except Exception as e:
            print(f"Could not click cookie button: {e}")
            # Try alternative selectors if the specific one fails
            try:
                alternative_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Acceptera alla')]"))
                )
                alternative_button.click()
                print("Accepted cookies using alternative selector")
            except Exception as e2:
                print(f"Also failed with alternative selector: {e2}")

        # Give the page time to load after handling cookies
        time.sleep(3)
        
        # Try to find map element with data attributes
        try:
            map_elements = driver.find_elements(By.CSS_SELECTOR, 
                '[data-map], [class*="map-container"], [class*="MapContainer"], [id*="map"]')
            
            print(f"Found {len(map_elements)} potential map elements")
            
            for element in map_elements:
                print(f"Map element ID: {element.get_attribute('id')}, Class: {element.get_attribute('class')}")
                # Get all data attributes
                data_attrs = driver.execute_script(
                    """
                    const attrs = {};
                    for (const attr of arguments[0].attributes) {
                        if (attr.name.startsWith('data-')) {
                            attrs[attr.name] = attr.value;
                        }
                    }
                    return attrs;
                    """, 
                    element
                )
                print(f"Data attributes: {data_attrs}")
                
                # Check for coordinates in data attributes
                if 'data-map-lat' in data_attrs and 'data-map-lng' in data_attrs:
                    return (float(data_attrs['data-map-lat']), float(data_attrs['data-map-lng']))
                
                # Look inside the element for other elements with coordinate data
                child_elements = element.find_elements(By.CSS_SELECTOR, '[data-lat], [data-lng], [data-latitude], [data-longitude]')
                for child in child_elements:
                    lat = child.get_attribute('data-lat') or child.get_attribute('data-latitude')
                    lng = child.get_attribute('data-lng') or child.get_attribute('data-longitude')
                    if lat and lng:
                        return (float(lat), float(lng))
        except Exception as e:
            print(f"Error examining map elements: {e}")
        
        # Try to extract coordinates using JavaScript
        script = """
        // Try different methods to find coordinates

        // Method 1: Check global variables
        if (window.hemnet && window.hemnet.listing && window.hemnet.listing.coordinates) {
            return window.hemnet.listing.coordinates;
        }
        
        // Method 2: Check for map initialization data
        let mapData = {};
        const scripts = document.querySelectorAll('script:not([src])');
        for (const script of scripts) {
            const text = script.textContent;
            
            // Look for patterns that might contain coordinates
            let match;
            
            // Pattern 1: Look for direct coordinate initialization
            match = text.match(/lat[\s\w]*[:=][\s\w]*(-?\d+\.\d+)[\s\w]*,[\s\w]*lng[\s\w]*[:=][\s\w]*(-?\d+\.\d+)/i);
            if (match) {
                mapData.lat = match[1];
                mapData.lng = match[2];
                return mapData;
            }
            
            // Pattern 2: Look for coordinates in JSON-like structures
            match = text.match(/"latitude"[\s\w]*:[\s\w]*(-?\d+\.\d+)[\s\w]*,[\s\w]*"longitude"[\s\w]*:[\s\w]*(-?\d+\.\d+)/i);
            if (match) {
                mapData.lat = match[1];
                mapData.lng = match[2];
                return mapData;
            }
            
            // Pattern 3: Look for map initialization
            match = text.match(/map[^(]*?\([\s\w]*(-?\d+\.\d+)[\s\w]*,[\s\w]*(-?\d+\.\d+)/i);
            if (match) {
                mapData.lat = match[1];
                mapData.lng = match[2];
                return mapData;
            }
        }
        
        // Method 3: Look for meta tags with geo information
        const metaTags = document.querySelectorAll('meta[name*="geo"], meta[property*="geo"]');
        for (const tag of metaTags) {
            const content = tag.getAttribute('content');
            if (content && content.includes(',')) {
                const [lat, lng] = content.split(',').map(s => s.trim());
                mapData.lat = lat;
                mapData.lng = lng;
                return mapData;
            }
        }
        
        // Method 4: Look for data in Google Maps iframe
        const mapIframes = document.querySelectorAll('iframe[src*="google.com/maps"]');
        for (const iframe of mapIframes) {
            const src = iframe.getAttribute('src');
            const match = src.match(/q=(-?\d+\.\d+),(-?\d+\.\d+)/);
            if (match) {
                mapData.lat = match[1];
                mapData.lng = match[2];
                return mapData;
            }
        }
        
        return null;
        """
        
        map_data = driver.execute_script(script)
        if map_data and 'lat' in map_data and 'lng' in map_data:
            return (float(map_data['lat']), float(map_data['lng']))
            
        # If JavaScript methods fail, try to look for network requests with coordinates
        logs = driver.get_log("performance")
        
        print(f"Analyzing {len(logs)} network log entries")
        
        for log in logs:
            try:
                log_entry = json.loads(log["message"])
                
                if "Network.requestWillBeSent" in log_entry["message"]["method"]:
                    request = log_entry["message"]["params"].get("request", {})
                    request_url = request.get("url", "")
                    
                    # Check if it's a Google Maps API request
                    if "google" in request_url and "maps" in request_url:
                        print(f"Found Maps API request: {request_url[:100]}...")
                        
                        # Check postData for coordinates
                        post_data = request.get("postData", "")
                        if post_data:
                            print(f"Request has post data of length {len(post_data)}")
                            
                            # Look for various coordinate formats
                            patterns = [
                                r'\[null,\s*(-?\d+\.\d+),\s*(-?\d+\.\d+)',
                                r'"lat\w*":\s*(-?\d+\.\d+).*?"lng\w*":\s*(-?\d+\.\d+)',
                                r'"latitude":\s*(-?\d+\.\d+).*?"longitude":\s*(-?\d+\.\d+)',
                                r'q=(-?\d+\.\d+),(-?\d+\.\d+)'
                            ]
                            
                            for pattern in patterns:
                                match = re.search(pattern, post_data)
                                if match:
                                    lat, lng = match.group(1), match.group(2)
                                    print(f"Found coordinates in request: {lat}, {lng}")
                                    return (float(lat), float(lng))
            except Exception as e:
                # Skip entries that can't be parsed
                continue
                
        print("Could not find coordinates using any method.")
        return None
        
    finally:
        driver.quit()

# Example usage
url = "https://www.hemnet.se/bostad/lagenhet-4rum-vikaholm-vaxjo-kommun-rundquists-vag-34-21405925"
coordinates = extract_coordinates(url)
print(f"Property coordinates: {coordinates}")
