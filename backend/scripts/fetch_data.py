import mysql.connector
import pandas as pd
import requests
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("../logs/fetch_data.log"),
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

# Fetch data from API
def fetch_data_from_api(coin, start_date, end_date):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart/range"
    params = {
        'vs_currency': 'usd',
        'from': int(start_date.timestamp()),
        'to': int(end_date.timestamp())
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data

# Process and store raw data
def process_and_store_raw_data(coin):
    db = get_db_connection()
    cursor = db.cursor()
    
    # Fetch existing timestamps to avoid duplicates
    query = f"SELECT timestamp FROM raw_data_{coin}"
    cursor.execute(query)
    existing_timestamps = {row[0] for row in cursor.fetchall()}
    
    # Define the date range for data fetching
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # Fetch data for the past year
    
    # Fetch data from API
    logger.info(f"Fetching raw data for {coin}...")
    data = fetch_data_from_api(coin, start_date, end_date)
    
    # Process data and prepare for insertion
    processed_data = []
    for i, timestamp in enumerate(data['prices']):
        ts = datetime.fromtimestamp(timestamp[0] / 1000.0)
        if ts in existing_timestamps:
            continue  # Skip if the timestamp already exists
        
        price = data['prices'][i][1]
        volume = data['total_volumes'][i][1]
        market_cap = data['market_caps'][i][1]
        
        # Assuming open, high, low, and close prices are the same as price for simplicity
        processed_data.append((ts, price, volume, market_cap, price, price, price, price))
    
    # Insert data into the database
    insert_query = f"""
    INSERT INTO raw_data_{coin} 
    (timestamp, price, volume, market_cap, open, high, low, close) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, processed_data)
    db.commit()
    
    cursor.close()
    db.close()
    logger.info(f"Data fetching and storing completed for {coin}.")

if __name__ == "__main__":
    logger.info("Fetching and storing data for Bitcoin...")
    process_and_store_raw_data('bitcoin')

    logger.info("Fetching and storing data for Ethereum...")
    process_and_store_raw_data('ethereum')