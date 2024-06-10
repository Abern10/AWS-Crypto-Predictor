import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression

def train_model(processed_file_path, model_path, prediction_file_path, days_to_predict=5):
    df = pd.read_csv(processed_file_path)
    
    # Debugging: Print the head of the data being used for training
    print(f"Training model with data from {processed_file_path}:")
    print(df.head())

    # Ensure timestamp column is in datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Example model training steps
    model = LinearRegression()
    X = df[['timestamp']].apply(lambda x: x.astype('int64') // 10**9)  # Convert to seconds
    y = df['price']
    
    model.fit(X, y)
    joblib.dump(model, model_path)
    
    # Example prediction steps
    future_dates = pd.date_range(start=df['timestamp'].max(), periods=days_to_predict+1, freq='D')[1:]
    future_X = future_dates.astype('int64') // 10**9
    predictions = model.predict(future_X)
    
    predictions_df = pd.DataFrame({'timestamp': future_dates, 'prediction': predictions})
    
    # Debugging: Print the predictions
    print(f"Predictions for the next {days_to_predict} days:")
    print(predictions_df)
    
    predictions_df.to_csv(prediction_file_path, index=False)

if __name__ == "__main__":
    train_model('backend/data/processed/btc_data_processed.csv', 'backend/models/btc_model.pkl', 'backend/data/predictions/btc_predictions.csv', days_to_predict=5)
    train_model('backend/data/processed/eth_data_processed.csv', 'backend/models/eth_model.pkl', 'backend/data/predictions/eth_predictions.csv', days_to_predict=5)