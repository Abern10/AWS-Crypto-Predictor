import mysql.connector
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import warnings

warnings.filterwarnings("ignore")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("../logs/train_model.log"),
    logging.StreamHandler()
])
logger = logging.getLogger(__name__)

def fetch_processed_data(crypto_name):
    db = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',
        user='abern8',
        password='JettaGLI17!',
        database='crypto_db'
    )
    cursor = db.cursor()
    
    query = f"SELECT timestamp, price_arima, price_other FROM processed_data_{crypto_name.lower()}"
    cursor.execute(query)
    data = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=columns)
    cursor.close()
    db.close()
    return df

def store_predictions(predictions, table_name):
    db = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',
        user='abern8',
        password='JettaGLI17!',
        database='crypto_db'
    )
    cursor = db.cursor()
    
    for prediction in predictions:
        cursor.execute(
            f"INSERT INTO {table_name} (timestamp, predicted_price) VALUES (%s, %s)",
            (prediction['timestamp'], prediction['predicted_price'])
        )
    
    db.commit()
    cursor.close()
    db.close()

def arima_predictions(train_data, forecast_periods):
    train_data = train_data.astype(float)  # Ensure the data is numeric
    model = ARIMA(train_data, order=(5, 1, 0))
    model_fit = model.fit()
    predictions = model_fit.forecast(steps=forecast_periods)
    return predictions

def linear_regression_predictions(train_data, forecast_periods):
    model = LinearRegression()
    X_train = np.arange(len(train_data)).reshape(-1, 1)
    y_train = train_data.values
    model.fit(X_train, y_train)
    X_forecast = np.arange(len(train_data), len(train_data) + forecast_periods).reshape(-1, 1)
    predictions = model.predict(X_forecast)
    return predictions

def random_forest_predictions(train_data, forecast_periods):
    model = RandomForestRegressor(n_estimators=100)
    X_train = np.arange(len(train_data)).reshape(-1, 1)
    y_train = train_data.values
    model.fit(X_train, y_train)
    X_forecast = np.arange(len(train_data), len(train_data) + forecast_periods).reshape(-1, 1)
    predictions = model.predict(X_forecast)
    return predictions

def meta_model_predictions(arima_preds, lr_preds, rf_preds, actual_values):
    X_meta = np.column_stack((arima_preds, lr_preds, rf_preds))
    model = LinearRegression()
    model.fit(X_meta, actual_values)
    meta_predictions = model.predict(X_meta)
    return meta_predictions

def train_and_predict(crypto_name):
    logger.info(f"Fetching processed data for {crypto_name}...")
    data_df = fetch_processed_data(crypto_name)
    data_df['timestamp'] = pd.to_datetime(data_df['timestamp'])
    data_df.set_index('timestamp', inplace=True)
    
    train_data_arima, test_data_arima = train_test_split(data_df['price_arima'], test_size=0.2, shuffle=False)
    train_data_other, test_data_other = train_test_split(data_df['price_other'], test_size=0.2, shuffle=False)
    
    forecast_periods = len(test_data_arima)
    
    logger.info(f"Training and predicting for {crypto_name}...")
    
    arima_preds = arima_predictions(train_data_arima, forecast_periods)
    lr_preds = linear_regression_predictions(train_data_other, forecast_periods)
    rf_preds = random_forest_predictions(train_data_other, forecast_periods)
    
    actual_values = test_data_arima.values
    meta_predictions = meta_model_predictions(arima_preds, lr_preds, rf_preds, actual_values)
    
    final_predictions = []
    start_date = test_data_arima.index[0]
    for i in range(forecast_periods):
        final_predictions.append({
            'timestamp': (start_date + timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S'),
            'predicted_price': meta_predictions[i]
        })
    
    logger.info(f"Storing final predictions for {crypto_name}...")
    store_predictions(final_predictions, f'predictions_{crypto_name.lower()}')
    logger.info(f"Training and prediction completed for {crypto_name}.")

if __name__ == "__main__":
    logger.info("Processing data for Bitcoin...")
    train_and_predict('bitcoin')

    logger.info("Processing data for Ethereum...")
    train_and_predict('ethereum')