SHELL := powershell.exe

.PHONY: venv install fmt lint test dvc-init repro run-api docker-build docker-run

venv:
	python -m venv .venv; .\.venv\Scripts\Activate.ps1; python -m pip install --upgrade pip

install:
	.\.venv\Scripts\Activate.ps1; pip install -r requirements.txt

fmt:
	.\.venv\Scripts\Activate.ps1; ruff format src app tests

lint:
	.\.venv\Scripts\Activate.ps1; ruff check src app tests

test:
	.\.venv\Scripts\Activate.ps1; pytest -q

dvc-init:
	dvc init -q

repro:
	dvc repro -q

run-api:
	.\.venv\Scripts\Activate.ps1; python -m flask --app app.main run --host=0.0.0.0 --port=8000

docker-build:
	docker build -t water-quality-api -f app/Dockerfile .

docker-run:
	docker run -p 8000:8000 water-quality-api


