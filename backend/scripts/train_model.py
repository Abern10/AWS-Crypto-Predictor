import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
import numpy as np
from datetime import datetime, timezone
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_processed_data(currency):
    # Dummy function to simulate fetching processed data
    # Replace with actual data fetching logic
    if currency == 'bitcoin':
        data = {
            'timestamp': pd.date_range(start='2024-01-01', periods=150, freq='D'),
            'price': np.random.uniform(low=60000, high=70000, size=150)
        }
    elif currency == 'ethereum':
        data = {
            'timestamp': pd.date_range(start='2024-01-01', periods=150, freq='D'),
            'price': np.random.uniform(low=3000, high=4000, size=150)
        }
    df = pd.DataFrame(data)
    return df

def store_predictions(predictions, table_name):
    # Dummy function to simulate storing predictions
    # Replace with actual database or storage logic
    for prediction in predictions:
        logger.info(f"Storing prediction for {table_name}: {prediction}")

def train_and_predict_stacked(df, table_name, days_to_predict=30):
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)  # Convert to datetime
    df['price'] = pd.to_numeric(df['price'], errors='coerce')  # Ensure price is numeric and handle errors

    # Check for and handle any missing values
    if df['price'].isnull().any():
        logger.warning("Missing values found in 'price' column. Filling with the mean value.")
        df['price'].fillna(df['price'].mean(), inplace=True)

    # Prepare data for ARIMA model
    df.set_index('timestamp', inplace=True)
    df.index = pd.DatetimeIndex(df.index.values, freq='D')  # Set frequency to daily

    # Reset index to access timestamp column
    df['timestamp_unix'] = df.index.astype(np.int64) // 10**9  # Convert to Unix time for other models

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    meta_features = np.zeros((len(df), 3))
    meta_targets = np.zeros(len(df))

    for train_idx, valid_idx in kf.split(df):
        train_df, valid_df = df.iloc[train_idx], df.iloc[valid_idx]

        # Linear Regression
        lr = LinearRegression()
        lr.fit(train_df[['timestamp_unix']], train_df['price'])
        meta_features[valid_idx, 0] = lr.predict(valid_df[['timestamp_unix']])

        # ARIMA
        train_df_arima, valid_df_arima = df.iloc[train_idx], df.iloc[valid_idx]
        arima = ARIMA(train_df_arima['price'], order=(5, 1, 0))
        arima_fit = arima.fit()
        arima_forecast = arima_fit.forecast(len(valid_df_arima))
        meta_features[valid_idx, 1] = arima_forecast.values

        # Random Forest
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(train_df[['timestamp_unix']], train_df['price'])
        meta_features[valid_idx, 2] = rf.predict(valid_df[['timestamp_unix']])

        meta_targets[valid_idx] = valid_df['price']

    # Train meta-model
    meta_model = LinearRegression()
    meta_model.fit(meta_features, meta_targets)

    # Make predictions
    final_predictions = []
    last_timestamp_unix = df['timestamp_unix'].iloc[-1]
    future_timestamps_unix = [last_timestamp_unix + i * 86400 for i in range(1, days_to_predict + 1)]  # Add days in seconds

    for ts in future_timestamps_unix:
        lr_pred = lr.predict([[ts]])[0]
        arima_pred = arima_fit.forecast(steps=1).values[0]
        rf_pred = rf.predict([[ts]])[0]
        meta_feature = np.array([lr_pred, arima_pred, rf_pred]).reshape(1, -1)
        final_pred = meta_model.predict(meta_feature)[0]

        final_predictions.append({
            'timestamp': datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
            'predicted_price': final_pred
        })

    store_predictions(final_predictions, table_name)

if __name__ == "__main__":
    # Fetch data for Bitcoin
    logger.info("Fetching processed data for Bitcoin...")
    bitcoin_df = fetch_processed_data('bitcoin')
    logger.info(f"Fetched columns: {bitcoin_df.columns}")
    logger.info(f"Processed data sample: \n{bitcoin_df.head()}")

    # Train and predict for Bitcoin
    logger.info("Training and predicting for Bitcoin...")
    train_and_predict_stacked(bitcoin_df, 'predictions_bitcoin')

    # Fetch data for Ethereum
    logger.info("Fetching processed data for Ethereum...")
    ethereum_df = fetch_processed_data('ethereum')
    logger.info(f"Fetched columns: {ethereum_df.columns}")
    logger.info(f"Processed data sample: \n{ethereum_df.head()}")

    # Train and predict for Ethereum
    logger.info("Training and predicting for Ethereum...")
    train_and_predict_stacked(ethereum_df, 'predictions_ethereum')

    logger.info("Training and prediction completed.")