# Virtual TA Jobs Architecture

Welcome to the **Virtual TA Jobs** orchestration engine! This repository (`virtual-ta-job`) serves as the background Infrastructure-as-Code pipeline and active automation layer for the entire ecosystem.

---

## 🏗️ Ecosystem Relationship

This repository is purely a backend operational engine. It acts as the bridge physically spanning the gap between the administrative control plane and the student-facing infrastructure.

- **Virtual TA Admin portal (`virtual-ta-admin`)**: Admins insert schedules into the core Cloud SQL database.
- **Virtual TA Jobs (`virtual-ta-job`)**: *(You are here)*. A background Cloud Scheduler cron runs natively every hour (`hourly-job`). It actively polls the Admin database for pending events, calculating exactly when to start or destroy instances. 
- **Virtual TA (`virtual-ta`)**: When the Job Orchestrator detects a scheduled event, it mechanically triggers a Cloud Build pipeline that literally clones the `virtual-ta` student baseline, injects custom instructor courses, and permanently dynamically hosts it as a public classroom container.

---

## 📂 Architecture of this Repository

The pipeline is completely decoupled into infrastructure mapping, execution hooks, and CI/CD bash deployment logic natively executing across Google Cloud Build.

### Codebase Structure
```text
virtual-ta-job/
├── hourly/
│   ├── hourly_job.py      # The execution logic pulling SQL state & firing Pub/Sub logic
│   ├── database.py        # Connects natively to Cloud SQL using active Secret Manager
│   └── Dockerfile         # Packages the Hourly Job into a Cloud Run container
├── builder/
│   └── Dockerfile         # Custom Cloud Build execution image containing `jq`, `git`, and python
├── terraform/           
│   ├── main.tf            # Authoritative provisioning of the entire architecture + IAM bindings
│   └── variables.tf       # Parameter overrides
├── cloudbuild-deploy.yaml # CI/CD trigger logic explicitly compiling and deploying a Virtual TA URL
├── cloudbuild-demolish.yaml # CI/CD trigger logic actively tearing down expired Event URLs
└── setup.md               # Raw gcloud commands mapping execution bounds
```

---

## ☁️ Infrastructure Setup

This entire CI/CD ecosystem physically bootstraps itself over a serverless architecture entirely mapped via Terraform (`terraform/main.tf`):

### 🚀 Automated Infrastructure Deployment
When a registered workshop actively crosses its scheduled Start Time, the pipeline automatically executes a rigorous construction sequence dynamically:
1. **Google Cloud Scheduler**: Pulses the `hourly-job` REST footprint automatically exactly on the hour.
2. **Google Cloud Run (Jobs)**: The `hourly-job` spins up natively, reads the Cloud SQL database, isolates expired vs starting events, then identically pipes execution JSON payloads onto native Pub/Sub.
3. **Google Cloud Pub/Sub**: The system relies on two distinct message bus architectures:
   - `deploy_queue`: Submits instructions to dynamically construct infrastructure.
   - `demolish_queue`: Submits instructions targeting specific event destruction.
4. **Google Cloud Build Triggers**: Native Eventarc mappings actively listen to Pub/Sub queues. When a payload arrives (e.g., `deploy_queue`), Cloud Build connects directly to the **`main`** branch of [https://github.com/gca-americas/virtual-ta-job](https://github.com/gca-americas/virtual-ta-job), pulls the latest source code, and dynamically executes `cloudbuild-deploy.yaml`. This guarantees your infrastructure pipelines are always executing the absolute latest Bash compiler steps directly over GCP!
5. **Dynamic Skills Injection**: Before the Google Cloud container natively builds the student AI portal, the bash pipeline identically clones only the specific target variables defined by that Event. It uses secure Git `sparse-checkout` mechanisms to cleanly drop exclusively the exact Markdown files, specific instructor skillsets, and codebases legally required for that precise session directly into the `virtual-ta` container. This keeps every student container rigorously locked down and physically separated from other active course algorithms!

### 🗑️ Automated Infrastructure Demolition
Instead of paying for active compute instances indefinitely, the Job Orchestrator executes a rigorous lifecycle cleanup:
1. **Expiration Detection**: Every hour, the `hourly_job.py` scans `running_logs` in Cloud SQL. If it detects a Cloud Run service whose mapped event date formally expired before the current timestamp, it targets the instance.
2. **Execution Teardown**: It publishes the `event_id` and literal `service_name` directly to the `demolish_queue`.
3. **Container Destruction**: Cloud Build securely intercepts this signal and explicitly executes `cloudbuild-demolish.yaml`. This script physically rips the `Virtual TA` classroom container completely out of Google Cloud Run via `gcloud run services delete`, guaranteeing your organization exactly zero trailing compute costs for finalized workshops!

---

## 🔐 Service Account & Security Settings

Because the pipeline is programmatically spinning up new student-facing resources natively inside your project, it requires a rigorously scoped Service Account execution array to safely traverse Google APIs:

### 1. Operation Service Identity (`virtual-ta-job-sa`)
This isolated Identity securely executes the `hourly-job` execution hooks and creates architecture without human intervention. 
It possesses strictly scoped granular GCP IAM privileges:
- `roles/run.admin` (Provisions the new student web-servers dynamically)
- `roles/cloudsql.client` (Safely connects to the Admin SQL pipeline natively)
- `roles/iam.serviceAccountUser` (Securely binds identities across active architecture)
- `roles/artifactregistry.admin` (Compiles native docker containers iteratively)
- `roles/cloudbuild.editor` (Issues the Cloud Builder tasks securely)
- `roles/secretmanager.secretAccessor` (Acquires dynamic DB passwords natively inside Cloud Run)
- `roles/pubsub.publisher` (Directly authorizes pushing payloads into identical queues)

### 2. Cloud Build Service Agent
Your GCP-native Cloud Build agent automatically executes the CI/CD files. To natively read the `_BODY` substitutions actively mapped inside the Pub/Sub bus, the Terraform permanently explicitly grants exactly:
- `roles/pubsub.subscriber` on your active Google Project globally.
