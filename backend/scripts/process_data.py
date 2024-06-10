import pandas as pd

def preprocess_data(file_path):
    df = pd.read_csv(file_path)
    
    # Debugging: Print the head of the data being processed
    print(f"Preprocessing data from {file_path}:")
    # print(df.head())

    # Example preprocessing steps
    df = df.dropna()
    df = df.sort_values('timestamp')

    return df

if __name__ == "__main__":
    btc_data_processed = preprocess_data('backend/data/raw/btc_data.csv')
    btc_data_processed.to_csv('backend/data/processed/btc_data_processed.csv', index=False)
    eth_data_processed = preprocess_data('backend/data/raw/eth_data.csv')
    eth_data_processed.to_csv('backend/data/processed/eth_data_processed.csv', index=False)