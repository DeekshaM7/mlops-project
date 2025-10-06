Sustainable Water Quality Anomaly Detection MLOps Pipeline

Overview
- End-to-end MLOps pipeline on the Water Potability dataset: ingestion, preprocessing, training, evaluation, packaging, CI/CD, and containerized inference.

Quickstart
1. Create virtual environment and install deps:
   - Windows PowerShell:
     - `python -m venv .venv`
     - `.venv\\Scripts\\Activate.ps1`
     - `pip install -r requirements.txt`
2. Initialize Git and DVC:
   - `git init`
   - `dvc init`
3. Track data and run pipeline:
   - `dvc add data/raw/water_potability.csv`
   - `dvc repro`

Project Structure
```
data/
  raw/              # original csv (DVC-tracked)
  processed/        # cleaned feature sets
notebooks/
  eda.ipynb         # EDA and visualizations
src/
  data/
    ingest.py
    preprocess.py
  models/
    train.py
    evaluate.py
    infer.py
  utils/
    io.py
    metrics.py
configs/
  params.yaml
  logging.yaml
app/
  main.py           # FastAPI inference app
  schemas.py
  model_registry/
    model.joblib    # latest trained model
  Dockerfile
ci/
  github/
    workflows/
      ci.yml
tests/
  test_preprocess.py
  test_train.py
Makefile
requirements.txt
dvc.yaml
.gitignore
.dvcignore
README.md
```

Sustainability Notes
- Aligns with SDG 6 (Clean Water) and SDG 12 (Responsible Consumption & Production) by enabling early anomaly detection, reproducible science, and resource-efficient deployment on edge devices.


