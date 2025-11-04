import argparse
import os

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    accuracy_score,
    f1_score,
    roc_auc_score,
)

from src.utils.io import ensure_dir, load_yaml, save_json


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate trained model on test set")
    parser.add_argument("--params", type=str, required=True, help="Path to params.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    params = load_yaml(args.params)

    processed_dir = params["data"]["processed_dir"]
    target_column = params["data"]["target_column"]
    registry_dir = params["registry"]["dir"]
    model_filename = params["registry"]["model_filename"]
    plots_dir = params["evaluate"]["plots_dir"]
    threshold = float(params["evaluate"]["threshold"])

    model_path = os.path.join(registry_dir, model_filename)
    test = pd.read_csv(os.path.join(processed_dir, "test.csv"))
    X_test = test.drop(columns=[target_column]).values
    y_test = test[target_column].values

    clf = joblib.load(model_path)
    proba = clf.predict_proba(X_test)[:, 1]
    pred = (proba >= threshold).astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_test, pred)),
        "f1": float(f1_score(y_test, pred)),
        "roc_auc": float(roc_auc_score(y_test, proba)),
    }
    ensure_dir("artifacts/metrics")
    save_json(metrics, "artifacts/metrics/test_metrics.json")

    # Plots
    ensure_dir(plots_dir)
    fig_roc, ax_roc = plt.subplots(figsize=(6, 6))
    RocCurveDisplay.from_predictions(y_test, proba, ax=ax_roc)
    fig_roc.tight_layout()
    roc_path = os.path.join(plots_dir, "roc_curve.png")
    fig_roc.savefig(roc_path, dpi=150)
    plt.close(fig_roc)

    fig_cm, ax_cm = plt.subplots(figsize=(6, 6))
    ConfusionMatrixDisplay.from_predictions(y_test, pred, ax=ax_cm)
    fig_cm.tight_layout()
    cm_path = os.path.join(plots_dir, "confusion_matrix.png")
    fig_cm.savefig(cm_path, dpi=150)
    plt.close(fig_cm)

    print(f"Saved metrics and plots to artifacts; ROC-AUC={metrics['roc_auc']:.4f}")


if __name__ == "__main__":
    main()
