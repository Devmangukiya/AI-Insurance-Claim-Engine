## Parent image
FROM python:3.10-slim

## Essential environment variables for Python in Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

## Set the working directory inside the container
WORKDIR /app

## Install system dependencies required for building some Python packages
# This layer is cached and will rarely change.
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

## --- Caching Optimization for Faster Builds ---

## 1. Copy the requirements file first
# This allows Docker to cache the dependency installation layer.
COPY requirements.txt ./

## 2. Install third-party Python dependencies
# This is the most time-consuming step. It will only re-run if you
# modify requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

## 3. Copy the rest of your project source code
# This includes your 'app' directory, setup.py, and other files.
COPY . .

## 4. Install your own application as an editable package
# This step is very fast because all dependencies are already installed.
# It uses your setup.py to make your application code importable.
RUN pip install --no-cache-dir -e .

## --- End of Optimization ---

## Expose the port your Flask application runs on
EXPOSE 5000

## Command to run your application
CMD ["python", "app/application.py"]
