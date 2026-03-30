# Workshop TA Job - Setup Instructions

## 1. Create Pub/Sub Topics

```bash
export PROJECT_ID=""
gcloud config set project $PROJECT_ID

gcloud pubsub topics create deploy_queue
gcloud pubsub topics create demolish_queue

## 2. Create Database Credentials Secret

To store the database credentials securely, we'll create a Secret Manager payload that the Cloud Build jobs will ingest natively during execution.

```bash
cat << 'EOF' > /tmp/secret.txt
export CLOUD_SQL_CONNECTION_NAME="$PROJECT_ID:$REGION:$INSTANCE_NAME"
export DB_USER=""
export DB_PASS=""
export DB_NAME="events_db"
EOF

gcloud secrets create events-db-credentials --data-file=/tmp/secret.txt --replication-policy="automatic"
rm /tmp/secret.txt
```

## 3. Pre-Compile Builder Environment Image

To completely eliminate `pip install` download times blocking your pipeline deployments, pre-compile this repository's base utilities natively into your new cloud registry.

```bash

gcloud builds submit ./builder \
    --tag=us-central1-docker.pkg.dev/pokedemo-test/virtual-ta-pipeline/ta-builder:latest
```

## 4. Deploy Cloud Build Triggers

First, we provision a dedicated Service Account orchestrating everything natively with explicit boundaries:

```bash
gcloud iam service-accounts create virtual-ta-job-sa \
    --display-name="Virtual Technical Assistant Job Orchestrator" || true

SA_EMAIL="virtual-ta-job-sa@$PROJECT_ID.iam.gserviceaccount.com"

# Bind strictly scoped identity logic permissions bypassing validations naturally utilizing condition parameters
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/run.admin" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/iam.serviceAccountUser" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/artifactregistry.admin" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/storage.admin" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/cloudbuild.builds.editor" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/serviceusage.serviceUsageConsumer" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/secretmanager.secretAccessor" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/pubsub.publisher" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/cloudsql.client" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/aiplatform.user" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/logging.logWriter" --condition=None

We natively provision a secondary runtime service account (`virtual-ta-app-sa`) exclusively isolated to handle the application's actual data plane bindings (Vertex AI & Firestore) avoiding elevating orchestrator boundaries unnecessarily:

```bash
gcloud iam service-accounts create virtual-ta-app-sa \
    --display-name="Virtual Technical Assistant Application Runtime" || true

APP_SA_EMAIL="virtual-ta-app-sa@$PROJECT_ID.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$APP_SA_EMAIL" --role="roles/aiplatform.user" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$APP_SA_EMAIL" --role="roles/datastore.user" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$APP_SA_EMAIL" --role="roles/cloudtrace.agent" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$APP_SA_EMAIL" --role="roles/logging.logWriter" --condition=None
```


```bash
export APP_SA_EMAIL="virtual-ta-app-sa@$PROJECT_ID.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/cloudtrace.agent" --condition=None
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/logging.logWriter" --condition=None
```

Because Google Cloud CLI doesn't support GitHub-linked Pub/Sub triggers without a Gen-2 OAuth connection, these triggers use `--inline-config` and clone the public `virtual-ta-job` repo at runtime.

Run these from the `workshop-ta-job` directory:

```bash
export PROJECT_ID=""

# Deploy Trigger
gcloud builds triggers create pubsub \
    --name="deploy-event-pipeline" \
    --topic="projects/$PROJECT_ID/topics/deploy_queue" \
    --inline-config="cloudbuild-deploy.yaml" \
    --service-account="projects/$PROJECT_ID/serviceAccounts/$SA_EMAIL"

# Demolish Trigger
gcloud builds triggers create pubsub \
    --name="demolish-event-pipeline" \
    --topic="projects/$PROJECT_ID/topics/demolish_queue" \
    --inline-config="cloudbuild-demolish.yaml" \
    --service-account="projects/$PROJECT_ID/serviceAccounts/$SA_EMAIL"
```

## 5. Deploy Hourly Cloud Run Job

Instead of Cloud Build, we securely isolate the hourly automated environment teardowns into a lightning fast Cloud Run Job container.
Deploy the script natively from the `./hourly/` source folder before scheduling it:

```bash
cd hourly

gcloud run jobs deploy hourly-job \
  --source . \
  --region us-central1 \
  --project $PROJECT_ID \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --service-account="$SA_EMAIL" \
  --max-retries 0

cd ..
```

## 6. Configure Cloud Scheduler (Hourly Job)

Cloud Scheduler will invoke the native Cloud Run Job HTTP endpoint seamlessly exactly at the top of every hour.

```bash
PROJECT_NUMBER=$(gcloud projects describe pokedemo-test --format='value(projectNumber)')

gcloud scheduler jobs create http hourly-job-trigger \
    --schedule="0 * * * *" \
    --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/hourly-job:run" \
    --http-method POST \
    --oauth-service-account-email="$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --location="us-central1" \
    --project=$PROJECT_ID
```

## 7. Manual Test (No Trigger Needed)

To dynamically trigger the primary hourly teardown script independently of schedules:
```bash
gcloud run jobs execute hourly-job --region us-central1 --project $PROJECT_ID
```

To natively execute the Agent Evaluation jobs manually (without waiting for the 11:45PM or 01:00AM triggers):
```bash
# Force the system to instantly create test_event rows for up to 10 stale courses
gcloud run jobs execute daily-test-job --region us-central1 --project $PROJECT_ID

# (Wait for the Virtual TA Test instance to physically deploy in your Dashboard first)

# Manually trigger the ADK Multi-Agent test utilizing Gemini
gcloud run jobs execute eval-agent-job --region us-central1 --project $PROJECT_ID
```

