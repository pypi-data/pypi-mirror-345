# Command Registry Deployment Guide

This guide describes approaches and recommendations for deploying applications using Command Registry in various environments.

## Contents

- [Deployment Preparation](#deployment-preparation)
- [Docker Deployment](#docker-deployment)
- [VPS Deployment](#vps-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD for Command Registry](#cicd-for-command-registry)
- [Monitoring and Logging](#monitoring-and-logging)
- [Scaling](#scaling)
- [Security](#security)
- [Hybrid Schema and MCPProxy Integration](#hybrid-schema-and-mcpproxy-integration)

## Deployment Preparation

### 1. Creating Application Package

It is recommended to package your application as a Python package for convenient deployment:

```
my_app/
  ├── pyproject.toml
  ├── setup.py
  ├── setup.cfg
  ├── README.md
  ├── src/
  │   └── my_app/
  │       ├── __init__.py
  │       ├── commands/
  │       │   ├── __init__.py
  │       │   └── ...
  │       ├── app.py
  │       └── main.py
  └── tests/
      └── ...
```

Example `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-app"
version = "0.1.0"
description = "Command Registry Application"
authors = [{name = "Your Name", email = "your.email@example.com"}]
requires-python = ">=3.8"
dependencies = [
    "command-registry>=0.1.0",
    "fastapi>=0.68.0",
    "uvicorn>=0.15.0",
]
```

### 2. Configuration Setup

Create a configuration system that supports different environments:

```python
# src/my_app/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    APP_NAME: str = "Command Registry App"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_PORT: int = 8000
    
    # Command Registry settings
    STRICT_MODE: bool = True
    AUTO_FIX: bool = False
    
    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = "app_db"
    
    class Config:
        env_file = ".env"
        env_prefix = "APP_"

# Load settings
settings = Settings()
```

### 3. Creating Entry Point

```python
# src/my_app/main.py
import uvicorn
from my_app.app import app
from my_app.config import settings

def start():
    """Starts the application."""
    uvicorn.run(
        "my_app.app:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )

if __name__ == "__main__":
    start()
```

## Docker Deployment

### 1. Creating Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml setup.py setup.cfg ./

# Install dependencies
RUN pip install --no-cache-dir .

# Copy application code
COPY src/ ./src/

# Define environment variables
ENV APP_DEBUG=false \
    APP_LOG_LEVEL=INFO \
    APP_API_PORT=8000 \
    APP_STRICT_MODE=true \
    APP_AUTO_FIX=false

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "-m", "my_app.main"]
```

### 2. Docker Compose for Local Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_DEBUG=true
      - APP_LOG_LEVEL=DEBUG
      - APP_DB_HOST=db
    depends_on:
      - db
    volumes:
      - ./src:/app/src
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=app_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### 3. Build and Run

```bash
# Build image
docker build -t my-app .

# Run container
docker run -p 8000:8000 my-app

# Or using Docker Compose
docker-compose up
```

## VPS Deployment

### 1. Installing Dependencies on Server

```bash
# Update packages
sudo apt update
sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv

# Install Nginx
sudo apt install -y nginx

# Install Supervisor
sudo apt install -y supervisor
```

### 2. Gunicorn Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install application and Gunicorn
pip install gunicorn
pip install .  # install your application
```

### 3. Supervisor Configuration

```ini
# /etc/supervisor/conf.d/my-app.conf
[program:my-app]
command=/home/user/my-app/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker my_app.app:app -b 127.0.0.1:8000
directory=/home/user/my-app
user=user
autostart=true
autorestart=true
environment=APP_DEBUG=false,APP_LOG_LEVEL=INFO,APP_STRICT_MODE=true

[supervisord]
logfile=/var/log/supervisor/supervisord.log
```

### 4. Nginx Configuration

```nginx
# /etc/nginx/sites-available/my-app
server {
    listen 80;
``` 