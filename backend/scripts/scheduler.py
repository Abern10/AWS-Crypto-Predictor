import sys
import site
import os
import logging
import matplotlib
import schedule
import time
from scripts.fetch_data import fetch_data
from scripts.process_data import preprocess_data
from scripts.train_model import train_model
import matplotlib.pyplot as plt
import joblib
import pandas as pd
matplotlib.use('Agg')  # Use a non-interactive backend

# Add the virtual environment's site-packages directory
venv_path = os.path.join(os.path.dirname(__file__), '../../venv/lib/python3.12/site-packages')
site.addsitedir(venv_path)

# Ensure the scripts directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("scheduler.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Function to fetch data
def fetch_data(crypto, days):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto}/market_chart'
    params = {'vs_currency': 'usd', 'days': days}
    response = requests.get(url, params=params)
    data = response.json()
    
    prices = data['prices']
    timestamps = [datetime.utcfromtimestamp(price[0] / 1000).strftime('%Y-%m-%d %H:%M:%S') for price in prices]
    prices = [price[1] for price in prices]
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'price': prices
    })
    return df

# Function to store data in the database
def store_data_in_db(crypto, df):
    conn = mysql.connector.connect(
        host='aws-crypto-predictor-instance-1.cv60mwqgqo4b.us-east-2.rds.amazonaws.com',  # Replace with your DB host
        user='your-db-username',  # Replace with your DB username
        password='your-db-password',  # Replace with your DB password
        database='crypto_db'
    )
    cursor = conn.cursor()
    
    for index, row in df.iterrows():
        # Check if the record already exists
        cursor.execute(
            "SELECT COUNT(*) FROM raw_data WHERE crypto = %s AND timestamp = %s",
            (crypto, row['timestamp'])
        )
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insert the new record if it doesn't exist
            cursor.execute(
                "INSERT INTO raw_data (crypto, timestamp, price) VALUES (%s, %s, %s)",
                (crypto, row['timestamp'], row['price'])
            )
    
    conn.commit()
    cursor.close()
    conn.close()

# Scheduled job function
def job():
    try:
        logger.info("Running scheduled job...")
        
        crypto_list = ['bitcoin', 'ethereum']
        days = 30
        
        for crypto in crypto_list:
            df = fetch_data(crypto, days)
            store_data_in_db(crypto, df)
        
        logger.info("Data fetching and storing completed.")
    except Exception as e:
        logger.error(f"Error in job execution: {e}")
        print(f"Error in job execution: {e}")

# Function to run the scheduler
def run_scheduler():
    # Schedule the job to run every day at midnight
    schedule.every().day.at("00:00").do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    try:
        job()  # Run job once at startup for immediate effect
        run_scheduler()
    except Exception as e:
        logger.error(f"Failed to start job: {e}")
        print(f"Failed to start job: {e}")