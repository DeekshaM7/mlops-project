FROM python:3.12.4

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy files from repo root (build with context = repo root)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application and precomputed artifacts (expect build from repo root)
COPY app /app/app
COPY data/processed /app/data/processed

EXPOSE 8000
ENV FLASK_APP=app.main
ENV PYTHONUNBUFFERED=1

# Use Flask's built-in server for development inside the container.
# For production replace this with a proper WSGI server (gunicorn/uvicorn+ASGI) and workers.
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]


