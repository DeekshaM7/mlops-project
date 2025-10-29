# MLOps Governance Dashboard

## Overview

The governance dashboard provides real-time visualization of your MLOps pipeline metrics, model registry, audit trails, performance reports, and compliance status using **actual data** from MLflow, test results, and governance logs.

## 🚀 Quick Start

### 1. Generate Dashboard Data

First, fetch the latest data from your MLflow runs and metrics files:

```bash
python governance/fetch_dashboard_data.py
```

This creates `governance/dashboard_data.json` with:
- ✅ Test metrics from `artifacts/metrics/test_metrics.json`
- ✅ Training metrics from `artifacts/metrics/train_metrics.json`
- ✅ Latest MLflow run data (metrics, parameters, metadata)
- ✅ Model registry information
- ✅ Audit trail entries (if available)

### 2. Serve the Dashboard

**Option A: Using the included server (Recommended)**
```bash
python governance/serve_dashboard.py
```
Then open http://localhost:8080/dashboard.html in your browser.

**Option B: Using Python's built-in server**
```bash
cd governance
python -m http.server 8080
```
Then open http://localhost:8080/dashboard.html

**Option C: Direct browser access**
Simply open `governance/dashboard.html` in your browser (some features may require a server).

## 📊 Dashboard Features

### Analytics Tab
- **MLflow Run Information**: Current run name, user, CV score, validation ROC-AUC
- **Hyperparameters**: All model hyperparameters displayed in organized cards
- **Recent Activity**: Latest audit trail events (when available)

### Model Cards Tab
- **Model Registry**: All models from MLflow with version information
- **Model Details**: Run ID, algorithm, creation date, stage, status
- **Filtering**: Filter by environment and status
- **Actions**: View detailed model information

### Audit Trail Tab
- **Event Timeline**: Complete chronological history of all governance events
- **Event Details**: User, model, action, environment, timestamps
- **Export**: Download audit log as JSON
- **Filtering**: Filter by event type and time range

### Performance Reports Tab
- **Test Metrics**: Accuracy, F1 score, ROC-AUC from actual test data
- **Cross-Validation**: CV scores from training
- **Model Configuration**: Hyperparameters visualization (n_estimators, max_depth, etc.)
- **Training Information**: Dataset sizes, features, optimization trials
- **Performance Summary**: Detailed breakdown of model performance

### Compliance Reports Tab
- **Documentation**: Model cards, schemas, API documentation
- **Security**: Container scans, dependency audits, secrets management
- **Fairness & Bias**: Assessment framework (requires running bias assessment)
- **Testing**: Unit tests, integration tests, benchmarks
- **Performance**: Metrics tracking, MLflow integration
- **Audit & Governance**: Version control, CI/CD pipeline, audit trails

## 📁 Data Sources

The dashboard loads data from:

| Data Type | Source File | Description |
|-----------|-------------|-------------|
| Test Metrics | `artifacts/metrics/test_metrics.json` | Model performance on test set |
| Train Metrics | `artifacts/metrics/train_metrics.json` | Training and validation metrics |
| MLflow Runs | `mlruns/*/meta.yaml` | Experiment tracking metadata |
| MLflow Metrics | `mlruns/*/metrics/*` | Tracked metrics from runs |
| MLflow Params | `mlruns/*/params/*` | Hyperparameters from runs |
| Model Registry | `mlruns/models/*/version-*/meta.yaml` | Registered model information |
| Audit Trail | `governance/audit_trail.jsonl` | Governance event log |
| Dashboard Data | `governance/dashboard_data.json` | Aggregated dashboard data |

## 🔄 Refreshing Data

To update the dashboard with latest data:

1. Run your MLOps pipeline to generate new metrics
2. Regenerate dashboard data:
   ```bash
   python governance/fetch_dashboard_data.py
   ```
3. Refresh your browser (the dashboard will automatically load new data)

## 📝 Generating Audit Trail Data

The audit trail will be empty until you run governance workflows. To populate it:

### Method 1: Run Model Approval
```bash
python governance/approve_model.py
```

### Method 2: Use the Governance API
```python
from governance.model_governance import ModelGovernance, ModelMetadata

governance = ModelGovernance()

# Register a model
metadata = ModelMetadata(
    model_name="water-potability-classifier",
    version="1.0.0",
    created_by="user@example.com",
    created_at="2024-10-28T00:00:00",
    commit_hash="abc123",
    branch="main",
    environment="production",
    model_type="RandomForestClassifier",
    framework="scikit-learn",
    performance_metrics={"accuracy": 0.94},
    data_schema={},
    training_data_info={},
    hyperparameters={},
    dependencies=[],
    compliance_status="COMPLIANT",
    bias_assessment={},
    approval_status="APPROVED"
)

governance.register_model(metadata)
```

### Method 3: Run Complete Governance Workflow
```bash
# Generate model card
python governance/generate_model_card.py

# Run compliance evaluation
python governance/approve_model.py
```

## 🛠️ Customization

### Adding New Metrics

Edit `governance/fetch_dashboard_data.py` to include additional data sources:

```python
def generate_dashboard_data():
    # ... existing code ...
    
    # Add your custom metrics
    custom_metrics = load_custom_metrics()
    dashboard_data['custom_metrics'] = custom_metrics
    
    return dashboard_data
```

### Styling

The dashboard uses `dashboard.css` for styling. Edit this file to customize:
- Colors
- Fonts
- Layout
- Card sizes
- Animation

## 🔍 Troubleshooting

### Dashboard shows no data
- Ensure `dashboard_data.json` exists (run `fetch_dashboard_data.py`)
- Check browser console for errors (F12)
- Verify JSON file is valid

### Models not appearing
- Check if MLflow models are registered in `mlruns/models/`
- Ensure MLflow tracking is enabled during training
- Run model registration workflow

### Audit trail empty
- Audit events are created by governance workflows
- Run `python governance/approve_model.py` to create entries
- Check if `governance/audit_trail.jsonl` exists

### CORS errors
- Use the provided HTTP server instead of direct file access
- Run `python governance/serve_dashboard.py`

## 📚 Related Files

- `dashboard.html` - Main dashboard interface
- `dashboard.css` - Dashboard styling
- `fetch_dashboard_data.py` - Data extraction script
- `serve_dashboard.py` - HTTP server for dashboard
- `model_governance.py` - Governance framework
- `generate_model_card.py` - Model card generation
- `approve_model.py` - Model approval workflow

## 🎯 Next Steps

1. **Set up automated refresh**: Create a cron job or scheduled task to run `fetch_dashboard_data.py` periodically
2. **Integrate with CI/CD**: Add dashboard data generation to your GitHub Actions workflow
3. **Enable real-time updates**: Implement WebSocket or polling for live metrics
4. **Deploy dashboard**: Host on internal server or AWS S3 for team access
5. **Add authentication**: Implement user authentication for production use

## 📞 Support

For issues or questions:
1. Check the main project README
2. Review `VISUAL_ACCESS_GUIDE.md`
3. Check MLflow UI for underlying data issues
4. Verify DVC pipeline has run successfully
