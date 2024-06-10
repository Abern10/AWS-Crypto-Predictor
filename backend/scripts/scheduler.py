import sys
import site
import os
import logging

# Print the Python executable path
print("Python executable:", sys.executable)

# Explicitly add the virtual environment's site-packages directory
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

import schedule
import time
from scripts.fetch_data import fetch_data
from scripts.process_data import preprocess_data
from scripts.train_model import train_model
import matplotlib.pyplot as plt
import joblib
import pandas as pd

def job():
    try:
        logger.info("Running scheduled job...")
        # Step 1: Fetch data
        btc_data = fetch_data('bitcoin', 1)  # Fetch data for the past 1 day
        eth_data = fetch_data('ethereum', 1)

        os.makedirs('backend/data/raw', exist_ok=True)
        btc_data.to_csv('backend/data/raw/btc_data.csv', index=False)
        eth_data.to_csv('backend/data/raw/eth_data.csv', index=False)
        logger.info("Data fetched and saved to backend/data/raw/")

        # Step 2: Process data
        btc_data_processed = preprocess_data('backend/data/raw/btc_data.csv')
        eth_data_processed = preprocess_data('backend/data/raw/eth_data.csv')

        os.makedirs('backend/data/processed', exist_ok=True)
        btc_data_processed.to_csv('backend/data/processed/btc_data_processed.csv')
        eth_data_processed.to_csv('backend/data/processed/eth_data_processed.csv')
        logger.info("Data processed and saved to backend/data/processed/")

        # Step 3: Train models
        btc_model_path = 'backend/models/btc_model.pkl'
        eth_model_path = 'backend/models/eth_model.pkl'

        train_model('backend/data/processed/btc_data_processed.csv', btc_model_path, 'backend/data/predictions/btc_predictions.csv')
        train_model('backend/data/processed/eth_data_processed.csv', eth_model_path, 'backend/data/predictions/eth_predictions.csv')
        logger.info(f"Models saved to {btc_model_path} and {eth_model_path}")

        # Step 4: Visualize predictions
        def visualize_predictions(data_path, model_path, title):
            df = pd.read_csv(data_path)
            model = joblib.load(model_path)
            df['prediction'] = model.predict(df[['price']])

            plt.figure(figsize=(14, 7))
            plt.plot(df['timestamp'], df['price'], label='Actual Price')
            plt.plot(df['timestamp'], df['prediction'], label='Predicted Price', linestyle='--')
            plt.xlabel('Timestamp')
            plt.ylabel('Price (USD)')
            plt.title(title)
            plt.legend()
            plt.show()

        visualize_predictions('backend/data/processed/btc_data_processed.csv', btc_model_path, 'Bitcoin Price Prediction')
        visualize_predictions('backend/data/processed/eth_data_processed.csv', eth_model_path, 'Ethereum Price Prediction')
        logger.info("Visualizations generated")
    except Exception as e:
        logger.error(f"Error in job execution: {e}")

def run_scheduler():
    # Schedule the job to run every day at midnight
    # schedule.every().day.at("00:00").do(job)

    # Schedule the job to run every five minutes for testing purposes
    schedule.every(5).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    job()  # Run job once at startup for immediate effect
    run_scheduler()