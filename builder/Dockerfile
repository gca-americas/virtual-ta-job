# Use the official Google Cloud SDK image
FROM gcr.io/google.com/cloudsdktool/cloud-sdk:latest

# Install base packages required
RUN apt-get update && \
    apt-get install -y python3-pip jq git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install the required Python packages globally natively
RUN pip3 install --break-system-packages pg8000 google-cloud-secret-manager "cloud-sql-python-connector[pg8000]" python-dotenv
