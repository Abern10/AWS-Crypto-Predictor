import mysql.connector
import requests
from datetime import datetime, timedelta

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',
        user='abern8',
        password='JettaGLI17!',
        database='crypto_db'
    )

# Fetch data from Binance.US
def fetch_data_from_binance_us(coin, start_date, end_date, api_key):
    symbol = 'BTCUSDT' if coin.lower() == 'bitcoin' else 'ETHUSDT'
    url = f"https://api.binance.us/api/v3/klines"
    params = {
        'symbol': symbol,
        'interval': '1d',
        'startTime': int(start_date.timestamp() * 1000),
        'endTime': int(end_date.timestamp() * 1000)
    }
    headers = {
        'X-MBX-APIKEY': api_key
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return data

# Store data in the database
def store_data_in_db(coin, data):
    db = get_db_connection()
    cursor = db.cursor()
    
    # Prepare data for insertion
    processed_data = []
    for entry in data:
        ts = entry[0]  # Timestamp in milliseconds
        open_price = float(entry[1])
        high = float(entry[2])
        low = float(entry[3])
        close = float(entry[4])
        volume = float(entry[5])
        market_cap = None  # Binance.US does not provide market cap
        
        processed_data.append((ts, close, volume, market_cap, open_price, high, low, close))
    
    # Insert data into the database
    insert_query = f"""
    INSERT IGNORE INTO raw_data_{coin.lower()} 
    (timestamp, price, volume, market_cap, open, high, low, close) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, processed_data)
    db.commit()
    
    cursor.close()
    db.close()

def process_daily_fetch(coin, api_key):
    db = get_db_connection()
    cursor = db.cursor()
    
    # Fetch the latest timestamp from the database
    query = f"SELECT MAX(timestamp) FROM raw_data_{coin.lower()}"
    cursor.execute(query)
    last_timestamp = cursor.fetchone()[0]
    
    # Calculate the next day to fetch
    if last_timestamp is None:
        # If the table is empty, fetch data starting from a year ago
        start_date = datetime.now() - timedelta(days=365)
    else:
        start_date = datetime.fromtimestamp(last_timestamp / 1000.0) + timedelta(days=1)
    
    end_date = start_date + timedelta(days=1)
    
    # Check if there is a new day to fetch
    if start_date.date() >= datetime.now().date():
        print(f"No new data to be added for {coin}.")
        return
    
    # Fetch data from Binance.US
    print(f"Fetching data for {coin} from Binance.US for {start_date.date()}...")
    data = fetch_data_from_binance_us(coin, start_date, end_date, api_key)
    
    # Store data in the database
    store_data_in_db(coin, data)
    print(f"Data for {coin} on {start_date.date()} stored successfully.")

if __name__ == "__main__":
    api_key = 'ZQc7oSBhlqWcK7ReV12efw407djf909MbcXZuz29Kf8mvncmyVdyCaakbYcVzXWK'
    
    print("Fetching and storing daily data for Bitcoin...")
    process_daily_fetch('bitcoin', api_key)

    print("Fetching and storing daily data for Ethereum...")
    process_daily_fetch('ethereum', api_key)