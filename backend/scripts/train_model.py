import mysql.connector
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

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
    return df

# Store predictions
def store_predictions(predictions, table_name):
    db = get_db_connection()
    cursor = db.cursor()
    
    for prediction in predictions:
        cursor.execute(
            f"INSERT INTO {table_name} (timestamp, predicted_price) VALUES (%s, %s)",
            (prediction['timestamp'], prediction['predicted_price'])
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
            (prediction['timestamp'], model_name, prediction['predicted_price'], None, None, None)
        )
    
    db.commit()
    cursor.close()
    db.close()

# Model training and prediction functions
def arima_predictions(train_data, forecast_periods):
    train_data = train_data.astype(float)
    model = ARIMA(train_data, order=(5, 1, 0))
    model_fit = model.fit()
    predictions = model_fit.forecast(steps=forecast_periods)
    return predictions

def linear_regression_predictions(train_data, features, forecast_periods):
    model = LinearRegression()
    X_train = features
    y_train = train_data
    model.fit(X_train, y_train)
    
    # Log shapes and data types
    logger.info(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
    logger.info(f"Features columns: {features.columns}")
    
    # Prepare features for forecasting
    X_forecast = np.arange(len(train_data), len(train_data) + forecast_periods).reshape(-1, 1)
    
    # Calculate EMA for features
    ema_span = 7  # Example span for EMA
    features_ema = features.ewm(span=ema_span, adjust=False).mean().iloc[-1]
    features_forecast = np.hstack([X_forecast] + [np.full((forecast_periods, 1), features_ema[col]) for col in features.columns if col != 'timestamp_ml'])
    features_forecast_df = pd.DataFrame(features_forecast, columns=[col for col in features.columns if col != 'timestamp_ml'])
    
    predictions = model.predict(features_forecast_df)
    return predictions

def random_forest_predictions(train_data, features, forecast_periods):
    model = RandomForestRegressor(n_estimators=100)
    X_train = features
    y_train = train_data
    model.fit(X_train, y_train)
    
    # Log shapes and data types
    logger.info(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
    logger.info(f"Features columns: {features.columns}")
    
    # Prepare features for forecasting
    X_forecast = np.arange(len(train_data), len(train_data) + forecast_periods).reshape(-1, 1)
    
    # Calculate EMA for features
    ema_span = 7  # Example span for EMA
    features_ema = features.ewm(span=ema_span, adjust=False).mean().iloc[-1]
    features_forecast = np.hstack([X_forecast] + [np.full((forecast_periods, 1), features_ema[col]) for col in features.columns if col != 'timestamp_ml'])
    features_forecast_df = pd.DataFrame(features_forecast, columns=[col for col in features.columns if col != 'timestamp_ml'])
    
    predictions = model.predict(features_forecast_df)
    return predictions

def meta_model_predictions(arima_preds, lr_preds, rf_preds):
    X_meta = np.column_stack((arima_preds, lr_preds, rf_preds))
    model = LinearRegression()
    model.fit(X_meta, arima_preds)
    meta_predictions = model.predict(X_meta)
    return meta_predictions

def train_and_predict(crypto_name):
    logger.info(f"Fetching processed data for {crypto_name}...")
    data_df = fetch_processed_data(crypto_name)
    
    # Use 100% of the data for training
    train_data = data_df['price']
    features = data_df[['timestamp_ml', 'volume', 'market_cap', 'open', 'high', 'low', 'close']].dropna()
    
    forecast_periods = 30  # Predict for the next 30 days
    
    logger.info(f"Training and predicting for {crypto_name}...")
    
    # Create a separate variable for prices to avoid warnings
    prices = train_data.values
    
    arima_preds = arima_predictions(prices, forecast_periods)
    lr_preds = linear_regression_predictions(prices, features, forecast_periods)
    rf_preds = random_forest_predictions(prices, features, forecast_periods)
    
    meta_predictions = meta_model_predictions(arima_preds, lr_preds, rf_preds)
    
    final_predictions = []
    start_date = data_df['timestamp_ml'].iloc[-1] + timedelta(days=1)
    for i in range(forecast_periods):
        final_predictions.append({
            'timestamp': (start_date + timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S'),
            'predicted_price': meta_predictions[i]
        })
    
    logger.info(f"Storing final predictions for {crypto_name}...")
    store_predictions(final_predictions, f'predictions_{crypto_name.lower()}')
    store_past_predictions(final_predictions, f'past_predictions_{crypto_name.lower()}', 'meta_model')
    logger.info(f"Training and prediction completed for {crypto_name}.")

if __name__ == "__main__":
    logger.info("Processing data for Bitcoin...")
    train_and_predict('bitcoin')

    logger.info("Processing data for Ethereum...")
    train_and_predict('ethereum')