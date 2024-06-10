import requests
import pandas as pd
import os

def fetch_data(crypto, days=30):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto}/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': days
    }
    response = requests.get(url, params=params)
    
    data = response.json()
    
    # Debugging print to show the API response
    # print(f"API Response for {crypto}:", data)

    if 'prices' not in data:
        raise KeyError("'prices' key not found in the API response")

    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df

if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)

    btc_data = fetch_data('bitcoin')
    btc_data.to_csv(os.path.join(data_dir, 'btc_data.csv'), index=False)
    eth_data = fetch_data('ethereum')
    eth_data.to_csv(os.path.join(data_dir, 'eth_data.csv'), index=False)