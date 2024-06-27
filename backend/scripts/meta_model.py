from xgboost import XGBRegressor
import numpy as np
import logging

logger = logging.getLogger(__name__)

def meta_model_predictions(arima_preds, lr_preds, rf_preds, xgb_preds):
    try:
        X_meta = np.column_stack((arima_preds, lr_preds, rf_preds, xgb_preds))
        logger.info(f"Meta model input: {X_meta}")
        model = XGBRegressor(n_estimators=100)
        y_meta = arima_preds  # Using ARIMA predictions as the target for simplicity
        model.fit(X_meta, y_meta)
        meta_predictions = model.predict(X_meta)
        logger.info(f"Meta model predictions: {meta_predictions}")
        return meta_predictions
    except Exception as e:
        logger.error(f"Error in Meta model: {e}")
        return np.zeros(len(arima_preds))