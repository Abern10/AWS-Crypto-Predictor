import mysql.connector
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("process_data.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

def fetch_raw_data():
    conn = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',  # DB host (endpoint)
        user='abern8',  # DB username
        password='JettaGLI17!',  # DB password
        database='crypto_db'
    )
    cursor = conn.cursor()
    
    query = "SELECT crypto, timestamp, price FROM raw_data"
    cursor.execute(query)
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return pd.DataFrame(rows, columns=['crypto', 'timestamp', 'price'])

def process_data(df):
    # Example processing: calculate rolling mean as a feature
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df['rolling_mean'] = df['price'].rolling(window=7).mean()
    df.reset_index(inplace=True)
    return df

def store_processed_data(df):
    conn = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',  # DB host (endpoint)
        user='abern8',  # DB username
        password='JettaGLI17!',  # DB password
        database='crypto_db'
    )
    cursor = conn.cursor()
    
    for index, row in df.iterrows():
        # Check if the record already exists
        cursor.execute(
            "SELECT COUNT(*) FROM processed_data WHERE crypto = %s AND timestamp = %s",
            (row['crypto'], row['timestamp'])
        )
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insert the new record if it doesn't exist
            cursor.execute(
                "INSERT INTO processed_data (crypto, timestamp, price, rolling_mean) VALUES (%s, %s, %s, %s)",
                (row['crypto'], row['timestamp'], row['price'], row['rolling_mean'])
            )
    
    conn.commit()
    cursor.close()
    conn.close()

def main():
    try:
        logger.info("Fetching raw data...")
        raw_data_df = fetch_raw_data()
        
        logger.info("Processing data...")
        processed_data_df = process_data(raw_data_df)
        
        logger.info("Storing processed data...")
        store_processed_data(processed_data_df)
        
        logger.info("Data processing and storing completed.")
    except Exception as e:
        logger.error(f"Error in data processing: {e}")
        print(f"Error in data processing: {e}")

if __name__ == "__main__":
    main()