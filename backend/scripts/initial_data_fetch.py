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
def fetch_data_from_binance_us(symbol, start_date, end_date, api_key):
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

# Process and store raw data
def process_and_store_raw_data(symbol, table_name, api_key):
    db = get_db_connection()
    cursor = db.cursor()
    
    # Fetch existing timestamps to avoid duplicates
    query = f"SELECT timestamp FROM {table_name}"
    cursor.execute(query)
    existing_timestamps = {row[0] for row in cursor.fetchall()}
    
    # Define the date range for data fetching
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # Fetch data for the past year
    delta = timedelta(days=100)  # Adjust chunk size as needed
    
    # Fetch data from Binance.US in chunks
    while start_date < end_date:
        current_end_date = min(start_date + delta, end_date)
        
        print(f"Fetching data for {symbol} from {start_date} to {current_end_date}...")
        data = fetch_data_from_binance_us(symbol, start_date, current_end_date, api_key)
        
        if not data:
            break
        
        # Process data and prepare for insertion
        processed_data = []
        for entry in data:
            ts = entry[0]  # Timestamp in milliseconds
            if ts in existing_timestamps:
                continue  # Skip if the timestamp already exists
            
            open_price = float(entry[1])
            high = float(entry[2])
            low = float(entry[3])
            close = float(entry[4])
            volume = float(entry[5])
            market_cap = None  # Binance.US does not provide market cap
            
            processed_data.append((ts, close, volume, market_cap, open_price, high, low, close))
        
        # Insert data into the database
        if processed_data:
            insert_query = f"""
            INSERT INTO {table_name} 
            (timestamp, price, volume, market_cap, open, high, low, close) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_query, processed_data)
            db.commit()
        
        # Move to the next chunk
        start_date = current_end_date + timedelta(milliseconds=1)
    
    cursor.close()
    db.close()
    print(f"Data fetching and storing completed for {symbol}.")

if __name__ == "__main__":
    api_key = 'ZQc7oSBhlqWcK7ReV12efw407djf909MbcXZuz29Kf8mvncmyVdyCaakbYcVzXWK'
    print("Fetching and storing data for Bitcoin...")
    process_and_store_raw_data('BTCUSDT', 'raw_data_bitcoin', api_key)

    print("Fetching and storing data for Ethereum...")
    process_and_store_raw_data('ETHUSDT', 'raw_data_ethereum', api_key)