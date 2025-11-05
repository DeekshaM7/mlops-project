import argparse
import os
from typing import Dict, Any, Tuple

import joblib
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import numpy as np
import optuna
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

from src.utils.io import ensure_dir, load_yaml, save_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train classification model")
    parser.add_argument("--params", type=str, required=True, help="Path to params.yaml")
    return parser.parse_args()


def load_splits(
    processed_dir: str, target_column: str
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    train = pd.read_csv(os.path.join(processed_dir, "train.csv"))
    val = pd.read_csv(os.path.join(processed_dir, "val.csv"))

    X_train = train.drop(columns=[target_column]).values
    y_train = train[target_column].values
    X_val = val.drop(columns=[target_column]).values
    y_val = val[target_column].values
    return X_train, y_train, X_val, y_val


def objective_rf(
    trial: optuna.Trial, X: np.ndarray, y: np.ndarray, cv_folds: int
) -> float:
    """Random Forest hyperparameter optimization"""
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


def objective_xgb(
    trial: optuna.Trial, X: np.ndarray, y: np.ndarray, cv_folds: int
) -> float:
    """XGBoost hyperparameter optimization"""
    n_estimators = trial.suggest_int("n_estimators", 100, 500)
    max_depth = trial.suggest_int("max_depth", 3, 15)
    learning_rate = trial.suggest_float("learning_rate", 0.01, 0.3, log=True)
    subsample = trial.suggest_float("subsample", 0.6, 1.0)
    colsample_bytree = trial.suggest_float("colsample_bytree", 0.6, 1.0)
    min_child_weight = trial.suggest_int("min_child_weight", 1, 10)
    gamma = trial.suggest_float("gamma", 0.0, 1.0)
    reg_alpha = trial.suggest_float("reg_alpha", 0.0, 1.0)
    reg_lambda = trial.suggest_float("reg_lambda", 0.0, 1.0)

    clf = XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        min_child_weight=min_child_weight,
        gamma=gamma,
        reg_alpha=reg_alpha,
        reg_lambda=reg_lambda,
        random_state=42,
        n_jobs=-1,
        eval_metric="logloss",
        use_label_encoder=False,
    )

    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    scores = []
    for train_idx, valid_idx in skf.split(X, y):
        X_tr, X_va = X[train_idx], X[valid_idx]
        y_tr, y_va = y[train_idx], y[valid_idx]
        clf.fit(X_tr, y_tr, verbose=False)
        proba = clf.predict_proba(X_va)[:, 1]
        scores.append(roc_auc_score(y_va, proba))
    return float(np.mean(scores))


def train_model(
    model_type: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    params: Dict[str, Any],
) -> Tuple[Any, float, Dict[str, Any]]:
    """Train model based on type with hyperparameter tuning"""

    n_trials = int(params["train"]["n_trials"])
    cv_folds = int(params["train"]["cv_folds"])

    # Hyperparameter tuning
    study = optuna.create_study(direction="maximize")

    if model_type == "random_forest":
        study.optimize(
            lambda t: objective_rf(t, X_train, y_train, cv_folds), n_trials=n_trials
        )
        best_params = study.best_params

        # Train final model
        best_model = RandomForestClassifier(
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
            **best_params,
        )

    elif model_type == "xgboost":
        study.optimize(
            lambda t: objective_xgb(t, X_train, y_train, cv_folds), n_trials=n_trials
        )
        best_params = study.best_params

        # Calculate scale_pos_weight for imbalanced dataset
        scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

        # Train final model
        best_model = XGBClassifier(
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            n_jobs=-1,
            eval_metric="logloss",
            use_label_encoder=False,
            **best_params,
        )
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    # Train on combined train+val data
    X_tr_full = np.vstack([X_train, X_val])
    y_tr_full = np.concatenate([y_train, y_val])

    if model_type == "xgboost":
        best_model.fit(X_tr_full, y_tr_full, verbose=False)
    else:
        best_model.fit(X_tr_full, y_tr_full)

    # Evaluate on validation set
    val_proba = best_model.predict_proba(X_val)[:, 1]
    val_auc = roc_auc_score(y_val, val_proba)

    best_params["best_cv_score"] = study.best_value

    return best_model, val_auc, best_params


def main() -> None:
    args = parse_args()
    params = load_yaml(args.params)

    processed_dir = params["data"]["processed_dir"]
    target_column = params["data"]["target_column"]
    registry_dir = params["registry"]["dir"]
    model_filename = params["registry"]["model_filename"]
    model_type = params["model"]["type"]

    # Initialize MLflow
    experiment_name = f"water-potability-{model_type}"
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run():
        # Log model type
        mlflow.log_param("model_type", model_type)

        X_train, y_train, X_val, y_val = load_splits(processed_dir, target_column)

        # Log dataset info
        mlflow.log_param("n_samples_train", len(X_train))
        mlflow.log_param("n_samples_val", len(X_val))
        mlflow.log_param("n_features", X_train.shape[1])
        mlflow.log_param("n_trials", params["train"]["n_trials"])
        mlflow.log_param("cv_folds", params["train"]["cv_folds"])

        # Train model
        print(f"Training {model_type} model...")
        best_model, val_auc, best_params = train_model(
            model_type, X_train, y_train, X_val, y_val, params
        )

        # Log hyperparameters
        for param, value in best_params.items():
            mlflow.log_param(param, value)

        # Save model
        ensure_dir(registry_dir)
        model_path = os.path.join(registry_dir, model_filename)
        joblib.dump(best_model, model_path)

        # Save metrics
        train_metrics = {
            "model_type": model_type,
            "val_roc_auc": val_auc,
            "best_params": best_params,
        }

        # Log metrics to MLflow
        mlflow.log_metric("val_roc_auc", val_auc)
        mlflow.log_metric("best_cv_score", best_params["best_cv_score"])

        # Log model to MLflow
        if model_type == "xgboost":
            mlflow.xgboost.log_model(
                best_model,
                "model",
                registered_model_name=f"water-potability-{model_type}",
            )
        else:
            mlflow.sklearn.log_model(
                best_model,
                "model",
                registered_model_name=f"water-potability-{model_type}",
            )

        # Log artifacts
        ensure_dir("artifacts/metrics")
        save_json(train_metrics, "artifacts/metrics/train_metrics.json")
        mlflow.log_artifact("artifacts/metrics/train_metrics.json")

        print(f"✅ Model saved to {model_path}")
        print(f"✅ Model type: {model_type}")
        print(f"✅ Validation AUC: {val_auc:.4f}")
        print(f"✅ Best CV Score: {best_params['best_cv_score']:.4f}")
        print(f"✅ MLflow run ID: {mlflow.active_run().info.run_id}")


if __name__ == "__main__":
    main()
