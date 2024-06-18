import mysql.connector
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
from statsmodels.tsa.arima.model import ARIMA
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("../logs/train_model.log"),
    logging.StreamHandler()
])
logger = logging.getLogger(__name__)

def fetch_processed_data(table_name):
    db = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',
        user='abern8',
        password='JettaGLI17!',
        database='crypto_db'
    )
    cursor = db.cursor()
    
    query = f"SELECT * FROM {table_name}"
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
    cursor.execute(f"DELETE FROM {table_name}")
    for pred in predictions:
        cursor.execute(
            f"INSERT INTO {table_name} (timestamp, predicted_price) VALUES (%s, %s)",
            (pred['timestamp'], pred['predicted_price'])
        )
    db.commit()
    cursor.close()
    db.close()

def train_and_predict_stacked(df, table_name, days_to_predict=30):
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)  # Convert to datetime
    df['timestamp'] = df['timestamp'].apply(lambda x: x.timestamp())  # Convert to Unix time
    df['price'] = pd.to_numeric(df['price'])  # Ensure price is numeric
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    meta_features = np.zeros((len(df), 3))
    meta_targets = np.zeros(len(df))

    for train_idx, valid_idx in kf.split(df):
        train_df, valid_df = df.iloc[train_idx], df.iloc[valid_idx]

        # Linear Regression
        lr = LinearRegression()
        lr.fit(train_df[['timestamp']], train_df['price'])
        meta_features[valid_idx, 0] = lr.predict(valid_df[['timestamp']])

        # ARIMA
        arima = ARIMA(train_df['price'], order=(5, 1, 0))
        arima_fit = arima.fit()
        arima_forecast = arima_fit.forecast(len(valid_df))
        meta_features[valid_idx, 1] = arima_forecast.values

        # Random Forest
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(train_df[['timestamp']], train_df['price'])
        meta_features[valid_idx, 2] = rf.predict(valid_df[['timestamp']])

        meta_targets[valid_idx] = valid_df['price']

    # Train meta-model
    meta_model = LinearRegression()
    meta_model.fit(meta_features, meta_targets)

    # Make predictions
    final_predictions = []
    last_timestamp = df['timestamp'].iloc[-1]
    future_timestamps = [last_timestamp + i * 86400 for i in range(1, days_to_predict + 1)]  # Add days in seconds

    for ts in future_timestamps:
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
    logger.info("Fetching processed data for Bitcoin...")
    btc_df = fetch_processed_data('processed_data_bitcoin')
    logger.info(f"Fetched columns: {btc_df.columns}")
    logger.info(f"Processed data sample: \n{btc_df.head()}")

    logger.info("Training and predicting for Bitcoin...")
    train_and_predict_stacked(btc_df, 'predictions_bitcoin')

    logger.info("Fetching processed data for Ethereum...")
    eth_df = fetch_processed_data('processed_data_ethereum')
    logger.info(f"Fetched columns: {eth_df.columns}")
    logger.info(f"Processed data sample: \n{eth_df.head()}")

    logger.info("Training and predicting for Ethereum...")
    train_and_predict_stacked(eth_df, 'predictions_ethereum')

    logger.info("Training and prediction completed.")