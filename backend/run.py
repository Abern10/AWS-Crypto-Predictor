import sys
import os
import threading
import logging

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, socketio
from scripts.scheduler import run_scheduler

def start_scheduler():
    print("Starting scheduler thread...")
    logging.info("Starting scheduler thread...")
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True  # Daemonize thread to exit with the main program
    try:
        scheduler_thread.start()
        print("Scheduler thread started.")
        logging.info("Scheduler thread started.")
    except Exception as e:
        print(f"Scheduler thread failed to start: {e}")
        logging.info(f"Scheduler thread failed to start: {e}")

if __name__ == '__main__':
    print("Starting Flask server...")
    logging.info("Starting Flask server...")
    start_scheduler()
    socketio.run(app, host='0.0.0.0', port=1111, debug=True)
    print("Flask server started.")
    logging.info("Flask server started.")