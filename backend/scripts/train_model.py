import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
from datetime import datetime, timedelta

def train_model(df, model_path, prediction_path, days_to_predict):
    df['timestamp'] = pd.to_datetime(df['timestamp']).astype(int) / 10**9  # Convert timestamp to numeric
    X = df[['timestamp']]
    y = df['price']

    model = LinearRegression()
    model.fit(X, y)

    joblib.dump(model, model_path)

    # Generate future timestamps for prediction
    last_timestamp = df['timestamp'].iloc[-1]
    future_timestamps = [(last_timestamp + i * 24 * 3600) for i in range(1, days_to_predict + 1)]
    future_timestamps_df = pd.DataFrame(future_timestamps, columns=['timestamp'])

    # Predict future prices
    future_predictions = model.predict(future_timestamps_df)

    future_df = pd.DataFrame({
        'timestamp': pd.to_datetime(future_timestamps_df['timestamp'], unit='s'),
        'prediction': future_predictions
    })
    future_df.to_csv(prediction_path, index=False)
    print(f"Future predictions saved to {prediction_path}")

if __name__ == "__main__":
    df_btc = pd.read_csv('backend/data/processed/btc_data_processed.csv')
    train_model(df_btc, 'backend/models/btc_model.pkl', 'backend/data/predictions/btc_predictions.csv', days_to_predict=30)

    df_eth = pd.read_csv('backend/data/processed/eth_data_processed.csv')
    train_model(df_eth, 'backend/models/eth_model.pkl', 'backend/data/predictions/eth_predictions.csv', days_to_predict=30)