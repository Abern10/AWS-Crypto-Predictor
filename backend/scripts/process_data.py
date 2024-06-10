import pandas as pd

def preprocess_data(file_path):
    data = pd.read_csv(file_path)
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data = data.sort_values(by='timestamp').reset_index(drop=True)
    return data

if __name__ == "__main__":
    btc_data = preprocess_data('backend/data/raw/btc_data.csv')
    btc_data.to_csv('backend/data/processed/btc_data_processed.csv', index=False)
    eth_data = preprocess_data('backend/data/raw/eth_data.csv')
    eth_data.to_csv('backend/data/processed/eth_data_processed.csv', index=False)