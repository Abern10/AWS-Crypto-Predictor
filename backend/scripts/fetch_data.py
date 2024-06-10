import requests
import pandas as pd

def fetch_data(crypto, days=30):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto}/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'hourly'  # You can change this to 'daily' if you want daily data
    }
    response = requests.get(url, params=params)
    data = response.json()

    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df

if __name__ == "__main__":
    btc_data = fetch_data('bitcoin')
    btc_data.to_csv('backend/data/raw/btc_data.csv', index=False)
    eth_data = fetch_data('ethereum')
    eth_data.to_csv('backend/data/raw/eth_data.csv', index=False)