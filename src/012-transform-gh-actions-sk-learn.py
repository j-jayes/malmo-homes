from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np

# ExtendedCleanNumericTransformer as discussed
class ExtendedCleanNumericTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, standard_columns, area_columns=None, cost_columns=None):
        self.standard_columns = standard_columns
        self.area_columns = area_columns if area_columns is not None else []
        self.cost_columns = cost_columns if cost_columns is not None else []

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        existing_columns = X.columns
        for column in self.standard_columns + self.area_columns + self.cost_columns:
            if column in existing_columns:
                if column in self.standard_columns:
                    X[column] = pd.to_numeric(X[column].astype(str).str.replace(' kr/m²', '')
                                              .str.replace(' kr', '')
                                              .str.replace(' rum', '')
                                              .str.replace(' ', '')
                                              .str.replace('+', '')
                                              .str.extract('(\d+)')[0], errors='coerce')
                elif column in self.area_columns:
                    X[column] = pd.to_numeric(X[column].astype(str).str.replace(' m²', '').str.replace(',', '.'), errors='coerce')
                elif column in self.cost_columns:
                    X[column] = pd.to_numeric(X[column].astype(str).str.replace(' kr/år', '').str.replace(' ', ''), errors='coerce')
        return X

# DateTransformer as discussed
class DateTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, date_column):
        self.date_column = date_column
        self.swedish_to_english_months = {
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

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        for swedish, english in self.swedish_to_english_months.items():
            X[self.date_column] = X[self.date_column].str.replace(swedish, english)
        X[self.date_column] = pd.to_datetime(X[self.date_column].str.extract('(\d{2} \w+ \d{4})')[0], errors='coerce')
        X['Sale Year'] = X[self.date_column].dt.year
        X['Sale Month'] = X[self.date_column].dt.month
        X['Sale Day'] = X[self.date_column].dt.day
        return X

# FloorElevatorTransformer as discussed
class FloorElevatorTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, column):
        self.column = column

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['Floor Number'] = X[self.column].str.extract('(\d+)').astype(float)
        # Add a column called "Top Floor Number" to indicate the top floor number. It is the second number in the range if there is a range separated by "av"
        X['Top Floor Number'] = X[self.column].str.extract('av (\d+)').astype(float)

        def elevator_presence(row):
            if row is None:
                return np.nan
            elif 'hiss finns ej' in row:
                return 0
            elif 'hiss finns' in row:
                return 1
            else:
                return np.nan

        X['Elevator Presence'] = X[self.column].apply(elevator_presence)
        return X
    
# Create a class to code Nej and Ja to 0 and 1 for columns Uteplats and Balkong
class BinaryTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        for column in self.columns:
            X[column] = X[column].map({'Ja': 1, 'Nej': 0})
        return X
    
# Create a class to rename columns
class RenameColumnsTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, column_name_translation):
        self.column_name_translation = column_name_translation

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.rename(columns=self.column_name_translation)

# Define the column name translations
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
    'Top Floor Number': 'top_floor_number',
    'Elevator Presence': 'elevator_presence',
    # Adjusted for columns directly mentioned
    'Lat': 'latitude',
    'Long': 'longitude',
    # Additional translations if necessary
    'Tomträttsavgäld': 'land_right_fee',
    'Byggår': 'year_of_construction',
    'Bostadstyp': 'type_2',
    'Upplåtelseform': 'ownership_form',
}

# Assemble the pipeline
pipeline = Pipeline([
    ('extended_clean_numeric', ExtendedCleanNumericTransformer(
        standard_columns=['Slutpris', 'Utgångspris', 'Pris per kvadratmeter', 'Avgift', 'Driftskostnad', 'Byggår', 'Antal rum'],
        area_columns=['Biarea', 'Tomtarea', 'Boarea'],
        cost_columns=['Arrende']
    )),
    ('handle_date', DateTransformer(date_column='Sale Date')),
    ('floor_elevator', FloorElevatorTransformer(column='Våning')),
    ('binary_transformer', BinaryTransformer(columns=['Uteplats', 'Balkong'])),
    ('rename_columns', RenameColumnsTransformer(column_name_translation=column_name_translation)),

])

# Load the data again to apply the pipeline
data = pd.read_parquet("data/interim/hemnet_properties_cache.parquet")

# Apply the pipeline to the data
transformed_data = pipeline.fit_transform(data)

# Save the transformed data to a parquet file in "data/processed"
transformed_data.to_parquet("data/processed/hemnet_properties_transformed.parquet")