# ─────────────────────────────────────────────────────────────────
# DDoS Attack Prediction System — Docker Container
# ─────────────────────────────────────────────────────────────────
# Packages the Flask API + trained model into a portable container.
# Same image runs on your laptop, AWS, GCP, or any cloud platform.
#
# Build:   docker build -t ddos-predictor .
# Run:     docker run -p 5000:5000 ddos-predictor
# Test:    curl http://localhost:5000/health
# ─────────────────────────────────────────────────────────────────

# Start from official Python 3.11 slim image (small, secure base)
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (Docker caches this layer — speeds up rebuilds)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project into the container
COPY app.py .
COPY models/ ./models/

# Expose port 5000 so the host machine can reach the API
EXPOSE 5000

# Health check — Docker will ping this every 30s to confirm the app is alive
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Start the Flask API when the container launches
CMD ["python", "app.py"]
