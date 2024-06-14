import schedule
import time
import subprocess
import logging
import os

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'scheduler.log')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_file), logging.StreamHandler()])

def job():
    try:
        logging.info("Starting scheduled job...")

        # Step 1: Fetch data
        logging.info("Running fetch_data.py...")
        subprocess.run(['python3', 'fetch_data.py'], check=True)
        logging.info("fetch_data.py completed.")

        # Step 2: Process data
        logging.info("Running process_data.py...")
        subprocess.run(['python3', 'process_data.py'], check=True)
        logging.info("process_data.py completed.")

        # Step 3: Train models and predict future prices
        logging.info("Running train_model.py...")
        subprocess.run(['python3', 'train_model.py'], check=True)
        logging.info("train_model.py completed.")

        logging.info("Scheduled job completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in scheduled job: {e}")
        print(f"Error in scheduled job: {e}")

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
        logging.error(f"Failed to start job: {e}")
        print(f"Failed to start job: {e}")