import pandas as pd
import joblib
import matplotlib.pyplot as plt

def visualize_predictions(data_path, model_path, title):
    df = pd.read_csv(data_path)
    model = joblib.load(model_path)
    df['prediction'] = model.predict(df[['price']])

    plt.figure(figsize=(14, 7))
    plt.plot(df['timestamp'], df['price'], label='Actual Price')
    plt.plot(df['timestamp'], df['prediction'], label='Predicted Price', linestyle='--')
    plt.xlabel('Timestamp')
    plt.ylabel('Price (USD)')
    plt.title(title)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    visualize_predictions('backend/data/processed/btc_data_processed.csv', 'backend/models/btc_model.pkl', 'Bitcoin Price Prediction')
    visualize_predictions('backend/data/processed/eth_data_processed.csv', 'backend/models/eth_model.pkl', 'Ethereum Price Prediction')
