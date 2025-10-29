from typing import List

from flask import Flask, request, jsonify, send_file, abort
import os
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)


def _add_cors_headers(response):
    # Development-friendly CORS headers. Lock down in production.
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


app.after_request(_add_cors_headers)


_MODEL = None
_TRANSFORMER = None


def _load_model_and_transformer():
    global _MODEL, _TRANSFORMER
    if _MODEL is None or _TRANSFORMER is None:
        base = os.path.dirname(__file__)
        model_path = os.path.join(base, 'model_registry', 'model.joblib')
        transformer_path = os.path.normpath(os.path.join(base, '..', 'data', 'processed', 'transformer.joblib'))
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        if not os.path.exists(transformer_path):
            raise FileNotFoundError(f"Transformer not found at {transformer_path}")
        _MODEL = joblib.load(model_path)
        _TRANSFORMER = joblib.load(transformer_path)
    return _MODEL, _TRANSFORMER


@app.route('/', methods=['GET'])
def root():
    return jsonify(status='ok', message='Water Quality Potability API')


@app.route('/frontend', methods=['GET'])
def frontend():
    # Serve the local frontend shipped under app/frontend.html
    path = os.path.join(os.path.dirname(__file__), 'frontend.html')
    if not os.path.exists(path):
        abort(404)
    return send_file(path)


@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return ('', 204)

    data = request.get_json(silent=True)
    if not data or 'values' not in data:
        return jsonify({'error': "JSON body must include 'values' (list of numbers)"}), 400

    values = data['values']
    if not isinstance(values, list) or len(values) == 0:
        return jsonify({'error': "'values' must be a non-empty list of numbers"}), 400

    try:
        model, transformer = _load_model_and_transformer()
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 500

    try:
        # The saved transformer expects a DataFrame with column names used during training.
        # Accept either a list (ordered) or a dict (name->value).
        FEATURE_COLUMNS = ['ph','Hardness','Solids','Chloramines','Sulfate','Conductivity','Organic_carbon','Trihalomethanes','Turbidity']

        if isinstance(values, dict):
            # ensure all required columns present
            missing = [c for c in FEATURE_COLUMNS if c not in values]
            if missing:
                return jsonify({'error': f'Missing feature keys: {missing}'}), 400
            df = pd.DataFrame([{c: values[c] for c in FEATURE_COLUMNS}])
        elif isinstance(values, list):
            if len(values) != len(FEATURE_COLUMNS):
                return jsonify({'error': f'Expected {len(FEATURE_COLUMNS)} values (order: {FEATURE_COLUMNS}), got {len(values)}'}), 400
            df = pd.DataFrame([values], columns=FEATURE_COLUMNS)
        else:
            return jsonify({'error': "'values' must be a list or an object mapping feature name to value"}), 400

        X_t = transformer.transform(df)
    except Exception as e:
        return jsonify({'error': f'Transformer error: {e}'}), 400

    try:
        proba = float(model.predict_proba(X_t)[:, 1][0])
    except Exception as e:
        return jsonify({'error': f'Model prediction error: {e}'}), 500

    pred = int(proba >= 0.5)
    return jsonify({'probability_potable': proba, 'prediction': pred})


if __name__ == '__main__':
    # For local development; prefer running via `flask run` or a WSGI server in production.
    app.run(host='0.0.0.0', port=8000, debug=True)


