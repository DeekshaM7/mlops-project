# 🚀 Water Potability Classification - Complete MLOps Pipeline

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MLflow](https://img.shields.io/badge/MLflow-2.8.0+-blue.svg)](https://mlflow.org/)
[![DVC](https://img.shields.io/badge/DVC-3.30.0+-orange.svg)](https://dvc.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-S3%20%7C%20EC2%20%7C%20ECR-orange.svg)](https://aws.amazon.com/)

A **production-ready MLOps pipeline** implementing **Level 4 CI/CD automation** with comprehensive governance, monitoring, and zero-downtime deployment for water quality classification. This project demonstrates enterprise-grade machine learning operations practices aligned with **UN SDG 6 (Clean Water)** and **SDG 12 (Responsible Production)**.

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🏗️ Architecture](#️-architecture)
- [✨ Key Features](#-key-features)
- [📊 Model Performance](#-model-performance)
- [🚀 Quick Start](#-quick-start)
- [🔄 Pipeline Components](#-pipeline-components)
- [📁 Project Structure](#-project-structure)
- [⚖️ Model Governance](#️-model-governance)
- [📈 Monitoring & Observability](#-monitoring--observability)
- [🚢 Deployment Strategy](#-deployment-strategy)
- [📊 Governance Dashboard](#-governance-dashboard)
- [🧪 Testing](#-testing)
- [🔒 Security](#-security)
- [🛠️ Configuration](#️-configuration)
- [📚 API Documentation](#-api-documentation)
- [🔧 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)

---

## 🎯 Overview

This project implements a **complete MLOps solution** for predicting water potability using machine learning, featuring:

- **🔄 Level 4 CI/CD**: Fully automated pipeline from code commit to production deployment
- **📦 Data Versioning**: DVC integration with AWS S3 for reproducible experiments
- **🔬 Experiment Tracking**: MLflow for comprehensive model lifecycle management
- **🐳 Containerization**: Multi-stage Docker builds optimized for production
- **☁️ Cloud Infrastructure**: AWS EC2, S3, ECR, and CloudWatch integration
- **⚖️ Model Governance**: Comprehensive framework for responsible AI deployment
- **🛡️ Security**: Container scanning, vulnerability assessment, and secrets management
- **📊 Monitoring**: Real-time dashboards, alerts, and performance tracking
- **🚢 Zero-Downtime Deployment**: Blue-green deployment with automatic rollback

### 🌍 Sustainability Impact

This pipeline supports:
- **UN SDG 6 (Clean Water & Sanitation)**: Early detection of water quality issues
- **UN SDG 12 (Responsible Consumption)**: Efficient resource utilization and reproducible science
- **Edge Deployment**: Optimized for resource-constrained environments

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MLOPS PIPELINE ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   DATA LAYER    │      │   ML PLATFORM   │      │  APPLICATION    │
│                 │      │                 │      │                 │
│ • AWS S3        │ ───▶ │ • MLflow Server │ ───▶ │ • Flask API     │
│ • DVC Control   │      │ • Model Registry│      │ • Docker        │
│ • Data Pipeline │      │ • Experiments   │      │ • Load Balancer │
│ • Preprocessing │      │ • Artifacts     │      │ • Health Checks │
└─────────────────┘      └─────────────────┘      └─────────────────┘
         │                       │                         │
         └───────────────────────┼─────────────────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │   OPERATIONS & GOVERNANCE  │
                    │                            │
                    │ • GitHub Actions (6-stage) │
                    │ • CloudWatch Monitoring    │
                    │ • Model Governance         │
                    │ • Audit Trail             │
                    │ • Compliance Framework     │
                    │ • Blue-Green Deployment   │
                    └────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          CI/CD PIPELINE (6 STAGES)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. CODE QUALITY     →  2. DATA VALIDATION  →  3. CONTAINER BUILD           │
│     • Linting            • DVC Pipeline         • Multi-stage Docker        │
│     • Testing            • Data Validation      • Security Scanning         │
│     • Security Scan      • Model Training       • Push to ECR               │
│                          • MLflow Tracking                                   │
│                                                                              │
│  4. STAGING DEPLOY   →  5. PRODUCTION DEPLOY → 6. GOVERNANCE                │
│     • EC2 Deployment     • Blue-Green Deploy   • Model Cards                │
│     • Smoke Tests        • Health Checks       • Audit Trail                │
│     • Monitoring         • Load Balancing      • Compliance Report          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Category | Technologies |
|----------|-------------|
| **ML Framework** | scikit-learn, Optuna |
| **Tracking** | MLflow, DVC |
| **API** | Flask, Python 3.11+ |
| **Containerization** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |
| **Cloud** | AWS (S3, EC2, ECR, CloudWatch) |
| **Monitoring** | CloudWatch, Custom Metrics |
| **Security** | Trivy, Bandit, Safety |
| **Governance** | Custom Framework |

---

## ✨ Key Features

### 🔄 Complete CI/CD Automation
- ✅ **6-Stage Pipeline**: Code quality → Data validation → Container build → Staging → Production → Governance
- ✅ **Automated Testing**: Unit, integration, and smoke tests
- ✅ **Security Scanning**: Container vulnerabilities (Trivy), code security (Bandit), dependency checks (Safety)
- ✅ **Quality Gates**: Automated quality checks prevent bad code from reaching production
- ✅ **Multi-Environment**: Development, staging, and production environments

### 📦 Data & Model Management
- ✅ **DVC Integration**: Version control for datasets and models with S3 backend
- ✅ **MLflow Tracking**: Comprehensive experiment tracking and model registry
- ✅ **Reproducibility**: Complete lineage tracking from data to deployment
- ✅ **Model Versioning**: Automatic versioning with metadata and performance metrics

### ⚖️ Model Governance Framework
- ✅ **Audit Trails**: Complete logging of all model operations
- ✅ **Compliance Engine**: Automated rule-based compliance checking
- ✅ **Bias Assessment**: Statistical fairness metrics evaluation
- ✅ **Model Cards**: Automated documentation generation
- ✅ **Approval Workflows**: Multi-stage approval process with governance checks

### 📊 Monitoring & Observability
- ✅ **Real-time Dashboards**: CloudWatch integration with custom metrics
- ✅ **Performance Tracking**: Model drift detection and performance monitoring
- ✅ **Log Aggregation**: Centralized logging with retention policies
- ✅ **Alert System**: SNS notifications for critical events
- ✅ **Health Checks**: Automated health monitoring and recovery

### 🚢 Production Deployment
- ✅ **Zero-Downtime**: Blue-green deployment strategy
- ✅ **Automatic Rollback**: Health check failures trigger automatic rollback
- ✅ **Load Balancing**: Nginx-based load distribution
- ✅ **Scalability**: Horizontal scaling support
- ✅ **Security**: Non-root containers, secrets management

---

## 📊 Model Performance

### Current Production Model Metrics

| Metric | Value | Benchmark |
|--------|-------|-----------|
| **Test Accuracy** | 65.55% | Baseline: 60% |
| **F1 Score** | 0.4322 | Balanced performance |
| **ROC-AUC** | 0.6681 | Good discrimination |
| **CV Score** | 0.6796 | 5-fold cross-validation |
| **Val ROC-AUC** | 1.0 | Validation performance |
| **Response Time** | < 100ms | Production SLA |

### Model Configuration

```python
Model: RandomForestClassifier
Hyperparameters:
  - n_estimators: 288
  - max_depth: 27
  - min_samples_split: 7
  - min_samples_leaf: 1
  - cv_folds: 5
  - optimization_trials: 20

Training Data:
  - Total samples: 2,620
  - Training: 2,292 samples
  - Validation: 328 samples
  - Features: 9 water quality parameters
```

### Features

1. **pH**: Acidity/alkalinity level
2. **Hardness**: Calcium and magnesium content
3. **Solids**: Total dissolved solids
4. **Chloramines**: Disinfectant levels
5. **Sulfate**: Sulfate ion concentration
6. **Conductivity**: Electrical conductivity
7. **Organic Carbon**: Organic carbon content
8. **Trihalomethanes**: Disinfection by-products
9. **Turbidity**: Cloudiness measure

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required Software
- Python 3.11 or higher
- Docker 20.10+
- Git
- AWS CLI (configured)
- Make (optional)

# AWS Services (if deploying to cloud)
- S3 bucket for data storage
- ECR repository for Docker images
- EC2 instances for deployment
- CloudWatch for monitoring
```

### Installation Steps

#### 1. Clone Repository

```bash
git clone https://github.com/DeekshaM7/mlops-project.git
cd mlops-project
```

#### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Configure AWS & DVC

```bash
# Configure AWS credentials
aws configure

# Set up DVC remote (replace with your bucket)
dvc init
dvc remote add -d origin s3://your-dvc-bucket-name/data
dvc remote modify origin region us-east-1

# Pull data
dvc pull
```

#### 4. Run ML Pipeline

```bash
# Run complete DVC pipeline
dvc repro

# This will execute:
# 1. Data ingestion
# 2. Data preprocessing
# 3. Model training with Optuna
# 4. Model evaluation
```

#### 5. Start MLflow Server (Optional)

```bash
# Local MLflow server
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --host 0.0.0.0 --port 5000

# Access MLflow UI: http://localhost:5000
```

#### 6. Run Flask Application

```bash
# Start API server
python app/main.py

# API will be available at: http://localhost:5000
# Frontend at: http://localhost:5000/frontend
```

#### 7. Test API

```powershell
# Health check
curl http://localhost:5000/health

# Make prediction (PowerShell)
$body = @{
    ph = 7.2
    Hardness = 180.5
    Solids = 15000.0
    Chloramines = 7.8
    Sulfate = 250.0
    Conductivity = 400.0
    Organic_carbon = 12.5
    Trihalomethanes = 65.0
    Turbidity = 3.5
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:5000/predict" -Body $body -ContentType "application/json"
```

#### 8. Run with Docker

```bash
# Build production image
docker build -f docker/Dockerfile.prod -t water-quality-ml:latest .

# Run container
docker run -d -p 5000:5000 --name water-quality-api water-quality-ml:latest

# Check logs
docker logs water-quality-api
```

---

## 🔄 Pipeline Components

### DVC Pipeline Stages

The data pipeline is defined in `dvc.yaml` and consists of four stages:

#### 1. **Data Ingestion**
```bash
python -m src.data.ingest --input data/raw/water_potability.csv --output data/processed/water_potability.csv
```
- Loads raw data
- Basic validation
- Outputs clean dataset

#### 2. **Data Preprocessing**
```bash
python -m src.data.preprocess --params configs/params.yaml
```
- Handles missing values
- Feature engineering
- Train/validation/test split
- Saves preprocessing transformer
- Outputs: `train.csv`, `val.csv`, `test.csv`, `transformer.joblib`

#### 3. **Model Training**
```bash
python -m src.models.train --params configs/params.yaml
```
- Hyperparameter optimization with Optuna
- Cross-validation
- MLflow experiment tracking
- Saves best model
- Outputs: `model.joblib`, `train_metrics.json`

#### 4. **Model Evaluation**
```bash
python -m src.models.evaluate --params configs/params.yaml
```
- Test set evaluation
- Performance metrics calculation
- Visualization generation
- Outputs: `test_metrics.json`, plots

### GitHub Actions Workflow

The CI/CD pipeline (`complete-mlops-pipeline.yml`) has 6 stages:

#### **Stage 1: Code Quality & Unit Tests**
- Code formatting check (ruff)
- Linting and static analysis
- Security scanning (Bandit, Safety)
- Unit tests with coverage
- Upload test results

#### **Stage 2: Data Pipeline & Model Training**
- Setup AWS credentials
- Configure DVC with S3
- Pull latest data
- Data validation
- Run ML pipeline with MLflow
- Model validation & benchmarking
- Push artifacts to S3

#### **Stage 3: Container Build & Security Scan**
- Download model artifacts
- Build multi-stage Docker image
- Container security scan (Trivy)
- Integration tests
- Push to Amazon ECR

#### **Stage 4: Deploy to Staging**
- Deploy to staging EC2
- Run smoke tests
- Setup CloudWatch monitoring
- Verify deployment health

#### **Stage 5: Production Deployment** (Manual Approval Required)
- Blue-green deployment
- Health checks
- Load balancer update
- Production monitoring setup

#### **Stage 6: Model Governance & Audit**
- Generate model card
- Update model registry
- Bias and fairness evaluation
- Compliance report generation
- Audit trail logging

---

## 📁 Project Structure

```
mlops-project/
├── .github/
│   └── workflows/
│       ├── complete-mlops-pipeline.yml    # Main CI/CD pipeline
│       └── ci.yml                          # Basic CI workflow
├── app/
│   ├── main.py                             # Flask API application
│   ├── frontend.html                       # Web UI
│   ├── Dockerfile                          # Development Dockerfile
│   └── model_registry/
│       └── model.joblib                    # Latest trained model
├── artifacts/
│   ├── metrics/
│   │   ├── train_metrics.json             # Training metrics
│   │   └── test_metrics.json              # Test metrics
│   └── plots/                              # Visualizations
├── configs/
│   └── params.yaml                         # Hyperparameters and config
├── data/
│   ├── raw/
│   │   ├── water_potability.csv           # Raw dataset
│   │   └── water_potability.csv.dvc       # DVC tracking file
│   └── processed/
│       ├── train.csv                       # Training data
│       ├── val.csv                         # Validation data
│       ├── test.csv                        # Test data
│       ├── transformer.joblib              # Preprocessing pipeline
│       └── water_potability.csv            # Processed dataset
├── docker/
│   └── Dockerfile.prod                     # Production multi-stage build
├── governance/
│   ├── model_governance.py                 # Governance framework
│   ├── generate_model_card.py              # Model card generator
│   ├── approve_model.py                    # Approval workflow
│   ├── fetch_dashboard_data.py             # Dashboard data extractor
│   ├── serve_dashboard.py                  # Dashboard HTTP server
│   ├── dashboard.html                      # Governance dashboard UI
│   ├── dashboard.css                       # Dashboard styling
│   └── README.md                           # Governance documentation
├── infrastructure/
│   ├── setup-aws.sh                        # AWS infrastructure setup
│   ├── setup-ec2.sh                        # EC2 instance setup
│   ├── setup-monitoring.sh                 # Monitoring setup
│   ├── monitoring.yaml                     # CloudWatch config
│   └── docker-compose.mlflow.yml           # MLflow server setup
├── mlruns/                                 # MLflow experiments directory
├── poster/
│   ├── mlops_pipeline_poster.html          # Academic poster
│   └── pipeline_diagram.html               # Pipeline visualization
├── scripts/
│   ├── blue-green-deploy.sh                # Blue-green deployment
│   └── deploy.sh                           # General deployment script
├── src/
│   ├── data/
│   │   ├── ingest.py                       # Data ingestion
│   │   └── preprocess.py                   # Data preprocessing
│   ├── models/
│   │   ├── train.py                        # Model training
│   │   └── evaluate.py                     # Model evaluation
│   └── utils/
│       └── io.py                           # I/O utilities
├── tests/
│   ├── test_preprocess.py                  # Preprocessing tests
│   └── test_train.py                       # Training tests
├── dvc.yaml                                # DVC pipeline definition
├── dvc.lock                                # DVC pipeline lock file
├── requirements.txt                        # Python dependencies
├── Makefile                                # Automation commands
└── README.md                               # This file
```

---

## ⚖️ Model Governance

### Governance Framework

The project includes a comprehensive governance system for responsible AI deployment:

#### Key Components

1. **Model Registration**
   - Centralized metadata management
   - Version control and lineage tracking
   - Performance metrics logging

2. **Audit Trails**
   - Complete lifecycle event logging
   - User action tracking
   - Timestamp and environment metadata

3. **Compliance Engine**
   - Rule-based compliance checking
   - Automated evaluation
   - Threshold enforcement

4. **Bias Assessment**
   - Statistical fairness metrics
   - Protected attribute analysis
   - Bias mitigation recommendations

5. **Model Cards**
   - Automated documentation
   - Intended use and limitations
   - Performance characteristics

### Using the Governance Framework

#### Register a Model

```python
from governance.model_governance import ModelGovernance, ModelMetadata

governance = ModelGovernance()

metadata = ModelMetadata(
    model_name="water-potability-classifier",
    version="1.0.0",
    created_by="data-scientist@company.com",
    created_at="2024-10-28T00:00:00",
    commit_hash="abc123def",
    branch="main",
    environment="production",
    model_type="RandomForestClassifier",
    framework="scikit-learn 1.3.0",
    performance_metrics={
        "accuracy": 0.6555,
        "f1": 0.4322,
        "roc_auc": 0.6681
    },
    data_schema={"features": 9},
    training_data_info={"samples": 2620},
    hyperparameters={
        "n_estimators": 288,
        "max_depth": 27
    },
    dependencies=["scikit-learn==1.3.0", "pandas==2.0.3"],
    compliance_status="PENDING",
    bias_assessment={},
    approval_status="PENDING"
)

governance.register_model(metadata)
```

#### Generate Model Card

```bash
python governance/generate_model_card.py --model-name water-potability-classifier --version 1.0.0 --commit-hash abc123
```

#### Approve Model for Production

```bash
python governance/approve_model.py --model-name water-potability-classifier --version 1.0.0 --approver john.doe@company.com --min-accuracy 0.60 --notes "Approved after successful staging tests"
```

---

## 📈 Monitoring & Observability

### CloudWatch Integration

The pipeline automatically sets up CloudWatch dashboards with:

- **Application Metrics**: Request count, response time, error rates
- **Model Metrics**: Prediction confidence, input distribution
- **Infrastructure Metrics**: CPU, memory, disk utilization
- **Custom Metrics**: Model drift, data quality issues

### Alarms

Automated alerts for:
- High error rates (>5%)
- Slow response times (>500ms)
- Resource utilization (>80%)
- Model drift detected
- Compliance violations

### Setup Monitoring

```bash
# Deploy CloudWatch infrastructure (Linux/Mac)
./infrastructure/setup-monitoring.sh --environment production --region us-east-1 --notification-email your-email@example.com

# Or use CloudFormation directly
aws cloudformation deploy --template-file infrastructure/monitoring.yaml --stack-name mlops-monitoring-production --parameter-overrides Environment=production ApplicationName=water-quality-ml NotificationEmail=your-email@example.com
```

---

## 🚢 Deployment Strategy

### Blue-Green Deployment

Zero-downtime deployment with automatic rollback:

```bash
# Deploy new version (Linux/Mac)
./scripts/blue-green-deploy.sh --image-uri 123456789012.dkr.ecr.us-east-1.amazonaws.com/water-quality-ml:v1.2.0

# The script will:
# 1. Pull new Docker image
# 2. Start new environment (green)
# 3. Run health checks
# 4. Update load balancer
# 5. Stop old environment (blue)
# 6. Rollback on failure
```

### Environment Management

#### Local Development
```bash
# Start development server
python app/main.py

# Run with Docker
docker-compose up -d
```

#### Staging Environment
```bash
# Deploy to staging
./scripts/deploy.sh staging $IMAGE_URI

# Run smoke tests
python tests/smoke/test_staging.py --base-url $STAGING_URL
```

#### Production Environment
```bash
# Requires manual approval in GitHub Actions
# Automated deployment after approval

# Manual deployment
./scripts/blue-green-deploy.sh $IMAGE_URI
```

---

## 📊 Governance Dashboard

### Quick Start

```bash
# 1. Generate dashboard data
python governance/fetch_dashboard_data.py

# 2. Start dashboard server
python governance/serve_dashboard.py

# 3. Open in browser
# http://localhost:8080/dashboard.html
```

### Dashboard Features

#### 📈 Analytics Tab
- MLflow run information (run name, user, CV score)
- Complete hyperparameters visualization
- Recent audit events timeline

#### 📦 Model Cards Tab
- All registered models from MLflow
- Model metadata and status
- Filter by environment and status
- Version history

#### 📋 Audit Trail Tab
- Chronological event timeline
- User actions and timestamps
- Export to JSON functionality
- Filter by event type and date range

#### 📊 Performance Reports Tab
- Test metrics (accuracy, F1, ROC-AUC)
- Cross-validation scores
- Model configuration visualization
- Training dataset information
- Performance trends

#### ✅ Compliance Reports Tab
- Documentation checklist
- Security framework status
- Testing coverage
- Governance tool integration
- Compliance score

### Data Sources

| Data Source | File Location | Description |
|------------|---------------|-------------|
| Test Metrics | `artifacts/metrics/test_metrics.json` | Model performance on test set |
| Train Metrics | `artifacts/metrics/train_metrics.json` | Training and validation metrics |
| MLflow Runs | `mlruns/*/meta.yaml` | Experiment metadata |
| MLflow Metrics | `mlruns/*/metrics/*` | Tracked metrics |
| MLflow Params | `mlruns/*/params/*` | Hyperparameters |
| Model Registry | `mlruns/models/*/version-*/meta.yaml` | Registered models |
| Audit Trail | `governance/audit_trail.jsonl` | Governance events |

---

## 🧪 Testing

### Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_preprocess.py -v

# Run with coverage
pytest --cov=src --cov=app --cov-report=html --cov-report=term

# View coverage report
start htmlcov/index.html  # Windows PowerShell
```

---

## 🔒 Security

### Security Features

✅ **Container Security**
- Trivy scanning for vulnerabilities
- Non-root user execution
- Minimal base images (distroless)
- No secrets in images

✅ **Code Security**
- Bandit static analysis
- Safety dependency checking
- Secrets scanning in CI/CD
- HTTPS enforcement

✅ **AWS Security**
- IAM roles with least privilege
- Encrypted S3 buckets
- VPC isolation
- Security groups configuration

✅ **API Security**
- CORS configuration
- Rate limiting (production)
- Input validation
- Error handling

---

## 🛠️ Configuration

### Environment Variables

Create a `.env` file or export these variables:

```powershell
# AWS Configuration
$env:AWS_REGION="us-east-1"
$env:AWS_ACCOUNT_ID="123456789012"
$env:S3_BUCKET_NAME="your-dvc-bucket"
$env:ECR_REPOSITORY="water-quality-ml"

# MLflow Configuration
$env:MLFLOW_TRACKING_URI="http://localhost:5000"
$env:MLFLOW_EXPERIMENT_NAME="water-potability-classifier"

# Application Configuration
$env:FLASK_ENV="production"
$env:HOST="0.0.0.0"
$env:PORT="5000"
```

### DVC Configuration

```bash
# Configure S3 remote
dvc remote add -d origin s3://your-bucket/data
dvc remote modify origin region us-east-1

# With credentials
dvc remote modify origin access_key_id YOUR_ACCESS_KEY
dvc remote modify origin secret_access_key YOUR_SECRET_KEY

# Or use IAM role
dvc remote modify origin profile default
```

### Parameters (`configs/params.yaml`)

```yaml
data:
  test_size: 0.2
  val_size: 0.1
  random_state: 42

preprocessing:
  imputation_strategy: 'median'
  scaling_method: 'standard'

training:
  n_trials: 20
  cv_folds: 5
  random_state: 42
  
  param_space:
    n_estimators: [50, 300]
    max_depth: [5, 30]
    min_samples_split: [2, 10]
    min_samples_leaf: [1, 5]

evaluation:
  metrics:
    - accuracy
    - precision
    - recall
    - f1
    - roc_auc
```

---

## 📚 API Documentation

### Base URL

- **Local**: `http://localhost:5000`
- **Staging**: `http://your-staging-url`
- **Production**: `http://your-production-url`

### Endpoints

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

#### Root

```http
GET /
```

**Response:**
```json
{
  "status": "ok",
  "message": "Water Quality Potability API"
}
```

#### Frontend

```http
GET /frontend
```

Returns the HTML interface for making predictions.

#### Predict

```http
POST /predict
Content-Type: application/json
```

**Request Body (Single Prediction):**
```json
{
  "ph": 7.2,
  "Hardness": 180.5,
  "Solids": 15000.0,
  "Chloramines": 7.8,
  "Sulfate": 250.0,
  "Conductivity": 400.0,
  "Organic_carbon": 12.5,
  "Trihalomethanes": 65.0,
  "Turbidity": 3.5
}
```

**Response:**
```json
{
  "predictions": [1],
  "probabilities": [[0.35, 0.65]],
  "message": "Predictions generated successfully"
}
```

### Example Usage

#### PowerShell
```powershell
$body = @{
    ph = 7.2
    Hardness = 180.5
    Solids = 15000.0
    Chloramines = 7.8
    Sulfate = 250.0
    Conductivity = 400.0
    Organic_carbon = 12.5
    Trihalomethanes = 65.0
    Turbidity = 3.5
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:5000/predict" -Body $body -ContentType "application/json"
```

---

## 🔧 Troubleshooting

### Common Issues

#### DVC Issues

**Problem:** `dvc pull` fails with authentication error

```powershell
# Solution 1: Configure AWS credentials
aws configure

# Solution 2: Set DVC remote credentials
dvc remote modify origin access_key_id YOUR_KEY
dvc remote modify origin secret_access_key YOUR_SECRET

# Solution 3: Use IAM role
dvc remote modify origin profile default
```

**Problem:** DVC cache corruption

```powershell
# Clear cache and re-pull
Remove-Item -Recurse -Force .dvc/cache
dvc pull
```

#### MLflow Issues

**Problem:** Cannot connect to MLflow tracking server

```powershell
# Check MLflow server is running
curl http://localhost:5000

# Verify environment variable
echo $env:MLFLOW_TRACKING_URI

# Restart MLflow server
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --host 0.0.0.0 --port 5000
```

#### Docker Issues

**Problem:** Container fails to start

```powershell
# Check logs
docker logs water-quality-api

# Debug interactively
docker run -it --entrypoint /bin/bash water-quality-ml
```

#### Dashboard Issues

**Problem:** CORS errors when loading dashboard

```powershell
# Use HTTP server instead of opening file directly
python governance/serve_dashboard.py

# Then access at http://localhost:8080/dashboard.html
```

**Problem:** No data showing in dashboard

```powershell
# Regenerate dashboard data
python governance/fetch_dashboard_data.py

# Verify JSON file
Get-Content governance/dashboard_data.json
```

---

## 🤝 Contributing

### Development Workflow

1. **Fork & Clone**
   ```bash
   git clone https://github.com/your-username/mlops-project.git
   cd mlops-project
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Changes**
   - Follow PEP 8 style guidelines
   - Write comprehensive tests
   - Update documentation
   - Ensure all tests pass

4. **Test Changes**
   ```bash
   pytest tests/ -v
   ```

5. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   git push origin feature/amazing-feature
   ```

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **UN Sustainable Development Goals**: Inspired by SDG 6 and SDG 12
- **Open Source Community**: For amazing tools and frameworks
- **Contributors**: Thank you to all contributors

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/DeekshaM7/mlops-project/issues)
- **Documentation**: Check `/governance/README.md` for governance details
- **Academic Poster**: View `poster/mlops_pipeline_poster.html`
- **Pipeline Diagram**: View `poster/pipeline_diagram.html`

---

## 🎯 Project Status

- ✅ **Level 4 CI/CD**: Fully implemented
- ✅ **Model Governance**: Comprehensive framework
- ✅ **Zero-Downtime Deployment**: Blue-green strategy
- ✅ **Monitoring**: CloudWatch integration
- ✅ **Security**: Container scanning and secrets management
- ✅ **Documentation**: Complete and up-to-date
- ✅ **Production-Ready**: Deployed and tested

---

**Built with ❤️ using modern MLOps practices and cloud-native technologies.**

*Last Updated: October 29, 2025*
