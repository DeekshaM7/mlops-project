"""
Model Governance Framework
Implements comprehensive model versioning, audit trails, compliance measures, and bias mitigation
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import mlflow
import mlflow.sklearn
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ModelMetadata:
    """Model metadata for governance tracking"""

    model_name: str
    version: str
    created_by: str
    created_at: str
    commit_hash: str
    branch: str
    environment: str
    model_type: str
    framework: str
    performance_metrics: Dict[str, float]
    data_schema: Dict[str, Any]
    training_data_info: Dict[str, Any]
    hyperparameters: Dict[str, Any]
    dependencies: List[str]
    compliance_status: str
    bias_assessment: Dict[str, Any]
    approval_status: str
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None


@dataclass
class AuditTrailEntry:
    """Audit trail entry for tracking model lifecycle events"""

    timestamp: str
    event_type: str
    model_name: str
    model_version: str
    user: str
    action: str
    details: Dict[str, Any]
    environment: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ModelGovernance:
    """
    Comprehensive model governance system for MLOps pipeline
    """

    def __init__(self, governance_db_path: str = "governance/governance.db"):
        self.governance_db_path = governance_db_path
        self.audit_log_path = "governance/audit_trail.jsonl"
        self.compliance_rules_path = "governance/compliance_rules.json"
        self._ensure_directories()
        self._load_compliance_rules()

    def _ensure_directories(self):
        """Create necessary directories for governance"""
        os.makedirs(os.path.dirname(self.governance_db_path), exist_ok=True)
        os.makedirs("governance/reports", exist_ok=True)
        os.makedirs("governance/model-cards", exist_ok=True)
        os.makedirs("governance/audit-logs", exist_ok=True)

    def _load_compliance_rules(self):
        """Load compliance rules configuration"""
        try:
            with open(self.compliance_rules_path, "r") as f:
                self.compliance_rules = json.load(f)
        except FileNotFoundError:
            # Create default compliance rules
            self.compliance_rules = {
                "minimum_accuracy": 0.85,
                "maximum_bias_ratio": 0.1,
                "required_tests": ["unit_tests", "integration_tests", "bias_tests"],
                "required_documentation": [
                    "model_card",
                    "data_sheet",
                    "performance_report",
                ],
                "approval_required_for": ["production", "critical_systems"],
                "retention_policy_days": 365,
                "security_requirements": {
                    "vulnerability_scan": True,
                    "dependency_check": True,
                    "secrets_scan": True,
                },
            }
            self._save_compliance_rules()

    def _save_compliance_rules(self):
        """Save compliance rules to file"""
        with open(self.compliance_rules_path, "w") as f:
            json.dump(self.compliance_rules, f, indent=2)

    def log_audit_event(self, event: AuditTrailEntry):
        """Log an audit trail event"""
        with open(self.audit_log_path, "a") as f:
            f.write(json.dumps(asdict(event)) + "\n")

        logger.info(
            f"Audit event logged: {event.event_type} for {event.model_name}:{event.model_version}"
        )

    def register_model(self, metadata: ModelMetadata) -> bool:
        """Register a new model version with governance metadata"""
        try:
            # Log registration event
            audit_entry = AuditTrailEntry(
                timestamp=datetime.utcnow().isoformat(),
                event_type="MODEL_REGISTRATION",
                model_name=metadata.model_name,
                model_version=metadata.version,
                user=metadata.created_by,
                action="register_model",
                details={"metadata": asdict(metadata)},
                environment=metadata.environment,
            )
            self.log_audit_event(audit_entry)

            # Save metadata
            metadata_path = (
                f"governance/model-cards/{metadata.model_name}-{metadata.version}.json"
            )
            with open(metadata_path, "w") as f:
                json.dump(asdict(metadata), f, indent=2)

            # Register in MLflow if available
            if os.getenv("MLFLOW_TRACKING_URI"):
                self._register_mlflow_model(metadata)

            logger.info(f"Model registered: {metadata.model_name}:{metadata.version}")
            return True

        except Exception as e:
            logger.error(f"Failed to register model: {str(e)}")
            return False

    def _register_mlflow_model(self, metadata: ModelMetadata):
        """Register model in MLflow model registry"""
        try:
            mlflow.set_registry_uri(os.getenv("MLFLOW_TRACKING_URI"))

            # Create model version in registry
            client = mlflow.tracking.MlflowClient()

            # Register model with tags
            tags = {
                "governance.version": metadata.version,
                "governance.created_by": metadata.created_by,
                "governance.commit_hash": metadata.commit_hash,
                "governance.compliance_status": metadata.compliance_status,
                "governance.approval_status": metadata.approval_status,
                "governance.environment": metadata.environment,
            }

            # Update model version with governance tags
            try:
                model_version = client.get_model_version(
                    metadata.model_name, metadata.version
                )
                for key, value in tags.items():
                    client.set_model_version_tag(
                        metadata.model_name, metadata.version, key, value
                    )
            except mlflow.exceptions.RestException:
                logger.warning(
                    f"Model version not found in MLflow: {metadata.model_name}:{metadata.version}"
                )

        except Exception as e:
            logger.error(f"Failed to register model in MLflow: {str(e)}")

    def evaluate_compliance(
        self,
        model_name: str,
        model_version: str,
        performance_metrics: Dict[str, float],
        bias_metrics: Dict[str, float],
        test_results: Dict[str, bool],
    ) -> Dict[str, Any]:
        """Evaluate model compliance against governance rules"""

        compliance_report = {
            "model_name": model_name,
            "model_version": model_version,
            "evaluation_timestamp": datetime.utcnow().isoformat(),
            "overall_status": "PENDING",
            "checks": [],
        }

        all_passed = True

        # Performance check
        min_accuracy = self.compliance_rules.get("minimum_accuracy", 0.8)
        accuracy_check = {
            "check_name": "minimum_accuracy",
            "required": min_accuracy,
            "actual": performance_metrics.get("accuracy", 0.0),
            "status": (
                "PASS"
                if performance_metrics.get("accuracy", 0.0) >= min_accuracy
                else "FAIL"
            ),
            "details": f"Model accuracy must be >= {min_accuracy}",
        }
        compliance_report["checks"].append(accuracy_check)
        if accuracy_check["status"] == "FAIL":
            all_passed = False

        # Bias check
        max_bias = self.compliance_rules.get("maximum_bias_ratio", 0.1)
        bias_ratio = bias_metrics.get("max_bias_ratio", 0.0)
        bias_check = {
            "check_name": "bias_assessment",
            "required": f"<= {max_bias}",
            "actual": bias_ratio,
            "status": "PASS" if bias_ratio <= max_bias else "FAIL",
            "details": f"Maximum bias ratio must be <= {max_bias}",
        }
        compliance_report["checks"].append(bias_check)
        if bias_check["status"] == "FAIL":
            all_passed = False

        # Test requirements check
        required_tests = self.compliance_rules.get("required_tests", [])
        for test_name in required_tests:
            test_passed = test_results.get(test_name, False)
            test_check = {
                "check_name": f"required_test_{test_name}",
                "required": True,
                "actual": test_passed,
                "status": "PASS" if test_passed else "FAIL",
                "details": f"Required test '{test_name}' must pass",
            }
            compliance_report["checks"].append(test_check)
            if not test_passed:
                all_passed = False

        compliance_report["overall_status"] = (
            "COMPLIANT" if all_passed else "NON_COMPLIANT"
        )

        # Log compliance evaluation
        audit_entry = AuditTrailEntry(
            timestamp=datetime.utcnow().isoformat(),
            event_type="COMPLIANCE_EVALUATION",
            model_name=model_name,
            model_version=model_version,
            user="system",
            action="evaluate_compliance",
            details=compliance_report,
            environment="governance",
        )
        self.log_audit_event(audit_entry)

        return compliance_report

    def assess_bias(
        self, model, test_data: pd.DataFrame, protected_attributes: List[str]
    ) -> Dict[str, Any]:
        """Assess model bias across protected attributes"""

        bias_report = {
            "assessment_timestamp": datetime.utcnow().isoformat(),
            "protected_attributes": protected_attributes,
            "bias_metrics": {},
            "recommendations": [],
        }

        X_test = test_data.drop(columns=["Potability"])
        y_test = test_data["Potability"]
        y_pred = model.predict(X_test)

        overall_accuracy = (y_pred == y_test).mean()
        bias_ratios = []

        for attr in protected_attributes:
            if attr in test_data.columns:
                # Calculate bias metrics for each group
                unique_values = test_data[attr].unique()
                group_metrics = {}

                for value in unique_values:
                    mask = test_data[attr] == value
                    if mask.sum() > 0:
                        group_accuracy = (y_pred[mask] == y_test[mask]).mean()
                        group_metrics[str(value)] = {
                            "accuracy": float(group_accuracy),
                            "count": int(mask.sum()),
                            "positive_prediction_rate": float(
                                (y_pred[mask] == 1).mean()
                            ),
                        }

                # Calculate bias ratio (max difference in accuracy)
                accuracies = [metrics["accuracy"] for metrics in group_metrics.values()]
                bias_ratio = (
                    (max(accuracies) - min(accuracies)) if len(accuracies) > 1 else 0.0
                )
                bias_ratios.append(bias_ratio)

                bias_report["bias_metrics"][attr] = {
                    "group_metrics": group_metrics,
                    "bias_ratio": float(bias_ratio),
                    "overall_accuracy": float(overall_accuracy),
                }

                # Generate recommendations
                if bias_ratio > 0.05:  # 5% threshold
                    bias_report["recommendations"].append(
                        f"High bias detected for {attr} (ratio: {bias_ratio:.3f}). "
                        f"Consider data augmentation or bias mitigation techniques."
                    )

        bias_report["max_bias_ratio"] = float(max(bias_ratios)) if bias_ratios else 0.0
        bias_report["bias_assessment"] = (
            "LOW"
            if bias_report["max_bias_ratio"] < 0.05
            else "MODERATE" if bias_report["max_bias_ratio"] < 0.1 else "HIGH"
        )

        return bias_report

    def generate_model_card(self, model_name: str, model_version: str) -> str:
        """Generate comprehensive model card"""

        try:
            # Load model metadata
            metadata_path = f"governance/model-cards/{model_name}-{model_version}.json"
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            model_card_content = f"""
# Model Card: {model_name} v{model_version}

