import pandas as pd
from skimpy import skim


# read in the parquet file from "output/hemnet_properties_2024-02-23.parquet"
df = pd.read_parquet("data/interim/hemnet_properties_cache.parquet")

# skim the data
skim(df)

df_cleaned = clean_and_transform_hemnet_data("data/interim/hemnet_properties_cache.parquet", "data/processed/hemnet_properties_cleaned.parquet")

# skim the cleaned data
skim(df_cleaned)

# filter for type "Villa"
df_villa = df_cleaned[df_cleaned["type"] == "Villa"]

# skim df_villa
skim(df_villa)

# filter for type "Lägenhet"
df_lagenhet = df_cleaned[df_cleaned["type"] == "Lägenhet"]


# skim df_lagenhet
skim(df_lagenhet)

# read in location cache from "data/geodata/address_cache.parquet"
df_cache = pd.read_parquet("data/geodata/address_cache.parquet")

# rename columns in df_cache to lowercase
df_cache.columns = df_cache.columns.str.lower()

# join df_lagenhet with df_cache on "title"
df_lagenhet = df_lagenhet.merge(df_cache, on="title", how="left")

# filter out rows where "lat" is null
df_lagenhet = df_lagenhet[df_lagenhet["lat"].notnull()]

# drop columns supplementary_area_sqm, lot_area_sqm, and leasehold_fee_per_year
# drop columns supplementary_area, lot_area, and leasehold_fee, land_right_fee, housing_association
df_lagenhet = df_lagenhet.drop(columns=["supplementary_area_sqm", "lot_area_sqm", "leasehold_fee_per_year", "supplementary_area", "lot_area", "leasehold_fee", "land_right_fee", "housing_association"])

# save a sample of df_lagenhet to "temp"
df_lagenhet.sample(1000).to_csv("temp/sample.csv", index=False)



# export raw data
df_lagenhet_full = df[df["Type"] == "Lägenhet"]

df_cache = pd.read_parquet("data/geodata/address_cache.parquet")

df_lagenhet_full = df_lagenhet_full.merge(df_cache, on="Title", how="left")

df_lagenhet_full = df_lagenhet_full[df_lagenhet_full["Lat"].notnull()]

# sample 2000 rows
df_lagenhet_full.sample(2000).to_csv("temp/sample_full.csv", index=False)





# read raw data from "hemnet_properties_2024-04-04_17-36-50.parquet"
df_raw = pd.read_parquet("data/raw/hemnet_properties_2024-04-04_17-36-50.parquet")

df_raw.columns