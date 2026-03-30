# Use the official lightweight Python image.
FROM python:3.11-slim

# Generative AI Agent implicitly requires OS-level Git dependencies for GitPython context extraction
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install isolated Agent dependencies physically.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy internal python orchestrator modules.
COPY . .

# Instruct the runtime to natively fire the Evaluator logic.
ENTRYPOINT ["python", "-u", "main.py"]
