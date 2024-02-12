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
import operator

# Random Forest Regression
# Supervised learning
# Dependant y = 'exp'
# Independent variables X = 'hero1_class', 'hero2_class', 'hero3_class'
# Plot of dataset1 similar to arctangent function

# Based on visual inspection of plot, polynomial regression might be better fit

df = get_simulation_dataset(1)
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

def random_forest_model():
    regressor = RandomForestRegressor(n_estimators = 100, random_state = 0)
    regressor.fit(X_train, y_train)

    y_pred = regressor.predict(X_test) 
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    print(f'RMSE: {rmse}') #13.023468377137092
    print(f'R-squared:: {r2}') #0.36218110782957313


poly = PolynomialFeatures(degree=2)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

poly_reg = LinearRegression()
poly_reg.fit(X_train_poly, y_train)

y_pred = poly_reg.predict(X_test_poly)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
print(f'RMSE: {rmse}') #12.411438835398728 
print("R-squared:", r2) #0.42072028345750256


def plot_data():
    y_test_series = pd.Series(y_test.flatten())
    y_predict_series = pd.Series(y_pred)
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test_series, y_predict_series, color='blue', alpha=0.5)
    plt.plot([min(y_test_series), max(y_test_series)], [min(y_test_series), max(y_test_series)], color='red')
    plt.title('Actual vs. Predicted Values')
    plt.xlabel('Actual Experience Gained')
    plt.ylabel('Predicted Experience Gained')
    plt.show()
plot_data()

