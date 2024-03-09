from requests_html import HTMLSession
# from folder called utils and file called scraper-utils.py import the functions get_data and parse_html
from utils.scraper import collect_property_links_gh_actions
from utils.storage import save_to_parquet, load_parquet
import pandas as pd
import os
import logging

# this script reads in a list of links already collected and then collects new links
# the new links are then joined with the old links and duplicates are removed
# the final list of links is then saved to a parquet file
def main():
    # Step 1: Collect the links to the properties
    # create a new HTML session
    session = HTMLSession()
    # initiate logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # set the params
    base_url = "https://www.hemnet.se/salda/bostader?location_ids%5B%5D=17989"

    # Get the date 
    date = pd.Timestamp.now().strftime("%Y-%m-%d")

    # existing property links fils
    property_links_file = f"output/hemnet_links_total.parquet"

    property_links = load_parquet(property_links_file)
    
    new_property_links = collect_property_links_gh_actions(base_url)
    df_new_links = pd.DataFrame(new_property_links, columns=['url'])

    # count how many new links were collected that were not in the original list by doing a set difference
    new_links = set(new_property_links) - set(property_links['url'])

    # log the number of new links collected
    if len(new_links) > 0:
        logging.info(f"Collected {len(new_links)} new property links.")
    else:
        logging.info(f"No new property links collected.")

    # join the new links with the old links and remove duplicates
    df_links = pd.concat([property_links, df_new_links], ignore_index=True).drop_duplicates()
        
    save_to_parquet(df_links, property_links_file)

    print(f"There are a total of {len(df_links)} property links.")
    
if __name__ == "__main__":
    main()