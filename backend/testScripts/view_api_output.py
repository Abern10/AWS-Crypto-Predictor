import requests
from datetime import datetime, timedelta

# Fetch data from Binance.US
def fetch_data_from_binance_us(coin, start_date, end_date, api_key):
    symbol = 'BTCUSDT' if coin.lower() == 'bitcoin' else 'ETHUSDT'
    url = f"https://api.binance.us/api/v3/klines"
    params = {
        'symbol': symbol,
        'interval': '1d',
        'startTime': int(start_date.timestamp() * 1000),
        'endTime': int(end_date.timestamp() * 1000)
    }
    headers = {
        'X-MBX-APIKEY': api_key
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return data

if __name__ == "__main__":
    api_key = 'ZQc7oSBhlqWcK7ReV12efw407djf909MbcXZuz29Kf8mvncmyVdyCaakbYcVzXWK'
    coin = 'bitcoin'
    
    # Define the date range for data fetching
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # Fetch data for the past year
    
    # Fetch data from Binance.US
    print(f"Fetching data for {coin} from Binance.US...")
    data = fetch_data_from_binance_us(coin, start_date, end_date, api_key)
    
    # Print the fetched data
    print("Fetched data:")
    for entry in data:
        print(entry)