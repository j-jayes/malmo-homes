import pandas as pd
from skimpy import skim


# read in the parquet file from "output/hemnet_properties_2024-02-23.parquet"
df = pd.read_parquet("output/hemnet_properties_cache.parquet")

df

skim(df)

# sample 200 rows from the dataframe
df_sample = df.sample(200)

# write df sample to a csv file in a folder called "temp", and create temp folder if it doesn't exist
import os
os.makedirs("temp", exist_ok=True)

df_sample.to_csv("temp/hemnet_properties_sample.csv", index=False)





# read in all the files in "output" folder that contain "_final.parquet"
import glob

# get all the parquet files in the output folder
parquet_files = glob.glob("output/*_final.parquet")

# read in all the parquet files
dfs = [pd.read_parquet(file) for file in parquet_files]

dfs

# concatenate the dataframes
df_all = pd.concat(dfs, ignore_index=True)

# save to output folder calling the file "hemnet_properties_cache.parquet"
df_all.to_parquet("output/hemnet_properties_cache.parquet")

df_links = pd.read_parquet("output/hemnet_links_total.parquet")

# read in the parquet file from "output/hemnet_properties_final.parquet"
df_final = pd.read_parquet("output/hemnet_properties_cache.parquet")

# drop duplicates from df_final
df_final = df_final.drop_duplicates()

# count type of properties
df_final["Type"].value_counts()