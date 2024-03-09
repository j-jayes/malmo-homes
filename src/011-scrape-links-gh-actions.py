from requests_html import HTMLSession
# from folder called utils and file called scraper-utils.py import the functions get_data and parse_html
from utils.scraper import get_data, parse_html, collect_property_links
from utils.storage import save_to_parquet, load_parquet
import pandas as pd
import os
import logging
import time
import random

def main():
    # Step 1: Collect the links to the properties
    # create a new HTML session
    session = HTMLSession()
    # initiate logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # set the params
    base_url = "https://www.hemnet.se/salda/bostader?location_ids%5B%5D=17989"
    min_area = 20
    max_area = 250
    step = 2

    # Get the date 
    date = pd.Timestamp.now().strftime("%Y-%m-%d")

    # property links file
    property_links_file = f"output/hemnet_links_{date}_total.parquet"

    # collect the property links if the file does not exist
    if not os.path.exists(property_links_file):
        property_links = collect_property_links(base_url, min_area, max_area, step)
        df_links = pd.DataFrame(property_links, columns=['url'])
        save_to_parquet(df_links, property_links_file)
    else:
        df_links = load_parquet(property_links_file)

    print(f"Collected a total of {len(df_links)} property links.")
    
if __name__ == "__main__":
    main()