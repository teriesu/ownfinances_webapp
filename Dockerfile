FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Generate and set locale
RUN sed -i '/es_CO.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen es_CO.UTF-8
ENV LANG es_CO.UTF-8
ENV LC_ALL es_CO.UTF-8

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Default command (can be overridden in docker-compose)
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
