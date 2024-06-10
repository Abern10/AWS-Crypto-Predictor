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

def job():
    try:
        print("Running scheduled job...")
        logger.info("Running scheduled job...")
        # Step 1: Fetch data
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        os.makedirs(data_dir, exist_ok=True)

        btc_data = fetch_data('bitcoin', 30)  # Fetch data for the past 30 days
        eth_data = fetch_data('ethereum', 30)

        btc_data.to_csv(os.path.join(data_dir, 'btc_data.csv'), index=False)
        eth_data.to_csv(os.path.join(data_dir, 'eth_data.csv'), index=False)
        logger.info("Data fetched and saved to backend/data/raw/")

        # Step 2: Process data
        processed_data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
        os.makedirs(processed_data_dir, exist_ok=True)

        btc_data_processed = preprocess_data(os.path.join(data_dir, 'btc_data.csv'))
        eth_data_processed = preprocess_data(os.path.join(data_dir, 'eth_data.csv'))

        btc_data_processed.to_csv(os.path.join(processed_data_dir, 'btc_data_processed.csv'))
        eth_data_processed.to_csv(os.path.join(processed_data_dir, 'eth_data_processed.csv'))
        logger.info("Data processed and saved to backend/data/processed/")

        # Step 3: Train models and predict future prices
        model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
        os.makedirs(model_dir, exist_ok=True)

        prediction_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'predictions')
        os.makedirs(prediction_dir, exist_ok=True)

        btc_model_paths = {
            'linear_regression': os.path.join(model_dir, 'btc_lr_model.pkl'),
            'arima': os.path.join(model_dir, 'btc_arima_model.pkl'),
            'random_forest': os.path.join(model_dir, 'btc_rf_model.pkl')
        }
        eth_model_paths = {
            'linear_regression': os.path.join(model_dir, 'eth_lr_model.pkl'),
            'arima': os.path.join(model_dir, 'eth_arima_model.pkl'),
            'random_forest': os.path.join(model_dir, 'eth_rf_model.pkl')
        }

        btc_predictions = train_model(
            os.path.join(processed_data_dir, 'btc_data_processed.csv'),
            btc_model_paths,
            os.path.join(prediction_dir, 'btc_predictions.csv'),
            days_to_predict=5
        )

        eth_predictions = train_model(
            os.path.join(processed_data_dir, 'eth_data_processed.csv'),
            eth_model_paths,
            os.path.join(prediction_dir, 'eth_predictions.csv'),
            days_to_predict=5
        )
        logger.info(f"Models saved to {btc_model_paths} and {eth_model_paths}")

        # Step 4: Visualize predictions
        def visualize_predictions(data_path, prediction_path, title, output_path):
            df = pd.read_csv(data_path)
            df_predictions = pd.read_csv(prediction_path)

            plt.figure(figsize=(14, 7))
            plt.plot(df['timestamp'], df['price'], label='Actual Price')
            plt.plot(df_predictions['timestamp'], df_predictions['prediction'], label='Predicted Price', linestyle='--', color='red')
            plt.xlabel('Timestamp')
            plt.ylabel('Price (USD)')
            plt.title(title)
            plt.legend()
            plt.savefig(output_path)
            plt.close()

        visualization_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'visualizations')
        os.makedirs(visualization_dir, exist_ok=True)

        visualize_predictions(
            os.path.join(processed_data_dir, 'btc_data_processed.csv'),
            os.path.join(prediction_dir, 'btc_predictions.csv'),
            'Bitcoin Price Prediction',
            os.path.join(visualization_dir, 'btc_price_prediction.png')
        )
        visualize_predictions(
            os.path.join(processed_data_dir, 'eth_data_processed.csv'),
            os.path.join(prediction_dir, 'eth_predictions.csv'),
            'Ethereum Price Prediction',
            os.path.join(visualization_dir, 'eth_price_prediction.png')
        )
        logger.info("Visualizations generated")
    except Exception as e:
        logger.error(f"Error in job execution: {e}")
        print(f"Error in job execution: {e}")

def run_scheduler():
    # Schedule the job to run every day at midnight
    # schedule.every().day.at("00:00").do(job)

    # Schedule the job to run every five minutes for testing purposes
    schedule.every(5).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    try:
        job()  # Run job once at startup for immediate effect
        run_scheduler()
    except:
        print("Failed to start job.")
        logging.info("Failed to start job.")