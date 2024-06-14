import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA
import mysql.connector
import logging
import os

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'train_model.log')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_file), logging.StreamHandler()])

def fetch_processed_data():
    try:
        db = mysql.connector.connect(
            host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',  # DB host (endpoint)
            user='abern8',  # DB username
            password='JettaGLI17!',  # DB password
            database='crypto_db'
        )
        cursor = db.cursor()

        cursor.execute("SELECT id, crypto, timestamp, price FROM processed_data")
        processed_data = cursor.fetchall()
        df = pd.DataFrame(processed_data, columns=['id', 'crypto', 'timestamp', 'price'])

        cursor.close()
        db.close()
        logging.info(f"Fetched columns: {df.columns}")
        logging.info(f"Processed data sample: \n{df.head()}")
        return df
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        raise

def train_and_predict(df, model_type, crypto):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df[df['crypto'] == crypto].copy()
    df.set_index('timestamp', inplace=True)
    df['price'] = df['price'].astype(float)  # Ensure price column is float

    X = np.array((df.index - df.index[0]).days).reshape(-1, 1)
    y = df['price'].values.astype(float)  # Ensure y is float

    if model_type == 'linear_regression':
        model = LinearRegression()
    elif model_type == 'random_forest':
        model = RandomForestRegressor(n_estimators=100)
    elif model_type == 'arima':
        model = ARIMA(y, order=(5, 1, 0))
    else:
        raise ValueError("Invalid model type specified.")

    if model_type == 'arima':
        model_fit = model.fit()
        predictions = model_fit.forecast(steps=30)
    else:
        model.fit(X, y)
        future_X = np.array([len(X) + i for i in range(1, 31)]).reshape(-1, 1)
        predictions = model.predict(future_X)

    future_dates = [df.index[-1] + timedelta(days=i) for i in range(1, 31)]
    return pd.DataFrame({'timestamp': future_dates, 'predicted_price': predictions})

def store_predictions(predictions, crypto):
    try:
        db = mysql.connector.connect(
            host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',  # DB host (endpoint)
            user='abern8',  # DB username
            password='JettaGLI17!',  # DB password
            database='crypto_db'
        )
        cursor = db.cursor()

        cursor.execute("DELETE FROM predictions WHERE crypto=%s", (crypto,))
        for _, row in predictions.iterrows():
            cursor.execute(
                "INSERT INTO predictions (crypto, timestamp, predicted_price) VALUES (%s, %s, %s)",
                (crypto, row['timestamp'], row['predicted_price'])
            )

        db.commit()
        cursor.close()
        db.close()
        logging.info(f"Stored predictions for {crypto} in the database.")
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        raise

if __name__ == "__main__":
    try:
        logging.info("Fetching processed data...")
        processed_data_df = fetch_processed_data()

        logging.info(f"Processed data: \n{processed_data_df.head()}")

        logging.info("Training and predicting for Bitcoin...")
        btc_predictions_lr = train_and_predict(processed_data_df, 'linear_regression', 'bitcoin')
        btc_predictions_rf = train_and_predict(processed_data_df, 'random_forest', 'bitcoin')
        btc_predictions_arima = train_and_predict(processed_data_df, 'arima', 'bitcoin')

        btc_predictions = pd.concat([btc_predictions_lr, btc_predictions_rf, btc_predictions_arima])
        store_predictions(btc_predictions, 'bitcoin')

        logging.info("Training and predicting for Ethereum...")
        eth_predictions_lr = train_and_predict(processed_data_df, 'linear_regression', 'ethereum')
        eth_predictions_rf = train_and_predict(processed_data_df, 'random_forest', 'ethereum')
        eth_predictions_arima = train_and_predict(processed_data_df, 'arima', 'ethereum')

        eth_predictions = pd.concat([eth_predictions_lr, eth_predictions_rf, eth_predictions_arima])
        store_predictions(eth_predictions, 'ethereum')
    except Exception as e:
        logging.error(f"Error in training and prediction: {e}")
        print(f"Error in training and prediction: {e}")