import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def train_model(file_path, model_path):
    df = pd.read_csv(file_path)
    df['target'] = df['price'].shift(-1)
    df.dropna(inplace=True)

    X = df[['price']]
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

    score = model.score(X_test, y_test)
    print(f"Model R^2 score: {score}")

if __name__ == "__main__":
    train_model('backend/data/processed/btc_data_processed.csv', 'backend/models/btc_model.pkl')
    train_model('backend/data/processed/eth_data_processed.csv', 'backend/models/eth_model.pkl')