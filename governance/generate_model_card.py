#!/usr/bin/env python3
"""
Generate Model Card Script
Creates comprehensive model documentation for governance
"""

import argparse
import json
import os
import sys
from datetime import datetime
import joblib
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from governance.model_governance import ModelGovernance, ModelMetadata


def parse_args():
    parser = argparse.ArgumentParser(description="Generate model card for governance")
    parser.add_argument("--model-name", required=True, help="Name of the model")
    parser.add_argument("--version", required=True, help="Model version")
    parser.add_argument("--commit-hash", required=True, help="Git commit hash")
    parser.add_argument(
        "--model-path",
        default="app/model_registry/model.joblib",
        help="Path to model file",
    )
    parser.add_argument(
        "--test-data", default="data/processed/test.csv", help="Path to test data"
    )
    return parser.parse_args()


def get_model_performance(model_path: str, test_data_path: str):
    """Get model performance metrics"""
    try:
        model = joblib.load(model_path)
        test_data = pd.read_csv(test_data_path)

        X_test = test_data.drop(columns=["Potability"])
        y_test = test_data["Potability"]

        # Get predictions
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        from sklearn.metrics import (
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
            roc_auc_score,
        )

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_proba),
        }

        return metrics, len(test_data)

    except Exception as e:
        print(f"Warning: Could not load model performance: {e}")
        return {}, 0


def get_mlflow_info(model_name: str, version: str):
    """Get additional info from MLflow if available"""
    try:
        if not os.getenv("MLFLOW_TRACKING_URI"):
            return {}

        client = MlflowClient()
        model_version = client.get_model_version(model_name, version)

        # Get run information
        run = client.get_run(model_version.run_id)

        return {
            "mlflow_run_id": model_version.run_id,
            "mlflow_model_uri": model_version.source,
            "training_metrics": dict(run.data.metrics),
            "hyperparameters": dict(run.data.params),
        }

    except Exception as e:
        print(f"Warning: Could not get MLflow info: {e}")
        return {}


def main():
    args = parse_args()

    print(f"🏗️  Generating model card for {args.model_name} v{args.version}")

    # Initialize governance
    governance = ModelGovernance()

    # Get model performance
    performance_metrics, test_size = get_model_performance(
        args.model_path, args.test_data
    )

    # Get MLflow information
    mlflow_info = get_mlflow_info(args.model_name, args.version)

    # Create model metadata
    metadata = ModelMetadata(
        model_name=args.model_name,
        version=args.version,
        created_by=os.getenv("GITHUB_ACTOR", "system"),
        created_at=datetime.utcnow().isoformat(),
        commit_hash=args.commit_hash,
        branch=os.getenv("GITHUB_REF_NAME", "unknown"),
        environment=os.getenv("ENVIRONMENT", "development"),
        model_type="RandomForestClassifier",
        framework="scikit-learn",
        performance_metrics=performance_metrics,
        data_schema={
            "features": [
                "ph",
                "Hardness",
                "Solids",
                "Chloramines",
                "Sulfate",
                "Conductivity",
                "Organic_carbon",
                "Trihalomethanes",
                "Turbidity",
            ],
            "target": "Potability",
            "feature_types": {
                "ph": "float",
                "Hardness": "float",
                "Solids": "float",
                "Chloramines": "float",
                "Sulfate": "float",
                "Conductivity": "float",
                "Organic_carbon": "float",
                "Trihalomethanes": "float",
                "Turbidity": "float",
            },
        },
        training_data_info={
            "size": test_size * 4,  # Estimate total dataset size
            "test_size": test_size,
            "source": "Water Quality Dataset",
        },
        hyperparameters=mlflow_info.get("hyperparameters", {}),
        dependencies=[
            "scikit-learn>=1.3.0",
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "joblib>=1.3.0",
        ],
        compliance_status="PENDING",
        bias_assessment={},
        approval_status="PENDING",
    )

    # Register model
    success = governance.register_model(metadata)

    if success:
        # Generate model card
        card_path = governance.generate_model_card(args.model_name, args.version)
        print(f"✅ Model card generated: {card_path}")

        # Generate governance report
        report = {
            "model_name": args.model_name,
            "version": args.version,
            "registration_status": "SUCCESS",
            "model_card_path": card_path,
            "performance_metrics": performance_metrics,
            "compliance_checks": {
                "model_card": True,
                "performance_metrics": bool(performance_metrics),
                "data_schema": True,
                "dependencies": True,
            },
            "generated_at": datetime.utcnow().isoformat(),
        }

        report_path = (
            f"governance/reports/{args.model_name}-{args.version}-governance.json"
        )
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"✅ Governance report generated: {report_path}")

    else:
        print("❌ Failed to register model")
        sys.exit(1)


if __name__ == "__main__":
    main()
