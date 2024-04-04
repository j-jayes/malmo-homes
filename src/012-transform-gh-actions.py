import pandas as pd
import re

def clean_and_transform_hemnet_data(input_file_path, output_file_path):
    # Load the dataset
    data = pd.read_parquet(input_file_path)

    # Numeric Conversion
    def clean_numeric(column):
        return pd.to_numeric(column.str.replace(' kr/m²', '').str.replace(' kr', '').str.replace(' ', '').str.replace('+', '').str.extract('(\d+)')[0], errors='coerce')

    data['Slutpris'] = clean_numeric(data['Slutpris'])
    data['Utgångspris'] = clean_numeric(data['Utgångspris'])
    data['Pris per kvadratmeter'] = clean_numeric(data['Pris per kvadratmeter'])
    data['Avgift'] = clean_numeric(data['Avgift'])
    data['Driftskostnad'] = clean_numeric(data['Driftskostnad'])

    # Date Handling
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
    for swedish, english in swedish_to_english_months.items():
        data['Sale Date'] = data['Sale Date'].str.replace(swedish, english)
    data['Sale Date'] = pd.to_datetime(data['Sale Date'].str.extract('(\d{2} \w+ \d{4})')[0], errors='coerce')
    data['Sale Year'] = data['Sale Date'].dt.year
    data['Sale Month'] = data['Sale Date'].dt.month
    data['Sale Day'] = data['Sale Date'].dt.day

    # Transform 'Balkong' and 'Uteplats' into binary format
    data['Balkong'] = data['Balkong'].map({'Ja': 1, 'Nej': 0})
    data['Uteplats'] = data['Uteplats'].map({'Ja': 1, 'Nej': 0})

    # Extract floor number and elevator presence
    data['Floor Number'] = data['Våning'].str.extract('(\d+)').astype(float)
    data['Elevator Presence'] = data['Våning'].apply(lambda x: 1 if 'hiss finns' in str(x) else 0)

    # Correctly extract numerical area values
    data['Biarea (m²)'] = data['Biarea'].str.replace(' m²', '').str.replace(',', '.').astype(float)
    data['Tomtarea (m²)'] = data['Tomtarea'].str.replace(' m²', '').str.replace(',', '.').astype(float)
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

    # Save the cleaned data to a new csv file
    data.to_parquet(output_file_path, index=False)

    return data
