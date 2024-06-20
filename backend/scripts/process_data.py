import mysql.connector
from datetime import datetime

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',
        user='abern8',
        password='JettaGLI17!',
        database='crypto_db'
    )

# Fetch raw data from the database
def fetch_raw_data(coin):
    db = get_db_connection()
    cursor = db.cursor()
    
    query = f"SELECT * FROM raw_data_{coin.lower()}"
    cursor.execute(query)
    raw_data = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return raw_data

# Calculate market cap (Example calculation, assuming market cap is calculated as price * volume)
def calculate_market_cap(price, volume):
    return price * volume

# Process and store data in the processed data table
def process_and_store_processed_data(coin):
    db = get_db_connection()
    cursor = db.cursor()
    
    # Fetch raw data
    raw_data = fetch_raw_data(coin)
    
    # Prepare data for insertion
    processed_data = []
    for row in raw_data:
        timestamp_ms = row[0]
        price = row[1]
        volume = row[2]
        market_cap = row[3] if row[3] is not None else calculate_market_cap(price, volume)
        open_price = row[4]
        high = row[5]
        low = row[6]
        close = row[7]
        
        # Convert milliseconds to datetime
        timestamp_arima = datetime.fromtimestamp(timestamp_ms / 1000.0)
        
        # Add entries to processed data
        processed_data.append((timestamp_arima, timestamp_ms, price, volume, market_cap, open_price, high, low, close))
    
    # Insert processed data into the database
    insert_query = f"""
    INSERT INTO processed_data_{coin.lower()} 
    (timestamp_arima, timestamp_ml, price, volume, market_cap, open, high, low, close) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, processed_data)
    db.commit()
    
    cursor.close()
    db.close()
    print(f"Processed data for {coin} stored successfully.")

if __name__ == "__main__":
    print("Processing and storing data for Bitcoin...")
    process_and_store_processed_data('bitcoin')

    print("Processing and storing data for Ethereum...")
    process_and_store_processed_data('ethereum')