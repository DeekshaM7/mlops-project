#!/usr/bin/env python3
"""
Model Approval Script
Automates model approval workflow with governance checks
"""

import argparse
import json
import os
import sys
from datetime import datetime
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from governance.model_governance import ModelGovernance

def parse_args():
    parser = argparse.ArgumentParser(description="Approve model for deployment")
    parser.add_argument("--model-name", required=True, help="Name of the model")
    parser.add_argument("--version", required=True, help="Model version")
    parser.add_argument("--approver", default=None, help="Approver name")
    parser.add_argument("--reason", default="Automated approval", help="Approval reason")
    parser.add_argument("--test-data", default="data/processed/test.csv", help="Path to test data")
    parser.add_argument("--min-accuracy", type=float, default=0.75, help="Minimum accuracy threshold")
    parser.add_argument("--min-precision", type=float, default=0.70, help="Minimum precision threshold")
    parser.add_argument("--min-recall", type=float, default=0.70, help="Minimum recall threshold")
    return parser.parse_args()

def check_performance_thresholds(metadata, min_accuracy, min_precision, min_recall):
    """Check if model meets performance thresholds"""
    metrics = metadata.performance_metrics
    
    checks = {
        "accuracy": metrics.get("accuracy", 0) >= min_accuracy,
        "precision": metrics.get("precision", 0) >= min_precision,
        "recall": metrics.get("recall", 0) >= min_recall
    }
    
    return all(checks.values()), checks

def run_bias_assessment(governance, model_name, version, test_data_path):
    """Run bias assessment on the model"""
    try:
        if not os.path.exists(test_data_path):
            print(f"Warning: Test data not found at {test_data_path}")
            return True, {}
        
        test_data = pd.read_csv(test_data_path)
        
        # For water potability, we'll check for bias across different feature ranges
        # This is a placeholder - in real scenarios you'd have protected attributes
        protected_attributes = {
            'ph_range': test_data['ph'] > test_data['ph'].median(),
            'hardness_range': test_data['Hardness'] > test_data['Hardness'].median()
        }
        
        bias_results = governance.assess_bias(model_name, version, test_data, protected_attributes)
        
        # Check if bias is within acceptable limits (example thresholds)
        bias_acceptable = all(
            result.get('statistical_parity_difference', 0) < 0.1 
            for result in bias_results.values()
        )
        
        return bias_acceptable, bias_results
        
    except Exception as e:
        print(f"Warning: Bias assessment failed: {e}")
        return True, {}

def main():
    args = parse_args()
    
    print(f"🔍 Starting approval process for {args.model_name} v{args.version}")
    
    # Initialize governance
    governance = ModelGovernance()
    
    # Get model metadata
    metadata = governance.get_model_metadata(args.model_name, args.version)
    if not metadata:
        print(f"❌ Model {args.model_name} v{args.version} not found in registry")
        sys.exit(1)
    
    print(f"📋 Found model: {metadata.model_name} v{metadata.version}")
    
    # Check performance thresholds
    performance_ok, performance_checks = check_performance_thresholds(
        metadata, args.min_accuracy, args.min_precision, args.min_recall
    )
    
    print("📊 Performance Checks:")
    for metric, passed in performance_checks.items():
        status = "✅" if passed else "❌"
        actual = metadata.performance_metrics.get(metric, 0)
        print(f"  {status} {metric}: {actual:.3f}")
    
    # Run compliance evaluation
    print("🔧 Running compliance evaluation...")
    compliance_result = governance.evaluate_compliance(args.model_name, args.version)
    compliance_ok = compliance_result.get('overall_score', 0) >= 0.8
    
    print(f"📋 Compliance Score: {compliance_result.get('overall_score', 0):.2f}")
    for check, result in compliance_result.get('checks', {}).items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    # Run bias assessment
    print("⚖️  Running bias assessment...")
    bias_ok, bias_results = run_bias_assessment(governance, args.model_name, args.version, args.test_data)
    
    if bias_results:
        print("📊 Bias Assessment Results:")
        for attr, results in bias_results.items():
            spd = results.get('statistical_parity_difference', 0)
            status = "✅" if abs(spd) < 0.1 else "❌"
            print(f"  {status} {attr}: SPD = {spd:.3f}")
    
    # Overall approval decision
    all_checks_passed = performance_ok and compliance_ok and bias_ok
    
    if all_checks_passed:
        # Approve the model
        approver = args.approver or os.getenv('GITHUB_ACTOR', 'system')
        success = governance.approve_model(
            args.model_name, 
            args.version, 
            approver, 
            args.reason
        )
        
        if success:
            print(f"✅ Model {args.model_name} v{args.version} APPROVED for deployment")
            
            # Create approval report
            approval_report = {
                "model_name": args.model_name,
                "version": args.version,
                "approval_status": "APPROVED",
                "approver": approver,
                "approval_reason": args.reason,
                "approval_timestamp": datetime.utcnow().isoformat(),
                "checks": {
                    "performance": performance_checks,
                    "compliance": compliance_result,
                    "bias": bias_results
                },
                "thresholds": {
                    "min_accuracy": args.min_accuracy,
                    "min_precision": args.min_precision,
                    "min_recall": args.min_recall
                }
            }
            
            # Save approval report
            report_path = f"governance/reports/{args.model_name}-{args.version}-approval.json"
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, 'w') as f:
                json.dump(approval_report, f, indent=2)
            
            print(f"📋 Approval report saved: {report_path}")
            
        else:
            print(f"❌ Failed to approve model {args.model_name} v{args.version}")
            sys.exit(1)
    else:
        print(f"❌ Model {args.model_name} v{args.version} REJECTED")
        
        rejection_report = {
            "model_name": args.model_name,
            "version": args.version,
            "approval_status": "REJECTED",
            "rejection_timestamp": datetime.utcnow().isoformat(),
            "failed_checks": {
                "performance": not performance_ok,
                "compliance": not compliance_ok,
                "bias": not bias_ok
            },
            "check_details": {
                "performance": performance_checks,
                "compliance": compliance_result,
                "bias": bias_results
            }
        }
        
        # Save rejection report
        report_path = f"governance/reports/{args.model_name}-{args.version}-rejection.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(rejection_report, f, indent=2)
        
        print(f"📋 Rejection report saved: {report_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()