## Model Details
- **Model Name**: {model_name}
- **Version**: {model_version}
- **Created By**: {metadata.get('created_by', 'Unknown')}
- **Created At**: {metadata.get('created_at', 'Unknown')}
- **Model Type**: {metadata.get('model_type', 'Unknown')}
- **Framework**: {metadata.get('framework', 'Unknown')}
- **Git Commit**: {metadata.get('commit_hash', 'Unknown')}

## Intended Use
This model predicts water potability based on water quality parameters. It is intended for:
- Water quality assessment applications
- Environmental monitoring systems
- Public health decision support

## Training Data
- **Dataset**: Water Quality Dataset
- **Size**: {metadata.get('training_data_info', {}).get('size', 'Unknown')} samples
- **Features**: {len(metadata.get('data_schema', {}).get('features', []))} features
- **Target**: Binary classification (potable/non-potable)

## Performance Metrics
"""

            for metric, value in metadata.get("performance_metrics", {}).items():
                model_card_content += (
                    f"- **{metric.replace('_', ' ').title()}**: {value:.4f}\n"
                )

            model_card_content += f"""
## Bias Assessment
- **Bias Assessment Level**: {metadata.get('bias_assessment', {}).get('bias_assessment', 'Not Assessed')}
- **Max Bias Ratio**: {metadata.get('bias_assessment', {}).get('max_bias_ratio', 'N/A')}

