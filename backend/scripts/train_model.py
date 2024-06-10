import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def train_model(data_path, model_path, prediction_path):
    df = pd.read_csv(data_path)
    X = df[['timestamp']].values.reshape(-1, 1)  # Assuming 'timestamp' is a numeric feature
    y = df['price'].values

    model = LinearRegression()
    model.fit(X, y)

    joblib.dump(model, model_path)

    # Predict the prices
    df['prediction'] = model.predict(X)
    df.to_csv(prediction_path, index=False)
    print(f"Predictions saved to {prediction_path}")

if __name__ == "__main__":
    train_model('backend/data/processed/btc_data_processed.csv', 'backend/models/btc_model.pkl', 'backend/data/predictions/btc_predictions.csv')
    train_model('backend/data/processed/eth_data_processed.csv', 'backend/models/eth_model.pkl', 'backend/data/predictions/eth_predictions.csv')