FROM python:3.11-slim

# Install OS-level build dependencies in a single layer, then clean up
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies before copying application code so that Docker
# can cache this layer and avoid re-installing packages on every code change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Run as a non-root user for improved security
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 5000

# Use gunicorn for a production-grade WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]