from flask import jsonify, request
from app import app, socketio
import pandas as pd
import os

@app.route('/api/data', methods=['GET'])
def get_data():
    crypto = request.args.get('crypto')
    timescale = request.args.get('timescale')

    if timescale not in ['year', 'month', 'day', 'hour']:
        return jsonify({'error': 'Invalid timescale'}), 400

    data_file = f'backend/data/processed/{crypto}_data_processed.csv'
    prediction_file = f'backend/data/predictions/{crypto}_predictions.csv'
    if not os.path.exists(data_file):
        return jsonify({'error': f'No data available for {crypto}'}), 404

    df = pd.read_csv(data_file)
    df_predictions = pd.read_csv(prediction_file)

    if timescale == 'hour':
        df = df.tail(60)
        df_predictions = df_predictions.tail(60)
    elif timescale == 'day':
        df = df.tail(24)
        df_predictions = df_predictions.tail(24)
    elif timescale == 'month':
        df = df.tail(30 * 24)
        df_predictions = df_predictions.tail(30 * 24)
    elif timescale == 'year':
        df = df.tail(365 * 24)
        df_predictions = df_predictions.tail(365 * 24)

    result = {
        'timestamps': df['timestamp'].tolist(),
        'prices': df['price'].tolist(),
        'predictions': df_predictions['prediction'].tolist()
    }

    return jsonify(result)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_update')
def handle_request_update(json):
    crypto = json.get('crypto')
    timescale = json.get('timescale')

    if timescale not in ['year', 'month', 'day', 'hour']:
        socketio.emit('error', {'error': 'Invalid timescale'})
        return

    data_file = f'backend/data/processed/{crypto}_data_processed.csv'
    prediction_file = f'backend/data/predictions/{crypto}_predictions.csv'
    if not os.path.exists(data_file):
        socketio.emit('error', {'error': f'No data available for {crypto}'})
        return

    df = pd.read_csv(data_file)
    df_predictions = pd.read_csv(prediction_file)

    if timescale == 'hour':
        df = df.tail(60)
        df_predictions = df_predictions.tail(60)
    elif timescale == 'day':
        df = df.tail(24)
        df_predictions = df_predictions.tail(24)
    elif timescale == 'month':
        df = df.tail(30 * 24)
        df_predictions = df_predictions.tail(30 * 24)
    elif timescale == 'year':
        df = df.tail(365 * 24)
        df_predictions = df_predictions.tail(365 * 24)

    result = {
        'timestamps': df['timestamp'].tolist(),
        'prices': df['price'].tolist(),
        'predictions': df_predictions['prediction'].tolist()
    }

    socketio.emit('update_graph', result)