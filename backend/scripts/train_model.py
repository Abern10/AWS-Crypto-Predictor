import mysql.connector
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("train_model.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

def fetch_processed_data():
    conn = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',  # DB host (endpoint)
        user='abern8',  # DB username
        password='JettaGLI17!',  # DB password
        database='crypto_db'
    )
    cursor = conn.cursor()
    
    query = "SELECT crypto, timestamp, price, rolling_mean FROM processed_data"
    cursor.execute(query)
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return pd.DataFrame(rows, columns=['crypto', 'timestamp', 'price', 'rolling_mean'])

def train_and_predict(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
    
    predictions = []
    
    for crypto in df['crypto'].unique():
        crypto_df = df[df['crypto'] == crypto]
        crypto_df = crypto_df.dropna()  # Drop rows with missing values
        
        X = np.arange(len(crypto_df)).reshape(-1, 1)
        y = crypto_df['price'].values
        
        # Linear Regression
        lr_model = LinearRegression()
        lr_model.fit(X, y)
        
        # ARIMA
        arima_model = ARIMA(y, order=(5, 1, 0))
        arima_model_fit = arima_model.fit()
        
        # Random Forest
        rf_model = RandomForestRegressor(n_estimators=100)
        rf_model.fit(X, y)
        
        future_days = 30
        future_X = np.arange(len(crypto_df), len(crypto_df) + future_days).reshape(-1, 1)
        future_timestamps = [crypto_df.index[-1] + timedelta(days=i) for i in range(1, future_days + 1)]
        
        lr_predictions = lr_model.predict(future_X)
        arima_predictions = arima_model_fit.forecast(steps=future_days)
        rf_predictions = rf_model.predict(future_X)
        
        combined_predictions = (lr_predictions + arima_predictions + rf_predictions) / 3
        
        predictions.extend(zip([crypto] * future_days, future_timestamps, combined_predictions))
    
    return pd.DataFrame(predictions, columns=['crypto', 'timestamp', 'prediction'])

def clear_predictions_table():
    conn = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',  # DB host (endpoint)
        user='abern8',  # DB username
        password='JettaGLI17!',  # DB password
        database='crypto_db'
    )
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM predictions")
    conn.commit()
    
    cursor.close()
    conn.close()

def store_predictions(df):
    conn = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',  # DB host (endpoint)
        user='abern8',  # DB username
        password='JettaGLI17!',  # DB password
        database='crypto_db'
    )
    cursor = conn.cursor()
    
    for index, row in df.iterrows():
        cursor.execute(
            "INSERT INTO predictions (crypto, timestamp, prediction) VALUES (%s, %s, %s)",
            (row['crypto'], row['timestamp'], row['prediction'])
        )
    
    conn.commit()
    cursor.close()
    conn.close()

def main():
    try:
        logger.info("Fetching processed data...")
        processed_data_df = fetch_processed_data()
        
        logger.info("Training model and generating predictions...")
        predictions_df = train_and_predict(processed_data_df)
        
        logger.info("Clearing predictions table...")
        clear_predictions_table()
        
        logger.info("Storing new predictions...")
        store_predictions(predictions_df)
        
        logger.info("Model training and prediction storing completed.")
    except Exception as e:
        logger.error(f"Error in model training and prediction: {e}")
        print(f"Error in model training and prediction: {e}")

if __name__ == "__main__":
    main()