## Compliance Status
- **Overall Status**: {metadata.get('compliance_status', 'Unknown')}
- **Approval Status**: {metadata.get('approval_status', 'Pending')}

## Limitations and Risks
- Model performance may vary on data from different water sources
- Regular retraining recommended as water quality standards evolve
- Should not be used as sole decision criterion for critical water safety decisions

## Governance Information
- **Environment**: {metadata.get('environment', 'Unknown')}
- **Retention Policy**: {self.compliance_rules.get('retention_policy_days', 365)} days
- **Last Updated**: {datetime.utcnow().isoformat()}
"""

            # Save model card
            card_path = f"governance/model-cards/{model_name}-{model_version}-card.md"
            with open(card_path, "w") as f:
                f.write(model_card_content)

            logger.info(f"Model card generated: {card_path}")
            return card_path

        except Exception as e:
            logger.error(f"Failed to generate model card: {str(e)}")
            raise

    def get_audit_trail(self, model_name: str, model_version: str = None) -> List[Dict]:
        """Retrieve audit trail for a model"""
        audit_entries = []

        try:
            with open(self.audit_log_path, "r") as f:
                for line in f:
                    entry = json.loads(line.strip())
                    if entry.get("model_name") == model_name:
                        if (
                            model_version is None
                            or entry.get("model_version") == model_version
                        ):
                            audit_entries.append(entry)

            # Sort by timestamp
            audit_entries.sort(key=lambda x: x.get("timestamp", ""))

        except FileNotFoundError:
            logger.warning("Audit trail file not found")

        return audit_entries

    def approve_model(
        self, model_name: str, model_version: str, approver: str, notes: str = ""
    ) -> bool:
        """Approve model for deployment"""

        try:
            # Load current metadata
            metadata_path = f"governance/model-cards/{model_name}-{model_version}.json"
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Update approval status
            metadata["approval_status"] = "APPROVED"
            metadata["approved_by"] = approver
            metadata["approved_at"] = datetime.utcnow().isoformat()

            # Save updated metadata
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            # Log approval event
            audit_entry = AuditTrailEntry(
                timestamp=datetime.utcnow().isoformat(),
                event_type="MODEL_APPROVAL",
                model_name=model_name,
                model_version=model_version,
                user=approver,
                action="approve_model",
                details={"notes": notes},
                environment="governance",
            )
            self.log_audit_event(audit_entry)

            logger.info(f"Model approved: {model_name}:{model_version} by {approver}")
            return True

        except Exception as e:
            logger.error(f"Failed to approve model: {str(e)}")
            return False
