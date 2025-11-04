"""
Model Registry Module
---------------------
Handles loading and versioning of machine learning models.
"""

import os
import joblib

def load_model(model_name: str = "dummy_model.pkl"):
    """
    Load the specified model from the model registry.
    """
    model_path = os.path.join(os.path.dirname(__file__), model_name)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file '{model_name}' not found in model registry.")
    return joblib.load(model_path)

def list_models():
    """
    List all available models in the model registry.
    """
    base_dir = os.path.dirname(__file__)
    return [f for f in os.listdir(base_dir) if f.endswith(".pkl") or f.endswith(".joblib")]
