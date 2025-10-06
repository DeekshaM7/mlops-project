from typing import List

import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel, Field


class Features(BaseModel):
	values: List[float] = Field(..., description="Ordered feature vector matching training columns")


app = FastAPI(title="Water Quality Potability API", version="0.1.0")


def _load_model_and_transformer():
	model = joblib.load("app/model_registry/model.joblib")
	# Transformer saved during preprocess lives under data/processed
	transformer = joblib.load("data/processed/transformer.joblib")
	return model, transformer


@app.get("/")
def root():
	return {"status": "ok", "message": "Water Quality Potability API"}


@app.post("/predict")
def predict(features: Features):
	model, transformer = _load_model_and_transformer()
	X = np.array([features.values])
	X_t = transformer.transform(X)
	proba = float(model.predict_proba(X_t)[:, 1][0])
	pred = int(proba >= 0.5)
	return {"probability_potable": proba, "prediction": pred}


