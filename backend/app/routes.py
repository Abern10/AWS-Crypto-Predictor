from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import pandas as pd

app = Flask(__name__)
CORS(app)

# Define the paths to the data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up one directory from the current file
DATA_DIR = os.path.join(BASE_DIR, 'backend', 'data', 'processed')
PREDICTIONS_DIR = os.path.join(BASE_DIR, 'backend', 'data', 'predictions')

@app.route('/api/data', methods=['GET'])
def get_data():
    crypto = request.args.get('crypto')
    if not crypto:
        return jsonify({'error': 'No crypto specified'}), 400

    try:
        # Load the processed data
        data_path = os.path.join(DATA_DIR, f'{crypto}_data_processed.csv')
        predictions_path = os.path.join(PREDICTIONS_DIR, f'{crypto}_predictions.csv')
        
        if not os.path.exists(data_path):
            return jsonify({'error': f'Data file for {crypto} not found'}), 404
        
        if not os.path.exists(predictions_path):
            return jsonify({'error': f'Predictions file for {crypto} not found'}), 404

        data = pd.read_csv(data_path)
        predictions = pd.read_csv(predictions_path)

        # Convert timestamps to string for JSON serialization
        data['timestamp'] = data['timestamp'].astype(str)
        predictions['timestamp'] = predictions['timestamp'].astype(str)

        return jsonify({
            'timestamps': data['timestamp'].tolist(),
            'prices': data['price'].tolist(),
            'predictions': {
                'timestamps': predictions['timestamp'].tolist(),
                'prices': predictions['prediction'].tolist()
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=1111, debug=True)