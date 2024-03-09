import pandas as pd
import re

# Load the dataset
file_path = 'temp/hemnet_properties_sample.csv'
data = pd.read_csv(file_path)

# Display the first few rows of the dataset to understand its structure
data.head()


# Step 1: Numeric Conversion
# Define a function to clean numeric fields
def clean_numeric(column):
    return pd.to_numeric(column.str.replace(' kr/m²', '').str.replace(' kr', '').str.replace(' ', '').str.replace('+', '').str.extract('(\d+)')[0], errors='coerce')

# Apply the function to the relevant columns
data['Slutpris'] = clean_numeric(data['Slutpris'])
data['Utgångspris'] = clean_numeric(data['Utgångspris'])
data['Pris per kvadratmeter'] = clean_numeric(data['Pris per kvadratmeter'])
data['Avgift'] = clean_numeric(data['Avgift'])
data['Driftskostnad'] = clean_numeric(data['Driftskostnad'])

# Step 2: Date Handling
# Convert 'Sale Date' to datetime format and extract year, month, day

# Map of Swedish month names to English
swedish_to_english_months = {
    'januari': 'January',
    'februari': 'February',
    'mars': 'March',
    'april': 'April',
    'maj': 'May',
    'juni': 'June',
    'juli': 'July',
    'augusti': 'August',
    'september': 'September',
    'oktober': 'October',
    'november': 'November',
    'december': 'December'
}

# Replace Swedish month names with English in the 'Sale Date' column
for swedish, english in swedish_to_english_months.items():
    data['Sale Date'] = data['Sale Date'].str.replace(swedish, english)

# Convert 'Sale Date' to datetime format again and extract year, month, day
data['Sale Date'] = pd.to_datetime(data['Sale Date'].str.extract('(\d{2} \w+ \d{4})')[0], errors='coerce')
data['Sale Year'] = data['Sale Date'].dt.year
data['Sale Month'] = data['Sale Date'].dt.month
data['Sale Day'] = data['Sale Date'].dt.day

# Display the cleaned 'Sale Date' data
data[['Sale Date', 'Sale Year', 'Sale Month', 'Sale Day']].head()


# view data
data.head()

# write the cleaned data to a new csv file
cleaned_file_path = 'temp/hemnet_properties_sample_cleaned.csv'

data.to_csv(cleaned_file_path, index=False)


import re

# Transform 'Balkong' and 'Uteplats' into binary format
data['Balkong'] = data['Balkong'].map({'Ja': 1, 'Nej': 0})
data['Uteplats'] = data['Uteplats'].map({'Ja': 1, 'Nej': 0})

# Extract floor number from 'Våning' and create a binary column for elevator presence
data['Floor Number'] = data['Våning'].str.extract('(\d+)').astype(float)  # Extract the first number as floor
data['Elevator Presence'] = data['Våning'].apply(lambda x: 1 if 'hiss finns' in str(x) else 0)

# Correctly extract numerical area values from 'Biarea' and 'Tomtarea' (including handling commas for decimal points)
data['Biarea (m²)'] = data['Biarea'].str.replace(' m²', '').str.replace(',', '.').astype(float)
data['Tomtarea (m²)'] = data['Tomtarea'].str.replace(' m²', '').str.replace(',', '.').astype(float)

# Extract numerical value from 'Arrende' correctly handling space and kr/år
data['Arrende (kr/år)'] = data['Arrende'].str.replace(' kr/år', '').str.replace(' ', '').astype(float)


# Translation of column names to English and conversion to snake case
column_name_translation = {
    'Slutpris': 'final_price',
    'Title': 'title',
    'Type': 'type',
    'Location': 'location',
    'Sale Date': 'sale_date',
    'Agent Name': 'agent_name',
    'Agent Link': 'agent_link',
    'Pris per kvadratmeter': 'price_per_square_meter',
    'Utgångspris': 'starting_price',
    'Prisutveckling': 'price_development',
    'Antal rum': 'number_of_rooms',
    'Boarea': 'living_area',
    'Avgift': 'fee',
    'Driftskostnad': 'operational_cost',
    'Biarea': 'supplementary_area',
    'Tomtarea': 'lot_area',
    'Uteplats': 'outdoor_space',
    'Arrende': 'leasehold_fee',
    'Förening': 'housing_association',
    'Sale Year': 'sale_year',
    'Sale Month': 'sale_month',
    'Sale Day': 'sale_day',
    'Balkong': 'balcony',
    'Våning': 'floor',
    'Floor Number': 'floor_number',
    'Elevator Presence': 'elevator_presence',
    'Biarea (m²)': 'supplementary_area_sqm',
    'Tomtarea (m²)': 'lot_area_sqm',
    'Arrende (kr/år)': 'leasehold_fee_per_year',
    'Bostadstyp': 'type_2',
    'Byggår': 'year_of_construction',
    'Upplåtelseform': 'release_form'
}


# Rename the columns
data = data.rename(columns=column_name_translation)

data

