from statsmodels.tsa.arima.model import ARIMA
import numpy as np
import logging

logger = logging.getLogger(__name__)

def arima_predictions(train_data, forecast_periods):
    try:
        train_data = train_data.astype(float)
        model = ARIMA(train_data, order=(5, 1, 0))
        model_fit = model.fit()
        predictions = model_fit.forecast(steps=forecast_periods)
        logger.info(f"ARIMA predictions: {predictions}")
        return predictions
    except Exception as e:
        logger.error(f"Error in ARIMA model: {e}")
        return np.zeros(forecast_periods)