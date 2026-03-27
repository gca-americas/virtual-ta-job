# Use the official lightweight Python image.
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

WORKDIR /app

# Install dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image.
COPY . .

# Run the hourly script natively
ENTRYPOINT ["python", "hourly_job.py"]
