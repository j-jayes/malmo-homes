from requests_html import HTMLSession
from utils.scraper import parse_html
from utils.storage import save_to_parquet, load_parquet
import pandas as pd
import logging
import time
import random

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    session = HTMLSession()
    # Get the date and time
    date_time = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")

    property_links_file = "output/hemnet_links_total.parquet"
    df_links = pd.read_parquet(property_links_file)

    cache_file = 'output/hemnet_properties_cache.parquet'
    try:
        property_data_cache = load_parquet(cache_file)
    except FileNotFoundError:
        property_data_cache = pd.DataFrame()

    # Filter links not in the cache
    if not property_data_cache.empty:
        cached_urls = set(property_data_cache['url'])
        df_links = df_links[~df_links['url'].isin(cached_urls)]

    # Select a subset new properties
    df_links_subset = df_links.head(5)
    logging.info(f"Selected {len(df_links_subset)} new properties for processing.")

    for index, row in df_links_subset.iterrows():
        url = row['url']
        try:
            r = session.get(url)
            data = parse_html(r.html.html)
            data['url'] = url

            property_data_cache = pd.concat([property_data_cache, pd.DataFrame([data])], ignore_index=True)
            logging.info(f"Data collected for {url}")
            time.sleep(5 + 5 * random.random())  # Random delay
        except Exception as e:
            logging.error(f"Error collecting data for {url}: {e}")

    # Save updated cache and new data
    save_to_parquet(property_data_cache, cache_file)
    logging.info("Cache updated with new properties.")

    if not property_data_cache.empty:
        # Save only the newly added properties
        new_properties = property_data_cache.tail(len(df_links_subset))
        output_file = f'output/hemnet_properties_{date}.parquet'
        save_to_parquet(new_properties, output_file)
        logging.info(f"New property data saved to {output_file}")

if __name__ == "__main__":
    main()
