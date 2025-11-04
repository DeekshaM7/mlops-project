# DVC Experiments Guide

This guide explains how to run, track, and compare experiments using DVC and MLflow.

## 🚀 Quick Start

### Run All 20 Experiments Automatically
```powershell
# Automated: Runs 10 RF + 10 XGBoost experiments
.\run_experiments.ps1
```

### Manual Experiment Workflow
```powershell
# 1. Start MLflow UI (in separate terminal)
mlflow ui

# 2. Run a single experiment
dvc exp run --name my-exp-1 --set-param model.type=xgboost --set-param train.n_trials=25

# 3. View results
dvc exp show
```

---

## 📊 What Gets Tracked?

### By DVC:
- ✅ Model type (random_forest or xgboost)
- ✅ Number of hyperparameter tuning trials
- ✅ Cross-validation folds
- ✅ Validation ROC-AUC score
- ✅ All model parameters
- ✅ Code versions and data versions

### By MLflow:
- ✅ All hyperparameters (n_estimators, max_depth, learning_rate, etc.)
- ✅ Training metrics (val_roc_auc, best_cv_score)
- ✅ Model artifacts (saved models)
- ✅ Dataset characteristics
- ✅ Run duration and timestamps
- ✅ Experiment comparison and visualization

---

## 🔬 Experiment Configurations

### Random Forest Experiments (10 total)
```yaml
Experiment 1:  n_trials=15, cv_folds=5
Experiment 2:  n_trials=20, cv_folds=5
Experiment 3:  n_trials=25, cv_folds=5
Experiment 4:  n_trials=20, cv_folds=3
Experiment 5:  n_trials=20, cv_folds=7
Experiment 6:  n_trials=30, cv_folds=5
Experiment 7:  n_trials=15, cv_folds=3
Experiment 8:  n_trials=25, cv_folds=3
Experiment 9:  n_trials=10, cv_folds=5
Experiment 10: n_trials=35, cv_folds=5
```

### XGBoost Experiments (10 total)
```yaml
Experiment 1:  n_trials=15, cv_folds=5
Experiment 2:  n_trials=20, cv_folds=5
Experiment 3:  n_trials=25, cv_folds=5
Experiment 4:  n_trials=20, cv_folds=3
Experiment 5:  n_trials=20, cv_folds=7
Experiment 6:  n_trials=30, cv_folds=5
Experiment 7:  n_trials=15, cv_folds=3
Experiment 8:  n_trials=25, cv_folds=3
Experiment 9:  n_trials=10, cv_folds=5
Experiment 10: n_trials=35, cv_folds=5
```

---

## 📈 Viewing Experiment Results

### DVC Commands

```powershell
# Show all experiments
dvc exp show

# Show only changed parameters and metrics
dvc exp show --only-changed

# Sort by validation AUC (descending)
dvc exp show --sort-by='artifacts/metrics/train_metrics.json:val_roc_auc' --sort-order=desc

# Compare specific experiments
dvc exp diff <exp1> <exp2>

# Show experiment details
dvc exp show --include-params=model,train

# Filter experiments
dvc exp show --only-changed --include-params=model.type
```

### MLflow UI

```powershell
# Start MLflow UI
mlflow ui

# Access in browser
http://localhost:5000
```

**MLflow Features:**
- 📊 Visual comparison of metrics across runs
- 📈 Parallel coordinates plots
- 🔍 Filter and search experiments
- 📥 Download models and artifacts
- 🏆 Compare best performing models

---

## 🎯 Selecting the Best Model

### Method 1: DVC Sort
```powershell
# Find best by validation AUC
dvc exp show --sort-by='artifacts/metrics/train_metrics.json:val_roc_auc' --sort-order=desc | head -5
```

### Method 2: MLflow UI
1. Go to http://localhost:5000
2. Select experiment: "water-potability-random_forest" or "water-potability-xgboost"
3. Sort by "val_roc_auc" metric
4. Compare top performers

### Method 3: Python Script
```python
import mlflow
import pandas as pd

# Get all runs
client = mlflow.tracking.MlflowClient()
experiments = client.search_experiments()

best_runs = []
for exp in experiments:
    runs = client.search_runs(exp.experiment_id, order_by=["metrics.val_roc_auc DESC"], max_results=5)
    best_runs.extend(runs)

# Create comparison DataFrame
df = pd.DataFrame([{
    'experiment': run.info.experiment_id,
    'run_id': run.info.run_id,
    'model_type': run.data.params.get('model_type'),
    'val_roc_auc': run.data.metrics.get('val_roc_auc'),
    'n_trials': run.data.params.get('n_trials'),
    'cv_folds': run.data.params.get('cv_folds')
} for run in best_runs])

print(df.sort_values('val_roc_auc', ascending=False))
```

