import requests
import mysql.connector
import pandas as pd
from datetime import datetime

def fetch_data(crypto, days):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto}/market_chart'
    params = {'vs_currency': 'usd', 'days': days}
    response = requests.get(url, params=params)
    data = response.json()
    
    prices = data['prices']
    timestamps = [datetime.utcfromtimestamp(price[0] / 1000).strftime('%Y-%m-%d %H:%M:%S') for price in prices]
    prices = [price[1] for price in prices]
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'price': prices
    })
    return df

def store_data_in_db(crypto, df):
    conn = mysql.connector.connect(
        host='cryptodb.cliawc8awtqk.us-east-1.rds.amazonaws.com',  # DB host (endpoint)
        user='abern8',  # DB username
        password='JettaGLI17!',  # DB password
        database='crypto_db'
    )
    cursor = conn.cursor()
    
    for index, row in df.iterrows():
        # Check if the record already exists
        cursor.execute(
            "SELECT COUNT(*) FROM raw_data WHERE crypto = %s AND timestamp = %s",
            (crypto, row['timestamp'])
        )
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insert the new record if it doesn't exist
            cursor.execute(
                "INSERT INTO raw_data (crypto, timestamp, price) VALUES (%s, %s, %s)",
                (crypto, row['timestamp'], row['price'])
            )
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    crypto_list = ['bitcoin', 'ethereum']
    days = 30
    
    for crypto in crypto_list:
        df = fetch_data(crypto, days)
        store_data_in_db(crypto, df)