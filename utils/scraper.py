
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from math import ceil
import re
import random
import time


# function to get the HTML content from a page
def get_data(s, url):
    r = s.get(url)
    print(r)
    # return the HTML content that can be parsed by BeautifulSoup
    return r.html.html

# function to parse the HTML content of a partcular property
def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {}

    # Extract the final price
    final_price_container = soup.find('div', class_='SaleAttributes_sellingPrice__iFujI')
    if final_price_container:
        # Assuming the second span contains the final price
        final_price = final_price_container.find_all('span', class_='SaleAttributes_sellingPriceText__UZF0W')[1].text
        final_price = final_price.replace(u'\xa0', u' ')  # Replace non-breaking spaces
        data['Slutpris'] = final_price

    # Extract the title (h1 tag)
    title_tag = soup.find('h1', class_='hcl-heading')
    if title_tag:
        data['Title'] = title_tag.text.strip()

    # Extract the property type, location and sale date
    type_location_date_container = soup.find('div', class_='ListingContent_paddedContainer__OC_QR')
    if type_location_date_container:
        type_location_date_text = type_location_date_container.find('p', class_='hcl-text').text.strip()
        type_location_date_parts = type_location_date_text.split(' - ')
        if len(type_location_date_parts) == 3:
            data['Type'] = type_location_date_parts[0]
            data['Location'] = type_location_date_parts[1]
            data['Sale Date'] = type_location_date_parts[2]

    # Extract the real estate agent information
    agent_info_container = soup.find('div', id='maklarinfo')
    if agent_info_container:
        # Extract the agent's name from the 'a' tag
        agent_name_tag = agent_info_container.find('a', class_='hcl-link')
        if agent_name_tag:
            data['Agent Name'] = agent_name_tag.text.strip()

        # Extract the agent link
        # the agent link is the href from agent_name_tag
        agent_link = agent_name_tag.get('href') if agent_name_tag else None
        data['Agent Link'] = agent_link

    # Find the section with the aria-label 'information om bostaden'
    section = soup.find('section', {'aria-label': 'information om bostaden'})

    # Find all divs with class 'hcl-flex--container hcl-flex--justify-space-between'
    # This assumes that all the information divs share this class.
    info_divs = section.find_all('div', class_='hcl-flex--container hcl-flex--justify-space-between')

    for div in info_divs:
        # Find the 'p' tag for the property name
        property_name_element = div.find('p', class_='hcl-text')
        if property_name_element:
            property_name = property_name_element.get_text(strip=True)
        
            # Find the 'strong' tag for the property value
            property_value_element = div.find('strong', class_='hcl-text')
            if property_value_element:
                property_value = property_value_element.get_text(strip=True)
                property_value = property_value.replace(u'\xa0', u' ')  # Replace non-breaking spaces

                # Add the property name and value to the data dictionary
                data[property_name] = property_value

    return data


# function to get the property links
def get_total_pages(session, base_url, min_area, max_area):
    url = f"{base_url}&living_area_min={min_area}&living_area_max={max_area}"
    try:
        r = session.get(url)
        # r.html.render()  # Uncomment if JavaScript needs to run to load the pagination information
        
        # Find the total number of results from the pagination div
        pagination_text = r.html.find('.hcl-pagination', first=True).text
        
        # Use regex to extract the total number of results
        total_results_match = re.search(r'av\s+(\d+)', pagination_text)
        if total_results_match:
            total_results = int(total_results_match.group(1))  # Convert the captured number to an integer
        else:
            print("Warning: Could not find total results in pagination text for URL:", url)
            return 0  # Return 0 if we can't find the total results
        
        total_pages = ceil(total_results / 50)  # Assuming 50 results per page
        return total_pages
    except Exception as e:
        print(f"Error fetching total pages for URL: {url}. Error: {e}")
        return 0  # Return 0 to handle errors gracefully

def collect_property_links(base_url, min_area, max_area, step):
    session = HTMLSession()
    property_links = []
    
    current_min_area = min_area
    while current_min_area <= max_area:
        current_max_area = current_min_area + step if current_min_area < 160 else current_min_area + 10

        try:
            total_pages = get_total_pages(session, base_url, current_min_area, current_max_area)
        except ValueError as e:
            print(f"Skipping range {current_min_area}-{current_max_area} due to error: {e}")
            current_min_area = current_max_area + 1
            continue

        for page in range(1, total_pages + 1):
            try:
                url = f"{base_url}&living_area_min={current_min_area}&living_area_max={current_max_area}&page={page}"
                r = session.get(url)
                # r.html.render()  # Uncomment if JavaScript needs to run to load the links
                
                # Extract property links
                links = r.html.find('div[data-testid="result-list"] a.hcl-card')
                property_links.extend(['https://www.hemnet.se' + link.attrs['href'] for link in links if 'href' in link.attrs])
                
                # Optional: Print out the progress
                print(f"Collected links from page {page} for size range {current_min_area}-{current_max_area}")
                # sleep for a random time between 1 and 3 seconds
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"Error collecting links from page {page} for size range {current_min_area}-{current_max_area}. Error: {e}")
                # Continue to the next page even if the current one fails

        # here we increase the current_min_area to the next step, increasing by one
        current_min_area = current_max_area + 1

    return property_links

