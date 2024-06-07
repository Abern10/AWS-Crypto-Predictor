import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df.set_index('timestamp', inplace=True)
    df['price'] = df['price'].rolling(window=7).mean()  # Example feature: 7-day moving average
    df.dropna(inplace=True)
    return df

if __name__ == "__main__":
    btc_data = preprocess_data('backend/data/raw/btc_data.csv')
    eth_data = preprocess_data('backend/data/raw/eth_data.csv')

    os.makedirs('backend/data/processed', exist_ok=True)
    btc_data.to_csv('backend/data/processed/btc_data_processed.csv')
    eth_data.to_csv('backend/data/processed/eth_data_processed.csv')
    print("Data processed and saved to backend/data/processed/")