---

## 🔄 Applying the Best Experiment

```powershell
# 1. Identify best experiment name
dvc exp show --sort-by='artifacts/metrics/train_metrics.json:val_roc_auc' --sort-order=desc

# 2. Apply the experiment
dvc exp apply <best-experiment-name>

# 3. Commit the changes
git add .
git commit -m "Apply best experiment: <experiment-name>"

# 4. Push to production
git push origin master
```

---

## 📤 Sharing Experiments

### Push to DVC Remote
```powershell
# Push all experiments
dvc exp push origin

# Push specific experiment
dvc exp push origin <experiment-name>
```

### Pull from DVC Remote
```powershell
# List remote experiments
dvc exp list origin

# Pull specific experiment
dvc exp pull origin <experiment-name>

# Pull all experiments
dvc exp pull origin --all
```

---

## 🧪 Running Custom Experiments

### Single Model Type
```powershell
# Random Forest with custom params
dvc exp run --name rf-custom-1 \
  --set-param model.type=random_forest \
  --set-param train.n_trials=40 \
  --set-param train.cv_folds=10

# XGBoost with custom params
dvc exp run --name xgb-custom-1 \
  --set-param model.type=xgboost \
  --set-param train.n_trials=50 \
  --set-param train.cv_folds=5
```

### Batch Experiments
```powershell
# Run multiple experiments in sequence
dvc exp run --name exp-1 --set-param train.n_trials=10
dvc exp run --name exp-2 --set-param train.n_trials=20
dvc exp run --name exp-3 --set-param train.n_trials=30
```

### Queue Experiments (Parallel)
```powershell
# Queue multiple experiments
dvc exp run --queue --name exp-1 --set-param train.n_trials=10
dvc exp run --queue --name exp-2 --set-param train.n_trials=20
dvc exp run --queue --name exp-3 --set-param train.n_trials=30

# Run all queued experiments in parallel (2 workers)
dvc queue start --jobs 2
```

---

## 📊 Experiment Metrics Tracked

### Training Metrics (`artifacts/metrics/train_metrics.json`)
- `val_roc_auc` - Validation ROC-AUC score
- `model_type` - Model algorithm used
- `best_params` - Best hyperparameters found
- `best_cv_score` - Best cross-validation score

### Test Metrics (`artifacts/metrics/test_metrics.json`)
- `test_roc_auc` - Test set ROC-AUC
- `test_accuracy` - Test set accuracy
- `test_precision` - Test set precision
- `test_recall` - Test set recall
- `test_f1` - Test set F1-score

---

## 🔍 Troubleshooting

### Issue: "No experiments to show"
```powershell
# Make sure you've run at least one experiment
dvc exp run

# Check experiment list
dvc exp list
```

### Issue: MLflow not tracking
```powershell
# Verify MLflow server is running
curl http://localhost:5000

# Check MLflow tracking URI
echo $env:MLFLOW_TRACKING_URI

# Restart MLflow
mlflow ui --host 0.0.0.0 --port 5000
```

### Issue: Experiments running slow
```powershell
# Reduce n_trials for faster experiments
dvc exp run --set-param train.n_trials=5

# Use fewer CV folds
dvc exp run --set-param train.cv_folds=3
```

### Issue: Out of memory
```powershell
# Reduce dataset size or use subset
# Reduce n_estimators
# Use fewer parallel jobs in model training
```

---

## 📚 Additional Resources

- **DVC Experiments Documentation**: https://dvc.org/doc/user-guide/experiment-management
- **MLflow Documentation**: https://mlflow.org/docs/latest/index.html
- **XGBoost Documentation**: https://xgboost.readthedocs.io/
- **Optuna Documentation**: https://optuna.readthedocs.io/

---

## 🎉 Expected Results

After running all 20 experiments, you should have:

✅ 10 Random Forest models with different configurations  
✅ 10 XGBoost models with different configurations  
✅ All experiments tracked in DVC  
✅ All experiments logged in MLflow  
✅ Metrics comparison available  
✅ Best model identified  
✅ Model artifacts saved  
✅ Reproducible results  

**Total Expected Time:** 30-60 minutes (depending on hardware)
