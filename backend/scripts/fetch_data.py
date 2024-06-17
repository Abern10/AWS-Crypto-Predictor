import requests
import mysql.connector
from datetime import datetime, timezone
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("../logs/fetch_data.log"),
    logging.StreamHandler()
])
logger = logging.getLogger(__name__)

def fetch_and_store_data(crypto_name, table_name):
    db = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',
        user='abern8',
        password='JettaGLI17!',
        database='crypto_db'
    )
    cursor = db.cursor()

    # Fetch existing timestamps to avoid duplicates
    cursor.execute(f"SELECT DISTINCT DATE(timestamp) FROM {table_name}")
    existing_dates = {row[0] for row in cursor.fetchall()}

    # Fetch data from CoinGecko API
    url = f'https://api.coingecko.com/api/v3/coins/{crypto_name}/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': '30',
        'interval': 'daily'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        prices = data['prices']

        # Store data in database
        for price in prices:
            timestamp = datetime.fromtimestamp(price[0] / 1000, tz=timezone.utc)
            date_only = timestamp.date()
            if date_only not in existing_dates:
                existing_dates.add(date_only)
                cursor.execute(
                    f"INSERT INTO {table_name} (timestamp, price) VALUES (%s, %s)",
                    (timestamp, price[1])
                )
        db.commit()
        logger.info(f"Data fetching and storing completed successfully for {crypto_name}.")
    else:
        logger.error(f"Error fetching data from CoinGecko API for {crypto_name}: {response.text}")

    cursor.close()
    db.close()

if __name__ == "__main__":
    logger.info("Fetching data for Bitcoin...")
    fetch_and_store_data('bitcoin', 'raw_data_bitcoin')

    logger.info("Fetching data for Ethereum...")
    fetch_and_store_data('ethereum', 'raw_data_ethereum')