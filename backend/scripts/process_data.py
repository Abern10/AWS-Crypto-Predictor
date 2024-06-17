import mysql.connector
import pandas as pd
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("../logs/process_data.log"),
    logging.StreamHandler()
])
logger = logging.getLogger(__name__)

def fetch_raw_data(table_name):
    db = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',
        user='abern8',
        password='JettaGLI17!',
        database='crypto_db'
    )
    cursor = db.cursor()
    
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    data = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=columns)
    cursor.close()
    db.close()
    return df

def store_processed_data(df, table_name):
    db = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',
        user='abern8',
        password='JettaGLI17!',
        database='crypto_db'
    )
    cursor = db.cursor()
    
    for index, row in df.iterrows():
        cursor.execute(
            f"INSERT INTO {table_name} (timestamp, price) VALUES (%s, %s)",
            (row['timestamp'], row['price'])
        )
    
    db.commit()
    cursor.close()
    db.close()

def process_and_store_data(raw_table, processed_table):
    logger.info(f"Fetching raw data from {raw_table}...")
    raw_data_df = fetch_raw_data(raw_table)
    
    # Convert timestamp to datetime
    raw_data_df['timestamp'] = pd.to_datetime(raw_data_df['timestamp'])
    
    # Clean and preprocess data
    # Remove duplicates if any
    raw_data_df = raw_data_df.drop_duplicates(subset=['timestamp'])
    
    # Sort data by timestamp
    raw_data_df = raw_data_df.sort_values(by='timestamp')
    
    # Reset index
    raw_data_df = raw_data_df.reset_index(drop=True)
    
    logger.info(f"Storing processed data into {processed_table}...")
    store_processed_data(raw_data_df, processed_table)
    logger.info(f"Data processing and storing completed for {processed_table}.")

if __name__ == "__main__":
    logger.info("Processing data for Bitcoin...")
    process_and_store_data('raw_data_bitcoin', 'processed_data_bitcoin')

    logger.info("Processing data for Ethereum...")
    process_and_store_data('raw_data_ethereum', 'processed_data_ethereum')