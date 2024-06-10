from flask import jsonify, request
from app import app, socketio
from scripts.fetch_data import fetch_data
from scripts.process_data import preprocess_data
from scripts.train_model import train_model
import pandas as pd
import joblib
import os

@app.route('/api/data', methods=['GET'])
def get_data():
    crypto = request.args.get('crypto')
    timescale = 'month'  # Always fetch data for the past 30 days

    try:
        print(f"Fetching data for {crypto} for the past 30 days")
        data = fetch_data(crypto)
        print("Data fetched:", data.head())

        print("Preprocessing data...")
        processed_data = preprocess_data(data)
        print("Processed data:", processed_data.head())

        if 'timestamp' not in processed_data.columns or 'price' not in processed_data.columns:
            raise ValueError("Processed data does not contain required columns 'timestamp' and 'price'")

        print("Training model and making predictions...")
        model_path = f'backend/models/{crypto}_model.pkl'
        prediction_path = f'backend/data/predictions/{crypto}_predictions.csv'
        train_model(processed_data, model_path, prediction_path, days_to_predict=5)

        print("Loading predictions...")
        predictions_df = pd.read_csv(prediction_path)
        print("Predictions loaded:", predictions_df.head())

        response = {
            'timestamps': processed_data['timestamp'].tolist(),
            'prices': processed_data['price'].tolist(),
            'predictions': {
                'timestamps': predictions_df['timestamp'].tolist(),
                'prices': predictions_df['prediction'].tolist()
            }
        }
        print("Sending response...")
        return jsonify(response)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_update')
def handle_request_update(json):
    crypto = json.get('crypto')
    timescale = 'month'  # Always fetch data for the past 30 days

    try:
        print(f"Fetching data for {crypto} for the past 30 days")
        data = fetch_data(crypto)
        print("Data fetched:", data.head())

        print("Preprocessing data...")
        processed_data = preprocess_data(data)
        print("Processed data:", processed_data.head())

        if 'timestamp' not in processed_data.columns or 'price' not in processed_data.columns:
            raise ValueError("Processed data does not contain required columns 'timestamp' and 'price'")

        print("Training model and making predictions...")
        model_path = f'backend/models/{crypto}_model.pkl'
        prediction_path = f'backend/data/predictions/{crypto}_predictions.csv'
        train_model(processed_data, model_path, prediction_path, days_to_predict=5)

        print("Loading predictions...")
        predictions_df = pd.read_csv(prediction_path)
        print("Predictions loaded:", predictions_df.head())

        response = {
            'timestamps': processed_data['timestamp'].tolist(),
            'prices': processed_data['price'].tolist(),
            'predictions': {
                'timestamps': predictions_df['timestamp'].tolist(),
                'prices': predictions_df['prediction'].tolist()
            }
        }
        print("Sending response...")
        socketio.emit('update_graph', response)
    except Exception as e:
        print(f"Error: {str(e)}")
        socketio.emit('error', {'error': str(e)})