import mysql.connector
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import logging
from arima_model import arima_predictions
from linear_regression_model import linear_regression_predictions
from random_forest_model import random_forest_predictions
from xgboost_model import xgboost_predictions
from meta_model import meta_model_predictions
from sklearn.preprocessing import StandardScaler

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("../logs/train_model.log"),
    logging.StreamHandler()
])
logger = logging.getLogger(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',
        user='abern8',
        password='JettaGLI17!',
        database='crypto_db'
    )

# Fetch processed data
def fetch_processed_data(crypto_name):
    db = get_db_connection()
    cursor = db.cursor()
    
    query = f"SELECT timestamp_ml, price, volume, market_cap, open, high, low, close FROM processed_data_{crypto_name.lower()}"
    cursor.execute(query)
    data = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=columns)
    cursor.close()
    db.close()

    logger.info(f"Fetched data columns: {df.columns}")
    logger.info(f"Fetched data types:\n{df.dtypes}")
    logger.info(f"First few rows of fetched data:\n{df.head()}")
    
    return df

# Store predictions
def store_predictions(predictions, table_name):
    db = get_db_connection()
    cursor = db.cursor()
    
    cursor.execute(f"TRUNCATE TABLE {table_name}")
    
    for prediction in predictions:
        cursor.execute(
            f"INSERT INTO {table_name} (timestamp, predicted_price) VALUES (%s, %s)",
            (prediction['timestamp'], float(prediction['predicted_price']))  # Convert to float
        )
    
    db.commit()
    cursor.close()
    db.close()

def store_past_predictions(predictions, table_name, model_name):
    db = get_db_connection()
    cursor = db.cursor()
    
    for prediction in predictions:
        cursor.execute(
            f"INSERT INTO {table_name} (timestamp, model_name, predicted_price, actual_price, prediction_error, prediction_accuracy) VALUES (%s, %s, %s, %s, %s, %s)",
            (prediction['timestamp'], model_name, float(prediction['predicted_price']), None, None, None)  # Convert to float
        )
    
    db.commit()
    cursor.close()
    db.close()

def normalize_features(features):
    scaler = StandardScaler()
    normalized_features = scaler.fit_transform(features)
    return pd.DataFrame(normalized_features, columns=features.columns)

def train_and_predict(crypto_name):
    logger.info(f"Fetching processed data for {crypto_name}...")
    data_df = fetch_processed_data(crypto_name)
    
    train_data = data_df['price']
    features = data_df[['timestamp_ml', 'volume', 'market_cap', 'open', 'high', 'low', 'close']].dropna()
    
    features = normalize_features(features)
    
    forecast_periods = 30  # Predict for the next 30 days
    
    logger.info(f"Training and predicting for {crypto_name}...")
    
    prices = train_data.values
    last_timestamp = data_df['timestamp_ml'].iloc[-1]
    
    arima_preds = arima_predictions(prices, forecast_periods)
    lr_preds = linear_regression_predictions(prices, features, forecast_periods, last_timestamp)
    rf_preds = random_forest_predictions(prices, features, forecast_periods, last_timestamp)
    xgb_preds = xgboost_predictions(prices, features, forecast_periods, last_timestamp)
    
    meta_predictions = meta_model_predictions(arima_preds, lr_preds, rf_preds, xgb_preds)
    
    final_predictions = []
    start_date = last_timestamp + 86400000  # Add one day in milliseconds
    for i in range(forecast_periods):
        final_predictions.append({
            'timestamp': datetime.fromtimestamp((start_date + i * 86400000) / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),  # Convert to datetime and format
            'predicted_price': meta_predictions[i]
        })
    
    logger.info(f"Storing final predictions for {crypto_name}...")
    store_predictions(final_predictions, f'predictions_{crypto_name.lower()}')
    store_past_predictions(final_predictions, f'past_predictions_{crypto_name.lower()}', 'meta_model')
    logger.info(f"Training and prediction completed for {crypto_name}.")

if __name__ == "__main__":
    logger.info("Processing data for Bitcoin…")
    train_and_predict('bitcoin')
    logger.info("Processing data for Ethereum...")
    train_and_predict('ethereum')