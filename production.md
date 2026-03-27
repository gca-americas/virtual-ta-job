# Virtual Technical Assistant - Production Deployment Guide

This guide is explicitly tailored for administrators standing up a brand new, pristine Google Cloud Project to launch the Virtual Technical Assistant pipeline orchestrator. 

## Prerequisites
1. A fresh Google Cloud Project configured with active billing.
2. A populated Google Cloud SQL Postgres Instance.
3. The Google Cloud CLI (`gcloud`) mapped to your terminal.

---

## Phase 1: Environment Initialization

Connect your local terminal securely directly to the new remote project parameter.

To avoid retyping your long IDs constantly, generate them locally in your bash window first! 



```bash
export PROJECT_ID=""
export REGION=""
export DB_PASSWORD=""

gcloud config set project $PROJECT_ID
gcloud auth login
```

---

## Phase 2: Deploying the Orchestration Engine

We heavily recommend deploying the core infrastructure logic completely seamlessly through **Terraform**, which guarantees all Pub/Sub Topics, Triggers, Cloud Run Jobs, and strict IAM Service Account policies configure exactly correctly.

1. Navigate to the Terraform payload directory.
```bash
cd terraform
```

2. Initialize the Hashicorp Provider engine natively.
```bash
terraform init
```

3. Deploy securely parameters globally!
```bash
terraform apply \
    -var="project_id=$PROJECT_ID" \
    -var="region=$REGION" \
    -var="github_org=gca-americas" \
    -var="db_connection_name=$PROJECT_ID:$REGION:events-db-instance" \
    -var="db_user=admin" \
    -var="db_pass=$DB_PASSWORD" \
    -var="db_name=event_db"
```

> **Note:** It creates the dedicated `virtual-ta-job-sa` Service Account tightly scoped inside Google Cloud exclusively to control your pipeline boundaries seamlessly!

---

## Phase 3: Container Execution Orchestration

Also have to agree terms and conditon for the trigger in cloud build with Github repo.

Now that the backend repositories (`virtual-ta-pipeline`) exist, you must execute the preliminary compilation explicitly so the Cloud Build YAML triggers have a base framework locally.

```bash

cd .. 

# Compile Pipeline execution optimizer explicitly 
gcloud builds submit ./builder \
    --tag=$REGION-docker.pkg.dev/$PROJECT_ID/virtual-ta-pipeline/ta-builder:latest

# Compile Cloud Run Jobs execution template natively
cd hourly
gcloud run jobs deploy hourly-job \
  --source . \
  --region $REGION \
  --project $PROJECT_ID \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --service-account="virtual-ta-job-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --max-retries 0
cd ..
```

### Complete!
Google Cloud Scheduler will naturally execute your `hourly-job` trigger every hour dynamically utilizing `virtual-ta-job-sa` perfectly! Your Web Application will securely spin up automatically whenever the Cloud SQL database registers active start dates instantly via Pub/Sub!
