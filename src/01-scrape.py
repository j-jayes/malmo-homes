from requests_html import HTMLSession
from bs4 import BeautifulSoup

def get_data(s, url):
    r = s.get(url)
    print(r)
    # return the HTML content that can be parsed by BeautifulSoup
    return r.html.html

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
        agent_link = agent_name_tag.get('href')
        if agent_link:
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

def main():
    session = HTMLSession()
    url = "https://www.hemnet.se/salda/lagenhet-2rum-fagelbacken-malmo-kommun-edward-lindahlsgatan-12f-4025812685731529616"

    html_content = get_data(session, url)
    data = parse_html(html_content)
    print(data)
