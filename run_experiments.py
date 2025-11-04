#!/usr/bin/env python3
"""
Run multiple DVC experiments with different model types and hyperparameters.
Each experiment is tracked by both DVC and MLflow.
"""

import subprocess
import time
from typing import List, Dict, Any
import json
import os

# Experiment configurations
EXPERIMENTS: List[Dict[str, Any]] = [
    # Random Forest Experiments (10 experiments)
    # {"name": "rf_exp_1", "model_type": "random_forest", "n_trials": 15, "cv_folds": 5},
    # {"name": "rf_exp_2", "model_type": "random_forest", "n_trials": 20, "cv_folds": 5},
    # {"name": "rf_exp_3", "model_type": "random_forest", "n_trials": 25, "cv_folds": 5},
    # {"name": "rf_exp_4", "model_type": "random_forest", "n_trials": 20, "cv_folds": 3},
    # {"name": "rf_exp_5", "model_type": "random_forest", "n_trials": 20, "cv_folds": 7},
    # {"name": "rf_exp_6", "model_type": "random_forest", "n_trials": 30, "cv_folds": 5},
    # {"name": "rf_exp_7", "model_type": "random_forest", "n_trials": 15, "cv_folds": 3},
    # {"name": "rf_exp_8", "model_type": "random_forest", "n_trials": 25, "cv_folds": 3},
    # {"name": "rf_exp_9", "model_type": "random_forest", "n_trials": 10, "cv_folds": 5},
    # {"name": "rf_exp_10", "model_type": "random_forest", "n_trials": 35, "cv_folds": 5},
    # XGBoost Experiments (10 experiments)
    {"name": "xgb_exp_1", "model_type": "xgboost", "n_trials": 15, "cv_folds": 5},
    {"name": "xgb_exp_2", "model_type": "xgboost", "n_trials": 20, "cv_folds": 5},
    {"name": "xgb_exp_3", "model_type": "xgboost", "n_trials": 25, "cv_folds": 5},
    {"name": "xgb_exp_4", "model_type": "xgboost", "n_trials": 20, "cv_folds": 3},
    {"name": "xgb_exp_5", "model_type": "xgboost", "n_trials": 20, "cv_folds": 7},
    {"name": "xgb_exp_6", "model_type": "xgboost", "n_trials": 30, "cv_folds": 5},
    {"name": "xgb_exp_7", "model_type": "xgboost", "n_trials": 15, "cv_folds": 3},
    {"name": "xgb_exp_8", "model_type": "xgboost", "n_trials": 25, "cv_folds": 3},
    {"name": "xgb_exp_9", "model_type": "xgboost", "n_trials": 10, "cv_folds": 5},
    {"name": "xgb_exp_10", "model_type": "xgboost", "n_trials": 35, "cv_folds": 5},
]


