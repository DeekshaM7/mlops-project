FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy minimal files
COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app and minimal artifacts (model + transformer)
COPY . /app/app
COPY ../data/processed/ /app/data/processed/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


