from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd

# Load the dataset
df = pd.read_csv('temp/hemnet_properties.csv')

# Separate the target variable and predictors
X = df.drop('final_price', axis=1)
y = df['final_price']

# Splitting dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Selecting numerical and categorical columns (assuming 'location' is the only categorical column for simplicity)
numeric_features = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
numeric_features.remove('sale_year')
numeric_features.remove('sale_month')
numeric_features.remove('sale_day')
categorical_features = ['location']

# Creating transformers for numerical and categorical data
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))])

# Combining transformers into a preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)])

# Creating the XGBoost regression pipeline
xgb_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('regressor', XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, random_state=42))])

# Training the model
xgb_pipeline.fit(X_train, y_train)

# Predicting and evaluating the model
y_pred = xgb_pipeline.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"RMSE: {rmse}")





from sklearn.linear_model import LassoCV

# Creating the regularized regression (Lasso) pipeline
lasso_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                 ('regressor', LassoCV(cv=5, random_state=42))])

# Training the Lasso model
lasso_pipeline.fit(X_train, y_train)

# Extracting the best alpha (regularization strength) found by CV
best_alpha = lasso_pipeline.named_steps['regressor'].alpha_
print(f"Best alpha (regularization strength): {best_alpha}")

# Extracting feature names after preprocessing
feature_names = (lasso_pipeline.named_steps['preprocessor']
                 .transformers_[0][2] + 
                 list(lasso_pipeline.named_steps['preprocessor']
                 .named_transformers_['cat']
                 .named_steps['onehot']
                 .get_feature_names_out(categorical_features)))

# Extracting coefficients
coefficients = lasso_pipeline.named_steps['regressor'].coef_

# Combining feature names and coefficients in a DataFrame
# where feature_names is a list of column names and coefficients is an array of coefficients
coef_df = pd.DataFrame({
    'Feature': feature_names,
    'Coefficient': coefficients
}).sort_values(by='Coefficient', key=abs, ascending=False)

# Displaying features with the highest absolute coefficients
print(coef_df[coef_df['Coefficient'] != 0])
