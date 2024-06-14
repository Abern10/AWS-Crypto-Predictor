import mysql.connector
import pandas as pd
import logging
import os

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'process_data.log')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_file), logging.StreamHandler()])

def fetch_raw_data():
    try:
        db = mysql.connector.connect(
            host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',  # DB host (endpoint)
            user='abern8',  # DB username
            password='JettaGLI17!',  # DB password
            database='crypto_db'
        )
        cursor = db.cursor()

        cursor.execute("SELECT * FROM raw_data")
        raw_data = cursor.fetchall()
        df = pd.DataFrame(raw_data, columns=['id', 'crypto', 'timestamp', 'price'])

        cursor.close()
        db.close()
        return df
    except mysql.connector.Error as err:
        logging.error(f"Error fetching raw data: {err}")
        return None

def process_data(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    df = df.groupby('crypto')['price'].resample('D').mean().reset_index()
    return df

def store_processed_data(df):
    try:
        db = mysql.connector.connect(
                host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',  # DB host (endpoint)
                user='abern8',  # DB username
                password='JettaGLI17!',  # DB password
                database='crypto_db'
        )
        cursor = db.cursor()

        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO processed_data (crypto, timestamp, price)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE price = VALUES(price)
            """, (row['crypto'], row['timestamp'], row['price']))

        db.commit()
        cursor.close()
        db.close()
        logging.info("Processed data stored successfully.")
    except mysql.connector.Error as err:
        logging.error(f"Error storing processed data: {err}")

if __name__ == "__main__":
    logging.info("Fetching raw data...")
    raw_data_df = fetch_raw_data()
    if raw_data_df is not None:
        logging.info("Processing data...")
        processed_data_df = process_data(raw_data_df)
        logging.info("Storing processed data...")
        store_processed_data(processed_data_df)
    else:
        logging.error("No raw data to process.")