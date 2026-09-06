FROM python:3.11-slim

# Prevent python from buffering stdout/stderr and creating bytecode
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATA_DIR=/app/data \
    OUTPUT_PATH=/app/output/predictions.csv

WORKDIR /app

# Install dependencies first for Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and default data
COPY . .

# Ensure output directory exists
RUN mkdir -p /app/output

# Deep health check command
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=2 \
  CMD python main.py --healthcheck || exit 1

ENTRYPOINT ["python", "main.py"]