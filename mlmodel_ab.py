"""
MLModel module for analyzing simulation data and developing data-driven solutions.

This module uses machine learning techniques to analyze game simulation data and includes functions for:
    - Data preprocessing
    - Training and evaluating a Random Forest regression model
    - Training and evaluating a Polynomial regression model
    - Plotting actual vs. predicted values
"""

from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from data_ab import get_simulation_dataset, get_data_simulation

# Random Forest Regression and Polynomial Regression
# Supervised learning
# Dataset1, N = 5000
# Dataset2, N = 10000
# Dependant y = 'exp'
# Independent variables X = 'hero1_class', 'hero2_class', 'hero3_class'

# Test for Dataset1
# Random forest regression:
# RMSE: 13.023468377137092
# R-squared: 0.36218110782957313

# Polynomial regression:
# RMSE: 12.411438835398728 
# R-squared: 0.42072028345750256

#Dataset2 random forest regression
#RMSE: 15.501181916945496
#R-squared:: 0.12171738791769571

#Dataset2 polynomial regression
#RMSE: 15.513436783163018
#R-squared: 0.12032814023977545

def process_data(dataset_id):
    """Preprocess the simulation data."""
    df = get_simulation_dataset(dataset_id)

    df.drop(columns=['boss', 'hero1_name', 'hero2_name', 'hero3_name', 'hero1_talent5', 'hero2_talent5', 'hero3_talent5',], inplace=True)
    #df.fillna('', inplace=True)
    #df.fillna('No Talent', inplace=True)

    y = df['exp'].values.ravel()
    classes_df = df.iloc[:, 1:4] 

    #df = pd.get_dummies(df, columns=['hero1_class', 'hero2_class', 'hero3_class'], prefix=['hero1', 'hero2', 'hero3'])
    class_columns = ['hero1_class', 'hero2_class', 'hero3_class']

    #encoding for hero classes
    encoder = OneHotEncoder(sparse=False)
    encoded_classes = encoder.fit_transform(classes_df[class_columns])
    encoded_classes_df = pd.DataFrame(encoded_classes, columns=encoder.get_feature_names_out(class_columns))
    df_encoded = pd.concat([classes_df, encoded_classes_df], axis=1)
    df_encoded.drop(columns=class_columns, inplace=True)
    X = df_encoded

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)
    return X, y
X, y = process_data(2)

def random_forest_model():
    """Train and evaluate a Random Forest regression model."""
    regressor = RandomForestRegressor(n_estimators = 100, random_state = 0)
    regressor.fit(X_train, y_train)

    y_pred = regressor.predict(X_test) 
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    print(f'RMSE: {rmse}') 
    print(f'R-squared:: {r2}') 

def polynomial_regression_model():
    """Train and evaluate a Polynomial regression model."""
    poly = PolynomialFeatures(degree=2)
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)

    poly_reg = LinearRegression()
    poly_reg.fit(X_train_poly, y_train)

    y_pred = poly_reg.predict(X_test_poly)

    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    print(f'RMSE: {rmse}') 
    print("R-squared:", r2)

def plot_data():
    """Plot actual vs. predicted values."""
    y_test_series = pd.Series(y_test.flatten())
    y_predict_series = pd.Series(y_pred)
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test_series, y_predict_series, color='blue', alpha=0.5)
    plt.plot([min(y_test_series), max(y_test_series)], [min(y_test_series), max(y_test_series)], color='red')
    plt.title('Actual vs. Predicted Values')
    plt.xlabel('Actual Experience Gained')
    plt.ylabel('Predicted Experience Gained')
    plt.show()
