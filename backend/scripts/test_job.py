import sys
import site
import os
import logging
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt

# Ensure the necessary paths are set
venv_path = os.path.join(os.path.dirname(__file__), '../../venv/lib/python3.12/site-packages')
site.addsitedir(venv_path)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Use a non-interactive backend for matplotlib
matplotlib.use('Agg')

# Import the job function
from scripts.scheduler import job

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("test_job.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        print("Running test job...", flush=True)
        logger.info("Running test job...")
        job()
        print("Test job completed successfully.", flush=True)
        logger.info("Test job completed successfully.")
    except Exception as e:
        print(f"Test job failed. Error: {e}", flush=True)
        logger.error(f"Test job failed. Error: {e}")