import argparse
import os
from typing import Dict, Any

import joblib
import numpy as np
import optuna
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

from src.utils.io import ensure_dir, load_yaml, save_json


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Train classification model")
	parser.add_argument("--params", type=str, required=True, help="Path to params.yaml")
	return parser.parse_args()


def load_splits(processed_dir: str, target_column: str):
	train = pd.read_csv(os.path.join(processed_dir, "train.csv"))
	val = pd.read_csv(os.path.join(processed_dir, "val.csv"))

	X_train = train.drop(columns=[target_column]).values
	y_train = train[target_column].values
	X_val = val.drop(columns=[target_column]).values
	y_val = val[target_column].values
	return X_train, y_train, X_val, y_val


def objective(trial: optuna.Trial, X: np.ndarray, y: np.ndarray, cv_folds: int) -> float:
	n_estimators = trial.suggest_int("n_estimators", 100, 500)
	max_depth = trial.suggest_int("max_depth", 3, 30)
	min_samples_split = trial.suggest_int("min_samples_split", 2, 10)
	min_samples_leaf = trial.suggest_int("min_samples_leaf", 1, 10)

	clf = RandomForestClassifier(
		n_estimators=n_estimators,
		max_depth=max_depth,
		min_samples_split=min_samples_split,
		min_samples_leaf=min_samples_leaf,
		class_weight="balanced",
		random_state=42,
		n_jobs=-1,
	)

	skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
	scores = []
	for train_idx, valid_idx in skf.split(X, y):
		X_tr, X_va = X[train_idx], X[valid_idx]
		y_tr, y_va = y[train_idx], y[valid_idx]
		clf.fit(X_tr, y_tr)
		proba = clf.predict_proba(X_va)[:, 1]
		scores.append(roc_auc_score(y_va, proba))
	return float(np.mean(scores))


def main() -> None:
	args = parse_args()
	params = load_yaml(args.params)

	processed_dir = params["data"]["processed_dir"]
	target_column = params["data"]["target_column"]
	registry_dir = params["registry"]["dir"]
	model_filename = params["registry"]["model_filename"]

	X_train, y_train, X_val, y_val = load_splits(processed_dir, target_column)

	# Hyperparameter tuning
	n_trials = int(params["train"]["n_trials"])
	cv_folds = int(params["train"]["cv_folds"])
	study = optuna.create_study(direction="maximize")
	study.optimize(lambda t: objective(t, X_train, y_train, cv_folds), n_trials=n_trials)
	best_params = study.best_params

	# Train final model using best params
	best_model = RandomForestClassifier(
		class_weight="balanced",
		random_state=42,
		n_jobs=-1,
		**best_params,
	)
	X_tr_full = np.vstack([X_train, X_val])
	y_tr_full = np.concatenate([y_train, y_val])
	best_model.fit(X_tr_full, y_tr_full)

	# Save model
	ensure_dir(registry_dir)
	model_path = os.path.join(registry_dir, model_filename)
	joblib.dump(best_model, model_path)

	# Save metrics for training set (AUC on val as proxy)
	val_proba = best_model.predict_proba(X_val)[:, 1]
	train_metrics = {"val_roc_auc": roc_auc_score(y_val, val_proba), "best_params": best_params}
	ensure_dir("artifacts/metrics")
	save_json(train_metrics, "artifacts/metrics/train_metrics.json")
	print(f"Model saved to {model_path}; AUC(val)={train_metrics['val_roc_auc']:.4f}")


if __name__ == "__main__":
	main()