def run_dvc_experiment(exp_config: Dict[str, Any]) -> bool:
    """Run a single DVC experiment with given configuration."""

    exp_name = exp_config["name"]
    model_type = exp_config["model_type"]
    n_trials = exp_config["n_trials"]
    cv_folds = exp_config["cv_folds"]

    print(f"\n{'='*80}")
    print(f"🚀 Running Experiment: {exp_name}")
    print(f"   Model Type: {model_type}")
    print(f"   N Trials: {n_trials}")
    print(f"   CV Folds: {cv_folds}")
    print(f"{'='*80}\n")

    # Build DVC experiment command with proper parameter syntax
    # Use 'params.yaml:param.path' format for nested parameters
    cmd = [
        "dvc",
        "exp",
        "run",
        "--name",
        exp_name,
        "--set-param",
        f"configs/params.yaml:model.type={model_type}",
        "--set-param",
        f"configs/params.yaml:train.n_trials={n_trials}",
        "--set-param",
        f"configs/params.yaml:train.cv_folds={cv_folds}",
    ]

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Run the experiment
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            print(f"✅ Experiment {exp_name} completed successfully!")
            print(result.stdout)

            return True

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.lower()

            # Check for permission errors
            if "permission denied" in error_msg or "errno 13" in error_msg:
                print(f"⚠️  Permission error on attempt {attempt + 1}/{max_retries}")

                if attempt < max_retries - 1:
                    print(f"   Retrying in 3 seconds...")
                    time.sleep(3)

                    # Try to clear locks
                    try:
                        tmp_locks = [".dvc/tmp/lock", ".dvc/tmp/index/lock"]
                        for lock in tmp_locks:
                            if os.path.exists(lock):
                                os.remove(lock)
                                print(f"   Removed lock: {lock}")
                    except:
                        pass

                    # Try to fix permissions
                    try:
                        subprocess.run(
                            ["chmod", "-R", "u+rwX", ".dvc/cache", ".dvc/tmp"],
                            capture_output=True,
                            check=False,
                        )
                    except:
                        pass

                    continue
                else:
                    print(
                        f"❌ Experiment {exp_name} failed after {max_retries} attempts!"
                    )
                    print(f"\n💡 FIX: Run these commands to fix permissions:")
                    print(f"   sudo chown -R $USER:$USER .")
                    print(f"   chmod -R u+rwX .dvc")
                    print(f"\nError: {e.stderr}")
                    return False
            else:
                print(f"❌ Experiment {exp_name} failed!")
                print(f"Error: {e.stderr}")
                return False

    return False


def main():
    """Run all experiments."""

    print("=" * 80)
    print("🔬 DVC + MLflow Experiment Runner")
    print("=" * 80)
    print(f"Total experiments to run: {len(EXPERIMENTS)}")
    print(f"Models: Random Forest (10), XGBoost (10)")
    print("=" * 80)

    # Track results
    results = {
        "total": len(EXPERIMENTS),
        "successful": 0,
        "failed": 0,
        "experiments": [],
    }

    start_time = time.time()

    # Run each experiment
    for i, exp_config in enumerate(EXPERIMENTS, 1):
        print(f"\n📊 Progress: {i}/{len(EXPERIMENTS)}")

        exp_start = time.time()
        success = run_dvc_experiment(exp_config)
        exp_duration = time.time() - exp_start

        # Record result
        exp_result = {
            "name": exp_config["name"],
            "model_type": exp_config["model_type"],
            "success": success,
            "duration_seconds": round(exp_duration, 2),
        }
        results["experiments"].append(exp_result)

        if success:
            results["successful"] += 1
        else:
            results["failed"] += 1

        print(f"⏱️  Duration: {exp_duration:.2f}s")

        # Small delay between experiments
        if i < len(EXPERIMENTS):
            time.sleep(2)

    total_duration = time.time() - start_time

    # Print summary
    print("\n" + "=" * 80)
    print("📈 EXPERIMENT SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {results['successful']}/{results['total']}")
    print(f"❌ Failed: {results['failed']}/{results['total']}")
    print(f"⏱️  Total Duration: {total_duration/60:.2f} minutes")
    print("=" * 80)

    # Save results
    results["total_duration_minutes"] = round(total_duration / 60, 2)

    os.makedirs("artifacts/experiments", exist_ok=True)
    with open("artifacts/experiments/experiment_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📝 Results saved to: artifacts/experiments/experiment_results.json")

    # Show commands for next steps
    print("\n" + "=" * 80)
    print("🎯 NEXT STEPS")
    print("=" * 80)
    print("1. View all experiments:")
    print("   dvc exp show")
    print()
    print("2. Compare experiments:")
    print("   dvc exp show --only-changed")
    print()
    print("3. View MLflow UI:")
    print("   mlflow ui")
    print()
    print("4. Apply best experiment:")
    print("   dvc exp apply <exp-name>")
    print()
    print("5. Push experiments to remote:")
    print("   dvc exp push origin")
    print("=" * 80)

    return results["failed"] == 0


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
