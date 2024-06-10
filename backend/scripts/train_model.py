import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

def train_model(processed_data_path, model_paths, prediction_path, days_to_predict=5):
    # Load the processed data
    df = pd.read_csv(processed_data_path)

    # Ensure the timestamp is the index
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    # Extract the features and target
    X = np.arange(len(df)).reshape(-1, 1)  # Time as a feature
    y = df['price'].values

    # Debugging prints
    print(f"Feature (X) shape: {X.shape}")
    print(f"Target (y) shape: {y.shape}")

    try:
        # Train Linear Regression
        lr_model = LinearRegression()
        lr_model.fit(X, y)
        print("Linear Regression model trained successfully.")
        
        # Train ARIMA
        arima_model = ARIMA(y, order=(5, 1, 0))
        arima_model_fit = arima_model.fit()
        print("ARIMA model trained successfully.")
        
        # Train Random Forest
        rf_model = RandomForestRegressor(n_estimators=100)
        rf_model.fit(X, y)
        print("Random Forest model trained successfully.")
        
        try:
            # Save the models
            joblib.dump(lr_model, model_paths['linear_regression'])
            arima_model_fit.save(model_paths['arima'])  # Corrected ARIMA model saving
            joblib.dump(rf_model, model_paths['random_forest'])
            print(f"Models saved to {model_paths}")
        except Exception as e:
            print(f"Error during model saving: {e}")

    except Exception as e:
        print(f"Error during model training: {e}")

    try:
        # Make predictions for the next 5 days
        future_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=days_to_predict)
        X_future = np.arange(len(df), len(df) + days_to_predict).reshape(-1, 1)

        # Debugging prints
        print(f"Future feature (X_future) shape: {X_future.shape}")

        # Linear Regression Predictions
        lr_predictions = lr_model.predict(X_future)
        print(f"Linear Regression predictions: {lr_predictions}")

        # ARIMA Predictions
        arima_predictions = arima_model_fit.forecast(steps=days_to_predict)
        print(f"ARIMA predictions: {arima_predictions}")

        # Random Forest Predictions
        rf_predictions = rf_model.predict(X_future)
        print(f"Random Forest predictions: {rf_predictions}")

        # Combine predictions (simple average)
        combined_predictions = (lr_predictions + arima_predictions + rf_predictions) / 3
        print(f"Combined predictions: {combined_predictions}")

        # Create a DataFrame for predictions
        predictions_df = pd.DataFrame({'timestamp': future_dates, 'prediction': combined_predictions})

        # Save predictions
        predictions_df.to_csv(prediction_path, index=False)
        print(f"Predictions saved to {prediction_path}")
        
        # Print predictions
        print(f"Predictions for {processed_data_path}:")
        print(predictions_df)
        
    except Exception as e:
        print(f"Error during predictions: {e}")

    return predictions_df

if __name__ == "__main__":
    btc_model_paths = {
        'linear_regression': '../models/btc_lr_model.pkl',
        'arima': '../models/btc_arima_model.pkl',
        'random_forest': '../models/btc_rf_model.pkl'
    }
    btc_predictions = train_model('../data/processed/btc_data_processed.csv', btc_model_paths, '../data/predictions/btc_predictions.csv')
    print(btc_predictions.head())

    eth_model_paths = {
        'linear_regression': '../models/eth_lr_model.pkl',
        'arima': '../models/eth_arima_model.pkl',
        'random_forest': '../models/eth_rf_model.pkl'
    }
    eth_predictions = train_model('../data/processed/eth_data_processed.csv', eth_model_paths, '../data/predictions/eth_predictions.csv')
    print(eth_predictions.head())