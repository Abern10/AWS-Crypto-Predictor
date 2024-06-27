from sklearn.ensemble import RandomForestRegressor
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def random_forest_predictions(train_data, features, forecast_periods, last_timestamp):
    try:
        model = RandomForestRegressor(n_estimators=100)
        X_train = features
        y_train = train_data
        model.fit(X_train, y_train)
        
        logger.info(f"Random Forest X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
        logger.info(f"Random Forest Features columns: {features.columns}")
        
        X_forecast = np.arange(len(train_data), len(train_data) + forecast_periods) * 86400000 + last_timestamp
        features_forecast = np.hstack([X_forecast.reshape(-1, 1)] + [np.full((forecast_periods, 1), features[col].mean()) for col in features.columns if col != 'timestamp_ml'])
        features_forecast_df = pd.DataFrame(features_forecast, columns=features.columns)
        
        predictions = model.predict(features_forecast_df)
        logger.info(f"Random Forest predictions: {predictions}")
        return predictions
    except Exception as e:
        logger.error(f"Error in Random Forest model: {e}")
        return np.zeros(forecast_periods)