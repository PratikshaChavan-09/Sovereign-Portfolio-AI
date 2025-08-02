FROM python:3.12.6-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# FORCE REINSTALL google-generativeai to ensure it's available at runtime
RUN pip install --force-reinstall --no-cache-dir google-generativeai==0.8.4

# Quick verification
RUN python -c "import google.generativeai as genai; print('✅ google-generativeai OK')"

# Copy application code
COPY . .

# Set Python path
ENV PYTHONPATH=/app:/app/backend:/app/frontend

# Expose port
EXPOSE 8501

# Run with verification
CMD python -c "import google.generativeai; print('Runtime check: Gemini OK')" && \
    streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0