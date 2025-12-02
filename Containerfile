# Multi-stage Dockerfile - Unified Flask API + React Frontend
# Stage 1: Build React frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package.json ./

# Install frontend dependencies
RUN npm install

# Copy frontend source
COPY frontend/ .

# Build frontend
RUN npm run build

# Stage 2: Python + Nginx unified container
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (nginx, gcc for Python packages, supervisor)
RUN apt-get update && apt-get install -y \
    gcc \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python project files
COPY pyproject.toml .
COPY README.md .
COPY src/ src/
COPY api.py .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy built frontend from builder stage
COPY --from=frontend-builder /frontend/dist /usr/share/nginx/html

# Copy nginx configuration
COPY config/nginx.conf /etc/nginx/sites-available/default

# Create supervisor configuration
RUN mkdir -p /var/log/supervisor
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose port 80 (nginx will handle both frontend and API proxying)
EXPOSE 80

# Run supervisor to manage nginx and gunicorn
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
