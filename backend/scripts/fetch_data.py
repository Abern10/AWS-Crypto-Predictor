import requests
import pandas as pd
from datetime import datetime
import mysql.connector
import logging
import os
import time

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'fetch_data.log')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_file), logging.StreamHandler()])

# Replace with your actual API URL and key
API_URL = 'https://api.coingecko.com/api/v3/coins/markets'
API_KEY = 'your_api_key'  # Not used in this example as CoinGecko doesn't require it

def fetch_data(crypto: str, days: int):
    params = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'daily',
        'ids': crypto
    }

    response = requests.get(API_URL, params=params)
    data = response.json()

    prices = data['prices']
    timestamps = [datetime.utcfromtimestamp(price[0] / 1000).strftime('%Y-%m-%d %H:%M:%S') for price in prices]
    values = [price[1] for price in prices]

    df = pd.DataFrame({
        'timestamp': timestamps,
        'price': values
    })

    return df

def store_data(df: pd.DataFrame, crypto: str):
    db = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',  # DB host (endpoint)
        user='abern8',  # DB username
        password='JettaGLI17!',  # DB password
        database='crypto_db'
    )

    cursor = db.cursor()

    for index, row in df.iterrows():
        timestamp = row['timestamp']
        price = row['price']

        cursor.execute(f"SELECT COUNT(*) FROM raw_data WHERE crypto='{crypto}' AND timestamp='{timestamp}'")
        result = cursor.fetchone()

        if result[0] == 0:
            cursor.execute(f"INSERT INTO raw_data (crypto, timestamp, price) VALUES (%s, %s, %s)", (crypto, timestamp, price))
    
    db.commit()
    cursor.close()
    db.close()

if __name__ == '__main__':
    try:
        logging.info("Fetching data for Bitcoin...")
        btc_data = fetch_data('bitcoin', 30)
        store_data(btc_data, 'bitcoin')
        logging.info("Data for Bitcoin fetched and stored successfully.")

        logging.info("Fetching data for Ethereum...")
        eth_data = fetch_data('ethereum', 30)
        store_data(eth_data, 'ethereum')
        logging.info("Data for Ethereum fetched and stored successfully.")

    except Exception as e:
        logging.error(f"Error in fetching or storing data: {e}")
        print(f"Error in fetching or storing data: {e}")