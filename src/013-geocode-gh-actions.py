def geocode_addresses(data_file='data/interim/hemnet_properties_cache.parquet', cache_file='data/geodata/address_cache.parquet', user_agent="your_unique_user_agent_here"):
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter
    from geopy.exc import GeocoderTimedOut, GeocoderQuotaExceeded
    import pandas as pd
    import json

    # Load your data
    data = pd.read_parquet(data_file)

    addresses = data["Title"].unique()

    df_addresses = pd.DataFrame(addresses, columns=["title"])

    # Try to load existing cache
    try:
        cache_df = pd.read_parquet(cache_file)
        # Ensure the dataframe is not empty
        if not cache_df.empty:
            # Convert the dataframe to a dictionary with titles as keys and lat-long tuples as values
            cache = dict(zip(cache_df.Title, zip(cache_df.Lat, cache_df.Long)))
    except FileNotFoundError:
        print("Cache file not found. Starting with an empty cache.")
        cache = {}

    # Find addresses that are not in the cache
    df_addresses = df_addresses[~df_addresses['title'].isin(cache.keys())]

    # Take the first 1000 addresses for processing
    df_addresses = df_addresses.head(10)

    # Initialize the geocoder with a unique user_agent
    geolocator = Nominatim(user_agent=user_agent)

    # Use RateLimiter to respect the API limits
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=5, error_wait_seconds=10, max_retries=2, swallow_exceptions=True)

    def geocode_address_with_cache(address):
        try:
            location = geocode(f"{address}, Malmö, Sweden")
            if location:
                result = (location.latitude, location.longitude)
                cache[address] = result
                print(f"Geocoding successful for {address}: {result}")
                return result
            else:
                print(f"Geocoding failed for {address}: No location found.")
                return (None, None)
        except (GeocoderTimedOut, GeocoderQuotaExceeded) as e:
            print(f"Geocoding error for {address}: {str(e)}")
            return (None, None)
            
    # Apply the function to your data
    df_addresses['lat_lon'] = df_addresses['title'].apply(geocode_address_with_cache)

    # Save the updated cache
    cache_df = pd.DataFrame(list(cache.items()), columns=['Title', 'LatLon'])
    cache_df[['Lat', 'Long']] = pd.DataFrame(cache_df['LatLon'].tolist(), index=cache_df.index)
    cache_df.drop(columns=['LatLon'], inplace=True)
    cache_df.to_parquet(cache_file)


# Run the function
geocode_addresses()
