import requests
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fetch_data(crypto_id, days):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={days}'
    response = requests.get(url)
    data = response.json()
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

if __name__ == "__main__":
    btc_data = fetch_data('bitcoin', 365)
    eth_data = fetch_data('ethereum', 365)

    os.makedirs('backend/data/raw', exist_ok=True)
    btc_data.to_csv('backend/data/raw/btc_data.csv', index=False)
    eth_data.to_csv('backend/data/raw/eth_data.csv', index=False)
    print("Data fetched and saved to backend/data/raw/")
