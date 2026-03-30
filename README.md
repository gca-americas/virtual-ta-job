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
├── eval/
│   ├── daily_test/        # Dynamically isolates and provisions isolated testing events for stale courses natively
│   └── eval_agent/        # The core LLM Evaluator mapping Vertex AI Multi-Agent logic generating syntheic interactions
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

### 🤖 Automated AI Evaluations
To rigorously ensure course modifications organically function against live LLMs structurally, the Architecture continuously evaluates published material autonomously via two identical pipelines:
1. **The Daily Test Generator (`daily_test-job`)**: Executes natively identifying up to 10 stale courses lacking recent evaluations safely mapping each identically against isolated 24-hour testing Events (`eval_YYMMDD_#`). The `hourly_job` detects these strings dynamically publishing Cloud Run instances strictly designated for AI analysis!
2. **The ADK Grading Engine (`eval-agent-job`)**: Natively clones GitHub course context and iteratively executes the Gemini Vertex AI endpoints (ADK). It physically triggers 64 concurrent `Question` queries across the generated Cloud Run endpoints, mapping the REST payload cleanly back into the `Scoring` LLM orchestrator cleanly updating the `eval_score` permanently in the `courses` SQL tracking database seamlessly!

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

---

## 🏃 Running Locally

If you are developing or testing the pipeline natively on your local machine, you shouldn't rely on deploying to Cloud Run every iteration. You can execute all three autonomous jobs securely from the terminal. 

**Prerequisites:**
You must execute these scripts physically from the root directories so Python natively discovers the `database.py` configurations safely! 

Ensure your `.env` contains valid credentials or your `gcloud auth application-default login` securely matches your Google Cloud scope.

1. **Test the Infrastructure Orchestrator (`hourly-job`)**
```bash
# Triggers active event provisioning logic & teardowns
cd virtual-ta-job/hourly
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python hourly_job.py
```

2. **Test the Virtual TA Auto-Provisioner (`daily_test`)**
```bash
# Injects up to 10 stale courses into `events` locally simulating 11:45PM
cd virtual-ta-job/eval/daily_test
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
deactivate
```

3. **Test the Multi-Agent Score Evaluator (`eval_agent`)**
```bash
# Downloads GitHub context natively, executes the Gemini generative testing suite, and validates Cloud Run endpoints mimicking 01:00AM.
cd virtual-ta-job/eval/eval_agent
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python eval/eval_agent/main.py
deactivate
```
