import requests
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import logging
import os

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'fetch_data.log')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_file), logging.StreamHandler()])

def fetch_and_store_data(crypto, days):
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        end_timestamp = int(end_time.timestamp())
        start_timestamp = int(start_time.timestamp())

        url = f'https://api.coingecko.com/api/v3/coins/{crypto}/market_chart/range'
        params = {
            'vs_currency': 'usd',
            'from': start_timestamp,
            'to': end_timestamp
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        prices = data['prices']
        timestamps = [datetime.utcfromtimestamp(price[0] / 1000).strftime('%Y-%m-%d %H:%M:%S') for price in prices]
        prices = [price[1] for price in prices]

        df = pd.DataFrame({'timestamp': timestamps, 'price': prices})

        db = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',  # DB host (endpoint)
        user='abern8',  # DB username
        password='JettaGLI17!',  # DB password
        database='crypto_db'
        )
        cursor = db.cursor()

        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO raw_data (crypto, timestamp, price)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE price = VALUES(price)
            """, (crypto, row['timestamp'], row['price']))

        db.commit()
        cursor.close()
        db.close()
        logging.info(f"Data for {crypto} fetched and stored successfully.")
    except Exception as e:
        logging.error(f"Error fetching data for {crypto}: {e}")

if __name__ == "__main__":
    fetch_and_store_data('bitcoin', 30)
    fetch_and_store_data('ethereum', 30)