import schedule
import time
from fetch_data import fetch_data
import os

def job():
    btc_data = fetch_data('bitcoin', 1)  # Fetch data for the past 1 day
    eth_data = fetch_data('ethereum', 1)

    os.makedirs('backend/data/raw', exist_ok=True)
    btc_data.to_csv('backend/data/raw/btc_data.csv', index=False)
    eth_data.to_csv('backend/data/raw/eth_data.csv', index=False)
    print("Data fetched and saved to backend/data/raw/")

    # Optionally, you can call other scripts here to process data and retrain the model
    # os.system('python backend/scripts/process_data.py')
    # os.system('python backend/scripts/train_model.py')

# Schedule the job to run every day at midnight
schedule.every().day.at("00:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
